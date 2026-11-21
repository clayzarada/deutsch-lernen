"""Reading room: short texts at the learner's level, read LingQ-style on top of the known-words record.

The built-in library lives in readers_data.py. The learner's own texts (pasted, imported from a .txt file or written
by AI on request) are kept in reading_texts, and each finished read is logged in reading_finished. Reading time
itself goes into the shared activity table (kind "reading") from the page, like every other page's study time, so
the planner, the stats and the streak count it without any extra code.
"""
import random
import re

from fastapi import APIRouter, HTTPException

from . import ai, db, known
from .readers_data import BY_ID, LEVELS, TEXTS

router = APIRouter()

MAX_CHARS = 20_000  # about 3,000 words: plenty for one sitting, and keeps tokenizing quick
MAX_TITLE = 120
WORDS_PER_MINUTE = 100  # a learner's careful reading pace, for the "about N min" hint
AI_LEVELS = ("A1", "A2", "B1", "B2", "C1")
STORY_WORDS = {"A1": "120-160", "A2": "200-280", "B1": "320-420", "B2": "400-500", "C1": "450-550"}
STORY_GRAMMAR = {
    "A1": "present tense only, short main clauses, nominative and accusative, a few common dative phrases",
    "A2": "Perfekt for past events, modal verbs, the dative, simple weil/dass/wenn clauses",
    "B1": "Präteritum for narration, subordinate clauses, some Konjunktiv II and passive",
    "B2": "varied tenses and clause types, passive, Konjunktiv II, some idioms",
    "C1": "rich, natural style with complex sentences and idiomatic language",
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS reading_texts(
  id INTEGER PRIMARY KEY, title TEXT, level TEXT, topic TEXT, text TEXT, source TEXT, created_at TEXT, updated_at TEXT);
CREATE TABLE IF NOT EXISTS reading_finished(
  id INTEGER PRIMARY KEY, text_key TEXT, title TEXT, words INTEGER, seconds INTEGER, ts TEXT, date TEXT,
  level TEXT, known_pct INTEGER);
"""


def _init():
    # Cheap, and runs every time so the tables come back after a backup from before the reading room is restored.
    with db.connect() as conn:
        conn.executescript(SCHEMA)
        cols = {r[1] for r in conn.execute("PRAGMA table_info(reading_finished)")}
        for col, kind in (("level", "TEXT"), ("known_pct", "INTEGER")):  # added after the first 3.0 builds
            if col not in cols:
                conn.execute(f"ALTER TABLE reading_finished ADD COLUMN {col} {kind}")


# ---------- texts ----------

def _lib_text(t):
    return "\n\n".join(t["paragraphs"])


def _user_key(row_id):
    return f"u{row_id}"


def _get(key):
    """(text dict, full text) for a library id ("a1-mein-tag") or a user text ("u12")."""
    if key in BY_ID:
        t = BY_ID[key]
        return {"key": key, "title": t["title"], "level": t["level"], "genre": t["genre"], "topic": t["topic"],
                "summary_en": t["summary_en"], "summary_tr": t["summary_tr"], "source": "library"}, _lib_text(t)
    _init()
    m = re.fullmatch(r"u(\d+)", key or "")
    row = db.q1("SELECT * FROM reading_texts WHERE id=?", (int(m.group(1)),)) if m else None
    if not row:
        raise HTTPException(404, "That text wasn't found.")
    return {"key": key, "id": row["id"], "title": row["title"], "level": row["level"] or "", "genre": "",
            "topic": row["topic"] or "", "summary_en": "", "summary_tr": "", "source": row["source"],
            "created_at": row["created_at"]}, row["text"]


def coverages(texts):
    """{key: {"known_pct", "words", "new"}} for many texts at once. Same rule as known.coverage (known, learning
    and ignored words count as understood), but statuses are looked up once instead of once per text."""
    words = {k: known.lemmas_in(t) for k, t in texts.items()}
    st = known.statuses(set().union(*words.values())) if words else {}
    out = {}
    for k, ws in words.items():
        if not ws:
            out[k] = {"known_pct": 100, "words": 0, "new": 0}
            continue
        ok = sum(1 for w in ws if st.get(w, known.NEW) >= known.LEARNING or st.get(w) == known.IGNORED)
        new = len({w for w in ws if known.NEW <= st.get(w, known.NEW) < known.LEARNING})
        out[k] = {"known_pct": round(100 * ok / len(ws)), "words": len(ws), "new": new}
    return out


def _clean(text):
    text = (text or "").replace("\r\n", "\n").replace("\r", "\n").replace("\t", " ")
    text = re.sub(r"[  ]+\n", "\n", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _check_text(text):
    if not text:
        raise HTTPException(400, "Paste or import a text first.")
    if len(text) > MAX_CHARS:
        raise HTTPException(400, "This text is too long. The limit is 20,000 characters (about 3,000 words), "
                                 "so split it into parts.")
    if not known.lemmas_in(text):
        raise HTTPException(400, "There are no words in this text.")


def _title_from(text):
    first = text.split("\n", 1)[0].strip()
    return first[:60] + ("…" if len(first) > 60 else "")


def add_text(title, text, level="", source="user", topic=""):
    _init()
    text = _clean(text)
    _check_text(text)
    title = (title or "").strip()[:MAX_TITLE] or _title_from(text)
    level = level if level in AI_LEVELS else ""
    now = db.now()
    rid = db.ex("INSERT INTO reading_texts(title, level, topic, text, source, created_at, updated_at) "
                "VALUES(?,?,?,?,?,?,?)", (title, level, (topic or "").strip()[:80], text, source, now, now))
    return _get(_user_key(rid))[0]


def library():
    """Every text (built-in first, then the learner's own) with its length, coverage and how often it was finished."""
    _init()
    rows = db.q("SELECT * FROM reading_texts ORDER BY id DESC")
    items, texts = [], {}
    for t in TEXTS:
        meta, text = _get(t["id"])
        items.append(meta)
        texts[t["id"]] = text
    for r in rows:
        key = _user_key(r["id"])
        items.append({"key": key, "id": r["id"], "title": r["title"], "level": r["level"] or "", "genre": "",
                      "topic": r["topic"] or "", "summary_en": "", "summary_tr": "", "source": r["source"],
                      "created_at": r["created_at"]})
        texts[key] = r["text"]
    cov = coverages(texts)
    done = {r["text_key"]: r for r in db.q(
        "SELECT text_key, COUNT(*) AS n, MAX(ts) AS last FROM reading_finished GROUP BY text_key")}
    for it in items:
        c = cov[it["key"]]
        it.update(c, minutes=max(1, round(c["words"] / WORDS_PER_MINUTE)),
                  finished=done[it["key"]]["n"] if it["key"] in done else 0,
                  last_finished=done[it["key"]]["last"] if it["key"] in done else None)
    recent = db.q("SELECT text_key, title, words, seconds, ts FROM reading_finished ORDER BY id DESC LIMIT 15")
    return {"texts": items, "recent": recent, "levels": list(LEVELS), "ai_levels": list(AI_LEVELS),
            "max_chars": MAX_CHARS, "finished_total": db.q1("SELECT COUNT(*) AS n FROM reading_finished")["n"]}


def finish(key, seconds):
    _init()
    meta, text = _get(key)
    seconds = max(0, min(int(seconds or 0), 4 * 3600))
    cov = coverages({key: text})[key]  # how much the learner knew when they finished (for the level estimate)
    db.ex("INSERT INTO reading_finished(text_key, title, words, seconds, ts, date, level, known_pct) "
          "VALUES(?,?,?,?,?,?,?,?)", (key, meta["title"], cov["words"], seconds, db.now(), db.today(),
                                      meta["level"] or "", cov["known_pct"]))
    return {"ok": True, "finished": db.q1("SELECT COUNT(*) AS n FROM reading_finished WHERE text_key=?", (key,))["n"]}


def coach_summary():
    """What the coach sees: texts finished lately."""
    _init()
    return db.q("SELECT title, date, words, ROUND(seconds / 60.0) AS minutes FROM reading_finished "
                "ORDER BY id DESC LIMIT 10")


def finished_for_levels():
    """For the progress page's reading-level estimate: one entry per finished text that has a level, with how
    much of it the learner knew when they finished it."""
    _init()
    return [{"level": r["level"], "known_pct": r["known_pct"]} for r in db.q(
        "SELECT level, known_pct FROM reading_finished WHERE level <> '' AND known_pct IS NOT NULL ORDER BY id")]


try:  # the progress page's level estimate (app/levels.py) may not exist in every build
    from . import levels
    levels.register_reading_source(finished_for_levels)
except ImportError:
    pass


# ---------- AI story (optional: needs a Claude key or Plus) ----------

def write_story(level, topic):
    s = db.get_settings()
    level = level if level in AI_LEVELS else (s["level"] if s["level"] in AI_LEVELS else "A2")
    st = known.statuses()
    familiar = [w for w, v in st.items() if v >= known.LEARNING]
    random.shuffle(familiar)
    familiar = sorted(familiar[:350])
    system = ("You write short, original German reading texts (graded readers) for a language learner. "
              "The German must be natural and correct, like a good graded reader, never a word list in disguise.")
    task = (f"Write a story for CEFR level {level}, {STORY_WORDS[level]} words long.\n"
            f"Grammar for this level: {STORY_GRAMMAR[level]}.\n"
            + (f"Topic: {topic}\n" if topic else "Pick an everyday topic with a small surprise or a happy ending.\n")
            + ("Build the story mostly from words the learner already knows or is learning (listed below, in their "
               "dictionary form; use any inflected form). You may use common function words freely and about "
               "5 to 10 new words that fit the level and the topic; make their meaning clear from context.\n"
               f"Known and learning words: {', '.join(familiar)}\n" if familiar else
               "The learner has not marked many words yet, so keep the vocabulary to the most common words of the level.\n")
            + "Give a short German title and the text as a list of paragraphs (no headings, no translations, no notes).")
    out = ai.call(system, task, ai._obj({"title": ai.S, "paragraphs": ai._arr(ai.S)}), effort="low",
                  max_tokens=4000, feature="reading_story")
    text = "\n\n".join(p.strip() for p in out.get("paragraphs", []) if p.strip())
    return add_text(out.get("title", ""), text, level, "ai", topic)


# ---------- HTTP ----------

@router.get("/api/readingroom")
def api_library():
    return library()


@router.get("/api/readingroom/texts/{key}")
def api_text(key: str):
    meta, text = _get(key)
    return {**meta, "text": text}


@router.post("/api/readingroom/texts")
def api_add(body: dict):
    return add_text(str(body.get("title") or ""), str(body.get("text") or ""), str(body.get("level") or ""))


@router.put("/api/readingroom/texts/{key}")
def api_update(key: str, body: dict):
    meta, text = _get(key)
    if meta["source"] == "library":
        raise HTTPException(400, "Texts from the built-in library can't be changed.")
    title = str(body.get("title") if body.get("title") is not None else meta["title"]).strip()[:MAX_TITLE]
    if not title:
        raise HTTPException(400, "Give the text a title.")
    level = str(body.get("level") if body.get("level") is not None else meta["level"])
    level = level if level in AI_LEVELS else ""
    if body.get("text") is not None:
        text = _clean(str(body["text"]))
        _check_text(text)
    db.ex("UPDATE reading_texts SET title=?, level=?, text=?, updated_at=? WHERE id=?",
          (title, level, text, db.now(), meta["id"]))
    return _get(key)[0]


@router.delete("/api/readingroom/texts/{key}")
def api_delete(key: str):
    meta, _ = _get(key)
    if meta["source"] == "library":
        raise HTTPException(400, "Texts from the built-in library can't be changed.")
    db.ex("DELETE FROM reading_texts WHERE id=?", (meta["id"],))
    return {"ok": True}


@router.post("/api/readingroom/finished")
def api_finished(body: dict):
    return finish(str(body.get("key") or ""), body.get("seconds"))


@router.post("/api/readingroom/story")
def api_story(body: dict):
    return write_story(str(body.get("level") or ""), str(body.get("topic") or "").strip()[:200])
