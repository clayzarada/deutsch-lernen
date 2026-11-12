"""Anki export: .apkg files via genanki, or direct push into a running Anki through the AnkiConnect add-on."""
import json
import tempfile
import urllib.request
import zlib
from pathlib import Path

import genanki

# Fixed IDs so re-importing updates existing notes instead of duplicating them.
MODEL_ID = 1607392319
DECK_BASE_ID = 2059400110

CSS = """
.card { font-family: Arial, sans-serif; font-size: 24px; text-align: center; color: #111; background: #fff; }
.extra { font-size: 16px; color: #555; margin-top: 16px; }
.nightMode .card { color: #eee; background: #222; }
.nightMode .extra { color: #aaa; }
"""

MODEL = genanki.Model(
    MODEL_ID, "GermanStudy Card",
    fields=[{"name": "Front"}, {"name": "Back"}, {"name": "Extra"}, {"name": "CardId"}],
    templates=[{
        "name": "Card 1",
        "qfmt": "{{Front}}",
        "afmt": '{{FrontSide}}<hr id="answer">{{Back}}<div class="extra">{{Extra}}</div>',
    }],
    css=CSS,
)


def _html(text):
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")


def deck_name(card, names):
    book, chapter = names.get(("b", card["book_id"])), names.get(("c", card["chapter_id"]))
    parts = ["German"] + [p.replace("::", ":") for p in (book, chapter) if p]
    return "::".join(parts)


def build_apkg(cards, names):
    decks = {}
    for c in cards:
        name = deck_name(c, names)
        if name not in decks:
            decks[name] = genanki.Deck(DECK_BASE_ID + zlib.crc32(name.encode()) % 10_000_000, name)
        tags = [t.replace(" ", "_") for t in json.loads(c["tags"] or "[]")] + [c["type"] or "card"]
        decks[name].add_note(genanki.Note(
            model=MODEL,
            fields=[_html(c["front"]), _html(c["back"]), _html(c["extra"]), str(c["id"])],
            tags=tags,
            guid=genanki.guid_for("germanstudy", c["id"]),
        ))
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "deck.apkg"
        genanki.Package(list(decks.values())).write_to_file(str(out))
        return out.read_bytes()


def _anki_connect(action, **params):
    body = json.dumps({"action": action, "version": 6, "params": params}).encode()
    req = urllib.request.Request("http://127.0.0.1:8765", body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read())
    if result.get("error"):
        raise RuntimeError(result["error"])
    return result["result"]


def push(cards, names):
    """Add cards to a running Anki (needs the AnkiConnect add-on). Uses Anki's built-in Basic note type."""
    try:
        _anki_connect("version")
    except Exception:
        raise RuntimeError("Couldn't reach Anki. Open Anki and install the AnkiConnect add-on (code 2055492159).")
    for name in {deck_name(c, names) for c in cards}:
        _anki_connect("createDeck", deck=name)
    notes = [{
        "deckName": deck_name(c, names),
        "modelName": "Basic",
        "fields": {"Front": _html(c["front"]),
                   "Back": _html(c["back"]) + (f"<br><br><small>{_html(c['extra'])}</small>" if c["extra"] else "")},
        "tags": ["germanstudy", c["type"] or "card"],
        "options": {"allowDuplicate": False, "duplicateScope": "deck"},
    } for c in cards]
    result = _anki_connect("addNotes", notes=notes)
    added = sum(1 for r in result if r)
    return {"added": added, "skipped": len(notes) - added}
