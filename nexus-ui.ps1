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

    $installChoice = Read-Host "Would you like to install Claude CLI now? (y/n)"
    if ($installChoice -match "^[Yy]$") {
        Write-Host ""
        Write-Host "Installing Claude CLI (this may take a minute)..." -ForegroundColor Cyan
        try {
            # Use the official Windows installer
            Invoke-RestMethod https://claude.ai/install.ps1 | Invoke-Expression

            # Verify installation - refresh PATH
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
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
            Write-Host ""
            Write-Host "Please install manually by running:" -ForegroundColor Yellow
            Write-Host "  irm https://claude.ai/install.ps1 | iex" -ForegroundColor White
        }
    } else {
        Write-Host ""
        Write-Host "Skipping Claude CLI installation."
        Write-Host "You can install later by running:" -ForegroundColor Yellow
        Write-Host "  irm https://claude.ai/install.ps1 | iex" -ForegroundColor White
    }
    Write-Host ""
} else {
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

        Write-Host "Your Claude CLI must be updated to continue." -ForegroundColor Yellow
        $updateChoice = Read-Host "Update now? (y/n)"
        if ($updateChoice -match "^[Yy]$") {
            Write-Host ""
            Write-Host "Updating Claude CLI..." -ForegroundColor Cyan
            try {
                # Use the official Windows installer for updates
                Invoke-RestMethod https://claude.ai/install.ps1 | Invoke-Expression

                # Refresh PATH and verify update
                $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
                $newVersion = & claude --version 2>&1 | Select-String -Pattern "\d+\.\d+\.\d+" | ForEach-Object { $_.Matches[0].Value }
                if ($newVersion) {
                    $newMajor = [int]($newVersion.Split('.')[0])
                    if ($newMajor -ge $minMajor) {
                        Write-Host "[OK] Claude CLI updated to $newVersion" -ForegroundColor Green
                    } else {
                        Write-Host "[ERROR] Update failed. Please update manually:" -ForegroundColor Red
                        Write-Host "  irm https://claude.ai/install.ps1 | iex" -ForegroundColor Yellow
                        Read-Host "Press Enter to exit"
                        exit 1
                    }
                }
            } catch {
                Write-Host ""
                Write-Host "[ERROR] Update failed: $_" -ForegroundColor Red
                Write-Host ""
                Write-Host "Please update manually by running:" -ForegroundColor Yellow
                Write-Host "  irm https://claude.ai/install.ps1 | iex" -ForegroundColor White
                Read-Host "Press Enter to exit"
                exit 1
            }
        } else {
            Write-Host ""
            Write-Host "Cannot continue without updating Claude CLI." -ForegroundColor Red
            Write-Host "Run: irm https://claude.ai/install.ps1 | iex" -ForegroundColor Yellow
            Read-Host "Press Enter to exit"
            exit 1
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
