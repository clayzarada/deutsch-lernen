@echo off
cd /d "%~dp0"
if not exist .venv (
  echo First run: setting up Python environment. This takes a minute...
  py -m venv .venv || python -m venv .venv
)
.venv\Scripts\python -m pip install -q --disable-pip-version-check -r requirements.txt
.venv\Scripts\python run.py
pause
