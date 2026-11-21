"""The B1 lessons (app/lessons_b1.py): complete, in the course format, and checked against the app's own
dictionary and verb engine, with Turkish for every English text."""
import re

import pytest

from app import dictionary, lessons, verbs
from app.lessons_b1 import LESSONS
from app.lessons_b1_tr import EXACT as TR
from app.lessons_data import LESSONS as A1
from app.packs import _items, _rows

# Names and the few words the offline dictionary doesn't have as a form (checked by hand).
NAMES = {"Demir", "Izmir", "Ankara", "Hamburg", "Brandt", "Jana", "Murat", "Bremen", "Köln", "Sophie", "Lukas",
         "Wien", "München", "Lehmann", "Kaya", "Roth", "Schulz", "Weber", "Yılmaz", "Becker", "Aydın", "Elif",
         "Thomas", "Novak", "Oma", "Leon", "Gisela", "Spanien", "Polen", "Nina", "Sami", "Paul", "Schmidt",
         "Deutschland", "Rossi", "Max", "Berger", "Jonas", "Keller", "Meyer", "Kılıç", "Aylin", "Lea", "Tim", "Ben",
         "Julia", "Marco", "Can", "Emma", "Petrov", "Sara", "Ali", "Mira", "Dennis", "Berlin", "Frau", "Herr"}
# Correct German the dictionary doesn't list as a form (checked by hand). Compound nouns it can split
# (Theaterverein = Theater + der Verein) count as known. Present participles used as adjectives
# (schlafendes) are not dictionary forms either.
NOT_IN_DICTIONARY = {"Onlinebanking", "Mathe", "mitschicken", "wiederbekommen", "lachendes", "schlafendes"}
NOT_LISTED_WORDS = {"geboren", "umweltfreundlich", "abwechslungsreich"}  # in the word lists
# Wrong choices are often invented forms on purpose ("beginnte"); only the right answers are checked.

SPEAKER_WORDS = {"Führerin", "Besucher", "Durchsage", "Mitarbeiter", "Beraterin", "Sachbearbeiterin",
                 "Verkäufer", "Ärztin", "Hausmeister"}


def _german_texts():
    """(lesson id, German sentence) for every dialogue line, grammar example and filled-in exercise."""
    for l in LESSONS:
        for r in _rows(l["dialogue"]):
            yield l["id"], r[1]
        for de, _en in _items(l["grammar"][2]):
            yield l["id"], de
        for r in _rows(l["exercises"]):
            yield l["id"], r[0].replace("___", r[1])


def test_ids_are_unique_and_prefixed():
    ids = [l["id"] for l in LESSONS]
    assert len(ids) == len(set(ids)) and 18 <= len(ids) <= 24
    assert all(i.startswith("b1-") for i in ids)
    assert not set(ids) & {l["id"] for l in A1}


def test_every_lesson_has_all_parts_and_a_working_quiz(monkeypatch):
    monkeypatch.setattr(lessons, "BY_ID", {**lessons.BY_ID, **{l["id"]: l for l in LESSONS}})
    for l in LESSONS:
        assert l["level"] == "B1" and l["title"] and l["subtitle"], l["id"]
        c = lessons._content(l)
        words = c["words"]
        assert 15 <= len(words) <= 20, (l["id"], len(words))
        assert len({w["de"] for w in words}) == len(words) and len({w["en"] for w in words}) == len(words), l["id"]
        assert len(c["dialogue"]) >= 6 and all(d["who"] and d["de"] and d["en"] for d in c["dialogue"]), l["id"]
        assert c["grammar"]["title"] and len(c["grammar"]["text"]) > 300 and len(c["grammar"]["examples"]) >= 4, l["id"]
        for r in _rows(l["exercises"]):
            assert len(r) == 4 and r[0].count("___") == 1 and len(set(r[1:])) == 3, (l["id"], r)
        assert 6 <= len(_rows(l["exercises"])) <= 8, l["id"]
        for seed in range(5):
            qs = lessons.quiz(l["id"], seed)
            assert 12 <= len(qs) <= 18, l["id"]
            for q in qs:
                assert q["answers"] and q["prompt"], (l["id"], q)
                if q["kind"] == "choice":
                    assert q["answers"][0] in q["choices"] and len(set(q["choices"])) == len(q["choices"]) >= 3, (l["id"], q)


def _noun_entries(word):
    return [e for e in dictionary.lookup(word, 8) if e["pos"] == "noun" and e["word"] == word]


# Where the dictionary's first reading is a different word with another gender, checked by hand.
GENDER_OK = {"Gehalt": "das"}  # das Gehalt (salary); der Gehalt is "content" (Alkoholgehalt)


@pytest.mark.skipif(not dictionary.available(), reason="no offline dictionary")
def test_noun_genders_match_the_dictionary():
    bad = []
    for l in LESSONS:
        for w in lessons._words(l):
            if not w["article"]:
                continue
            entries = _noun_entries(w["word"])
            genders = {dictionary.ARTICLE[g] for e in entries for g in e["genders"]}
            if not entries:
                bad.append((l["id"], w["de"], "not in the dictionary"))
            elif w["article"] not in genders and GENDER_OK.get(w["word"]) != w["article"]:
                bad.append((l["id"], w["de"], sorted(genders)))
    assert not bad


@pytest.mark.skipif(not dictionary.available(), reason="no offline dictionary")
def test_other_words_are_dictionary_words():
    bad = []
    for l in LESSONS:
        for w in lessons._words(l):
            if w["article"]:
                continue
            # "sich freuen auf" -> freuen; "sich erinnern" -> erinnern
            parts = [p for p in w["de"].split() if p != "sich"]
            head = parts[0]
            if head in NOT_LISTED_WORDS:
                continue
            if not any(e["word"] == head for e in dictionary.lookup(head, 8)):
                bad.append((l["id"], w["de"]))
    assert not bad


@pytest.mark.skipif(not dictionary.available(), reason="no offline dictionary")
def test_every_german_word_is_a_known_form():
    """Catches typos and invented forms in dialogues, examples and the right exercise answers."""
    bad = set()
    for lid, text in _german_texts():
        for tok in re.findall(r"[A-Za-zÄÖÜäöüßıİ]+(?:-[A-Za-zÄÖÜäöüß]+)*", text):
            if tok in NAMES or tok in NOT_IN_DICTIONARY or tok in SPEAKER_WORDS or "-" in tok:
                continue
            if not (dictionary.known(tok) or dictionary.known(tok.lower()) or dictionary.known(tok.capitalize())
                    or (tok[:1].isupper() and dictionary.compound(tok))):
                bad.add((lid, tok))
    assert not bad, sorted(bad)


# Principal parts written as "gehen → ging → ist gegangen" in grammar texts, checked against app/verbs.py.
PARTS = re.compile(r"(\w+) → (\w+) → (hat|ist) (\w+)")


def test_principal_parts_match_the_verb_engine():
    seen = 0
    for l in LESSONS:
        for inf, praet, aux, pp in PARTS.findall(l["grammar"][1]):
            v = verbs._BY_INF.get(inf)
            assert v, inf
            assert verbs.forms(v, "praet", 0)[0] == praet, (inf, praet)
            assert verbs.partizip(v) == pp and {"s": "ist", "h": "hat"}[v["aux"]] == aux, (inf, pp, aux)
            seen += 1
    assert seen >= 3


def test_praeteritum_answers_match_the_verb_engine():
    """The Präteritum lesson's answers are what the verb engine conjugates."""
    l = next(x for x in LESSONS if x["id"] == "b1-lebenslauf")
    person = {"Ich": 0, "ich": 0, "du": 1, "Er": 2, "er": 2, "sie": 2, "Wir": 3, "wir": 3}
    checked = 0
    for r in _rows(l["exercises"]):
        m = re.search(r"\((\w+)\)$", r[0])
        subject = next((w for w in re.findall(r"\w+", r[0]) if w in person), None)
        if not m or not subject:
            continue
        inf = m.group(1)
        v = verbs._BY_INF.get(inf) or next((x for x in verbs.VERBS if x["base"] == inf and x["prefix"]), None)
        assert v, inf
        expected = verbs._praet_simple(v)[person[subject]] if v["prefix"] else verbs.forms(v, "praet", person[subject])[0]
        assert r[1].lower() == expected.lower(), (r, expected)
        checked += 1
    assert checked >= 6


def _english_texts(l):
    yield l["subtitle"]
    for _de, en in _items(l["words"]):
        yield en
    for r in _rows(l["dialogue"]):
        yield r[2]
    title, text, examples = l["grammar"]
    yield title
    yield text
    for _de, en in _items(examples):
        yield en


def test_every_english_text_has_turkish():
    missing = [(l["id"], s) for l in LESSONS for s in _english_texts(l) if s.strip() not in TR]
    assert not missing, missing[:10]
    # Only grammar titles made of German words ("bevor, nachdem, während, seit") stay the same.
    same = [k for k, v in TR.items() if not v.strip() or (v == k and not any(k == l["grammar"][0] for l in LESSONS))]
    assert not same, same


def test_turkish_goes_through_the_app_translator(monkeypatch):
    from app import i18n
    monkeypatch.setattr(i18n, "lang", lambda: "tr")
    l = LESSONS[0]
    assert i18n.tr(l["subtitle"]) == TR[l["subtitle"]]
    assert i18n.tr(l["grammar"][1]) == TR[l["grammar"][1]]
