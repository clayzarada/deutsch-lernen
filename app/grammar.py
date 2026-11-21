"""Grammar: the handbook (grammar_data.py), its search, the "Explain this" links in the Mistake Book, the gender
rules for the der/die/das drill, and typed sentence building for the word order practice.

Everything here is rule-based and offline: no AI.
"""
import json
import re

from fastapi import APIRouter, HTTPException

from . import db, decl, genderrules, wordorder
from .grammar_data import LEVELS, THEMES, TOPIC_BY_ID, TOPICS
from .i18n import lang, localize

router = APIRouter()


def _pick(v):
    """One half of an (English, Turkish) pair for the app language; anything else is returned as it is."""
    if isinstance(v, tuple) and len(v) == 2:
        return v[1] if lang() == "tr" else v[0]
    return v


# ---------------------------------------------------------------------------------------------------------------
# The handbook
# ---------------------------------------------------------------------------------------------------------------
def _block(b):
    kind = b[0]
    if kind == "table":
        t = b[1]
        return {"kind": "table", "cols": [_pick(c) for c in t["cols"]],
                "rows": [[_pick(c) for c in r] for r in t["rows"]], "caption": _pick(t["caption"]) if t["caption"] else ""}
    return {"kind": kind, "text": _pick(b[1:3])}


def topic_view(t):
    """A topic in the app language, ready for the page."""
    tr = lang() == "tr"
    return {"id": t["id"], "level": t["level"], "theme": t["theme"], "title": _pick(t["title"]),
            "summary": _pick(t["summary"]), "body": [_block(b) for b in t["body"]],
            "examples": [{"de": de, "tr": (tr_ if tr else en)} for de, en, tr_ in t["examples"]],
            "mistakes": [{"wrong": w, "right": r, "why": (wt if tr else we)} for w, r, we, wt in t["mistakes"]],
            "note": t["note"], "try": t["try"]}


def index():
    return {"levels": LEVELS, "themes": [{"id": k, "title": _pick(v)} for k, v in THEMES],
            "topics": [{"id": t["id"], "level": t["level"], "theme": t["theme"], "title": _pick(t["title"]),
                        "summary": _pick(t["summary"]), "has_try": bool(t["try"])} for t in TOPICS]}


# ---------- search ----------
_FOLD = str.maketrans({"ä": "a", "ö": "o", "ü": "u", "ß": "ss", "ı": "i", "ş": "s", "ç": "c", "ğ": "g", "â": "a", "é": "e"})


def fold(s):
    """Lower case without accents, so "Prapositionen", "präpositionen" and "PRÄPOSITIONEN" are the same."""
    return re.sub(r"\s+", " ", (s or "").replace("İ", "i").lower().translate(_FOLD)).strip()


def _texts(t):
    """Every piece of text of a topic, by how much a hit there counts."""
    title = " ".join(t["title"])
    strong = " ".join([t["keys"], t["id"].replace("-", " ")])
    body = []
    for b in t["body"]:
        if b[0] == "table":
            body += [c if isinstance(c, str) else " ".join(c) for r in [b[1]["cols"]] + b[1]["rows"] for c in r]
        else:
            body += [b[1], b[2]]
    body += [" ".join(e) for e in t["examples"]] + [" ".join(m) for m in t["mistakes"]] + list(t["summary"]) + [t["note"]]
    return fold(title), fold(strong), fold(" ".join(body))


_INDEX = None


def _search_index():
    global _INDEX
    if _INDEX is None:
        _INDEX = [(t, *_texts(t)) for t in TOPICS]
    return _INDEX


def _word_score(w, title, strong, body):
    whole = re.compile(r"(?<![a-z])" + re.escape(w) + r"(?![a-z])")
    s = 0
    for text, weight in ((title, 10), (strong, 6), (body, 1)):
        if whole.search(text):
            s += weight * 2
        elif w in text:
            s += weight
    return s


def search(q):
    """Topic ids that match every word of the query, best first. A German word ("wegen", "dessen") finds the topics
    whose keywords, tables or examples use it; a whole word counts more than part of one."""
    words = [w for w in fold(q).split() if w]
    if not words:
        return [t["id"] for t in TOPICS]
    found = []
    for t, title, strong, body in _search_index():
        score = 0
        for w in words:
            s = _word_score(w, title, strong, body)
            if not s and len(w) > 5:  # "präpositionen" also finds "Präposition", "endings" finds "ending"
                s = _word_score(re.sub(r"(en|n|e|s)$", "", w), title, strong, body) / 2
            if not s:
                break
            score += s
        else:
            found.append((score, t["id"]))
    return [i for _s, i in sorted(found, key=lambda x: -x[0])]


# ---------------------------------------------------------------------------------------------------------------
# Mistake Book: which handbook topic explains a mistake (rules only, no AI)
# ---------------------------------------------------------------------------------------------------------------
_CASE_TOPIC = {"nom": "cases", "akk": "accusative", "dat": "dative", "gen": "genitive"}
_PREP_TOPIC = {"akk": "prep-akk", "dat": "prep-dat", "gen": "prep-gen"}


def skill_topic(key):
    """The topic for one drill skill key (decl.py, verbs.py, wordorder.py), or None."""
    key = key or ""
    if key.startswith("trig:p:"):
        trig = decl.TRIGGERS.get(key)
        return _PREP_TOPIC.get(trig[1]) if trig else None
    if key.startswith("trig:v:"):
        trig = decl.TRIGGERS.get(key)
        return "dative" if trig and trig[1] == "dat" else "accusative"
    if key.startswith(("def:", "dies:", "ein:", "poss:")):
        fam, case = key.split(":")[:2]
        if fam in ("dies", "poss", "ein") and case == "nom":
            return {"dies": "der-words", "poss": "possessives", "ein": "ein-kein"}[fam]
        if fam == "poss":
            return "possessives"
        return _CASE_TOPIC.get(case)
    best = None
    for t in TOPICS:  # the longest matching prefix wins ("vb:pp:sep" before "vb:pp:")
        for s in t["skills"]:
            if (key == s or (s.endswith(":") and key.startswith(s))) and (not best or len(s) > len(best[0])):
                best = (s, t["id"])
    return best[1] if best else None


_MATCH = [(t["id"], re.compile(t["match"], re.I)) for t in TOPICS if t["match"]]
# Broad labels ("Word order", "Cases", "Adjectives", "Articles") point to the overview topic, but count less than
# anything specific, so "Word order" + "After weil the verb goes to the end" opens Subordinate clauses.
_GENERIC = [("v2", re.compile(r"word order|wortstellung|satzstellung", re.I)),
            ("cases", re.compile(r"\bcases?\b|\bkasus\b", re.I)),
            ("adj-endings", re.compile(r"\badjecti|\badjektiv", re.I)),
            ("gender", re.compile(r"\barticles?\b|\bartikel\b", re.I)),
            ("pronouns", re.compile(r"\bpronouns?\b|\bpronomen\b", re.I))]
_ORDER = {t["id"]: i for i, t in enumerate(TOPICS)}


def mistake_topic(m):
    """The handbook topic that best explains a Mistake Book entry, or None.
    Specific evidence: each linked drill skill 4 points, the mistake's topic label matching a topic's pattern 3, its
    explanation 2, the question and answers 1. Broad labels add 2 (label) or 1 (explanation). At least 2 points are
    needed, so one loose word in a sentence isn't enough; on a tie the more specific evidence wins."""
    specific, broad = {}, {}

    def add(d, tid, n):
        if tid:
            d[tid] = d.get(tid, 0) + n

    skills = m.get("skills")
    if isinstance(skills, str):
        try:
            skills = json.loads(skills)
        except ValueError:
            skills = []
    for k in skills or []:
        add(specific, skill_topic(k), 4)
    sentence = " ".join(x or "" for x in (m.get("question"), m.get("wrong"), m.get("correct")))
    for text, weight, broad_weight in ((m.get("topic"), 3, 2), (m.get("explanation"), 2, 1), (sentence, 1, 0)):
        if not text:
            continue
        for tid, rx in _MATCH:
            if rx.search(text):
                add(specific, tid, weight)
        for tid, rx in _GENERIC:
            if broad_weight and rx.search(text):
                add(broad, tid, broad_weight)
    ids = set(specific) | set(broad)
    if not ids:
        return None
    best = max(ids, key=lambda i: (specific.get(i, 0) + broad.get(i, 0), specific.get(i, 0), -_ORDER[i]))
    return best if specific.get(best, 0) + broad.get(best, 0) >= 2 else None


def mistake_links(status="open"):
    out = {}
    for m in db.q("SELECT id, topic, question, wrong, correct, explanation, skills FROM mistakes WHERE status=?", (status,)):
        tid = mistake_topic(m)
        if tid:
            out[m["id"]] = {"id": tid, "title": _pick(TOPIC_BY_ID[tid]["title"])}
    return out


# ---------------------------------------------------------------------------------------------------------------
# Typed sentence building (Verbs > Free practice > Word order, "Type it")
# ---------------------------------------------------------------------------------------------------------------
# Other full sentences that are just as right as the one in wordorder.py. Mostly another "you" (the English
# prompt doesn't say du, ihr or Sie) or another natural order.
ALSO_RIGHT = {
    "Wann kommst du nach Hause?": ["Wann kommt ihr nach Hause?", "Wann kommen Sie nach Hause?"],
    "Kommst du morgen mit?": ["Kommt ihr morgen mit?", "Kommen Sie morgen mit?"],
    "Hast du schon gegessen?": ["Habt ihr schon gegessen?", "Haben Sie schon gegessen?"],
    "Warum lernst du Deutsch?": ["Warum lernt ihr Deutsch?", "Warum lernen Sie Deutsch?"],
    "Was machst du am Wochenende?": ["Was macht ihr am Wochenende?", "Was machen Sie am Wochenende?"],
    "Können Sie mir helfen?": ["Kannst du mir helfen?", "Könnt ihr mir helfen?"],
    "Wie lange bleibt ihr in Rom?": ["Wie lange bleibst du in Rom?", "Wie lange bleiben Sie in Rom?"],
    "Du kannst heute Abend bei uns essen.": ["Ihr könnt heute Abend bei uns essen.", "Sie können heute Abend bei uns essen."],
    "Ich rufe dich heute Abend an.": ["Ich rufe Sie heute Abend an.", "Ich rufe euch heute Abend an."],
    "Kannst du mir sagen, wo der Bahnhof ist?": ["Können Sie mir sagen, wo der Bahnhof ist?"],
    "Weißt du, dass Anna gestern angerufen hat?": ["Wisst ihr, dass Anna gestern angerufen hat?",
                                                   "Wissen Sie, dass Anna gestern angerufen hat?"],
    "Wir trinken jeden Morgen einen Kaffee.": ["Wir trinken jeden Morgen Kaffee."],
    "Ich möchte einen Kaffee bestellen.": ["Ich möchte gern einen Kaffee bestellen."],
}
_PUNCT = re.compile(r"[.,!?;:\"'„“”‚‘’«»()\-–—]")


def norm_sentence(s):
    """Lenient form for comparing typed sentences: case, punctuation, spacing and umlaut spelling (ae, oe, ue, ss)
    don't matter."""
    s = (s or "").lower().translate(str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"}))
    return re.sub(r"\s+", " ", _PUNCT.sub(" ", s)).strip()


def _full(s):
    return " ".join(s["chunks"]) + s["end"]


def accepted(sid):
    """Every full sentence that counts as right for this item."""
    s = wordorder.SENTENCES[int(sid)]
    locked = " ".join(s["chunks"][:s["lock"]])
    out = [_full(s)] + [(locked + " " + a).strip() + s["end"] for a in s["alts"]]
    return out + ALSO_RIGHT.get(_full(s), [])


def _edits(a, b):
    """Levenshtein distance, small strings only."""
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


# Which chunks hold the verbs the rule is about: the conjugated verb, and the end of the bracket. (Questions: the
# first two chunks, so both W-questions and yes/no questions are covered.)
def _verb_chunks(s):
    last, lock = len(s["chunks"]) - 1, s["lock"]
    return {"v2": [lock], "inv": [lock], "bracket": [lock, last], "sep": [lock, last], "sub": [lock, last],
            "quest": [0, 1]}[s["rule"]]


def _verbs_placed(words, s):
    """Are the verbs where they belong, even though other parts of the sentence are in another order?"""
    sizes = [len(norm_sentence(c).split()) for c in s["chunks"]]
    for i in _verb_chunks(s):
        at = sum(sizes[:i])
        if words[at:at + sizes[i]] != norm_sentence(s["chunks"][i]).split():
            return False
    return True


def compare(answer, sid):
    """Check a typed sentence. Returns verdict "right", "typo" (one small slip in one long word: counts as right),
    "middle" (the right words with the verbs in the right place, but the other parts in an unusual order),
    "order" (all the right words, wrong order) or "words", with the words missing and the ones that don't belong."""
    s = wordorder.SENTENCES[int(sid)]
    given = norm_sentence(answer)
    locked = norm_sentence(" ".join(s["chunks"][:s["lock"]]))
    tries = [given] + ([f"{locked} {given}"] if locked and not given.startswith(locked) else [])
    goods = [norm_sentence(a) for a in accepted(sid)]
    for g in tries:
        if g in goods:
            return {"verdict": "right", "missing": [], "extra": []}
    # Words are compared in the lenient form but shown as written: the sentence's with capitals and umlauts,
    # the learner's as typed.
    spelled = {norm_sentence(w): _PUNCT.sub("", w) for a in reversed(accepted(sid)) for w in a.split()}
    typed = {norm_sentence(w): _PUNCT.sub("", w) for w in (answer or "").split() if norm_sentence(w)}
    target = goods[0].split()
    for g in tries:
        gw = g.split()
        for good in goods:
            ww = good.split()
            if len(gw) == len(ww):
                diff = [(x, y) for x, y in zip(gw, ww) if x != y]
                if len(diff) == 1 and len(diff[0][1]) >= 4 and _edits(*diff[0]) == 1:
                    return {"verdict": "typo", "missing": [], "extra": [],
                            "typo": {"given": typed.get(diff[0][0], diff[0][0]), "right": spelled.get(diff[0][1], diff[0][1])}}
            if sorted(gw) == sorted(ww):
                return {"verdict": "middle" if good == goods[0] and _verbs_placed(gw, s) else "order", "missing": [], "extra": []}
    missing, extra = list(target), []
    for w in tries[-1].split():  # with the given start added if the learner left it out
        if w in missing:
            missing.remove(w)
        else:
            extra.append(w)
    return {"verdict": "words", "missing": [spelled.get(w, w) for w in missing], "extra": [typed.get(w, w) for w in extra]}


def typed_next(rules=None, recent=()):
    q = wordorder.next_sentence(rules, recent)
    s = wordorder.SENTENCES[q["id"]]
    q["start"] = " ".join(s["chunks"][:s["lock"]])
    q["words"] = len(_full(s).split())
    return q


def typed_check(sid, answer, hinted=False):
    """Mark a typed sentence. Right answers raise the rule's skill only when the tiles weren't shown; wrong answers
    count against it, except "middle": the verb rule being practised was right, only the other parts weren't in
    the usual order, so the skill is left alone."""
    s = wordorder.SENTENCES[int(sid)]
    res = compare(answer, sid)
    right = res["verdict"] in ("right", "typo")
    if not (right and hinted) and res["verdict"] != "middle":
        decl.update_skill(f"wo:{s['rule']}", right, False)
    db.ex("INSERT INTO answers(source, topic, correct, ts, date) VALUES('verbs','Verbs: word order',?,?,?)",
          (int(right), db.now(), db.today()))
    return {**res, "correct": right, "solution": _full(s), "why": wordorder.RULES[s["rule"]][1],
            "also": accepted(sid)[1:4]}


# ---------------------------------------------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------------------------------------------
@router.get("/api/grammar")
def grammar_index():
    return index()


@router.get("/api/grammar/topic/{topic_id}")
def grammar_topic(topic_id: str):
    t = TOPIC_BY_ID.get(topic_id)
    if not t:
        raise db.UserError("There is no such grammar topic.")
    return topic_view(t)


@router.get("/api/grammar/search")
def grammar_search(q: str = ""):
    return {"ids": search(q)}


@router.get("/api/grammar/mistakes")
def grammar_mistakes(status: str = "open"):
    return {"links": mistake_links(status)}


@router.get("/api/genders/rules")
def gender_rules():
    return genderrules.progress()


@router.post("/api/wordorder/typed/next")
def wordorder_typed_next(body: dict):
    return localize({**typed_next(body.get("rules") or [], body.get("recent") or []), "progress": wordorder.progress()})


@router.post("/api/wordorder/typed/check")
def wordorder_typed_check(body: dict):
    try:
        sid = int(body.get("id"))
    except (TypeError, ValueError):
        sid = -1
    if not 0 <= sid < len(wordorder.SENTENCES):  # a bad id was a 500 error, and -1 quietly read the last sentence
        raise HTTPException(400, "No such sentence")
    answer = str(body.get("answer") or "")[:500]  # one sentence
    return localize({**typed_check(sid, answer, bool(body.get("hinted"))),
                     "progress": wordorder.progress()})
