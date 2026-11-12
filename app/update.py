"""Tells the learner when a newer version of the app has been released.

At most once a day (and only when asked by the page, after it has loaded) the app asks GitHub for the newest
release: one small request that gives up after a few seconds. The answer is cached in the settings table, so
opening the app many times a day still means one check. Offline or any error: nothing is shown, nothing breaks.

Updating itself is a fresh download: the learner's data lives outside the app folder, so it is kept.
"""
import datetime as dt
import json
import re
import urllib.request

from . import db
from .version import VERSION

REPO = "clayzarada/deutsch-lernen"
API = f"https://api.github.com/repos/{REPO}/releases/latest"
DOWNLOAD_PAGE = "https://zaradaholdingsgroup.com/lab/"
CHECK_EVERY = dt.timedelta(hours=24)
TIMEOUT_S = 4


def _parse(v):
    """'v0.1.10' -> (0, 1, 10), so 0.1.10 counts as newer than 0.1.9."""
    nums = [int(x) for x in re.findall(r"\d+", v or "")[:3]]
    return tuple(nums + [0] * (3 - len(nums)))


def _fetch():
    req = urllib.request.Request(API, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": f"deutsch-lernen/{VERSION}"})
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as r:
        j = json.load(r)
    return {"tag": j.get("tag_name", ""), "notes": (j.get("body") or "")[:2000],
            "published": j.get("published_at", ""), "url": j.get("html_url", "")}


def status(force=False):
    s = db.get_settings()
    cached = None
    try:
        cached = json.loads(s.get("update_cache") or "null")
    except ValueError:
        pass
    now = dt.datetime.now()
    fresh = cached and now - dt.datetime.fromisoformat(cached["checked_at"]) < CHECK_EVERY
    if force or not fresh:
        try:
            cached = {**_fetch(), "checked_at": now.isoformat(timespec="seconds")}
            db.set_setting("update_cache", json.dumps(cached))
        except Exception as e:  # offline, GitHub slow or down: try again next time, say nothing
            print("update check failed:", e)
            if force:
                return {"current": VERSION, "ok": False}
    if not cached:
        return {"current": VERSION, "ok": False}
    latest = cached["tag"].lstrip("v")
    return {"current": VERSION, "ok": True, "latest": latest, "newer": _parse(latest) > _parse(VERSION),
            "notes": cached["notes"], "published": cached["published"], "download": DOWNLOAD_PAGE,
            "checked_at": cached["checked_at"]}
