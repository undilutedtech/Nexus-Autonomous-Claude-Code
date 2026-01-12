@echo off
cd /d "%~dp0"
REM Nexus UI - Web Interface Launcher for Windows

echo.
echo ====================================
echo   Nexus UI - Web Interface
echo ====================================
echo.

REM Check if Python is available
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python not found in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo [OK] Python found

REM Check if venv exists, create if not
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate the virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet

REM Run the Python launcher
python "%~dp0start_ui.py" %*

pause
