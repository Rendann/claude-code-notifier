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