#!/bin/bash
cd "$(dirname "$0")"
# Nexus UI - Web Interface Launcher for Unix/Linux/macOS

echo ""
echo "===================================="
echo "  Nexus UI - Web Interface"
echo "===================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "ERROR: Python not found"
        echo "Please install Python from https://python.org"
        exit 1
    fi
    PYTHON_CMD="python"
else
    PYTHON_CMD="python3"
fi

echo "[OK] Python found"

# Check if venv exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --quiet

# Check if Claude CLI is available (required for spec generator)
if ! command -v claude &> /dev/null; then
    echo "[!] Claude CLI not found"
    echo ""
    echo "Claude CLI is required for the Spec Generator feature."
    echo ""

    # Check if npm is available for installation
    if command -v npm &> /dev/null; then
        read -p "Would you like to install Claude CLI now via npm? (y/n): " INSTALL_CHOICE
        if [[ "$INSTALL_CHOICE" =~ ^[Yy]$ ]]; then
            echo ""
            echo "Installing Claude CLI via npm (this may take a minute)..."
            npm install -g @anthropic-ai/claude-code 2>/dev/null

            # Verify installation
            if command -v claude &> /dev/null; then
                echo "[OK] Claude CLI installed successfully!"
                echo ""
                echo "You need to authenticate with Claude before using the Spec Generator."
                echo "Run 'claude login' to authenticate, or it will prompt you when needed."
                echo ""
            else
                echo "[!] Installation may have succeeded but 'claude' not found in PATH"
                echo "Try restarting your terminal and running this script again."
            fi
        else
            echo ""
            echo "Skipping Claude CLI installation."
            echo "You can install later using one of these methods:"
            echo "  1. curl -fsSL https://claude.ai/install.sh | bash"
            echo "  2. npm install -g @anthropic-ai/claude-code"
        fi
    else
        echo "To install Claude CLI, you can:"
        echo "  1. Run: curl -fsSL https://claude.ai/install.sh | bash"
        echo "  2. Install Node.js, then run: npm install -g @anthropic-ai/claude-code"
    fi
    echo ""
else
    echo "[OK] Claude CLI found"

    # Check for updates if npm is available
    if command -v npm &> /dev/null; then
        echo "     Checking for updates..."

        # Get current version
        CURRENT_VER=$(claude --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)

        # Get latest version from npm
        LATEST_VER=$(npm view @anthropic-ai/claude-code version 2>/dev/null)

        if [ -n "$CURRENT_VER" ] && [ -n "$LATEST_VER" ] && [ "$CURRENT_VER" != "$LATEST_VER" ]; then
            echo "[!] Update available: $CURRENT_VER -> $LATEST_VER"
            read -p "Would you like to update Claude CLI? (y/n): " UPDATE_CHOICE
            if [[ "$UPDATE_CHOICE" =~ ^[Yy]$ ]]; then
                echo "Updating Claude CLI..."
                npm install -g @anthropic-ai/claude-code@latest 2>/dev/null
                echo "[OK] Claude CLI updated!"
            fi
        else
            echo "     Up to date ($CURRENT_VER)"
        fi
    fi
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "[WARNING] Node.js not found - UI may not work properly"
    echo "Install from https://nodejs.org"
else
    echo "[OK] Node.js found"
fi

# Run the Python launcher
python start_ui.py "$@"
