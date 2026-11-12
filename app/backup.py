"""Backups of the study database: one automatically each day the app starts, plus any made by hand.
Kept in data/backups; the newest 14 automatic ones are kept. Books (PDF files) are not copied: they only change
when you import or delete one, and everything you write on them lives in the database."""
import datetime as dt
import re
import sqlite3

from . import db

KEEP_AUTO = 14
NAME = re.compile(r"^[\w.\- ]+\.db$")
NEEDED_TABLES = {"settings", "books", "cards", "answers"}


def folder():
    d = db.DATA / "backups"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _copy(src, dst):
    """SQLite's own backup copy: safe while the app is using the database."""
    a, b = sqlite3.connect(src), sqlite3.connect(dst)
    try:
        with b:
            a.backup(b)
    finally:
        a.close()
        b.close()


def make(label="manual"):
    path = folder() / f"study.{dt.datetime.now():%Y-%m-%d_%H%M%S}.{label}.db"
    _copy(db.DB_PATH, path)
    return path.name


def daily():
    """Called at start-up: back up once per calendar day, then prune old automatic backups."""
    if not db.DB_PATH.exists():
        return None
    today = f"{dt.date.today():%Y-%m-%d}"
    made = None
    if not any(p.name.startswith(f"study.{today}") for p in folder().glob("*.auto.db")):
        made = make("auto")
    autos = sorted(folder().glob("study.*.auto.db"), key=lambda p: p.name, reverse=True)
    for old in autos[KEEP_AUTO:]:
        old.unlink(missing_ok=True)
    return made


def listing():
    out = []
    for p in folder().glob("*.db"):
        st = p.stat()
        kind = "auto" if p.name.endswith(".auto.db") else "before-restore" if ".before-restore." in p.name else "manual"
        out.append({"name": p.name, "kind": kind, "size": st.st_size,
                    "created": dt.datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds")})
    return sorted(out, key=lambda b: b["created"], reverse=True)


def restore(name):
    """Replace the current data with a backup. The current data is backed up first, so this can be undone."""
    if not NAME.match(name or ""):
        raise db.UserError("That isn't a backup file.")
    path = folder() / name
    if not path.exists():
        raise db.UserError("That backup doesn't exist any more.")
    try:
        con = sqlite3.connect(path)
        tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        con.close()
    except sqlite3.DatabaseError:
        raise db.UserError("That file isn't a readable backup.")
    if not NEEDED_TABLES <= tables:
        raise db.UserError("That file doesn't look like a backup of this app.")
    safety = make("before-restore")
    _copy(path, db.DB_PATH)
    db.init()  # brings an older backup up to date with the current app
    return {"restored": name, "safety_copy": safety}
