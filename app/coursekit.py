"""A guided course: a fixed list of stages, each with a briefing, charts, a drill, a reading with gaps, flashcards and
a checkpoint, unlocked in order. Shared by the Declensions course (app/course.py, planets) and the Verbs course
(app/verbcourse.py, Alexander's march). A course only supplies its stages and a rule engine; everything about
progress, unlocking, stars and steps lives here, so a new course (word order, say) is mostly content.

The engine (a module or object) provides:
    build(mode, key) -> question     core_keys() -> set of skill keys     log_answer(family, right)
and the course passes:
    counts(key) -> whether a skill counts toward "skills solid" (long noun or verb lists would swamp it)
    card_tag: tag for the flashcards a stage adds
"""
import random
import re

from . import db, decl, i18n

STEP_INFO = {
    "learn": ("Briefing", "Read how it works, with charts and examples."),
    "chart": ("Charts", "Fill in the tables from memory."),
    "drill": ("Drill", "20 quick questions. Get 16 right to pass."),
    "reading": ("Reading", "Fill in the endings in a short text."),
    "cards": ("Flashcards", "Flip through the key rules."),
    "checkpoint": ("Checkpoint", "Pass this to unlock the next planet."),
}
_GAP = re.compile(r"\{([^{}|]+)\|([^{}|]*)(?:\|([^{}|]*))?\}")
SENTENCE_MODES = ("dsent", "wsent", "sent", "combo", "vsent", "modsent")


def G(mode, keys, w=1.0, review=False):
    """A group of questions a stage asks: a question builder (mode) over these skills, with a weight. Review groups
    (earlier stages mixed in) don't count toward the stage's own skills."""
    return {"mode": mode, "keys": keys, "w": w, "review": review}


def parse_reading(text):
    """'Ich sehe {den|the|def:akk:m} Mann' -> text and gap segments."""
    out, pos = [], 0
    for m in _GAP.finditer(text):
        if m.start() > pos:
            out.append({"t": text[pos:m.start()]})
        out.append({"a": m.group(1).strip(), "hint": m.group(2).strip(), "key": (m.group(3) or "").strip() or None})
        pos = m.end()
    if pos < len(text):
        out.append({"t": text[pos:]})
    return out


class Course:
    def __init__(self, stages, engine, counts=lambda k: True, card_tag="declension", step_info=None,
                 drill=(20, 16), reading_pass=.8, what=""):
        self.stages = stages
        self.engine = engine
        self.counts = counts
        self.card_tag = card_tag
        self.step_info = {**STEP_INFO, **(step_info or {})}
        self.drill_len, self.drill_pass = drill
        self.reading_pass = reading_pass
        self.what = what
        self.STAGE = {s["id"]: s for s in stages}
        self.ORDER = [s["id"] for s in stages]
        for s in stages:
            if callable(s["pool"]):
                s["pool"] = s["pool"]()

    # ---------- structure ----------
    def steps_of(self, stage):
        return ["learn"] + (["chart"] if stage["tables"] else []) + ["drill", "reading", "cards", "checkpoint"]

    def checkpoint_size(self, stage):
        return (25, 21) if stage.get("home") else (15, 13)

    def stage_keys(self, stage):
        """The skills this stage teaches (its own, not the review mixed into checkpoints)."""
        core = self.engine.core_keys()
        return sorted({k for g in stage["pool"] if not g.get("review") for k in g["keys"] if k in core and self.counts(k)})

    # ---------- questions ----------
    def question(self, stage_id, mode="drill", recent=()):
        """One question for a stage. Checkpoints lean on full sentences and mix in review of earlier stages."""
        stage = self.STAGE[stage_id]
        idx = self.ORDER.index(stage_id)
        checkpoint = mode == "checkpoint"
        if checkpoint and idx and random.random() < .2:
            stage = self.stages[random.randrange(idx)]
        groups = stage["pool"]
        weights = [g["w"] * (2 if checkpoint and g["mode"] in SENTENCE_MODES else 1) for g in groups]
        group = random.choices(groups, weights)[0]
        st, now, recent = decl._state(), db.now(), set(recent or ())
        key = random.choices(group["keys"], [decl._weight(k, st, recent, now) for k in group["keys"]])[0]
        return self.engine.build(group["mode"], key)

    def reading_brief(self, stage_id):
        """What a freshly written reading for this stage should practise (for the AI writer)."""
        stage = self.STAGE[stage_id]
        return {"focus": f"{stage['title']}: {stage['blurb']}", "example": stage["reading"][1]}

    # ---------- progress ----------
    def _done(self):
        out = {}
        ids = set(self.ORDER)
        for r in db.q("SELECT * FROM decl_progress"):
            if r["stage"] in ids:
                out.setdefault(r["stage"], {})[r["step"]] = r
        return out

    def journey(self):
        done, st = self._done(), decl._state()
        stages, unlocked, current = [], True, None
        for s in self.stages:
            mine = done.get(s["id"], {})
            steps = self.steps_of(s)
            complete = "checkpoint" in mine
            keys = self.stage_keys(s)
            solid = sum(1 for k in keys if st.get(k, {}).get("box", 0) >= 3)
            all_steps = all(x in mine for x in steps)
            stars = (1 if complete else 0) + (1 if complete and all_steps else 0) + (1 if complete and all_steps and solid >= .8 * len(keys) else 0)
            if unlocked and not complete and current is None:
                current = s["id"]
            size, need = self.checkpoint_size(s)
            stages.append({
                "id": s["id"], "planet": s["planet"], "title": s["title"], "blurb": s["blurb"], "hue": s.get("hue", 0),
                "ring": s.get("ring", False), "nebula": s.get("nebula", False), "home": s.get("home", False),
                "region": s.get("region"),
                "unlocked": unlocked, "complete": complete, "stars": stars,
                "skills": {"total": len(keys), "solid": solid, "seen": sum(1 for k in keys if k in st)},
                "steps": [{"id": x, "label": self.step_info[x][0], "text": self.step_info[x][1], "done": x in mine,
                           "best": mine.get(x, {}).get("best"), "skipped": bool(mine.get(x, {}).get("skipped"))} for x in steps],
                "checkpoint": {"size": size, "need": need}, "cards": len(s["cards"]),
            })
            unlocked = unlocked and complete
        return {"stages": stages, "current": current or self.ORDER[-1], "finished": current is None,
                "stars": sum(s["stars"] for s in stages), "max_stars": 3 * len(stages),
                "drill": {"size": self.drill_len, "need": self.drill_pass}}

    def detail(self, stage_id):
        s = self.STAGE[stage_id]
        return {"id": s["id"], "lesson": [list(b) for b in s["lesson"]],
                "tables": [{"id": t, "rows": rows, "cols": cols} for t, rows, cols in s["tables"]],
                "reading": {"title": s["reading"][0], "segments": parse_reading(s["reading"][1])},
                "cards": [{"front": f, "back": b, "extra": e} for f, b, e in s["cards"]],
                "cards_added": db.q1("SELECT COUNT(*) AS n FROM cards WHERE tags LIKE ?", (f'%"decl:{s["id"]}"%',))["n"]}

    def _unlocked(self, stage_id):
        return next(s["unlocked"] for s in self.journey()["stages"] if s["id"] == stage_id)

    def complete(self, stage_id, step, score=None, total=None):
        """Mark a step done if it was passed. Returns whether it counted, and the updated journey."""
        stage = self.STAGE[stage_id]
        if step not in self.steps_of(stage):
            raise db.UserError("Unknown step")
        if not self._unlocked(stage_id):
            raise db.UserError("This planet is still locked.")
        passed = True
        if step == "drill":
            passed = (score or 0) >= self.drill_pass and (total or 0) >= self.drill_len
        elif step == "checkpoint":
            size, need = self.checkpoint_size(stage)
            passed = (score or 0) >= need and (total or 0) >= size
        elif step == "reading":
            passed = bool(total) and score / total >= self.reading_pass
        was_complete = bool(db.q1("SELECT 1 AS x FROM decl_progress WHERE stage=? AND step='checkpoint'", (stage_id,)))
        if passed:
            db.ex("INSERT INTO decl_progress(stage, step, done_at, best) VALUES(?,?,?,?) ON CONFLICT(stage, step) DO UPDATE SET "
                  "best = MAX(COALESCE(best, 0), COALESCE(excluded.best, 0))", (stage_id, step, db.now(), score))
        idx = self.ORDER.index(stage_id)
        newly = passed and step == "checkpoint" and not was_complete
        return {"passed": passed, "planet_complete": newly,
                "next": self.ORDER[idx + 1] if newly and idx + 1 < len(self.ORDER) else None, "journey": self.journey()}

    def add_cards(self, stage_id):
        """Put the stage's rule cards into the learner's spaced-repetition deck (once)."""
        s = self.STAGE[stage_id]
        tag = f'["{self.card_tag}", "decl:{s["id"]}"]'
        have = {r["front"] for r in db.q("SELECT front FROM cards WHERE tags LIKE ?", (f'%"decl:{s["id"]}"%',))}
        t = i18n.tr if i18n.lang() == "tr" else (lambda x: x)  # cards go into the deck in the app's language
        rows = [(None, None, "rule", t(f), t(b), t(e), tag, db.now()) for f, b, e in s["cards"]
                if f not in have and i18n.tr(f) not in have]  # a card added in either language counts
        if rows:
            db.exmany("INSERT INTO cards(book_id, chapter_id, type, front, back, extra, tags, created_at) VALUES(?,?,?,?,?,?,?,?)", rows)
        return {"added": len(rows), "already": len(have)}

    def record(self, items, family="sent"):
        """Results from a reading or a matching round: [{key, correct}]. Updates the skills that have a key and logs
        every answer under the given family (it decides the topic shown in progress)."""
        core = self.engine.core_keys()
        for it in items:
            right = bool(it.get("correct"))
            if it.get("key") in core:
                decl.update_skill(it["key"], right, False)
            self.engine.log_answer(family, right)
        return {"ok": True}

    def brief(self):
        """The journey in a few numbers, for the Today page."""
        j = self.journey()
        cur = next(s for s in j["stages"] if s["id"] == j["current"])
        todo = [x for x in cur["steps"] if not x["done"]]
        return {"finished": j["finished"], "title": cur["title"], "planet": cur["planet"], "blurb": cur["blurb"],
                "steps_done": len(cur["steps"]) - len(todo), "steps_total": len(cur["steps"]),
                "next_step": todo[0]["label"] if todo else None,
                "planets_done": sum(1 for s in j["stages"] if s["complete"]), "planets_total": len(j["stages"]),
                "stars": j["stars"], "max_stars": j["max_stars"]}

    def coach_summary(self):
        j = self.journey()
        cur = next(s for s in j["stages"] if s["id"] == j["current"])
        return {"what": self.what,
                "stages_complete": sum(1 for s in j["stages"] if s["complete"]), "stages_total": len(j["stages"]),
                "finished": j["finished"], "current_stage": f"{cur['title']} ({cur['planet']})",
                "steps_left_on_current": [x["label"] for x in cur["steps"] if not x["done"]]}
