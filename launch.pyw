"""Desktop-shortcut launcher: starts the app quietly (no console window) and opens it in its own window.

Closing the window stops the app. If the app is already running (e.g. from start.bat), it just opens a window.
"""
import ctypes
import json
import os
import socket
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

import psutil

ROOT = Path(__file__).resolve().parent
PORT = int(os.environ.get("GERMANSTUDY_PORT", 8777))  # tests set another port; normal use never does
URL = f"http://127.0.0.1:{PORT}"
BROWSERS = [
    r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe",
    r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe",
    r"%ProgramFiles%\Google\Chrome\Application\chrome.exe",
    r"%LocalAppData%\Google\Chrome\Application\chrome.exe",
]


def server_up():
    try:
        socket.create_connection(("127.0.0.1", PORT), timeout=0.5).close()
        return True
    except OSError:
        return False


def error(msg):
    ctypes.windll.user32.MessageBoxW(None, msg, "Deutsch lernen", 0x10)


def stop_tree(proc):
    """Stop a process and everything it started. A venv's python.exe is a small starter that runs the real
    interpreter as a child, so stopping only the starter could leave the server running (and holding the port)."""
    try:
        p = psutil.Process(proc.pid)
        for c in p.children(recursive=True):
            c.terminate()
        p.terminate()
        psutil.wait_procs([*p.children(recursive=True), p], timeout=5)
    except psutil.Error:
        pass


def disk_version():
    """The version of the code in this folder (after an update, newer than a server that is still running)."""
    try:
        return json.loads((ROOT / "version.json").read_text(encoding="utf-8"))["version"]
    except (OSError, ValueError, KeyError):
        return None


def running_version():
    """The version the server on PORT reports, or None if it doesn't answer like this app."""
    try:
        with urllib.request.urlopen(f"{URL}/api/version", timeout=2) as r:
            return json.load(r).get("version")
    except (OSError, ValueError):
        return None


def stop_old_server():
    """Stop this app's own server holding PORT (never anything else), and wait until the port is free."""
    for c in psutil.net_connections(kind="tcp"):
        if c.laddr and c.laddr.port == PORT and c.status == psutil.CONN_LISTEN and c.pid:
            try:
                p = psutil.Process(c.pid)
                if "app.main:app" in " ".join(p.cmdline()):
                    parent = p.parent()
                    p.terminate()
                    p.wait(5)
                    if parent and "app.main:app" in " ".join(parent.cmdline()):  # its venv starter, if any
                        parent.terminate()
            except (psutil.Error, psutil.TimeoutExpired):
                pass
    for _ in range(40):
        if not server_up():
            return
        time.sleep(0.25)


def start_server():
    (ROOT / "data").mkdir(exist_ok=True)
    log = open(ROOT / "data" / "app.log", "a")
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(PORT),
         "--log-level", "warning"],
        cwd=ROOT, stdout=log, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW)
    for _ in range(80):
        if server_up() and server.poll() is None:
            return server
        if server.poll() is not None:
            # Opened twice at once: the other launch's server got the port first. Use it if it's this version.
            if server_up() and running_version() == disk_version():
                return None
            break
        time.sleep(0.25)
    stop_tree(server)
    error("The app couldn't start. Try double-clicking start.bat in the GermanStudy folder to see what's wrong.\n\n"
          f"Details are in {ROOT / 'data' / 'app.log'}")
    sys.exit(1)


def main():
    server = None
    if server_up():
        # A server is already running. After an update it can still be the old version, which doesn't know the
        # new pages ("Not Found"), so replace it when its version doesn't match the files on disk.
        if running_version() != disk_version():
            stop_old_server()
            server = start_server()
    else:
        server = start_server()
    browser = next((p for p in map(os.path.expandvars, BROWSERS) if Path(p).exists()), None)
    if not browser:
        webbrowser.open(URL)  # no Edge/Chrome: use the normal browser and leave the app running
        return
    # A separate browser profile makes this its own app window, so we can tell when it's closed.
    profile = str(ROOT / "data" / "window-profile")
    subprocess.Popen([
        browser, f"--app={URL}", f"--user-data-dir={profile}",
        "--no-first-run", "--no-default-browser-check", "--window-size=1440,920",
    ])
    # The browser hands the window to other processes, so watch for those rather than the one we started.
    time.sleep(5)
    while window_open(profile):
        time.sleep(2)
    if server:
        stop_tree(server)


def window_open(profile):
    for p in psutil.process_iter(["name", "cmdline"]):
        try:
            if p.info["name"] in ("msedge.exe", "chrome.exe") and profile in " ".join(p.info["cmdline"] or []):
                return True
        except (psutil.Error, TypeError):
            pass
    return False


if __name__ == "__main__":
    main()
