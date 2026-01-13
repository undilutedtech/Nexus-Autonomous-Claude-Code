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
                    echo [ERROR] Update failed. Please update manually:
                    echo         npm install -g @anthropic-ai/claude-code@latest
                    pause
                    exit /b 1
                )
            ) else (
                echo.
                echo Cannot continue without updating Claude CLI.
                echo Run: npm install -g @anthropic-ai/claude-code@latest
                pause
                exit /b 1
            )
        ) else (
            echo Please update Claude CLI manually:
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
                        echo [OK] Claude CLI updated!
                    )
                )
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
