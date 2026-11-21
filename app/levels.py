"""Honest progress: what the learner can really do, estimated per skill on the CEFR scale (A1-C1), plus a weekly
study goal (instead of a streak) and an optional monthly level check.

Everything here is rule-based and offline. Each estimate says where it comes from, and says plainly when there
isn't enough evidence yet, instead of guessing. The page builds its sentences from the numbers returned here
(so the whole text lives in the UI and its Turkish translation).

Where each estimate comes from:
- Vocabulary: the share of the most frequent German words the learner knows (see VOCAB_RULES), or the
  vocabulary part of a recent level check, whichever shows more. Neither source alone can prove what the learner
  doesn't know: the app only sees words met in it, and a short check only samples a few.
- Grammar: declension and verb drill answers of the last GRAMMAR_DAYS days, grouped into areas per level
  (see GRAMMAR_AREAS), or the grammar part of a recent level check, whichever shows more.
- Writing: texts from the Writing desk (marked by AI) that passed at their level.
- Reading: texts from the reading room when one is registered (see register_reading_source), else the vocabulary
  estimate, since reading comfortably is mostly a matter of knowing the words.
"""
import datetime as dt
import functools
import json
import random
import re

from fastapi import APIRouter, HTTPException

from . import db, decl, dictionary, known, verbs
from .i18n import localize

router = APIRouter()

LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]
SCHEMA = """
CREATE TABLE IF NOT EXISTS level_checks(
  id INTEGER PRIMARY KEY, started_at TEXT, finished_at TEXT, date TEXT, state TEXT, result TEXT);
"""
_ready = False


def _init():
    global _ready
    if not _ready:
        with db.connect() as conn:
            conn.executescript(SCHEMA)
        _ready = True


def level_index(name):
    """"B1" -> 2; anything unknown -> None."""
    return LEVELS.index(name) if name in LEVELS else None


# ---------------------------------------------------------------------------------------------------------------
# Vocabulary
# ---------------------------------------------------------------------------------------------------------------
# (band: the N most frequent words, level reached, share of that band needed). A known word counts 1, a word still
# being learned counts half. The bands follow the usual rough sizes (A1 ~500 words, A2 ~1000, B1 ~2000,
# B2 ~3500, C1 beyond); the shares sit a bit low because a frequency list always holds some words a learner never
# needs (names, slang, rare homographs), and the app only counts words it has seen the learner meet.
VOCAB_RULES = [(500, 0, .40), (1000, 1, .50), (2000, 2, .55), (3500, 3, .60), (6000, 4, .60)]
VOCAB_MIN_WORDS = 30  # fewer words tracked than this: not enough to say anything
_NOT_A_WORD = re.compile(r"^(gerund of|female equivalent|synonym of|alternative|plural of|abbreviation|initialism|"
                         r"misspelling|obsolete|archaic|clipping)", re.I)


@functools.lru_cache(maxsize=1)
def frequency_words():
    """The most frequent German dictionary words as [(lowercase word, rank)], most frequent first. Built once from
    the offline dictionary; lower case so "Ja" and "ja" count once."""
    if not dictionary.available():
        return []
    rows = dictionary._con().execute(
        "SELECT word, glosses, rank FROM word WHERE rank IS NOT NULL AND rank <= ? ORDER BY rank",
        (VOCAB_RULES[-1][0],)).fetchall()
    seen, out = set(), []
    for r in rows:
        w = r["word"]
        if len(w) < 2 or w.isupper() or " " in w:
            continue
        if all(_NOT_A_WORD.match(g) for g in json.loads(r["glosses"])):
            continue
        k = w.lower()
        if k not in seen:
            seen.add(k)
            out.append((k, r["rank"]))
    return out


def vocab_bands(statuses):
    """For each frequency band: how many of its words are known / being learned, and the weighted share."""
    best = {}
    for w, s in statuses.items():
        k = w.lower()
        best[k] = max(best.get(k, known.NEW), s)
    words = frequency_words()
    out = []
    for top, _lvl, _need in VOCAB_RULES:
        band = [w for w, r in words if r <= top]
        k = sum(1 for w in band if best.get(w) == known.KNOWN)
        lrn = sum(1 for w in band if best.get(w) == known.LEARNING)
        total = len(band)
        out.append({"top": top, "known": k, "learning": lrn, "total": total,
                    "pct": round(100 * (k + lrn / 2) / total) if total else 0})
    return out


def vocab_level(bands):
    """The highest level whose band share is reached, and how many more words the next level needs."""
    level, nxt = None, None
    for (top, lvl, need), b in zip(VOCAB_RULES, bands):
        if b["total"] and (b["known"] + b["learning"] / 2) >= need * b["total"]:
            level = lvl
        else:
            missing = need * b["total"] - (b["known"] + b["learning"] / 2)
            nxt = {"level": lvl, "top": top, "words": max(1, int(missing + .999)), "need_pct": round(100 * need)}
            break
    return level, nxt


def vocab_estimate(check=None):
    st = known.statuses()
    tracked = sum(1 for s in st.values() if s >= known.LEARNING)
    bands = vocab_bands(st)
    level, nxt = vocab_level(bands)
    out = {"skill": "vocab", "tracked": tracked, "bands": bands, "next": nxt, "source": "words",
           "enough": tracked >= VOCAB_MIN_WORDS, "level": level if tracked >= VOCAB_MIN_WORDS else None}
    _merge_check(out, check, "vocab")
    return out


def _merge_check(out, check, part):
    """Use a recent level check when it shows a higher level than the practice data (or there is no data)."""
    if not check:
        return
    lvl = check["result"].get(part)
    if lvl is None:
        return
    if not out["enough"] or out["level"] is None or lvl > out["level"]:
        out.update(level=lvl, enough=True, source="check", check_date=check["date"])


# ---------------------------------------------------------------------------------------------------------------
# Grammar
# ---------------------------------------------------------------------------------------------------------------
GRAMMAR_DAYS = 120   # only recent answers count: ability fades
AREA_MIN = 10        # answers needed before an area counts as tested
AREA_SOLID = .80     # share right for an area to count as solid
GRAMMAR_MIN = 30     # fewer answers than this in total: not enough data
_DET = ("def", "dies", "ein", "poss")


def _fam_case(key):
    p = key.split(":")
    return p[0], (p[1] if len(p) > 1 and p[1] in decl.CASES else None)


# (id, level, does this skill key belong here?). Levels follow the usual order of German courses.
GRAMMAR_AREAS = [
    ("articles_nom_akk", 0, lambda f, c, k: f in _DET and c in ("nom", "akk")),
    ("pronouns_akk", 0, lambda f, c, k: f == "pers" and c == "akk"),
    ("present", 0, lambda f, c, k: k in ("vb:praes:reg", "vb:praes:irr", "vb:praes:stem", "vb:modal:praes")),
    ("articles_dat", 1, lambda f, c, k: f in _DET and c == "dat"),
    ("pronouns_dat", 1, lambda f, c, k: (f == "pers" and c == "dat") or f == "refl"),
    ("prepositions", 1, lambda f, c, k: f == "trig"),
    ("perfekt", 1, lambda f, c, k: k == "vb:perf:aux" or k.startswith("vb:pp:")),
    ("separable", 1, lambda f, c, k: k == "vb:praes:sep"),
    ("adjectives", 2, lambda f, c, k: f in ("adjw", "adjm", "adjs") and c in ("nom", "akk", "dat")),
    ("relative", 2, lambda f, c, k: (f == "rel" and c != "gen") or f == "wer"),
    ("praeteritum", 2, lambda f, c, k: k.startswith("vb:praet:") or k == "vb:modal:praet" or f == "vp"),
    ("future_konj2", 2, lambda f, c, k: k == "vb:fut1" or k.startswith("vb:konj2:")),
    ("genitive", 3, lambda f, c, k: c == "gen" and f not in ("trig",)),
    ("plusq_fut2", 3, lambda f, c, k: k in ("vb:plusq", "vb:fut2")),
]
GRAMMAR_TOP = 3  # drills cover grammar up to B2


def _case_of(key):
    try:
        return decl.key_case(key)
    except KeyError:  # a trigger key from an older version
        return None


def grammar_log(days=GRAMMAR_DAYS):
    since = (db.study_date() - dt.timedelta(days=days)).isoformat()
    return db.q("SELECT key, correct FROM decl_log WHERE date >= ?", (since,))


def grammar_from_log(rows):
    """Areas, per-case accuracy and the level reached, from (key, correct) answer rows."""
    areas = {a[0]: {"id": a[0], "level": a[1], "n": 0, "right": 0} for a in GRAMMAR_AREAS}
    cases = {c: {"case": c, "name": decl.CASE_NAME[c], "n": 0, "right": 0} for c in decl.CASES}
    for r in rows:
        key = r["key"]
        f, c = _fam_case(key)
        if f == "trig":
            c = _case_of(key)
        for aid, _lvl, test in GRAMMAR_AREAS:
            if test(f, c, key):
                areas[aid]["n"] += 1
                areas[aid]["right"] += r["correct"]
        if c and not key.startswith(("vb:", "vp:", "gender:", "plural:")):
            cases[c]["n"] += 1
            cases[c]["right"] += r["correct"]
    for a in areas.values():
        a["pct"] = round(100 * a["right"] / a["n"]) if a["n"] else None
        a["state"] = "untested" if a["n"] < AREA_MIN else "solid" if a["right"] >= AREA_SOLID * a["n"] else "weak"
    for c in cases.values():
        c["pct"] = round(100 * c["right"] / c["n"]) if c["n"] else None
    level = None
    for lvl in range(GRAMMAR_TOP + 1):
        mine = [a for a in areas.values() if a["level"] == lvl]
        solid = sum(1 for a in mine if a["state"] == "solid")
        if solid * 3 >= 2 * len(mine):  # two thirds of a level's areas solid
            level = lvl
        else:
            break
    nxt_lvl = 0 if level is None else level + 1
    todo = [a["id"] for a in areas.values() if a["level"] == nxt_lvl and a["state"] != "solid"]
    return {"areas": list(areas.values()), "cases": list(cases.values()), "level": level,
            "next": {"level": nxt_lvl, "areas": todo} if nxt_lvl <= GRAMMAR_TOP else None,
            "answers": len(rows)}


def grammar_estimate(check=None):
    g = grammar_from_log(grammar_log())
    enough = g["answers"] >= GRAMMAR_MIN
    out = {"skill": "grammar", **g, "enough": enough, "level": g["level"] if enough else None, "source": "drills",
           "days": GRAMMAR_DAYS}
    _merge_check(out, check, "grammar")
    return out


# ---------------------------------------------------------------------------------------------------------------
# Writing (texts from the Writing desk, marked by AI against their target level)
# ---------------------------------------------------------------------------------------------------------------
WRITING_PASS = 60  # the desk's own pass mark
WRITING_DAYS = 365


def writing_from_rows(rows):
    """rows: (level, score). The level is the highest one with two passed texts at it or above;
    one passed text at a higher level is reported as a tentative sign."""
    passed = [level_index(r["level"]) for r in rows if (r["score"] or 0) >= WRITING_PASS and level_index(r["level"]) is not None]
    level = None
    for lvl in range(len(LEVELS) - 1, -1, -1):
        if sum(1 for p in passed if p >= lvl) >= 2:
            level = lvl
            break
    tentative = max(passed) if passed and (level is None or max(passed) > level) else None
    return {"texts": len(rows), "passed": len(passed), "level": level, "tentative": tentative}


def writing_estimate():
    since = (db.study_date() - dt.timedelta(days=WRITING_DAYS)).isoformat()
    rows = db.q("SELECT level, score FROM writings WHERE date >= ?", (since,))
    w = writing_from_rows(rows)
    if w["level"] is None and w["tentative"] is not None:
        w["level"] = w["tentative"]  # one passed text is still evidence; the page says it's based on one text
    return {"skill": "writing", **w, "enough": len(rows) > 0, "source": "writings"}


# ---------------------------------------------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------------------------------------------
# A reading room (built separately) can register a function returning the texts read: [{"level": "B1",
# "known_pct": 93}, ...]. Without one, reading is estimated from the vocabulary.
_READING_SOURCES = []
READ_COMFORT = 90  # % of a text's words known for it to count as read comfortably


def register_reading_source(fn):
    _READING_SOURCES.append(fn)
    return fn


def reading_from_texts(texts):
    ok = [level_index(t.get("level")) for t in texts
          if (t.get("known_pct") or 0) >= READ_COMFORT and level_index(t.get("level")) is not None]
    level = None
    for lvl in range(len(LEVELS) - 1, -1, -1):
        if sum(1 for p in ok if p >= lvl) >= 2:
            level = lvl
            break
    return {"texts": len(texts), "comfortable": len(ok), "level": level}


def reading_estimate(vocab):
    texts = []
    for fn in _READING_SOURCES:
        try:
            texts += list(fn() or [])
        except Exception:  # the reading room is optional; never let it break this page
            continue
    if texts:
        r = reading_from_texts(texts)
        return {"skill": "reading", **r, "enough": True, "source": "texts"}
    return {"skill": "reading", "texts": 0, "level": vocab["level"], "enough": vocab["enough"], "source": "vocab"}


# ---------------------------------------------------------------------------------------------------------------
# The whole picture
# ---------------------------------------------------------------------------------------------------------------
SKILL_ORDER = ("vocab", "grammar", "writing", "reading")


def verdict(skills, setting):
    """Ready for the next level when every skill with evidence is at least one level above the learner's
    setting (and there are at least two such skills). The weakest skill is what holds them back."""
    rated = [s for s in skills if s["enough"]]
    ranked = sorted(rated, key=lambda s: (-1 if s["level"] is None else s["level"], SKILL_ORDER.index(s["skill"])))
    weakest = ranked[0]["skill"] if len(rated) >= 2 else None
    ready = None
    if setting is not None and len(rated) >= 2 and all(s["level"] is not None and s["level"] >= setting + 1 for s in rated):
        ready = setting + 1
    return {"ready": ready, "weakest": weakest, "rated": len(rated)}


def last_check(days=None):
    _init()
    row = db.q1("SELECT * FROM level_checks WHERE finished_at IS NOT NULL ORDER BY id DESC LIMIT 1")
    if not row:
        return None
    out = {"id": row["id"], "date": row["date"], "result": json.loads(row["result"])}
    if days is not None and (db.study_date() - dt.date.fromisoformat(row["date"])).days > days:
        return None
    return out


CHECK_COUNTS_DAYS = 90  # a check older than this no longer lifts an estimate
CHECK_EVERY_DAYS = 30


def summary():
    setting = level_index(db.get_settings()["level"])
    check = last_check(CHECK_COUNTS_DAYS)
    vocab = vocab_estimate(check)
    grammar = grammar_estimate(check)
    writing = writing_estimate()
    reading = reading_estimate(vocab)
    skills = [vocab, grammar, writing, reading]
    latest = last_check()
    days_since = (db.study_date() - dt.date.fromisoformat(latest["date"])).days if latest else None
    return {"known": {**known.counts(), "history": known.history()}, "skills": skills, "verdict": verdict(skills, setting),
            "setting": setting, "levels": LEVELS, "week": week_goal(), "checks": check_history(),
            "check_due": days_since is None or days_since > CHECK_EVERY_DAYS, "days_since_check": days_since}


# ---------------------------------------------------------------------------------------------------------------
# Weekly goal (instead of a streak): days studied this week out of a target. Rest days never break anything.
# ---------------------------------------------------------------------------------------------------------------
def week_target():
    try:
        return min(7, max(3, int(db.get_settings().get("week_goal") or 5)))
    except ValueError:
        return 5


def week_goal(today=None):
    today = today or db.study_date()
    monday = today - dt.timedelta(days=today.weekday())
    dates = [(monday + dt.timedelta(days=i)).isoformat() for i in range(7)]
    active = {r["date"] for r in db.q(
        "SELECT date FROM reading WHERE date >= ? UNION SELECT date FROM reviews WHERE date >= ? "
        "UNION SELECT date FROM answers WHERE date >= ? UNION SELECT date FROM activity WHERE date >= ?",
        (dates[0],) * 4)}
    studied = [d in active for d in dates]
    target = week_target()
    days = sum(studied)
    return {"days": days, "target": target, "met": days >= target, "studied": studied,
            "today_index": today.weekday(), "today_done": today.isoformat() in active}


# ---------------------------------------------------------------------------------------------------------------
# Monthly level check: about 10 minutes, rule-based, adaptive. No AI, no network.
# ---------------------------------------------------------------------------------------------------------------
# Order of the questions; each part adapts on its own (right: one level up, wrong: one level down).
CHECK_PLAN = ["vocab", "case", "verb"] * 8 + ["vocab", "vocab"]
SECTION_TOP = {"vocab": 4, "case": 3, "verb": 3}  # highest level each part can test (C1, B2, B2)
VOCAB_BAND = [(0, 500), (500, 1000), (1000, 2000), (2000, 3500), (3500, 6000)]
CASE_KEYS = {
    0: [f"{f}:{c}:{g}" for f in ("def", "ein") for c in ("nom", "akk") for g in decl.GENDERS],
    1: [f"{f}:dat:{g}" for f in ("def", "ein", "poss") for g in decl.GENDERS] + [f"poss:akk:{g}" for g in decl.GENDERS]
       + [f"pers:{c}:{p}" for c in ("akk", "dat") for p in ("ich", "du", "er", "sie", "wir", "ihr")],
    2: [f"{f}:{c}:{g}" for f in ("adjw", "adjm") for c in ("nom", "akk", "dat") for g in decl.GENDERS]
       + [f"rel:{c}:{g}" for c in ("nom", "akk", "dat") for g in ("m", "f", "n")],
    3: [f"{f}:gen:{g}" for f in ("def", "ein", "poss", "adjw", "adjm") for g in decl.GENDERS]
       + [f"adjs:{c}:{g}" for c in ("nom", "akk", "dat") for g in decl.GENDERS] + ["rel:dat:pl", "rel:gen:m", "rel:gen:f"],
}
VERB_KEYS = {
    0: ["vb:praes:reg", "vb:praes:irr", "vb:modal:praes"],
    1: ["vb:praes:stem", "vb:praes:sep", "vb:pp:weak", "vb:pp:strong", "vb:praet:irr"],
    2: ["vb:praet:weak", "vb:praet:strong", "vb:fut1", "vb:konj2:irr", "vb:modal:praet"],
    3: ["vb:plusq", "vb:fut2", "vb:konj2:wuerde", "vb:praet:mixed"],
}
PASS_SHARE = .6  # a level counts as passed with 60%+ right over at least two questions at it


@functools.lru_cache(maxsize=1)
def _vocab_pool():
    """Words for the recognition questions: common nouns (with their own frequency) and the verb engine's verbs."""
    pool = []
    for n in dictionary.nouns(0, VOCAB_BAND[-1][1]):
        meaning = "; ".join(dictionary.short([n["meaning"]], 1).split("; ")[:2])  # short options read fairly
        if meaning and len(meaning) <= 60:
            pool.append({"word": f"{dictionary.ARTICLE.get(n['g'], '')} {n['word']}".strip(), "meaning": meaning,
                         "rank": n["rank"], "pos": "noun"})
    for v in verbs.VERBS:
        if v["refl"]:
            continue
        e = dictionary.lookup(v["inf"], 1)
        if e and e[0]["word"] == v["inf"] and e[0]["rank"]:
            pool.append({"word": v["inf"], "meaning": v["en"], "rank": e[0]["rank"], "pos": "verb"})
    return pool


def _band(level):
    lo, hi = VOCAB_BAND[level]
    return [w for w in _vocab_pool() if lo < w["rank"] <= hi]


def vocab_question(level, used=()):
    words = [w for w in _band(level) if w["word"] not in used] or _band(level)
    w = random.choice(words)
    others = [o for o in _vocab_pool() if o["pos"] == w["pos"] and o["meaning"] != w["meaning"]
              and abs(_band_of(o["rank"]) - level) <= 1]
    seen, wrong = {w["meaning"]}, []
    for o in random.sample(others, len(others)):
        if o["meaning"] not in seen:
            seen.add(o["meaning"])
            wrong.append(o["meaning"])
        if len(wrong) == 3:
            break
    choices = wrong + [w["meaning"]]
    random.shuffle(choices)
    return {"family": "vocab", "kind": "choice", "prompt": w["word"], "choices": choices, "answers": [w["meaning"]],
            "display": w["meaning"], "why": "", "cue": "", "word": w["word"]}


def _band_of(rank):
    return next((i for i, (lo, hi) in enumerate(VOCAB_BAND) if lo < rank <= hi), len(VOCAB_BAND) - 1)


def case_question(level):
    key = random.choice(CASE_KEYS[level])
    family = key.split(":")[0]
    if family in _DET:
        q = decl.gen_det_sentence(key)
    elif family.startswith("adj"):
        q = decl._gen_sentence(key)  # always a full sentence: in a test, the case has to be worked out
    else:
        q = decl.GENERATORS[family](key)
    return {**q, "kind": "text"}


def verb_question(level):
    key = random.choice(VERB_KEYS[level])
    q = verbs.gen_conj(key)
    tense = {"vb:modal:praes": "praes", "vb:modal:praet": "praet"}.get(key) or verbs.key_tense(key) or "praes"
    return {**q, "tense": verbs.TENSES[tense]}


def make_question(section, level, used=()):
    if section == "vocab":
        return vocab_question(level, used)
    return case_question(level) if section == "case" else verb_question(level)


def is_right(q, answer):
    if q["kind"] == "choice":
        return (answer or "").strip() in q["answers"]
    return decl.norm(answer) in {decl.norm(a) for a in q["answers"]}


def next_level(level, right, top):
    return min(top, level + 1) if right else max(0, level - 1)


def score_section(items, top):
    """items: [{"level", "correct"}]. The highest level passed (60%+ right over at least two questions there),
    or None when not even the lowest one was."""
    by = {}
    for it in items:
        n, c = by.get(it["level"], (0, 0))
        by[it["level"]] = (n + 1, c + int(bool(it["correct"])))
    best = None
    for lvl in range(top + 1):
        n, c = by.get(lvl, (0, 0))
        if n >= 2 and c >= PASS_SHARE * n:
            best = lvl
    return best


def score_check(items):
    """The result of a finished check: a level per part, grammar (the weaker of cases and verbs) and an overall
    level (the middle of vocabulary, cases and verbs). None means below A1."""
    res = {s: score_section([i for i in items if i["section"] == s], top) for s, top in SECTION_TOP.items()}
    low = lambda v: -1 if v is None else v  # noqa: E731
    res["grammar"] = None if res["case"] is None or res["verb"] is None else min(res["case"], res["verb"])
    mid = sorted(low(res[s]) for s in ("vocab", "case", "verb"))[1]
    res["overall"] = None if mid < 0 else mid
    res["right"] = sum(1 for i in items if i["correct"])
    res["total"] = len(items)
    res["sections"] = {s: {"n": sum(1 for i in items if i["section"] == s),
                           "right": sum(1 for i in items if i["section"] == s and i["correct"])} for s in SECTION_TOP}
    return res


def _public(q, section, n):
    """What the page may see: never the answers."""
    out = {k: q.get(k) for k in ("prompt", "cue", "kind", "choices", "label", "tense", "word")}
    out.update(section=section, n=n, total=len(CHECK_PLAN))
    return localize(out)


def _start_level(section):
    setting = level_index(db.get_settings()["level"]) or 0
    return min(SECTION_TOP[section], max(0, setting - 1))  # start a little below the setting, then climb


def start_check():
    _init()
    levels = {s: _start_level(s) for s in SECTION_TOP}
    section = CHECK_PLAN[0]
    q = make_question(section, levels[section])
    state = {"levels": levels, "items": [], "current": {"section": section, "level": levels[section], "q": q}}
    cid = db.ex("INSERT INTO level_checks(started_at, date, state) VALUES(?,?,?)",
                (db.now(), db.today(), json.dumps(state, ensure_ascii=False)))
    return {"id": cid, "question": _public(q, section, 1)}


def answer_check(cid, answer):
    _init()
    row = db.q1("SELECT * FROM level_checks WHERE id=?", (cid,))
    if not row or row["finished_at"]:
        raise HTTPException(404, "This level check is already finished.")
    state = json.loads(row["state"])
    cur = state["current"]
    q, section = cur["q"], cur["section"]
    right = is_right(q, answer)
    state["items"].append({"section": section, "level": cur["level"], "correct": right, "answer": (answer or "")[:200],
                           "key": q.get("key") or q.get("word"), "case": q.get("case")})
    state["levels"][section] = next_level(cur["level"], right, SECTION_TOP[section])
    feedback = localize({"correct": right, "display": q["display"], "full": q.get("full") or q["display"], "why": q.get("why", "")})
    n = len(state["items"])
    if n < len(CHECK_PLAN):
        section = CHECK_PLAN[n]
        used = {i["key"] for i in state["items"] if i["section"] == "vocab"}
        nq = make_question(section, state["levels"][section], used)
        state["current"] = {"section": section, "level": state["levels"][section], "q": nq}
        db.ex("UPDATE level_checks SET state=? WHERE id=?", (json.dumps(state, ensure_ascii=False), cid))
        return {**feedback, "next": _public(nq, section, n + 1)}
    result = score_check(state["items"])
    state["current"] = None
    now = db.now()
    db.ex("UPDATE level_checks SET state=?, result=?, finished_at=?, date=? WHERE id=?",
          (json.dumps(state, ensure_ascii=False), json.dumps(result), now, db.today(), cid))
    # The check is real study, so it counts as a study day for the weekly goal.
    secs = int((dt.datetime.fromisoformat(now) - dt.datetime.fromisoformat(row["started_at"])).total_seconds())
    db.ex("INSERT INTO activity(kind, seconds, ts, date) VALUES('levelcheck', ?, ?, ?)", (min(max(secs, 0), 1800), now, db.today()))
    return {**feedback, "next": None, "result": result}


def check_history(limit=12):
    _init()
    rows = db.q("SELECT id, date, result FROM level_checks WHERE finished_at IS NOT NULL ORDER BY id DESC LIMIT ?", (limit,))
    return [{"id": r["id"], "date": r["date"], **json.loads(r["result"])} for r in rows]


# ---------------------------------------------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------------------------------------------
@router.get("/api/level")
def level_summary():
    return summary()


@router.get("/api/level/brief")
def level_brief():
    """The small summary on Home: words known and this week's goal."""
    c = known.counts()
    return {"known": c["known"], "learning": c["learning"], "week": week_goal()}


@router.post("/api/level/check/start")
def level_check_start():
    return start_check()


@router.post("/api/level/check/answer")
def level_check_answer(body: dict):
    return answer_check(int(body.get("id") or 0), str(body.get("answer") or ""))
