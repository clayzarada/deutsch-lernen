#!/bin/bash
# Builds "Deutsch lernen.app" on this Mac and installs it in Applications.
# Double-click this file in Finder (or run it in Terminal). Safe to run again: it rebuilds the app and never
# touches the data in ~/Library/Application Support/Deutsch lernen.
set -euo pipefail
cd "$(dirname "$0")"

APP_NAME="Deutsch lernen"
SUPPORT="$HOME/Library/Application Support/$APP_NAME"

say() { printf '\n\033[1m%s\033[0m\n' "$*"; }
fail() { printf '\n\033[31m%s\033[0m\n' "$*"; read -r -p "Press Return to close." _ || true; exit 1; }

# ---- 1. Python 3.10 or newer (the one built into macOS is too old) ----
PY=""
for cand in python3.13 python3.12 python3.11 python3.10 \
            /Library/Frameworks/Python.framework/Versions/3.1[0-3]/bin/python3 \
            /opt/homebrew/bin/python3 /usr/local/bin/python3 python3; do
  if command -v "$cand" >/dev/null 2>&1 && "$cand" -c 'import sys; sys.exit(sys.version_info < (3, 10))' 2>/dev/null; then
    PY="$(command -v "$cand")"; break
  fi
done
if [ -z "$PY" ]; then
  open "https://www.python.org/downloads/macos/" || true
  fail "Python 3.10 or newer is needed. Download the latest macOS installer from python.org (the page just opened),
install it, then double-click this file again."
fi
say "Using $("$PY" --version) at $PY"

# ---- 2. A private build environment with everything the app needs ----
say "Installing the app's components (the first time takes a few minutes)..."
[ -d .build-venv ] || "$PY" -m venv .build-venv
source .build-venv/bin/activate
python -m pip install --quiet --upgrade pip
python -m pip install --quiet -r requirements.txt pyinstaller "pywebview>=5"

# ---- 3. App icon ----
say "Making the icon..."
rm -rf build/icon.iconset && mkdir -p build/icon.iconset
for s in 16 32 128 256 512; do
  sips -z $s $s static/icon.png --out "build/icon.iconset/icon_${s}x${s}.png" >/dev/null
  d=$((s * 2)); [ $d -gt 512 ] && d=512
  sips -z $d $d static/icon.png --out "build/icon.iconset/icon_${s}x${s}@2x.png" >/dev/null
done
iconutil -c icns build/icon.iconset -o build/icon.icns

# ---- 4. Build the app ----
say "Building $APP_NAME.app..."
rm -rf "dist/$APP_NAME.app"
pyinstaller --noconfirm --clean --log-level WARN --windowed \
  --name "$APP_NAME" --icon build/icon.icns --osx-bundle-identifier local.deutsch-lernen \
  --add-data "static:static" --add-data "version.json:." \
  --hidden-import app.main --collect-submodules app \
  --collect-submodules uvicorn --collect-all webview --collect-data genanki \
  launch_mac.py
[ -d "dist/$APP_NAME.app" ] || fail "The build didn't produce an app. Scroll up for the error."

# ---- 5. API keys (only the first time; later changes are made in the app's Settings) ----
mkdir -p "$SUPPORT"
if [ -f keys.env ]; then
  if [ -f "$SUPPORT/.env" ]; then
    say "API keys were already set up, keeping them."
  else
    cp keys.env "$SUPPORT/.env" && chmod 600 "$SUPPORT/.env"
    say "API keys installed."
  fi
  rm -f keys.env  # don't leave a copy of the keys lying around in this folder
fi

# ---- 6. Install and open ----
DEST="/Applications"
[ -w "$DEST" ] || { DEST="$HOME/Applications"; mkdir -p "$DEST"; }
rm -rf "$DEST/$APP_NAME.app"
cp -R "dist/$APP_NAME.app" "$DEST/"
xattr -dr com.apple.quarantine "$DEST/$APP_NAME.app" 2>/dev/null || true
say "Done! $APP_NAME is in $DEST. Opening it now..."
open "$DEST/$APP_NAME.app"
echo "Tip: drag it from $DEST to the Dock to keep it there. You can close this window."
