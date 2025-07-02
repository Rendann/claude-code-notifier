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

# Export the function so it can be sourced by other scripts
export -f get_bundle_id

# If script is run directly, test the function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ -n "$1" ]]; then
        echo "Bundle ID for $1: $(get_bundle_id "$1")"
    else
        echo "Usage: $0 <app_name>"
        echo "Example: $0 cursor"
    fi
fi