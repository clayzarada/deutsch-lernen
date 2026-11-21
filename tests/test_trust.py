"""FSRS flashcard scheduling, "Export all my data" and the AI-written card tag."""
import csv
import datetime as dt
import io
import json
import zipfile

import pytest

from app import db, srs

NOW = dt.datetime(2026, 3, 2, 9, 0, 0)


def new_card(**kw):
    return {"due": None, "interval": 0, "ease": 2.5, "reps": 0, "lapses": 0, "stability": None, "difficulty": None, **kw}


def grade(card, g, at, r=0.9):
    """Grade a card at a given time and return the updated card."""
    return {**card, **srs.schedule(card, g, r, at)}


def at_due(card):
    return dt.datetime.fromisoformat(card["due"])


# ---------- the scheduler ----------

def test_new_card_learning_steps_then_days():
    c = new_card()
    p = srs.preview(c, 0.9, NOW)
    assert p[1] == "10m" and p[2] == "6h"
    assert p[3].endswith("d") and p[4].endswith("d")
    again = grade(c, 1, NOW)
    assert again["interval"] == pytest.approx(10 / 1440, abs=1e-4)
    assert again["reps"] == 0 and again["lapses"] == 1
    assert again["stability"] == pytest.approx(srs.W[0], abs=1e-3)
    hard = grade(again, 2, at_due(again))  # still learning: back in 6 hours
    assert hard["interval"] == 0.25 and hard["reps"] == 0
    good = grade(hard, 3, at_due(hard))  # graduates to days
    assert good["interval"] == 1 and good["reps"] == 1
    first_good = grade(c, 3, NOW)
    first_easy = grade(c, 4, NOW)
    assert 1 <= first_good["interval"] < first_easy["interval"] <= 10
    assert first_good["stability"] == pytest.approx(srs.W[2], abs=1e-3)


def test_intervals_grow_with_good_answers():
    c = grade(new_card(), 3, NOW)
    t, intervals = NOW, [c["interval"]]
    for _ in range(6):
        t = at_due(c)
        c = grade(c, 3, t)
        intervals.append(c["interval"])
    assert all(b > a for a, b in zip(intervals, intervals[1:])), intervals
    assert intervals[-1] > 60  # after seven good reviews the card is months away
    assert intervals[2] / intervals[1] < 5  # but it grows step by step, not in wild jumps


def test_buttons_stay_in_order_and_due_matches_interval():
    c = grade(grade(grade(new_card(), 3, NOW), 3, NOW + dt.timedelta(days=2)), 3, NOW + dt.timedelta(days=8))
    t = at_due(c)
    res = {g: srs.schedule(c, g, 0.9, t)["interval"] for g in (1, 2, 3, 4)}
    assert res[1] < 1 <= res[2] <= res[3] < res[4]
    out = srs.schedule(c, 3, 0.9, t)
    assert dt.datetime.fromisoformat(out["due"]) == t + dt.timedelta(days=out["interval"])


def test_lapse_resets_and_relearns():
    c = grade(new_card(), 3, NOW)
    for _ in range(4):
        c = grade(c, 3, at_due(c))
    before = c
    missed = grade(c, 1, at_due(c))
    assert missed["reps"] == 0 and missed["lapses"] == before["lapses"] + 1
    assert missed["interval"] < 1  # 10 minutes
    assert missed["stability"] < before["stability"]
    assert missed["difficulty"] > before["difficulty"]
    back = grade(missed, 3, at_due(missed))
    assert 1 <= back["interval"] < before["interval"]  # days again, but shorter than before the miss
    assert back["reps"] == 1


def test_retention_changes_the_interval():
    c = grade(grade(new_card(), 3, NOW), 3, NOW + dt.timedelta(days=2))
    t = at_due(c)
    low, mid, high = (srs.schedule(c, 3, r, t)["interval"] for r in (0.8, 0.9, 0.95))
    assert low > mid > high


def test_retention_setting_is_clamped(client):
    db.set_setting("desired_retention", "0.5")
    assert srs.retention() == 0.8
    db.set_setting("desired_retention", "0.99")
    assert srs.retention() == 0.95
    db.set_setting("desired_retention", "nonsense")
    assert srs.retention() == 0.9
    db.set_setting("desired_retention", "0.9")


def test_overdue_card_gets_more_credit_than_one_reviewed_on_time():
    c = grade(grade(new_card(), 3, NOW), 3, NOW + dt.timedelta(days=2))
    on_time = srs.schedule(c, 3, 0.9, at_due(c))
    late = srs.schedule(c, 3, 0.9, at_due(c) + dt.timedelta(days=10))
    assert late["stability"] > on_time["stability"]


# ---------- cards from before FSRS ----------

def test_legacy_card_keeps_its_schedule():
    old = {"due": "2026-03-12T09:00:00", "interval": 10, "ease": 2.5, "reps": 3, "lapses": 0}
    s, d = srs.from_legacy(old)
    assert s == 10 and 4 <= d <= 6
    # On its due day, FSRS expects 90% recall, exactly what the old interval promised.
    assert srs.recall(10, s) == pytest.approx(0.9, abs=1e-6)
    good = srs.schedule(old, 3, 0.9, dt.datetime(2026, 3, 12, 9))
    assert 20 <= good["interval"] <= 45  # SM-2 would have said 25 days; nothing jumps
    hard_ease = srs.from_legacy({**old, "ease": 1.3})[1]
    easy_ease = srs.from_legacy({**old, "ease": 3.2})[1]
    assert hard_ease > d > easy_ease
    assert srs.from_legacy({**old, "reps": 0, "interval": 10 / 1440})[0] == srs.W[0]  # still in learning


def test_migration_fills_stability_and_difficulty(client):
    due = (dt.datetime.now() + dt.timedelta(days=5)).isoformat(timespec="seconds")
    old = db.ex("INSERT INTO cards(type, front, back, due, interval, ease, reps, lapses) "
                "VALUES('vocab','das Fenster','window',?,12,2.3,4,1)", (due,))
    new = db.ex("INSERT INTO cards(type, front, back) VALUES('vocab','die Tür','door')")
    db.init()
    o = db.q1("SELECT * FROM cards WHERE id=?", (old,))
    assert o["stability"] == 12 and 5 < o["difficulty"] < 6
    assert o["due"] == due and o["interval"] == 12  # untouched
    n = db.q1("SELECT * FROM cards WHERE id=?", (new,))
    assert n["stability"] is None and n["difficulty"] is None
    db.ex("DELETE FROM cards WHERE id IN (?,?)", (old, new))


# ---------- the review API and undo ----------

def test_review_and_undo_restore_everything(client):
    cid = client.post("/api/cards", json={"front": "der Baum", "back": "tree"}).json()["id"]
    first = client.post(f"/api/review/{cid}", json={"grade": 3}).json()
    c1 = first["card"]
    assert c1["stability"] and c1["difficulty"] and c1["interval"] >= 1 and c1["reps"] == 1
    assert set(c1["previews"]) == {"1", "2", "3", "4"}
    second = client.post(f"/api/review/{cid}", json={"grade": 1}).json()
    assert second["card"]["lapses"] == 1 and second["card"]["reps"] == 0
    undone = client.post("/api/review-undo", json=second["undo"]).json()["card"]
    for k in ("ease", "interval", "reps", "lapses", "due", "stability", "difficulty"):
        assert undone[k] == c1[k], k
    assert not db.q1("SELECT id FROM reviews WHERE id=?", (second["undo"]["review_id"],))
    # An undo from an older page (no FSRS columns) still works; the card falls back to its old schedule.
    third = client.post(f"/api/review/{cid}", json={"grade": 3}).json()
    prev = {k: v for k, v in third["undo"]["prev"].items() if k not in ("stability", "difficulty")}
    r = client.post("/api/review-undo", json={**third["undo"], "prev": prev})
    assert r.status_code == 200 and r.json()["card"]["previews"]
    client.delete(f"/api/cards/{cid}")


def test_review_queue_previews(client):
    cid = client.post("/api/cards", json={"front": "der Fluss", "back": "river"}).json()["id"]
    q = client.get("/api/review/queue").json()
    card = next(c for c in q["cards"] if c["id"] == cid)
    assert card["previews"]["1"] == "10m" and card["previews"]["2"] == "6h"
    client.delete(f"/api/cards/{cid}")


def test_retention_is_a_setting(client):
    s = client.put("/api/settings", json={"desired_retention": "0.85"}).json()
    assert s["desired_retention"] == "0.85" and srs.retention() == 0.85
    client.put("/api/settings", json={"desired_retention": "0.9"})


# ---------- export all my data ----------

def test_export_all_my_data(client):
    (db.BOOKS / "lehrbuch.pdf").write_bytes(b"%PDF-1.4 fake book " * 1000)
    (db.MEDIA / "episode.mp3").write_bytes(b"ID3 fake audio")
    env = db.DATA / ".env"
    env.write_text("ANTHROPIC_API_KEY=sk-ant-very-secret\n")
    db.set_setting("some_api_key", "sk-should-not-leak")
    cid = client.post("/api/cards", json={"front": "der Löffel", "back": "spoon"}).json()["id"]
    client.post(f"/api/review/{cid}", json={"grade": 3})
    db.ex("INSERT INTO writings(created_at, date, title, text, words, score) VALUES(?,?,?,?,?,?)",
          (db.now(), db.today(), "Mein Tag", "Heute bin ich früh aufgestanden.", 5, 70))
    db.add_mistakes("practice", [{"topic": "Dativ", "wrong": "mit der Mann", "correct": "mit dem Mann"}])
    r = client.get("/api/export/all")
    assert r.status_code == 200 and r.headers["content-type"] == "application/zip"
    assert "my-data" in r.headers["content-disposition"]
    z = zipfile.ZipFile(io.BytesIO(r.content))
    names = set(z.namelist())
    assert {"README.txt", "study.db", "csv/flashcards.csv", "csv/known_words.csv", "csv/writings.csv",
            "csv/mistakes.csv", "csv/reading_history.csv", "csv/activity.csv", "csv/flashcard_reviews.csv",
            "books/lehrbuch.pdf", "media/episode.mp3"} <= names
    assert not any(n.endswith(".env") or "account" in n for n in names)
    for n in names:
        data = z.read(n)
        assert b"sk-ant-very-secret" not in data and b"sk-should-not-leak" not in data, n
    cards = list(csv.DictReader(io.StringIO(z.read("csv/flashcards.csv").decode("utf-8-sig"))))
    row = next(c for c in cards if c["front"] == "der Löffel")
    assert row["back"] == "spoon" and float(row["stability"]) > 0 and row["due"]
    assert "Mein Tag" in z.read("csv/writings.csv").decode("utf-8-sig")
    assert "mit dem Mann" in z.read("csv/mistakes.csv").decode("utf-8-sig")
    assert b"API keys" in z.read("README.txt")
    assert z.read("books/lehrbuch.pdf") == (db.BOOKS / "lehrbuch.pdf").read_bytes()
    db.ex("DELETE FROM settings WHERE key='some_api_key'")
    env.unlink()
    client.delete(f"/api/cards/{cid}")


# ---------- AI-written cards ----------

def test_old_ai_cards_get_the_ai_tag(client):

    conn = db.connect()
    try:
        with conn:
            ids = {}
            for name, chapter, tags in (
                    ("ai", 1, ["Dativ", "food"]),               # Claude's topic tags, from a chapter
                    ("hand", 1, []),                            # written by hand
                    ("dict", 1, ["dictionary", "noun"]),        # offline dictionary
                    ("pack", None, ["pack", "verbs"]),          # built-in pack
                    ("course", None, ["course", "lesson:a1"]),  # built-in course
                    ("table", 1, ["gemini-notebook"]),          # plain table import
                    ("tidied", 1, ["Perfekt", "gemini-notebook"])):  # tidied by Claude
                ids[name] = conn.execute("INSERT INTO cards(chapter_id, type, front, back, tags) VALUES(?,?,?,?,?)",
                                         (chapter, "vocab", name, name, json.dumps(tags))).lastrowid
            db._tag_ai_cards(conn)
    finally:
        conn.close()
    tagged = {n for n, i in ids.items() if "ai" in json.loads(db.q1("SELECT tags FROM cards WHERE id=?", (i,))["tags"])}
    assert tagged == {"ai", "tidied"}
    db.ex(f"DELETE FROM cards WHERE id IN ({','.join(str(i) for i in ids.values())})")
