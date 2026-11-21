"""Spaced repetition scheduling with FSRS (the Free Spaced Repetition Scheduler that modern Anki uses).

Grades: 1 = Again, 2 = Hard, 3 = Good, 4 = Easy. Intervals are in days.

FSRS keeps two numbers per card:
- stability (S): how many days until the chance of remembering the card drops to 90%;
- difficulty (D): 1 (easy) to 10 (hard); it decides how fast stability grows.
The next interval is the time until the chance of remembering falls to the desired retention (0.9 by default,
0.8-0.95 in Settings). This is FSRS-6 with its published default parameters, written out from the formulas.

Learning steps work like before: a new or missed card ("reps" = 0) comes back after minutes (Again: 10 minutes,
Hard: 6 hours) until it is answered Good or Easy, then it moves on to days. "interval" and "due" are kept up to
date as always, because the stats and the known-words count read them; "ease" is no longer used for scheduling
and is left as it was.
"""
import datetime as dt
import math

# FSRS-6 default parameters (w0..w20).
W = (0.212, 1.2931, 2.3065, 8.2956, 6.4133, 0.8334, 3.0194, 0.001, 1.8722, 0.1666, 0.796,
     1.4835, 0.0614, 0.2629, 1.6483, 0.6014, 1.8729, 0.5425, 0.0912, 0.0658, 0.1542)
DECAY = -W[20]
FACTOR = 0.9 ** (1 / DECAY) - 1  # makes the chance of remembering exactly 90% after S days

DEFAULT_RETENTION = 0.9
MIN_RETENTION, MAX_RETENTION = 0.8, 0.95
AGAIN_STEP = 10 / 1440  # a missed card comes back in 10 minutes
HARD_STEP = 0.25        # "Hard" while still learning: 6 hours
MAX_INTERVAL = 36500
S_MIN = 0.01


def retention():
    """The learner's desired retention from Settings, kept within the allowed range."""
    from . import db  # here, not at the top: db imports this module while migrating old cards
    try:
        r = float(db.get_settings().get("desired_retention") or DEFAULT_RETENTION)
    except ValueError:
        r = DEFAULT_RETENTION
    return min(MAX_RETENTION, max(MIN_RETENTION, r))


# ---------- the FSRS formulas ----------

def recall(t, s):
    """Chance of remembering after t days at stability s."""
    return (1 + FACTOR * max(t, 0) / s) ** DECAY


def next_interval(s, r):
    """Days until the chance of remembering falls to r."""
    return s / FACTOR * (r ** (1 / DECAY) - 1)


def _clamp_d(d):
    return min(10.0, max(1.0, d))


def _clamp_s(s):
    return min(MAX_INTERVAL, max(S_MIN, s))


def init_stability(g):
    return W[g - 1]


def init_difficulty(g):
    return _clamp_d(W[4] - math.exp(W[5] * (g - 1)) + 1)


def next_difficulty(d, g):
    delta = -W[6] * (g - 3)
    d2 = d + delta * (10 - d) / 9  # changes shrink as the card nears the hardest value
    return _clamp_d(W[7] * init_difficulty(4) + (1 - W[7]) * d2)  # a slow pull back toward the default


def stability_after_success(d, s, r, g):
    hard = W[15] if g == 2 else 1
    easy = W[16] if g == 4 else 1
    return _clamp_s(s * (1 + math.exp(W[8]) * (11 - d) * s ** -W[9] * (math.exp(W[10] * (1 - r)) - 1) * hard * easy))


def stability_after_lapse(d, s, r):
    new = W[11] * d ** -W[12] * ((s + 1) ** W[13] - 1) * math.exp(W[14] * (1 - r))
    return _clamp_s(min(new, s / math.exp(W[17] * W[18])))


def stability_short_term(s, g):
    """Reviews on the same day (learning steps) change stability only a little."""
    inc = math.exp(W[17] * (g - 3 + W[18])) * s ** -W[19]
    if g >= 3:
        inc = max(inc, 1)
    return _clamp_s(s * inc)


# ---------- cards from before FSRS ----------

def from_legacy(card):
    """Stability and difficulty for a card scheduled by the old SM-2 code (or imported from Anki), chosen so its
    schedule doesn't jump: a card due after `interval` days gets stability = interval, which means FSRS also
    expects 90% recall on the day it is due. Ease becomes difficulty (2.5, the starting ease, is the middle;
    every miss lowered the ease, so lapses are already in it). Cards still in learning ("reps" = 0) start from
    the stability of a first "Again"."""
    ease = card.get("ease") or 2.5
    d = _clamp_d(5 + (2.5 - ease) * 5 / 1.2)
    if not (card.get("reps") or 0):
        return W[0], d
    return _clamp_s(card.get("interval") or W[0]), d


def _state(card):
    """(stability, difficulty), or None for a card that was never reviewed."""
    if card.get("due") is None:
        return None
    if card.get("stability") and card.get("difficulty"):
        return card["stability"], card["difficulty"]
    return from_legacy(card)


def _elapsed(card, now):
    """Days since the last review: the due date minus the interval it was given."""
    try:
        last = dt.datetime.fromisoformat(card["due"]) - dt.timedelta(days=card.get("interval") or 0)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, (now - last).total_seconds() / 86400)


def _days(s, r):
    return min(MAX_INTERVAL, max(1, round(next_interval(s, r))))


def _outcomes(card, r, now):
    """What each grade would do: {grade: (stability, difficulty, interval, reps, lapses)}."""
    reps, lapses = card.get("reps") or 0, card.get("lapses") or 0
    st = _state(card)
    out = {}
    if st is None:  # a new card
        for g in (1, 2, 3, 4):
            out[g] = (init_stability(g), init_difficulty(g))
    else:
        s, d = st
        t = _elapsed(card, now)
        rec = recall(t, s)
        for g in (1, 2, 3, 4):
            if t < 1:
                s2 = stability_short_term(s, g)
            elif g == 1:
                s2 = stability_after_lapse(d, s, rec)
            else:
                s2 = stability_after_success(d, s, rec, g)
            out[g] = (s2, next_difficulty(d, g))

    learning = st is None or reps == 0
    ivl = {g: _days(out[g][0], r) for g in (2, 3, 4)}
    if learning:
        ivl[2] = HARD_STEP
    else:  # keep the buttons in order: Hard <= Good < Easy
        ivl[2] = min(ivl[2], ivl[3])
        ivl[3] = max(ivl[3], ivl[2] + 1)
    ivl[4] = max(ivl[4], ivl[3] + 1)
    ivl[1] = AGAIN_STEP

    return {1: (*out[1], ivl[1], 0, lapses + 1),  # every miss counts toward "tricky", as before
            2: (*out[2], ivl[2], reps if learning else reps + 1, lapses),
            3: (*out[3], ivl[3], reps + 1, lapses),
            4: (*out[4], ivl[4], reps + 1, lapses)}


def schedule(card, grade, r=None, now=None):
    """The card's new schedule after a grade. Returns the columns to store."""
    now = now or dt.datetime.now()
    s, d, interval, reps, lapses = _outcomes(card, r or retention(), now)[grade]
    due = now + dt.timedelta(days=interval)
    return {"ease": card.get("ease") or 2.5, "interval": round(interval, 4), "reps": reps, "lapses": lapses,
            "stability": round(s, 4), "difficulty": round(d, 4), "due": due.isoformat(timespec="seconds")}


def _label(days):
    if days < 1 / 24:
        return f"{round(days * 1440)}m"
    if days < 1:
        return f"{round(days * 24)}h"
    if days < 30:
        return f"{round(days)}d"
    return f"{days / 30:.1f}mo"


def preview(card, r=None, now=None):
    """When the card would come back for each grade, e.g. {1: '10m', 3: '3d'} - shown on the grade buttons."""
    res = _outcomes(card, r or retention(), now or dt.datetime.now())
    return {g: _label(res[g][2]) for g in (1, 2, 3, 4)}
