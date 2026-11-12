"""Links Mistake Book entries to declension skills, so they can be drilled for free with the rule engine, and
marks a mistake learned once each of its skills has been answered right on three separate study days
(a day only counts if that skill had no wrong answer that day)."""
import json

from . import ai, db, decl

LEARNED_DAYS = 3
BATCH = 40


def _valid():
    return decl._core_keys()


def _clean(keys):
    valid = _valid()
    out = []
    for k in keys or []:
        k = (k or "").strip()
        if k in valid and k not in out:
            out.append(k)
    return out[:4]


def classify_pending():
    """Ask Claude once (per batch of 40) which declension skills each new mistake is about. Mistakes that
    aren't about declension get an empty list, so they're never sent again."""
    rows = db.q("SELECT id, topic, question, wrong, correct, full_correct, explanation FROM mistakes "
                "WHERE skills IS NULL ORDER BY id LIMIT ?", (BATCH,))
    if not rows:
        return {"linked": 0, "checked": 0}
    found = ai.classify_mistakes(rows, sorted(n["word"] for n in decl.NOUNS))
    linked = 0
    for r in rows:
        keys = _clean(found.get(r["id"], []))
        linked += bool(keys)
        db.ex("UPDATE mistakes SET skills=? WHERE id=?", (json.dumps(keys), r["id"]))
    return {"linked": linked, "checked": len(rows),
            "pending": db.q1("SELECT COUNT(*) AS n FROM mistakes WHERE skills IS NULL")["n"]}


def _good_days(key, since):
    return db.q1("SELECT COUNT(*) AS n FROM (SELECT date FROM decl_log WHERE key=? AND date>=? "
                 "GROUP BY date HAVING MIN(correct)=1)", (key, since))["n"]


def progress(m):
    """Days of right answers so far (the weakest of the mistake's skills counts), or None if not linked."""
    keys = json.loads(m["skills"] or "[]") if m.get("skills") else []
    if not keys:
        return None
    since = (m["last_seen"] or m["created_at"] or "")[:10]
    return min(_good_days(k, since) for k in keys)


def auto_learn(keys=None):
    """Mark linked mistakes learned when they've been drilled right on enough days. Returns those just learned."""
    learned = []
    for m in db.q("SELECT * FROM mistakes WHERE status='open' AND skills IS NOT NULL AND skills <> '[]'"):
        mk = json.loads(m["skills"])
        if keys is not None and not set(mk) & set(keys):
            continue
        if progress(m) >= LEARNED_DAYS:
            db.ex("UPDATE mistakes SET status='learned', learned_at=?, learned_by='drill' WHERE id=?", (db.now(), m["id"]))
            learned.append({"id": m["id"], "wrong": m["wrong"], "correct": m["correct"]})
    return learned


def keys_for(ids=None):
    """All skills of the given (or all open) linked mistakes."""
    if ids:
        marks = ",".join("?" * len(ids))
        rows = db.q(f"SELECT skills FROM mistakes WHERE id IN ({marks}) AND skills IS NOT NULL", ids)
    else:
        rows = db.q("SELECT skills FROM mistakes WHERE status='open' AND skills IS NOT NULL")
    out = []
    for r in rows:
        for k in json.loads(r["skills"]):
            if k not in out:
                out.append(k)
    return out
