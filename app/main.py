"""FastAPI server: JSON API under /api plus the single-page web UI under /static."""
import json
import os
import re
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from . import ai, anki, backup, course, db, decl, mistakelink, pdfs, planner, srs, tts, update, usage, verbs, writing
from .verbcourse import VERBS_COURSE
from .version import AUTHOR, BUILD_NAME, COPYRIGHT, OWNER, VERSION, WEBSITE
from .i18n import localize

DOC_TYPES = (".pdf", ".html", ".htm", ".txt", ".md")
AUDIO_TYPES = {".mp3": "audio/mpeg", ".m4a": "audio/mp4", ".wav": "audio/wav", ".ogg": "audio/ogg",
               ".webm": "audio/webm", ".aac": "audio/aac"}

ROOT = db.ROOT
STATIC = ROOT / "static"
ENV_PATH = Path(os.environ["GERMANSTUDY_ENV"]) if os.environ.get("GERMANSTUDY_ENV") else ROOT / ".env"
load_dotenv(ENV_PATH)
db.init()
try:
    backup.daily()
except Exception as _e:  # a failed backup must never stop the app from starting
    print('daily backup failed:', _e)

app = FastAPI(title="German Study")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.middleware("http")
async def _revalidate_static(request, call_next):
    # Make the browser check for newer app files on every load, so updates show up right away.
    response = await call_next(request)
    if request.url.path.startswith("/static/") and "/vendor/" not in request.url.path:
        response.headers["Cache-Control"] = "no-cache"
    return response


@app.exception_handler(ai.AIError)
def _ai_error(_, exc):
    return JSONResponse({"detail": str(exc)}, status_code=502)


@app.exception_handler(db.UserError)
def _user_error(_, exc):
    return JSONResponse({"detail": str(exc)}, status_code=400)


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html", headers={"Cache-Control": "no-store"})


def _book(book_id):
    b = db.q1("SELECT * FROM books WHERE id=?", (book_id,))
    if not b:
        raise HTTPException(404, "Book not found")
    return b


def _chapter(chapter_id):
    c = db.q1("SELECT * FROM chapters WHERE id=?", (chapter_id,))
    if not c:
        raise HTTPException(404, "Chapter not found")
    return c


def _chapter_text(c):
    b = _book(c["book_id"])
    return pdfs.page_text(db.BOOKS / b["filename"], c["start_page"], c["end_page"])


# ---------- Settings ----------

def _write_env_key(name, key):
    lines = ENV_PATH.read_text().splitlines() if ENV_PATH.exists() else []
    lines = [l for l in lines if not l.startswith(f"{name}=")]
    if key:
        lines.append(f"{name}={key}")
    ENV_PATH.write_text("\n".join(lines) + "\n")
    if key:
        os.environ[name] = key
    else:
        os.environ.pop(name, None)


@app.get("/api/version")
def get_version():
    return {"version": VERSION, "name": BUILD_NAME}


@app.get("/api/update")
def get_update(force: bool = False):
    """Is a newer release out? Checked at most once a day unless force=true (the Settings button)."""
    return update.status(force)


@app.post("/api/update/install")
def install_update():
    """Download (Windows app) or pull (git copy) the newest version in the background."""
    return update.start_install()


@app.get("/api/update/progress")
def update_progress():
    return update.progress()


@app.post("/api/update/restart")
def restart_for_update():
    """Windows app: quit and let the helper swap in the new version and reopen the app."""
    return update.restart_to_finish()


@app.get("/api/settings")
def get_settings():
    return {**db.get_settings(), "voices": tts.VOICES, "version": VERSION, "build_name": BUILD_NAME, "credits": {"author": AUTHOR, "owner": OWNER, "copyright": COPYRIGHT, "website": WEBSITE},
            "has_key": bool(os.environ.get("ANTHROPIC_API_KEY", "").strip()),
            "has_gemini_key": bool(os.environ.get("GEMINI_API_KEY", "").strip())}


@app.put("/api/settings")
def put_settings(body: dict):
    if "api_key" in body:
        _write_env_key("ANTHROPIC_API_KEY", body.pop("api_key").strip())
    if "gemini_key" in body:
        _write_env_key("GEMINI_API_KEY", body.pop("gemini_key").strip())
    for k, v in body.items():
        if k in db.DEFAULT_SETTINGS:
            db.set_setting(k, v)
    return get_settings()


# ---------- Books & chapters ----------

@app.get("/api/books")
def list_books():
    books = db.q("SELECT * FROM books ORDER BY id DESC")
    read = planner.pages_read_by_book()
    for b in books:
        b["chapters"] = db.q("SELECT * FROM chapters WHERE book_id=? ORDER BY ord", (b["id"],))
        b["pages_read"] = read.get(b["id"], 0)
    return books


def _as_html(raw, ext):
    text = raw.decode("utf-8", errors="replace")
    if ext in (".html", ".htm"):
        return text
    esc = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    paras = [p.strip() for p in esc.split("\n\n") if p.strip()]
    return "".join(f"<h2>{p.lstrip('#').strip()}</h2>" if p.startswith("#") else f"<p>{p.replace(chr(10), '<br>')}</p>"
                   for p in paras)


@app.post("/api/books")
def upload_book(file: UploadFile = File(...)):
    ext = Path(file.filename).suffix.lower()
    if ext not in DOC_TYPES:
        raise HTTPException(400, "Please choose a PDF, HTML, Markdown or text file.")
    name = f"{uuid.uuid4().hex}.pdf"
    path = db.BOOKS / name
    try:
        if ext == ".pdf":
            with open(path, "wb") as f:
                while chunk := file.file.read(1 << 20):
                    f.write(chunk)
        else:  # e.g. sources exported from Gemini Notebook via Google Takeout
            pdfs.html_to_pdf(_as_html(file.file.read(), ext), path)
        count, chapters = pdfs.detect_chapters(path)
    except Exception:
        path.unlink(missing_ok=True)
        raise HTTPException(400, "That file couldn't be opened.")
    title = Path(file.filename).stem
    book_id = db.ex("INSERT INTO books(title, filename, page_count, created_at) VALUES(?,?,?,?)",
                    (title, name, count, db.now()))
    db.exmany("INSERT INTO chapters(book_id, ord, title, start_page, end_page) VALUES(?,?,?,?,?)",
              [(book_id, i, t, s, e) for i, (t, s, e) in enumerate(chapters)])
    return get_book(book_id)


@app.get("/api/books/{book_id}")
def get_book(book_id: int):
    b = _book(book_id)
    b["chapters"] = db.q("SELECT * FROM chapters WHERE book_id=? ORDER BY ord", (book_id,))
    return b


@app.put("/api/books/{book_id}")
def update_book(book_id: int, body: dict):
    _book(book_id)
    if "title" in body:
        db.ex("UPDATE books SET title=? WHERE id=?", (body["title"], book_id))
    if "last_page" in body:
        db.ex("UPDATE books SET last_page=? WHERE id=?", (int(body["last_page"]), book_id))
    return {"ok": True}


@app.delete("/api/books/{book_id}")
def delete_book(book_id: int):
    b = _book(book_id)
    db.ex("DELETE FROM books WHERE id=?", (book_id,))
    (db.BOOKS / b["filename"]).unlink(missing_ok=True)
    (db.THUMBS / f"{book_id}.png").unlink(missing_ok=True)
    return {"ok": True}


@app.get("/api/books/{book_id}/file")
def book_file(book_id: int):
    return FileResponse(db.BOOKS / _book(book_id)["filename"], media_type="application/pdf")


@app.get("/api/books/{book_id}/thumb")
def book_thumb(book_id: int):
    b = _book(book_id)
    out = db.THUMBS / f"{book_id}.png"
    if not out.exists():
        pdfs.thumbnail(db.BOOKS / b["filename"], out)
    return FileResponse(out, media_type="image/png")


@app.put("/api/books/{book_id}/chapters")
def save_chapters(book_id: int, body: dict):
    b = _book(book_id)
    keep = []
    for i, c in enumerate(body["chapters"]):
        start, end = int(c["start_page"]), int(c["end_page"])
        if not (1 <= start <= end <= b["page_count"]):
            raise HTTPException(400, f"Chapter '{c['title']}' has invalid pages ({start}-{end}).")
        if c.get("id"):
            db.ex("UPDATE chapters SET ord=?, title=?, start_page=?, end_page=? WHERE id=? AND book_id=?",
                  (i, c["title"], start, end, c["id"], book_id))
            keep.append(int(c["id"]))
        else:
            keep.append(db.ex("INSERT INTO chapters(book_id, ord, title, start_page, end_page) VALUES(?,?,?,?,?)",
                              (book_id, i, c["title"], start, end)))
    marks = ",".join("?" * len(keep)) or "NULL"
    db.ex(f"DELETE FROM chapters WHERE book_id=? AND id NOT IN ({marks})", (book_id, *keep))
    return get_book(book_id)


@app.get("/api/books/{book_id}/export")
def export_book(book_id: int):
    b = _book(book_id)
    annots = db.q("SELECT * FROM annotations WHERE book_id=?", (book_id,))
    data = pdfs.export_annotated(db.BOOKS / b["filename"], annots)
    safe = re.sub(r"[^\w\- ]", "", b["title"]) or "book"
    return Response(data, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="{safe} (with answers).pdf"'})


# ---------- Annotations (your writing on the PDF) ----------

@app.get("/api/books/{book_id}/annotations")
def get_annotations(book_id: int, page: int):
    rows = db.q("SELECT * FROM annotations WHERE book_id=? AND page=?", (book_id, page))
    for r in rows:
        r["data"] = json.loads(r["data"])
    return rows


@app.post("/api/annotations")
def add_annotation(body: dict):
    aid = db.ex("INSERT INTO annotations(book_id, page, kind, x, y, data, updated_at) VALUES(?,?,?,?,?,?,?)",
                (body["book_id"], body["page"], body["kind"], body.get("x", 0), body.get("y", 0),
                 json.dumps(body["data"], ensure_ascii=False), db.now()))
    return {"id": aid}


@app.put("/api/annotations/{aid}")
def update_annotation(aid: int, body: dict):
    db.ex("UPDATE annotations SET x=?, y=?, data=?, updated_at=? WHERE id=?",
          (body.get("x", 0), body.get("y", 0), json.dumps(body["data"], ensure_ascii=False), db.now(), aid))
    return {"ok": True}


@app.delete("/api/annotations/{aid}")
def delete_annotation(aid: int):
    db.ex("DELETE FROM annotations WHERE id=?", (aid,))
    return {"ok": True}


@app.post("/api/books/{book_id}/check_page")
def check_page(book_id: int, body: dict):
    b = _book(book_id)
    page = int(body["page"])
    image = body["image"].split(",", 1)[-1]
    text = pdfs.page_text(db.BOOKS / b["filename"], page, page)
    result = ai.check_page(image, text)
    ts, date = db.now(), db.today()
    graded = [i for i in result["items"] if i["verdict"] != "unclear"]
    db.exmany("INSERT INTO answers(source, topic, correct, ts, date) VALUES(?,?,?,?,?)",
              [("page", i["topic"], 1 if i["verdict"] == "correct" else 0, ts, date) for i in graded])
    db.add_mistakes("page", [
        {"topic": i["topic"], "wrong": i["student_answer"], "correct": i["correction"], "explanation": i["explanation"],
         "context": f"{b['title']}, p. {page}, {i['exercise']}", "question": i["question"],
         "full_correct": i["corrected_sentence"], "book_id": book_id, "page": page}
        for i in graded if i["verdict"] in ("incorrect", "partly")])
    result["new_mistakes"] = sum(1 for i in graded if i["verdict"] in ("incorrect", "partly"))
    return result


# ---------- Reading time ----------

@app.post("/api/reading")
def log_reading(body: dict):
    seconds = max(0, min(int(body.get("seconds", 0)), 60))
    db.ex("INSERT INTO reading(book_id, page, seconds, ts, date) VALUES(?,?,?,?,?)",
          (body["book_id"], body["page"], seconds, db.now(), db.today()))
    db.ex("UPDATE books SET last_page=? WHERE id=?", (body["page"], body["book_id"]))
    return {"ok": True}


@app.post("/api/activity")
def log_activity(body: dict):
    seconds = max(0, min(int(body.get("seconds", 0)), 60))
    db.ex("INSERT INTO activity(kind, seconds, ts, date) VALUES(?,?,?,?)",
          (body.get("kind", "practice"), seconds, db.now(), db.today()))
    return {"ok": True}


# ---------- AI helpers in the reader ----------

@app.post("/api/lookup")
def lookup(body: dict):
    return ai.lookup(body["word"], body.get("sentence", ""))


@app.post("/api/explain")
def explain(body: dict):
    context = ""
    if body.get("book_id") and body.get("page"):
        b = _book(body["book_id"])
        context = pdfs.page_text(db.BOOKS / b["filename"], int(body["page"]), int(body["page"]))
    return {"text": ai.explain(body["text"], context)}


# ---------- Practice sets ----------

def _set_with_exercises(set_id):
    s = db.q1("SELECT * FROM exercise_sets WHERE id=?", (set_id,))
    if not s:
        raise HTTPException(404, "Practice set not found")
    s["exercises"] = db.q("SELECT * FROM exercises WHERE set_id=? ORDER BY ord", (set_id,))
    for e in s["exercises"]:
        e["options"] = json.loads(e["options"] or "[]")
    return s


@app.post("/api/chapters/{chapter_id}/exercises")
def generate_exercises(chapter_id: int, body: dict):
    c = _chapter(chapter_id)
    count = max(3, min(int(body.get("count", 15)), 40))
    items = ai.generate_exercises(c["title"], _chapter_text(c), count, body.get("focus", ""))
    n = db.q1("SELECT COUNT(*) AS n FROM exercise_sets WHERE chapter_id=?", (chapter_id,))["n"]
    set_id = db.ex("INSERT INTO exercise_sets(book_id, chapter_id, title, created_at) VALUES(?,?,?,?)",
                   (c["book_id"], chapter_id, f"{c['title']} - Set {n + 1}", db.now()))
    db.exmany("INSERT INTO exercises(set_id, ord, type, topic, instructions, prompt, options, answer, explanation) "
              "VALUES(?,?,?,?,?,?,?,?,?)",
              [(set_id, i, e["type"], e["topic"], e["instructions"], e["prompt"],
                json.dumps(e["options"], ensure_ascii=False), e["answer"], e["explanation"])
               for i, e in enumerate(items)])
    return _set_with_exercises(set_id)


@app.get("/api/exercise_sets")
def list_sets(book_id: int | None = None):
    sql = ("SELECT s.*, COUNT(e.id) AS total, SUM(e.correct IS NOT NULL) AS answered, "
           "COALESCE(SUM(e.correct),0) AS correct FROM exercise_sets s LEFT JOIN exercises e ON e.set_id=s.id ")
    args = ()
    if book_id:
        sql += "WHERE s.book_id=? "
        args = (book_id,)
    return db.q(sql + "GROUP BY s.id ORDER BY s.id DESC", args)


@app.get("/api/exercise_sets/{set_id}")
def get_set(set_id: int):
    return _set_with_exercises(set_id)


@app.delete("/api/exercise_sets/{set_id}")
def delete_set(set_id: int):
    db.ex("DELETE FROM exercise_sets WHERE id=?", (set_id,))
    return {"ok": True}


def _exercise_question(e):
    """The full task of a practice exercise (instruction, sentence, options) and its correct sentence."""
    options = e["options"] if isinstance(e["options"], list) else json.loads(e["options"] or "[]")
    task = "\n".join(p for p in (e["prompt"], " / ".join(options)) if p)
    question = f"{e['instructions']}\n\n{task}" if e["instructions"] else task
    answer = e["answer"].split("|")[0].strip()
    full = e["prompt"].replace("___", answer, 1) if "___" in e["prompt"] else ""
    return {"question": question, "full_correct": full}


def _norm(s):
    return re.sub(r"[\s.,!?;:\"'„“”]+", " ", (s or "").lower()).strip()


@app.post("/api/exercise_sets/{set_id}/check")
def check_set(set_id: int, body: dict):
    s = _set_with_exercises(set_id)
    answers = {int(k): v for k, v in body["answers"].items() if str(v).strip()}
    results, to_ai = {}, []
    for e in s["exercises"]:
        if e["id"] not in answers or e["correct"] is not None and e["user_answer"] == answers[e["id"]]:
            continue
        user = answers[e["id"]]
        accepted = [_norm(a) for a in e["answer"].split("|")]
        if _norm(user) in accepted:
            results[e["id"]] = {"correct": True, "feedback": "Richtig!"}
        elif e["type"] == "multiple_choice":
            results[e["id"]] = {"correct": False, "feedback": f"The answer is: {e['answer']}. {e['explanation']}"}
        else:
            to_ai.append({"id": e["id"], "type": e["type"], "instructions": e["instructions"],
                          "prompt": e["prompt"], "expected": e["answer"], "user": user})
    if to_ai:
        results.update(ai.grade_answers(to_ai))
    ts, date = db.now(), db.today()
    by_id = {e["id"]: e for e in s["exercises"]}
    for eid, r in results.items():
        db.ex("UPDATE exercises SET user_answer=?, correct=?, feedback=?, answered_at=? WHERE id=?",
              (answers[eid], 1 if r["correct"] else 0, r["feedback"], ts, eid))
        db.ex("INSERT INTO answers(source, topic, correct, ts, date) VALUES(?,?,?,?,?)",
              ("practice", by_id[eid]["topic"], 1 if r["correct"] else 0, ts, date))
    db.add_mistakes("practice", [
        {**_exercise_question(by_id[eid]), "topic": by_id[eid]["topic"], "wrong": answers[eid],
         "correct": by_id[eid]["answer"].split("|")[0].strip(), "explanation": r["feedback"],
         "context": s["title"]}
        for eid, r in results.items() if not r["correct"]])
    out = _set_with_exercises(set_id)
    out["new_mistakes"] = sum(1 for r in results.values() if not r["correct"])
    return out


@app.post("/api/exercise_sets/{set_id}/reset")
def reset_set(set_id: int, wrong_only: bool = False):
    db.ex("UPDATE exercises SET user_answer=NULL, correct=NULL, feedback=NULL, answered_at=NULL WHERE set_id=?"
          + (" AND correct=0" if wrong_only else ""), (set_id,))
    return _set_with_exercises(set_id)


# ---------- Flashcards ----------

def _card_query(book_id=None, chapter_id=None, search=None):
    sql, args = "SELECT * FROM cards WHERE 1=1", []
    if chapter_id:
        sql += " AND chapter_id=?"
        args.append(chapter_id)
    elif book_id:
        sql += " AND book_id=?"
        args.append(book_id)
    if search:
        sql += " AND (front LIKE ? OR back LIKE ? OR extra LIKE ?)"
        args += [f"%{search}%"] * 3
    return db.q(sql + " ORDER BY id DESC", args)


@app.get("/api/cards")
def list_cards(book_id: int | None = None, chapter_id: int | None = None, q: str | None = None):
    return _card_query(book_id, chapter_id, q)


@app.post("/api/cards")
def add_card(body: dict):
    cid = db.ex("INSERT INTO cards(book_id, chapter_id, type, front, back, extra, tags, created_at) "
                "VALUES(?,?,?,?,?,?,?,?)",
                (body.get("book_id"), body.get("chapter_id"), body.get("type", "vocab"), body["front"],
                 body["back"], body.get("extra", ""), json.dumps(body.get("tags", [])), db.now()))
    return db.q1("SELECT * FROM cards WHERE id=?", (cid,))


@app.put("/api/cards/{card_id}")
def update_card(card_id: int, body: dict):
    db.ex("UPDATE cards SET front=?, back=?, extra=?, type=? WHERE id=?",
          (body["front"], body["back"], body.get("extra", ""), body.get("type", "vocab"), card_id))
    return db.q1("SELECT * FROM cards WHERE id=?", (card_id,))


@app.delete("/api/cards/{card_id}")
def delete_card(card_id: int):
    db.ex("DELETE FROM cards WHERE id=?", (card_id,))
    return {"ok": True}


@app.post("/api/chapters/{chapter_id}/cards")
def generate_cards(chapter_id: int, body: dict):
    c = _chapter(chapter_id)
    count = max(5, min(int(body.get("count", 25)), 60))
    existing = [r["front"] for r in db.q("SELECT front FROM cards WHERE book_id=?", (c["book_id"],))]
    cards = ai.generate_cards(c["title"], _chapter_text(c), count, existing, body.get("focus", ""))
    now = db.now()
    db.exmany("INSERT INTO cards(book_id, chapter_id, type, front, back, extra, tags, created_at) "
              "VALUES(?,?,?,?,?,?,?,?)",
              [(c["book_id"], chapter_id, k["type"], k["front"], k["back"], k["extra"],
                json.dumps(k["tags"], ensure_ascii=False), now) for k in cards])
    return {"added": len(cards)}


@app.get("/api/review/queue")
def review_queue(chapter_id: int | None = None, book_id: int | None = None, extra_new: int = 0, ahead: bool = False):
    """Cards to review now. ahead=True returns every card in scope for practice that doesn't change the schedule."""
    scope, args = "", []
    if chapter_id:
        scope, args = " AND chapter_id=?", [chapter_id]
    elif book_id:
        scope, args = " AND book_id=?", [book_id]
    now = db.now()
    counts = planner.card_counts()
    if ahead:
        cards = db.q("SELECT * FROM cards WHERE 1=1" + scope + " ORDER BY due IS NULL, due LIMIT 300", args)
    else:
        due = db.q("SELECT * FROM cards WHERE due IS NOT NULL AND due <= ?" + scope + " ORDER BY due LIMIT 300",
                   [now, *args])
        limit = counts["new_available"] + max(0, min(extra_new, 200))
        new = db.q("SELECT * FROM cards WHERE due IS NULL" + scope + " ORDER BY id LIMIT ?", [*args, limit])
        cards = due + new
    for c in cards:
        c["previews"] = srs.preview(c)
    summary = db.q1("SELECT COUNT(*) AS total, COALESCE(SUM(due IS NULL), 0) AS new, "
                    "COALESCE(SUM(due > ?), 0) AS later, MIN(CASE WHEN due > ? THEN due END) AS next_due "
                    "FROM cards WHERE 1=1" + scope, [now, now, *args])
    return {"cards": cards, "counts": counts, "scope": summary, "ahead": ahead}


@app.post("/api/review/{card_id}")
def review_card(card_id: int, body: dict):
    card = db.q1("SELECT * FROM cards WHERE id=?", (card_id,))
    if not card:
        raise HTTPException(404, "Card not found")
    grade = int(body["grade"])
    upd = srs.schedule(card, grade)
    prev = {k: card[k] for k in ("ease", "interval", "reps", "lapses", "due")}
    db.ex("UPDATE cards SET ease=?, interval=?, reps=?, lapses=?, due=? WHERE id=?",
          (upd["ease"], upd["interval"], upd["reps"], upd["lapses"], upd["due"], card_id))
    rid = db.ex("INSERT INTO reviews(card_id, grade, seconds, was_new, ts, date) VALUES(?,?,?,?,?,?)",
                (card_id, grade, max(0, min(int(body.get("seconds", 0)), 180)), 1 if card["due"] is None else 0,
                 db.now(), db.today()))
    card = db.q1("SELECT * FROM cards WHERE id=?", (card_id,))
    card["previews"] = srs.preview(card)
    return {"card": card, "counts": planner.card_counts(), "undo": {"card_id": card_id, "review_id": rid, "prev": prev}}


@app.post("/api/review-undo")
def review_undo(body: dict):
    """Take back the last grade: restore the card's schedule and remove the review from the log."""
    card_id, rid, prev = int(body["card_id"]), int(body["review_id"]), body["prev"]
    if not db.q1("SELECT id FROM reviews WHERE id=? AND card_id=?", (rid, card_id)):
        raise HTTPException(404, "That review can't be undone any more")
    db.ex("UPDATE cards SET ease=?, interval=?, reps=?, lapses=?, due=? WHERE id=?",
          (prev["ease"], prev["interval"], prev["reps"], prev["lapses"], prev["due"], card_id))
    db.ex("DELETE FROM reviews WHERE id=?", (rid,))
    card = db.q1("SELECT * FROM cards WHERE id=?", (card_id,))
    card["previews"] = srs.preview(card)
    return {"card": card, "counts": planner.card_counts()}


@app.get("/api/review/stats")
def review_stats():
    return planner.card_stats()


def _names():
    names = {("b", b["id"]): b["title"] for b in db.q("SELECT id, title FROM books")}
    names.update({("c", c["id"]): c["title"] for c in db.q("SELECT id, title FROM chapters")})
    return names


@app.get("/api/anki/export")
def anki_export(book_id: int | None = None, chapter_id: int | None = None):
    cards = _card_query(book_id, chapter_id)
    if not cards:
        raise HTTPException(400, "No cards to export.")
    return Response(anki.build_apkg(cards, _names()), media_type="application/octet-stream",
                    headers={"Content-Disposition": 'attachment; filename="German.apkg"'})


@app.post("/api/anki/push")
def anki_push(body: dict):
    cards = _card_query(body.get("book_id"), body.get("chapter_id"))
    if not cards:
        raise HTTPException(400, "No cards to send.")
    try:
        return anki.push(cards, _names())
    except RuntimeError as e:
        raise HTTPException(400, str(e))


# ---------- Listening (audio episodes & pronunciation) ----------

def _media(mid):
    m = db.q1("SELECT * FROM media WHERE id=?", (mid,))
    if not m:
        raise HTTPException(404, "Audio not found")
    m["script"] = json.loads(m["script"]) if m["script"] else None
    return m


@app.get("/api/media")
def list_media(chapter_id: int | None = None):
    sql = ("SELECT m.id, m.book_id, m.chapter_id, m.title, m.source, m.seconds, m.listens, m.created_at, "
           "c.title AS chapter FROM media m LEFT JOIN chapters c ON c.id = m.chapter_id")
    rows = db.q(sql + (" WHERE m.chapter_id=?" if chapter_id else "") + " ORDER BY m.id DESC",
                (chapter_id,) if chapter_id else ())
    return rows


@app.get("/api/media/{mid}")
def get_media(mid: int):
    return _media(mid)


@app.get("/api/media/{mid}/file")
def media_file(mid: int):
    m = _media(mid)
    return FileResponse(db.MEDIA / m["filename"], media_type=m["mime"])


@app.put("/api/media/{mid}")
def rename_media(mid: int, body: dict):
    db.ex("UPDATE media SET title=? WHERE id=?", (body["title"], mid))
    return _media(mid)


@app.delete("/api/media/{mid}")
def delete_media(mid: int):
    m = _media(mid)
    db.ex("DELETE FROM media WHERE id=?", (mid,))
    (db.MEDIA / m["filename"]).unlink(missing_ok=True)
    return {"ok": True}


@app.post("/api/media/{mid}/listened")
def media_listened(mid: int):
    db.ex("UPDATE media SET listens = listens + 1 WHERE id=?", (mid,))
    return {"ok": True}


def _save_media(chapter_id, title, source, data, ext, mime, seconds=None, script=None):
    c = _chapter(chapter_id) if chapter_id else None
    name = f"{uuid.uuid4().hex}{ext}"
    (db.MEDIA / name).write_bytes(data)
    mid = db.ex("INSERT INTO media(book_id, chapter_id, title, source, filename, mime, seconds, script, created_at) "
                "VALUES(?,?,?,?,?,?,?,?,?)",
                (c["book_id"] if c else None, chapter_id, title, source, name, mime, seconds,
                 json.dumps(script, ensure_ascii=False) if script else None, db.now()))
    return _media(mid)


@app.post("/api/chapters/{chapter_id}/episode")
def make_episode(chapter_id: int, body: dict):
    c = _chapter(chapter_id)
    style = body.get("style", "dialogue")
    minutes = max(1, min(int(body.get("minutes", 3)), 10))
    script = ai.write_episode(c["title"], _chapter_text(c), minutes, style, body.get("focus", ""))
    s = db.get_settings()
    names = [sp["name"] for sp in script["speakers"]][: 1 if style == "story" else 2]
    voices = dict(zip(names, [s["voice_a"], s["voice_b"]]))
    turns = [t for t in script["turns"] if t["speaker"] in voices and t["text"].strip()]
    if not turns:
        raise ai.AIError("The episode script came back empty. Please try again.")
    audio, seconds = tts.synthesize(turns, voices)
    script["turns"] = turns
    return _save_media(chapter_id, script["title"], style, audio, ".wav", "audio/wav", seconds, script)


@app.post("/api/speak")
def speak(body: dict):
    text = body["text"].strip()[:600]
    if not text:
        raise HTTPException(400, "Nothing to read.")
    return FileResponse(tts.speak(text), media_type="audio/wav")


# ---------- Mistake Book ----------

@app.get("/api/mistakes")
def list_mistakes(status: str = "open", topic: str | None = None):
    sql, args = "SELECT * FROM mistakes WHERE status=?", [status]
    if topic is not None:
        sql += " AND topic=?"
        args.append(topic)
    mistakelink.auto_learn()
    mistakes = db.q(sql + " ORDER BY times DESC, last_seen DESC", args)
    for m in mistakes:
        m["skills"] = json.loads(m["skills"]) if m["skills"] else None
        m["drill_days"] = mistakelink.progress({**m, "skills": json.dumps(m["skills"]) if m["skills"] else None})
    topics = db.q("SELECT topic, COUNT(*) AS n, SUM(times) AS times FROM mistakes WHERE status=? "
                  "GROUP BY topic ORDER BY n DESC, topic", (status,))
    counts = {r["status"]: r["n"] for r in db.q("SELECT status, COUNT(*) AS n FROM mistakes GROUP BY status")}
    pending = db.q1("SELECT COUNT(*) AS n FROM mistakes WHERE skills IS NULL")["n"]
    return {"mistakes": mistakes, "topics": topics, "counts": counts, "unlinked": pending,
            "learned_days": mistakelink.LEARNED_DAYS, "linked_open": len(mistakelink.keys_for())}


@app.post("/api/mistakes/link")
def mistakes_link():
    return mistakelink.classify_pending()


@app.post("/api/mistakes/skills")
def mistakes_skills(body: dict):
    ids = [int(i) for i in body.get("ids") or []]
    return {"keys": mistakelink.keys_for(ids or None)}


@app.put("/api/mistakes")
def update_mistakes(body: dict):
    ids = [int(i) for i in body["ids"]]
    marks = ",".join("?" * len(ids)) or "NULL"
    if body.get("status") in ("open", "learned"):
        db.ex(f"UPDATE mistakes SET status=? WHERE id IN ({marks})", (body["status"], *ids))
    elif body.get("delete"):
        db.ex(f"DELETE FROM mistakes WHERE id IN ({marks})", ids)
    return {"ok": True}


def _mistakes(ids):
    marks = ",".join("?" * len(ids)) or "NULL"
    return db.q(f"SELECT * FROM mistakes WHERE id IN ({marks})", ids)


def _recover_questions(rows):
    """Fills in the full question for mistakes saved before questions were stored. Practice ones come from
    the saved exercise; textbook-page ones are looked up on the page by Claude (one call per page)."""
    missing = [m for m in rows if not m["question"]]
    pages = {}
    for m in missing:
        if m["source"] == "practice":
            e = db.q1("SELECT * FROM exercises WHERE prompt=? AND user_answer=? ORDER BY id DESC LIMIT 1",
                      (m["context"], m["wrong"])) or db.q1("SELECT * FROM exercises WHERE prompt=? LIMIT 1",
                                                           (m["context"],))
            if e:
                q = _exercise_question(e)
                db.ex("UPDATE mistakes SET question=?, full_correct=? WHERE id=?",
                      (q["question"], q["full_correct"], m["id"]))
        elif m["source"] == "page":
            book_id, page = m["book_id"], m["page"]
            ref = re.match(r"^(.*), p\. (\d+), (.*)$", m["context"] or "")
            if not book_id and ref:
                b = db.q1("SELECT id FROM books WHERE title=?", (ref.group(1),))
                book_id, page = (b["id"] if b else None), int(ref.group(2))
            if book_id and page:
                pages.setdefault((book_id, page), []).append(
                    {"id": m["id"], "exercise": ref.group(3) if ref else "", "wrong": m["wrong"], "correct": m["correct"]})
    for (book_id, page), items in pages.items():
        b = db.q1("SELECT * FROM books WHERE id=?", (book_id,))
        if not b:
            continue
        found = ai.recover_questions(pdfs.page_text(db.BOOKS / b["filename"], page, page), items)
        for mid, r in found.items():
            db.ex("UPDATE mistakes SET question=?, full_correct=?, book_id=?, page=? WHERE id=?",
                  (r["question"], r["corrected_sentence"], book_id, page, mid))
    for m in _mistakes([m["id"] for m in missing]):  # rebuild cards made before the question was known
        if m["card_id"] and m["question"]:
            db.ex("UPDATE cards SET front=?, back=?, extra=? WHERE id=?", (*_mistake_card(m), m["card_id"]))
    return len(missing)


def _mistake_card(m):
    """Front: the real task to answer. Back: the answer and the corrected sentence. Extra: what went wrong."""
    # Instruction and sentence go on separate lines (older questions joined them with a dash).
    front = re.sub(r"\s+[–—]\s+", "\n\n", m["question"], count=1) if m["question"] else f"Correct this:\n{m['wrong']}"
    back = m["correct"] + (f"\n\n{m['full_correct']}" if m["full_correct"] else "")
    extra = f"You once wrote: {m['wrong']}" + (f"\n{m['explanation']}" if m["explanation"] else "")
    return front, back, extra


@app.post("/api/mistakes/recover")
def mistakes_recover(body: dict | None = None):
    ids = (body or {}).get("ids")
    rows = _mistakes([int(i) for i in ids]) if ids else db.q("SELECT * FROM mistakes WHERE COALESCE(question,'')=''")
    return {"recovered": _recover_questions(rows)}


@app.post("/api/mistakes/cards")
def mistakes_to_cards(body: dict):
    ids = [int(i) for i in body["ids"]]
    _recover_questions(_mistakes(ids))
    rows = [m for m in _mistakes(ids) if not m["card_id"]]
    for m in rows:
        cid = db.ex("INSERT INTO cards(book_id, type, front, back, extra, tags, created_at) VALUES(?,'fix',?,?,?,?,?)",
                    (m["book_id"], *_mistake_card(m), json.dumps([m["topic"], "mistake-book"], ensure_ascii=False),
                     db.now()))
        db.ex("UPDATE mistakes SET card_id=? WHERE id=?", (cid, m["id"]))
    return {"added": len(rows), "skipped": len(ids) - len(rows)}


@app.post("/api/mistakes/drill")
def mistakes_drill(body: dict):
    ids = [int(i) for i in body["ids"]]
    _recover_questions(_mistakes(ids))
    rows = [{k: m[k] for k in ("topic", "question", "wrong", "correct", "full_correct", "explanation")}
            for m in _mistakes(ids)]
    if not rows:
        raise HTTPException(400, "Pick some mistakes first.")
    count = max(5, min(int(body.get("count", 12)), 30))
    items = ai.drill_mistakes(rows, count)
    topics = sorted({r["topic"] for r in rows if r["topic"]})
    title = "Mistake drill: " + (", ".join(topics[:3]) + (" ..." if len(topics) > 3 else "") if topics else "mixed")
    set_id = db.ex("INSERT INTO exercise_sets(book_id, chapter_id, title, created_at) VALUES(NULL, NULL, ?, ?)",
                   (title, db.now()))
    db.exmany("INSERT INTO exercises(set_id, ord, type, topic, instructions, prompt, options, answer, explanation) "
              "VALUES(?,?,?,?,?,?,?,?,?)",
              [(set_id, i, e["type"], e["topic"], e["instructions"], e["prompt"],
                json.dumps(e["options"], ensure_ascii=False), e["answer"], e["explanation"])
               for i, e in enumerate(items)])
    return {"set_id": set_id, "added": len(items)}


# ---------- Gemini Notebook bridge ----------

@app.get("/api/chapters/{chapter_id}/pdf")
def chapter_pdf(chapter_id: int):
    c = _chapter(chapter_id)
    b = _book(c["book_id"])
    data = pdfs.chapter_pdf(db.BOOKS / b["filename"], c["start_page"], c["end_page"])
    safe = re.sub(r"[^\w\- ]", "", f"{b['title']} - {c['title']}") or "chapter"
    return Response(data, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="{safe}.pdf"'})


def _parse_table(text):
    """Cards straight from a 2+ column table (CSV, TSV, 'a | b' or Markdown), when it's clearly one."""
    rows = []
    for line in text.strip().splitlines():
        line = line.strip().strip("|")
        if not line or set(line) <= set("-|: "):
            continue
        for sep in ("\t", "|", ";", ","):
            parts = [p.strip().strip('"') for p in line.split(sep)]
            if len(parts) >= 2 and parts[0] and parts[1]:
                rows.append(parts)
                break
        else:
            return None
    if len(rows) < 3:
        return None
    if rows[0][0].lower() in ("german", "deutsch", "front", "term", "word", "wort"):
        rows = rows[1:]
    return [{"type": "vocab", "front": r[0], "back": r[1], "extra": " · ".join(r[2:]), "tags": []} for r in rows]


@app.post("/api/import")
def import_material(chapter_id: int = Form(...), kind: str = Form(...), text: str = Form(""),
                    title: str = Form(""), file: UploadFile | None = File(None)):
    c = _chapter(chapter_id)
    if kind == "audio":
        if not file:
            raise HTTPException(400, "Choose an audio file.")
        ext = Path(file.filename).suffix.lower()
        if ext not in AUDIO_TYPES:
            raise HTTPException(400, "That audio format isn't supported. Use MP3, M4A, WAV, OGG or WebM.")
        m = _save_media(chapter_id, title.strip() or Path(file.filename).stem, "imported", file.file.read(),
                        ext, AUDIO_TYPES[ext])
        return {"kind": "audio", "media_id": m["id"], "added": 1}

    if file:
        raw = file.file.read()
        text = (pdfs.text_of_pdf(raw) if file.filename.lower().endswith(".pdf")
                else raw.decode("utf-8", errors="replace")) + "\n" + text
    text = text.strip()
    if not text:
        raise HTTPException(400, "Paste some text or choose a file first.")
    if len(text) > 120_000:
        raise HTTPException(400, "That's a lot of text. Import it in smaller pieces.")

    if kind == "cards":
        cards = _parse_table(text) or ai.convert_import("cards", text, c["title"])
        now = db.now()
        db.exmany("INSERT INTO cards(book_id, chapter_id, type, front, back, extra, tags, created_at) "
                  "VALUES(?,?,?,?,?,?,?,?)",
                  [(c["book_id"], chapter_id, k["type"], k["front"], k["back"], k["extra"],
                    json.dumps(k["tags"] + ["gemini-notebook"], ensure_ascii=False), now) for k in cards])
        return {"kind": "cards", "added": len(cards)}

    items = ai.convert_import("exercises", text, c["title"])
    set_id = db.ex("INSERT INTO exercise_sets(book_id, chapter_id, title, created_at) VALUES(?,?,?,?)",
                   (c["book_id"], chapter_id, title.strip() or f"{c['title']} - from Gemini Notebook", db.now()))
    db.exmany("INSERT INTO exercises(set_id, ord, type, topic, instructions, prompt, options, answer, explanation) "
              "VALUES(?,?,?,?,?,?,?,?,?)",
              [(set_id, i, e["type"], e["topic"], e["instructions"], e["prompt"],
                json.dumps(e["options"], ensure_ascii=False), e["answer"], e["explanation"])
               for i, e in enumerate(items)])
    return {"kind": "exercises", "added": len(items), "set_id": set_id}


# ---------- Coach, plans, stats ----------

# ---------- declension trainer ----------

@app.get("/api/decl/state")
def decl_state():
    return localize({**decl.progress(), "tables": decl.tables(), "triggers": decl.trigger_lists()})


@app.post("/api/decl/next")
def decl_next(body: dict):
    return localize(decl.next_question(body.get("focus"), body.get("cases"), body.get("recent"), body.get("keys")))


@app.post("/api/decl/answer")
def decl_answer(body: dict):
    result = decl.grade(body["question"], body.get("answer", ""), body.get("ms"))
    learned = mistakelink.auto_learn([p["key"] for p in body["question"]["parts"]])
    return localize({**result, "learned": learned,
                     "next": decl.next_question(body.get("focus"), body.get("cases"), body.get("recent"), body.get("keys"))})


@app.post("/api/decl/table")
def decl_table(body: dict):
    return decl.check_table(body["table"], body.get("answers", {}))


@app.get("/api/decl/journey")
def decl_journey():
    return localize(course.journey())


@app.get("/api/decl/stage/{stage_id}")
def decl_stage(stage_id: str):
    if stage_id not in course.STAGE:
        raise HTTPException(404, "Unknown planet")
    return localize(course.detail(stage_id))


@app.post("/api/decl/stage/{stage_id}/next")
def decl_stage_next(stage_id: str, body: dict):
    return localize(course.question(stage_id, body.get("mode", "drill"), body.get("recent")))


@app.post("/api/decl/stage/{stage_id}/answer")
def decl_stage_answer(stage_id: str, body: dict):
    result = decl.grade(body["question"], body.get("answer", ""), body.get("ms"))
    return localize({**result, "next": course.question(stage_id, body.get("mode", "drill"), body.get("recent"))})


@app.post("/api/decl/stage/{stage_id}/complete")
def decl_stage_complete(stage_id: str, body: dict):
    return localize(course.complete(stage_id, body["step"], body.get("score"), body.get("total")))


@app.post("/api/decl/stage/{stage_id}/cards")
def decl_stage_cards(stage_id: str):
    return course.add_cards(stage_id)


@app.post("/api/decl/stage/{stage_id}/reading")
def decl_stage_reading(stage_id: str, body: dict):
    brief = course.reading_brief(stage_id)
    for _ in range(2):  # one retry if the text came back without usable gaps
        r = ai.decl_reading(brief, (body.get("topic") or "").strip())
        segments = course.parse_reading(r["text"])
        if sum(1 for s in segments if "a" in s) >= 6:
            return localize({"title": r["title"], "segments": segments})
    raise ai.AIError("The text came back without gaps. Please try again.")


@app.post("/api/decl/record")
def decl_record(body: dict):
    family = body.get("family") if body.get("family") in decl.FAMILY_LABEL else "sent"
    return course.record(body.get("items", []), family)


@app.get("/api/decl/match")
def decl_match(kind: str = "all"):
    """A round of "Match the case": prepositions and verbs to sort into the case they take."""
    from .i18n import lang
    return localize({"cards": decl.match_round(kind, lang=lang())})


@app.post("/api/decl/sprint")
def decl_sprint(body: dict):
    return decl.save_sprint(int(body.get("score", 0)))


# ---------- verbs (same shape as the declension endpoints, so the page code is shared) ----------
@app.get("/api/verbs/state")
def verbs_state():
    return localize({**verbs.progress(), "tables": verbs.tables(), "triggers": []})


@app.post("/api/verbs/next")
def verbs_next(body: dict):
    return localize(verbs.next_question(body.get("focus"), body.get("cases"), body.get("recent"), body.get("keys")))


@app.post("/api/verbs/answer")
def verbs_answer(body: dict):
    result = verbs.grade(body["question"], body.get("answer", ""), body.get("ms"))
    learned = mistakelink.auto_learn([p["key"] for p in body["question"]["parts"]])
    return localize({**result, "learned": learned,
                     "next": verbs.next_question(body.get("focus"), body.get("cases"), body.get("recent"), body.get("keys"))})


@app.post("/api/verbs/table")
def verbs_table(body: dict):
    return verbs.check_table(body["table"], body.get("answers", {}))


@app.get("/api/verbs/journey")
def verbs_journey():
    return localize(VERBS_COURSE.journey())


@app.get("/api/verbs/stage/{stage_id}")
def verbs_stage(stage_id: str):
    if stage_id not in VERBS_COURSE.STAGE:
        raise HTTPException(404, "Unknown stage")
    return localize(VERBS_COURSE.detail(stage_id))


@app.post("/api/verbs/stage/{stage_id}/next")
def verbs_stage_next(stage_id: str, body: dict):
    return localize(VERBS_COURSE.question(stage_id, body.get("mode", "drill"), body.get("recent")))


@app.post("/api/verbs/stage/{stage_id}/answer")
def verbs_stage_answer(stage_id: str, body: dict):
    result = verbs.grade(body["question"], body.get("answer", ""), body.get("ms"))
    return localize({**result, "next": VERBS_COURSE.question(stage_id, body.get("mode", "drill"), body.get("recent"))})


@app.post("/api/verbs/stage/{stage_id}/complete")
def verbs_stage_complete(stage_id: str, body: dict):
    return localize(VERBS_COURSE.complete(stage_id, body["step"], body.get("score"), body.get("total")))


@app.post("/api/verbs/stage/{stage_id}/cards")
def verbs_stage_cards(stage_id: str):
    return VERBS_COURSE.add_cards(stage_id)


@app.post("/api/verbs/stage/{stage_id}/reading")
def verbs_stage_reading(stage_id: str, body: dict):
    brief = VERBS_COURSE.reading_brief(stage_id)
    for _ in range(2):  # one retry if the text came back without usable gaps
        r = ai.verb_reading(brief, (body.get("topic") or "").strip())
        segments = course.parse_reading(r["text"])
        if sum(1 for s in segments if "a" in s) >= 6:
            return localize({"title": r["title"], "segments": segments})
    raise ai.AIError("The text came back without gaps. Please try again.")


@app.post("/api/verbs/record")
def verbs_record(body: dict):
    family = body.get("family") if body.get("family") in verbs.FAMILY_LABEL else "vsent"
    return VERBS_COURSE.record(body.get("items", []), family)


@app.post("/api/verbs/sprint")
def verbs_sprint(body: dict):
    return verbs.save_sprint(int(body.get("score", 0)))


# ---------- writing desk ----------

@app.get("/api/writing")
def writing_home():
    return {"tasks": writing.tasks(), "history": writing.history()}


@app.get("/api/writing/{wid}")
def writing_get(wid: int):
    return writing.get(wid)


@app.post("/api/writing/check")
def writing_check(body: dict):
    return writing.grade(body)


@app.post("/api/writing/task")
def writing_new_task(body: dict):
    return ai.writing_task(body.get("level") or db.get_settings()["level"], (body.get("topic") or "").strip())


@app.delete("/api/writing/{wid}")
def writing_delete(wid: int):
    db.ex("DELETE FROM writings WHERE id=?", (wid,))
    return {"ok": True}


# ---------- costs and backups ----------

@app.get("/api/usage")
def usage_summary():
    return usage.summary()


@app.get("/api/backups")
def backups_list():
    return {"backups": backup.listing(), "folder": str(backup.folder())}


@app.post("/api/backups")
def backups_make():
    return {"made": backup.make("manual"), "backups": backup.listing()}


@app.post("/api/backups/restore")
def backups_restore(body: dict):
    return backup.restore(body.get("name"))


@app.get("/api/stats")
def stats():
    return {"today": planner.day_stats(db.today()), "week": planner.week(), "streak": planner.streak(),
            "cards": planner.card_counts(), "weak_topics": planner.weak_topics(),
            "calendar": planner.calendar(), "journey": localize(course.brief()), "verbs_journey": localize(VERBS_COURSE.brief())}


@app.get("/api/progress")
def progress():
    return planner.progress()


@app.get("/api/plan/today")
def plan_today():
    return planner.today_plan()


@app.post("/api/plan/generate")
def plan_generate(body: dict):
    minutes = int(body.get("minutes") or db.get_settings()["daily_minutes"])
    return planner.generate(minutes, body.get("note", ""))


@app.post("/api/plan/{plan_id}/blocks/{idx}")
def plan_block(plan_id: int, idx: int, body: dict):
    return planner.update_block(plan_id, idx, body["action"])


@app.get("/api/coach/messages")
def coach_messages():
    return db.q("SELECT * FROM coach_messages ORDER BY id DESC LIMIT 60")[::-1]


@app.post("/api/coach/chat")
def coach_chat(body: dict):
    history = [{"role": m["role"], "content": m["content"]}
               for m in db.q("SELECT * FROM coach_messages ORDER BY id DESC LIMIT 20")[::-1]]
    reply = ai.coach_reply(planner.build_context(), history, body["message"])
    db.ex("INSERT INTO coach_messages(role, content, ts) VALUES('user',?,?)", (body["message"], db.now()))
    db.ex("INSERT INTO coach_messages(role, content, ts) VALUES('assistant',?,?)", (reply, db.now()))
    return coach_messages()


@app.delete("/api/coach/messages")
def clear_coach():
    db.ex("DELETE FROM coach_messages")
    return {"ok": True}


@app.get("/api/resources")
def list_resources():
    return db.q("SELECT * FROM resources ORDER BY kind, title")


@app.post("/api/resources")
def add_resource(body: dict):
    db.ex("INSERT INTO resources(title, url, kind, notes) VALUES(?,?,?,?)",
          (body["title"], body.get("url", ""), body.get("kind", "other"), body.get("notes", "")))
    return list_resources()


@app.delete("/api/resources/{rid}")
def delete_resource(rid: int):
    db.ex("DELETE FROM resources WHERE id=?", (rid,))
    return list_resources()
