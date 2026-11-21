"""Backend quality checks for 3.0: an old 2.4 database still opens, the app starts without optional files, the
reading room's word look-ups stay fast, and malformed requests get a 400 instead of a crash."""
import datetime as dt
import io
import os
import sqlite3
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import pytest

from app import db, dictionary, known, readingroom, srs

ROOT = Path(__file__).resolve().parent.parent

# The database as Deutsch lernen 2.4 left it: app/db.py SCHEMA at tag v2.4.0, copied word for word (cards have no
# stability or difficulty yet, and none of the 3.0 tables exist).
V24_SCHEMA = """
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS books(
  id INTEGER PRIMARY KEY, title TEXT, filename TEXT, page_count INTEGER,
  last_page INTEGER DEFAULT 1, created_at TEXT);
CREATE TABLE IF NOT EXISTS chapters(
  id INTEGER PRIMARY KEY, book_id INTEGER REFERENCES books(id) ON DELETE CASCADE,
  ord INTEGER, title TEXT, start_page INTEGER, end_page INTEGER);
CREATE TABLE IF NOT EXISTS annotations(
  id INTEGER PRIMARY KEY, book_id INTEGER REFERENCES books(id) ON DELETE CASCADE,
  page INTEGER, kind TEXT, x REAL, y REAL, data TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS reading(
  id INTEGER PRIMARY KEY, book_id INTEGER, page INTEGER, seconds INTEGER, ts TEXT, date TEXT);
CREATE TABLE IF NOT EXISTS activity(
  id INTEGER PRIMARY KEY, kind TEXT, seconds INTEGER, ts TEXT, date TEXT);
CREATE TABLE IF NOT EXISTS exercise_sets(
  id INTEGER PRIMARY KEY, book_id INTEGER REFERENCES books(id) ON DELETE CASCADE,
  chapter_id INTEGER, title TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS exercises(
  id INTEGER PRIMARY KEY, set_id INTEGER REFERENCES exercise_sets(id) ON DELETE CASCADE,
  ord INTEGER, type TEXT, topic TEXT, instructions TEXT, prompt TEXT, options TEXT,
  answer TEXT, explanation TEXT, user_answer TEXT, correct INTEGER, feedback TEXT, answered_at TEXT);
CREATE TABLE IF NOT EXISTS answers(
  id INTEGER PRIMARY KEY, source TEXT, topic TEXT, correct INTEGER, ts TEXT, date TEXT);
CREATE TABLE IF NOT EXISTS cards(
  id INTEGER PRIMARY KEY, book_id INTEGER, chapter_id INTEGER, type TEXT,
  front TEXT, back TEXT, extra TEXT, tags TEXT, due TEXT,
  interval REAL DEFAULT 0, ease REAL DEFAULT 2.5, reps INTEGER DEFAULT 0, lapses INTEGER DEFAULT 0,
  created_at TEXT);
CREATE TABLE IF NOT EXISTS reviews(
  id INTEGER PRIMARY KEY, card_id INTEGER, grade INTEGER, seconds INTEGER, was_new INTEGER, ts TEXT, date TEXT);
CREATE TABLE IF NOT EXISTS media(
  id INTEGER PRIMARY KEY, book_id INTEGER, chapter_id INTEGER, title TEXT, source TEXT,
  filename TEXT, mime TEXT, seconds REAL, script TEXT, listens INTEGER DEFAULT 0, created_at TEXT);
CREATE TABLE IF NOT EXISTS mistakes(
  id INTEGER PRIMARY KEY, source TEXT, topic TEXT, wrong TEXT, correct TEXT, explanation TEXT, context TEXT,
  times INTEGER DEFAULT 1, status TEXT DEFAULT 'open', card_id INTEGER, created_at TEXT, last_seen TEXT,
  question TEXT, full_correct TEXT, book_id INTEGER, page INTEGER);
CREATE TABLE IF NOT EXISTS decl_skills(
  key TEXT PRIMARY KEY, seen INTEGER DEFAULT 0, correct INTEGER DEFAULT 0, box INTEGER DEFAULT 0,
  due TEXT, last_ms INTEGER, last_seen TEXT, wrong_last INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS decl_progress(
  stage TEXT, step TEXT, done_at TEXT, best INTEGER, PRIMARY KEY(stage, step));
CREATE TABLE IF NOT EXISTS decl_log(key TEXT, date TEXT, correct INTEGER);
CREATE INDEX IF NOT EXISTS decl_log_key ON decl_log(key, date);
CREATE TABLE IF NOT EXISTS api_usage(
  id INTEGER PRIMARY KEY, ts TEXT, date TEXT, feature TEXT, provider TEXT, model TEXT, input_tokens INTEGER,
  output_tokens INTEGER, cache_read INTEGER, cache_write INTEGER, web_searches INTEGER, cost REAL);
CREATE TABLE IF NOT EXISTS writings(
  id INTEGER PRIMARY KEY, created_at TEXT, date TEXT, task_id TEXT, title TEXT, kind TEXT, level TEXT, task TEXT,
  text TEXT, words INTEGER, seconds INTEGER, score INTEGER, result TEXT);
CREATE TABLE IF NOT EXISTS resources(id INTEGER PRIMARY KEY, title TEXT, url TEXT, kind TEXT, notes TEXT);
CREATE TABLE IF NOT EXISTS plans(id INTEGER PRIMARY KEY, date TEXT, data TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS coach_messages(id INTEGER PRIMARY KEY, role TEXT, content TEXT, ts TEXT);
CREATE TABLE IF NOT EXISTS lesson_progress(lesson_id TEXT PRIMARY KEY, best INTEGER, total INTEGER, tries INTEGER DEFAULT 0,
  done_at TEXT, last_at TEXT);
CREATE TABLE IF NOT EXISTS page_checks(book_id INTEGER, page INTEGER, data TEXT, checked_at TEXT,
  PRIMARY KEY(book_id, page));
"""


def _make_v24_db(path):
    con = sqlite3.connect(path)
    with con:
        con.executescript(V24_SCHEMA)
        for k, v in (("level", "A2"), ("onboarded", "1"), ("migrated_text_size_10", "1"),
                     ("migrated_day_starts_4am", "1"), ("migrated_mistakes_backfill", "1")):
            con.execute("INSERT INTO settings(key, value) VALUES(?,?)", (k, v))
        now = dt.datetime.now().isoformat(timespec="seconds")
        due = (dt.datetime.now() + dt.timedelta(days=4)).isoformat(timespec="seconds")
        con.execute("INSERT INTO books(id, title, filename, page_count, created_at) VALUES(1,'Lehrbuch','b.pdf',10,?)",
                    (now,))
        con.execute("INSERT INTO chapters(id, book_id, ord, title, start_page, end_page) VALUES(1,1,1,'Kapitel 1',1,5)")
        # SM-2 cards: one in review (made by AI, so it has topic tags only), one still learning, one new.
        con.execute("INSERT INTO cards(id, book_id, chapter_id, type, front, back, tags, due, interval, ease, reps, "
                    "lapses, created_at) VALUES(1,1,1,'vocab','der Hund','dog','[\"Tiere\"]',?,12,2.3,4,1,?)", (due, now))
        con.execute("INSERT INTO cards(id, type, front, back, due, interval, ease, reps, lapses, created_at) "
                    "VALUES(2,'vocab','die Katze','cat',?,0.0069,2.5,0,1,?)", (due, now))
        con.execute("INSERT INTO cards(id, type, front, back, created_at) VALUES(3,'vocab','das Pferd','horse',?)", (now,))
        today = db.today()
        con.execute("INSERT INTO reviews(card_id, grade, seconds, was_new, ts, date) VALUES(1,3,5,0,?,?)", (now, today))
        con.execute("INSERT INTO answers(source, topic, correct, ts, date) VALUES('declension','Dativ',1,?,?)",
                    (now, today))
        con.execute("INSERT INTO decl_log(key, date, correct) VALUES('def:dat:m', ?, 1)", (today,))
        con.execute("INSERT INTO writings(created_at, date, level, title, text, words, score) "
                    "VALUES(?,?,'A2','Mein Tag','Heute ist schön.',3,70)", (now, today))
        con.execute("INSERT INTO lesson_progress(lesson_id, best, total, tries, done_at, last_at) "
                    "VALUES('hallo',10,10,1,?,?)", (now, now))
    con.close()


@pytest.fixture
def other_db():
    """Point the app at another database file for one test, then back at the usual one."""
    usual = db.DB_PATH

    def use(path):
        db.DB_PATH = path
        db.init()  # what start-up (or loading a file as a backup) does
    yield use
    db.DB_PATH = usual
    db.init()


def _v24_path():
    path = Path(tempfile.mkdtemp(prefix="dl-v24-")) / "study.db"
    _make_v24_db(path)
    return path


PAGES = ("/api/settings", "/api/stats", "/api/progress", "/api/plan/today", "/api/level", "/api/level/brief",
         "/api/known", "/api/readingroom", "/api/lessons", "/api/levels/A1/test", "/api/review/queue",
         "/api/grammar", "/api/genders/rules", "/api/grammar/mistakes")


@pytest.mark.parametrize("ui", ["en", "tr"])
def test_a_2_4_database_opens_and_every_main_page_works(client, other_db, ui):
    other_db(_v24_path())
    db.set_setting("ui_language", ui)
    cols = {r["name"] for r in db.q("PRAGMA table_info(cards)")}
    assert {"stability", "difficulty"} <= cols
    hund = db.q1("SELECT * FROM cards WHERE id=1")
    assert hund["stability"] == 12 and 1 <= hund["difficulty"] <= 10 and hund["interval"] == 12
    assert "ai" in hund["tags"]
    assert db.q1("SELECT stability FROM cards WHERE id=2")["stability"] == srs.W[0]  # still learning
    assert db.q1("SELECT stability FROM cards WHERE id=3")["stability"] is None  # never reviewed
    for url in PAGES:
        r = client.get(url)
        assert r.status_code == 200, (url, r.text[:300])
    lvl = client.get("/api/level").json()
    assert lvl["known"]["known"] == 0 and lvl["known"]["learning"] == 2  # Hund (reviewed) and Katze (learning)
    r = client.post("/api/review/1", json={"grade": 3}).json()
    assert r["card"]["interval"] >= 12 and r["card"]["stability"] > 12
    assert client.post("/api/readingroom/finished", json={"key": "a1-mein-tag", "seconds": 300}).status_code == 200
    z = zipfile.ZipFile(io.BytesIO(client.get("/api/export/all").content))
    assert "csv/known_words.csv" in z.namelist()


def test_empty_database_every_main_page_works(client, other_db):
    other_db(Path(tempfile.mkdtemp(prefix="dl-empty-")) / "study.db")
    for url in PAGES:
        r = client.get(url)
        assert r.status_code == 200, (url, r.text[:300])
    lvl = client.get("/api/level").json()
    assert all(s["level"] is None for s in lvl["skills"]) and lvl["verdict"]["ready"] is None


def test_tables_come_back_after_restoring_an_old_backup(client, other_db):
    """known.py and levels.py make their tables once; after a restore (db.init) they must make them again."""
    known.statuses()
    client.get("/api/level")
    other_db(_v24_path())
    assert client.post("/api/known/mark", json={"lemmas": ["Haus"], "status": 3}).status_code == 200
    assert client.post("/api/level/check/start").status_code == 200


def test_app_starts_without_the_b1_lessons(tmp_path):
    """lessons_b1.py is optional: without it the app must still start, with A1 and A2 only."""
    code = """
import importlib.abc, sys
class NoB1(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path, target=None):
        if name in ("app.lessons_b1", "app.lessons_b1_tr"):
            raise ModuleNotFoundError(name)
sys.meta_path.insert(0, NoB1())
from fastapi.testclient import TestClient
from app.main import app
from app import lessons
assert lessons.LEVELS == ["A1", "A2"], lessons.LEVELS
with TestClient(app) as c:
    for url in ("/api/lessons", "/api/levels/A1/test", "/api/level", "/api/stats"):
        assert c.get(url).status_code == 200, url
    assert c.get("/api/levels/B1/test").status_code == 404
    c.put("/api/settings", json={"ui_language": "tr"})
    assert c.get("/api/lessons").status_code == 200
print("ok")
"""
    env = {**os.environ, "GERMANSTUDY_DATA": str(tmp_path / "data"), "GERMANSTUDY_ENV": str(tmp_path / ".env")}
    r = subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=env, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0 and "ok" in r.stdout, r.stderr[-2000:]


# ---------- known words ----------

def test_passing_a_lesson_marks_phrases_and_plural_nouns(client):
    db.init()
    known._init()
    db.ex("DELETE FROM known_words")
    last = db.q1("SELECT COALESCE(MAX(id), 0) AS n FROM answers")["n"]
    for lid in ("familie", "morgens"):
        n = len(client.get(f"/api/lessons/{lid}").json()["quiz"])
        assert client.post(f"/api/lessons/{lid}/complete", json={"results": [True] * n}).json()["passed"]
    s = known.statuses(["Eltern", "waschen", "duschen", "Mutter"])
    assert all(v == known.LEARNING for v in s.values()), s
    db.ex("DELETE FROM known_words")
    db.ex("DELETE FROM lesson_progress")
    db.ex("DELETE FROM answers WHERE id > ?", (last,))  # other tests count the course's answers


def test_marking_many_words_is_one_quick_write():
    db.init()
    known._init()
    words = [f"testwort{i}" for i in range(400)]
    known.saw(words)
    known.mark(words[:200], known.KNOWN)
    s = known.statuses(words)
    assert sum(v == known.KNOWN for v in s.values()) == 200 and sum(v == known.SEEN for v in s.values()) == 200
    known.saw(words[:1])
    assert db.q1("SELECT seen FROM known_words WHERE lemma='testwort0'")["seen"] == 2
    known.mark(words[:1], known.SEEN, "lesson")  # lessons never lower a status
    assert known.statuses(words[:1]) == {"testwort0": known.KNOWN}
    db.ex("DELETE FROM known_words WHERE lemma LIKE 'testwort%'")


# ---------- dictionary look-ups (the reading room tokenizes thousands of words) ----------

@pytest.mark.skipif(not dictionary.available(), reason="no offline dictionary")
def test_compound_lookup_uses_the_word_index():
    plan = dictionary._con().execute(
        "EXPLAIN QUERY PLAN SELECT * FROM word WHERE word = ? COLLATE NOCASE AND word = ? AND pos = 'noun' "
        "AND gender != '' ORDER BY rank LIMIT 1", ("Spieler", "Spieler")).fetchall()
    assert any("INDEX" in str(tuple(r)) for r in plan), [tuple(r) for r in plan]
    c = dictionary.compound("Kaffeetassenschrank")
    assert c and c["gender"] == "m" and c["compound"][1] == "Schrank"


@pytest.mark.skipif(not dictionary.available(), reason="no offline dictionary")
def test_lemma_of_agrees_with_lookup():
    text = readingroom._lib_text(readingroom.TEXTS[0]) + " Kaffeetassenschrank Häuser ging schönen Lehrerin"
    for w in set(known._WORD.findall(text)):
        found = dictionary.lookup(w, 1)
        assert dictionary.lemma_of(w) == ((found[0]["word"], found[0]["pos"]) if found else (None, None)), w


# ---------- malformed requests ----------

def test_bad_requests_get_a_400_not_a_crash(client):
    cid = client.post("/api/cards", json={"front": "der Tisch", "back": "table"}).json()["id"]
    for g in (0, 5, -1):
        assert client.post(f"/api/review/{cid}", json={"grade": g}).status_code == 400
    client.delete(f"/api/cards/{cid}")
    for sid in ("x", -1, 10 ** 6, None):
        assert client.post("/api/wordorder/typed/check", json={"id": sid, "answer": "Ich gehe."}).status_code == 400
    assert client.post("/api/level/check/answer", json={"id": "abc", "answer": "x"}).status_code == 404
    r = client.post("/api/known/mark", json={"lemmas": ["x" * 5000], "status": 3}).json()
    assert list(r["statuses"]) == ["x" * 100]
    db.ex("DELETE FROM known_words WHERE lemma = ?", ("x" * 100,))
