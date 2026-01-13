# Nexus - Autonomous Coding Platform
# PowerShell launcher script for Windows

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Nexus - Autonomous Coding Platform" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Claude CLI is installed
$claudePath = Get-Command claude -ErrorAction SilentlyContinue
if (-not $claudePath) {
    Write-Host "[!] Claude CLI not found" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Claude CLI is required to run Nexus."
    Write-Host ""

    # Check if npm is available for installation
    $npmPath = Get-Command npm -ErrorAction SilentlyContinue
    if ($npmPath) {
        $installChoice = Read-Host "Would you like to install Claude CLI now via npm? (y/n)"
        if ($installChoice -match "^[Yy]$") {
            Write-Host ""
            Write-Host "Installing Claude CLI via npm (this may take a minute)..." -ForegroundColor Cyan
            & npm install -g @anthropic-ai/claude-code

            # Verify installation
            $claudePath = Get-Command claude -ErrorAction SilentlyContinue
            if ($claudePath) {
                Write-Host "[OK] Claude CLI installed successfully!" -ForegroundColor Green
            } else {
                Write-Host "[!] Installation may have succeeded but 'claude' not found in PATH" -ForegroundColor Yellow
                Write-Host "Try restarting your terminal and running this script again."
                Write-Host ""
                Write-Host "If the problem persists, install manually:" -ForegroundColor Yellow
                Write-Host "  npm install -g @anthropic-ai/claude-code" -ForegroundColor White
                Read-Host "Press Enter to exit"
                exit 1
            }
        } else {
            Write-Host ""
            Write-Host "Please install Claude CLI first:"
            Write-Host "  1. Download from: https://claude.ai/download"
            Write-Host "  2. Or run: npm install -g @anthropic-ai/claude-code"
            Read-Host "Press Enter to exit"
            exit 1
        }
    } else {
        Write-Host "Please install Claude CLI first:"
        Write-Host "  1. Download from: https://claude.ai/download"
        Write-Host "  2. Install Node.js, then run: npm install -g @anthropic-ai/claude-code"
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host "[OK] Claude CLI found" -ForegroundColor Green

# Get current version
$currentVersion = & claude --version 2>&1 | Select-String -Pattern "\d+\.\d+\.\d+" | ForEach-Object { $_.Matches[0].Value }
Write-Host "     Version: $currentVersion" -ForegroundColor Gray

# Check minimum version requirement (2.0.0)
$minVersion = "2.0.0"
$needsUpdate = $false

if ($currentVersion) {
    $currentParts = $currentVersion.Split('.')
    $minParts = $minVersion.Split('.')
    $currentMajor = [int]$currentParts[0]
    $minMajor = [int]$minParts[0]

    if ($currentMajor -lt $minMajor) {
        $needsUpdate = $true
    }
}

if ($needsUpdate) {
    Write-Host ""
    Write-Host "[ERROR] Claude CLI version $currentVersion is too old!" -ForegroundColor Red
    Write-Host "        Minimum required version is $minVersion" -ForegroundColor Red
    Write-Host ""

    $npmPath = Get-Command npm -ErrorAction SilentlyContinue
    if ($npmPath) {
        Write-Host "Your Claude CLI must be updated to continue." -ForegroundColor Yellow
        $updateChoice = Read-Host "Update now? (y/n)"
        if ($updateChoice -match "^[Yy]$") {
            Write-Host ""
            Write-Host "Updating Claude CLI..." -ForegroundColor Cyan
            & npm install -g @anthropic-ai/claude-code@latest

            # Verify update
            $newVersion = & claude --version 2>&1 | Select-String -Pattern "\d+\.\d+\.\d+" | ForEach-Object { $_.Matches[0].Value }
            if ($newVersion) {
                $newMajor = [int]($newVersion.Split('.')[0])
                if ($newMajor -ge $minMajor) {
                    Write-Host "[OK] Claude CLI updated to $newVersion" -ForegroundColor Green
                } else {
                    Write-Host ""
                    Write-Host "[ERROR] Automatic update failed!" -ForegroundColor Red
                    Write-Host ""
                    Write-Host "Please update manually by running this command:" -ForegroundColor Yellow
                    Write-Host "  npm install -g @anthropic-ai/claude-code@latest" -ForegroundColor White
                    Write-Host ""
                    Write-Host "Then restart this script."
                    Read-Host "Press Enter to exit"
                    exit 1
                }
            }
        } else {
            Write-Host ""
            Write-Host "Cannot continue without updating Claude CLI." -ForegroundColor Red
            Write-Host ""
            Write-Host "Please update manually by running this command:" -ForegroundColor Yellow
            Write-Host "  npm install -g @anthropic-ai/claude-code@latest" -ForegroundColor White
            Read-Host "Press Enter to exit"
            exit 1
        }
    } else {
        Write-Host "Please update Claude CLI manually by running this command:" -ForegroundColor Yellow
        Write-Host "  npm install -g @anthropic-ai/claude-code@latest" -ForegroundColor White
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    # Check for optional updates if npm is available
    $npmPath = Get-Command npm -ErrorAction SilentlyContinue
    if ($npmPath) {
        try {
            $latestVersion = & npm view @anthropic-ai/claude-code version 2>&1
            if ($currentVersion -and $latestVersion -and ($currentVersion -ne $latestVersion)) {
                Write-Host "[!] Update available: $currentVersion -> $latestVersion" -ForegroundColor Yellow
                $updateChoice = Read-Host "Would you like to update? (y/n)"
                if ($updateChoice -match "^[Yy]$") {
                    Write-Host "Updating Claude CLI..." -ForegroundColor Cyan
                    & npm install -g @anthropic-ai/claude-code@latest

                    # Verify update worked
                    $newVersion = & claude --version 2>&1 | Select-String -Pattern "\d+\.\d+\.\d+" | ForEach-Object { $_.Matches[0].Value }
                    if ($newVersion -eq $latestVersion) {
                        Write-Host "[OK] Claude CLI updated to $newVersion" -ForegroundColor Green
                    } else {
                        Write-Host "[!] Update may have failed. Current version: $newVersion" -ForegroundColor Yellow
                        Write-Host "    To update manually run: npm install -g @anthropic-ai/claude-code@latest" -ForegroundColor Gray
                    }
                }
            }
        } catch {
            # Silently ignore update check failures
        }
    }
}

# Check if user has credentials
$claudeCreds = Join-Path $env:USERPROFILE ".claude\.credentials.json"
if (Test-Path $claudeCreds) {
    Write-Host "[OK] Claude authenticated" -ForegroundColor Green
} else {
    Write-Host "[!] Not authenticated with Claude" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Authentication is required before using Nexus."
    Write-Host "This will open a browser window to sign in."
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

# Run the app
& $pythonCmd start.py
