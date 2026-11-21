"""The "Export all my data" download: one .zip with everything the learner made, in formats any computer can open.

Unlike the backup file (backup.py), which is for loading back into this app, this is for the learner to keep,
look through or take elsewhere: a copy of the study database, CSV spreadsheets of the important tables, the
imported books and audio, and a README explaining it all.

The zip is written to a temporary file and streamed, so large books never sit in memory. Only the database and
the books and media folders are read; .env (the API keys) and the account session file are never touched, and
setting names that look like secrets are removed from the database copy as a second safety net.
"""
import csv
import datetime as dt
import io
import os
import re
import sqlite3
import tempfile
import zipfile
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from . import backup, db, known
from .version import VERSION

router = APIRouter()

FILE_DIRS = ("books", "media")  # the learner's imported books and audio (page pictures are rebuilt from the books)
SECRET = re.compile(r"key|token|secret|password", re.I)
# Already-compressed files are stored as they are; squeezing them again only costs time.
STORED = {".pdf", ".mp3", ".m4a", ".aac", ".ogg", ".webm", ".jpg", ".jpeg", ".png", ".zip"}

README = """Deutsch lernen - all your data
Exported {created} from Deutsch lernen {version}.

study.db
  A copy of your whole study database (SQLite). Any SQLite viewer can open it, for example
  "DB Browser for SQLite". To use it in Deutsch lernen again, use Settings > Backups > Load backup file
  with a backup file instead; this export is for keeping and reading.

csv/  (spreadsheets; open them with Excel, LibreOffice or Google Sheets)
  flashcards.csv         every flashcard with its schedule: when it is due, the interval in days,
                         stability (days until you'd have a 90% chance of remembering it), difficulty (1-10),
                         successful reviews in a row (reps) and how often you missed it (lapses).
                         Cards with the tag "ai" were written by AI.
  flashcard_reviews.csv  every grade you gave a card (1 Again, 2 Hard, 3 Good, 4 Easy) and when.
  known_words.csv        the German words the app tracks for you: known, learning, seen or ignored.
  writings.csv           your texts from the writing desk, with their score. The feedback was written by AI.
  mistakes.csv           your Mistake Book. Explanations were written by AI.
  reading_history.csv    time spent on each page of your books.
  activity.csv           time spent studying, by kind of activity.
  answers.csv            every exercise answer, right or wrong, by topic.

books/  the books and texts you imported.
media/  your audio: listening episodes and audio you imported.

Your API keys and your account sign-in are never included in this export.
"""


def _csv(rows, columns):
    """CSV text with a header. UTF-8 with a BOM, so Excel shows umlauts correctly."""
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(columns)
    for r in rows:
        w.writerow(["" if r.get(c) is None else r.get(c) for c in columns])
    return "﻿" + out.getvalue()


def _known_rows():
    statuses = known.statuses()  # first: it also creates the known-words tables if needed
    names = {r["lemma"]: r for r in db.q("SELECT * FROM known_words")}
    rows = []
    for w, st in sorted(statuses.items()):

        r = names.get(w) or {}
        rows.append({"word": w, "status": known.NAMES.get(st, st), "source": r.get("source") or "flashcards",
                     "times_seen": r.get("seen") or 0, "first_seen": r.get("first_seen"), "updated_at": r.get("updated_at")})
    return rows


def tables():
    """{file name: CSV text} for the csv/ folder."""
    return {
        "flashcards.csv": _csv(db.q(
            "SELECT c.id, c.type, c.front, c.back, c.extra, c.tags, b.title AS book, ch.title AS chapter, c.created_at, "
            "c.due, c.interval AS interval_days, c.stability, c.difficulty, c.reps, c.lapses, c.ease "
            "FROM cards c LEFT JOIN books b ON b.id = c.book_id LEFT JOIN chapters ch ON ch.id = c.chapter_id ORDER BY c.id"),
            ["id", "type", "front", "back", "extra", "tags", "book", "chapter", "created_at", "due", "interval_days",
             "stability", "difficulty", "reps", "lapses", "ease"]),
        "flashcard_reviews.csv": _csv(db.q(
            "SELECT r.ts, r.date, r.card_id, c.front, r.grade, r.seconds, r.was_new FROM reviews r "
            "LEFT JOIN cards c ON c.id = r.card_id ORDER BY r.id"),
            ["ts", "date", "card_id", "front", "grade", "seconds", "was_new"]),
        "known_words.csv": _csv(_known_rows(), ["word", "status", "source", "times_seen", "first_seen", "updated_at"]),
        "writings.csv": _csv(db.q("SELECT * FROM writings ORDER BY id"),
                             ["id", "created_at", "title", "kind", "level", "task", "text", "words", "seconds", "score",
                              "result"]),
        "mistakes.csv": _csv(db.q("SELECT * FROM mistakes ORDER BY id"),
                             ["id", "created_at", "last_seen", "source", "topic", "question", "wrong", "correct",
                              "full_correct", "explanation", "context", "times", "status", "learned_at"]),
        "reading_history.csv": _csv(db.q(
            "SELECT r.ts, r.date, b.title AS book, r.page, r.seconds FROM reading r "
            "LEFT JOIN books b ON b.id = r.book_id ORDER BY r.id"), ["ts", "date", "book", "page", "seconds"]),
        "activity.csv": _csv(db.q("SELECT ts, date, kind, seconds FROM activity ORDER BY id"),
                             ["ts", "date", "kind", "seconds"]),
        "answers.csv": _csv(db.q("SELECT ts, date, source, topic, correct FROM answers ORDER BY id"),
                            ["ts", "date", "source", "topic", "correct"]),
    }


def _scrub_secrets(path):
    con = sqlite3.connect(path)
    try:
        with con:
            gone = [k for (k,) in con.execute("SELECT key FROM settings").fetchall() if SECRET.search(k)]
            con.executemany("DELETE FROM settings WHERE key = ?", [(k,) for k in gone])
        # Rewrite the file so nothing deleted (here or earlier in the app) is left readable in its free pages.
        con.execute("VACUUM")

    finally:
        con.close()



def build(dest):
    """Write the export zip to dest."""
    created = dt.datetime.now().isoformat(timespec="seconds")
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        snap = Path(tmp) / "study.db"
        backup._copy(db.DB_PATH, snap)
        _scrub_secrets(snap)
        with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("README.txt", README.format(created=created, version=VERSION).replace("\n", "\r\n"))
            z.write(snap, "study.db")
            for name, text in tables().items():
                z.writestr(f"csv/{name}", text)
            for d in FILE_DIRS:
                base = db.DATA / d
                if not base.exists():
                    continue
                for p in sorted(base.rglob("*")):
                    if p.is_file() and not p.is_symlink() and not p.name.startswith("."):
                        kind = zipfile.ZIP_STORED if p.suffix.lower() in STORED else zipfile.ZIP_DEFLATED
                        z.write(p, f"{d}/{p.relative_to(base).as_posix()}", compress_type=kind)  # copied in chunks
    return dest


@router.get("/api/export/all")
def export_all():
    fd, tmp = tempfile.mkstemp(suffix=".zip")
    os.close(fd)
    try:
        build(tmp)
    except Exception:
        os.unlink(tmp)
        raise
    return FileResponse(tmp, media_type="application/zip", background=BackgroundTask(os.unlink, tmp),
                        filename=f"Deutsch-lernen-my-data-{dt.date.today():%Y-%m-%d}.zip")
