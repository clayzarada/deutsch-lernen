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
BILLING_URL = SUPABASE_URL + "/functions/v1/billing"  # Stripe
CHECKOUT_URL = os.environ.get("DL_CHECKOUT_URL", "https://deutschlernenapp.com/checkout/")
# Whether Plus can be bought yet, and through whom ("provider": "stripe" or "paddle"). A file on the website, so
# sales open, or move to another payment provider, for everyone without an app update.
PLUS_INFO_URL = os.environ.get("DL_PLUS_INFO_URL", "https://deutschlernenapp.com/plus.json")
_sales = {"at": 0, "open": False, "provider": "paddle"}
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
        tmp = SESSION_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(sess), encoding="utf-8")
        os.replace(tmp, SESSION_FILE)


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
    # Remember who asked, so a link can only sign in the person who typed their email here (see set_session).
    db.set_setting("signin_pending", json.dumps({"email": email, "at": time.time()}))
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


PENDING_SECONDS = 2 * 3600


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
        pending = json.loads(db.get_settings().get("signin_pending") or "{}")
    except ValueError:
        pending = {}
    email = (r.json().get("email") or "").lower()
    if not pending or time.time() - pending.get("at", 0) > PENDING_SECONDS or email != pending.get("email"):
        raise AccountError("This sign-in link wasn't requested from this app. Ask for a new one under Settings → Account & Plus.")
    db.set_setting("signin_pending", "")
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
        if r.status_code in (400, 401, 403):
            _save(None)  # refresh token revoked or expired: signed out
            return None
        if r.status_code >= 400:
            return sess["access_token"]  # server hiccup (429, 5xx): keep the session and try again later
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


def _call(url, t, body=None, timeout=20):
    """POST to one of our server functions: (status code, JSON answer)."""
    try:
        r = httpx.post(url, headers=_headers(t), json=body or {}, timeout=timeout)
    except httpx.HTTPError:
        raise AccountError("Couldn't reach the account server. Check your internet connection.")
    try:
        j = r.json()
    except ValueError:
        j = {}
    return r.status_code, j if isinstance(j, dict) else {}


def checkout_link(plan):
    """Where to buy Plus for this account. With Stripe, our server makes a Stripe Checkout page tied to the account;
    with Paddle, it's the website's checkout page, which ties the purchase to the account by its id."""
    uid = user_id()
    if not uid:
        raise AccountError("Sign in first.")
    plan = plan if plan in ("monthly", "yearly") else "yearly"
    if provider() == "stripe":
        t = token()
        if not t:
            raise AccountError("Sign in first.")
        code, j = _call(f"{BILLING_URL}/checkout", t, {"plan": plan})
        if code >= 400 or not j.get("url"):
            raise AccountError(j.get("error") or "Couldn't open checkout. Try again later.")
        return {"url": j["url"]}
    return {"url": CHECKOUT_URL + "?" + urllib.parse.urlencode({"plan": plan, "uid": uid, "email": (_load() or {}).get("email") or ""})}


def portal_link():
    """A link to the payment provider's page for changing or cancelling the subscription. Tries the current
    provider first; someone who bought through the other one (before a switch) is sent there instead."""
    t = token()
    if not t:
        raise AccountError("You're not signed in.")
    urls = [BILLING_URL, PADDLE_URL] if provider() == "stripe" else [PADDLE_URL, BILLING_URL]
    for i, url in enumerate(urls):
        code, j = _call(f"{url}/portal", t)
        if code < 400 and j.get("url"):
            return {"url": j["url"]}
        if code != 404 or i == len(urls) - 1:  # 404: no subscription with this provider (or it isn't set up)
            raise AccountError(j.get("error") or "Couldn't open subscription settings. Try again later.")


def delete_account():
    t = token()
    if not t:
        raise AccountError("You're not signed in.")
    # Stop any subscription first, so nobody is charged for an account that no longer exists. Both providers are
    # asked, since someone may have bought before a switch; 404 means that provider isn't set up (nothing to cancel).
    for url in (PADDLE_URL, BILLING_URL):
        try:
            code, j = _call(f"{url}/cancel", t, timeout=30)
        except AccountError:
            raise AccountError("Couldn't reach the account server, so the account wasn't deleted. Check your internet connection.")
        if code >= 400 and code != 404:
            raise AccountError(j.get("error") or "Couldn't cancel your subscription, so the account wasn't deleted. Try again later.")
    from . import cloud
    try:
        if plus_active() or cloud.status()["last"]:
            cloud.delete_all()  # backups next: the server can't remove them once the account is gone
    except Exception as e:
        raise AccountError(f"Couldn't remove your cloud backups, so the account wasn't deleted: {e}")
    t = token()
    try:
        r = httpx.post(f"{SUPABASE_URL}/rest/v1/rpc/delete_my_account", headers=_headers(t), json={}, timeout=20)
    except httpx.HTTPError:
        raise AccountError("Couldn't reach the account server. Your subscription is canceled and your cloud backups are "
                           "deleted; try Delete account again to finish.")
    if r.status_code >= 400:
        raise AccountError(f"Couldn't delete the account: {_msg(r)}")
    with _lock:
        _save(None)
        _status.update(at=0, data=None)
    return status()


# ---------- plan ----------

def _plus_info():
    """The website's plus.json, checked at most every few minutes; the last known answer when offline."""
    if time.time() - _sales["at"] >= STATUS_TTL:
        try:
            info = httpx.get(PLUS_INFO_URL, timeout=8).json()
            _sales["open"] = bool(info.get("sales_open"))
            _sales["provider"] = "stripe" if info.get("provider") == "stripe" else "paddle"
        except Exception:
            pass  # offline or unreachable: keep the last known answer
        _sales["at"] = time.time()
    return _sales


def sales_open():
    """True once Plus is on sale (False when offline and never seen)."""
    return _plus_info()["open"]


def provider():
    """"stripe" when plus.json says so; "paddle" otherwise (also when the file says nothing)."""
    return _plus_info()["provider"]


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
        ok = r.status_code == 200
        data = {**base, **r.json(), "signed_in": True} if ok else None
    except (httpx.HTTPError, ValueError):
        ok, r = False, None
    if not ok:
        # Keep the last known answer (a paying user stays Plus through a hiccup) and try again in a minute.
        cached = _status["data"]
        _status["at"] = time.time() - STATUS_TTL + 60
        if cached:
            _status["data"] = cached
        return {**(cached or base), "offline": r is None, **({"error": _msg(r)} if r is not None else {})}
    _status.update(at=time.time(), data=data)
    return data


def plus_active():
    return bool(status().get("plus"))


def forget_status():
    _status.update(at=0, data=None)
