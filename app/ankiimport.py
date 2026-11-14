"""Anki import: reads .apkg / .colpkg files (old and new Anki formats) and Anki's plain-text export (.txt/.tsv/.csv)
into the app's flashcards.

- Each Anki note becomes one card: the first field is the front, the second the back, other fields go to "extra".
  Cloze notes become one card per cloze number ("Er [...] nach Hause." → "geht").
- Pictures and sounds aren't imported (the app's cards are text); [sound:] tags and <img> are removed.
- Review progress can be kept: interval, ease and due date carry over for cards Anki had already learned.
"""
import csv
import datetime as dt
import html
import io
import json
import re
import sqlite3
import tempfile
import uuid
import zipfile
from pathlib import Path

from . import db

PENDING = {}  # token → parsed import, between the preview and the import


def _zstd_decompress(data):
    try:
        from compression import zstd  # Python 3.14+
        return zstd.decompress(data)
    except ImportError:
        import zstandard
        return zstandard.ZstdDecompressor().decompressobj().decompress(data)


# ---------- text cleanup ----------
def clean(s):
    """Anki field HTML → plain text with line breaks."""
    s = s or ""
    s = re.sub(r"\[sound:[^\]]*\]", "", s)
    s = re.sub(r"<img[^>]*>", "", s, flags=re.I)
    s = re.sub(r"<br\s*/?>|</div>|</p>|</li>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s).replace("\xa0", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    return s.strip()


CLOZE = re.compile(r"\{\{c(\d+)::(.*?)(?:::(.*?))?\}\}", re.S)


def cloze_cards(text):
    """[(front, back)] for each cloze number in a cloze field."""
    out = []
    for n in sorted({int(m.group(1)) for m in CLOZE.finditer(text)}):
        answers = []

        def sub(m, n=n):
            if int(m.group(1)) == n:
                answers.append(m.group(2))
                return f"[{m.group(3)}]" if m.group(3) else "[...]"
            return m.group(2)
        front = CLOZE.sub(sub, text)
        out.append((clean(front), clean(" … ".join(answers))))
    return out


# ---------- reading the collection ----------
FRONT_NAMES = ("front", "vorderseite", "german", "deutsch", "word", "wort", "text", "question", "frage")
BACK_NAMES = ("back", "rückseite", "english", "englisch", "meaning", "bedeutung", "translation", "answer", "antwort")


def _pick(names, wanted, default):
    low = [n.lower() for n in names]
    for w in wanted:
        if w in low:
            return low.index(w)
    return default


def _models(con):
    """{notetype id: {"fields": [names], "cloze": bool}} for both the old (col.models JSON) and new (notetypes) schema."""
    tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if "notetypes" in tables:
        out = {}
        for ntid, name, config in con.execute("SELECT id, name, config FROM notetypes"):
            fields = [r[0] for r in con.execute("SELECT name FROM fields WHERE ntid=? ORDER BY ord", (ntid,))]
            tmpl = b"".join(r[0] or b"" for r in con.execute("SELECT config FROM templates WHERE ntid=?", (ntid,)))
            out[ntid] = {"fields": fields, "cloze": b"{{cloze:" in tmpl or "cloze" in name.lower()}
        return out
    models = json.loads(con.execute("SELECT models FROM col").fetchone()[0] or "{}")
    return {int(k): {"fields": [f["name"] for f in m["flds"]], "cloze": m.get("type") == 1} for k, m in models.items()}


def _decks(con):
    tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if "decks" in tables:
        return {did: name.replace("\x1f", "::") for did, name in con.execute("SELECT id, name FROM decks")}
    decks = json.loads(con.execute("SELECT decks FROM col").fetchone()[0] or "{}")
    return {int(k): d["name"] for k, d in decks.items()}


def read_collection(path):
    """Notes from an Anki collection file: [{deck, front, back, extra, tags, progress}]."""
    con = sqlite3.connect(f"file:{Path(path).as_posix()}?mode=ro", uri=True)
    try:
        models, decks = _models(con), _decks(con)
        crt = con.execute("SELECT crt FROM col").fetchone()[0] or 0
        today = (dt.datetime.now().timestamp() - crt) // 86400 if crt else 0
        cards = {}
        for nid, did, ctype, queue, due, ivl, factor, reps, lapses, ord_ in con.execute(
                "SELECT nid, did, type, queue, due, ivl, factor, reps, lapses, ord FROM cards ORDER BY ord"):
            cards.setdefault(nid, []).append({"did": did, "type": ctype, "queue": queue, "due": due, "ivl": ivl,
                                              "factor": factor, "reps": reps, "lapses": lapses, "ord": ord_})
        out = []
        for nid, mid, tags, flds in con.execute("SELECT id, mid, tags, flds FROM notes ORDER BY id"):
            m = models.get(mid, {"fields": [], "cloze": False})
            vals = flds.split("\x1f")
            names = m["fields"] + [f"Field {i + 1}" for i in range(len(m["fields"]), len(vals))]
            cs = cards.get(nid, [])
            deck = decks.get(cs[0]["did"], "Default") if cs else "Default"
            tag_list = [t for t in (tags or "").split() if t][:6]
            if m["cloze"]:
                text = vals[0]
                extra = "\n".join(clean(v) for v in vals[1:] if clean(v))
                for i, (front, back) in enumerate(cloze_cards(text)):
                    card = next((c for c in cs if c["ord"] == i), None)
                    out.append({"deck": deck, "type": "cloze", "front": front, "back": back, "extra": extra,
                                "tags": tag_list, "progress": _progress(card, today)})
                continue
            fi = _pick(names, FRONT_NAMES, 0)
            bi = _pick(names, BACK_NAMES, 1 if fi != 1 else 0)
            front, back = clean(vals[fi]) if fi < len(vals) else "", clean(vals[bi]) if bi < len(vals) else ""
            extra = "\n".join(f"{names[i]}: {clean(v)}" if len(vals) > 3 else clean(v)
                              for i, v in enumerate(vals) if i not in (fi, bi) and clean(v))
            if not front or not back:
                continue
            out.append({"deck": deck, "type": "vocab", "front": front, "back": back, "extra": extra[:1500],
                        "tags": tag_list, "progress": _progress(cs[0] if cs else None, today)})
        return out
    finally:
        con.close()


def _progress(card, today):
    """Anki's schedule for a learned card (review queue), in the app's terms; None for new cards."""
    if not card or card["queue"] != 2 or card["ivl"] <= 0:
        return None
    days = max(0, card["due"] - today)
    return {"interval": float(card["ivl"]), "ease": round(max(1.3, (card["factor"] or 2500) / 1000), 2),
            "reps": card["reps"], "lapses": card["lapses"], "due_in_days": int(days)}


def read_text(raw):
    """Anki's 'Notes in Plain Text' export, or any 2-3 column tab/semicolon/comma file."""
    text = raw.decode("utf-8-sig", errors="replace")
    lines = [l for l in text.splitlines() if l.strip()]
    sep = "\t"
    header = [l for l in lines if l.startswith("#")]
    for h in header:
        m = re.match(r"#separator:(\w+)", h)
        if m:
            sep = {"tab": "\t", "semicolon": ";", "comma": ",", "pipe": "|", "space": " "}.get(m.group(1).lower(), "\t")
    body = [l for l in lines if not l.startswith("#")]
    if not header and body and "\t" not in body[0]:
        sep = ";" if body[0].count(";") >= body[0].count(",") else ","
    out = []
    for row in csv.reader(io.StringIO("\n".join(body)), delimiter=sep):
        row = [clean(x) for x in row]
        if len(row) >= 2 and row[0] and row[1]:
            out.append({"deck": "Imported", "type": "vocab", "front": row[0], "back": row[1],
                        "extra": "\n".join(x for x in row[2:] if x)[:1500], "tags": [], "progress": None})
    return out


def read_file(filename, raw):
    name = filename.lower()
    if name.endswith((".txt", ".tsv", ".csv")):
        return read_text(raw), 0
    try:
        z = zipfile.ZipFile(io.BytesIO(raw))
    except zipfile.BadZipFile:
        raise ValueError("That isn't an Anki package (.apkg or .colpkg) or a text file.")
    names = set(z.namelist())
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "collection.db"
        if "collection.anki21b" in names:
            target.write_bytes(_zstd_decompress(z.read("collection.anki21b")))
        elif "collection.anki21" in names:
            target.write_bytes(z.read("collection.anki21"))
        elif "collection.anki2" in names:
            target.write_bytes(z.read("collection.anki2"))
        else:
            raise ValueError("No Anki collection found in that file.")
        notes = read_collection(target)
    media = sum(1 for n in names if n.isdigit())
    return notes, media


# ---------- preview and import ----------
def preview(filename, raw):
    notes, media = read_file(filename, raw)
    if not notes:
        raise ValueError("No cards with a front and a back were found in that file.")
    have = {r["front"] for r in db.q("SELECT front FROM cards")}
    decks = {}
    for n in notes:
        d = decks.setdefault(n["deck"], {"name": n["deck"], "count": 0, "duplicates": 0, "learned": 0, "sample": []})
        d["count"] += 1
        d["duplicates"] += n["front"] in have
        d["learned"] += n["progress"] is not None
        if len(d["sample"]) < 3:
            d["sample"].append({k: n[k] for k in ("front", "back")})
    token = uuid.uuid4().hex
    PENDING.clear()  # one import at a time is plenty
    PENDING[token] = notes
    return {"token": token, "file": filename, "total": len(notes), "media": media,
            "decks": sorted(decks.values(), key=lambda d: d["name"])}


def run(token, decks=None, keep_progress=True):
    notes = PENDING.pop(token, None)
    if notes is None:
        raise ValueError("That import has expired. Choose the file again.")
    have = {r["front"] for r in db.q("SELECT front FROM cards")}
    now = dt.datetime.now()
    rows, skipped = [], 0
    for n in notes:
        if decks is not None and n["deck"] not in decks:
            continue
        if n["front"] in have:
            skipped += 1
            continue
        have.add(n["front"])
        leaf = n["deck"].split("::")[-1]
        tags = json.dumps(["anki", leaf, *n["tags"]], ensure_ascii=False)
        p = n["progress"] if keep_progress else None
        if p:
            due = (now + dt.timedelta(days=p["due_in_days"])).isoformat(timespec="seconds")
            rows.append((n["type"], n["front"], n["back"], n["extra"], tags, due, p["interval"], p["ease"], p["reps"], p["lapses"]))
        else:
            rows.append((n["type"], n["front"], n["back"], n["extra"], tags, None, 0, 2.5, 0, 0))
    created = db.now()
    db.exmany("INSERT INTO cards(book_id, chapter_id, type, front, back, extra, tags, due, interval, ease, reps, lapses, created_at) "
              "VALUES(NULL,NULL,?,?,?,?,?,?,?,?,?,?,?)", [(*r, created) for r in rows])
    return {"added": len(rows), "skipped": skipped, "learned": sum(1 for r in rows if r[5])}
