"""Checks that run on GitHub for every change (and locally with: python -m pytest)."""
import io
import json
import re
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


# ---------- starting up ----------
def test_version_file():
    v = json.loads((ROOT / "version.json").read_text(encoding="utf-8"))
    assert re.fullmatch(r"\d+\.\d+\.\d+", v["version"])
    assert v["name"] and v["fingerprint"]


def test_app_starts_and_reports_its_version(client):
    assert client.get("/").status_code == 200
    v = json.loads((ROOT / "version.json").read_text(encoding="utf-8"))
    assert client.get("/api/version").json()["version"] == v["version"]


# Pages that call the AI or download something are left out: tests never use the network.
SKIP_GET = {"/api/backups/export", "/api/anki/export"}


def test_every_page_answers(client):
    """Every simple GET endpoint answers without a server error on a brand-new install."""
    from app.main import app
    bad = []
    for r in app.routes:
        path = getattr(r, "path", "")
        if "GET" not in getattr(r, "methods", ()) or "{" in path or not path.startswith("/api/") or path in SKIP_GET:
            continue
        res = client.get(path)
        if res.status_code >= 500 and res.status_code != 502:  # 502 = "add an API key first", expected here
            bad.append((path, res.status_code, res.text[:200]))
    assert not bad, bad


# ---------- the Grammar courses ----------
def _courses():
    from app import course
    from app.verbcourse import VERBS_COURSE
    return [course.DECL, VERBS_COURSE]


def _grader(which):
    from app import decl, verbs
    return (decl, verbs)[which].grade


@pytest.mark.parametrize("which", [0, 1], ids=["declensions", "verbs"])
def test_every_question_accepts_its_own_answer(client, which):
    """Every kind of question in every stage can be built, and its correct answer is marked right."""
    c = _courses()[which]
    grade = _grader(which)
    for stage in c.stages:
        for group in stage["pool"]:
            for key in group["keys"]:
                for _ in range(2):
                    q = c.engine.build(group["mode"], key)
                    assert q["answers"], (stage["id"], key)
                    assert grade(q, q["answers"][0], 1000)["correct"], (stage["id"], key, q["prompt"], q["answers"][0])


def test_stage_endpoints(client):
    for prefix, c in zip(("decl", "verbs"), _courses()):
        assert client.get(f"/api/{prefix}/journey").status_code == 200
        for stage in c.stages:
            sid = stage["id"]
            assert client.get(f"/api/{prefix}/stage/{sid}").status_code == 200
            q = client.post(f"/api/{prefix}/stage/{sid}/next", json={"mode": "checkpoint"}).json()
            r = client.post(f"/api/{prefix}/stage/{sid}/answer", json={"question": q, "answer": "xyz", "ms": 5000})
            assert r.status_code == 200 and "next" in r.json()


def test_sentences_never_give_reflexive_verbs_a_plain_object():
    """'Anna trifft sich heute alte Freunde' is wrong German: reflexive verbs stay out of object sentences."""
    from app import verbs
    for key in [k for k in verbs.KEYS if k.startswith("vb:") and ":" in k]:
        for _ in range(20):
            try:
                q = verbs.gen_vsent(key)
            except Exception:
                break  # a key that can't make sentences
            if q["family"] == "vsent":
                assert not (q.get("cue") or "").startswith("sich "), q["prompt"]


def test_word_order_solutions():
    from app import wordorder
    for sid, s in enumerate(wordorder.SENTENCES):
        order = list(range(s["lock"], len(s["chunks"])))
        assert wordorder.check(sid, order)["correct"], " ".join(s["chunks"])
        if len(order) > 1:
            wrong = order[::-1]
            if [s["chunks"][i] for i in wrong] != [s["chunks"][i] for i in order]:
                assert not wordorder.check(sid, wrong)["correct"] or s["alts"], " ".join(s["chunks"])


# ---------- backups ----------
def test_backup_file_round_trip(client):
    from app import db
    client.put("/api/settings", json={"goal": "before", "api_key": "sk-ant-not-a-real-key"})
    (db.BOOKS).mkdir(parents=True, exist_ok=True)
    (db.BOOKS / "mybook.pdf").write_bytes(b"%PDF-1.4 test")
    res = client.get("/api/backups/export")
    assert res.status_code == 200
    data = res.content
    names = zipfile.ZipFile(io.BytesIO(data)).namelist()
    assert {"manifest.json", "study.db", "books/mybook.pdf"} <= set(names)
    assert not any(n.endswith(".env") for n in names)
    assert b"sk-ant-not-a-real-key" not in data  # API keys never go into a backup file

    client.put("/api/settings", json={"goal": "after"})
    (db.BOOKS / "mybook.pdf").unlink()
    r = client.post("/api/backups/import", files={"file": ("b.zip", data, "application/zip")})
    assert r.status_code == 200, r.text
    assert db.get_settings()["goal"] == "before"
    assert (db.BOOKS / "mybook.pdf").read_bytes() == b"%PDF-1.4 test"
    assert any(b["kind"] == "before-restore" for b in client.get("/api/backups").json()["backups"])


def _zip(entries):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for n, d in entries.items():
            z.writestr(n, d)
    return buf.getvalue()


@pytest.mark.parametrize("data", [
    b"not a zip at all",
    _zip({"study.db": b"x"}),  # no manifest
    _zip({"manifest.json": json.dumps({"app": "deutsch-lernen"}), "study.db": b"x", "../evil.txt": b"x"}),
    _zip({"manifest.json": json.dumps({"app": "deutsch-lernen"}), "study.db": b"x", "books/../../evil.txt": b"x"}),
    _zip({"manifest.json": json.dumps({"app": "deutsch-lernen"}), "study.db": b"not a database"}),
], ids=["not-zip", "no-manifest", "climbs-out", "climbs-out-nested", "bad-db"])
def test_backup_file_rejects_bad_files(client, data):
    from app import db
    before = db.DB_PATH.read_bytes()
    r = client.post("/api/backups/import", files={"file": ("b.zip", data, "application/zip")})
    assert r.status_code == 400
    assert db.DB_PATH.read_bytes() == before
    assert not (db.DATA.parent / "evil.txt").exists()


# ---------- updates ----------
def test_update_picks_the_right_download(monkeypatch):
    from app import update
    monkeypatch.setattr(update, "_fetch", lambda: {"tag": "v99.0.0", "name": "", "notes": "", "published": "", "url": "",
                                                   "assets": {update.WINDOWS_ASSET: "w", update.MAC_ASSET: "m"}})
    monkeypatch.setattr(update.sys, "frozen", True, raising=False)
    for platform, kind in (("win32", "windows"), ("darwin", "mac"), ("linux", "manual")):
        monkeypatch.setattr(update.sys, "platform", platform)
        s = update.status(force=True)
        assert s["newer"] and s["install"] == kind
    monkeypatch.setattr(update.sys, "platform", "darwin")
    monkeypatch.setattr(update, "_fetch", lambda: {"tag": "v99.0.0", "name": "", "notes": "", "published": "", "url": "",
                                                   "assets": {update.WINDOWS_ASSET: "w"}})
    assert update.status(force=True)["install"] == "manual"  # no Mac app attached yet: send them to the website


def test_mac_update_helper_restores_the_old_app_on_failure():
    from app import update
    sh = update.MAC_HELPER.format(pid=1, app="/Applications/Deutsch lernen.app", new="/n/Deutsch lernen.app", log="/l", work="/w")
    assert 'mv "/Applications/Deutsch lernen.app.old" "/Applications/Deutsch lernen.app"' in sh
    assert sh.rstrip().endswith('rm -rf "/w"')
