"""Builds the downloadable Windows version: "Deutsch-lernen-Windows.zip" on the Desktop.

    .venv\\Scripts\\python make_windows_package.py

It contains "Deutsch lernen.exe" (built with PyInstaller from launch_windows.py) and a short read-me.
It never contains your data or your API keys: the packaged app keeps its own data in %APPDATA%\\Deutsch lernen.
The build uses its own environment (.build-venv-win), so your everyday .venv is left alone.
"""
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".build-venv-win"
PY = VENV / "Scripts" / "python.exe"
DIST = ROOT / "dist" / "Deutsch lernen"
OUT = Path.home() / "Desktop" / "Deutsch-lernen-Windows.zip"

README = """DEUTSCH LERNEN FOR WINDOWS  (version {version})
==========================
Made by {author}. {copyright}

A desktop app for learning German. Everything runs on your own computer.

START
 1. Unzip this whole folder somewhere you keep programs (for example Documents).
 2. Double-click "Deutsch lernen.exe".
    If Windows says "Windows protected your PC": click "More info", then "Run anyway".
    (The app isn't code-signed yet, so Windows doesn't recognise it.)
 3. Optional: right-click "Deutsch lernen.exe" > Show more options > Send to > Desktop (create shortcut).

FIRST STEPS IN THE APP
 - Settings: pick English or Türkçe under "App language", then set your level, daily minutes and goal.
 - Settings: paste your Claude API key to turn on the AI features (practice sets, marking, flashcards,
   the coach). The download page explains how to get one, step by step. A Google Gemini key is optional
   and only needed for listening episodes and pronunciation.
 - Library: import a textbook PDF.
 - Declensions: start the journey on the first planet. This works without any API key.

YOUR DATA
 Your books, progress and API keys are kept in %APPDATA%\\Deutsch lernen (paste that into the File
 Explorer address bar to open it). Installing a newer version never deletes them: just replace this folder.

LICENSE
 Personal, non-commercial use only. Copying, changing, redistributing or selling the app requires
 written permission from {owner}. See LICENSE.txt. {website}
"""

# Shown in the .exe's Properties > Details.
VERSION_INFO = """VSVersionInfo(
  ffi=FixedFileInfo(filevers=({v0}, {v1}, {v2}, 0), prodvers=({v0}, {v1}, {v2}, 0), mask=0x3f, flags=0x0,
                    OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[StringFileInfo([StringTable('040904B0', [
    StringStruct('CompanyName', {owner!r}),
    StringStruct('FileDescription', 'Deutsch lernen'),
    StringStruct('FileVersion', {version!r}),
    StringStruct('InternalName', 'Deutsch lernen'),
    StringStruct('LegalCopyright', {copyright!r}),
    StringStruct('OriginalFilename', 'Deutsch lernen.exe'),
    StringStruct('ProductName', 'Deutsch lernen'),
    StringStruct('ProductVersion', {version!r}),
    StringStruct('Comments', {comments!r})])]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])]
)
"""


def run(*cmd):
    print(">", " ".join(map(str, cmd)))
    subprocess.run(cmd, check=True, cwd=ROOT)


def main():
    # 1. The version, bumped first if the code changed since the app last ran (same rule as at startup).
    sys.path.insert(0, str(ROOT))
    from app.version import AUTHOR, COPYRIGHT, OWNER, VERSION, WEBSITE

    # 2. A separate build environment with the app's packages plus PyInstaller and pywebview.
    if not PY.exists():
        run(sys.executable, "-m", "venv", VENV)
    run(PY, "-m", "pip", "install", "--quiet", "--upgrade", "pip")
    run(PY, "-m", "pip", "install", "--quiet", "-r", "requirements.txt", "pyinstaller", "pywebview>=5")

    # 3. Build. --windowed: no console window. version.json goes in so the app knows its version.
    shutil.rmtree(DIST, ignore_errors=True)
    v = [int(x) for x in (VERSION.split(".") + ["0", "0"])[:3]]
    info = ROOT / "build" / "version_info.txt"
    info.parent.mkdir(exist_ok=True)
    info.write_text(VERSION_INFO.format(v0=v[0], v1=v[1], v2=v[2], owner=OWNER, version=VERSION, copyright=COPYRIGHT,
                                        comments=f"Made by {AUTHOR}"), encoding="utf-8")
    run(PY, "-m", "PyInstaller", "--noconfirm", "--clean", "--log-level", "WARN", "--windowed",
        "--name", "Deutsch lernen", "--icon", "static/icon.ico", "--version-file", info,
        "--add-data", "static;static", "--add-data", "version.json;.",
        "--hidden-import", "app.main", "--collect-submodules", "app",
        "--collect-submodules", "uvicorn", "--collect-all", "webview", "--collect-data", "genanki",
        "launch_windows.py")
    exe = DIST / "Deutsch lernen.exe"
    if not exe.exists():
        raise SystemExit("The build didn't produce Deutsch lernen.exe. Scroll up for the error.")

    # 4. Safety check: nothing personal may end up in the package.
    bad = [p for p in DIST.rglob("*") if p.name in (".env", "keys.env", "study.db", "app.log")]
    if bad:
        raise SystemExit(f"Refusing to package personal files: {bad}")

    # 5. Zip it with a read-me.
    top = "Deutsch lernen"
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(DIST.rglob("*")):
            if p.is_file():
                z.write(p, f"{top}/{p.relative_to(DIST).as_posix()}")
        z.writestr(f"{top}/READ ME.txt", README.format(version=VERSION, author=AUTHOR, copyright=COPYRIGHT, owner=OWNER,
                                                       website=WEBSITE).replace("\n", "\r\n"))
        z.write(ROOT / "LICENSE", f"{top}/LICENSE.txt")
    print(f"\nMade {OUT} ({OUT.stat().st_size / 1e6:.0f} MB), version {VERSION}")


if __name__ == "__main__":
    main()
