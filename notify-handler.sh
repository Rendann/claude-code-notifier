#!/bin/bash

# Claude Code notification handler hook
# Handles explicit notifications from Claude Code (like permission requests)

# Source common utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

# Read JSON input from stdin
input=$(cat)

# Log the hook trigger
log_message "NOTIFICATION" "Input JSON: $input"

# Extract notification data
title=$(echo "$input" | jq -r '.title // "Claude Code"')
message=$(echo "$input" | jq -r '.message // "Notification"')
transcript_path=$(echo "$input" | jq -r '.transcript_path // "unknown"')

# Extract context
project_name=$(extract_project_name "$transcript_path")
originating_app=$(detect_originating_app)
focused_app=$(get_focused_app)

# Log extracted values
log_message "ANALYSIS" "Title: $title | Message: $message | Project: $project_name | Originating: $originating_app | Focused: $focused_app"

# Send notification only if user has switched away from the originating app
if should_notify "$originating_app" "$focused_app"; then
    bundle_id=$(get_bundle_id "$originating_app")
    
    # Customize message to include project context
    if [[ -n "$project_name" && "$project_name" != "unknown" ]]; then
        custom_message="$message in $project_name"
    else
        custom_message="$message"
    fi
    
    subtitle="From $originating_app"
    
    # Send the notification
    send_notification "$title" "$subtitle" "$custom_message" "$bundle_id" "claude-notification"
else
    log_message "SKIPPED" "User still focused on originating app - no notification sent"
fi

exit 0