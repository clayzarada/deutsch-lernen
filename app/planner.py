"""Study statistics, the context the coach sees, and daily plans with live progress tracking."""
import datetime as dt
import json

from .i18n import localize
from . import ai, course, db, decl, verbs, writing
from .verbcourse import VERBS_COURSE

PAGE_READ_SECONDS = 20  # time on a page before it counts as read


def _pages_read(where, args):
    row = db.q1(f"SELECT COUNT(*) AS n FROM (SELECT book_id, page FROM reading WHERE {where} "
                f"GROUP BY book_id, page HAVING SUM(seconds) >= ?)", (*args, PAGE_READ_SECONDS))
    return row["n"]


def day_stats(date):
    reading = db.q1("SELECT COALESCE(SUM(seconds),0) AS s FROM reading WHERE date=?", (date,))["s"]
    ans = db.q1("SELECT COUNT(*) AS n, COALESCE(SUM(correct),0) AS c FROM answers WHERE date=?", (date,))
    rev = db.q1("SELECT COUNT(*) AS n, COALESCE(SUM(seconds),0) AS s FROM reviews WHERE date=?", (date,))
    act = {r["kind"]: r["s"] for r in db.q(
        "SELECT kind, SUM(seconds) AS s FROM activity WHERE date=? GROUP BY kind", (date,))}
    return {
        "date": date,
        "minutes": round((reading + rev["s"] + sum(act.values())) / 60),
        "reading_minutes": round(reading / 60),
        "practice_minutes": round(act.get("practice", 0) / 60),
        "listening_minutes": round(act.get("listening", 0) / 60),
        "pages_read": _pages_read("date=?", (date,)),
        "questions": ans["n"],
        "accuracy": round(100 * ans["c"] / ans["n"]) if ans["n"] else None,
        "cards_reviewed": rev["n"],
        "flashcard_minutes": round(rev["s"] / 60),
    }


def week():
    return [day_stats((db.study_date() - dt.timedelta(days=i)).isoformat()) for i in range(6, -1, -1)]


def streak():
    """Days in a row with any studying. Today not done yet doesn't break the streak."""
    active = {r["date"] for r in db.q(
        "SELECT date FROM reading UNION SELECT date FROM reviews UNION SELECT date FROM answers "
        "UNION SELECT date FROM activity")}
    day = db.study_date()
    today_done = day.isoformat() in active
    if not today_done:
        day -= dt.timedelta(days=1)
    n = 0
    while day.isoformat() in active:
        n += 1
        day -= dt.timedelta(days=1)
    return {"days": n, "today_done": today_done}


def _seconds_by_date(since):
    rows = db.q("SELECT date, SUM(s) AS s FROM (SELECT date, seconds AS s FROM reading WHERE date>=? UNION ALL "
                "SELECT date, seconds FROM reviews WHERE date>=? UNION ALL SELECT date, seconds FROM activity WHERE date>=?) "
                "GROUP BY date", (since, since, since))
    return {r["date"]: r["s"] or 0 for r in rows}


def calendar(days=84):
    """Minutes studied on each of the last `days` study days, oldest first."""
    start = db.study_date() - dt.timedelta(days=days - 1)
    secs = _seconds_by_date(start.isoformat())
    answered = {r["date"] for r in db.q("SELECT DISTINCT date FROM answers WHERE date>=?", (start.isoformat(),))}
    out = []
    for i in range(days):
        d = (start + dt.timedelta(days=i)).isoformat()
        out.append({"date": d, "minutes": round(secs.get(d, 0) / 60), "active": d in secs or d in answered})
    return out


def progress(weeks=8):
    """Week-by-week totals (Monday to Sunday), oldest first, for the progress charts."""
    today = db.study_date()
    this_monday = today - dt.timedelta(days=today.weekday())
    start = this_monday - dt.timedelta(weeks=weeks - 1)
    since = start.isoformat()
    secs = _seconds_by_date(since)
    ans = {r["date"]: r for r in db.q("SELECT date, COUNT(*) AS n, SUM(correct) AS c FROM answers WHERE date>=? GROUP BY date", (since,))}
    rev = {r["date"]: r["n"] for r in db.q("SELECT date, COUNT(*) AS n FROM reviews WHERE date>=? GROUP BY date", (since,))}
    out = []
    for w in range(weeks):
        monday = start + dt.timedelta(weeks=w)
        days = [(monday + dt.timedelta(days=i)).isoformat() for i in range(7)]
        n = sum(ans[d]["n"] for d in days if d in ans)
        c = sum(ans[d]["c"] or 0 for d in days if d in ans)
        out.append({"start": monday.isoformat(), "minutes": round(sum(secs.get(d, 0) for d in days) / 60),
                    "questions": n, "accuracy": round(100 * c / n) if n else None,
                    "cards": sum(rev.get(d, 0) for d in days),
                    "days": sum(1 for d in days if d in secs or d in ans)})
    return {"weeks": out, "streak": streak(), "journey": localize(course.brief())}


def card_stats(days=14):
    """Upcoming reviews per study day, recent retention, and how the deck breaks down."""
    shift = f"-{db.DAY_START_HOUR} hours"
    today = db.study_date()
    by_day = {r["d"]: r["n"] for r in db.q("SELECT date(due, ?) AS d, COUNT(*) AS n FROM cards WHERE due IS NOT NULL GROUP BY d", (shift,))}
    overdue = sum(n for d, n in by_day.items() if d < today.isoformat())
    forecast = []
    for i in range(days):
        d = (today + dt.timedelta(days=i)).isoformat()
        forecast.append({"date": d, "due": by_day.get(d, 0) + (overdue if i == 0 else 0)})
    since = (today - dt.timedelta(days=30)).isoformat()
    r = db.q1("SELECT COUNT(*) AS n, COALESCE(SUM(grade > 1), 0) AS ok FROM reviews WHERE was_new=0 AND date>=?", (since,))
    deck = db.q1("SELECT COUNT(*) AS total, COALESCE(SUM(due IS NULL), 0) AS new, "
                 "COALESCE(SUM(due IS NOT NULL AND interval < 21), 0) AS learning, COALESCE(SUM(interval >= 21), 0) AS mature, "
                 f"COALESCE(SUM(lapses >= {TRICKY_LAPSES}), 0) AS tricky FROM cards")
    return {"forecast": forecast, "retention": round(100 * r["ok"] / r["n"]) if r["n"] >= 5 else None,
            "retention_reviews": r["n"], "deck": deck, "tricky_lapses": TRICKY_LAPSES}


TRICKY_LAPSES = 4  # a card missed this often probably needs rewording, not more repetition


def pages_read_by_book():
    rows = db.q("SELECT book_id, COUNT(*) AS n FROM (SELECT book_id, page FROM reading GROUP BY book_id, page "
                "HAVING SUM(seconds) >= ?) GROUP BY book_id", (PAGE_READ_SECONDS,))
    return {r["book_id"]: r["n"] for r in rows}


def card_counts():
    s = db.get_settings()
    due = db.q1("SELECT COUNT(*) AS n FROM cards WHERE due IS NOT NULL AND due <= ?", (db.now(),))["n"]
    new_total = db.q1("SELECT COUNT(*) AS n FROM cards WHERE due IS NULL")["n"]
    new_today = db.q1("SELECT COUNT(*) AS n FROM reviews WHERE date=? AND was_new=1", (db.today(),))["n"]
    new_avail = max(0, min(new_total, int(s["new_cards_per_day"]) - new_today))
    total = db.q1("SELECT COUNT(*) AS n FROM cards")["n"]
    return {"due": due, "new_available": new_avail, "new_total": new_total, "total": total}


def weak_topics(days=30):
    since = (db.study_date() - dt.timedelta(days=days)).isoformat()
    rows = db.q("SELECT topic, COUNT(*) AS n, SUM(correct) AS c FROM answers WHERE date>=? AND topic<>'' "
                "GROUP BY topic HAVING n>=3", (since,))
    for r in rows:
        r["accuracy"] = round(100 * r["c"] / r["n"])
    return sorted(rows, key=lambda r: r["accuracy"])[:10]


def book_progress():
    out = []
    for b in db.q("SELECT * FROM books ORDER BY id"):
        read_pages = {r["page"] for r in db.q(
            "SELECT page FROM reading WHERE book_id=? GROUP BY page HAVING SUM(seconds)>=?",
            (b["id"], PAGE_READ_SECONDS))}
        chapters = []
        for c in db.q("SELECT * FROM chapters WHERE book_id=? ORDER BY ord", (b["id"],)):
            span = range(c["start_page"], c["end_page"] + 1)
            ex = db.q1("SELECT COUNT(e.id) AS n, COALESCE(SUM(e.correct),0) AS c FROM exercises e "
                       "JOIN exercise_sets s ON s.id=e.set_id WHERE s.chapter_id=? AND e.correct IS NOT NULL",
                       (c["id"],))
            chapters.append({
                "chapter_id": c["id"], "title": c["title"], "pages": f"{c['start_page']}-{c['end_page']}",
                "pages_read": sum(1 for p in span if p in read_pages), "page_count": len(span),
                "practice_answered": ex["n"],
                "practice_accuracy": round(100 * ex["c"] / ex["n"]) if ex["n"] else None,
                "cards": db.q1("SELECT COUNT(*) AS n FROM cards WHERE chapter_id=?", (c["id"],))["n"],
            })
        out.append({"book_id": b["id"], "title": b["title"], "page_count": b["page_count"],
                    "last_page": b["last_page"], "pages_read": len(read_pages), "chapters": chapters})
    return out


def build_context():
    s = db.get_settings()
    recent_plans = []
    for p in db.q("SELECT * FROM plans ORDER BY id DESC LIMIT 5"):
        data = json.loads(p["data"])
        recent_plans.append({"date": p["date"], "blocks": [
            {"kind": bl["kind"], "title": bl["title"], "status": bl.get("status", "todo")} for bl in data["blocks"]]})
    return {
        "today": db.study_date().strftime("%A %Y-%m-%d"),
        "learner": {k: s[k] for k in ("level", "native_language", "daily_minutes", "goal", "exam_date")},
        "coach_notes": s["coach_notes"],
        "last_7_days": week(),
        "streak_days": streak()["days"],
        "flashcards": card_counts(),
        "weak_topics": weak_topics(),
        "books": book_progress(),
        "resources": db.q("SELECT title, url, kind, notes FROM resources"),
        "mistake_book": {
            "open_by_topic": db.q("SELECT topic, COUNT(*) AS mistakes, SUM(times) AS times FROM mistakes "
                                  "WHERE status='open' GROUP BY topic ORDER BY times DESC LIMIT 10"),
            "recent_examples": db.q("SELECT topic, wrong, correct FROM mistakes WHERE status='open' "
                                    "ORDER BY last_seen DESC LIMIT 8"),
            "how_to_use": "The learner can drill selected mistakes or turn them into flashcards on the Mistakes page.",
        },
        "declension_trainer": decl.coach_summary(),
        "declension_course": course.coach_summary(),
        "verb_trainer": verbs.coach_summary(),
        "verb_course": VERBS_COURSE.coach_summary(),
        "writing_desk": writing.recent_for_coach(),
        "listening_library": db.q(
            "SELECT m.id AS media_id, m.title, m.source, c.title AS chapter, ROUND(m.seconds / 60.0, 1) AS minutes, "
            "m.listens FROM media m LEFT JOIN chapters c ON c.id = m.chapter_id ORDER BY m.id DESC LIMIT 40"),
        "recent_plans": recent_plans,
    }


def _block_progress(bl):
    if not bl.get("started_at"):
        return None
    since = bl["started_at"]
    until = bl.get("done_at") or db.now()
    ans = db.q1("SELECT COUNT(*) AS n, COALESCE(SUM(correct),0) AS c FROM answers WHERE ts>=? AND ts<=?",
                (since, until))
    return {
        "minutes": round((dt.datetime.fromisoformat(until) - dt.datetime.fromisoformat(since)).total_seconds() / 60),
        "pages": _pages_read("ts>=? AND ts<=?", (since, until)),
        "questions": ans["n"],
        "correct": ans["c"],
        "cards": db.q1("SELECT COUNT(*) AS n FROM reviews WHERE ts>=? AND ts<=?", (since, until))["n"],
    }


TARGETS = (("target_pages", "pages"), ("target_questions", "questions"), ("target_cards", "cards"))


def _targets_met(bl, prog):
    """True when a started block has real targets (pages, questions or cards, not just minutes) and all are met."""
    goals = [(bl.get(t) or 0, prog.get(p, 0)) for t, p in TARGETS if bl.get(t)]
    return bool(goals) and all(have >= want for want, have in goals)


def _with_progress(plan):
    data = json.loads(plan["data"])
    finished = False
    for bl in data["blocks"]:
        bl["progress"] = _block_progress(bl)
        # A block finishes itself once its targets are reached, so the plan doesn't fill up with "in progress".
        if bl.get("status") == "active" and bl["progress"] and _targets_met(bl, bl["progress"]):
            bl.update(status="done", done_at=db.now(), auto_done=True)
            finished = True
    if finished:
        stored = {k: v for k, v in data.items()}
        stored["blocks"] = [{k: v for k, v in b.items() if k != "progress"} for b in data["blocks"]]
        db.ex("UPDATE plans SET data=? WHERE id=?", (json.dumps(stored, ensure_ascii=False), plan["id"]))
    return {"id": plan["id"], "date": plan["date"], "created_at": plan["created_at"], **data}


def today_plan():
    p = db.q1("SELECT * FROM plans WHERE date=? ORDER BY id DESC LIMIT 1", (db.today(),))
    return _with_progress(p) if p else None


def generate(minutes, note):
    result = ai.make_plan(build_context(), minutes, note)
    for bl in result["blocks"]:
        bl.update(status="todo", started_at=None, done_at=None)
    if result.get("learner_profile", "").strip():
        db.set_setting("coach_notes", result["learner_profile"].strip())
    data = {"summary": result["summary"], "blocks": result["blocks"], "minutes": minutes}
    db.ex("INSERT INTO plans(date, data, created_at) VALUES(?,?,?)",
          (db.today(), json.dumps(data, ensure_ascii=False), db.now()))
    return today_plan()


def update_block(plan_id, idx, action):
    p = db.q1("SELECT * FROM plans WHERE id=?", (plan_id,))
    data = json.loads(p["data"])
    bl = data["blocks"][idx]
    if action == "start":
        bl.update(status="active", started_at=db.now(), done_at=None)
    elif action == "done":
        bl.update(status="done", done_at=db.now())
        bl.setdefault("started_at", None)
    elif action == "skip":
        bl.update(status="skipped")
    elif action == "reset":
        bl.update(status="todo", started_at=None, done_at=None)
    db.ex("UPDATE plans SET data=? WHERE id=?", (json.dumps(data, ensure_ascii=False), plan_id))
    return _with_progress(db.q1("SELECT * FROM plans WHERE id=?", (plan_id,)))


# ---------- the free plan: same blocks as the coach's, built by rules instead of AI ----------
def _current_book():
    """The book read most recently, its page and the chapter that page is in."""
    r = db.q1("SELECT book_id FROM reading ORDER BY ts DESC LIMIT 1")
    b = db.q1("SELECT * FROM books WHERE id=?", (r["book_id"],)) if r else db.q1("SELECT * FROM books ORDER BY id DESC LIMIT 1")
    if not b:
        return None, None, None
    page = b["last_page"] or 1
    ch = db.q1("SELECT * FROM chapters WHERE book_id=? AND start_page<=? AND end_page>=? ORDER BY ord LIMIT 1",
               (b["id"], page, page)) or db.q1("SELECT * FROM chapters WHERE book_id=? ORDER BY ord LIMIT 1", (b["id"],))
    return b, ch, page




def current_book_brief():
    """For Home's "read on" shortcut: the book read last and the page it's on (None without a book)."""
    book, ch, page = _current_book()
    return {"id": book["id"], "title": book["title"], "page": page, "chapter": ch["title"] if ch else ""} if book else None


def quick_plan(minutes):
    """A plan without AI, in the same blocks (with live progress) as the coach's plan. About a third of the time goes
    to the textbook where you left off; the rest, in this order while it fits: flashcards that are due, the most
    repeated open mistake, a grammar course step (both courses from an hour up), a short noun or number drill, and
    gap-fills from the current chapter."""
    minutes = max(10, min(int(minutes), 300))
    day = db.study_date().toordinal()
    book, ch, page = _current_book()
    reading = round(minutes * 0.35) if book and minutes >= 20 else 0
    budget = minutes - reading
    blocks, why = [], []

    def add(block):
        nonlocal budget
        if block["minutes"] <= budget:
            blocks.append(block)
            budget -= block["minutes"]
            return True
        return False

    cc = card_counts()
    cards = cc["due"] + cc["new_available"]
    if cards:
        m = max(5, min(round(cards / 4), round(budget * 0.45)))
        if add({"kind": "flashcards", "title": "Flashcards", "minutes": m, "target_cards": min(cards, m * 4),
                "instructions": f"{cc['due']} cards are due and {cc['new_available']} new ones are waiting. Due cards come first.",
                "why": "Reviews done on the day they're due take the least time."}):
            why.append(f"{cards} flashcards waiting")

    mk = db.q("SELECT topic FROM mistakes WHERE status='open' GROUP BY topic ORDER BY SUM(times) DESC LIMIT 1")
    if mk and minutes >= 20:
        m = 5 if minutes < 60 else 10
        if add({"kind": "mistakes", "title": f"Mistake Book: {mk[0]['topic']}", "minutes": m, "target_questions": m * 2,
                "instructions": f"Open the Mistake Book and drill **{mk[0]['topic']}**, the topic you've missed most.",
                "why": "Fixing a repeated mistake now stops it from setting in."}):
            why.append(f"open mistakes in {mk[0]['topic']}")

    grammar = []
    for kind, b, page_name in (("declensions", course.brief(), "Declensions"), ("verbs", VERBS_COURSE.brief(), "Verbs")):
        if b["finished"]:
            grammar.append({"kind": kind, "sub": "free", "title": f"{page_name}: free practice",
                            "instructions": f"The {page_name.lower()} course is finished. Drill your weakest skills in Free practice."})
        else:
            step = f" Next step: **{b['next_step']}**." if b["next_step"] else ""
            grammar.append({"kind": kind, "title": f"{page_name}: {b['title']}",
                            "instructions": f"Continue the course at **{b['title']}** ({b['steps_done']} of {b['steps_total']} steps done).{step}"})
    for g in (grammar if minutes >= 60 else [grammar[day % 2]]):
        m = 10 if minutes < 90 else 15
        add({**g, "minutes": m, "target_questions": m * 3,
             "why": "Endings and verb forms only become automatic with a little practice every day."})

    if minutes >= 25:
        sub, title, text = (("nouns", "Nouns: der, die, das and plurals", "Genders and plurals, most common nouns first.")
                            if day % 2 == 0 else ("numbers", "Numbers, times and dates", "Numbers, clock times, dates and prices."))
        add({"kind": "declensions", "sub": sub, "title": title, "minutes": 5, "target_questions": 15,
             "instructions": f"Declensions → Free practice → {sub.title()}. {text}",
             "why": "A few minutes a day is enough for these to stick."})

    if book and ch and minutes >= 50:
        add({"kind": "practice", "sub": "gaps", "chapter_id": ch["id"], "book_id": book["id"], "minutes": 8,
             "target_questions": 10, "title": f"Gap-fills: {ch['title']}",
             "instructions": "Practice → Gap-fills from the book: real sentences from the chapter with one word to fill in.",
             "why": "Grammar in sentences from your own book."})

    reading += budget  # whatever didn't fit goes to the book
    if book and reading >= 8:
        blocks.append({"kind": "reader", "book_id": book["id"], "chapter_id": ch["id"] if ch else None, "start_page": page,
                       "minutes": reading, "target_pages": max(1, reading // 4), "target_questions": max(1, reading // 3),
                       "title": f"Read on: {book['title']}, page {page}",
                       "instructions": "Read where you left off and do the exercises on the page. Check them when you're done.",
                       "why": "Working through the book in order keeps everything else connected."})
        why.append(f"{book['title']}, page {page}")
    elif reading and blocks:
        g = next((b for b in blocks if b["kind"] in ("declensions", "verbs") and not b.get("sub")), blocks[-1])
        g["minutes"] += reading
        if g.get("target_questions"):
            g["target_questions"] = g["minutes"] * 3

    for bl in blocks:
        bl.update(status="todo", started_at=None, done_at=None)
    summary = "A quick plan built from your data, without AI" + (": " + ", ".join(why) + "." if why else ".")
    data = {"summary": summary, "blocks": blocks, "minutes": minutes, "quick": True}
    db.ex("INSERT INTO plans(date, data, created_at) VALUES(?,?,?)", (db.today(), json.dumps(data, ensure_ascii=False), db.now()))
    return today_plan()
