"""Windows app entry point for the downloadable version: "Deutsch lernen.exe" is built from this file
(see make_windows_package.py). Your own copy keeps using launch.pyw / start.bat as before.

Everything the learner creates (books, answers, flashcards, progress) and their API keys live in
%APPDATA%\\Deutsch lernen, so replacing the app with a newer version never touches them.

The app runs its local server and shows it in a Microsoft Edge "app window" (its own window, no tabs or address
bar). Edge is part of every Windows 10/11 install. Closing that window quits the app.

Why not pywebview: its Windows window needs .NET, and .NET refuses to load the app's DLLs when they were unzipped
from a downloaded zip (Windows marks such files as "from the internet"). That crashed every downloaded copy up to
0.1.5. Edge needs nothing extra. Fallbacks: Chrome in the same app mode, then the default browser.
"""
import os
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

SUPPORT = Path(os.environ.get("APPDATA", Path.home())) / "Deutsch lernen"
SUPPORT.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("GERMANSTUDY_DATA", str(SUPPORT / "data"))
os.environ.setdefault("GERMANSTUDY_ENV", str(SUPPORT / ".env"))
# A window-only app has no console, so keep a log for troubleshooting.
if getattr(sys, "frozen", False):
    sys.stdout = sys.stderr = open(SUPPORT / "app.log", "a", buffering=1, encoding="utf-8")

# Creating this file makes the app open in the default browser instead of its own window.
USE_BROWSER = SUPPORT / "use-browser"
PROFILE = SUPPORT / "window"  # the app window's own browser profile (theme, last page); separate from the learner's
BROWSERS = [
    r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe",
    r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe",
    r"%LocalAppData%\Microsoft\Edge\Application\msedge.exe",
    r"%ProgramFiles%\Google\Chrome\Application\chrome.exe",
    r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe",
    r"%LocalAppData%\Google\Chrome\Application\chrome.exe",
]


def free_port(start=8777):
    """8777 normally; the same port every time keeps the window's saved settings (theme, last page)."""
    for port in range(start, start + 40):
        with socket.socket() as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    raise SystemExit("No free local port for the app.")


def window_open():
    """Is a browser process using our profile still running? The browser hands its window to other processes,
    so we look for any process with our profile folder on its command line rather than the one we started."""
    import psutil
    needle = str(PROFILE).lower()
    for p in psutil.process_iter(["name", "cmdline"]):
        try:
            if p.info["name"] in ("msedge.exe", "chrome.exe") and needle in " ".join(p.info["cmdline"] or []).lower():
                return True
        except (psutil.Error, TypeError):
            pass
    return False


def open_app_window(url, wait=True):
    """Open the app in its own Edge/Chrome window and (unless wait=False) wait until it is closed.
    False if no such browser."""
    browser = next((p for p in map(os.path.expandvars, BROWSERS) if Path(p).exists()), None)
    if not browser:
        return False
    print("window:", browser)
    subprocess.Popen([browser, f"--app={url}", f"--user-data-dir={PROFILE}", "--no-first-run",
                      "--no-default-browser-check", "--disable-sync", "--window-size=1440,920"])
    if not wait:
        return True
    for _ in range(40):  # wait up to 20 s for the window to appear
        if window_open():
            break
        time.sleep(0.5)
    while window_open():
        time.sleep(2)
    return True


LOCK = SUPPORT / "running.txt"  # "pid port" of the copy that is running, so a second double-click reuses it


def already_running():
    """The port of a copy of the app that is already running, or None."""
    try:
        pid, port = LOCK.read_text().split()
        import psutil
        if not psutil.pid_exists(int(pid)) or int(pid) == os.getpid():
            return None
        for _ in range(60):  # the other copy may still be starting up: give it up to a minute
            try:
                with socket.create_connection(("127.0.0.1", int(port)), timeout=1):
                    return int(port)
            except OSError:
                if not psutil.pid_exists(int(pid)):
                    return None
                time.sleep(1)
    except (OSError, ValueError):
        pass
    return None


def main():
    print(f"--- starting {time.strftime('%Y-%m-%d %H:%M:%S')}")
    # Double-clicked while it's already open (or still starting up): show the running copy instead of a second one.
    port = already_running()
    if port:
        print("already running on", port)
        if USE_BROWSER.exists() or not open_app_window(f"http://127.0.0.1:{port}", wait=False):
            webbrowser.open(f"http://127.0.0.1:{port}")
        return
    port = free_port()
    try:
        LOCK.write_text(f"{os.getpid()} {port}")  # before the slow imports, so a second double-click finds us
    except OSError:
        pass
    import uvicorn
    from app.main import app
    from app.version import VERSION

    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(150):
        if server.started:
            break
        time.sleep(0.1)
    url = f"http://127.0.0.1:{port}"
    print(f"version {VERSION}, serving {url}")

    shown = False
    if not USE_BROWSER.exists():
        try:
            shown = open_app_window(url)
        except Exception as e:  # never let a window problem stop the app: fall back to the normal browser
            print("app window failed, using the default browser:", repr(e))
    if shown:
        server.should_exit = True
        thread.join(timeout=3)
    else:
        webbrowser.open(url)
        thread.join()  # keeps serving until the app is ended (sign-out, Task Manager)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()  # goes to app.log
        raise
