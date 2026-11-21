"""The course by level: A1 and A2 lessons (B1 when present), stable ids, Turkish, dictionary checks and level tests."""
import pytest

from app import db, dictionary, i18n, lessoncheck, lessons, leveltest
from app.packs import _rows

# Progress is stored by lesson id, so these must never change (new lessons only get added).
A1_IDS = ["hallo", "woher", "zahlen", "cafe", "familie", "tag", "einkaufen", "wohnung", "stadt", "freizeit", "termine",
          "gestern", "beruf", "datum", "arzt", "kleidung", "wetter", "bahn", "wo", "unterwegs"]
A2_IDS = ["urlaub", "frueher", "schulzeit", "geschenke", "restaurant", "nachbarn", "verkehr", "umzug", "mode",
          "wohnungssuche", "vergleich", "morgens", "interessen", "umwelt", "gesundheit", "arbeit", "reise", "medien",
          "amt", "lebenslauf"]


def _ids(level):
    return [l["id"] for l in lessons.LESSONS if l["level"] == level]


def test_levels_in_order_with_stable_unique_ids():
    ids = [l["id"] for l in lessons.LESSONS]
    assert len(ids) == len(set(ids))
    assert _ids("A1") == A1_IDS and _ids("A2") == A2_IDS
    assert ids[:len(A1_IDS) + len(A2_IDS)] == A1_IDS + A2_IDS  # B1 (if there) comes after
    assert lessons.LEVELS[:2] == ["A1", "A2"]
    assert all(l.get("unit") for l in lessons.LESSONS if l["level"] in ("A1", "A2"))


def test_every_lesson_has_its_parts_and_builds_a_quiz_in_both_languages():
    for l in lessons.LESSONS:
        for tr in (False, True):
            c = lessons._content(l, tr)
            assert 12 <= len(c["words"]) <= 20 and len(c["dialogue"]) >= 5 and len(c["grammar"]["examples"]) >= 3, l["id"]
            qs = lessons.quiz(l["id"], 7, tr=tr)
            assert 12 <= len(qs) <= 18, l["id"]
            for q in qs:
                assert q["answers"] and q["prompt"], (l["id"], q)
                if q["kind"] == "choice":
                    assert q["answers"][0] in q["choices"] and len(set(q["choices"])) == len(q["choices"]) >= 3, (l["id"], q)
        for r in _rows(l["exercises"]):
            assert len(r) == 4 and r[0].count("___") == 1 and len(set(r[1:])) == 3, (l["id"], r)


@pytest.mark.skipif(not dictionary.available(), reason="no offline dictionary")
def test_lessons_match_the_dictionary_and_have_turkish():
    assert lessoncheck.problems() == []


def test_turkish_lesson_content():
    c = lessons._content(lessons.BY_ID["hallo"], True)
    assert c["subtitle"] == "Selamlaşma ve adınızı söyleme"
    assert c["words"][0] == {"de": "Hallo", "en": "merhaba", "article": "", "word": "Hallo"}
    assert c["dialogue"][0]["de"].startswith("Hallo! Ich bin Anna") and c["dialogue"][0]["en"] == "Merhaba! Ben Anna. Adın ne?"
    assert c["grammar"]["title"] == "du mu, Sie mi?" and "**du**" in c["grammar"]["text"]
    for l in lessons.LESSONS:
        en, tr = lessons._content(l), lessons._content(l, True)
        assert tr["subtitle"] != en["subtitle"] and tr["grammar"]["text"] != en["grammar"]["text"], l["id"]
        assert all(a["en"] != b["en"] for a, b in zip(en["dialogue"], tr["dialogue"])), l["id"]
    # hints in exercise sentences, and meaning choices, are in Turkish
    qs = lessons.quiz("familie", 1, tr=True)
    assert "___ Mutter heißt Anna. (benim)" in [q["prompt"] for q in qs]
    meanings = {w["en"] for w in lessons._words(lessons.BY_ID["familie"], True)}
    assert all(set(q["choices"]) <= meanings for q in qs if q["cue"] == "What does it mean?")
    # the A1 and A2 Turkish is in the app's table too, like the B1 Turkish
    assert i18n.EXACT["one-way; simple"] == "tek yön, basit"


def test_level_tests_build_from_each_level():
    for level in lessons.LEVELS:
        for tr in (False, True):
            qs = leveltest.build(level, seed=3, tr=tr)
            assert 25 <= len(qs) <= 45, level
            for q in qs:
                assert q["answers"] and q["prompt"] and q["cue"], (level, q)
                if q["kind"] == "choice":
                    assert q["answers"][0] in q["choices"] and len(set(q["choices"])) == len(q["choices"]) >= 3, (level, q)
    own = {r[0] for r in _rows(lessons.TESTS["A1"])}
    assert any(q["prompt"] in own for q in leveltest.build("A1", seed=1, tr=False))
    assert any(q["prompt"] == "Heute ist der ___ Juni. (2.)" for s in range(30) for q in leveltest.build("A1", s, tr=True))


def test_level_test_scoring_and_progress(client):
    db.ex("DELETE FROM lesson_progress")
    t = client.get("/api/levels/A1/test").json()
    n = len(t["quiz"])
    assert t["level"] == "A1" and t["pass"] == 0.75 and t["lessons"] == 20 and not t["passed"]
    r = client.post("/api/levels/A1/test/complete", json={"results": [True] * (n // 2) + [False] * (n - n // 2)}).json()
    assert not r["passed"] and r["overview"]["levels"][0]["test"] == {"best": n // 2, "total": n, "passed": False, "tries": 1}
    assert r["overview"]["next"] == "hallo"
    r = client.post("/api/levels/A1/test/complete", json={"results": [True] * n}).json()
    a1 = r["overview"]["levels"][0]
    assert r["passed"] and a1["test"]["passed"] and a1["test"]["best"] == n and a1["test"]["tries"] == 2
    # a passed level stays passed; the suggested lesson moves on to the first level not passed
    client.post("/api/levels/A1/test/complete", json={"results": [False] * n})
    o = client.get("/api/lessons").json()
    assert o["levels"][0]["test"]["passed"] and o["levels"][0]["test"]["best"] == n
    assert o["next"] == "urlaub"
    client.put("/api/settings", json={"use_course": "1"})
    assert client.get("/api/stats").json()["course"]["next"]["id"] == "urlaub"
    blocks = client.post("/api/plan/quick", json={"minutes": 30}).json()["blocks"]
    assert blocks[0]["kind"] == "course" and blocks[0]["lesson_id"] == "urlaub" and blocks[0]["title"].startswith("A2 · Lesson 1:")
    assert client.get("/api/levels/C2/test").status_code == 404
    assert client.post("/api/levels/A1/test/complete", json={"results": []}).status_code == 400
    db.ex("DELETE FROM level_tests")
    assert client.get("/api/lessons").json()["next"] == "hallo"


def test_level_progress_counts_and_new_lesson_cards(client):
    db.ex("DELETE FROM lesson_progress")
    n = len(client.get("/api/lessons/urlaub").json()["quiz"])
    client.post("/api/lessons/urlaub/complete", json={"results": [True] * n})
    o = client.get("/api/lessons").json()
    a2 = next(x for x in o["levels"] if x["level"] == "A2")
    assert a2["done"] == 1 and a2["total"] == 20 and o["next"] == "hallo"
    row = next(x for x in o["lessons"] if x["id"] == "urlaub")
    assert row["level"] == "A2" and row["ln"] == 1 and row["unit"] == "Travel"
    l = client.get("/api/lessons/urlaub").json()
    assert l["level"] == "A2" and l["ln"] == 1 and l["level_count"] == 20 and l["next"] == "frueher"
    assert client.post("/api/lessons/urlaub/cards").json()["added"] == len(l["words"])
    tags = db.q1("SELECT tags FROM cards WHERE front='das Meer'")["tags"]
    assert "lesson:urlaub" in tags and "level:A2" in tags
    db.ex("DELETE FROM lesson_progress")


def test_turkish_through_the_routes(client):
    client.put("/api/settings", json={"ui_language": "tr"})
    try:
        l = client.get("/api/lessons/arzt").json()
        assert l["subtitle"] == "Vücut, hastalık ve doktorun tavsiyeleri"
        assert {"de": "der Kopf", "en": "baş, kafa", "article": "der", "word": "Kopf"} in l["words"]
        assert l["grammar"]["examples"][0] == {"de": "Trink viel Wasser!", "en": "Bol su iç!"}
        o = client.get("/api/lessons").json()
        assert next(x for x in o["lessons"] if x["id"] == "reise")["subtitle"] == "Seyahat planları ve koşullar: wenn"
        if "B1" in lessons.LEVELS:
            first = _ids("B1")[0]
            b1 = client.get(f"/api/lessons/{first}").json()
            assert b1["dialogue"][0]["en"] != lessons._content(lessons.BY_ID[first])["dialogue"][0]["en"]
    finally:
        client.put("/api/settings", json={"ui_language": "en"})
