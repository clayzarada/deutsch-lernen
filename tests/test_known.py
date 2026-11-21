"""Known words: statuses from flashcards, lessons and reading, and the learner's own choice winning."""
from app import db, known


def _reset():
    db.init()
    known._init()
    db.ex("DELETE FROM known_words")
    db.ex("DELETE FROM cards")


def test_tokenize_round_trips_and_finds_lemmas():
    text = "Die Männer gehen nach Hause, 2 Kinder spielen."
    toks = known.tokenize(text)
    assert "".join(p["t"] for p in toks) == text
    lem = {p["t"]: p["lemma"] for p in toks if p.get("lemma")}
    assert lem["Männer"] == "Mann"
    assert lem["Kinder"] == "Kind"


def test_cards_decide_learning_and_known():
    _reset()
    db.ex("INSERT INTO cards(type, front, back, interval, reps, due) VALUES('vocab','der Hund','dog',30,5,'2030-01-01')")
    db.ex("INSERT INTO cards(type, front, back, interval, reps, due) VALUES('vocab','die Katze','cat',1,1,'2030-01-01')")
    db.ex("INSERT INTO cards(type, front, back) VALUES('vocab','das Pferd','horse')")
    db.ex("INSERT INTO cards(type, front, back) VALUES('vocab','helfen + ?','+ Dativ')")
    s = known.statuses()
    assert s["Hund"] == known.KNOWN and s["Katze"] == known.LEARNING and s["Pferd"] == known.SEEN
    assert "helfen" not in s  # pattern cards teach grammar, not the word
    c = known.counts()
    assert c["known"] == 1 and c["learning"] == 1 and c["seen"] == 1


def test_lessons_and_reading_only_raise_but_user_can_lower():
    _reset()
    known.mark(["Haus"], known.LEARNING, "lesson")
    known.saw(["Haus", "Baum"])
    s = known.statuses(["Haus", "Baum"])
    assert s == {"Haus": known.LEARNING, "Baum": known.SEEN}
    known.mark(["Haus"], known.SEEN, "lesson")
    assert known.statuses(["Haus"])["Haus"] == known.LEARNING
    known.mark(["Haus"], known.SEEN)  # the learner's choice
    assert known.statuses(["Haus"])["Haus"] == known.SEEN
    known.mark(["Haus"], known.KNOWN, "lesson")  # a later lesson doesn't override the learner
    assert known.statuses(["Haus"])["Haus"] == known.SEEN


def test_coverage():
    _reset()
    known.mark(["der", "Mann", "gehen", "nach", "Haus"], known.KNOWN)
    cov = known.coverage("Der Mann geht nach Hause. Der Mann schläft.")
    assert cov["words"] == 8 and cov["unknown"] == ["schlafen"]
    assert cov["known_pct"] == round(100 * 7 / 8)


def test_api(client):
    _reset()
    r = client.post("/api/known/text", json={"text": "Der Hund bellt.", "saw": True}).json()
    words = [p for p in r["tokens"] if p.get("lemma")]
    assert [p["s"] for p in words] == [known.SEEN] * 3
    r = client.post("/api/known/mark", json={"lemmas": ["Hund"], "status": 3}).json()
    assert r["statuses"] == {"Hund": 3}
    summary = client.get("/api/known").json()
    assert summary["known"] == 1 and summary["seen"] == 2 and summary["history"][-1]["known"] == 1
    assert client.post("/api/known/mark", json={"lemmas": ["x"], "status": 7}).status_code == 400
