"""Cloud backup for Plus: the study database (progress, cards, answers, notes, everything written on books) is
copied, compressed and stored in the account's private folder on our server. Books themselves (the PDF files)
stay on the computer; they're large and the learner already has them.

Backups are made once a day when the setting is on, and by hand any time. The newest KEEP are kept.
Restoring works like a local restore: the current data is backed up on this computer first, so it can be undone."""
import datetime as dt
import gzip
import re
import shutil
import tempfile
import threading
from pathlib import Path

import httpx

from . import account, backup, db

BUCKET = "backups"
KEEP = 5
EVERY_HOURS = 20
NAME = re.compile(r"^\d{8}-\d{6}\.db\.gz$")
_lock = threading.Lock()


class CloudError(db.UserError):
    pass


def _base():
    return f"{account.SUPABASE_URL}/storage/v1/object"


def _auth():
    t = account.token()
    uid = account.user_id()
    if not t or not uid:
        raise CloudError("Sign in under Settings → Account & Plus to use cloud backup.")
    return {"apikey": account.PUBLISHABLE_KEY, "authorization": f"Bearer {t}"}, uid


def _fail(r, what):
    try:
        msg = r.json().get("message") or r.json().get("error") or r.text
    except ValueError:
        msg = r.text
    if r.status_code in (401, 403) or "row-level security" in str(msg):
        raise CloudError(f"Couldn't {what}: cloud backup is part of Plus.")
    raise CloudError(f"Couldn't {what} ({r.status_code}). Try again later.")


def listing():
    """The account's cloud backups, newest first: [{name, created, size}]."""
    h, uid = _auth()
    try:
        r = httpx.post(f"{_base()}/list/{BUCKET}", headers=h, timeout=20,
                       json={"prefix": uid, "limit": 100, "sortBy": {"column": "name", "order": "desc"}})
    except httpx.HTTPError:
        raise CloudError("Couldn't reach the backup server. Check your internet connection.")
    if r.status_code >= 400:
        _fail(r, "list your cloud backups")
    out = []
    for f in r.json():
        if NAME.match(f.get("name") or ""):
            stamp = dt.datetime.strptime(f["name"][:15], "%Y%m%d-%H%M%S")
            out.append({"name": f["name"], "created": stamp.isoformat(timespec="seconds"),
                        "size": (f.get("metadata") or {}).get("size")})
    return sorted(out, key=lambda b: b["name"], reverse=True)


def _delete(names):
    if not names:
        return
    h, uid = _auth()
    r = httpx.request("DELETE", f"{_base()}/{BUCKET}", headers=h, timeout=20, json={"prefixes": [f"{uid}/{n}" for n in names]})
    if r.status_code >= 400:
        _fail(r, "remove old cloud backups")


def make():
    """Upload a compressed copy of the study database now, then keep only the newest KEEP."""
    with _lock:
        h, uid = _auth()
        name = f"{dt.datetime.now():%Y%m%d-%H%M%S}.db.gz"
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            snap = Path(tmp) / "study.db"
            backup._copy(db.DB_PATH, snap)
            gz = Path(tmp) / name
            with open(snap, "rb") as src, gzip.open(gz, "wb", compresslevel=6) as dst:
                shutil.copyfileobj(src, dst)
            data = gz.read_bytes()
        try:
            r = httpx.post(f"{_base()}/{BUCKET}/{uid}/{name}", headers={**h, "content-type": "application/gzip", "x-upsert": "false"},
                           content=data, timeout=120)
        except httpx.HTTPError:
            raise CloudError("Couldn't reach the backup server. Check your internet connection.")
        if r.status_code >= 400:
            _fail(r, "save the cloud backup")
        db.set_setting("cloud_backup_last", dt.datetime.now().isoformat(timespec="seconds"))
        try:
            _delete([b["name"] for b in listing()[KEEP:]])
        except CloudError as e:  # pruning can wait until next time
            print("cloud prune failed:", e)
        return {"made": name, "size": len(data)}


def restore(name):
    """Replace the study data on this computer with a cloud backup (after a local safety copy)."""
    if not NAME.match(name or ""):
        raise CloudError("That isn't a cloud backup.")
    with _lock:
        h, uid = _auth()
        try:
            r = httpx.get(f"{_base()}/authenticated/{BUCKET}/{uid}/{name}", headers=h, timeout=120)
        except httpx.HTTPError:
            raise CloudError("Couldn't reach the backup server. Check your internet connection.")
        if r.status_code >= 400:
            _fail(r, "download that cloud backup")
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
            snap = Path(tmp) / "study.db"
            try:
                snap.write_bytes(gzip.decompress(r.content))
            except (OSError, EOFError):
                raise CloudError("That cloud backup is damaged and wasn't used.")
            backup._check(snap)
            safety = backup.make("before-restore")
            backup._copy(snap, db.DB_PATH)
        db.init()  # brings a backup from an older version up to date
        return {"restored": name, "safety_copy": safety}


def delete_all():
    """Remove every cloud backup of the signed-in account (used before deleting the account)."""
    try:
        names = [b["name"] for b in listing()]
    except CloudError:
        return 0
    for i in range(0, len(names), 50):
        _delete(names[i:i + 50])
    return len(names)


def status():
    s = db.get_settings()
    return {"enabled": s.get("cloud_backup") == "1", "last": s.get("cloud_backup_last") or None, "keep": KEEP}


def due():
    s = db.get_settings()
    if s.get("cloud_backup") != "1":
        return False
    last = s.get("cloud_backup_last")
    if not last:
        return True
    try:
        return dt.datetime.now() - dt.datetime.fromisoformat(last) >= dt.timedelta(hours=EVERY_HOURS)
    except ValueError:
        return True


def auto():
    """At start-up, in the background: back up if it's on, due, and the account has Plus. Never raises."""
    def run():
        try:
            if due() and account.plus_active():
                make()
        except Exception as e:
            print("automatic cloud backup failed:", e)
    threading.Thread(target=run, daemon=True).start()
