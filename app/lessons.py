"""The built-in course, A1 to B1: lessons, their quizzes, progress and flashcards.

Lessons come from lessons_data.py (A1), lessons_a2.py (A2) and lessons_b1.py (B1, only if that file exists),
in that order. A lesson has four steps: words, a dialogue, a grammar point and a quiz. The quiz is built fresh
each time from the lesson's words (meanings both ways, der/die/das, typing) and its hand-written exercises.
A lesson counts as done at 70% or better; lessons are open in any order, the first one not done is suggested next.

The lesson format (see lessons_data.py for examples):
  id, title (German), subtitle, words ("German=English; ..."), dialogue ("Speaker|German|English" lines),
  grammar (title, text, examples "German=English; ..."), exercises ("Sentence with ___|answer|wrong|wrong" lines)
  optional: level ("A1"; taken from the file when missing), unit (an English theme name, translated in tr.js).
A lesson file may also have TEST: hand-written items for its level test, in the exercises format.

Turkish lives next to each file (lessons_a1_tr.py, lessons_a2_tr.py, lessons_b1_tr.py), lined up with the
English by position (see lessons_tr.py). When the app language is Turkish, every English text a lesson sends is
swapped for that lesson's own Turkish, else for i18n.tr(); German stays German.
"""
import json
import random
import re

from . import db, i18n, lessons_a2, lessons_data, lessons_tr
from .packs import _items, _rows

try:  # B1 is written separately; the course works without it.
    from . import lessons_b1
except ImportError:
    lessons_b1 = None

PASS = 0.7
ARTICLES = ("der", "die", "das")
PLURAL_ONLY = {"Eltern", "Geschwister", "Leute", "Ferien", "Lebensmittel", "Möbel", "Nebenkosten", "Öffnungszeiten", "Nachrichten"}
LEVEL_ORDER = ("A1", "A2", "B1")


def _load():
    lessons, tests = [], {}
    for level, mod in zip(LEVEL_ORDER, (lessons_data, lessons_a2, lessons_b1)):
        if mod is None:
            continue
        lessons += [{**l, "level": l.get("level") or level} for l in mod.LESSONS]
        tests[level] = getattr(mod, "TEST", "")
    return lessons, tests


LESSONS, TESTS = _load()
BY_ID = {l["id"]: l for l in LESSONS}
LEVELS = [lv for lv in LEVEL_ORDER if any(l["level"] == lv for l in LESSONS)]


# ---------- Turkish ----------
def _turkish_by_lesson():
    """{lesson id: {English: Turkish}} from the *_tr files that exist."""
    out = {}
    for name in ("lessons_a1_tr", "lessons_a2_tr", "lessons_b1_tr"):
        try:
            mod = __import__(f"{__package__}.{name}", fromlist=["TR"])
        except ImportError:
            continue
        for l in mod.LESSONS:
            if l["id"] in mod.TR:
                out[l["id"]] = dict(lessons_tr.pairs(l, mod.TR[l["id"]]))
    return out


TURKISH = _turkish_by_lesson()


def turkish():
    return i18n.lang() == "tr"


def tr_text(l, s, tr=True):
    """Turkish for one English text of lesson l (its own Turkish first, then the app's), or s unchanged."""
    if not tr or not s:
        return s
    own = TURKISH.get(l["id"], {}).get(s.strip())
    return own if own is not None else i18n.tr(s)


_HINT = re.compile(r"\(([^()]+)\)\s*$")


def hint(l, prompt, tr):
    """An exercise sentence with its English hint in brackets in Turkish ("(my)" -> "(benim)")."""
    return _HINT.sub(lambda m: f"({tr_text(l, m.group(1).strip())})", prompt) if tr else prompt


# ---------- content ----------
def _words(l, tr=False):
    out = []
    for de, en in _items(l["words"]):
        art, _, rest = de.partition(" ")
        noun = art in ARTICLES and bool(rest) and rest.split()[0] not in PLURAL_ONLY and rest[:1].isupper()
        out.append({"de": de, "en": tr_text(l, en, tr), "article": art if noun else "", "word": rest if noun else de})
    return out


def lesson_words(lesson_id):
    """The words a lesson teaches (dictionary form without the article)."""
    return _words(BY_ID[lesson_id])


def _grammar(l, tr):
    title, text, examples = l["grammar"]
    return tr_text(l, title, tr), tr_text(l, text, tr), [(de, tr_text(l, en, tr)) for de, en in _items(examples)]


def _subtitle(l, tr):
    return tr_text(l, l["subtitle"], tr)


def _content(l, tr=False):
    title, text, examples = _grammar(l, tr)
    return {
        "id": l["id"], "title": l["title"], "subtitle": _subtitle(l, tr), "level": l["level"], "unit": l.get("unit", ""),
        "words": _words(l, tr),
        "dialogue": [{"who": r[0], "de": r[1], "en": tr_text(l, r[2], tr)} for r in _rows(l["dialogue"])],
        "grammar": {"title": title, "text": text, "examples": [{"de": de, "en": en} for de, en in examples]},
    }


def _progress():
    return {r["lesson_id"]: r for r in db.q("SELECT * FROM lesson_progress")}


def overview():
    from . import leveltest  # the level tests build on this module
    tr = turkish()
    prog, tests = _progress(), leveltest.results()
    rows, counter = [], {}
    for n, l in enumerate(LESSONS, 1):
        p = prog.get(l["id"])
        counter[l["level"]] = counter.get(l["level"], 0) + 1
        rows.append({"id": l["id"], "n": n, "ln": counter[l["level"]], "level": l["level"], "unit": l.get("unit", ""),
                     "title": l["title"], "subtitle": _subtitle(l, tr), "done": bool(p and p["done_at"]),
                     "best": p["best"] if p else None, "total": p["total"] if p else None, "words": len(_words(l))})
    # Suggest the first lesson not done. Levels whose test is passed come last: the learner has shown they know them.
    open_ = [x for x in rows if not x["done"]]
    passed = {lv for lv, t in tests.items() if t["passed"]}
    nxt = next((x for x in open_ if x["level"] not in passed), None) or (open_[0] if open_ else None)
    levels = []
    for lv in LEVELS:
        mine = [x for x in rows if x["level"] == lv]
        t = tests.get(lv) or {"best": None, "total": None, "passed": False, "tries": 0}
        levels.append({"level": lv, "done": sum(x["done"] for x in mine), "total": len(mine), "test": t})
    return {"lessons": rows, "levels": levels, "next": nxt["id"] if nxt else None,
            "done": sum(x["done"] for x in rows), "total": len(rows)}


def brief():
    """For Home and the quick plan: the lesson to do next (finished = no lesson left)."""
    o = overview()
    nxt = next((x for x in o["lessons"] if x["id"] == o["next"]), None)
    return {"done": o["done"], "total": o["total"], "finished": nxt is None, "next": nxt}


# ---------- quizzes ----------
def word_questions(words, rnd, n_mean=3, n_german=2, n_type=2, n_art=2, pool=None):
    """Meaning, German and typing questions about these words, plus der/die/das for some nouns.
    pool: the words the wrong choices come from (default: the same words)."""
    pool = pool or words
    qs = []

    def choice(prompt, cue, right, wrong):
        wrong = list(dict.fromkeys(x for x in wrong if x != right))
        opts = [right] + rnd.sample(wrong, min(3, len(wrong)))
        rnd.shuffle(opts)
        qs.append({"kind": "choice", "group": "words", "prompt": prompt, "cue": cue, "choices": opts, "answers": [right]})

    picked = rnd.sample(words, min(n_mean + n_german + n_type, len(words)))
    for w in picked[:n_mean]:
        choice(w["de"], "What does it mean?", w["en"], [x["en"] for x in pool if x["de"] != w["de"]])
    for w in picked[n_mean:n_mean + n_german]:
        # Never offer another German word with the same meaning as a "wrong" choice.
        choice(w["en"], "Which is the German?", w["de"], [x["de"] for x in pool if x["en"] != w["en"]])
    for w in picked[n_mean + n_german:]:
        same = [x for x in pool if x["en"] == w["en"]] or [w]
        qs.append({"kind": "text", "group": "words", "prompt": w["en"], "cue": "Type it in German",
                   "answers": list(dict.fromkeys([w["de"], w["word"]] + [a for x in same for a in (x["de"], x["word"])]))})
    nouns = [w for w in words if w["article"]]
    for w in rnd.sample(nouns, min(n_art, len(nouns))):
        qs.append({"kind": "choice", "group": "articles", "prompt": f"___ {w['word']}",
                   "cue": f"der, die or das? ({w['en']})", "choices": list(ARTICLES), "answers": [w["article"]]})
    return qs


def exercise_question(l, row, rnd, tr=False):
    """A hand-written exercise line as a choice question; the cue is its lesson's grammar point."""
    opts = row[1:]
    rnd.shuffle(opts)
    return {"kind": "choice", "group": "grammar", "prompt": hint(l, row[0], tr), "cue": _grammar(l, tr)[0],
            "choices": opts, "answers": [row[1]]}


def quiz(lesson_id, seed=None, tr=None):
    """About 15 questions: {kind: choice|text, group, prompt, cue, choices, answers}."""
    l = BY_ID[lesson_id]
    tr = turkish() if tr is None else tr
    rnd = random.Random(seed)
    qs = word_questions(_words(l, tr), rnd)
    rnd.shuffle(qs)
    return qs + [exercise_question(l, r, rnd, tr) for r in _rows(l["exercises"])]


def lesson(lesson_id):
    tr = turkish()
    l = BY_ID[lesson_id]
    p = _progress().get(lesson_id)
    have = {r["front"] for r in db.q("SELECT front FROM cards")}
    c = _content(l, tr)
    idx = LESSONS.index(l)
    same = [x for x in LESSONS if x["level"] == l["level"]]
    return {**c, "n": idx + 1, "count": len(LESSONS), "ln": same.index(l) + 1, "level_count": len(same),
            "quiz": quiz(lesson_id, tr=tr), "pass": PASS,
            "done": bool(p and p["done_at"]), "best": p["best"] if p else None, "total": p["total"] if p else None,
            "cards_left": sum(1 for w in c["words"] if w["de"] not in have),
            "next": LESSONS[idx + 1]["id"] if idx + 1 < len(LESSONS) else None}


def complete(lesson_id, results):
    """results: one True/False per quiz question. Records the try and logs the answers for the stats."""
    l = BY_ID[lesson_id]
    total, right = len(results), sum(bool(x) for x in results)
    if not total:
        raise ValueError("No answers")
    passed = right / total >= PASS
    now = db.now()
    old = db.q1("SELECT * FROM lesson_progress WHERE lesson_id=?", (lesson_id,))
    better = not old or right / total >= (old["best"] or 0) / max(1, old["total"] or 1)
    best, best_total = (right, total) if better else (old["best"], old["total"])
    done_at = (old["done_at"] if old else None) or (now if passed else None)
    db.ex("INSERT INTO lesson_progress(lesson_id, best, total, tries, done_at, last_at) VALUES(?,?,?,1,?,?) "
          "ON CONFLICT(lesson_id) DO UPDATE SET best=excluded.best, total=excluded.total, tries=tries+1, "
          "done_at=excluded.done_at, last_at=excluded.last_at", (lesson_id, best, best_total, done_at, now))
    db.exmany("INSERT INTO answers(source, topic, correct, ts, date) VALUES('lesson',?,?,?,?)",
              [(f"Course: {l['title']}", int(bool(x)), now, db.today()) for x in results])
    return {"right": right, "total": total, "passed": passed, "overview": overview()}


def add_cards(lesson_id):
    """The lesson's words as flashcards, with the meaning in the app's language at the time."""
    l = BY_ID[lesson_id]
    have = {r["front"] for r in db.q("SELECT front FROM cards")}
    now = db.now()
    tags = json.dumps(["course", f"lesson:{lesson_id}", f"level:{l['level']}"], ensure_ascii=False)
    rows = [(None, None, "vocab", w["de"], w["en"], "", tags, now) for w in _words(l, turkish()) if w["de"] not in have]
    db.exmany("INSERT INTO cards(book_id, chapter_id, type, front, back, extra, tags, created_at) VALUES(?,?,?,?,?,?,?,?)", rows)
    return {"added": len(rows)}
