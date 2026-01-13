# Nexus UI - Web Interface Launcher
# PowerShell launcher script for Windows

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "  Nexus UI - Web Interface" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available (try python, then py launcher)
$pythonCmd = "python"
$pythonPath = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonPath) {
    $pythonPath = Get-Command py -ErrorAction SilentlyContinue
    if ($pythonPath) {
        $pythonCmd = "py"
    } else {
        Write-Host "[ERROR] Python not found in PATH" -ForegroundColor Red
        Write-Host "Please install Python from https://python.org"
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host "[OK] Python found ($pythonCmd)" -ForegroundColor Green

# Check if venv exists, create if not
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    & $pythonCmd -m venv venv
}

# Activate the virtual environment (dot-source to persist env vars)
$activateScript = Join-Path $PSScriptRoot "venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    . $activateScript
} else {
    Write-Host "[ERROR] Virtual environment activation script not found" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "Installing dependencies..."
& pip install -r requirements.txt --quiet

# Check if Claude CLI is available (required for spec generator)
$claudePath = Get-Command claude -ErrorAction SilentlyContinue
if (-not $claudePath) {
    Write-Host "[!] Claude CLI not found" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Claude CLI is required for the Spec Generator feature."
    Write-Host ""

    # Check if npm is available for installation
    $npmPath = Get-Command npm -ErrorAction SilentlyContinue
    if ($npmPath) {
        $installChoice = Read-Host "Would you like to install Claude CLI now via npm? (y/n)"
        if ($installChoice -match "^[Yy]$") {
            Write-Host ""
            Write-Host "Installing Claude CLI via npm (this may take a minute)..." -ForegroundColor Cyan
            try {
                & npm install -g @anthropic-ai/claude-code 2>&1 | Out-Null

                # Verify installation
                $claudePath = Get-Command claude -ErrorAction SilentlyContinue
                if ($claudePath) {
                    Write-Host "[OK] Claude CLI installed successfully!" -ForegroundColor Green
                    Write-Host ""
                    Write-Host "You need to authenticate with Claude before using the Spec Generator."
                    Write-Host "Run 'claude login' to authenticate, or it will prompt you when needed."
                    Write-Host ""
                } else {
                    Write-Host "[!] Installation may have succeeded but 'claude' not found in PATH" -ForegroundColor Yellow
                    Write-Host "Try restarting your terminal and running this script again."
                }
            } catch {
                Write-Host "[ERROR] Failed to install Claude CLI: $_" -ForegroundColor Red
                Write-Host "You can install manually from: https://claude.ai/download"
            }
        } else {
            Write-Host ""
            Write-Host "Skipping Claude CLI installation."
            Write-Host "You can install later from: https://claude.ai/download"
            Write-Host "Or run: npm install -g @anthropic-ai/claude-code"
        }
    } else {
        Write-Host "To install Claude CLI, you can either:"
        Write-Host "  1. Download from: https://claude.ai/download"
        Write-Host "  2. Install Node.js, then run: npm install -g @anthropic-ai/claude-code"
    }
    Write-Host ""
} else {
    Write-Host "[OK] Claude CLI found" -ForegroundColor Green

    # Check for updates if npm is available
    $npmPath = Get-Command npm -ErrorAction SilentlyContinue
    if ($npmPath) {
        Write-Host "     Checking for updates..." -ForegroundColor Gray
        try {
            # Get current version
            $currentVersion = & claude --version 2>&1 | Select-String -Pattern "\d+\.\d+\.\d+" | ForEach-Object { $_.Matches[0].Value }

            # Check latest version from npm
            $latestVersion = & npm view @anthropic-ai/claude-code version 2>&1

            if ($currentVersion -and $latestVersion -and ($currentVersion -ne $latestVersion)) {
                Write-Host "[!] Update available: $currentVersion -> $latestVersion" -ForegroundColor Yellow
                $updateChoice = Read-Host "Would you like to update Claude CLI? (y/n)"
                if ($updateChoice -match "^[Yy]$") {
                    Write-Host "Updating Claude CLI..." -ForegroundColor Cyan
                    & npm install -g @anthropic-ai/claude-code@latest 2>&1 | Out-Null
                    Write-Host "[OK] Claude CLI updated!" -ForegroundColor Green
                }
            } else {
                Write-Host "     Up to date ($currentVersion)" -ForegroundColor Gray
            }
        } catch {
            # Silently ignore update check failures
        }
    }
}

# Check if user is authenticated with Claude (REQUIRED for Spec Generator)
$claudeCreds = Join-Path $env:USERPROFILE ".claude\.credentials.json"
if (Test-Path $claudeCreds) {
    Write-Host "[OK] Claude authenticated" -ForegroundColor Green
} else {
    Write-Host "[!] Not authenticated with Claude" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Authentication is required before using Nexus."
    Write-Host "This will open a browser window to sign in with your Claude account."
    Write-Host ""

    $loginChoice = Read-Host "Press Enter to authenticate (or 'q' to quit)"

    if ($loginChoice -eq "q") {
        Write-Host "Exiting. Please run 'claude login' manually before using Nexus."
        exit 1
    }

    Write-Host ""
    Write-Host "Opening browser for authentication..." -ForegroundColor Cyan
    Write-Host "Complete the login in your browser, then return here."
    Write-Host ""

    & claude login

    # Verify login succeeded
    if (Test-Path $claudeCreds) {
        Write-Host ""
        Write-Host "[OK] Authentication successful!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "[ERROR] Authentication failed or was cancelled." -ForegroundColor Red
        Write-Host "Please try again by running this script."
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""

# Check if Node.js is available (for UI)
$nodePath = Get-Command node -ErrorAction SilentlyContinue
if (-not $nodePath) {
    Write-Host "[WARNING] Node.js not found - UI may not work properly" -ForegroundColor Yellow
    Write-Host "Install from https://nodejs.org"
} else {
    Write-Host "[OK] Node.js found" -ForegroundColor Green
}

# Run the Python launcher
$startUiScript = Join-Path $PSScriptRoot "start_ui.py"
& $pythonCmd $startUiScript $args

Read-Host "Press Enter to exit"
