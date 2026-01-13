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
            npm install -g @anthropic-ai/claude-code

            # Verify installation
            if command -v claude &> /dev/null; then
                echo "[OK] Claude CLI installed successfully!"
                return 0
            else
                echo "[!] Installation may have succeeded but 'claude' not found in PATH"
                echo "Try restarting your terminal and running this script again."
                echo ""
                echo "If the problem persists, install manually:"
                echo "  npm install -g @anthropic-ai/claude-code"
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

# Get current version
CURRENT_VER=$(claude --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
echo "     Version: $CURRENT_VER"

# Check minimum version requirement (2.0.0)
MIN_VERSION="2.0.0"
NEEDS_UPDATE=0

if [ -n "$CURRENT_VER" ]; then
    CURRENT_MAJOR=$(echo "$CURRENT_VER" | cut -d. -f1)
    MIN_MAJOR=$(echo "$MIN_VERSION" | cut -d. -f1)

    if [ "$CURRENT_MAJOR" -lt "$MIN_MAJOR" ]; then
        NEEDS_UPDATE=1
    fi
fi

if [ "$NEEDS_UPDATE" -eq 1 ]; then
    echo ""
    echo "[ERROR] Claude CLI version $CURRENT_VER is too old!"
    echo "        Minimum required version is $MIN_VERSION"
    echo ""

    if command -v npm &> /dev/null; then
        echo "Your Claude CLI must be updated to continue."
        read -p "Update now? (y/n): " UPDATE_CHOICE
        if [[ "$UPDATE_CHOICE" =~ ^[Yy]$ ]]; then
            echo ""
            echo "Updating Claude CLI..."
            npm install -g @anthropic-ai/claude-code@latest

            # Verify update
            NEW_VER=$(claude --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
            if [ -n "$NEW_VER" ]; then
                NEW_MAJOR=$(echo "$NEW_VER" | cut -d. -f1)
                if [ "$NEW_MAJOR" -ge "$MIN_MAJOR" ]; then
                    echo "[OK] Claude CLI updated to $NEW_VER"
                else
                    echo ""
                    echo "[ERROR] Automatic update failed!"
                    echo ""
                    echo "Please update manually by running this command:"
                    echo "  npm install -g @anthropic-ai/claude-code@latest"
                    echo ""
                    echo "Then restart this script."
                    exit 1
                fi
            fi
        else
            echo ""
            echo "Cannot continue without updating Claude CLI."
            echo ""
            echo "Please update manually by running this command:"
            echo "  npm install -g @anthropic-ai/claude-code@latest"
            exit 1
        fi
    else
        echo "Please update Claude CLI manually by running this command:"
        echo "  npm install -g @anthropic-ai/claude-code@latest"
        exit 1
    fi
else
    # Check for optional updates if npm is available
    if command -v npm &> /dev/null; then
        LATEST_VER=$(npm view @anthropic-ai/claude-code version 2>/dev/null)
        if [ -n "$CURRENT_VER" ] && [ -n "$LATEST_VER" ] && [ "$CURRENT_VER" != "$LATEST_VER" ]; then
            echo "[!] Update available: $CURRENT_VER -> $LATEST_VER"
            read -p "Would you like to update? (y/n): " UPDATE_CHOICE
            if [[ "$UPDATE_CHOICE" =~ ^[Yy]$ ]]; then
                echo "Updating Claude CLI..."
                npm install -g @anthropic-ai/claude-code@latest

                # Verify update
                NEW_VER=$(claude --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
                if [ "$NEW_VER" = "$LATEST_VER" ]; then
                    echo "[OK] Claude CLI updated to $NEW_VER"
                else
                    echo "[!] Update may have failed. Current version: $NEW_VER"
                    echo "    To update manually run: npm install -g @anthropic-ai/claude-code@latest"
                fi
            fi
        fi
    fi
fi

# Check if user has credentials
CLAUDE_CREDS="$HOME/.claude/.credentials.json"
if [ -f "$CLAUDE_CREDS" ]; then
    echo "[OK] Claude authenticated"
else
    echo "[!] Not authenticated with Claude"
    echo ""
    echo "Authentication is required before using Nexus."
    echo "This will open a browser window to sign in."
    echo ""
    read -p "Press Enter to authenticate (or 'q' to quit): " LOGIN_CHOICE

    if [ "$LOGIN_CHOICE" = "q" ]; then
        echo "Exiting. Please run 'claude login' manually before using Nexus."
        exit 1
    fi

    echo ""
    echo "Opening browser for authentication..."
    echo "Complete the login in your browser, then return here."
    echo ""

    claude login

    # Check if login succeeded
    if [ -f "$CLAUDE_CREDS" ]; then
        echo ""
        echo "[OK] Authentication successful!"
    else
        echo ""
        echo "[ERROR] Authentication failed or was cancelled."
        echo "Please try again by running this script."
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
