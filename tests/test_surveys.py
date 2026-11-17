"""In-app questions and the weekly usage summary."""
import json

import httpx
import pytest

from app import account, db, surveys

Q = {"id": "nav-test", "title": "Quick question", "question": "Which?", "kind": "choice", "allow_comment": True,
     "options": [{"id": "side", "label": "Side", "try": "nav:side"}, {"id": "top", "label": "Top", "try": "nav:top"}]}


class R:
    def __init__(self, status, body=None):
        self.status_code, self._b = status, body

    def json(self):
        return self._b


@pytest.fixture
def server(monkeypatch):
    sent = {"answers": [], "usage": []}

    def get(url, headers=None, timeout=None, params=None):
        assert url.endswith("/rest/v1/surveys")
        return R(200, [Q])

    def post(url, json=None, timeout=None, headers=None):
        sent["answers" if url.endswith("/survey_answers") else "usage"].append(json)
        return R(201)

    monkeypatch.setattr(httpx, "get", get)
    monkeypatch.setattr(httpx, "post", post)
    account._save(None)
    for k in ("surveys_done", "usage_sent_week", "share_usage"):
        db.set_setting(k, "")
    surveys._cache.update(at=0, list=[])
    yield sent
    surveys._cache.update(at=0, list=[])
    for k in ("surveys_done", "usage_sent_week", "share_usage"):
        db.set_setting(k, "")


def test_question_answer_and_never_again(client, server):
    assert [s["id"] for s in client.get("/api/surveys").json()] == ["nav-test"]
    bad = client.post("/api/surveys/nav-test", json={"answer": "middle"})
    assert bad.status_code == 400
    r = client.post("/api/surveys/nav-test", json={"answer": "top", "comment": " nice "}).json()
    assert r["pending"] == []
    row = server["answers"][-1]
    assert row["answer"] == "top" and row["comment"] == "nice" and row["user_id"] is None and len(row["install_id"]) == 32
    assert client.get("/api/surveys").json() == []  # answered: gone for good on this computer


def test_skip_sends_a_skip(client, server):
    client.get("/api/surveys")
    client.post("/api/surveys/nav-test", json={"skipped": True})
    assert server["answers"][-1]["skipped"] is True and server["answers"][-1]["answer"] is None


def test_weekly_summary_once_and_can_be_turned_off(server):
    db.set_setting("share_usage", "1")
    assert surveys.send_weekly() is True
    row = server["usage"][-1]
    assert {"days_active", "minutes", "cards_reviewed", "answers", "lessons_done", "install_id", "week"} <= row.keys()
    assert "front" not in json.dumps(row)  # numbers only, never card text
    assert surveys.send_weekly() is False  # already sent this week
    db.set_setting("usage_sent_week", "")
    db.set_setting("share_usage", "0")
    assert surveys.send_weekly() is False


def test_offline_is_harmless(client, monkeypatch):
    def boom(*a, **k):
        raise httpx.ConnectError("offline")
    monkeypatch.setattr(httpx, "get", boom)
    surveys._cache.update(at=0, list=[])
    assert client.get("/api/surveys").json() == []
