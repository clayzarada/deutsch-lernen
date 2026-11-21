"""Grammar: the handbook data, its search and Mistake Book links, the der/die/das rules, and typed sentence building."""
import re

import pytest

from app import db, decl, genderrules, grammar, verbs, wordorder, wordtrain
from app.grammar_data import LEVELS, THEMES, TOPICS

TURKISH_LETTERS = set("çğıöşüÇĞİÖŞÜ")


def _pair(v):
    return isinstance(v, tuple) and len(v) == 2 and all(isinstance(x, str) and x.strip() for x in v)


# ---------- handbook data ----------
def test_handbook_size_and_ids():
    assert 35 <= len(TOPICS) <= 45
    ids = [t["id"] for t in TOPICS]
    assert len(ids) == len(set(ids))
    themes = {k for k, _ in THEMES}
    for t in TOPICS:
        assert t["level"] in LEVELS and t["theme"] in themes, t["id"]
    assert {t["level"] for t in TOPICS} == set(LEVELS)


@pytest.mark.parametrize("t", TOPICS, ids=[t["id"] for t in TOPICS])
def test_every_topic_is_complete_in_both_languages(t):
    assert _pair(t["title"]) and _pair(t["summary"])
    kinds = [b[0] for b in t["body"]]
    assert "table" in kinds, "every topic has at least one table"
    for b in t["body"]:
        if b[0] == "table":
            cols, rows = b[1]["cols"], b[1]["rows"]
            assert rows and all(len(r) == len(cols) for r in rows)
            for cell in cols + [c for r in rows for c in r]:
                assert isinstance(cell, str) or _pair(cell)
        else:
            assert b[0] in ("p", "rule", "tip") and _pair(b[1:3])
    assert 4 <= len(t["examples"]) <= 8
    for ex in t["examples"]:
        assert len(ex) == 3 and all(x.strip() for x in ex)
    assert t["mistakes"]
    for m in t["mistakes"]:
        assert len(m) == 4 and all(x.strip() for x in m) and m[0] != m[1]
    # The note for Turkish speakers is written in Turkish.
    assert len(t["note"]) > 150 and TURKISH_LETTERS & set(t["note"])
    if t["match"]:
        re.compile(t["match"])


@pytest.mark.parametrize("t", [t for t in TOPICS if t["try"]], ids=[t["id"] for t in TOPICS if t["try"]])
def test_try_it_links_point_at_real_drills(t):
    spec = t["try"]
    assert spec["view"] in ("decl", "verbs")
    fams = {f[0] for f in (decl.FAMILIES if spec["view"] == "decl" else verbs.FAMILIES)}
    toggles = decl.CASES if spec["view"] == "decl" else verbs.TENSES
    assert set(spec.get("focus") or []) <= fams
    assert set(spec.get("cases") or []) <= set(toggles)
    assert set(spec.get("rules") or []) <= set(wordorder.RULES)
    assert spec["sub"] in ("drill", "nouns", "order", "tables")


def test_every_drill_skill_has_a_handbook_topic():
    keys = decl._core_keys() | verbs.core_keys() | set(wordorder.KEYS)
    missing = sorted(k for k in keys if not grammar.skill_topic(k))
    assert not missing, missing[:10]


@pytest.mark.parametrize("key, topic", [
    ("adjm:dat:f", "adj-ein"), ("adjw:nom:m", "adj-der"), ("adjs:gen:n", "adj-none"), ("def:dat:m", "dative"),
    ("def:akk:m", "accusative"), ("poss:dat:f", "possessives"), ("trig:p:wegen", "prep-gen"), ("trig:p:mit", "prep-dat"),
    ("trig:p:für", "prep-akk"), ("trig:w:in:wo", "two-way"), ("trig:v:helfen", "dative"), ("rel:gen:m", "relative"),
    ("noun:dat:weak", "n-decl"), ("vb:pp:sep", "separable"), ("vb:pp:strong", "partizip"), ("vp:gehen", "praeteritum"),
    ("vb:konj2:wuerde", "konj2"), ("wo:sub", "subordinate"), ("wo:inv", "v2"),
])
def test_skill_topics(key, topic):
    assert grammar.skill_topic(key) == topic


@pytest.mark.parametrize("q, first", [("wegen", "prep-gen"), ("dessen", "relative"), ("Wechselpräpositionen", "two-way"),
                                       ("konjunktiv", "konj2"), ("adjective endings", "adj-endings"), ("sıfat", "adj-endings"),
                                       ("TeKaMoLo", "tekamolo"), ("Partizip", "partizip")])
def test_search_finds_topics_and_german_words(q, first):
    assert grammar.search(q)[0] == first


def test_search_needs_every_word_and_empty_lists_all():
    assert grammar.search("zzzz nothing") == []
    assert len(grammar.search("")) == len(TOPICS)


# ---------- Mistake Book links ----------
@pytest.mark.parametrize("m, topic", [
    ({"topic": "Dativ articles", "explanation": "mit takes the dative"}, "dative"),
    ({"topic": "Perfekt with sein"}, "perfekt"),
    ({"topic": "Adjective endings"}, "adj-endings"),
    ({"topic": "Adjectives", "skills": '["adjw:akk:m"]'}, "adj-der"),
    ({"topic": "Word order", "explanation": "After weil the verb goes to the end."}, "subordinate"),
    ({"topic": "Word order"}, "v2"),
    ({"topic": "Wechselpräpositionen"}, "two-way"),
    ({"topic": "food vocabulary", "explanation": "Brot means bread."}, None),
    ({"topic": "Spelling", "wrong": "Ich habe ein Hund", "correct": "Ich habe einen Hund"}, None),
])
def test_mistakes_are_linked_by_rules(m, topic):
    assert grammar.mistake_topic(m) == topic


def test_mistake_links_api(client):
    db.ex("INSERT INTO mistakes(source, topic, wrong, correct, explanation, status, created_at, last_seen) "
          "VALUES('practice', 'Relative pronouns', 'der', 'dessen', 'whose = dessen', 'open', ?, ?)", (db.now(), db.now()))
    mid = db.q1("SELECT MAX(id) AS id FROM mistakes")["id"]
    links = client.get("/api/grammar/mistakes").json()["links"]
    assert links[str(mid)]["id"] == "relative"


def test_topic_api_in_both_languages(client):
    en = client.get("/api/grammar/topic/two-way").json()
    assert en["title"].startswith("Two-way") and en["examples"][0]["de"] and en["try"]["view"] == "decl"
    client.put("/api/settings", json={"ui_language": "tr"})
    try:
        tr = client.get("/api/grammar/topic/two-way").json()
        assert tr["title"].startswith("İki yönlü") and tr["examples"][0]["de"] == en["examples"][0]["de"]
        assert tr["body"][1]["cols"][0] == "Fiiller"
    finally:
        client.put("/api/settings", json={"ui_language": "en"})
    assert client.get("/api/grammar/topic/nope").status_code == 400


# ---------- der, die, das rules ----------
@pytest.mark.parametrize("word, gender, rule, fits", [
    ("Zeitung", "f", "ung", True), ("Freiheit", "f", "heit", True), ("Möglichkeit", "f", "heit", True),
    ("Freundschaft", "f", "schaft", True), ("Information", "f", "ion", True), ("Universität", "f", "taet", True),
    ("Musik", "f", "ik", True), ("Konferenz", "f", "enz", True), ("Polizei", "f", "ei", True), ("Lampe", "f", "e", True),
    ("Mädchen", "n", "chen", True), ("Museum", "n", "um", True), ("Dokument", "n", "ment", True), ("Ergebnis", "n", "nis", True),
    ("Tourismus", "m", "ismus", True), ("Frühling", "m", "seasons", True), ("Lehrling", "m", "ling", True),
    ("Polizist", "m", "ist", True), ("Motor", "m", "or", True), ("Montag", "m", "days", True), ("Januar", "m", "months", True),
    ("Sonntagabend", "m", "times", True), ("Regen", "m", "weather", True), ("Lehrer", "m", "agent", True),
    ("Essen", "n", "inf", True),
    # exceptions: the rule applies, but this noun breaks it
    ("Kuchen", "m", "chen", False), ("Kollege", "m", "e", False), ("Erlaubnis", "f", "nis", False), ("Moment", "m", "ment", False),
    ("Gewitter", "n", "weather", False), ("Stadion", "n", "ion", False),
    # no rule
    ("Tisch", "m", None, None), ("Baum", "m", None, None), ("Kosten", "pl", "inf", False),
])
def test_gender_rules_predict_sample_nouns(word, gender, rule, fits):
    rid, ok, note = genderrules.explain(word, gender)
    assert rid == rule and ok == fits
    assert note.startswith("No rule" if rule is None else ("Rule:" if fits else "Exception!"))


def test_gender_rule_reliability_matches_the_dictionary():
    """Each rule's stated reliability is close to what it really does on the app's dictionary nouns."""
    from app import dictionary
    if not dictionary.available():
        pytest.skip("no dictionary")
    counts = {}
    for n in dictionary.nouns(0, 10 ** 6):
        r = genderrules.predict(n["word"])
        if r:
            c = counts.setdefault(r["id"], [0, 0])
            c[0] += r["g"] == n["g"].split(",")[0]
            c[1] += 1
    for r in genderrules.RULES:
        right, total = counts.get(r["id"], (0, 0))
        if total >= 20:
            assert abs(100 * right / total - r["pct"]) <= 5, (r["id"], right, total)


def test_rule_mastery_is_counted():
    before = {r["id"]: r for r in genderrules.progress()["rules"]}
    assert not before["ismus"]["mastered"]
    for _ in range(genderrules.MASTER_MIN):
        genderrules.record("ismus", "Tourismus", True)
    genderrules.record("ment", "Moment", False)
    genderrules.record(None, "Tisch", True)
    p = genderrules.progress()
    rules = {r["id"]: r for r in p["rules"]}
    assert rules["ismus"]["mastered"] and not rules["ment"]["mastered"]
    assert p["mastered"] >= 1 and p["by_heart"]["answered"] >= 1


def test_noun_drill_shows_the_rule_and_can_focus_on_one(client):
    q = wordtrain.noun_question("650", "gender", rule="ung")
    assert q["prompt"].lower().endswith("ung") and q["rule_id"] == "ung" and q["rule_note"]
    answered = {r["id"]: r["answered"] for r in client.get("/api/genders/rules").json()["rules"]}["ung"]
    r = client.post("/api/nouns/answer", json={"question": q, "answer": "die", "rule": "ung", "mode": "gender"}).json()
    assert r["correct"] and r["next"]["rule_id"] == "ung"
    after = {r["id"]: r["answered"] for r in client.get("/api/genders/rules").json()["rules"]}["ung"]
    assert after == answered + 1


# ---------- typed sentence building ----------
def _sid(german):
    return next(s["id"] for s in wordorder.SENTENCES if " ".join(s["chunks"]) + s["end"] == german)


@pytest.mark.parametrize("german, typed, verdict", [
    ("Ich bleibe heute zu Hause, weil ich krank bin.", "ich bleibe heute zu hause weil ich krank bin", "right"),
    ("Ich bleibe heute zu Hause, weil ich krank bin.", "Ich bleibe heute zu Hause, weil ich bin krank.", "order"),
    ("Ich möchte einen Kaffee bestellen.", "Ich moechte einen Kaffee bestellen", "right"),
    ("Morgen fahre ich nach Hamburg.", "fahre ich nach Hamburg", "right"),          # the given start may be left out
    ("Morgen fahre ich nach Hamburg.", "Morgen ich fahre nach Hamburg.", "order"),
    ("Mein Bruder wohnt seit drei Jahren in Berlin.", "Mein Bruder wohnt in Berlin seit drei Jahren.", "right"),
    ("Können Sie mir helfen?", "Kannst du mir helfen?", "right"),                   # another "you"
    ("Wir trinken jeden Morgen einen Kaffee.", "Wir trinken jeden Morgen einen Kafee.", "typo"),
    ("Wir kaufen am Samstag im Supermarkt ein.", "Wir kaufen im Supermarkt am Samstag ein.", "middle"),
    ("Wir kaufen am Samstag im Supermarkt ein.", "Wir einkaufen am Samstag im Supermarkt.", "words"),
    ("Ich glaube, dass er morgen kommt.", "Ich glaube, dass er kommt.", "words"),
])
def test_typed_answers(german, typed, verdict):
    assert grammar.compare(typed, _sid(german))["verdict"] == verdict


def test_typed_answer_shows_missing_words_as_written():
    r = grammar.compare("Ich glaube, dass er kommt.", _sid("Ich glaube, dass er morgen kommt."))
    assert r["missing"] == ["morgen"] and r["extra"] == []
    r = grammar.compare("Ich bleibe heute zu Hause, weil ich müde bin.", _sid("Ich bleibe heute zu Hause, weil ich krank bin."))
    assert r["missing"] == ["krank"] and r["extra"] == ["müde"]


def test_typed_check_with_hint_does_not_raise_the_skill(client):
    sid = _sid("Ich rufe dich heute Abend an.")
    key = "wo:sep"
    box = lambda: (db.q1("SELECT box FROM decl_skills WHERE key=?", (key,)) or {"box": 0})["box"]
    start = box()
    r = client.post("/api/wordorder/typed/check", json={"id": sid, "answer": "Ich rufe dich heute Abend an", "hinted": True}).json()
    assert r["correct"] and box() == start
    r = client.post("/api/wordorder/typed/check", json={"id": sid, "answer": "Ich rufe dich heute Abend an"}).json()
    assert r["correct"] and box() == start + 1 and "Ich rufe Sie heute Abend an." in r["also"]


def test_typed_next_api(client):
    q = client.post("/api/wordorder/typed/next", json={"rules": ["sub"]}).json()
    s = wordorder.SENTENCES[q["id"]]
    assert s["rule"] == "sub" and q["start"] == " ".join(s["chunks"][:s["lock"]]) and q["meaning"] and q["tiles"]
