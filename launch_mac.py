"""Mac app entry point: "Deutsch lernen.app" is built from this file (see build_mac.command).

Everything the learner creates (books, answers, flashcards, progress) and the API keys live in
~/Library/Application Support/Deutsch lernen, so rebuilding or replacing the app never touches them.
The app runs its local server and shows it in a native window; closing the window quits the app.
"""
import os
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

SUPPORT = Path.home() / "Library" / "Application Support" / "Deutsch lernen"
SUPPORT.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("GERMANSTUDY_DATA", str(SUPPORT / "data"))
os.environ.setdefault("GERMANSTUDY_ENV", str(SUPPORT / ".env"))
# A window-only app has no console, so keep a log for troubleshooting.
if getattr(sys, "frozen", False):
    sys.stdout = sys.stderr = open(SUPPORT / "app.log", "a", buffering=1, encoding="utf-8")

# Creating this file makes the app open in the default browser instead of its own window
# (a fallback if the built-in window ever misbehaves).
USE_BROWSER = SUPPORT / "use-browser"


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


def main():
    print(f"--- starting {time.strftime('%Y-%m-%d %H:%M:%S')}")
    import uvicorn
    from app.main import app

    port = free_port()
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(150):
        if server.started:
            break
        time.sleep(0.1)
    url = f"http://127.0.0.1:{port}"

    webview = None
    if not USE_BROWSER.exists():
        try:
            import webview
        except ImportError:
            print("pywebview is missing, opening the browser instead")
    if webview:
        webview.settings["ALLOW_DOWNLOADS"] = True  # Anki export and "PDF with my answers"
        webview.settings["OPEN_EXTERNAL_LINKS_IN_BROWSER"] = True  # videos and resources open in Safari/Chrome
        webview.create_window("Deutsch lernen", url, width=1440, height=920, min_size=(900, 600))
        webview.start(private_mode=False, storage_path=str(SUPPORT / "window"))
        server.should_exit = True
        thread.join(timeout=3)
    else:
        webbrowser.open(url)
        thread.join()  # keeps running until the app is quit from the Dock


if __name__ == "__main__":
    main()
