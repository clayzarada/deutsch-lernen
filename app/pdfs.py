"""PDF handling with PyMuPDF: chapter detection, text extraction, and exporting your written answers into a PDF."""
import json

import pymupdf as fitz

from .db import UserError

MAX_CHAPTER_CHARS = 300_000


def detect_chapters(path):
    """Return (page_count, [(title, start_page, end_page)]) using the PDF's bookmarks when it has them."""
    doc = fitz.open(path)
    n = doc.page_count
    toc = [t for t in doc.get_toc(simple=True) if 1 <= t[2] <= n]
    entries = []
    for level in (1, 2):
        entries = [t for t in toc if t[0] == level]
        if len(entries) >= 2:
            break
    doc.close()
    if len(entries) < 2:
        return n, [("Whole book", 1, n)]
    entries.sort(key=lambda t: t[2])
    chapters = []
    for i, (_, title, start) in enumerate(entries):
        end = entries[i + 1][2] - 1 if i + 1 < len(entries) else n
        chapters.append((title.strip() or f"Chapter {i + 1}", start, max(start, end)))
    if chapters[0][1] > 1:
        chapters.insert(0, ("Front matter", 1, chapters[0][1] - 1))
    return n, chapters


def page_text(path, start, end):
    doc = fitz.open(path)
    parts = []
    for p in range(max(1, start), min(end, doc.page_count) + 1):
        parts.append(f"--- Seite {p} ---\n{doc[p - 1].get_text().strip()}")
    doc.close()
    text = "\n\n".join(parts)
    if len(text) > MAX_CHAPTER_CHARS:
        raise UserError("This chapter is very long. Split it into smaller chapters in the Library first.")
    return text


def chapter_pdf(path, start, end):
    """A PDF with just these pages, e.g. to upload a chapter to Gemini Notebook."""
    src = fitz.open(path)
    out = fitz.open()
    out.insert_pdf(src, from_page=start - 1, to_page=end - 1)
    data = out.tobytes(garbage=3, deflate=True)
    out.close()
    src.close()
    return data


def html_to_pdf(html, out_path):
    """Turns a text/HTML document (e.g. a Google Takeout export) into a readable PDF for the library."""
    story = fitz.Story(html=html, user_css="body { font-family: sans-serif; font-size: 11pt; line-height: 1.4; }")
    writer = fitz.DocumentWriter(str(out_path))
    page = fitz.paper_rect("a4")
    area = page + (54, 54, -54, -54)
    more = 1
    while more:
        device = writer.begin_page(page)
        more, _ = story.place(area)
        story.draw(device)
        writer.end_page()
    writer.close()


def text_of_pdf(data):
    doc = fitz.open(stream=data, filetype="pdf")
    text = "\n\n".join(p.get_text() for p in doc)
    doc.close()
    return text


def thumbnail(path, out, width=320):
    doc = fitz.open(path)
    page = doc[0]
    zoom = width / page.rect.width
    page.get_pixmap(matrix=fitz.Matrix(zoom, zoom)).save(out)
    doc.close()


def _rgb(hex_color):
    h = (hex_color or "#1d4ed8").lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def export_annotated(path, annotations):
    """Burn typed answers and pen strokes into a copy of the PDF and return its bytes."""
    doc = fitz.open(path)
    for a in annotations:
        if not 1 <= a["page"] <= doc.page_count:
            continue
        page = doc[a["page"] - 1]
        w, h = page.rect.width, page.rect.height
        m = page.derotation_matrix
        data = json.loads(a["data"])
        if a["kind"] == "text" and data.get("text", "").strip():
            size = float(data.get("size", 11))
            point = fitz.Point(a["x"] * w, a["y"] * h + size) * m
            page.insert_text(point, data["text"], fontsize=size, color=_rgb(data.get("color")),
                             rotate=page.rotation)
        elif a["kind"] == "ink" and len(data.get("points", [])) > 1:
            pts = [fitz.Point(x * w, y * h) * m for x, y in data["points"]]
            shape = page.new_shape()
            shape.draw_polyline(pts)
            shape.finish(color=_rgb(data.get("color")), width=float(data.get("width", 2)),
                         stroke_opacity=float(data.get("opacity", 1)), closePath=False)
            shape.commit()
    out = doc.tobytes(garbage=3, deflate=True)
    doc.close()
    return out
