#!/bin/bash

# focus_window_hook.sh - Claude Code Hook for Window Focus Return
# 
# This script captures the currently focused window ID, waits 5 seconds,
# then uses Hammerspoon cross-space detection to refocus that window.
#
# Usage: ./focus_window_hook.sh
# For Claude Code: Add as Stop hook in settings.json

# Don't exit on error - we want to see what failed
set +e

# Claude Code passes JSON data to hooks via stdin - consume it to avoid interference
if [ -t 0 ]; then
    # Running interactively
    HOOK_DATA=""
else
    # Running as hook - read and discard the JSON input
    HOOK_DATA=$(cat)
fi

HAMMERSPOON_CLI="/Applications/Hammerspoon.app/Contents/Frameworks/hs/hs"

# Log file for debugging
LOG_FILE="/tmp/claude_focus_hook.log"
echo "🎯 Claude Code Window Focus Hook - $(date)" | tee "$LOG_FILE"
echo "================================" | tee -a "$LOG_FILE"

# Log hook data for debugging
if [[ -n "$HOOK_DATA" ]]; then
    echo "Hook data received (first 100 chars): ${HOOK_DATA:0:100}..." | tee -a "$LOG_FILE"
else
    echo "No hook data (running interactively)" | tee -a "$LOG_FILE"
fi

# Check if Hammerspoon CLI exists
if [[ ! -f "$HAMMERSPOON_CLI" ]]; then
    echo "❌ Hammerspoon CLI not found at $HAMMERSPOON_CLI" | tee -a "$LOG_FILE"
    exit 1
fi

# Phase 1: Capture focused window ID
echo "📍 Capturing focused window..." | tee -a "$LOG_FILE"

CAPTURE_SCRIPT='
local win = hs.window.focusedWindow()
if win then
    local winID = win:id()
    local app = win:application():name()
    local title = win:title() or "NO_TITLE"
    
    print("WINDOW_ID:" .. winID)
    print("WINDOW_APP:" .. app)
    print("WINDOW_TITLE:" .. title)
else
    print("ERROR:No focused window")
end'

# Capture both stdout and stderr
CAPTURE_OUTPUT=$("$HAMMERSPOON_CLI" -c "$CAPTURE_SCRIPT" 2>&1)
CAPTURE_EXIT_CODE=$?

echo "Capture exit code: $CAPTURE_EXIT_CODE" | tee -a "$LOG_FILE"
echo "Capture output: $CAPTURE_OUTPUT" | tee -a "$LOG_FILE"

# Parse captured window info
WINDOW_ID=$(echo "$CAPTURE_OUTPUT" | grep "^WINDOW_ID:" | cut -d':' -f2)
WINDOW_APP=$(echo "$CAPTURE_OUTPUT" | grep "^WINDOW_APP:" | cut -d':' -f2)
WINDOW_TITLE=$(echo "$CAPTURE_OUTPUT" | grep "^WINDOW_TITLE:" | cut -d':' -f2)

if [[ -z "$WINDOW_ID" ]]; then
    echo "❌ Failed to capture window ID" | tee -a "$LOG_FILE"
    exit 1
fi

echo "✅ Captured: $WINDOW_APP (ID: $WINDOW_ID)" | tee -a "$LOG_FILE"

# Phase 2: Wait 5 seconds
echo "⏳ Waiting 5 seconds..." | tee -a "$LOG_FILE"
sleep 5

# Phase 3: Focus the window using cross-space detection
echo "🔄 Attempting to refocus window..." | tee -a "$LOG_FILE"

FOCUS_SCRIPT="
local windowfilter = require('hs.window.filter')
local targetID = $WINDOW_ID

-- Use windowfilter with setCurrentSpace(nil) to ignore Mission Control Spaces
-- This shows windows from ALL spaces (current + other spaces)
local wf_all = windowfilter.new()
wf_all:setCurrentSpace(nil)  -- nil = ignore Mission Control Spaces (ALL spaces)
local allSpaceWindows = wf_all:getWindows()

local targetWindow = nil
for _, win in pairs(allSpaceWindows) do
    if win:id() == targetID then
        targetWindow = win
        break
    end
end

if targetWindow then
    local success = targetWindow:focus()
    if success then
        local timer = require('hs.timer')
        timer.usleep(300000)
        local newFocused = hs.window.focusedWindow()
        if newFocused and newFocused:id() == targetID then
            print('SUCCESS')
        else
            print('PARTIAL')
        end
    else
        print('FAILED')
    end
else
    print('NOT_FOUND')
end"

FOCUS_RESULT=$("$HAMMERSPOON_CLI" -c "$FOCUS_SCRIPT" 2>&1)
FOCUS_EXIT_CODE=$?

echo "Focus exit code: $FOCUS_EXIT_CODE" | tee -a "$LOG_FILE"
echo "Focus result: $FOCUS_RESULT" | tee -a "$LOG_FILE"

# Report results
case "$FOCUS_RESULT" in
    "SUCCESS")
        echo "🎉 SUCCESS: Refocused $WINDOW_APP"
        ;;
    "PARTIAL")
        echo "⚠️  PARTIAL: Focus command ran but verification failed"
        ;;
    "FAILED")
        echo "❌ FAILED: Focus command failed"
        ;;
    "NOT_FOUND")
        echo "❌ NOT_FOUND: Window not visible (recency limitation)"
        ;;
    *)
        echo "❌ UNKNOWN: Unexpected result: $FOCUS_RESULT"
        ;;
esac

echo "Hook execution complete." | tee -a "$LOG_FILE"
echo "Log saved to: $LOG_FILE" | tee -a "$LOG_FILE"

# Always exit 0 so Claude Code doesn't show error
exit 0