# Deutsch lernen: Mac copy

This folder is a finished, working German study app (Python FastAPI server + a browser front end in `static/`),
originally built and tested on Windows. It has been prepared for macOS. **The job here is only to get it built and
running on this Mac.** Please don't redesign, refactor or "improve" the app itself; keep changes to packaging and
small Mac-specific fixes. That keeps this session short.

## Build and install
Run `./build_mac.command` (it is also double-clickable in Finder). It:
1. finds Python 3.10+ (the macOS system Python 3.9 is too old; install from python.org or Homebrew if missing),
2. makes `.build-venv` and installs `requirements.txt` plus `pyinstaller` and `pywebview`,
3. builds `dist/Deutsch lernen.app` from `launch_mac.py` with PyInstaller,
4. copies `keys.env` (Claude and Gemini API keys) to `~/Library/Application Support/Deutsch lernen/.env` and deletes
   `keys.env`, then installs the app into /Applications and opens it.

Never print, echo or commit the contents of `keys.env` or the `.env` file.

## How the Mac version works
- `launch_mac.py` sets `GERMANSTUDY_DATA` and `GERMANSTUDY_ENV` to `~/Library/Application Support/Deutsch lernen/`,
  starts uvicorn on 127.0.0.1:8777 (or the next free port) in a thread, and shows it in a pywebview window.
- All user data (SQLite `study.db`, imported books, audio) lives in that Application Support folder, never in the
  app bundle. Rebuilding the app is always safe.
- Log file: `~/Library/Application Support/Deutsch lernen/app.log`. Check it first when something fails.
- Fallback: `touch ~/Library/Application\ Support/Deutsch\ lernen/use-browser` makes the app open in the default
  browser instead of its own window.

## If the build or app fails
- **Module not found** in app.log: add `--hidden-import <module>` (or `--collect-submodules <pkg>`) to the
  pyinstaller line in `build_mac.command` and rerun it.
- **App opens then closes**: run `"/Applications/Deutsch lernen.app/Contents/MacOS/Deutsch lernen"` in Terminal to
  see the error directly.
- **Downloads do nothing in the window** (Flashcards → Anki → Download, or the Reader's download button): check
  the pywebview version supports `ALLOW_DOWNLOADS`; if it can't be made to work, use the `use-browser` fallback.
- To test without building: `source .build-venv/bin/activate && python launch_mac.py`.

## Check after installing
1. The app opens in its own window and Settings shows both API keys as saved.
2. Library: import a PDF (e.g. from `Goethe practice exams/`), open it in the Reader, type an answer on the page.
3. Declensions: open the first planet and answer a few drill questions.
4. Flashcards → Anki → Download .apkg file saves a file.
5. Quit (Cmd+Q) and reopen: the imported book and progress are still there.
