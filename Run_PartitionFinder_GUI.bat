@echo off
REM PartitionFinder GUI Launcher
REM This batch file launches the PartitionFinder GUI application

echo Starting PartitionFinder GUI...
echo.

REM Try to find Python 3.12 first, then fall back to python3, then python
py -3.12 PartitionFinder_GUI.py
if %ERRORLEVEL% NEQ 0 (
    python PartitionFinder_GUI.py
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Could not start PartitionFinder GUI
    echo Please ensure Python 3.8+ is installed
    echo.
    pause
)
