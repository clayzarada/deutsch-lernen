"""Cloud backup for Plus: upload, list, keep the newest few, restore, and remove everything on account deletion."""
import base64
import gzip
import json
import time

import httpx
import pytest

from app import account, cloud, db

UID = "0b6c2f4e-1111-4222-8333-944455556666"


def _jwt(sub):
    enc = lambda d: base64.urlsafe_b64encode(json.dumps(d).encode()).decode().rstrip("=")
    return f"{enc({'alg': 'none'})}.{enc({'sub': sub})}.sig"


class R:
    def __init__(self, status, body=None, content=b""):
        self.status_code, self._body, self.content = status, body, content
        self.text = json.dumps(body) if body is not None else ""

    def json(self):
        return self._body


@pytest.fixture
def storage(monkeypatch):
    """A pretend Supabase Storage bucket that keeps files in a dict, and enforces 'Plus to add'."""
    files, state = {}, {"plus": True}

    def post(url, headers=None, json=None, content=None, timeout=None, params=None):
        if "/storage/v1/object/list/backups" in url:
            names = sorted((k.split("/", 1)[1] for k in files if k.startswith(json["prefix"] + "/")), reverse=True)
            return R(200, [{"name": n, "metadata": {"size": len(files[f'{json["prefix"]}/{n}'])}} for n in names])
        if "/storage/v1/object/backups/" in url:
            if not state["plus"]:
                return R(403, {"message": "new row violates row-level security policy"})
            key = url.split("/storage/v1/object/backups/")[1]
            files[key] = content
            return R(200, {"Key": key})
        raise AssertionError(url)

    def get(url, headers=None, timeout=None):
        key = url.split("/authenticated/backups/")[1]
        return R(200, content=files[key]) if key in files else R(404, {"message": "not found"})

    def request(method, url, headers=None, json=None, timeout=None):
        assert method == "DELETE"
        for k in json["prefixes"]:
            files.pop(k, None)
        return R(200, [])

    monkeypatch.setattr(httpx, "post", post)
    monkeypatch.setattr(httpx, "get", get)
    monkeypatch.setattr(httpx, "request", request)
    account._save({"access_token": _jwt(UID), "refresh_token": "R", "expires_at": int(time.time()) + 3600, "email": "a@b.de"})
    yield files, state
    account._save(None)
    db.set_setting("cloud_backup", "")
    db.set_setting("cloud_backup_last", "")


def test_backup_list_prune_and_restore(client, storage):
    files, state = storage
    db.set_setting("level", "B1")
    made = []
    for i in range(cloud.KEEP + 2):
        name = f"2026111{i}-120000.db.gz"
        made.append(name)
        files[f"{UID}/{name}"] = b"old"
    r = client.post("/api/cloud/backup").json()
    assert r["made"] and r["last"]
    names = [b["name"] for b in r["backups"]]
    assert len(names) == cloud.KEEP and names[0] == r["made"]  # newest kept, oldest pruned
    assert gzip.decompress(files[f"{UID}/{r['made']}"])[:16] == b"SQLite format 3\x00"

    db.set_setting("level", "A1")  # change something, then restore the backup made above
    out = client.post("/api/cloud/restore", json={"name": r["made"]}).json()
    assert out["safety_copy"] and db.get_settings()["level"] == "B1"


def test_free_account_cannot_upload_but_bad_names_are_refused(client, storage):
    files, state = storage
    state["plus"] = False
    r = client.post("/api/cloud/backup")
    assert r.status_code == 400 and "Plus" in r.json()["detail"]
    assert client.post("/api/cloud/restore", json={"name": "../../etc/passwd"}).status_code == 400


def test_damaged_backup_is_not_used(client, storage):
    files, state = storage
    files[f"{UID}/20261116-120000.db.gz"] = b"not gzip"
    r = client.post("/api/cloud/restore", json={"name": "20261116-120000.db.gz"})
    assert r.status_code == 400 and "damaged" in r.json()["detail"]


def test_setting_and_due(client, storage):
    assert client.put("/api/cloud", json={"enabled": False}).json()["enabled"] is False
    assert cloud.due() is False
    db.set_setting("cloud_backup", "1")
    assert cloud.due() is True
    db.set_setting("cloud_backup_last", "2999-01-01T00:00:00")
    assert cloud.due() is False


def test_delete_all_removes_every_backup(storage):
    files, state = storage
    for i in range(3):
        files[f"{UID}/2026111{i}-120000.db.gz"] = b"x"
    assert cloud.delete_all() == 3 and not files


def test_signed_out_gets_a_clear_message(client):
    account._save(None)
    r = client.get("/api/cloud?full=true")
    assert r.status_code == 400 and "Sign in" in r.json()["detail"]
