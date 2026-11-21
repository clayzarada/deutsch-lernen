"""Honest progress: level estimates per skill, the weekly goal and the monthly level check's scoring."""
import datetime as dt

from app import db, known, levels


def _reset():
    db.init()
    levels._init()
    known._init()
    for t in ("known_words", "cards", "decl_log", "writings", "level_checks", "activity", "reading", "reviews", "answers"):
        db.ex(f"DELETE FROM {t}")
    db.set_setting("level", "A2")
    db.set_setting("week_goal", "5")


def _bands(*shares):
    """Bands with the given weighted shares (0-1), 1000 words each."""
    return [{"top": top, "known": int(s * 1000), "learning": 0, "total": 1000, "pct": round(100 * s)}
            for (top, _l, _n), s in zip(levels.VOCAB_RULES, shares)]


# ---------- vocabulary ----------
def test_vocab_level_follows_the_frequency_bands():
    assert levels.vocab_level(_bands(.3, .2, .1, 0, 0))[0] is None
    lvl, nxt = levels.vocab_level(_bands(.9, .6, .4, .2, .1))
    assert lvl == 1  # A2: 40%+ of the top 500, 50%+ of the top 1000, but not 55% of the top 2000
    assert nxt["level"] == 2 and nxt["top"] == 2000 and nxt["words"] == 150
    assert levels.vocab_level(_bands(1, 1, 1, 1, 1)) == (4, None)


def test_learning_words_count_half():
    b = [{"top": 500, "known": 100, "learning": 200, "total": 500, "pct": 40}] + _bands(0, 0, 0, 0)[1:]
    assert levels.vocab_level(b)[0] == 0  # 100 + 200/2 = 200 = 40% of 500


def test_vocab_estimate_needs_enough_words():
    _reset()
    known.mark(["Haus", "gehen", "gut"], known.KNOWN)
    v = levels.vocab_estimate()
    assert v["enough"] is False and v["level"] is None
    top = [w for w, _r in levels.frequency_words()[:200]]
    known.mark(top, known.KNOWN)
    v = levels.vocab_estimate()
    assert v["enough"] and v["bands"][0]["known"] >= 195


def test_a_recent_check_can_lift_an_estimate_but_never_lower_it():
    out = {"enough": True, "level": 2}
    levels._merge_check(out, {"date": "2026-01-01", "result": {"vocab": 1}}, "vocab")
    assert out["level"] == 2
    levels._merge_check(out, {"date": "2026-01-01", "result": {"vocab": 3}}, "vocab")
    assert out["level"] == 3 and out["source"] == "check"
    empty = {"enough": False, "level": None}
    levels._merge_check(empty, {"date": "2026-01-01", "result": {"vocab": 0}}, "vocab")
    assert empty == {"enough": True, "level": 0, "source": "check", "check_date": "2026-01-01"}


# ---------- grammar ----------
def _rows(key, n, right):
    return [{"key": key, "correct": int(i < right)} for i in range(n)]


def test_grammar_levels_need_two_thirds_of_their_areas_solid():
    a1 = _rows("def:akk:m", 10, 9) + _rows("pers:akk:ich", 10, 8) + _rows("vb:praes:reg", 10, 10)
    g = levels.grammar_from_log(a1)
    assert g["level"] == 0
    assert g["next"]["level"] == 1 and "articles_dat" in g["next"]["areas"]
    # 9 of 20 dative answers right: weak, and it shows in the dative bar
    g = levels.grammar_from_log(a1 + _rows("def:dat:f", 20, 9))
    dat = next(c for c in g["cases"] if c["case"] == "dat")
    assert dat["n"] == 20 and dat["pct"] == 45
    assert next(a for a in g["areas"] if a["id"] == "articles_dat")["state"] == "weak"
    # too few answers: untested, which does not count as solid
    g = levels.grammar_from_log(_rows("def:akk:m", 9, 9) + _rows("vb:praes:reg", 10, 10))
    assert g["level"] is None


def test_grammar_case_accuracy_ignores_verbs_and_reads_trigger_keys():
    g = levels.grammar_from_log(_rows("vb:perf:aux", 5, 5) + _rows("trig:p:mit", 4, 2) + _rows("trig:unknown", 2, 2))
    cases = {c["case"]: c for c in g["cases"]}
    assert cases["dat"]["n"] == 4 and cases["dat"]["pct"] == 50
    assert sum(c["n"] for c in cases.values()) == 4


def test_grammar_reaching_b2():
    rows = []
    for key in ("def:akk:m", "pers:akk:du", "vb:praes:reg", "ein:dat:m", "pers:dat:er", "trig:p:mit", "vb:pp:weak",
                "vb:praes:sep", "adjw:dat:f", "rel:akk:m", "vb:praet:strong", "vb:fut1", "def:gen:m", "vb:plusq"):
        rows += _rows(key, 12, 12)
    g = levels.grammar_from_log(rows)
    assert g["level"] == 3 and g["next"] is None


# ---------- writing and reading ----------
def test_writing_needs_two_passed_texts():
    w = levels.writing_from_rows([{"level": "B1", "score": 70}])
    assert w["level"] is None and w["tentative"] == 2
    w = levels.writing_from_rows([{"level": "B1", "score": 70}, {"level": "A2", "score": 65}, {"level": "B2", "score": 40}])
    assert w["level"] == 1 and w["tentative"] == 2 and w["passed"] == 2


def test_reading_from_texts_and_fallback():
    r = levels.reading_from_texts([{"level": "B1", "known_pct": 95}, {"level": "B1", "known_pct": 92},
                                   {"level": "B2", "known_pct": 80}])
    assert r["level"] == 2 and r["comfortable"] == 2
    vocab = {"level": 1, "enough": True}
    assert levels.reading_estimate(vocab)["source"] == "vocab"
    levels.register_reading_source(lambda: [{"level": "A2", "known_pct": 99}] * 2)
    try:
        r = levels.reading_estimate(vocab)
        assert r["source"] == "texts" and r["level"] == 1
    finally:
        levels._READING_SOURCES.clear()


# ---------- the verdict ----------
def _s(skill, level, enough=True):
    return {"skill": skill, "level": level, "enough": enough}


def test_ready_only_when_every_rated_skill_is_above_the_setting():
    v = levels.verdict([_s("vocab", 2), _s("grammar", 2), _s("writing", None, False), _s("reading", 2)], 1)
    assert v["ready"] == 2
    v = levels.verdict([_s("vocab", 3), _s("grammar", 1), _s("writing", None, False), _s("reading", 3)], 1)
    assert v["ready"] is None and v["weakest"] == "grammar"
    v = levels.verdict([_s("vocab", 3), _s("grammar", None, False), _s("writing", None, False), _s("reading", None, False)], 1)
    assert v["ready"] is None and v["weakest"] is None and v["rated"] == 1
    v = levels.verdict([_s("vocab", 1), _s("grammar", None)], 1)  # below A1 counts as the weakest
    assert v["weakest"] == "grammar"


# ---------- weekly goal ----------
def test_week_goal_counts_days_this_week_and_rest_days_break_nothing():
    _reset()
    today = dt.date(2026, 11, 19)  # a Thursday
    for d in ("2026-11-16", "2026-11-18", "2026-11-12"):  # Monday, Wednesday, and last week's Thursday
        db.ex("INSERT INTO activity(kind, seconds, ts, date) VALUES('practice', 60, ?, ?)", (d + "T10:00:00", d))
    w = levels.week_goal(today)
    assert w["days"] == 2 and w["target"] == 5 and not w["met"]
    assert w["studied"] == [True, False, True, False, False, False, False] and w["today_index"] == 3
    db.set_setting("week_goal", "12")
    assert levels.week_goal(today)["target"] == 7
    db.set_setting("week_goal", "abc")
    assert levels.week_goal(today)["target"] == 5


# ---------- level check scoring ----------
def _items(section, pairs):
    return [{"section": section, "level": lvl, "correct": ok} for lvl, ok in pairs]


def test_score_section_takes_the_highest_level_passed_twice():
    assert levels.score_section([], 3) is None
    assert levels.score_section(_items("case", [(1, True)]), 3) is None  # one question is not enough
    seq = [(0, True), (1, True), (2, False), (1, True), (2, False), (1, True), (2, False), (1, True)]
    assert levels.score_section(_items("case", seq), 3) == 1
    seq = [(2, True), (3, False), (2, False), (1, True), (2, True), (3, False), (2, True)]
    assert levels.score_section(_items("case", seq), 3) == 2  # 3 of 4 right at B1
    assert levels.score_section(_items("case", [(0, False), (0, False), (0, True)]), 3) is None


def test_score_check_overall_is_the_middle_part():
    items = (_items("vocab", [(3, True), (3, True), (4, False)]) + _items("case", [(1, True), (1, True)])
             + _items("verb", [(2, True), (2, True), (3, False)]))
    r = levels.score_check(items)
    assert (r["vocab"], r["case"], r["verb"]) == (3, 1, 2)
    assert r["grammar"] == 1 and r["overall"] == 2
    assert r["right"] == 6 and r["total"] == 8 and r["sections"]["verb"] == {"n": 3, "right": 2}
    r = levels.score_check(_items("vocab", [(0, False), (0, False)]))
    assert r["overall"] is None and r["grammar"] is None


def test_adapting_and_marking():
    assert levels.next_level(2, True, 3) == 3 and levels.next_level(3, True, 3) == 3
    assert levels.next_level(0, False, 3) == 0 and levels.next_level(2, False, 3) == 1
    choice = {"kind": "choice", "answers": ["to go"]}
    assert levels.is_right(choice, "to go") and not levels.is_right(choice, "to see")
    text = {"kind": "text", "answers": ["dem Mann"]}
    assert levels.is_right(text, "  Dem  Mann. ") and not levels.is_right(text, "den Mann")


def test_questions_for_every_level_have_answers():
    for section, top in levels.SECTION_TOP.items():
        for lvl in range(top + 1):
            q = levels.make_question(section, lvl)
            assert q["answers"] and q["prompt"]
            if q["kind"] == "choice":
                assert len(q["choices"]) == 4 and q["answers"][0] in q["choices"]


# ---------- the whole check through the API ----------
def test_level_check_api(client):
    _reset()
    r = client.post("/api/level/check/start").json()
    cid, q = r["id"], r["question"]
    assert "answers" not in q and q["n"] == 1 and q["total"] == len(levels.CHECK_PLAN)
    out = None
    for _ in levels.CHECK_PLAN:
        out = client.post("/api/level/check/answer", json={"id": cid, "answer": "falsch"}).json()
        assert out["correct"] is False and out["display"]
    assert out["next"] is None and out["result"]["overall"] is None and out["result"]["total"] == len(levels.CHECK_PLAN)
    assert client.post("/api/level/check/answer", json={"id": cid, "answer": "x"}).status_code == 404
    s = client.get("/api/level").json()
    assert s["checks"][0]["id"] == cid and s["check_due"] is False
    assert s["week"]["today_done"] is True  # the check counts as a study day
    assert {sk["skill"] for sk in s["skills"]} == {"vocab", "grammar", "writing", "reading"}
    assert client.get("/api/stats").json()["week_goal"]["days"] >= 1
    b = client.get("/api/level/brief").json()
    assert set(b) == {"known", "learning", "week"}
