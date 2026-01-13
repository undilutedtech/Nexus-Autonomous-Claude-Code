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
    Write-Host "[ERROR] Claude CLI not found" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Claude CLI first:"
    Write-Host "  https://claude.ai/download"
    Write-Host ""
    Write-Host "Then run this script again."
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Claude CLI found" -ForegroundColor Green

# Check if user has credentials
$claudeCreds = Join-Path $env:USERPROFILE ".claude\.credentials.json"
if (Test-Path $claudeCreds) {
    Write-Host "[OK] Claude credentials found" -ForegroundColor Green
} else {
    Write-Host "[!] Not authenticated with Claude" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "You need to run 'claude login' to authenticate."
    Write-Host "This will open a browser window to sign in."
    Write-Host ""
    $loginChoice = Read-Host "Would you like to run 'claude login' now? (y/n)"

    if ($loginChoice -match "^[Yy]$") {
        Write-Host ""
        Write-Host "Running 'claude login'..."
        Write-Host "Complete the login in your browser, then return here."
        Write-Host ""
        & claude login

        if (Test-Path $claudeCreds) {
            Write-Host ""
            Write-Host "[OK] Login successful!" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "[ERROR] Login failed or was cancelled." -ForegroundColor Red
            Write-Host "Please try again."
            Read-Host "Press Enter to exit"
            exit 1
        }
    } else {
        Write-Host ""
        Write-Host "Please run 'claude login' manually, then try again."
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
