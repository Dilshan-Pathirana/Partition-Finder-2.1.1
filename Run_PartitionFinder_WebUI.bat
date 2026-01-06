@echo off
REM PartitionFinder Web UI Launcher (single production server)
REM Starts FastAPI + serves built React UI from the same port.

echo Starting PartitionFinder Web UI (single server)...
echo.

set REPO_ROOT=%~dp0
cd /d "%REPO_ROOT%"

REM Prefer local venv python if present
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m partitionfinder.webapp.prod
  goto done
)

REM Fall back to Windows Python launcher, then python on PATH
py -3 PartitionFinder.py --help >nul 2>&1
if %ERRORLEVEL% EQU 0 (
  py -3 -m partitionfinder.webapp.prod
  goto done
)

python -m partitionfinder.webapp.prod

:done
if %ERRORLEVEL% NEQ 0 (
  echo.
  echo ERROR: Could not start PartitionFinder Web UI.
  echo - Ensure Python dependencies are installed: pip install -r requirements.txt
  echo - Ensure Node.js is installed (for building the UI): https://nodejs.org/
  echo.
  pause
)
