#!/bin/bash

# Claude Code Enhanced Notification System Installer
# This script sets up the notification system automatically

set -e

# Default installation directory (can be overridden by environment variable)
INSTALL_DIR="${CLAUDE_NOTIFICATIONS_DIR:-$HOME/.claude-notifications}"
CLAUDE_SETTINGS="$HOME/.claude/settings.json"

echo "🚀 Installing Claude Code Enhanced Notification System..."
echo "📁 Installation directory: $INSTALL_DIR"

# Check dependencies
echo "📋 Checking dependencies..."

if ! command -v jq &> /dev/null; then
    echo "❌ jq is required but not installed. Installing..."
    if command -v brew &> /dev/null; then
        brew install jq
    else
        echo "❌ Homebrew not found. Please install jq manually: https://stedolan.github.io/jq/"
        exit 1
    fi
fi

if ! command -v terminal-notifier &> /dev/null; then
    echo "❌ terminal-notifier is required but not installed. Installing..."
    if command -v brew &> /dev/null; then
        brew install terminal-notifier
    else
        echo "❌ Homebrew not found. Please install terminal-notifier manually"
        exit 1
    fi
fi

echo "✅ Dependencies check complete"

# Create installation directory if it doesn't exist
echo "🔧 Setting up installation directory..."
mkdir -p "$INSTALL_DIR"

# Get the directory where this install script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Copy scripts to installation directory (if not already there)
if [[ "$SCRIPT_DIR" != "$INSTALL_DIR" ]]; then
    echo "📋 Copying scripts to $INSTALL_DIR..."
    cp "$SCRIPT_DIR"/*.sh "$INSTALL_DIR/"
fi

# Make scripts executable
chmod +x "$INSTALL_DIR"/*.sh
echo "✅ Scripts setup complete"

# Test notification permissions
echo "🔔 Testing notification permissions..."
terminal-notifier -message "Claude Code notification system is ready!" -title "Setup Complete" -sound "Hero"

# Check if Claude settings file exists
if [[ ! -f "$CLAUDE_SETTINGS" ]]; then
    echo "📁 Creating Claude settings directory..."
    mkdir -p "$(dirname "$CLAUDE_SETTINGS")"
fi

# Check if hooks are already configured
if [[ -f "$CLAUDE_SETTINGS" ]] && jq -e '.hooks' "$CLAUDE_SETTINGS" &> /dev/null; then
    echo "⚠️  Claude hooks already configured. Please manually add the following to your settings.json:"
    echo ""
    # Convert absolute path to relative path for display
    RELATIVE_INSTALL_DIR=$(echo "$INSTALL_DIR" | sed "s|$HOME|~|")
    cat << EOF
"hooks": {
  "Notification": [
    {
      "matcher": "",
      "hooks": [
        {
          "type": "command",
          "command": "$RELATIVE_INSTALL_DIR/notify-handler.sh"
        }
      ]
    }
  ],
  "Stop": [
    {
      "matcher": "",
      "hooks": [
        {
          "type": "command",
          "command": "$RELATIVE_INSTALL_DIR/notify-completion.sh"
        }
      ]
    }
  ]
}
EOF
    echo ""
else
    echo "⚙️  Configuring Claude hooks..."
    
    # Create or update settings.json with relative paths
    RELATIVE_INSTALL_DIR=$(echo "$INSTALL_DIR" | sed "s|$HOME|~|")
    cat > "$CLAUDE_SETTINGS" << EOF
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "$RELATIVE_INSTALL_DIR/notify-handler.sh"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "$RELATIVE_INSTALL_DIR/notify-completion.sh"
          }
        ]
      }
    ]
  }
}
EOF
    echo "✅ Claude hooks configured"
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "📖 What's next:"
echo "1. Launch Claude Code from any supported application (IDE, terminal, etc.)"
echo "2. Switch to another app while Claude is working"
echo "3. Get beautiful notifications when Claude finishes!"
echo "4. Click notifications to return to your originating app"
echo ""
echo "🔍 Supported apps: IntelliJ IDEA, Cursor, VS Code, WebStorm, PyCharm, Terminal, iTerm, Ghostty, and more"
echo "🐛 Debug logs: tail -f $INSTALL_DIR/debug.log"
echo "📁 Installed at: $INSTALL_DIR"
echo ""
echo "Happy coding! 🚀"