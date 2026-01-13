#!/bin/bash
cd "$(dirname "$0")"

echo ""
echo "========================================"
echo "  Nexus - Autonomous Coding Platform"
echo "========================================"
echo ""

# Function to install Claude CLI
install_claude_cli() {
    echo ""
    echo "Claude CLI is required to run Nexus."
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
                return 0
            else
                echo "[!] Installation may have succeeded but 'claude' not found in PATH"
                echo "Try restarting your terminal and running this script again."
                return 1
            fi
        fi
    fi

    echo ""
    echo "To install Claude CLI, you can:"
    echo "  1. Run: curl -fsSL https://claude.ai/install.sh | bash"
    echo "  2. Install Node.js, then run: npm install -g @anthropic-ai/claude-code"
    return 1
}

# Check if Claude CLI is installed
if ! command -v claude &> /dev/null; then
    echo "[!] Claude CLI not found"

    if ! install_claude_cli; then
        echo ""
        echo "Please install Claude CLI and run this script again."
        exit 1
    fi
fi

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

# Check if user has credentials
CLAUDE_CREDS="$HOME/.claude/.credentials.json"
if [ -f "$CLAUDE_CREDS" ]; then
    echo "[OK] Claude credentials found"
else
    echo "[!] Not authenticated with Claude"
    echo ""
    echo "You need to run 'claude login' to authenticate."
    echo "This will open a browser window to sign in."
    echo ""
    read -p "Would you like to run 'claude login' now? (y/n): " LOGIN_CHOICE

    if [[ "$LOGIN_CHOICE" =~ ^[Yy]$ ]]; then
        echo ""
        echo "Running 'claude login'..."
        echo "Complete the login in your browser, then return here."
        echo ""
        claude login

        # Check if login succeeded
        if [ -f "$CLAUDE_CREDS" ]; then
            echo ""
            echo "[OK] Login successful!"
        else
            echo ""
            echo "[ERROR] Login failed or was cancelled."
            echo "Please try again."
            exit 1
        fi
    else
        echo ""
        echo "Please run 'claude login' manually, then try again."
        exit 1
    fi
fi

echo ""

# Check if venv exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --quiet

# Run the app
python start.py
