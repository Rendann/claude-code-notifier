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

# Source the bundle ID mapping function
source "$HOME/scripts/get-bundle-id.sh"

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
    # Get bundle ID for the originating app
    bundle_id=$(get_bundle_id "$originating_app")
    
    # Customize message to include project name and originating app if meaningful
    if [[ "$project_name" != "unknown" && "$project_name" != "" ]]; then
        custom_message="$message in $project_name"
        subtitle="From $originating_app"
    else
        custom_message="$message"
        subtitle="From $originating_app"
    fi
    
    # Send enhanced notification with click action
    if [[ -n "$bundle_id" ]]; then
        echo "Running terminal-notifier command:" >> "$log_file"
        echo "terminal-notifier -group \"claude-notification-$(date +%s)\" -title \"$title\" -subtitle \"$subtitle\" -message \"$custom_message\" -activate \"$bundle_id\" -sound \"Hero\" -ignoreDnD" >> "$log_file"
        
        terminal_output=$(/opt/homebrew/bin/terminal-notifier \
            -group "claude-notification-$(date +%s)" \
            -title "$title" \
            -subtitle "$subtitle" \
            -message "$custom_message" \
            -activate "$bundle_id" \
            -sound "Hero" \
            -ignoreDnD 2>&1)
        
        echo "terminal-notifier output: $terminal_output" >> "$log_file"
        echo "Sent notification with bundle ID: $bundle_id" >> "$log_file"
    else
        echo "Running terminal-notifier command (no bundle ID):" >> "$log_file"
        echo "terminal-notifier -group \"claude-notification-$(date +%s)\" -title \"$title\" -subtitle \"$subtitle\" -message \"$custom_message\" -sound \"Hero\" -ignoreDnD" >> "$log_file"
        
        terminal_output=$(/opt/homebrew/bin/terminal-notifier \
            -group "claude-notification-$(date +%s)" \
            -title "$title" \
            -subtitle "$subtitle" \
            -message "$custom_message" \
            -sound "Hero" \
            -ignoreDnD 2>&1)
        
        echo "terminal-notifier output: $terminal_output" >> "$log_file"
        echo "Sent basic notification (no bundle ID for $originating_app)" >> "$log_file"
    fi
fi

exit 0
