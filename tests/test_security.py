"""The local server only serves this computer's own pages, and backups can't smuggle in dangerous settings."""
import json

from app import backup, db


def test_other_websites_cannot_post(client):
    assert client.post("/api/backups", headers={"origin": "https://evil.example"}).status_code == 403
    assert client.post("/api/backups", headers={"origin": "null"}).status_code == 403
    assert client.post("/api/backups", headers={"referer": "https://evil.example/page"}).status_code == 403
    # the app's own window, and tools without a browser, still work
    assert client.post("/api/backups", headers={"origin": "http://testserver"}).status_code == 200
    assert client.post("/api/backups").status_code == 200


def test_foreign_host_is_refused(client):
    assert client.get("/api/settings", headers={"host": "attacker.example:8777"}).status_code == 403
    assert client.get("/api/settings", headers={"host": "127.0.0.1:8777"}).status_code == 200


def test_restore_forgets_update_cache_and_bad_file_names(client):
    db.set_setting("update_cache", json.dumps({"tag": "v999", "assets": {"x.zip": "https://evil/x.zip"}}))
    bid = db.ex("INSERT INTO books(title, filename) VALUES(?, ?)", ("Evil", "../../secret.txt"))
    ok = db.ex("INSERT INTO books(title, filename) VALUES(?, ?)", ("Fine", "0123abcd.pdf"))
    backup.scrub()
    assert not db.get_settings().get("update_cache")
    names = {r["id"]: r["filename"] for r in db.q("SELECT id, filename FROM books")}
    assert names[bid] == "" and names[ok] == "0123abcd.pdf"
    db.ex("DELETE FROM books WHERE id IN (?, ?)", (bid, ok))
