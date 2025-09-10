#!/bin/bash

# Universal Window Detection System
# Minimal, app-agnostic multi-window detection

# Get window identifier for any application
get_window_id() {
    local app_type="$1"
    local mode="${2:-originating}"  # originating|focused
    
    case "$mode" in
        "originating") get_originating_window_id "$app_type" ;;
        "focused") get_focused_window_id "$app_type" ;;
        *) get_originating_window_id "$app_type" ;;  # Default to originating for invalid modes
    esac
}

# Get window where Claude process originated (process-based, always works)
get_originating_window_id() {
    local app_type="$1"
    local pid=$$
    
    # Strategy 1: Look for unique process arguments
    while [[ $pid -gt 1 ]]; do
        local cmd=$(ps -o command= -p "$pid" 2>/dev/null)
        
        # Extract any window-specific identifiers from command line
        local window_id=$(echo "$cmd" | grep -oE -- '--[a-z-]*window[a-z-]*[=:][a-zA-Z0-9:-]+' | head -1)
        if [[ -n "$window_id" ]]; then
            echo "$app_type:$window_id"
            return
        fi
        
        pid=$(ps -o ppid= -p "$pid" 2>/dev/null | xargs)
        [[ -z "$pid" ]] && break
    done
    
    # Strategy 2: Use working directory as window identifier
    local workspace=$(basename "$PWD" 2>/dev/null)
    if [[ -n "$workspace" && "$workspace" != "/" ]]; then
        echo "$app_type:$workspace"
    else
        echo "$app_type:unknown"
    fi
}

# Get currently focused window (OSA-based, universal for GUI apps)  
get_focused_window_id() {
    local app_type="$1"
    
    # Get the display name for OSA
    local display_name=$(get_app_display_name "$app_type")
    [[ -z "$display_name" ]] && { echo "$app_type:unknown"; return; }
    
    # Universal OSA window title detection
    local window_title=$(osascript -e "tell application \"System Events\" to tell process \"$display_name\" to get title of front window" 2>/dev/null)
    
    if [[ -n "$window_title" ]]; then
        # Extract meaningful identifier from window title
        local window_id=$(extract_window_identifier "$window_title")
        echo "$app_type:$window_id"
    else
        echo "$app_type:unknown"
    fi
}

# Convert internal app names to display names for OSA
get_app_display_name() {
    local app_type="$1"
    
    case "$app_type" in
        "vscode") echo "Code" ;;
        "iterm") echo "iTerm2" ;;
        "terminal") echo "Terminal" ;;
        "cursor") echo "Cursor" ;;
        "idea") echo "IntelliJ IDEA" ;;
        "chrome") echo "Google Chrome" ;;
        "firefox") echo "Firefox" ;;
        "safari") echo "Safari" ;;
        "finder") echo "Finder" ;;
        *) echo "" ;;
    esac
}

# Extract meaningful window identifier from window title
extract_window_identifier() {
    local title="$1"
    
    # Remove common prefixes and extract meaningful part
    # Pattern 1: "App Name — workspace" or "App Name – workspace" (em-dash/en-dash only)
    if [[ "$title" == *[—–]* ]]; then
        local workspace="${title##*[—–] }"  # Get everything after last em-dash/en-dash + space
        workspace=$(echo "$workspace" | xargs)  # trim whitespace
        [[ -n "$workspace" ]] && { echo "$workspace"; return; }
    fi
    
    # Pattern 2: Use full title if no separator found
    echo "$title"
}

# Enhanced notification decision with window awareness
should_notify_with_windows() {
    local originating_app="$1"
    local focused_app="$2"
    
    # Different apps = always notify (preserve existing behavior)
    if [[ "$originating_app" != "$focused_app" ]]; then
        return 0  # Should notify
    fi
    
    # Same app = check windows
    local orig_window=$(get_window_id "$originating_app" "originating")
    local focused_window=$(get_window_id "$focused_app" "focused")
    
    # Log window comparison for debugging
    log_message "WINDOW_CHECK" "App: $originating_app | Originating: $orig_window | Focused: $focused_window"
    
    # Notify if different windows or unknown originating window
    [[ "$orig_window" != "$focused_window" || "$orig_window" == *":unknown" ]]
}

# Get enhanced app info with window context for notifications
get_app_with_window_info() {
    local app_type="$1"
    local window_id=$(get_window_id "$app_type" "focused")
    
    # Extract just the window part (after the colon)
    local window_name="${window_id#*:}"
    
    if [[ -n "$window_name" && "$window_name" != "unknown" ]]; then
        echo "$app_type ($window_name)"
    else
        echo "$app_type"
    fi
}

# Export functions for use in other scripts
export -f get_window_id get_originating_window_id get_focused_window_id
export -f get_app_display_name extract_window_identifier 
export -f should_notify_with_windows get_app_with_window_info