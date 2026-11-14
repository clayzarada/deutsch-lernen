"""The built-in beginner course and the welcome flow."""
from app import db, lessons


def test_every_lesson_is_complete_and_its_quiz_is_answerable():
    assert len(lessons.LESSONS) == 12
    for l in lessons.LESSONS:
        c = lessons._content(l)
        assert len(c["words"]) >= 12 and len(c["dialogue"]) >= 5 and len(c["grammar"]["examples"]) >= 3, l["id"]
        for seed in range(3):
            qs = lessons.quiz(l["id"], seed)
            assert 12 <= len(qs) <= 18, l["id"]
            for q in qs:
                assert q["answers"] and q["prompt"], (l["id"], q)
                if q["kind"] == "choice":
                    assert q["answers"][0] in q["choices"] and len(set(q["choices"])) == len(q["choices"]) >= 3, (l["id"], q)
        for r in lessons._rows(l["exercises"]):
            assert len(r) == 4 and r[0].count("___") == 1, (l["id"], r)


def test_nouns_carry_their_article():
    words = {w["de"]: w for w in lessons._words(lessons.BY_ID["cafe"])}
    assert words["der Kaffee"]["article"] == "der" and words["der Kaffee"]["word"] == "Kaffee"
    assert words["trinken"]["article"] == ""
    assert not any(w["article"] for w in lessons._words(lessons.BY_ID["familie"]) if w["de"] == "die Eltern")


def test_lesson_endpoints_and_progress(client):
    o = client.get("/api/lessons").json()
    assert o["next"] == "hallo" and o["done"] == 0 and o["total"] == 12
    l = client.get("/api/lessons/hallo").json()
    n = len(l["quiz"])
    assert l["n"] == 1 and l["next"] == "woher" and l["cards_left"] == len(l["words"])
    # under 70% doesn't finish the lesson
    r = client.post("/api/lessons/hallo/complete", json={"results": [True] * 5 + [False] * (n - 5)}).json()
    assert not r["passed"] and r["overview"]["next"] == "hallo"
    r = client.post("/api/lessons/hallo/complete", json={"results": [True] * n}).json()
    assert r["passed"] and r["overview"]["next"] == "woher" and r["overview"]["done"] == 1
    # a worse try later keeps the lesson done and the best score
    client.post("/api/lessons/hallo/complete", json={"results": [False] * n})
    row = next(x for x in client.get("/api/lessons").json()["lessons"] if x["id"] == "hallo")
    assert row["done"] and row["best"] == n
    assert db.q1("SELECT COUNT(*) AS n FROM answers WHERE source='lesson'")["n"] == 3 * n
    added = client.post("/api/lessons/hallo/cards").json()["added"]
    assert added == len(l["words"]) and client.post("/api/lessons/hallo/cards").json()["added"] == 0
    assert client.get("/api/lessons/nope").status_code == 404
    assert client.post("/api/lessons/hallo/complete", json={"results": []}).status_code == 400


def test_welcome_saves_answers_and_adds_packs(client):
    r = client.post("/api/welcome", json={"level": "A1", "daily_minutes": 20, "use_course": "1", "packs": ["phrases", "nope"]}).json()
    s = r["settings"]
    assert s["onboarded"] == "1" and s["level"] == "A1" and s["daily_minutes"] == "20" and s["use_course"] == "1"
    assert r["added"] > 40
    stats = client.get("/api/stats").json()
    assert stats["course"]["next"]["id"] == "woher"  # lesson 1 was finished in the test above
    plan = client.post("/api/plan/quick", json={"minutes": 30}).json()
    assert plan["blocks"][0]["kind"] == "course" and plan["blocks"][0]["lesson_id"] == "woher"
    client.put("/api/settings", json={"use_course": "0"})
    assert client.get("/api/stats").json()["course"] is None
    assert all(b["kind"] != "course" for b in client.post("/api/plan/quick", json={"minutes": 30}).json()["blocks"])
