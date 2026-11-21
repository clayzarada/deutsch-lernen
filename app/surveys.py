"""In-app questions from the developer, and a small weekly usage summary to compare the answers with.

Questions come from the `surveys` table on our server; the sidebar shows a (!) until the learner answers or skips.
Answers carry this copy's random install id and, when signed in, the account id. The weekly summary (days studied,
minutes, cards reviewed, exercises answered, lessons done) is sent once a week unless turned off in Settings.
Nothing here ever blocks or breaks the app: all network trouble is swallowed."""
import datetime as dt
import json
import threading
import time
import uuid

import httpx

from . import account, db
from .version import VERSION

CACHE_SECONDS = 1800
_cache = {"at": 0, "list": []}


def install_id():
    """A random id for this copy of the app (not tied to the person unless they sign in)."""
    s = db.get_settings()
    iid = s.get("install_id")
    if not iid:
        iid = uuid.uuid4().hex
        db.set_setting("install_id", iid)
    return iid


def _who():
    """(headers, account id or None): the account only when its session is valid, so the server accepts it."""
    t = account.token() if account._load() else None
    h = {"apikey": account.PUBLISHABLE_KEY, "content-type": "application/json",
         "authorization": f"Bearer {t or account.PUBLISHABLE_KEY}"}
    return h, (account.user_id() if t else None)


def _headers():
    return _who()[0]


def _done():
    try:
        return set(json.loads(db.get_settings().get("surveys_done") or "[]"))
    except ValueError:
        return set()


def _mark_done(sid):
    done = _done() | {sid}
    db.set_setting("surveys_done", json.dumps(sorted(done)))


def pending(force=False):
    """Open questions this copy hasn't answered or skipped yet. Cached; [] when offline."""
    if force or time.time() - _cache["at"] > CACHE_SECONDS:
        try:
            r = httpx.get(f"{account.SUPABASE_URL}/rest/v1/surveys", headers=_headers(), timeout=10,
                          params={"select": "id,title,question,kind,options,allow_comment", "order": "created_at.asc"})
            if r.status_code == 200 and isinstance(r.json(), list):
                _cache.update(at=time.time(), list=r.json())
        except Exception:
            _cache["at"] = time.time()  # offline: try again later, keep what we had
    done = _done()
    return [s for s in _cache["list"] if s.get("id") not in done]


def answer(survey_id, choice=None, comment=None, skipped=False):
    """Send an answer (or a skip). Marked done locally even if sending fails, so the learner isn't asked again."""
    known = {s["id"]: s for s in _cache["list"]}
    if survey_id not in known:
        raise db.UserError("That question isn't open any more.")
    s = known[survey_id]
    if not skipped:
        ids = [str(o.get("id")) for o in s.get("options") or []]
        if s["kind"] in ("choice", "image_choice") and str(choice) not in ids:
            raise db.UserError("Pick one of the options.")
        if s["kind"] == "rating" and str(choice) not in {"1", "2", "3", "4", "5"}:
            raise db.UserError("Pick a rating from 1 to 5.")
        if s["kind"] == "text" and not (comment or "").strip():
            raise db.UserError("Write a short answer, or skip.")
    h, uid = _who()
    row = {"survey_id": survey_id, "install_id": install_id(), "user_id": uid,
           "answer": None if skipped or choice is None else str(choice), "comment": (comment or "").strip()[:2000] or None,
           "skipped": bool(skipped), "app_version": VERSION}
    _mark_done(survey_id)
    try:
        httpx.post(f"{account.SUPABASE_URL}/rest/v1/survey_answers", json=row, timeout=10,
                   headers={**h, "prefer": "return=minimal"})
    except Exception as e:
        print("survey answer not sent:", e)
    return {"ok": True, "pending": pending()}


# ---------- weekly usage summary ----------

def _week_start(day=None):
    day = day or dt.date.today()
    return day - dt.timedelta(days=day.weekday())


def summary(week=None):
    """Numbers for the 7 days before `week` (a Monday): how much the app was used, no content."""
    end = week or _week_start()
    start = end - dt.timedelta(days=7)
    a, b = start.isoformat(), end.isoformat()
    days = db.q("SELECT date FROM reading WHERE date>=? AND date<? UNION SELECT date FROM reviews WHERE date>=? AND date<? "
                "UNION SELECT date FROM answers WHERE date>=? AND date<? UNION SELECT date FROM activity WHERE date>=? AND date<?",
                (a, b) * 4)
    secs = db.q1("SELECT COALESCE(SUM(s),0) AS s FROM (SELECT seconds AS s FROM reading WHERE date>=? AND date<? "
                 "UNION ALL SELECT seconds FROM reviews WHERE date>=? AND date<? UNION ALL SELECT seconds FROM activity "
                 "WHERE date>=? AND date<?)", (a, b) * 3)["s"] or 0
    first = db.q1("SELECT MIN(d) AS d FROM (SELECT MIN(date) AS d FROM reviews UNION ALL SELECT MIN(date) FROM answers "
                  "UNION ALL SELECT MIN(date) FROM activity UNION ALL SELECT MIN(date) FROM reading)")["d"]
    s = db.get_settings()
    import os
    return {
        "week": start.isoformat(),
        "days_active": len(days),
        "minutes": int(secs // 60),
        "cards_reviewed": db.q1("SELECT COUNT(*) AS n FROM reviews WHERE date>=? AND date<?", (a, b))["n"],
        "answers": db.q1("SELECT COUNT(*) AS n FROM answers WHERE date>=? AND date<?", (a, b))["n"],
        "lessons_done": db.q1("SELECT COUNT(*) AS n FROM lesson_progress WHERE done_at IS NOT NULL")["n"],
        "total_cards": db.q1("SELECT COUNT(*) AS n FROM cards")["n"],
        "first_use": first,
        "app_version": VERSION,
        "ui_language": s.get("ui_language"),
        "nav_layout": s.get("nav_layout"),
        "has_own_key": bool(os.environ.get("ANTHROPIC_API_KEY", "").strip()),
    }


def send_weekly():
    """Once a week (on the first start after a Monday), if sharing is on. Returns True when sent."""
    s = db.get_settings()
    if s.get("share_usage") != "1" or s.get("onboarded") != "1":
        return False  # only with the learner's yes
    week = _week_start()
    if s.get("usage_sent_week") == week.isoformat():
        return False
    h, uid = _who()
    row = {**summary(week), "install_id": install_id(), "user_id": uid}
    try:
        r = httpx.post(f"{account.SUPABASE_URL}/rest/v1/usage_summaries", json=row, timeout=10,
                       headers={**h, "prefer": "return=minimal"})
    except Exception:
        return False
    if r.status_code < 300 or r.status_code == 409:
        db.set_setting("usage_sent_week", week.isoformat())
        return True
    return False


def start_background():
    def run():
        try:
            send_weekly()
            pending(force=True)
        except Exception as e:
            print("survey/usage check failed:", e)
    threading.Thread(target=run, daemon=True).start()
