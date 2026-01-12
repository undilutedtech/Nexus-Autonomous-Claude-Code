# Nexus UI - Web Interface Launcher
# PowerShell launcher script for Windows

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "  Nexus UI - Web Interface" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
$pythonPath = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonPath) {
    Write-Host "[ERROR] Python not found in PATH" -ForegroundColor Red
    Write-Host "Please install Python from https://python.org"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Python found" -ForegroundColor Green

# Check if venv exists, create if not
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    & python -m venv venv
}

# Activate the virtual environment
$activateScript = Join-Path $PSScriptRoot "venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
} else {
    Write-Host "[ERROR] Virtual environment activation script not found" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host "Installing dependencies..."
& pip install -r requirements.txt --quiet

# Check if Node.js is available (for UI)
$nodePath = Get-Command node -ErrorAction SilentlyContinue
if (-not $nodePath) {
    Write-Host "[WARNING] Node.js not found - UI may not work properly" -ForegroundColor Yellow
    Write-Host "Install from https://nodejs.org"
}

# Run the Python launcher
$startUiScript = Join-Path $PSScriptRoot "start_ui.py"
& python $startUiScript $args

Read-Host "Press Enter to exit"
