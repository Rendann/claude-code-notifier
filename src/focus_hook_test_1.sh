#!/bin/bash

# focus_hook_test_1.sh - Minimal Window Focus Test
# Captures window ID, waits 5 seconds, then refocuses using cross-space detection

set +e  # Don't exit on error

HAMMERSPOON_CLI="/Applications/Hammerspoon.app/Contents/Frameworks/hs/hs"

# Check Hammerspoon CLI
if [[ ! -f "$HAMMERSPOON_CLI" ]]; then
    echo "❌ Hammerspoon CLI not found"
    exit 1
fi

# Phase 1: Capture focused window ID
echo "📍 Capturing window ID..."

CAPTURE_SCRIPT='
local win = hs.window.focusedWindow()
if win then
    print("WINDOW_ID:" .. win:id())
else
    print("ERROR:No focused window")
end'

CAPTURE_OUTPUT=$("$HAMMERSPOON_CLI" -c "$CAPTURE_SCRIPT" 2>&1)
WINDOW_ID=$(echo "$CAPTURE_OUTPUT" | grep "^WINDOW_ID:" | cut -d':' -f2)

if [[ -z "$WINDOW_ID" ]]; then
    echo "❌ Failed to capture window ID"
    exit 1
fi

echo "✅ Captured window ID: $WINDOW_ID"

# Phase 2: Wait 5 seconds
echo "⏳ Waiting 5 seconds..."
sleep 5

# Phase 3: Focus using cross-space detection
echo "🔄 Attempting focus..."

FOCUS_SCRIPT="
local windowfilter = require('hs.window.filter')
local targetID = $WINDOW_ID

local wf_all = windowfilter.new()
wf_all:setCurrentSpace(nil)
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

# Report result
case "$FOCUS_RESULT" in
    "SUCCESS")
        echo "🎉 SUCCESS"
        ;;
    *)
        echo "❌ FAILED: $FOCUS_RESULT"
        ;;
esac