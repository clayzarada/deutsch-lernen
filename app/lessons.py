"""The built-in beginner course: lessons from lessons_data.py, their quizzes, progress and flashcards.

A lesson has four steps: words, a dialogue, a grammar point and a quiz. The quiz is built fresh each time from
the lesson's words (meanings both ways, der/die/das, typing) and its hand-written exercises. A lesson counts
as done at 70% or better; lessons are open in any order, the first one not done is suggested next.
"""
import json
import random

from . import db
from .lessons_data import LESSONS
from .packs import _items, _rows

PASS = 0.7
ARTICLES = ("der", "die", "das")
PLURAL_ONLY = {"Eltern", "Geschwister"}
BY_ID = {l["id"]: l for l in LESSONS}


def _words(l):
    out = []
    for de, en in _items(l["words"]):
        art, _, rest = de.partition(" ")
        noun = art in ARTICLES and bool(rest) and rest.split()[0] not in PLURAL_ONLY and rest[:1].isupper()
        out.append({"de": de, "en": en, "article": art if noun else "", "word": rest if noun else de})
    return out


def _content(l):
    title, text, examples = l["grammar"]
    return {
        "id": l["id"], "title": l["title"], "subtitle": l["subtitle"], "words": _words(l),
        "dialogue": [{"who": r[0], "de": r[1], "en": r[2]} for r in _rows(l["dialogue"])],
        "grammar": {"title": title, "text": text, "examples": [{"de": de, "en": en} for de, en in _items(examples)]},
    }


def _progress():
    return {r["lesson_id"]: r for r in db.q("SELECT * FROM lesson_progress")}


def overview():
    prog = _progress()
    out, next_id = [], None
    for n, l in enumerate(LESSONS, 1):
        p = prog.get(l["id"])
        done = bool(p and p["done_at"])
        if not done and next_id is None:
            next_id = l["id"]
        out.append({"id": l["id"], "n": n, "title": l["title"], "subtitle": l["subtitle"], "done": done,
                    "best": p["best"] if p else None, "total": p["total"] if p else None,
                    "words": len(_words(l))})
    return {"lessons": out, "next": next_id, "done": sum(x["done"] for x in out), "total": len(out)}


def brief():
    """For Home and the quick plan: the lesson to do next (finished = no lesson left)."""
    o = overview()
    nxt = next((x for x in o["lessons"] if x["id"] == o["next"]), None)
    return {"done": o["done"], "total": o["total"], "finished": nxt is None, "next": nxt}


def quiz(lesson_id, seed=None):
    """About 15 questions: {kind: choice|text, group, prompt, cue, choices, answers}."""
    l = BY_ID[lesson_id]
    rnd = random.Random(seed)
    words = _words(l)
    qs = []

    def choice(prompt, cue, right, wrong):
        opts = [right] + rnd.sample(wrong, min(3, len(wrong)))
        rnd.shuffle(opts)
        qs.append({"kind": "choice", "group": "words", "prompt": prompt, "cue": cue, "choices": opts, "answers": [right]})

    picked = rnd.sample(words, min(7, len(words)))
    for w in picked[:3]:
        choice(w["de"], "What does it mean?", w["en"], [x["en"] for x in words if x["en"] != w["en"]])
    for w in picked[3:5]:
        choice(w["en"], "Which is the German?", w["de"], [x["de"] for x in words if x["de"] != w["de"]])
    for w in picked[5:7]:
        qs.append({"kind": "text", "group": "words", "prompt": w["en"], "cue": "Type it in German",
                   "answers": list(dict.fromkeys([w["de"], w["word"]]))})
    nouns = [w for w in words if w["article"]]
    for w in rnd.sample(nouns, min(2, len(nouns))):
        qs.append({"kind": "choice", "group": "articles", "prompt": f"___ {w['word']}",
                   "cue": f"der, die or das? ({w['en']})", "choices": list(ARTICLES), "answers": [w["article"]]})
    rnd.shuffle(qs)
    for r in _rows(l["exercises"]):
        opts = r[1:]
        rnd.shuffle(opts)
        qs.append({"kind": "choice", "group": "grammar", "prompt": r[0], "cue": l["grammar"][0],
                   "choices": opts, "answers": [r[1]]})
    return qs


def lesson(lesson_id):
    l = BY_ID[lesson_id]
    p = _progress().get(lesson_id)
    have = {r["front"] for r in db.q("SELECT front FROM cards")}
    c = _content(l)
    idx = LESSONS.index(l)
    return {**c, "n": idx + 1, "count": len(LESSONS), "quiz": quiz(lesson_id), "pass": PASS,
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
    l = BY_ID[lesson_id]
    have = {r["front"] for r in db.q("SELECT front FROM cards")}
    now = db.now()
    tags = json.dumps(["course", f"lesson:{lesson_id}"], ensure_ascii=False)
    rows = [(None, None, "vocab", w["de"], w["en"], "", tags, now) for w in _words(l) if w["de"] not in have]
    db.exmany("INSERT INTO cards(book_id, chapter_id, type, front, back, extra, tags, created_at) VALUES(?,?,?,?,?,?,?,?)", rows)
    return {"added": len(rows)}
