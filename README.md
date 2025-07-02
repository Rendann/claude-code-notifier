# Claude Code Enhanced Notification System
<img width="351" alt="image" src="https://github.com/user-attachments/assets/c5e98d8d-75b1-4ece-80e7-f9a259cdc9dd" />
<img width="351" alt="image" src="https://github.com/user-attachments/assets/5073f30d-5817-47b4-9585-8982bd518edf" />
<img width="351" alt="image" src="https://github.com/user-attachments/assets/292c8c08-186f-432b-9c19-53b9e784d8dd" />


Smart, click-to-focus notification system for Claude Code that delivers context-aware notifications with seamless app switching functionality.

## Overview

This enhanced notification system transforms Claude Code into a fully integrated development tool using the [hooks feature](https://docs.anthropic.com/en/docs/claude-code/hooks). The system intelligently detects your workflow context and delivers beautiful, actionable notifications that you can click to instantly return to your work.

## ✨ Features

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
Core utility that walks up the process tree to identify the application that launched Claude Code. Recognizes common IDEs (IntelliJ, Cursor, VS Code, etc.), terminals (Ghostty, iTerm, Terminal), and other development tools by examining process names in the parent hierarchy.

### `get-bundle-id.sh`
Maps application names to their macOS bundle identifiers, enabling the click-to-focus functionality. Contains bundle IDs for popular development applications like `com.jetbrains.intellij`, `com.todesktop.230313mzl4w4u92` (Cursor), `com.mitchellh.ghostty`, etc.

### `notify-completion.sh`
Hook for the `Stop` event that triggers when Claude Code finishes a conversation. Extracts project context from transcript paths, detects the currently focused app, and sends enhanced notifications with click-to-focus functionality using `terminal-notifier`.

### `notify-handler.sh`
Hook for the `Notification` event that handles explicit notifications from Claude Code (like permission requests). Provides enhanced formatting, project context, and click-to-focus functionality for immediate notifications.

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
