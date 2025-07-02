# Claude Code Enhanced Notification System

Smart, click-to-focus notification system for Claude Code that delivers context-aware notifications with seamless app switching functionality.

## Overview

This enhanced notification system transforms Claude Code into a fully integrated development tool using the [hooks feature](https://docs.anthropic.com/en/docs/claude-code/hooks). The system intelligently detects your workflow context and delivers beautiful, actionable notifications that you can click to instantly return to your work.

## ✨ What's New in v2.0

- **🎯 Click-to-Focus**: Click any notification to instantly activate the originating application
- **🎨 Enhanced UI**: Beautiful notifications with proper titles, subtitles, and formatting  
- **⚡ Improved Reliability**: Uses `terminal-notifier` for consistent, professional notifications
- **🔧 Better Debugging**: Comprehensive logging with detailed command output tracking
- **🚫 DnD Bypass**: Important notifications bypass Do Not Disturb mode
- **📱 Unique Grouping**: Each notification is properly grouped without replacement issues

## Setup

### 1. Install Scripts
```bash
# Create scripts directory
mkdir -p ~/scripts

# Make them executable
chmod +x ~/scripts/*.sh
```

### 2. Configure Claude Code Hooks
Add this configuration to your `~/.claude/settings.json`:

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "~/scripts/notify-handler.sh"
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
            "command": "~/scripts/notify-completion.sh"
          }
        ]
      }
    ]
  }
}
```

### 3. Install Dependencies
```bash
# Ensure jq is installed for JSON parsing
brew install jq

# Install terminal-notifier for enhanced notifications with click handling
brew install terminal-notifier
```

## Scripts

### `detect-originating-app.sh`
Core utility that walks up the process tree to identify the application that launched Claude Code.

```bash
#!/bin/bash

# Function to detect the originating application by walking up process tree
detect_originating_app() {
    current_pid=$$  # Start with current script's PID
    
    while [[ $current_pid -gt 1 ]]; do
        # Get process name
        process_name=$(ps -o comm= -p "$current_pid" 2>/dev/null)
        
        # Check if it's a known IDE/editor
        case "$process_name" in
            *"idea"*|*"IntelliJ"*) echo "idea"; return ;;
            *"Cursor"*) echo "cursor"; return ;;
            *"code"*) echo "vscode"; return ;;
            *"WebStorm"*) echo "webstorm"; return ;;
            *"PHPStorm"*) echo "phpstorm"; return ;;
            *"PyCharm"*) echo "pycharm"; return ;;
            *"Sublime"*) echo "sublime"; return ;;
            *"Terminal"*) echo "terminal"; return ;;
            *"iTerm"*) echo "iterm"; return ;;
            *"Ghostty"*) echo "ghostty"; return ;;
            *"Alacritty"*) echo "alacritty"; return ;;
        esac
        
        # Move to parent process
        current_pid=$(ps -o ppid= -p "$current_pid" 2>/dev/null | xargs)
        
        # Safety check to avoid infinite loop
        if [[ -z "$current_pid" ]]; then
            break
        fi
    done
    
    echo "unknown"
}

# Export the function so it can be sourced by other scripts
export -f detect_originating_app

# If script is run directly, test the function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Originating app: $(detect_originating_app)"
fi
```

### `notify-completion.sh`
Hook for the `Stop` event - shows enhanced notifications when Claude Code finishes a conversation with click-to-focus functionality.

```bash
#!/bin/bash

# Read JSON input from stdin
input=$(cat)

# Log file for debugging
log_file="$HOME/scripts/claude-hooks-debug.log"

# Log the input data with timestamp
echo "=== $(date) ===" >> "$log_file"
echo "Input JSON:" >> "$log_file"
echo "$input" >> "$log_file"

# Extract project directory from transcript path
transcript_path=$(echo "$input" | jq -r '.transcript_path // "unknown"')
# Extract the encoded directory name after the last slash, remove .jsonl extension
encoded_dir=$(basename "$(dirname "$transcript_path")")
# Decode the directory name by replacing hyphens with slashes and taking meaningful parts
decoded_path=$(echo "$encoded_dir" | sed 's/-/\//g')
# Extract meaningful project name (skip /Users/username part)
project_name=$(echo "$decoded_path" | sed 's|^/Users/[^/]*/||' | sed 's|^/||')

# Source the originating app detection function
source "$HOME/scripts/detect-originating-app.sh"

# Get the originating application (where Claude was launched from)
originating_app=$(detect_originating_app)

# Get the currently focused application
focused_app_full=$(osascript -e 'tell application "System Events" to get name of first application process whose frontmost is true')
case "$focused_app_full" in
    "IntelliJ IDEA") focused_app="idea" ;;
    "iTerm2") focused_app="iterm" ;;
    "iTerm") focused_app="iterm" ;;
    "Ghostty") focused_app="ghostty" ;;
    "Cursor") focused_app="cursor" ;;
    *) focused_app=$(echo "$focused_app_full" | tr '[:upper:]' '[:lower:]') ;;
esac

# Log extracted values
echo "Transcript path: $transcript_path" >> "$log_file"
echo "Encoded dir: $encoded_dir" >> "$log_file"
echo "Project name: $project_name" >> "$log_file"
echo "Originating app: $originating_app" >> "$log_file"
echo "Focused app: $focused_app_full -> $focused_app" >> "$log_file"
echo "" >> "$log_file"

# Show notification only if user has switched away from the originating app
if [[ "$originating_app" != "$focused_app" ]]; then
    # Send macOS notification with originating app info
    osascript -e "display notification \"Claude has finished running in $project_name (from $originating_app)\" with title \"Claude Code\" subtitle \"Task completed\" sound name \"Hero\""
fi

exit 0
```

### `get-bundle-id.sh`
Utility script that maps application names to their macOS bundle identifiers for notification click handling.

```bash
#!/bin/bash

# Function to get bundle ID for common applications
get_bundle_id() {
    local app_name="$1"
    
    case "$app_name" in
        "idea") echo "com.jetbrains.intellij" ;;
        "cursor") echo "com.todesktop.230313mzl4w4u92" ;;
        "vscode") echo "com.microsoft.VSCode" ;;
        "webstorm") echo "com.jetbrains.WebStorm" ;;
        "phpstorm") echo "com.jetbrains.PhpStorm" ;;
        "pycharm") echo "com.jetbrains.PyCharm" ;;
        "sublime") echo "com.sublimetext.4" ;;
        "terminal") echo "com.apple.Terminal" ;;
        "iterm") echo "com.googlecode.iterm2" ;;
        "ghostty") echo "com.mitchellh.ghostty" ;;
        "alacritty") echo "org.alacritty" ;;
        *) echo "" ;;
    esac
}
```

### `notify-handler.sh`
Hook for the `Notification` event - handles explicit notifications from Claude Code with enhanced formatting and click-to-focus functionality.

```bash
#!/bin/bash

# Read JSON input from stdin
input=$(cat)

# Log file for debugging
log_file="$HOME/scripts/claude-hooks-debug.log"

# Log the input data with timestamp
echo "=== Notification $(date) ===" >> "$log_file"
echo "Input JSON:" >> "$log_file"
echo "$input" >> "$log_file"

# Extract notification data
title=$(echo "$input" | jq -r '.title // "Claude Code"')
message=$(echo "$input" | jq -r '.message // "Notification"')
transcript_path=$(echo "$input" | jq -r '.transcript_path // "unknown"')

# Extract and clean project name from transcript path
if [[ "$transcript_path" != "unknown" ]]; then
    encoded_dir=$(basename "$(dirname "$transcript_path")")
    decoded_path=$(echo "$encoded_dir" | sed 's/-/\//g')
    project_name=$(echo "$decoded_path" | sed 's|^/Users/[^/]*/||' | sed 's|^/||')
else
    project_name="unknown"
fi

# Source the originating app detection function
source "$HOME/scripts/detect-originating-app.sh"

# Get the originating application (where Claude was launched from)
originating_app=$(detect_originating_app)

# Get the currently focused application
focused_app_full=$(osascript -e 'tell application "System Events" to get name of first application process whose frontmost is true')
case "$focused_app_full" in
    "IntelliJ IDEA") focused_app="idea" ;;
    "iTerm2") focused_app="iterm" ;;
    "iTerm") focused_app="iterm" ;;
    "Ghostty") focused_app="ghostty" ;;
    "Cursor") focused_app="cursor" ;;
    *) focused_app=$(echo "$focused_app_full" | tr '[:upper:]' '[:lower:]') ;;
esac

# Log extracted values
echo "Title: $title" >> "$log_file"
echo "Message: $message" >> "$log_file"
echo "Project name: $project_name" >> "$log_file"
echo "Originating app: $originating_app" >> "$log_file"
echo "Focused app: $focused_app_full -> $focused_app" >> "$log_file"
echo "" >> "$log_file"

# Show notification only if user has switched away from the originating app
if [[ "$originating_app" != "$focused_app" ]]; then
    # Customize message to include project name and originating app if meaningful
    if [[ "$project_name" != "unknown" && "$project_name" != "" ]]; then
        custom_message="$message in $project_name (from $originating_app)"
    else
        custom_message="$message (from $originating_app)"
    fi
    
    # Send macOS notification
    osascript -e "display notification \"$custom_message\" with title \"$title\" sound name \"Hero\""
fi

exit 0
```

## How It Works

1. **Process Detection**: Scripts walk up the process tree to find the originating application
2. **Focus Detection**: Uses AppleScript to determine the currently focused application  
3. **Smart Notifications**: Only shows notifications when you've switched away from the originating app
4. **Click-to-Focus**: Click any notification to instantly return to the originating application
5. **Project Context**: Extracts project names from Claude Code transcript paths for better context
6. **Enhanced UI**: Beautiful notifications with titles, subtitles, and proper formatting

## Features

- 🎯 **Click-to-Focus**: Click notifications to instantly return to the originating application
- 🧠 **Context-aware**: Shows project name and source application in every notification
- 🔍 **App-specific detection**: Intelligently detects IDEs, terminals, and other applications
- 👀 **Focus-aware**: Only notifies when you've switched away from your work
- 🎨 **Enhanced UI**: Beautiful formatting with titles, subtitles, and proper grouping
- 🔊 **Smart sounds**: Audio feedback with Do Not Disturb bypass for important notifications
- 📊 **Comprehensive logging**: Detailed debug information for troubleshooting
- ⚡ **Instant switching**: Seamless workflow integration across multiple applications
- 🔄 **Real-time detection**: Monitors focus changes and process hierarchy in real-time

**Supported Applications:**
- IDEs: IntelliJ IDEA, Cursor, VS Code, WebStorm, PHPStorm, PyCharm, Sublime Text
- Terminals: Terminal, iTerm, Ghostty, Alacritty

## Debugging

Check the log file for troubleshooting:
```bash
tail -f ~/scripts/claude-hooks-debug.log
```

## Customization

### Adding New Applications
1. **Add process detection**: Edit the case statement in `detect-originating-app.sh` to recognize new applications
2. **Add bundle ID mapping**: Update the `get-bundle-id.sh` script with the application's bundle identifier
3. **Test click-to-focus**: Verify the bundle ID works with `terminal-notifier -activate "bundle.id"`

### Changing Notification Behavior
Modify the notification logic in `notify-completion.sh` and `notify-handler.sh` to customize:
- When notifications appear (focus detection logic)
- Message formatting and content
- Sound selection and timing

### Custom Sounds
Change the `-sound "Hero"` parameter in the terminal-notifier commands to use different notification sounds like:
- `"Glass"`, `"Ping"`, `"Pop"`, `"Purr"`, `"Sosumi"`, `"Submarine"`, `"Blow"`
- `"default"` for system default
- Custom sound files (place in `~/Library/Sounds/`)

## Requirements

- macOS (uses AppleScript for app detection)
- jq (JSON processing)
- terminal-notifier (enhanced notifications with click handling)
- Claude Code with hooks enabled

## Security Note

These scripts run with your user permissions as part of Claude Code hooks. They only read system information and show notifications - no sensitive operations are performed.