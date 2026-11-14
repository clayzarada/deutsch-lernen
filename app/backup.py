"""Backups of the study database: one automatically each day the app starts, plus any made by hand.
Kept in data/backups; the newest 14 automatic ones are kept. Books (PDF files) are not copied: they only change
when you import or delete one, and everything you write on them lives in the database.

A full backup file (export_file / import_file) is different: one .zip with the database AND the books, page
pictures and audio, to keep somewhere safe or move to another computer. API keys are never in it."""
import datetime as dt
import json
import re
import shutil
import sqlite3
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

from . import db
from .version import VERSION

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
    _check(path)
    safety = make("before-restore")
    _copy(path, db.DB_PATH)
    db.init()  # brings an older backup up to date with the current app
    return {"restored": name, "safety_copy": safety}


def _check(path):
    """Make sure a file is a database of this app before it replaces anything."""
    con = sqlite3.connect(path)
    try:
        tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    except sqlite3.DatabaseError:
        raise db.UserError("That file isn't a readable backup.")
    finally:
        con.close()  # (an open file can't be deleted on Windows)
    if not NEEDED_TABLES <= tables:
        raise db.UserError("That file doesn't look like a backup of this app.")


# ---------- full backup files ----------
APP_ID = "deutsch-lernen"
FILE_DIRS = ("books", "thumbs", "media")  # the folders in the data folder that belong to the learner's work


def export_file(dest):
    """Write everything the learner made to one zip at dest: the database plus books, page pictures and audio."""
    dest = Path(dest)
    with tempfile.TemporaryDirectory() as tmp:
        snap = Path(tmp) / "study.db"
        _copy(db.DB_PATH, snap)
        with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("manifest.json", json.dumps({"app": APP_ID, "version": VERSION,
                                                    "created": dt.datetime.now().isoformat(timespec="seconds")}, indent=2))
            z.write(snap, "study.db")
            for d in FILE_DIRS:
                base = db.DATA / d
                if base.exists():
                    for p in sorted(base.rglob("*")):
                        if p.is_file():
                            z.write(p, f"{d}/{p.relative_to(base).as_posix()}")
    return dest


def _allowed(name):
    """Only the database and files inside the learner's folders, never a path that climbs out of them."""
    if name in ("manifest.json", "study.db"):
        return True
    p = PurePosixPath(name)
    return (len(p.parts) >= 2 and p.parts[0] in FILE_DIRS and not p.is_absolute() and ".." not in p.parts
            and "\\" not in name and ":" not in name)


def import_file(src):
    """Replace the current data with a full backup file. What's there now is backed up first, so it can be undone."""
    try:
        z = zipfile.ZipFile(src)
    except (zipfile.BadZipFile, OSError):
        raise db.UserError("That file isn't a Deutsch lernen backup (it should be a .zip made with \"Save backup file\").")
    with z, tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        names = [i.filename for i in z.infolist() if not i.is_dir()]
        try:
            manifest = json.loads(z.read("manifest.json"))
        except (KeyError, ValueError):
            manifest = {}
        if manifest.get("app") != APP_ID or "study.db" not in names:
            raise db.UserError("That file isn't a Deutsch lernen backup (it should be a .zip made with \"Save backup file\").")
        bad = [n for n in names if not _allowed(n)]
        if bad:
            raise db.UserError("That backup file contains things it shouldn't, so it wasn't used.")
        z.extract("study.db", tmp)
        snap = Path(tmp) / "study.db"
        _check(snap)
        safety = make("before-restore")
        files = 0
        for n in names:
            if n.split("/")[0] in FILE_DIRS:
                target = db.DATA / n
                target.parent.mkdir(parents=True, exist_ok=True)
                with z.open(n) as r, open(target, "wb") as w:
                    shutil.copyfileobj(r, w)
                files += 1
        _copy(snap, db.DB_PATH)
    db.init()  # brings a backup from an older version up to date
    return {"restored": manifest.get("created"), "from_version": manifest.get("version"), "files": files,
            "safety_copy": safety}
