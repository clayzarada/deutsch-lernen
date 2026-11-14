"""Reading a textbook page for marking, without making the AI read typed answers off a picture.

The PDF's own text comes with positions, and so do the learner's typed answers (text boxes). Each typed answer is
put into the printed line it sits on, at the place it was typed, so a gap-fill reads like the finished sentence:

    L14: 3. Wie heißt ⟦A2: sein⟧ Vater?

The AI then marks text it can read exactly (no misreading, no answers split over two lines lost), which a small,
cheap model does well. Pen marks are never sent: they are for circling and brackets, not answers.

Re-checking a page only marks typed answers that changed since the last check; the others keep their marks.
"""
import json

import pymupdf as fitz

from . import db

LINE_H = 1.2  # text boxes use line-height 1.2 (see .tbox in style.css)


def _printed_lines(pdf_path, page_no):
    """The page's printed lines in reading order, with positions as fractions of the page (0..1)."""
    doc = fitz.open(pdf_path)
    try:
        page = doc[page_no - 1]
        W, H = page.rect.width, page.rect.height
        words = page.get_text("words")  # x0, y0, x1, y1, word, block, line, word_no
    finally:
        doc.close()
    lines = {}
    for x0, y0, x1, y1, w, b, ln, _ in words:
        lines.setdefault((b, ln), []).append((x0 / W, y0 / H, x1 / W, y1 / H, w))
    out = []
    for key in sorted(lines):  # PyMuPDF numbers blocks in reading order
        ws = sorted(lines[key], key=lambda t: t[0])
        out.append({"words": ws, "x0": min(w[0] for w in ws), "x1": max(w[2] for w in ws),
                    "y0": min(w[1] for w in ws), "y1": max(w[3] for w in ws), "answers": []})
    # Item numbers ("1", "2a") often sit in their own little block: join each to the sentence on its row.
    # Numbers left over (margin numbering, page numbers) are dropped; they'd only attract answers wrongly.
    text_lines = [ln for ln in out if not _is_number(ln)]
    for ln in out:
        if _is_number(ln):
            row = [t for t in text_lines if t["y0"] - .004 <= (ln["y0"] + ln["y1"]) / 2 <= t["y1"] + .004
                   and 0 <= t["x0"] - ln["x1"] < .12]
            if row:
                t = min(row, key=lambda t: t["x0"] - ln["x1"])
                t["words"] = ln["words"] + t["words"]
    return text_lines, H


def _is_number(ln):
    t = "".join(w[4] for w in ln["words"])
    return len(t) <= 4 and any(c.isdigit() for c in t) and sum(c.isalpha() for c in t) <= 1


def _anchor(box, lines):
    """(index, on_the_line): the printed line a typed answer belongs to: the one it sits on, else the nearest one
    just above it (an answer written on the blank line under a question)."""
    by, bh = box["y"], box["h"]
    mid = by + min(bh, box["line_h"]) / 2  # the middle of the answer's first line
    best, best_d, on = None, None, False
    for i, ln in enumerate(lines):
        if ln["y0"] - box["line_h"] * .35 <= mid <= ln["y1"] + box["line_h"] * .35:
            d, here = abs((ln["y0"] + ln["y1"]) / 2 - mid) * 4 + max(0, ln["x0"] - box["x"], box["x"] - ln["x1"]), True
        elif ln["y1"] < mid:
            d, here = 10 + (mid - ln["y1"]) * 20 + max(0, ln["x0"] - box["x"] - .05) * 2, False
        else:
            continue
        if best_d is None or d < best_d:
            best, best_d, on = i, d, here
    return best, on


def transcript(pdf_path, page_no, annots):
    """(text, answers, has_handwriting). answers: {"A1": {"id", "text"}}; the text shows each answer in place."""
    lines, page_h = _printed_lines(pdf_path, page_no)
    boxes, ink = [], False
    for a in annots:
        if a["kind"] == "ink":
            if (a["data"].get("opacity") or 1) >= 1:  # highlighter strokes aren't answers
                ink = True
            continue
        text = " ".join(t.strip() for t in (a["data"].get("text") or "").splitlines() if t.strip())
        if not text:
            continue
        lh = (a["data"].get("size") or 12) * LINE_H / page_h
        n = max(1, len((a["data"].get("text") or "").strip().splitlines()))
        boxes.append({"id": a["id"], "text": text, "x": a["x"], "y": a["y"], "h": n * lh, "line_h": lh})
    boxes.sort(key=lambda b: (round(b["y"], 3), b["x"]))
    answers = {}
    loose = []
    for n, b in enumerate(boxes, 1):
        ref = f"A{n}"
        answers[ref] = {"id": b["id"], "text": b["text"]}
        i, on = _anchor(b, lines) if lines else (None, False)
        # On the line: in place (a filled gap reads like the sentence). Below it: after the line's text.
        (lines[i]["answers"] if i is not None else loose).append((b["x"] if on else 2 + b["y"], ref, b["text"]))

    out = []
    for n, ln in enumerate(lines, 1):
        parts = [(w[0], w[4]) for w in ln["words"]] + [(x, f"⟦{ref}: {t}⟧") for x, ref, t in ln["answers"]]
        parts.sort(key=lambda p: p[0])
        out.append(f"L{n}: " + " ".join(p[1] for p in parts))
    for x, ref, t in loose:
        out.append(f"(not near any printed line) ⟦{ref}: {t}⟧")
    return "\n".join(out), answers, ink


# ---------- remembering the last check, so a re-check only marks what changed ----------
def previous(book_id, page):
    """{annotation id: (answer text, marked item)} from the last check of this page."""
    row = db.q("SELECT data FROM page_checks WHERE book_id=? AND page=?", (book_id, page))
    try:
        data = json.loads(row[0]["data"]) if row else {}
    except ValueError:
        data = {}
    return {int(k): (v["text"], v["item"]) for k, v in data.get("typed", {}).items()}


def remember(book_id, page, typed):
    """typed: {annotation id: (answer text, marked item)}"""
    data = json.dumps({"typed": {str(k): {"text": t, "item": i} for k, (t, i) in typed.items()}}, ensure_ascii=False)
    db.ex("INSERT INTO page_checks(book_id, page, data, checked_at) VALUES(?,?,?,?) "
          "ON CONFLICT(book_id, page) DO UPDATE SET data=excluded.data, checked_at=excluded.checked_at",
          (book_id, page, data, db.now()))
