"""Level tests: one test at the end of each course level (A1, A2, B1), built from that level's lessons.

A test mixes the level's words (meanings both ways, typing, der/die/das), one hand-written exercise from many of
its lessons and the level's own test items (TEST in its lesson file). It works for any level that has lessons, so
the B1 test appears by itself once lessons_b1.py is there. 75% passes the level; every try is kept as the best score.
"""
import random

from fastapi import APIRouter, HTTPException

from . import db, lessons
from .packs import _rows

PASS = 0.75
N_GRAMMAR = 14   # lesson exercises per test (one each from this many lessons)
N_OWN = 10       # hand-written test items per test

SCHEMA = """
CREATE TABLE IF NOT EXISTS level_tests(level TEXT PRIMARY KEY, best INTEGER, total INTEGER, tries INTEGER DEFAULT 0,
  passed_at TEXT, last_at TEXT);
"""
router = APIRouter()


def _init():
    # Every time (it's cheap): a restored backup may be a database from before level tests existed.
    conn = db.connect()
    try:
        conn.executescript(SCHEMA)
    finally:
        conn.close()


def results():
    """{level: {best, total, passed, tries}} for the levels tried so far."""
    _init()
    return {r["level"]: {"best": r["best"], "total": r["total"], "passed": bool(r["passed_at"]), "tries": r["tries"]}
            for r in db.q("SELECT * FROM level_tests")}


def _level_lessons(level):
    return [l for l in lessons.LESSONS if l["level"] == level]


def build(level, seed=None, tr=False):
    """About 35 questions in the lesson quiz format."""
    ls = _level_lessons(level)
    if not ls:
        raise KeyError(level)
    rnd = random.Random(seed)
    words = list({w["de"]: w for l in ls for w in lessons._words(l, tr)}.values())
    qs = lessons.word_questions(words, rnd, n_mean=4, n_german=3, n_type=3, n_art=4)
    for l in sorted(rnd.sample(ls, min(N_GRAMMAR, len(ls))), key=ls.index):
        qs.append(lessons.exercise_question(l, rnd.choice(_rows(l["exercises"])), rnd, tr))
    # The level's own items, under a "Mixed grammar" cue; their English hints are translated by i18n.tr().
    mixed = {"id": f"{level}-test", "grammar": ("Mixed grammar", "", "")}
    own = _rows(lessons.TESTS.get(level) or "")
    for r in rnd.sample(own, min(N_OWN, len(own))):
        qs.append(lessons.exercise_question(mixed, r, rnd, tr))
    rnd.shuffle(qs)
    return qs


def test(level):
    r = results().get(level) or {"best": None, "total": None, "passed": False, "tries": 0}
    return {"level": level, "quiz": build(level, tr=lessons.turkish()), "pass": PASS, "lessons": len(_level_lessons(level)), **r}


def complete(level, answers):
    """answers: one True/False per question. Keeps the best score; passing once keeps the level passed."""
    _init()
    total, right = len(answers), sum(bool(x) for x in answers)
    if not total:
        raise ValueError("No answers")
    passed = right / total >= PASS
    now = db.now()
    old = db.q1("SELECT * FROM level_tests WHERE level=?", (level,))
    better = not old or right / total >= (old["best"] or 0) / max(1, old["total"] or 1)
    best, best_total = (right, total) if better else (old["best"], old["total"])
    passed_at = (old["passed_at"] if old else None) or (now if passed else None)
    db.ex("INSERT INTO level_tests(level, best, total, tries, passed_at, last_at) VALUES(?,?,?,1,?,?) "
          "ON CONFLICT(level) DO UPDATE SET best=excluded.best, total=excluded.total, tries=tries+1, "
          "passed_at=excluded.passed_at, last_at=excluded.last_at", (level, best, best_total, passed_at, now))
    db.exmany("INSERT INTO answers(source, topic, correct, ts, date) VALUES('lesson',?,?,?,?)",
              [(f"Course: {level} test", int(bool(x)), now, db.today()) for x in answers])
    return {"right": right, "total": total, "passed": passed, "overview": lessons.overview()}


# ---------- routes ----------
def _check(level):
    if level not in lessons.LEVELS:
        raise HTTPException(404, "No such level")


@router.get("/api/levels/{level}/test")
def level_test(level: str):
    _check(level)
    return test(level)


@router.post("/api/levels/{level}/test/complete")
def level_test_complete(level: str, body: dict):
    _check(level)
    try:
        return complete(level, body.get("results") or [])
    except ValueError as e:
        raise HTTPException(400, str(e))
