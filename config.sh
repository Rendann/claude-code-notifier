#!/bin/bash

# Configuration for Claude Code Enhanced Notification System
# This file defines paths and settings used by all scripts

# Default installation directory (can be overridden)
CLAUDE_NOTIFICATIONS_DIR="${CLAUDE_NOTIFICATIONS_DIR:-$HOME/.claude-notifications}"

# Log file location
CLAUDE_NOTIFICATIONS_LOG_FILE="$CLAUDE_NOTIFICATIONS_DIR/debug.log"

# Log rotation settings
CLAUDE_NOTIFICATIONS_MAX_LOG_LINES=2500  # Maximum lines before rotation
CLAUDE_NOTIFICATIONS_KEEP_LOG_LINES=1500  # Lines to keep after rotation

# Claude settings file
CLAUDE_NOTIFICATIONS_SETTINGS_FILE="$HOME/.claude/settings.json"

# Terminal notifier path (try common locations)
if command -v terminal-notifier &> /dev/null; then
    CLAUDE_NOTIFICATIONS_TERMINAL_NOTIFIER_PATH=$(which terminal-notifier)
elif [[ -f "/opt/homebrew/bin/terminal-notifier" ]]; then
    CLAUDE_NOTIFICATIONS_TERMINAL_NOTIFIER_PATH="/opt/homebrew/bin/terminal-notifier"
elif [[ -f "/usr/local/bin/terminal-notifier" ]]; then
    CLAUDE_NOTIFICATIONS_TERMINAL_NOTIFIER_PATH="/usr/local/bin/terminal-notifier"
else
    CLAUDE_NOTIFICATIONS_TERMINAL_NOTIFIER_PATH="terminal-notifier"
fi

# Export configuration variables
export CLAUDE_NOTIFICATIONS_DIR
export CLAUDE_NOTIFICATIONS_LOG_FILE
export CLAUDE_NOTIFICATIONS_MAX_LOG_LINES
export CLAUDE_NOTIFICATIONS_KEEP_LOG_LINES
export CLAUDE_NOTIFICATIONS_SETTINGS_FILE
export CLAUDE_NOTIFICATIONS_TERMINAL_NOTIFIER_PATH

# Function to get script directory (where this config.sh is located)
get_script_dir() {
    local script_path
    if [[ -n "${BASH_SOURCE[0]}" ]]; then
        script_path="${BASH_SOURCE[0]}"
    else
        # Fallback for scripts sourcing this file
        script_path="$CLAUDE_NOTIFICATIONS_DIR/config.sh"
    fi
    echo "$(cd "$(dirname "$script_path")" && pwd)"
}

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Export the function
export -f get_script_dir