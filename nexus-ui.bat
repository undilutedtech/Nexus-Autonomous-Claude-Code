@echo off
setlocal EnableDelayedExpansion
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

REM Check if Claude CLI is available (required for spec generator)
where claude >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [!] Claude CLI not found
    echo.
    echo Claude CLI is required for the Spec Generator feature.
    echo.

    REM Check if npm is available for installation
    where npm >nul 2>&1
    if !ERRORLEVEL! equ 0 (
        set /p INSTALL_CHOICE="Would you like to install Claude CLI now via npm? (y/n): "
        if /i "!INSTALL_CHOICE!"=="y" (
            echo.
            echo Installing Claude CLI via npm [this may take a minute]...
            call npm install -g @anthropic-ai/claude-code
            where claude >nul 2>&1
            if !ERRORLEVEL! equ 0 (
                echo [OK] Claude CLI installed successfully!
                echo.
                echo You need to authenticate with Claude before using the Spec Generator.
                echo Run 'claude login' to authenticate, or it will prompt you when needed.
            ) else (
                echo [!] Installation may have succeeded but 'claude' not found in PATH
                echo Try restarting your terminal and running this script again.
            )
        ) else (
            echo.
            echo Skipping Claude CLI installation.
            echo You can install later from: https://claude.ai/download
            echo Or run: npm install -g @anthropic-ai/claude-code
        )
    ) else (
        echo To install Claude CLI, you can either:
        echo   1. Download from: https://claude.ai/download
        echo   2. Install Node.js, then run: npm install -g @anthropic-ai/claude-code
    )
    echo.
) else (
    echo [OK] Claude CLI found

    REM Check for updates if npm is available
    where npm >nul 2>&1
    if !ERRORLEVEL! equ 0 (
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
)

REM Check if user is authenticated with Claude (REQUIRED for Spec Generator)
set "CLAUDE_CREDS=%USERPROFILE%\.claude\.credentials.json"
if exist "%CLAUDE_CREDS%" (
    echo [OK] Claude authenticated
) else (
    echo [!] Not authenticated with Claude
    echo.
    echo Authentication is required before using Nexus.
    echo This will open a browser window to sign in with your Claude account.
    echo.
    set /p LOGIN_CHOICE="Press Enter to authenticate (or 'q' to quit): "
    if /i "!LOGIN_CHOICE!"=="q" (
        echo Exiting. Please run 'claude login' manually before using Nexus.
        pause
        exit /b 1
    )
    echo.
    echo Opening browser for authentication...
    echo Complete the login in your browser, then return here.
    echo.
    call claude login

    if exist "%CLAUDE_CREDS%" (
        echo.
        echo [OK] Authentication successful!
    ) else (
        echo.
        echo [ERROR] Authentication failed or was cancelled.
        echo Please try again by running this script.
        pause
        exit /b 1
    )
)

echo.

REM Check if Node.js is available
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Node.js not found - UI may not work properly
    echo Install from https://nodejs.org
) else (
    echo [OK] Node.js found
)

REM Run the Python launcher
python "%~dp0start_ui.py" %*

pause
