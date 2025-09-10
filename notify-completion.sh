#!/bin/bash

# Claude Code completion notification hook
# Triggers when Claude Code finishes a conversation

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"
source "$SCRIPT_DIR/universal-window.sh"

# Read JSON input from stdin
input=$(cat)

# Log the hook trigger
log_message "COMPLETION" "Input JSON: $input"

# Extract data from JSON
transcript_path=$(echo "$input" | jq -r '.transcript_path // "unknown"')
project_name=$(extract_project_name "$transcript_path")
originating_app=$(detect_originating_app)
focused_app=$(get_focused_app)

# Log extracted values
log_message "ANALYSIS" "Project: $project_name | Originating: $originating_app | Focused: $focused_app"

# Send notification only if user has switched away from the originating app/window
if should_notify_with_windows "$originating_app" "$focused_app"; then
    bundle_id=$(get_bundle_id "$originating_app")
    
    # Prepare notification content
    if [[ -n "$project_name" && "$project_name" != "unknown" ]]; then
        message="Claude has finished running in $project_name"
    else
        message="Claude has finished running"
    fi
    
    # Enhanced subtitle with window information
    subtitle="Task completed from $(get_app_with_window_info "$originating_app")"
    
    # Send the notification
    send_notification "Claude Code" "$subtitle" "$message" "$bundle_id" "claude-completion"
else
    log_message "SKIPPED" "User still focused on originating app/window - no notification sent"
fi

exit 0