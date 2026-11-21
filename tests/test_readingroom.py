"""Reading room: the built-in library is sound, coverage matches known.coverage, own texts and the finished log work."""
from collections import Counter

from app import db, known, readingroom
from app.readers_data import BY_ID, GENRES, LEVELS, TEXTS, TOPICS

# Rough length bands per level (running words): A1 starts around 120, B1 goes up to about 450.
LENGTH = {"A1": (110, 200), "A2": (190, 320), "B1": (260, 470)}


def _reset():
    db.init()
    readingroom._init()
    known._init()
    for t in ("reading_texts", "reading_finished", "known_words", "cards"):
        db.ex(f"DELETE FROM {t}")


def test_library_is_sound():
    assert len(TEXTS) == 30 and len(BY_ID) == 30
    assert Counter(t["level"] for t in TEXTS) == {"A1": 10, "A2": 10, "B1": 10}
    for t in TEXTS:
        assert t["level"] in LEVELS and t["genre"] in GENRES and t["topic"] in TOPICS, t["id"]
        assert t["title"] and t["summary_en"] and t["summary_tr"] and t["paragraphs"], t["id"]
        text = "\n\n".join(t["paragraphs"])
        toks = known.tokenize(text)
        assert "".join(p["t"] for p in toks) == text, t["id"]
        n = len([p for p in toks if p.get("lemma")])
        lo, hi = LENGTH[t["level"]]
        assert lo <= n <= hi, (t["id"], n)
    assert len({t["title"] for t in TEXTS}) == 30


def test_library_genres_vary():
    genres = Counter(t["genre"] for t in TEXTS)
    assert len(genres) >= 7 and genres["Mystery"] == 3 and genres["Recipe"] >= 1


def test_batch_coverage_matches_known_coverage():
    _reset()
    known.mark(["ich", "heißen", "sein", "und", "wohnen", "in"], known.KNOWN)
    known.mark(["Leipzig"], known.IGNORED)
    known.mark(["alt"], known.LEARNING)
    text = "\n\n".join(BY_ID["a1-mein-tag"]["paragraphs"])
    mine = readingroom.coverages({"x": text})["x"]
    ref = known.coverage(text)
    assert mine["known_pct"] == ref["known_pct"] and mine["words"] == ref["words"]
    assert mine["new"] == len(ref["unknown"])


def test_library_api_lists_texts_with_coverage(client):
    _reset()
    r = client.get("/api/readingroom").json()
    assert len(r["texts"]) == 30 and r["finished_total"] == 0
    t = next(x for x in r["texts"] if x["key"] == "a1-im-cafe")
    assert t["words"] > 100 and 0 <= t["known_pct"] <= 100 and t["finished"] == 0 and t["minutes"] >= 1
    full = client.get("/api/readingroom/texts/a1-im-cafe").json()
    assert full["text"].startswith("Kellnerin: Guten Tag!")
    assert client.get("/api/readingroom/texts/nope").status_code == 404


def test_own_texts(client):
    _reset()
    r = client.post("/api/readingroom/texts", json={"title": "", "text": "Der Hund bellt.\r\n\r\n\r\nDie Katze schläft."})
    t = r.json()
    assert r.status_code == 200 and t["key"].startswith("u") and t["source"] == "user"
    assert t["title"] == "Der Hund bellt."  # first line when no title is given
    full = client.get("/api/readingroom/texts/" + t["key"]).json()
    assert full["text"] == "Der Hund bellt.\n\nDie Katze schläft."
    mine = [x for x in client.get("/api/readingroom").json()["texts"] if x["key"] == t["key"]][0]
    assert mine["words"] == 6 and mine["known_pct"] == 0
    r = client.put("/api/readingroom/texts/" + t["key"], json={"title": "Tiere", "level": "A1"}).json()
    assert r["title"] == "Tiere" and r["level"] == "A1"
    assert client.put("/api/readingroom/texts/" + t["key"], json={"title": "  "}).status_code == 400
    assert client.put("/api/readingroom/texts/a1-im-cafe", json={"title": "x"}).status_code == 400
    assert client.delete("/api/readingroom/texts/a1-im-cafe").status_code == 400
    assert client.delete("/api/readingroom/texts/" + t["key"]).json()["ok"]
    assert client.get("/api/readingroom/texts/" + t["key"]).status_code == 404


def test_own_text_limits(client):
    _reset()
    assert client.post("/api/readingroom/texts", json={"text": "   "}).status_code == 400
    assert client.post("/api/readingroom/texts", json={"text": "123 456 !!!"}).status_code == 400
    big = "Das ist ein Satz. " * 2000
    assert client.post("/api/readingroom/texts", json={"text": big}).status_code == 400
    long_title = client.post("/api/readingroom/texts", json={"title": "T" * 500, "text": "Hallo Welt"}).json()
    assert len(long_title["title"]) == readingroom.MAX_TITLE


def test_finished_log(client):
    _reset()
    r = client.post("/api/readingroom/finished", json={"key": "a1-minka", "seconds": 240}).json()
    assert r["finished"] == 1
    client.post("/api/readingroom/finished", json={"key": "a1-minka", "seconds": 10 ** 9})
    assert client.post("/api/readingroom/finished", json={"key": "u999"}).status_code == 404
    lib = client.get("/api/readingroom").json()
    assert lib["finished_total"] == 2 and lib["recent"][0]["title"] == "Wo ist Minka?"
    assert next(x for x in lib["texts"] if x["key"] == "a1-minka")["finished"] == 2
    rows = db.q("SELECT seconds FROM reading_finished ORDER BY id")
    assert rows[0]["seconds"] == 240 and rows[1]["seconds"] == 4 * 3600  # capped
    assert readingroom.coach_summary()[0]["title"] == "Wo ist Minka?"
    lv = readingroom.finished_for_levels()
    assert len(lv) == 2 and lv[0]["level"] == "A1" and 0 <= lv[0]["known_pct"] <= 100
    own = client.post("/api/readingroom/texts", json={"text": "Hallo Welt"}).json()  # no level: not counted
    client.post("/api/readingroom/finished", json={"key": own["key"]})
    assert len(readingroom.finished_for_levels()) == 2


def test_reading_time_counts_as_reading(client):
    _reset()
    from app import planner
    before = planner.day_stats(db.today())["reading_minutes"]
    for _ in range(8):
        client.post("/api/activity", json={"kind": "reading", "seconds": 15})
    assert planner.day_stats(db.today())["reading_minutes"] == before + 2


def test_story_needs_ai(client):
    _reset()
    r = client.post("/api/readingroom/story", json={"topic": "Urlaub", "level": "A2"})
    assert r.status_code >= 400  # no key and no Plus in tests


def test_story_is_saved_as_ai_text(monkeypatch):
    _reset()
    known.mark(["Hund", "Park", "gehen"], known.KNOWN)
    seen = {}

    def fake_call(system, task, schema=None, **kw):
        seen.update(task=task, feature=kw.get("feature"))
        return {"title": "Im Park", "paragraphs": ["Der Hund geht in den Park.", "Er spielt."]}

    monkeypatch.setattr(readingroom.ai, "call", fake_call)
    t = readingroom.write_story("A1", "Hunde")
    assert t["source"] == "ai" and t["level"] == "A1" and t["title"] == "Im Park" and t["topic"] == "Hunde"
    assert seen["feature"] == "reading_story" and "Hund" in seen["task"] and "A1" in seen["task"]
    assert readingroom._get(t["key"])[1] == "Der Hund geht in den Park.\n\nEr spielt."
