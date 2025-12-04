@echo off
REM PartitionFinder GUI Launcher for Windows
REM Double-click this file to start the GUI application

echo Starting PartitionFinder GUI...
py -3.12 gui_app.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Could not start the application.
    echo Please make sure Python 3.12 is installed.
    echo.
    pause
)
