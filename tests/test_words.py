"""The offline dictionary and the free practice built on it: look-ups, gap-fills, chapter words, noun and number drills."""
import pymupdf
import pytest

from app import dictionary, textwork, wordtrain


# ---------- dictionary ----------
@pytest.mark.parametrize("form, word, article", [
    ("Männer", "Mann", "der"), ("Häusern", "Haus", "das"), ("Teilnehmern", "Teilnehmer", "der"),
    ("Zeitung", "Zeitung", "die"), ("Lehrerin", "Lehrerin", "die"),
])
def test_nouns_and_their_forms(form, word, article):
    e = dictionary.lookup(form)[0]
    assert (e["word"], e["article"]) == (word, article)


@pytest.mark.parametrize("form, word, pos", [("ging", "gehen", "verb"), ("gekauft", "kaufen", "verb"),
                                             ("schönen", "schön", "adj"), ("besser", "gut", "adj")])
def test_verbs_and_adjectives(form, word, pos):
    e = dictionary.lookup(form)[0]
    assert (e["word"], e["pos"]) == (word, pos)


def test_verb_forms_text():
    assert dictionary.lookup("gehen")[0]["forms_text"] == "er geht, ging, ist gegangen"


def test_unknown_compounds_take_the_last_part():
    e = dictionary.lookup("Sommerferienjacke")[0]
    assert e["article"] == "die" and e["compound"][1] == "Jacke"


def test_grammar_words_are_explained_by_case():
    e = dictionary.explain("ihm")[0]
    assert e["grammar"] and "dative" in e["meanings"][0]


def test_short_meanings_drop_long_brackets():
    assert dictionary.short(["computer (programmable electronic device that performs calculations)"]) == "computer"


# ---------- text from a chapter ----------
TEXT = """Exercise 4.2
Fill in the correct endings of the articles below, using the examples.
Der Schüler kauft einen neuen Computer. Die Lehrerin lobt den fleißigen Schüler.
Ich helfe meiner Mutter. Wir fahren mit dem Bus nach Hause.
This sentence is English and must not be used.
Er hat seinem Bruder ein altes Fahrrad geschenkt.
"""


def test_sentences_keep_german_and_drop_english():
    s = textwork.sentences(TEXT)
    assert "Der Schüler kauft einen neuen Computer." in s
    assert not any("English" in x or "Fill in" in x for x in s)


def test_gapfills_blank_one_word_with_its_answer():
    r = textwork.gapfills(TEXT, "mixed", 20, seed=1)
    assert r["items"] and all(r["available"].values())
    for it in r["items"]:
        assert it["before"] + it["solution"] + it["after"] == it["sentence"]
        assert it["solution"] in it["answers"] or it["gap"].replace("___", "") + it["answers"][0] == it["solution"].lower() \
            or it["gap"].replace("___", "") + it["answers"][0] == it["solution"]


def test_chapter_words_with_gender_and_examples():
    w = {x["word"]: x for x in textwork.words(TEXT)}
    assert w["Schüler"]["article"] == "der" and "Schüler" in w["Schüler"]["example"]
    assert "Exercise" not in w and "English" not in w
    card = textwork.card_for(w["Fahrrad"])
    assert card["front"] == "das Fahrrad" and "Plural: die Fahrräder" in card["extra"]


# ---------- number words ----------
@pytest.mark.parametrize("n, w", [(16, "sechzehn"), (17, "siebzehn"), (21, "einundzwanzig"), (101, "einhunderteins"),
                                  (1999, "eintausendneunhundertneunundneunzig"), (30, "dreißig")])
def test_number_words(n, w):
    assert wordtrain.words(n) == w


def test_years_times_dates_prices():
    assert wordtrain.year_words(1999) == "neunzehnhundertneunundneunzig"
    assert wordtrain.year_words(2024) == "zweitausendvierundzwanzig"
    assert wordtrain.clock(3, 30) == ["halb vier"]
    assert wordtrain.clock(12, 45)[0] == "Viertel vor eins"
    assert [wordtrain.ordinal(n) for n in (1, 3, 7, 19, 20)] == ["erst", "dritt", "siebt", "neunzehnt", "zwanzigst"]
    assert wordtrain.price_words(350)[0] == "drei Euro fünfzig"


def test_every_number_question_accepts_its_answer(client):
    for _ in range(80):
        q = wordtrain.number_question()
        assert wordtrain.grade(q, q["answers"][0])["correct"], q


def test_noun_drill(client):
    q = wordtrain.noun_question("200", "gender")
    assert q["kind"] == "choice" and q["answers"][0] in ("der", "die", "das")
    assert wordtrain.grade(q, q["answers"][0])["correct"]
    q = wordtrain.noun_question("200", "plural")
    assert wordtrain.grade(q, "die " + q["display"])["correct"] and not wordtrain.grade(q, "xyz")["correct"]


# ---------- the endpoints ----------
def test_endpoints(client, tmp_path):
    from app import db
    assert client.get("/api/dict", params={"word": "Männer"}).json()["entries"][0]["word"] == "Mann"
    for kind in ("nouns", "numbers"):
        q = client.post(f"/api/{kind}/next", json={}).json()
        r = client.post(f"/api/{kind}/answer", json={"question": q, "answer": q["answers"][0], "ms": 1000}).json()
        assert r["correct"] and r["next"]["prompt"]
    assert client.get("/api/nouns/state").json()["progress"]["ng"]["total"] > 100

    doc = pymupdf.open()
    page = doc.new_page()
    for n, line in enumerate(TEXT.splitlines()):
        page.insert_text((40, 60 + n * 18), line, fontsize=10)
    db.BOOKS.mkdir(parents=True, exist_ok=True)
    doc.save(db.BOOKS / "words.pdf")
    bid = db.ex("INSERT INTO books(title, filename, page_count, created_at) VALUES('W','words.pdf',1,?)", (db.now(),))
    cid = db.ex("INSERT INTO chapters(book_id, ord, title, start_page, end_page) VALUES(?,1,'Ch',1,1)", (bid,))
    words = client.get(f"/api/chapters/{cid}/words").json()["words"]
    assert any(w["word"] == "Computer" for w in words)
    added = client.post(f"/api/chapters/{cid}/words/cards", json={"words": words[:3]}).json()["added"]
    assert added == 3
    again = client.post(f"/api/chapters/{cid}/words/cards", json={"words": words[:3]}).json()["added"]
    assert again == 0  # already in the cards
    gaps = client.get(f"/api/chapters/{cid}/gapfill", params={"kind": "articles"}).json()
    assert gaps["items"] and all(i["kind"] == "articles" for i in gaps["items"])
    assert client.post("/api/gapfill/record", json={"kind": "articles", "correct": True}).json()["ok"]
