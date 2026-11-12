"""The app's version number, kept in version.json next to the code.

Every time the app starts from source, it fingerprints its own code (app/, static/ and the launchers). If the
fingerprint differs from the one saved last time, the code was changed, so the last number goes up
(0.1.0 -> 0.1.1). That way the version moves with every change made on this PC, published or not.

For a bigger step, edit "version" in version.json by hand (e.g. to "0.2.0"); the next start keeps it and
just records the new fingerprint.

The packaged app (PyInstaller) never bumps: it only reads the version.json it was built with.
"""
import hashlib
import json
import sys

from .db import ROOT

FILE = ROOT / "version.json"
WATCHED_DIRS = ("app", "static")
WATCHED_FILES = ("launch.pyw", "launch_mac.py", "run.py", "start.bat", "requirements.txt",
                 "build_mac.command", "make_mac_package.py", "make_windows_package.py", "launch_windows.py")
SKIP_PARTS = {"__pycache__", "vendor"}  # vendor = third-party files we never edit


def _fingerprint():
    h = hashlib.sha256()
    paths = [p for d in WATCHED_DIRS for p in (ROOT / d).rglob("*")
             if p.is_file() and not SKIP_PARTS & set(p.relative_to(ROOT).parts) and p.suffix != ".pyc"]
    paths += [ROOT / f for f in WATCHED_FILES if (ROOT / f).is_file()]
    for p in sorted(paths):
        h.update(p.relative_to(ROOT).as_posix().encode())
        # Normalise line endings so a git checkout on another system doesn't count as a change.
        h.update(p.read_bytes().replace(b"\r\n", b"\n"))
    return h.hexdigest()


def _read():
    try:
        return json.loads(FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"version": "0.1.0", "fingerprint": ""}


def _bump(v):
    parts = (v.split(".") + ["0", "0"])[:3]
    parts[2] = str(int(parts[2]) + 1)
    return ".".join(parts)


def check():
    """Return the current version, bumping it first if the code changed since the last start."""
    data = _read()
    if getattr(sys, "frozen", False):
        return data["version"]
    fp = _fingerprint()
    if fp != data.get("fingerprint"):
        if data.get("fingerprint"):  # first ever run just records the fingerprint
            data["version"] = _bump(data["version"])
        data["fingerprint"] = fp
        try:
            FILE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        except OSError as e:  # never stop the app over this
            print("could not save version.json:", e)
    return data["version"]


VERSION = check()
