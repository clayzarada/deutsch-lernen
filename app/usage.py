"""What the AI features cost: every Claude and Gemini call is logged with an estimated price, and an optional
monthly budget pauses Claude features once it's reached. Estimates use Anthropic's list prices; the real bill is
on console.anthropic.com (other apps or computers using the same key aren't counted here)."""
import datetime as dt

from . import db

# USD per million tokens: (input, output, cache read). Writing to the prompt cache costs 1.25x input.
PRICES = {
    "claude-fable-5-2": (8.0, 40.0, 0.20),
    "claude-fable-5-1": (10.0, 50.0, 1.00),
    "claude-opus-5-5": (4.0, 20.0, 0.20),
    "claude-opus-5": (5.0, 25.0, 0.50),
    "claude-opus-4-8": (5.0, 25.0, 0.50),
    "claude-sonnet-5-5": (2.0, 10.0, 0.10),
    "claude-sonnet-5": (2.0, 10.0, 0.20),
    "claude-haiku-5-5": (0.10, 0.50, 0.01),
}
WEB_SEARCH_PER_1000 = 10.0

FEATURES = {
    "generate_exercises": "Practice sets", "generate_cards": "Flashcard generation", "convert_import": "Gemini Notebook import",
    "recover_questions": "Mistake Book repair", "drill_mistakes": "Mistake drills (AI)", "write_episode": "Listening scripts",
    "grade_answers": "Marking practice answers", "check_page": "Checking textbook pages", "check_page_text": "Checking textbook pages (typed answers)", "confirm_mistakes": "Double-checking mistakes", "lookup": "Word look-ups",
    "explain": "Explanations", "decl_reading": "Declension readings", "make_plan": "Daily plans", "coach_reply": "Coach chat",
    "classify_mistakes": "Linking mistakes to drills", "grade_writing": "Writing marking", "writing_task": "Writing tasks",
    "synthesize": "Listening audio (Gemini)", "speak": "Pronunciation (Gemini)",
}


def _price(model):
    for name, p in PRICES.items():
        if model and model.startswith(name):
            return p
    return PRICES["claude-opus-5-5"]  # unknown model: assume Opus pricing rather than under-count


def log_claude(feature, resp):
    u = resp.usage
    inp = getattr(u, "input_tokens", 0) or 0
    out = getattr(u, "output_tokens", 0) or 0
    cread = getattr(u, "cache_read_input_tokens", 0) or 0
    cwrite = getattr(u, "cache_creation_input_tokens", 0) or 0
    stu = getattr(u, "server_tool_use", None)
    searches = (getattr(stu, "web_search_requests", 0) or 0) if stu else 0
    model = getattr(resp, "model", "") or ""
    pi, po, pc = _price(model)
    cost = (inp * pi + out * po + cread * pc + cwrite * pi * 1.25) / 1e6 + searches * WEB_SEARCH_PER_1000 / 1000
    db.ex("INSERT INTO api_usage(ts, date, feature, provider, model, input_tokens, output_tokens, cache_read, cache_write, "
          "web_searches, cost) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
          (db.now(), db.today(), feature, "claude", model, inp, out, cread, cwrite, searches, round(cost, 6)))


def log_gemini(feature, model):
    """Gemini audio is counted but not priced (the free tier costs nothing; paid rates vary)."""
    db.ex("INSERT INTO api_usage(ts, date, feature, provider, model, cost) VALUES(?,?,?,?,?,NULL)",
          (db.now(), db.today(), feature, "gemini", model))


def _month_start():
    return dt.date.today().replace(day=1).isoformat()


def month_spend():
    return db.q1("SELECT COALESCE(SUM(cost), 0) AS c FROM api_usage WHERE provider='claude' AND ts >= ?", (_month_start(),))["c"]


def budget():
    try:
        return max(0.0, float(db.get_settings().get("monthly_budget") or 0))
    except ValueError:
        return 0.0


def check_budget():
    """Raises before a Claude call once this month's spending reached the budget."""
    from .ai import AIError
    b = budget()
    if b and month_spend() >= b:
        raise AIError(f"This month's AI budget of ${b:.2f} has been reached, so AI features are paused until next month. "
                      "You can raise or clear the budget in Settings.")


def summary():
    start = _month_start()
    rows = db.q("SELECT feature, provider, COUNT(*) AS calls, COALESCE(SUM(cost), 0) AS cost FROM api_usage "
                "WHERE ts >= ? GROUP BY feature, provider ORDER BY cost DESC, calls DESC", (start,))
    months = db.q("SELECT substr(ts, 1, 7) AS month, COALESCE(SUM(cost), 0) AS cost, COUNT(*) AS calls FROM api_usage "
                  "WHERE provider='claude' GROUP BY month ORDER BY month DESC LIMIT 6")
    since = db.q1("SELECT MIN(ts) AS t FROM api_usage")["t"]
    return {
        "month": round(month_spend(), 4), "budget": budget(), "since": since,
        "features": [{**r, "label": FEATURES.get(r["feature"], r["feature"]), "cost": round(r["cost"], 4)} for r in rows],
        "months": [{**m, "cost": round(m["cost"], 4)} for m in reversed(months)],
        "today": round(db.q1("SELECT COALESCE(SUM(cost), 0) AS c FROM api_usage WHERE date=?", (db.today(),))["c"], 4),
    }
