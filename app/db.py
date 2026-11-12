"""SQLite storage. Every helper opens its own short-lived connection, which is fine for a single-user local app."""
import datetime as dt
import os
import sqlite3
import sys
from pathlib import Path

# In the packaged Mac app the code and static files sit in the bundle (sys._MEIPASS).
ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
# The Mac app keeps the learner's data in ~/Library/Application Support; otherwise it lives next to the code.
DATA = Path(os.environ["GERMANSTUDY_DATA"]) if os.environ.get("GERMANSTUDY_DATA") else ROOT / "data"
BOOKS = DATA / "books"
THUMBS = DATA / "thumbs"
MEDIA = DATA / "media"
DB_PATH = DATA / "study.db"


class UserError(Exception):
    """A problem the user can fix; shown to them as-is."""

SCHEMA = """
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
"""

DEFAULT_SETTINGS = {
    "level": "A2",
    "native_language": "English",
    "ui_language": "en",
    "daily_minutes": "45",
    "goal": "",
    "exam_date": "",
    "model": "claude-opus-5-5",
    "effort": "medium",
    "web_search": "1",
    "new_cards_per_day": "20",
    "coach_notes": "",
    "tts_model": "gemini-3.8-flash-tts",
    "voice_a": "Kore",
    "voice_b": "Puck",
    "monthly_budget": "",
}

SEED_RESOURCES = [
    ("Easy German (YouTube)", "https://www.youtube.com/@EasyGerman", "video",
     "Street interviews with German + English subtitles. Good for listening at A2-B2."),
    ("DW Learn German", "https://learngerman.dw.com", "course",
     "Free courses A1-C1 from Deutsche Welle, including the Nicos Weg video series."),
    ("Lingolia German grammar", "https://deutsch.lingolia.com", "reading",
     "Clear grammar explanations with exercises."),
]


def now():
    return dt.datetime.now().isoformat(timespec="seconds")


DAY_START_HOUR = 4  # a study day runs 4am to 4am, so a late-night session counts for the evening before


def study_date():
    return (dt.datetime.now() - dt.timedelta(hours=DAY_START_HOUR)).date()


def today():
    return study_date().isoformat()


def connect():
    for d in (DATA, BOOKS, THUMBS, MEDIA):
        d.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init():
    with connect() as conn:
        conn.executescript(SCHEMA)
        if conn.execute("SELECT COUNT(*) FROM resources").fetchone()[0] == 0:
            conn.executemany("INSERT INTO resources(title,url,kind,notes) VALUES(?,?,?,?)", SEED_RESOURCES)
        _migrate(conn)


def _migrate(conn):
    """One-time data updates, each recorded in settings so it only runs once."""
    cols = {r[1] for r in conn.execute("PRAGMA table_info(mistakes)")}
    for col, kind in (("question", "TEXT"), ("full_correct", "TEXT"), ("book_id", "INTEGER"), ("page", "INTEGER"),
                      ("skills", "TEXT"), ("learned_at", "TEXT"), ("learned_by", "TEXT")):
        if col not in cols:  # columns added after the Mistake Book first shipped
            conn.execute(f"ALTER TABLE mistakes ADD COLUMN {col} {kind}")
    done = {r[0] for r in conn.execute("SELECT key FROM settings WHERE key LIKE 'migrated_%'")}
    if "migrated_text_size_10" not in done:
        # Typed answers were 11pt, a bit larger than most textbook text; new boxes are 10pt.
        conn.execute("UPDATE annotations SET data = json_set(data, '$.size', 10) "
                     "WHERE kind = 'text' AND json_extract(data, '$.size') = 11")
        conn.execute("INSERT INTO settings(key, value) VALUES('migrated_text_size_10', '1')")
    if "migrated_day_starts_4am" not in done:
        # Activity used to be dated by the calendar day; re-date it so days run 4am to 4am.
        shift = f"-{DAY_START_HOUR} hours"
        for table, col in (("reading", "ts"), ("reviews", "ts"), ("answers", "ts"), ("activity", "ts"),
                           ("plans", "created_at")):
            conn.execute(f"UPDATE {table} SET date = date({col}, ?) WHERE {col} IS NOT NULL", (shift,))
        conn.execute("INSERT INTO settings(key, value) VALUES('migrated_day_starts_4am', '1')")
    if "migrated_mistakes_backfill" not in done:
        # Seed the Mistake Book with wrong answers from practice sets done before it existed.
        conn.execute("INSERT INTO mistakes(source, topic, wrong, correct, explanation, context, created_at, last_seen) "
                     "SELECT 'practice', topic, user_answer, trim(substr(answer || '|', 1, instr(answer || '|', '|') - 1)), "
                     "feedback, prompt, answered_at, answered_at FROM exercises WHERE correct = 0 AND user_answer IS NOT NULL")
        conn.execute("INSERT INTO settings(key, value) VALUES('migrated_mistakes_backfill', '1')")


def q(sql, args=()):
    with connect() as conn:
        return [dict(r) for r in conn.execute(sql, args).fetchall()]


def q1(sql, args=()):
    rows = q(sql, args)
    return rows[0] if rows else None


def ex(sql, args=()):
    conn = connect()
    try:
        with conn:
            cur = conn.execute(sql, args)
            return cur.lastrowid
    finally:
        conn.close()


def exmany(sql, rows):
    conn = connect()
    try:
        with conn:
            conn.executemany(sql, rows)
    finally:
        conn.close()


def add_mistakes(source, items):
    """items: dicts with topic, wrong, correct, explanation, context, and ideally question (the full task:
    instruction + sentence with ___ for the gap), full_correct (that sentence answered correctly), book_id, page.
    Repeating the same mistake on the same question bumps its count instead of adding a new entry."""
    ts = now()
    for m in items:
        wrong, correct = (m.get("wrong") or "").strip(), (m.get("correct") or "").strip()
        if not wrong or not correct or wrong.lower() == correct.lower():
            continue
        question = (m.get("question") or "").strip()
        same = q1("SELECT id FROM mistakes WHERE status='open' AND lower(wrong)=lower(?) AND lower(correct)=lower(?) "
                  "AND COALESCE(question, '') = ?", (wrong, correct, question))
        if same:
            ex("UPDATE mistakes SET times = times + 1, last_seen=? WHERE id=?", (ts, same["id"]))
        else:
            ex("INSERT INTO mistakes(source, topic, wrong, correct, explanation, context, created_at, last_seen, "
               "question, full_correct, book_id, page) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
               (source, (m.get("topic") or "").strip(), wrong, correct, (m.get("explanation") or "").strip(),
                (m.get("context") or "").strip(), ts, ts, question, (m.get("full_correct") or "").strip(),
                m.get("book_id"), m.get("page")))


def get_settings():
    s = dict(DEFAULT_SETTINGS)
    for r in q("SELECT key, value FROM settings"):
        s[r["key"]] = r["value"]
    return s


def set_setting(key, value):
    ex("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
       (key, str(value)))
