"""Start the app and open it in your browser."""
import threading
import webbrowser

import uvicorn

URL = "http://127.0.0.1:8777"

if __name__ == "__main__":
    threading.Timer(1.5, lambda: webbrowser.open(URL)).start()
    print(f"German Study is running at {URL}  (close this window to stop it)")
    uvicorn.run("app.main:app", host="127.0.0.1", port=8777, log_level="warning")
