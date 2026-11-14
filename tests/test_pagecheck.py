"""Page checking: typed answers reach the AI as text in the right place, and re-checks only send what changed."""
import json

import pymupdf
import pytest

LINES = ["Exercise 4.2", "Fill in the endings.", "Das ist ein___ gute Idee!", "Er folgte d___ Auto.",
         "Translate into German.", "He has a son and a daughter."]
Y0, STEP, SIZE = 100, 30, 11


@pytest.fixture()
def book(client, tmp_path):
    from app import db
    doc = pymupdf.open()
    page = doc.new_page(width=600, height=800)
    for n, t in enumerate(LINES):
        page.insert_text((60, Y0 + n * STEP), t, fontsize=SIZE)
        if n in (2, 3):
            page.insert_text((40, Y0 + n * STEP), str(n - 1), fontsize=SIZE)  # the item number in its own spot
    page.insert_text((570, 300), "8111", fontsize=7)  # margin numbering, as some books print it
    db.BOOKS.mkdir(parents=True, exist_ok=True)
    doc.save(db.BOOKS / "check.pdf")
    bid = db.ex("INSERT INTO books(title, filename, page_count, created_at) VALUES('T','check.pdf',1,?)", (db.now(),))
    return bid


def _box(client, bid, text, x, line, below=0.0):
    """A typed answer at x (0..1) on printed line `line` (or `below` lines lower)."""
    y = (Y0 + (line + below) * STEP - SIZE) / 800
    return client.post("/api/annotations", json={"book_id": bid, "page": 1, "kind": "text", "x": x, "y": y,
                                                 "data": {"text": text, "size": 12, "color": "#1d4ed8"}}).json()["id"]


def test_answers_are_placed_in_their_lines(client, book):
    from app import db, pagecheck
    _box(client, book, "eine", .5, 2)
    _box(client, book, "Er hat einen Sohn\nund eine Tochter.", .1, 5, below=.9)  # on the blank line under, two lines
    annots = [{**a, "data": json.loads(a["data"])} for a in db.q("SELECT * FROM annotations WHERE book_id=?", (book,))]
    text, answers, ink = pagecheck.transcript(db.BOOKS / "check.pdf", 1, annots)
    lines = text.splitlines()
    assert not ink and len(answers) == 2
    assert any("1 Das ist ein___ gute Idee! ⟦A1: eine⟧" in l for l in lines), text
    assert any("He has a son and a daughter." in l and "⟦A2: Er hat einen Sohn und eine Tochter.⟧" in l for l in lines), text
    assert "8111" not in text  # margin numbers are dropped


def test_recheck_only_sends_changed_answers(client, book, monkeypatch):
    from app import ai
    calls = []

    def fake(page, refs):
        calls.append((refs, None))
        return {"summary": "ok", "items": [
            {"refs": r, "exercise": r, "question": "q", "student_answer": "a", "verdict": "correct", "correction": "",
             "corrected_sentence": "", "explanation": "", "topic": "Articles"} for r in refs]}
    monkeypatch.setattr(ai, "check_page_text", fake)
    a1 = _box(client, book, "eine", .5, 2)
    _box(client, book, "dem", .5, 3)
    check = lambda: client.post(f"/api/books/{book}/check_page", json={"page": 1, "image": "data:image/jpeg;base64,AAAA"}).json()

    r = check()
    assert calls[-1] == (["A1", "A2"], None) and len(r["items"]) == 2  # no handwriting: no image sent

    r = check()  # nothing changed: no AI call at all
    assert len(calls) == 1 and len(r["items"]) == 2 and r["reused"] == 2

    client.put(f"/api/annotations/{a1}", json={"book_id": book, "page": 1, "kind": "text", "x": .5,
                                               "y": (Y0 + 2 * STEP - SIZE) / 800,
                                               "data": {"text": "eine.", "size": 12, "color": "#1d4ed8"}})
    r = check()
    assert calls[-1][0] == ["A1"] and len(r["items"]) == 2 and r["reused"] == 1

    client.post("/api/annotations", json={"book_id": book, "page": 1, "kind": "ink", "x": 0, "y": 0,
                                          "data": {"points": [[.1, .5], [.2, .5]], "color": "#000", "width": 2}})
    n = len(calls)
    r = check()
    assert len(calls) == n and r["reused"] == 2  # pen marks (circles, brackets) aren't answers: nothing to send


def test_quick_tasks_use_the_quick_model(client):
    from app import ai, db
    db.set_setting("model", "claude-sonnet-5-5")
    db.set_setting("quick_model", "claude-haiku-5-5")
    assert ai.model_for("lookup") == "claude-haiku-5-5"
    assert ai.model_for("check_page_text") == "claude-haiku-5-5"
    assert ai.model_for("check_page") == "claude-sonnet-5-5"  # scanned pages, read from the picture
    assert ai.model_for("generate_exercises") == "claude-sonnet-5-5"
    db.set_setting("quick_model", "")
    assert ai.model_for("lookup") == "claude-sonnet-5-5"


def _item(ref, verdict="correct"):
    return {"refs": ref, "exercise": ref, "question": "q", "student_answer": "a", "verdict": verdict,
            "correction": "c" if verdict != "correct" else "", "corrected_sentence": "", "explanation": "", "topic": "t"}


def test_marking_asks_again_when_answers_are_missing_and_double_checks_mistakes(monkeypatch):
    from app import ai
    refs = ["A1", "A2", "A3", "A4", "A5"]
    replies = [{"summary": "s", "items": [_item("A2", "incorrect")]},  # left most answers out
               {"summary": "s", "items": [_item(r, "incorrect" if r in ("A2", "A3") else "correct") for r in refs]},
               {"results": [{"n": 0, "student_is_right": True}, {"n": 1, "student_is_right": False}]}]
    sent = []

    def fake_call(system, content, schema=None, effort=None, **kw):
        sent.append((content, effort))
        return replies[len(sent) - 1]
    monkeypatch.setattr(ai, "call", fake_call)
    r = ai.check_page_text("L1: page", refs)
    assert len(sent) == 3 and "IMPORTANT" in sent[1][0] and sent[2][1] == "high"
    verdicts = {i["refs"]: i["verdict"] for i in r["items"]}
    assert verdicts == {"A1": "correct", "A2": "correct", "A3": "incorrect", "A4": "correct", "A5": "correct"}
