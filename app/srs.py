"""Spaced repetition scheduling (a simplified SM-2, the algorithm classic Anki uses).

Grades: 1 = Again, 2 = Hard, 3 = Good, 4 = Easy. Intervals are in days.
"""
import datetime as dt


def schedule(card, grade):
    ease = card["ease"] or 2.5
    interval = card["interval"] or 0
    reps = card["reps"] or 0
    lapses = card["lapses"] or 0

    if grade == 1:
        reps, lapses = 0, lapses + 1
        interval = 10 / 1440  # see it again in 10 minutes
        ease = max(1.3, ease - 0.2)
    else:
        if grade == 2:
            interval = 0.25 if reps == 0 else max(1, interval * 1.2)
            ease = max(1.3, ease - 0.15)
        elif grade == 3:
            interval = 1 if reps == 0 else 3 if reps == 1 else interval * ease
        else:
            interval = 4 if reps == 0 else max(interval * ease * 1.3, interval + 1)
            ease += 0.15
        reps += 1

    due = dt.datetime.now() + dt.timedelta(days=interval)
    return {"ease": round(ease, 3), "interval": round(interval, 4), "reps": reps, "lapses": lapses,
            "due": due.isoformat(timespec="seconds")}


def _label(days):
    if days < 1 / 24:
        return f"{round(days * 1440)}m"
    if days < 1:
        return f"{round(days * 24)}h"
    if days < 30:
        return f"{round(days)}d"
    return f"{days / 30:.1f}mo"


def preview(card):
    """When the card would come back for each grade, e.g. {1: '10m', 3: '3d'} - shown on the grade buttons."""
    return {g: _label(schedule(card, g)["interval"]) for g in (1, 2, 3, 4)}
