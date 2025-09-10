#!/bin/bash

# Common utilities for Claude Code notification system
# This file contains shared functions used by all notification scripts

# Source configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/config.sh"


# Function to log messages with timestamp and auto-rotation
log_message() {
    local level="$1"
    shift
    
    # Check if log rotation is needed before writing
    if [[ -f "$CLAUDE_NOTIFICATIONS_LOG_FILE" ]]; then
        local line_count=$(wc -l < "$CLAUDE_NOTIFICATIONS_LOG_FILE" 2>/dev/null || echo 0)
        if [[ $line_count -gt $CLAUDE_NOTIFICATIONS_MAX_LOG_LINES ]]; then
            # Rotate: keep only the last KEEP_LOG_LINES lines
            tail -n "$CLAUDE_NOTIFICATIONS_KEEP_LOG_LINES" "$CLAUDE_NOTIFICATIONS_LOG_FILE" > "$CLAUDE_NOTIFICATIONS_LOG_FILE.tmp" 2>/dev/null && \
            mv "$CLAUDE_NOTIFICATIONS_LOG_FILE.tmp" "$CLAUDE_NOTIFICATIONS_LOG_FILE" 2>/dev/null
            
            # Add rotation marker
            {
                echo "=== LOG ROTATED $(date) ==="
                echo "Trimmed log from $line_count to $CLAUDE_NOTIFICATIONS_KEEP_LOG_LINES lines"
                echo ""
            } >> "$CLAUDE_NOTIFICATIONS_LOG_FILE"
        fi
    fi
    
    # Write the actual log message
    echo "=== $level $(date) ===" >> "$CLAUDE_NOTIFICATIONS_LOG_FILE"
    echo "$@" >> "$CLAUDE_NOTIFICATIONS_LOG_FILE"
    echo "" >> "$CLAUDE_NOTIFICATIONS_LOG_FILE"
}

# Function to detect the originating application by walking up process tree
detect_originating_app() {
    local current_pid=$$
    
    while [[ $current_pid -gt 1 ]]; do
        local process_name=$(ps -o comm= -p "$current_pid" 2>/dev/null)
        
        case "$process_name" in
            *"idea"*|*"IntelliJ"*) echo "idea"; return ;;
            *"Cursor"*) echo "cursor"; return ;;
            *"code"*|*"Code"*) echo "vscode"; return ;;
            *"WebStorm"*) echo "webstorm"; return ;;
            *"PHPStorm"*) echo "phpstorm"; return ;;
            *"PyCharm"*) echo "pycharm"; return ;;
            *"Sublime"*) echo "sublime"; return ;;
            *"Terminal"*) echo "terminal"; return ;;
            *"iTerm"*) echo "iterm"; return ;;
            *"Ghostty"*) echo "ghostty"; return ;;
            *"Alacritty"*) echo "alacritty"; return ;;
        esac
        
        current_pid=$(ps -o ppid= -p "$current_pid" 2>/dev/null | xargs)
        [[ -z "$current_pid" ]] && break
    done
    
    echo "unknown"
}

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

# Function to get currently focused application
get_focused_app() {
    local app_name=$(lsappinfo list | grep ": (in front)" | sed 's/.*"\([^"]*\)".*/\1/')
    [[ -z "$app_name" ]] && { echo "unknown"; return; }
    
    case "$app_name" in
        "IntelliJ IDEA") echo "idea" ;;
        "iTerm2"|"iTerm") echo "iterm" ;;
        "Visual Studio Code"|"Code") echo "vscode" ;;
        "Cursor") echo "cursor" ;;
        "Ghostty") echo "ghostty" ;;
        "Terminal") echo "terminal" ;;
        *) echo "$app_name" | tr '[:upper:]' '[:lower:]' ;;
    esac
}

# Function to extract project name from transcript path
extract_project_name() {
    local transcript_path="$1"
    
    if [[ "$transcript_path" == "unknown" || -z "$transcript_path" ]]; then
        echo "unknown"
        return
    fi
    
    local encoded_dir=$(basename "$(dirname "$transcript_path")")
    local decoded_path=$(echo "$encoded_dir" | sed 's/-/\//g')
    echo "$decoded_path" | sed 's|^/Users/[^/]*/||' | sed 's|^/||'
}

# Function to send enhanced notification
send_notification() {
    local title="$1"
    local subtitle="$2"
    local message="$3"
    local bundle_id="$4"
    local group_prefix="$5"
    
    local group_id="${group_prefix}-$(date +%s)"
    local cmd="\"$CLAUDE_NOTIFICATIONS_TERMINAL_NOTIFIER_PATH\" -group \"$group_id\" -title \"$title\" -subtitle \"$subtitle\" -message \"$message\" -sound \"Hero\" -ignoreDnD"
    
    if [[ -n "$bundle_id" ]]; then
        cmd="$cmd -activate \"$bundle_id\""
    fi
    
    log_message "COMMAND" "Running: $cmd"
    
    local output=$(eval "$cmd" 2>&1)
    log_message "OUTPUT" "terminal-notifier output: $output"
    
    if [[ -n "$bundle_id" ]]; then
        log_message "SUCCESS" "Sent notification with bundle ID: $bundle_id"
    else
        log_message "SUCCESS" "Sent basic notification"
    fi
}

# Function to check what app is "in front"
is_app_in_front() {
    local app_name="$1"
    
    case "$app_name" in
        "iterm"|"iTerm2") lsappinfo list | grep -q '"iTerm2".*: (in front)' ;;
        "terminal"|"Terminal") lsappinfo list | grep -q '"Terminal".*: (in front)' ;;
        "vscode") lsappinfo list | grep -Eq '"(Code|Visual Studio Code)".*: \(in front\)' ;;
        "cursor") lsappinfo list | grep -q '"Cursor".*: (in front)' ;;
        "idea") lsappinfo list | grep -q '"IntelliJ IDEA".*: (in front)' ;;
        *) return 1 ;;  # Unknown apps default to "not in front"
    esac
}

# Function to check if notification should be sent
should_notify() {
    local originating_app="$1"
    ! is_app_in_front "$originating_app"
}

# Export all functions
export -f log_message detect_originating_app get_bundle_id get_focused_app extract_project_name send_notification should_notify is_app_in_front