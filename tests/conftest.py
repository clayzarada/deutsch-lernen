"""Every test run uses its own empty data folder and never talks to GitHub or the AI services."""
import os
import sys
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="deutsch-lernen-tests-"))
os.environ["GERMANSTUDY_DATA"] = str(_TMP / "data")
os.environ["GERMANSTUDY_ENV"] = str(_TMP / ".env")
os.environ["GERMANSTUDY_UPDATE_API"] = "http://127.0.0.1:9/no-network-in-tests"  # nothing listens on port 9
os.environ.pop("ANTHROPIC_API_KEY", None)
os.environ.pop("GEMINI_API_KEY", None)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest  # noqa: E402


@pytest.fixture(scope="session")
def client():
    from fastapi.testclient import TestClient
    from app.main import app
    with TestClient(app) as c:
        yield c
