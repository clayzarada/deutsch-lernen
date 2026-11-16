"""Plus accounts: sign-in with an emailed code, the plan check, and routing AI through the Plus server."""
import os
import time

import httpx
import pytest

from app import account, ai


class FakeResp:
    def __init__(self, status, body):
        self.status_code, self._body, self.text = status, body, str(body)

    def json(self):
        return self._body


@pytest.fixture
def server(monkeypatch):
    """A pretend Supabase: records calls and answers like the real one."""
    calls = []
    state = {"plus": True, "refresh_ok": True}

    def post(url, headers=None, json=None, timeout=None, params=None):
        calls.append(("POST", url, json, params))
        if url.endswith("/auth/v1/otp"):
            return FakeResp(200, {})
        if url.endswith("/auth/v1/verify"):
            if json["token"] != "123456":
                return FakeResp(403, {"msg": "Token has expired or is invalid"})
            return FakeResp(200, {"access_token": "AT1", "refresh_token": "RT1", "expires_in": 3600, "user": {"email": json["email"]}})
        if "grant_type=refresh_token" in url:
            if not state["refresh_ok"]:
                return FakeResp(400, {"msg": "Invalid Refresh Token"})
            return FakeResp(200, {"access_token": "AT2", "refresh_token": "RT2", "expires_in": 3600, "user": {}})
        if url.endswith("/auth/v1/logout") or url.endswith("/rpc/delete_my_account"):
            return FakeResp(204, {})
        if url.endswith("/paddle/portal"):
            return FakeResp(200, {"url": "https://sandbox-customer-portal.paddle.com/x"})
        raise AssertionError(url)

    def get(url, headers=None, timeout=None):
        calls.append(("GET", url, headers.get("authorization")))
        if url.endswith("/auth/v1/user"):
            ok = headers.get("authorization") == "Bearer LINK"
            return FakeResp(200 if ok else 401, {"email": "link@b.de"} if ok else {"msg": "bad jwt"})
        assert url == account.AI_BASE_URL + "/status"
        return FakeResp(200, {"email": "a@b.de", "plan": "plus" if state["plus"] else "free", "plus": state["plus"],
                              "used_usd": 1.0, "cap_usd": 4.0, "used_pct": 25})

    monkeypatch.setattr(httpx, "post", post)
    monkeypatch.setattr(httpx, "get", get)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    account._save(None)
    account.forget_status()
    yield calls, state
    account._save(None)
    account.forget_status()


def test_sign_in_with_code_and_plan(client, server):
    calls, state = server
    assert client.get("/api/account").json() == {"signed_in": False, "plus": False}
    assert client.post("/api/account/code", json={"email": " A@B.de "}).json() == {"sent": True, "email": "a@b.de"}
    bad = client.post("/api/account/verify", json={"email": "a@b.de", "code": "000000"})
    assert bad.status_code == 400 and "didn't work" in bad.json()["detail"]
    a = client.post("/api/account/verify", json={"email": "a@b.de", "code": "123 456"}).json()
    assert a["signed_in"] and a["plus"] and a["used_pct"] == 25
    assert account.SESSION_FILE.exists()
    # Plus counts as "AI is on" for every feature, while the own-key flag stays off
    s = client.get("/api/settings").json()
    assert s["has_key"] is True and s["own_key"] is False
    assert client.post("/api/account/signout").json()["signed_in"] is False
    assert not account.SESSION_FILE.exists()


def test_bad_email_is_rejected(client, server):
    r = client.post("/api/account/code", json={"email": "nope"})
    assert r.status_code == 400


def test_token_refreshes_and_expired_refresh_signs_out(server):
    calls, state = server
    account._save({"access_token": "OLD", "refresh_token": "RT1", "expires_at": int(time.time()) + 10, "email": "a@b.de"})
    assert account.token() == "AT2"
    assert account._load()["email"] == "a@b.de"
    account._save({"access_token": "OLD", "refresh_token": "RT1", "expires_at": int(time.time()) + 10, "email": "a@b.de"})
    state["refresh_ok"] = False
    assert account.token() is None and account._load() is None


def test_ai_uses_plus_server_without_own_key(server):
    calls, state = server
    with pytest.raises(ai.AIError, match="Plus or your own"):
        ai._client("lookup")
    account.verify("a@b.de", "123456")
    c = ai._client("lookup")
    assert str(c.base_url).rstrip("/") == account.AI_BASE_URL
    assert c.default_headers["Authorization"] == "Bearer AT1" and c.default_headers["x-dl-feature"] == "lookup"
    os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test"
    try:
        assert "functions" not in str(ai._client("lookup").base_url)  # own key wins
    finally:
        os.environ.pop("ANTHROPIC_API_KEY")


def test_free_account_gets_no_ai(server):
    calls, state = server
    state["plus"] = False
    account.verify("a@b.de", "123456")
    with pytest.raises(ai.AIError, match="Plus or your own"):
        ai._client("lookup")


def test_delete_account(client, server):
    account.verify("a@b.de", "123456")
    assert client.post("/api/account/delete").json()["signed_in"] is False
    assert not account.SESSION_FILE.exists()


def test_sign_in_by_emailed_link(client, server):
    calls, state = server
    client.post("/api/account/code", json={"email": "link@b.de"})
    otp = [c for c in calls if c[1].endswith("/auth/v1/otp")][-1]
    assert otp[3]["redirect_to"].endswith("/auth/callback")
    page = client.get("/auth/callback")
    assert page.status_code == 200 and "/api/account/session" in page.text
    bad = client.post("/api/account/session", json={"access_token": "NOPE", "refresh_token": "R"})
    assert bad.status_code == 400
    a = client.post("/api/account/session", json={"access_token": "LINK", "refresh_token": "R", "expires_at": "9999999999"}).json()
    assert a["signed_in"] and account._load()["email"] == "link@b.de"


def _jwt(sub):
    import base64, json as _j
    enc = lambda d: base64.urlsafe_b64encode(_j.dumps(d).encode()).decode().rstrip("=")
    return f"{enc({'alg': 'none'})}.{enc({'sub': sub})}.sig"


def test_checkout_link_carries_the_account_and_portal_opens(client, server):
    import urllib.parse
    uid = "0b6c2f4e-1111-4222-8333-944455556666"
    account._save({"access_token": _jwt(uid), "refresh_token": "R", "expires_at": int(time.time()) + 3600, "email": "a@b.de"})
    url = client.post("/api/account/checkout", json={"plan": "monthly"}).json()["url"]
    q = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)
    assert url.startswith(account.CHECKOUT_URL) and q["uid"] == [uid] and q["plan"] == ["monthly"] and q["email"] == ["a@b.de"]
    assert "plan=yearly" in client.post("/api/account/checkout", json={"plan": "weird"}).json()["url"]
    assert client.post("/api/account/portal").json()["url"].startswith("https://sandbox-customer-portal")


def test_checkout_needs_sign_in(client, server):
    assert client.post("/api/account/checkout", json={"plan": "monthly"}).status_code == 400
