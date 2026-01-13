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
                echo.
                echo If the problem persists, install manually:
                echo   npm install -g @anthropic-ai/claude-code
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

REM Get current version and extract version number
for /f "tokens=1" %%v in ('claude --version 2^>nul') do set FULL_VER=%%v
echo      Version: !FULL_VER!

REM Extract major version number (first digit before the dot)
for /f "tokens=1 delims=." %%m in ("!FULL_VER!") do set MAJOR_VER=%%m

REM Check minimum version requirement (2.0.0)
set MIN_MAJOR=2
set NEEDS_UPDATE=0

if !MAJOR_VER! LSS !MIN_MAJOR! set NEEDS_UPDATE=1

if !NEEDS_UPDATE! equ 1 (
    echo.
    echo [ERROR] Claude CLI version !FULL_VER! is too old!
    echo         Minimum required version is 2.0.0
    echo.

    where npm >nul 2>&1
    if !ERRORLEVEL! equ 0 (
        echo Your Claude CLI must be updated to continue.
        set /p UPDATE_CHOICE="Update now? (y/n): "
        if /i "!UPDATE_CHOICE!"=="y" (
            echo.
            echo Updating Claude CLI...
            call npm install -g @anthropic-ai/claude-code@latest

            REM Verify update
            for /f "tokens=1" %%v in ('claude --version 2^>nul') do set NEW_VER=%%v
            for /f "tokens=1 delims=." %%m in ("!NEW_VER!") do set NEW_MAJOR=%%m

            if !NEW_MAJOR! GEQ !MIN_MAJOR! (
                echo [OK] Claude CLI updated to !NEW_VER!
            ) else (
                echo.
                echo [ERROR] Automatic update failed!
                echo.
                echo Please update manually by running this command:
                echo   npm install -g @anthropic-ai/claude-code@latest
                echo.
                echo Then restart this script.
                pause
                exit /b 1
            )
        ) else (
            echo.
            echo Cannot continue without updating Claude CLI.
            echo.
            echo Please update manually by running this command:
            echo   npm install -g @anthropic-ai/claude-code@latest
            pause
            exit /b 1
        )
    ) else (
        echo Please update Claude CLI manually by running this command:
        echo   npm install -g @anthropic-ai/claude-code@latest
        pause
        exit /b 1
    )
) else (
    REM Check for optional updates if npm is available
    where npm >nul 2>&1
    if !ERRORLEVEL! equ 0 (
        for /f "tokens=*" %%v in ('npm view @anthropic-ai/claude-code version 2^>nul') do set LATEST_VER=%%v
        if defined LATEST_VER (
            if not "!FULL_VER!"=="!LATEST_VER!" (
                echo [!] Update available: !FULL_VER! -^> !LATEST_VER!
                set /p UPDATE_CHOICE="Would you like to update? (y/n): "
                if /i "!UPDATE_CHOICE!"=="y" (
                    echo Updating Claude CLI...
                    call npm install -g @anthropic-ai/claude-code@latest

                    REM Verify update
                    for /f "tokens=1" %%v in ('claude --version 2^>nul') do set NEW_VER=%%v
                    if "!NEW_VER!"=="!LATEST_VER!" (
                        echo [OK] Claude CLI updated to !NEW_VER!
                    ) else (
                        echo [!] Update may have failed. Current version: !NEW_VER!
                        echo     To update manually run: npm install -g @anthropic-ai/claude-code@latest
                    )
                )
            )
        )
    )
)

REM Check if user has credentials (check for ~/.claude/.credentials.json)
set "CLAUDE_CREDS=%USERPROFILE%\.claude\.credentials.json"
if exist "%CLAUDE_CREDS%" (
    echo [OK] Claude authenticated
    goto :setup_venv
)

REM No credentials - prompt user to login
echo [!] Not authenticated with Claude
echo.
echo Authentication is required before using Nexus.
echo This will open a browser window to sign in.
echo.
set /p "LOGIN_CHOICE=Press Enter to authenticate (or 'q' to quit): "

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

REM Check if login succeeded
if exist "%CLAUDE_CREDS%" (
    echo.
    echo [OK] Authentication successful!
    goto :setup_venv
) else (
    echo.
    echo [ERROR] Authentication failed or was cancelled.
    echo Please try again by running this script.
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
