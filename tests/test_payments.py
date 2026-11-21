"""Plus payments: plus.json picks Stripe or Paddle; with Stripe, checkout, portal and cancel go through our billing
function. The server side of Stripe (webhook, signature check) is tested with Deno in supabase/functions/_shared."""
import time

import httpx
import pytest

from app import account
from test_account import FakeResp, _jwt, server  # noqa: F401 (server is a fixture)

UID = "0b6c2f4e-1111-4222-8333-944455556666"


def _sign_in():
    account._save({"access_token": _jwt(UID), "refresh_token": "R", "expires_at": int(time.time()) + 3600, "email": "a@b.de"})


@pytest.fixture
def stripe(server):
    """The pretend server with plus.json saying "provider": "stripe" and a working billing function."""
    calls, state = server
    state["stripe_customer"] = True
    state["billing_calls"] = []

    def billing(url, body):
        state["billing_calls"].append((url.rsplit("/", 1)[1], body))
        if url.endswith("/billing/checkout"):
            if state.get("already_plus"):
                return FakeResp(409, {"error": "You already have Plus. Use Manage subscription to change or cancel it."})
            return FakeResp(200, {"url": f"https://checkout.stripe.com/c/pay/cs_test_{body['plan']}"})
        if url.endswith("/billing/portal"):
            if not state["stripe_customer"]:
                return FakeResp(404, {"error": "There's no subscription on this account yet."})
            return FakeResp(200, {"url": "https://billing.stripe.com/p/session/test_x"})
        if url.endswith("/billing/cancel"):
            return FakeResp(200, {"canceled": True})
        raise AssertionError(url)

    state["billing"] = billing
    account._sales.update(at=time.time(), open=True, provider="stripe")
    _sign_in()
    return calls, state


def test_plus_json_picks_the_provider(monkeypatch):
    answers = iter([{"sales_open": True, "provider": "stripe"}, {"sales_open": True, "provider": "something else"}])

    class J:
        def json(self):
            return next(answers)

    monkeypatch.setattr(httpx, "get", lambda url, timeout=None: J())
    account._sales.update(at=0)
    assert account.provider() == "stripe" and account.sales_open() is True
    account._sales.update(at=0)
    assert account.provider() == "paddle"  # anything unknown keeps the Paddle path
    account._sales.update(at=0, open=False, provider="paddle")


def test_stripe_checkout_opens_stripe_directly(client, stripe):
    calls, state = stripe
    url = client.post("/api/account/checkout", json={"plan": "monthly"}).json()["url"]
    assert url == "https://checkout.stripe.com/c/pay/cs_test_monthly"
    assert client.post("/api/account/checkout", json={"plan": "weird"}).json()["url"].endswith("cs_test_yearly")
    assert [c[0] for c in state["billing_calls"]] == ["checkout", "checkout"]
    # The request carries the sign-in token, so the server knows the account (no ids in the URL).
    assert not any("/checkout/" in c[1] and "uid=" in c[1] for c in calls)


def test_stripe_checkout_error_is_shown(client, stripe):
    calls, state = stripe
    state["already_plus"] = True
    r = client.post("/api/account/checkout", json={"plan": "yearly"})
    assert r.status_code == 400 and "already have Plus" in r.json()["detail"]


def test_stripe_checkout_needs_sign_in(client, stripe):
    account._save(None)
    assert client.post("/api/account/checkout", json={"plan": "monthly"}).status_code == 400


def test_stripe_portal_and_fallback_to_paddle(client, stripe):
    calls, state = stripe
    assert client.post("/api/account/portal").json()["url"].startswith("https://billing.stripe.com/")
    # Bought with Paddle before the switch: no Stripe customer, so Paddle's page opens.
    state["stripe_customer"] = False
    assert client.post("/api/account/portal").json()["url"].startswith("https://sandbox-customer-portal")
    # Neither has a subscription: the server's message is shown.
    state["paddle_customer"] = False
    r = client.post("/api/account/portal")
    assert r.status_code == 400 and "no subscription" in r.json()["detail"]


def test_paddle_portal_falls_back_to_stripe(client, stripe):
    calls, state = stripe
    account._sales.update(provider="paddle")
    state["paddle_customer"] = False
    assert client.post("/api/account/portal").json()["url"].startswith("https://billing.stripe.com/")


def test_delete_account_cancels_with_both_providers(client, stripe, monkeypatch):
    from app import cloud
    calls, state = stripe
    monkeypatch.setattr(cloud, "delete_all", lambda: 0)  # cloud backups have their own tests
    assert client.post("/api/account/delete").json()["signed_in"] is False
    assert state["cancels"] == 1 and ("cancel", {}) in state["billing_calls"]


def test_delete_account_stops_when_stripe_cancel_fails(client, stripe):
    calls, state = stripe
    state["billing"] = lambda url, body: FakeResp(502, {"error": "Couldn't cancel the subscription. Try again, or cancel it from Manage subscription."})
    r = client.post("/api/account/delete")
    assert r.status_code == 400 and "Couldn't cancel the subscription" in r.json()["detail"]
    assert account.SESSION_FILE.exists()  # still signed in; nothing was deleted
    assert not any(c[1].endswith("/rpc/delete_my_account") for c in calls)


def test_paddle_checkout_still_uses_the_website(client, stripe):
    account._sales.update(provider="paddle")
    url = client.post("/api/account/checkout", json={"plan": "monthly"}).json()["url"]
    assert url.startswith(account.CHECKOUT_URL) and f"uid={UID}" in url
