"""Updates: tells the learner when a newer version is out, and installs it with one click.

Checking: at most once a day (and only when asked by the page, after it has loaded) the app asks GitHub for the
newest release: one small request that gives up after a few seconds. The answer is cached in the settings table.
Offline or any error: nothing is shown, nothing breaks.

Installing depends on how the app was installed:
- "windows": the downloaded Windows app (PyInstaller). The new zip is downloaded and unpacked next to the learner's
  data, then a small helper script waits for the app to quit, swaps the new files into the app folder and opens it
  again. The learner's data lives in %APPDATA%\\Deutsch lernen, outside the app folder, so it is never touched.
  (Files the app downloads itself don't get Windows' "from the internet" mark, so the new version starts fast.)
- "git": a copy run from its source folder that is a git checkout (the owner's own copy). The new code is pulled
  from GitHub; the learner reopens the app to load it.
- "mac": the Mac app. GitHub builds a ready-made app for every release (.github/workflows/mac-app.yml); it is
  downloaded and unpacked next to the learner's data, then a small helper script waits for the app to quit, swaps
  the new app into place and opens it. Data lives in ~/Library/Application Support/Deutsch lernen, never touched.
- "manual": anything else. The banner links to the download page instead.
"""
import datetime as dt
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.request
import zipfile
from pathlib import Path

from . import db
from .db import ROOT
from .version import VERSION

REPO = "clayzarada/deutsch-lernen"
# GERMANSTUDY_UPDATE_API lets a test point the app at a fake release; normal use never sets it.
API = os.environ.get("GERMANSTUDY_UPDATE_API") or f"https://api.github.com/repos/{REPO}/releases/latest"
DOWNLOAD_PAGE = "https://zaradaholdingsgroup.com/lab/"
WINDOWS_ASSET = "Deutsch-lernen-Windows.zip"
MAC_ASSET = f"Deutsch-lernen-Mac-app-{'arm64' if platform.machine() == 'arm64' else 'x86_64'}.zip"
CHECK_EVERY = dt.timedelta(hours=24)
TIMEOUT_S = 4
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def _parse(v):
    """'v0.1.10' -> (0, 1, 10), so 0.1.10 counts as newer than 0.1.9."""
    nums = [int(x) for x in re.findall(r"\d+", v or "")[:3]]
    return tuple(nums + [0] * (3 - len(nums)))


def _get(url, timeout=TIMEOUT_S):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": f"deutsch-lernen/{VERSION}"})
    return urllib.request.urlopen(req, timeout=timeout)


def _fetch():
    with _get(API) as r:
        j = json.load(r)
    return {"tag": j.get("tag_name", ""), "name": j.get("name", ""), "notes": (j.get("body") or "")[:2000],
            "published": j.get("published_at", ""), "url": j.get("html_url", ""),
            "assets": {a["name"]: a["browser_download_url"] for a in j.get("assets", []) if a.get("name")}}


def install_kind():
    if getattr(sys, "frozen", False):
        return {"win32": "windows", "darwin": "mac"}.get(sys.platform, "manual")
    if (ROOT / ".git").exists() and shutil.which("git"):
        return "git"
    return "manual"


def status(force=False):
    s = db.get_settings()
    cached = None
    try:
        cached = json.loads(s.get("update_cache") or "null")
    except ValueError:
        pass
    now = dt.datetime.now()
    fresh = cached and "assets" in cached and now - dt.datetime.fromisoformat(cached["checked_at"]) < CHECK_EVERY
    if force or not fresh:
        try:
            cached = {**_fetch(), "checked_at": now.isoformat(timespec="seconds")}
            db.set_setting("update_cache", json.dumps(cached))
        except Exception as e:  # offline, GitHub slow or down: try again next time, say nothing
            print("update check failed:", e)
            if force:
                return {"current": VERSION, "ok": False}
    if not cached:
        return {"current": VERSION, "ok": False}
    latest = cached["tag"].lstrip("v")
    kind = install_kind()
    assets = cached.get("assets", {})
    can = kind == "git" or (kind == "windows" and WINDOWS_ASSET in assets) or (kind == "mac" and MAC_ASSET in assets)
    return {"current": VERSION, "ok": True, "latest": latest, "newer": _parse(latest) > _parse(VERSION),
            "notes": cached["notes"], "published": cached["published"], "download": DOWNLOAD_PAGE,
            "checked_at": cached["checked_at"], "install": kind if can else "manual"}


# ---------- installing ----------
JOB = {"stage": "idle"}  # idle, downloading, unpacking, pulling, ready, done, restarting, error (+ pct, message)
_lock = threading.Lock()


def _set(**kw):
    JOB.clear()
    JOB.update(kw)


def progress():
    return dict(JOB)


def start_install():
    """Start installing the newest release in the background. Progress: progress()."""
    with _lock:
        if JOB.get("stage") in ("downloading", "unpacking", "pulling", "ready", "restarting"):
            return progress()
        u = status()
        if not u.get("ok") or not u.get("newer"):
            _set(stage="error", message="There's no newer version to install.")
            return progress()
        kind = u["install"]
        if kind == "manual":
            _set(stage="error", message="This copy can't update itself. Download the new version instead.")
            return progress()
        _set(stage="pulling" if kind == "git" else "downloading", pct=0, latest=u["latest"])
    target = {"windows": _install_windows, "mac": _install_mac}.get(kind, _install_git)
    threading.Thread(target=target, args=(u["latest"],), daemon=True).start()
    return progress()


def _work_dir():
    return Path(os.environ.get("GERMANSTUDY_DATA", ROOT / "data")).parent / "update"


def _install_windows(latest):
    try:
        cache = json.loads(db.get_settings().get("update_cache") or "{}")
        url = cache["assets"][WINDOWS_ASSET]
        work = _work_dir()
        shutil.rmtree(work, ignore_errors=True)
        work.mkdir(parents=True)
        zpath = work / WINDOWS_ASSET
        with _get(url, timeout=30) as r, open(zpath, "wb") as f:
            total = int(r.headers.get("Content-Length") or 0)
            done = 0
            while chunk := r.read(1 << 16):
                f.write(chunk)
                done += len(chunk)
                if total:
                    JOB["pct"] = round(100 * done / total)
        JOB.update(stage="unpacking", pct=100)
        staging = work / "staging"
        with zipfile.ZipFile(zpath) as z:
            z.extractall(staging)
        if not (staging / "Deutsch lernen" / "Deutsch lernen.exe").exists():
            raise RuntimeError("the download doesn't contain the app")
        zpath.unlink()
        _set(stage="ready", latest=latest, message=f"Version {latest} is ready. The app restarts to finish.")
    except Exception as e:
        print("update failed:", repr(e))
        _set(stage="error", message=f"The update couldn't be downloaded ({e}). Try again later, or download it from the website.")


def _download(asset, work):
    cache = json.loads(db.get_settings().get("update_cache") or "{}")
    url = cache["assets"][asset]
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    zpath = work / asset
    with _get(url, timeout=30) as r, open(zpath, "wb") as f:
        total = int(r.headers.get("Content-Length") or 0)
        done = 0
        while chunk := r.read(1 << 16):
            f.write(chunk)
            done += len(chunk)
            if total:
                JOB["pct"] = round(100 * done / total)
    JOB.update(stage="unpacking", pct=100)
    return zpath


def _install_mac(latest):
    try:
        work = _work_dir()
        zpath = _download(MAC_ASSET, work)
        staging = work / "staging"
        # ditto keeps the app's symlinks and permissions, which Python's zipfile would lose
        r = subprocess.run(["ditto", "-x", "-k", str(zpath), str(staging)], capture_output=True, text=True, timeout=300)
        if r.returncode or not (staging / "Deutsch lernen.app" / "Contents" / "MacOS").exists():
            raise RuntimeError("the download doesn't contain the app")
        zpath.unlink()
        _set(stage="ready", latest=latest, message=f"Version {latest} is ready. The app restarts to finish.")
    except Exception as e:
        print("update failed:", repr(e))
        _set(stage="error", message=f"The update couldn't be downloaded ({e}). Try again later, or download it from the website.")


def _git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, timeout=120, creationflags=NO_WINDOW)


def _install_git(latest):
    try:
        req_before = hashlib.sha256((ROOT / "requirements.txt").read_bytes()).hexdigest()
        _git("checkout", "--", "version.json")  # the local version stamp would block the pull; the release has its own
        r = _git("pull", "--ff-only")
        if r.returncode:
            lines = (r.stderr or r.stdout or "git pull failed").strip().splitlines()
            raise RuntimeError(lines[-1] if lines else "git pull failed")
        if hashlib.sha256((ROOT / "requirements.txt").read_bytes()).hexdigest() != req_before:
            JOB.update(message="Installing new components...")
            subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "-r", str(ROOT / "requirements.txt")],
                           capture_output=True, timeout=600, creationflags=NO_WINDOW)
        _set(stage="done", latest=latest, message=f"Updated to {latest}. Close the app window and open it again to finish.")
    except Exception as e:
        print("update failed:", repr(e))
        _set(stage="error", message=f"The update couldn't be installed: {e}")


HELPER = r"""@echo off
rem Deutsch lernen updater: waits for the app to quit, swaps in the new version, opens it again.
set "PID={pid}"
:wait
tasklist /FI "PID eq %PID%" 2>nul | find "%PID%" >nul && (timeout /t 1 /nobreak >nul & goto wait)
rmdir /s /q "{app}\_internal"
robocopy "{new}" "{app}" /E /R:10 /W:1 /NFL /NDL /NJH /NJS /NP >> "{log}"
if %ERRORLEVEL% GEQ 8 echo robocopy failed with %ERRORLEVEL% >> "{log}"
start "" "{app}\Deutsch lernen.exe"
rmdir /s /q "{work}"
"""


MAC_HELPER = """#!/bin/sh
# Deutsch lernen updater: waits for the app to quit, swaps in the new version, opens it again.
while kill -0 {pid} 2>/dev/null; do sleep 1; done
xattr -dr com.apple.quarantine "{new}" 2>/dev/null
rm -rf "{app}.old"
if mv "{app}" "{app}.old" && ditto "{new}" "{app}"; then
  rm -rf "{app}.old"
else
  echo "update: couldn't replace the app" >> "{log}"
  rm -rf "{app}"; mv "{app}.old" "{app}"
fi
open "{app}"
rm -rf "{work}"
"""


def mac_app_path():
    """…/Deutsch lernen.app, from …/Deutsch lernen.app/Contents/MacOS/Deutsch lernen."""
    return Path(sys.executable).resolve().parents[2]


def _restart_mac():
    work = _work_dir()
    helper = work.parent / "finish-update.sh"
    helper.write_text(MAC_HELPER.format(pid=os.getpid(), app=mac_app_path(), new=work / "staging" / "Deutsch lernen.app",
                                        log=work.parent / "app.log", work=work), encoding="utf-8")
    subprocess.Popen(["/bin/sh", str(helper)], start_new_session=True, close_fds=True, cwd=str(work.parent),
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    _set(stage="restarting")

    def quit_soon():
        time.sleep(1.5)  # let the page get its answer first
        os._exit(0)
    threading.Thread(target=quit_soon, daemon=True).start()
    return {"ok": True}


def restart_to_finish():
    """Hand over to the helper script, close the app window and quit."""
    if JOB.get("stage") != "ready" or install_kind() not in ("windows", "mac"):
        return {"ok": False}
    if install_kind() == "mac":
        return _restart_mac()
    work = _work_dir()
    app_dir = Path(sys.executable).parent
    helper = work.parent / "finish-update.cmd"
    helper.write_text(HELPER.format(pid=os.getpid(), app=app_dir, new=work / "staging" / "Deutsch lernen",
                                    log=work.parent / "app.log", work=work), encoding="mbcs")
    subprocess.Popen(["cmd", "/c", str(helper)], creationflags=NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP,
                     close_fds=True, cwd=str(work.parent))
    _set(stage="restarting")

    def quit_soon():
        time.sleep(1.5)  # let the page get its answer first
        _close_app_window()
        time.sleep(3)
        os._exit(0)
    threading.Thread(target=quit_soon, daemon=True).start()
    return {"ok": True}


def _close_app_window():
    try:
        import psutil
        profile = str(Path(os.environ.get("GERMANSTUDY_DATA", ROOT / "data")).parent / "window").lower()
        for p in psutil.process_iter(["name", "cmdline"]):
            try:
                if p.info["name"] in ("msedge.exe", "chrome.exe") and profile in " ".join(p.info["cmdline"] or []).lower():
                    p.kill()
            except (psutil.Error, TypeError):
                pass
    except Exception as e:
        print("couldn't close the app window:", e)
