"""The Turkish dictionary must load as a JavaScript module: if it doesn't, the whole app fails to start.

`node --check` isn't enough (it parses the file as a plain script), so this imports it the way the browser does.
Skipped when Node.js isn't installed.
"""
import shutil
import subprocess
from pathlib import Path

import pytest

TR = Path(__file__).resolve().parent.parent / "static" / "i18n" / "tr.js"


@pytest.mark.skipif(not shutil.which("node"), reason="Node.js not installed")
def test_tr_js_loads_as_a_module_without_duplicate_keys():
    script = (
        "const fs = require('fs');"
        f"const src = fs.readFileSync({str(TR)!r}, 'utf8');"
        "const re = /^\\s*('(?:[^'\\\\]|\\\\.)*'|\"(?:[^\"\\\\]|\\\\.)*\")\\s*:/gm;"
        "const seen = new Map(); for (const m of src.matchAll(re)) seen.set(m[1], (seen.get(m[1]) || 0) + 1);"
        f"import({TR.as_uri()!r}).then(m => console.log(JSON.stringify({{"
        "n: Object.keys(m.default).length, dupes: [...seen].filter(([, n]) => n > 1).map(([k]) => k)}))));"
    )
    r = subprocess.run(["node", "-e", script], capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert r.returncode == 0, r.stderr
    import json
    out = json.loads(r.stdout.strip().splitlines()[-1])
    assert out["n"] > 1000
    # The same key twice is harmless only if both say the same thing; keep the list from growing.
    assert set(out["dupes"]) <= {"'Word order'", "'Verbs'", "'Both'", "'AI-written'"}, out["dupes"]
