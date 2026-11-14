"""Makes "Deutsch lernen for Mac.zip" on the Desktop: the app's code and the Mac installer, without any of your
own data (books, progress, cards) and WITHOUT your API keys, so the zip is safe to share or publish.

    .venv\\Scripts\\python make_mac_package.py               public build: no keys, no Goethe PDFs
    .venv\\Scripts\\python make_mac_package.py --personal    for your own Mac: includes your keys and the Goethe PDFs
"""
import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# PACKAGE_OUT_DIR: where the zip goes (GitHub's release build sets it; on a PC it's the Desktop).
OUT = Path(os.environ.get("PACKAGE_OUT_DIR") or Path.home() / "Desktop") / "Deutsch lernen for Mac.zip"
TOP = "Deutsch lernen for Mac"
SKIP_DIRS = {"__pycache__"}
SKIP_FILES = {"icon.ico"}


def add(z, src, arc, executable=False):
    info = zipfile.ZipInfo.from_file(src, f"{TOP}/{arc}")
    info.compress_type = zipfile.ZIP_DEFLATED
    # Unix permissions so the installer stays double-clickable after unzipping on the Mac.
    info.external_attr = ((0o755 if executable else 0o644) | 0o100000) << 16
    info.create_system = 3
    with open(src, "rb") as f:
        z.writestr(info, f.read())


def add_tree(z, folder, arc_prefix):
    for p in sorted(folder.rglob("*")):
        if p.is_file() and not SKIP_DIRS & set(p.parts) and p.name not in SKIP_FILES:
            add(z, p, f"{arc_prefix}/{p.relative_to(folder).as_posix()}")


def main():
    personal = "--personal" in sys.argv
    env = ROOT / ".env"
    keys = [] if not personal else [line for line in (env.read_text().splitlines() if env.exists() else [])
            if line.split("=", 1)[0].strip() in ("ANTHROPIC_API_KEY", "GEMINI_API_KEY") and "=" in line]
    out = OUT if personal else OUT.with_name("Deutsch-lernen-Mac.zip")  # the public name matches the download page
    with zipfile.ZipFile(out, "w") as z:
        add_tree(z, ROOT / "app", "app")
        add_tree(z, ROOT / "static", "static")
        for name in ("requirements.txt", "launch_mac.py", "README.md", "version.json", "LICENSE"):
            add(z, ROOT / name, name)
        add(z, ROOT / "build_mac.command", "build_mac.command", executable=True)
        add(z, ROOT / "mac" / "CLAUDE.md", "CLAUDE.md")
        add(z, ROOT / "mac" / ("START HERE.txt" if personal else "START HERE public.txt"), "START HERE.txt")
        goethe = ROOT / "downloads" / "goethe"
        if personal and goethe.exists():  # official exam PDFs: fine for you, not ours to redistribute
            add_tree(z, goethe, "Goethe practice exams")
        if keys:
            info = zipfile.ZipInfo(f"{TOP}/keys.env")
            info.external_attr = (0o600 | 0o100000) << 16
            info.create_system = 3
            z.writestr(info, "\n".join(keys) + "\n")
    names = zipfile.ZipFile(out).namelist()
    print(f"Made {out} ({out.stat().st_size / 1e6:.1f} MB, {len(names)} files, keys included: {[k.split('=')[0] for k in keys] or 'none'})")


if __name__ == "__main__":
    main()
