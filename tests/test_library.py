"""Anki import (old and new package formats, plain text), the flashcard pack library and the free quick plan."""
import io
import json
import sqlite3
import zipfile

import genanki
import pytest

from app import ankiimport, db, packs


def _zstd(data):
    try:
        from compression import zstd
        return zstd.compress(data)
    except ImportError:
        import zstandard
        return zstandard.ZstdCompressor().compress(data)


def _old_apkg(tmp_path):
    basic = genanki.Model(1, "Basic", fields=[{"name": "Front"}, {"name": "Back"}],
                          templates=[{"name": "C1", "qfmt": "{{Front}}", "afmt": "{{Back}}"}])
    deck = genanki.Deck(11, "Deutsch::Kapitel 1")
    deck.add_note(genanki.Note(basic, ["<b>der Hund</b>", "dog<br>[sound:hund.mp3]"], tags=["tiere"]))
    deck.add_note(genanki.Note(basic, ["die Katze", "cat <img src='k.jpg'>"]))
    deck.add_note(genanki.Note(genanki.CLOZE_MODEL, ["Er {{c1::geht}} nach {{c2::Hause::where}}.", "gehen"]))
    path = tmp_path / "old.apkg"
    genanki.Package(deck).write_to_file(path)
    return path.read_bytes()


def _new_apkg():
    """A package in the newer Anki format: collection.anki21b, zstd-compressed, with notetypes/fields/decks tables."""
    con = sqlite3.connect(":memory:")
    con.executescript("""
        CREATE TABLE col(id, crt, models, decks);
        CREATE TABLE notes(id, mid, tags, flds);
        CREATE TABLE cards(id, nid, did, ord, type, queue, due, ivl, factor, reps, lapses);
        CREATE TABLE notetypes(id, name, config);
        CREATE TABLE fields(ntid, ord, name);
        CREATE TABLE templates(ntid, ord, name, config);
        CREATE TABLE decks(id, name);""")
    import time
    crt = int(time.time()) - 100 * 86400
    con.execute("INSERT INTO col VALUES(1, ?, '', '')", (crt,))
    con.execute("INSERT INTO notetypes VALUES(5, 'Deutsch', x'00')")
    con.executemany("INSERT INTO fields VALUES(5, ?, ?)", [(0, "English"), (1, "German"), (2, "Plural")])
    con.execute("INSERT INTO templates VALUES(5, 0, 'Card 1', CAST('{{German}}' AS BLOB))")
    con.execute("INSERT INTO decks VALUES(7, 'Vokabeln\x1fA2')")
    con.execute("INSERT INTO notes VALUES(1, 5, ' haus ', 'house\x1fdas Haus\x1fdie Häuser')")
    con.execute("INSERT INTO notes VALUES(2, 5, '', 'tree\x1fder Baum\x1f')")
    # the first card is learned: 30-day interval, due in 10 days; the second is new
    con.execute("INSERT INTO cards VALUES(1, 1, 7, 0, 2, 2, 110, 30, 2300, 9, 1)")
    con.execute("INSERT INTO cards VALUES(2, 2, 7, 0, 0, 0, 1, 0, 0, 0, 0)")
    con.commit()
    raw = con.serialize()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("collection.anki2", b"old dummy")
        z.writestr("collection.anki21b", _zstd(raw))
        z.writestr("0", b"jpeg")
    return buf.getvalue()


def test_clean_and_cloze():
    assert ankiimport.clean("<div>der&nbsp;Hund</div><br>[sound:x.mp3]") == "der Hund"
    cards = ankiimport.cloze_cards("Er {{c1::geht}} nach {{c2::Hause::where}}.")
    assert cards == [("Er [...] nach Hause.", "geht"), ("Er geht nach [where].", "Hause")]


def test_old_package(tmp_path):
    notes, media = ankiimport.read_file("old.apkg", _old_apkg(tmp_path))
    by = {n["front"]: n for n in notes}
    assert by["der Hund"]["back"] == "dog" and by["der Hund"]["deck"] == "Deutsch::Kapitel 1" and "tiere" in by["der Hund"]["tags"]
    assert by["die Katze"]["back"] == "cat"
    assert by["Er [...] nach Hause."]["back"] == "geht" and by["Er [...] nach Hause."]["type"] == "cloze"


def test_new_package_picks_fields_by_name_and_keeps_progress():
    notes, media = ankiimport.read_file("new.apkg", _new_apkg())
    assert media == 1
    haus = next(n for n in notes if n["front"] == "das Haus")
    assert haus["back"] == "house" and haus["deck"] == "Vokabeln::A2" and "die Häuser" in haus["extra"]
    assert haus["progress"]["interval"] == 30 and haus["progress"]["ease"] == 2.3 and 9 <= haus["progress"]["due_in_days"] <= 11
    assert next(n for n in notes if n["front"] == "der Baum")["progress"] is None


def test_plain_text_export():
    raw = "#separator:tab\n#html:true\nder Tisch\ttable\nder Stuhl\tchair\tPlural: Stühle\n".encode()
    notes, _ = ankiimport.read_file("notes.txt", raw)
    assert [(n["front"], n["back"]) for n in notes] == [("der Tisch", "table"), ("der Stuhl", "chair")]
    assert notes[1]["extra"] == "Plural: Stühle"


def test_import_endpoints(client):
    r = client.post("/api/anki/import/preview", files={"file": ("new.apkg", _new_apkg())}).json()
    assert r["total"] == 2 and r["decks"][0]["learned"] == 1
    done = client.post("/api/anki/import", json={"token": r["token"], "decks": ["Vokabeln::A2"]}).json()
    assert done == {"added": 2, "skipped": 0, "learned": 1}
    haus = db.q1("SELECT * FROM cards WHERE front='das Haus'")
    assert haus["interval"] == 30 and haus["due"] > db.now() and "anki" in json.loads(haus["tags"])
    # importing the same file again skips what's already there
    r = client.post("/api/anki/import/preview", files={"file": ("new.apkg", _new_apkg())}).json()
    assert r["decks"][0]["duplicates"] == 2
    assert client.post("/api/anki/import", json={"token": r["token"]}).json()["skipped"] == 2
    bad = client.post("/api/anki/import/preview", files={"file": ("x.apkg", b"not a zip")})
    assert bad.status_code == 400


# ---------- packs ----------
def test_every_pack_builds():
    for pid, *_ in packs.PACKS:
        cards = packs.pack_cards(pid)
        assert len(cards) >= 20, pid
        assert all(c["front"] and c["back"] for c in cards), pid
        assert len({c["front"] for c in cards}) == len(cards), pid


@pytest.mark.parametrize("pack, front, back_or_extra", [
    ("topic-family", "die Mutter", "Plural: die Mütter"),
    ("verbs", "gehen", "er geht, ging, ist gegangen"),
    ("adjectives", "gut", "gut, besser, am besten"),
    ("irregular", "fahren · to drive, to go (by vehicle)", "er fährt, fuhr, hat/ist gefahren"),
])
def test_pack_cards_use_the_dictionary(pack, front, back_or_extra):
    c = next(c for c in packs.pack_cards(pack) if c["front"] == front)
    assert back_or_extra in (c["back"], c["extra"])


def test_irregular_pack_has_no_regular_verbs():
    fronts = {c["front"].split(" · ")[0] for c in packs.pack_cards("irregular")}
    assert {"gehen", "sein", "denken", "bringen"} <= fronts
    assert not {"machen", "sagen", "kaufen", "spielen"} & fronts


def test_pack_endpoints(client):
    lib = client.get("/api/packs").json()["packs"]
    fam = next(p for p in lib if p["id"] == "topic-family")
    r = client.post("/api/packs/topic-family/add").json()
    assert r["added"] == fam["count"] - fam["have"]
    assert client.post("/api/packs/topic-family/add").json()["added"] == 0
    lib = client.get("/api/packs").json()["packs"]
    assert next(p for p in lib if p["id"] == "topic-family")["added"] == r["added"]
    one = db.q1("SELECT id FROM cards WHERE front='die Mutter'")["id"]
    db.ex("UPDATE cards SET due=?, reps=1 WHERE id=?", (db.now(), one))
    assert client.post("/api/packs/topic-family/remove", json={"only_new": True}).json()["removed"] == r["added"] - 1
    assert db.q1("SELECT 1 FROM cards WHERE id=?", (one,))
    assert client.post("/api/packs/topic-family/remove", json={}).json()["removed"] == 1
    assert client.post("/api/packs/nope/add").status_code == 404


# ---------- quick plan ----------
def test_quick_plan(client):
    plan = client.post("/api/plan/quick", json={"minutes": 60}).json()
    assert plan["quick"] and plan["blocks"]
    assert abs(sum(b["minutes"] for b in plan["blocks"]) - 60) <= 10
    kinds = [b["kind"] for b in plan["blocks"]]
    assert "declensions" in kinds and "verbs" in kinds  # an hour: both grammar courses
    short = client.post("/api/plan/quick", json={"minutes": 15}).json()
    assert len([b for b in short["blocks"] if b["kind"] in ("declensions", "verbs") and not b.get("sub")]) == 1
    assert client.get("/api/plan/today").json()["id"] == short["id"]
