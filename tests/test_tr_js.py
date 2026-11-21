"""The Turkish dictionary must load as a JavaScript module: if it doesn't, the whole app fails to start.

`node --check` isn't enough (it parses the file as a plain script), so this imports it the way the browser does.
Skipped when Node.js isn't installed.
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
TR = HERE.parent / "static" / "i18n" / "tr.js"


@pytest.mark.skipif(not shutil.which("node"), reason="Node.js not installed")
def test_tr_js_loads_as_a_module_without_new_duplicate_keys():
    r = subprocess.run(["node", str(HERE / "check_tr.mjs"), str(TR)], capture_output=True, text=True,
                       encoding="utf-8", timeout=60)
    assert r.returncode == 0, r.stderr
    out = json.loads(r.stdout.strip().splitlines()[-1])
    assert out["n"] > 1000
    # The same key twice is harmless only while both say the same thing; keep the list from growing.
    assert set(out["dupes"]) <= {"'Word order'", "'Verbs'", "'Both'", "'AI-written'"}, out["dupes"]
