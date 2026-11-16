"""Deutsch lernen account (for Plus): sign in with an emailed code, keep the session on this computer, and ask
the server whether Plus is active. Plus AI requests go to our server function instead of straight to Anthropic,
so a Plus user needs no API key of their own.

The project URL and publishable key below are public by design (they identify the project; the database's
row-level security decides what each signed-in user may read)."""
import base64
import json
import os
import urllib.parse
import threading
import time

import httpx

from . import db

SUPABASE_URL = os.environ.get("DL_SUPABASE_URL", "https://zarusstgbgyvongoterq.supabase.co").rstrip("/")
PUBLISHABLE_KEY = os.environ.get("DL_SUPABASE_KEY", "sb_publishable_xPcjPWnIT6H0QuWmZ6PL8w_l-i949nV")
AI_BASE_URL = SUPABASE_URL + "/functions/v1/ai"
PADDLE_URL = SUPABASE_URL + "/functions/v1/paddle"
CHECKOUT_URL = os.environ.get("DL_CHECKOUT_URL", "https://deutschlernenapp.com/checkout/")
# Whether Plus can be bought yet. A file on the website, so sales open for everyone without an app update.
PLUS_INFO_URL = os.environ.get("DL_PLUS_INFO_URL", "https://deutschlernenapp.com/plus.json")
_sales = {"at": 0, "open": False}
SESSION_FILE = db.DATA / "account.json"
STATUS_TTL = 600  # seconds between plan checks

_lock = threading.Lock()
_status = {"at": 0, "data": None}


class AccountError(db.UserError):
    pass


def _headers(token=None):
    h = {"apikey": PUBLISHABLE_KEY, "content-type": "application/json"}
    if token:
        h["authorization"] = f"Bearer {token}"
    return h


def _msg(r):
    try:
        j = r.json()
        return j.get("msg") or j.get("error_description") or j.get("message") or (j.get("error") or {}).get("message") or r.text
    except Exception:
        return r.text or f"HTTP {r.status_code}"


def _load():
    try:
        return json.loads(SESSION_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _save(sess):
    if sess is None:
        SESSION_FILE.unlink(missing_ok=True)
    else:
        SESSION_FILE.write_text(json.dumps(sess), encoding="utf-8")


def _from_auth(j):
    return {"access_token": j["access_token"], "refresh_token": j["refresh_token"],
            "expires_at": int(j.get("expires_at") or time.time() + int(j.get("expires_in") or 3600)),
            "email": (j.get("user") or {}).get("email")}


# ---------- sign in ----------

def send_code(email, redirect_to=None):
    """Emails a sign-in link (and a code, once the email template includes one). The link opens redirect_to,
    this app's /auth/callback page, which hands the session back to the app."""
    email = (email or "").strip().lower()
    if "@" not in email:
        raise AccountError("Enter a valid email address.")
    params = {"redirect_to": redirect_to} if redirect_to else None
    try:
        r = httpx.post(f"{SUPABASE_URL}/auth/v1/otp", headers=_headers(), params=params,
                       json={"email": email, "create_user": True}, timeout=20)
    except httpx.HTTPError:
        raise AccountError("Couldn't reach the account server. Check your internet connection.")
    if r.status_code >= 400:
        if r.status_code == 429:
            raise AccountError("Too many sign-in emails just now. Wait a minute and try again.")
        raise AccountError(f"Couldn't send the code: {_msg(r)}")
    return {"sent": True, "email": email}


def verify(email, code):
    email = (email or "").strip().lower()
    code = "".join(ch for ch in (code or "") if ch.isdigit())
    if not code:
        raise AccountError("Enter the code from the email.")
    try:
        r = httpx.post(f"{SUPABASE_URL}/auth/v1/verify", headers=_headers(), json={"type": "email", "email": email, "token": code}, timeout=20)
    except httpx.HTTPError:
        raise AccountError("Couldn't reach the account server. Check your internet connection.")
    if r.status_code >= 400:
        raise AccountError("That code didn't work or has expired. Request a new one.")
    with _lock:
        _save(_from_auth(r.json()))
        _status.update(at=0, data=None)
    return status(force=True)


def set_session(access_token, refresh_token, expires_at=None):
    """Session from the emailed sign-in link (the callback page passes the tokens on)."""
    if not access_token or not refresh_token:
        raise AccountError("The sign-in link was incomplete. Request a new one.")
    try:
        r = httpx.get(f"{SUPABASE_URL}/auth/v1/user", headers=_headers(access_token), timeout=20)
    except httpx.HTTPError:
        raise AccountError("Couldn't reach the account server. Check your internet connection.")
    if r.status_code >= 400:
        raise AccountError("That sign-in link has expired. Request a new one.")
    try:
        exp = int(expires_at)
    except (TypeError, ValueError):
        exp = int(time.time()) + 3600
    with _lock:
        _save({"access_token": access_token, "refresh_token": refresh_token, "expires_at": exp, "email": r.json().get("email")})
        _status.update(at=0, data=None)
    return status(force=True)


def sign_out():
    with _lock:
        sess = _load()
        if sess:
            try:
                httpx.post(f"{SUPABASE_URL}/auth/v1/logout", headers=_headers(sess["access_token"]), timeout=10)
            except httpx.HTTPError:
                pass
        _save(None)
        _status.update(at=0, data=None)
    return status()


def token():
    """A valid access token, refreshed when it's close to expiring; None when signed out."""
    with _lock:
        sess = _load()
        if not sess:
            return None
        if sess.get("expires_at", 0) - time.time() > 120:
            return sess["access_token"]
        try:
            r = httpx.post(f"{SUPABASE_URL}/auth/v1/token?grant_type=refresh_token", headers=_headers(),
                           json={"refresh_token": sess["refresh_token"]}, timeout=20)
        except httpx.HTTPError:
            return sess["access_token"]  # offline: let the request fail with a clear message
        if r.status_code >= 400:
            _save(None)  # refresh token revoked or expired: signed out
            return None
        new = _from_auth(r.json())
        new["email"] = new["email"] or sess.get("email")
        _save(new)
        return new["access_token"]


def user_id():
    """The account's id, read from the signed-in session (the token's "sub")."""
    sess = _load()
    try:
        payload = sess["access_token"].split(".")[1]
        return json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))["sub"]
    except Exception:
        return None


def checkout_link(plan):
    """The website checkout page for this account; the purchase is tied to the account by its id."""
    uid = user_id()
    if not uid:
        raise AccountError("Sign in first.")
    plan = plan if plan in ("monthly", "yearly") else "yearly"
    return {"url": CHECKOUT_URL + "?" + urllib.parse.urlencode({"plan": plan, "uid": uid, "email": (_load() or {}).get("email") or ""})}


def portal_link():
    """A link to Paddle's page for changing or cancelling the subscription."""
    t = token()
    if not t:
        raise AccountError("You're not signed in.")
    try:
        r = httpx.post(f"{PADDLE_URL}/portal", headers=_headers(t), json={}, timeout=20)
    except httpx.HTTPError:
        raise AccountError("Couldn't reach the account server. Check your internet connection.")
    j = {}
    try:
        j = r.json()
    except ValueError:
        pass
    if r.status_code >= 400 or not j.get("url"):
        raise AccountError(j.get("error") or "Couldn't open subscription settings. Try again later.")
    return {"url": j["url"]}


def delete_account():
    t = token()
    if not t:
        raise AccountError("You're not signed in.")
    # Stop any subscription first, so nobody is charged for an account that no longer exists.
    try:
        r = httpx.post(f"{PADDLE_URL}/cancel", headers=_headers(t), json={}, timeout=30)
    except httpx.HTTPError:
        raise AccountError("Couldn't reach the account server, so the account wasn't deleted. Check your internet connection.")
    if r.status_code >= 400:
        try:
            msg = r.json().get("error")
        except ValueError:
            msg = None
        raise AccountError(msg or "Couldn't cancel your subscription, so the account wasn't deleted. Try again later.")
    from . import cloud
    try:
        cloud.delete_all()  # backups next: the server can't remove them once the account is gone
    except Exception as e:
        raise AccountError(f"Couldn't remove your cloud backups, so the account wasn't deleted: {e}")
    t = token()
    r = httpx.post(f"{SUPABASE_URL}/rest/v1/rpc/delete_my_account", headers=_headers(t), json={}, timeout=20)
    if r.status_code >= 400:
        raise AccountError(f"Couldn't delete the account: {_msg(r)}")
    with _lock:
        _save(None)
        _status.update(at=0, data=None)
    return status()


# ---------- plan ----------

def sales_open():
    """True once Plus is on sale (checked at most every few minutes; False when offline)."""
    if time.time() - _sales["at"] < STATUS_TTL:
        return _sales["open"]
    try:
        _sales["open"] = bool(httpx.get(PLUS_INFO_URL, timeout=8).json().get("sales_open"))
    except Exception:
        pass  # offline or unreachable: keep the last known answer
    _sales["at"] = time.time()
    return _sales["open"]


def status(force=False):
    """{signed_in, email, plus, used_usd, cap_usd, used_pct, sales_open}. Cached; never raises."""
    return {**_account_status(force), "sales_open": sales_open()}


def _account_status(force=False):
    sess = _load()
    if not sess:
        return {"signed_in": False, "plus": False}
    if not force and _status["data"] and time.time() - _status["at"] < STATUS_TTL:
        return _status["data"]
    base = {"signed_in": True, "email": sess.get("email"), "plus": False}
    t = token()
    if not t:
        return {"signed_in": False, "plus": False}
    try:
        r = httpx.get(f"{AI_BASE_URL}/status", headers=_headers(t), timeout=15)
        data = {**base, **r.json(), "signed_in": True} if r.status_code == 200 else {**base, "error": _msg(r)}
    except (httpx.HTTPError, ValueError):
        cached = _status["data"]
        return {**(cached or base), "offline": True}
    _status.update(at=time.time(), data=data)
    return data


def plus_active():
    return bool(status().get("plus"))


def forget_status():
    _status.update(at=0, data=None)
