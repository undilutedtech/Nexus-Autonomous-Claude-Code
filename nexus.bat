@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

echo.
echo ========================================
echo   Nexus - Autonomous Coding Platform
echo ========================================
echo.

REM Check if Claude CLI is installed
where claude >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Claude CLI not found
    echo.
    echo Claude CLI is required to run Nexus.
    echo.

    REM Check if npm is available for installation
    where npm >nul 2>&1
    if !errorlevel! equ 0 (
        set /p INSTALL_CHOICE="Would you like to install Claude CLI now via npm? (y/n): "
        if /i "!INSTALL_CHOICE!"=="y" (
            echo.
            echo Installing Claude CLI via npm [this may take a minute]...
            call npm install -g @anthropic-ai/claude-code
            where claude >nul 2>&1
            if !errorlevel! equ 0 (
                echo [OK] Claude CLI installed successfully!
            ) else (
                echo [!] Installation may have succeeded but 'claude' not found in PATH
                echo Try restarting your terminal and running this script again.
                pause
                exit /b 1
            )
        ) else (
            echo.
            echo Please install Claude CLI first:
            echo   1. Download from: https://claude.ai/download
            echo   2. Or run: npm install -g @anthropic-ai/claude-code
            pause
            exit /b 1
        )
    ) else (
        echo Please install Claude CLI first:
        echo   1. Download from: https://claude.ai/download
        echo   2. Install Node.js, then run: npm install -g @anthropic-ai/claude-code
        pause
        exit /b 1
    )
)

echo [OK] Claude CLI found

REM Check for updates if npm is available
where npm >nul 2>&1
if !errorlevel! equ 0 (
    echo      Checking for updates...

    REM Get current version
    for /f "tokens=*" %%v in ('claude --version 2^>nul') do set CURRENT_VER=%%v

    REM Get latest version from npm
    for /f "tokens=*" %%v in ('npm view @anthropic-ai/claude-code version 2^>nul') do set LATEST_VER=%%v

    if defined CURRENT_VER if defined LATEST_VER (
        if not "!CURRENT_VER!"=="!LATEST_VER!" (
            echo [!] Update available: !CURRENT_VER! -^> !LATEST_VER!
            set /p UPDATE_CHOICE="Would you like to update Claude CLI? (y/n): "
            if /i "!UPDATE_CHOICE!"=="y" (
                echo Updating Claude CLI...
                call npm install -g @anthropic-ai/claude-code@latest
                echo [OK] Claude CLI updated!
            )
        ) else (
            echo      Up to date
        )
    )
)

REM Check if user has credentials (check for ~/.claude/.credentials.json)
set "CLAUDE_CREDS=%USERPROFILE%\.claude\.credentials.json"
if exist "%CLAUDE_CREDS%" (
    echo [OK] Claude credentials found
    goto :setup_venv
)

REM No credentials - prompt user to login
echo [!] Not authenticated with Claude
echo.
echo You need to run 'claude login' to authenticate.
echo This will open a browser window to sign in.
echo.
set /p "LOGIN_CHOICE=Would you like to run 'claude login' now? (y/n): "

if /i "%LOGIN_CHOICE%"=="y" (
    echo.
    echo Running 'claude login'...
    echo Complete the login in your browser, then return here.
    echo.
    call claude login

    REM Check if login succeeded
    if exist "%CLAUDE_CREDS%" (
        echo.
        echo [OK] Login successful!
        goto :setup_venv
    ) else (
        echo.
        echo [ERROR] Login failed or was cancelled.
        echo Please try again.
        pause
        exit /b 1
    )
) else (
    echo.
    echo Please run 'claude login' manually, then try again.
    pause
    exit /b 1
)

:setup_venv
echo.

REM Check if venv exists, create if not
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate the virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet

REM Run the app
python start.py
