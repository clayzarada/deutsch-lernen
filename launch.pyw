"""Desktop-shortcut launcher: starts the app quietly (no console window) and opens it in its own window.

Closing the window stops the app. If the app is already running (e.g. from start.bat), it just opens a window.
"""
import ctypes
import os
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

import psutil

ROOT = Path(__file__).resolve().parent
PORT = 8777
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


def start_server():
    (ROOT / "data").mkdir(exist_ok=True)
    log = open(ROOT / "data" / "app.log", "a")
    server = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(PORT),
         "--log-level", "warning"],
        cwd=ROOT, stdout=log, stderr=log, creationflags=subprocess.CREATE_NO_WINDOW)
    for _ in range(80):
        if server_up():
            return server
        if server.poll() is not None:
            break
        time.sleep(0.25)
    server.kill()
    error("The app couldn't start. Try double-clicking start.bat in the GermanStudy folder to see what's wrong.\n\n"
          f"Details are in {ROOT / 'data' / 'app.log'}")
    sys.exit(1)


def main():
    server = None if server_up() else start_server()
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
        server.terminate()


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
