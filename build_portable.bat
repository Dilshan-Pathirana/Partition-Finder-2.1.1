@echo off
REM Build PartitionFinder Standalone Installer
REM This script creates a portable executable package

echo ============================================================
echo   PartitionFinder 2.1.1 - Build Standalone Package
echo ============================================================
echo.

echo Step 1: Installing PyInstaller...
py -3.12 -m pip install pyinstaller

if %ERRORLEVEL% NEQ 0 (
    echo Error: Could not install PyInstaller
    pause
    exit /b 1
)

echo.
echo Step 2: Building executable (this may take 5-10 minutes)...
py -3.12 -m PyInstaller partfinder_gui.spec --clean --noconfirm

if %ERRORLEVEL% NEQ 0 (
    echo Error: Build failed
    pause
    exit /b 1
)

echo.
echo Step 3: Creating portable ZIP package...
py -3.12 -c "import shutil; shutil.make_archive('PartitionFinder-2.1.1-Python3-Portable', 'zip', 'dist', 'PartitionFinder')"

echo.
echo ============================================================
echo   BUILD COMPLETE!
echo ============================================================
echo.
echo Output files:
echo   * dist\PartitionFinder\           - Executable folder
echo   * PartitionFinder-2.1.1-Python3-Portable.zip  - Portable package
echo.
echo To distribute:
echo   1. Share the .zip file (approx 150-200 MB)
echo   2. Users extract and run PartitionFinder.exe
echo   3. No Python installation needed!
echo.
pause
