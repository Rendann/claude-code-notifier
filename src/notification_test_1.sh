#!/bin/bash

# notification_test_1.sh - Test notifications with click-to-focus
# Captures window ID, sends notification, clicking notification focuses original window

set +e

HAMMERSPOON_CLI="/Applications/Hammerspoon.app/Contents/Frameworks/hs/hs"
TERMINAL_NOTIFIER="/opt/homebrew/bin/terminal-notifier"

# Check prerequisites
if [[ ! -f "$HAMMERSPOON_CLI" ]]; then
    echo "❌ Hammerspoon CLI not found"
    exit 1
fi

if [[ ! -f "$TERMINAL_NOTIFIER" ]]; then
    echo "❌ terminal-notifier not found at $TERMINAL_NOTIFIER"
    exit 1
fi

echo "🔔 Notification Click-to-Focus Test"
echo "=================================="

# Phase 1: Capture currently focused window ID
echo "📍 Capturing current window..."

WINDOW_ID=$("$HAMMERSPOON_CLI" -c "local w=hs.window.focusedWindow(); print(w and w:id() or 'ERROR')" 2>/dev/null)

if [[ "$WINDOW_ID" == "ERROR" || -z "$WINDOW_ID" ]]; then
    echo "❌ Failed to capture window ID"
    exit 1
fi

echo "✅ Captured window ID: $WINDOW_ID"

# Phase 2: 5-second countdown delay
echo ""
echo "⏳ 5-second countdown (switch to another window to test):"
for i in {5..1}; do
    echo "   $i..."
    sleep 1
done
echo "   Sending notification!"

# Phase 3: Create Hammerspoon command for click action
HAMMERSPOON_COMMAND="$HAMMERSPOON_CLI -c \"
local wf=require('hs.window.filter').new():setCurrentSpace(nil)
for _,w in pairs(wf:getWindows()) do
  if w:id()==$WINDOW_ID then
    w:focus()
    require('hs.timer').usleep(300000)
    return
  end
end\""

# Phase 4: Send notification with click-to-execute
echo ""
echo "📤 Sending notification..."

"$TERMINAL_NOTIFIER" \
    -title "Claude Code Test" \
    -subtitle "Window Focus Test" \
    -message "Task completed - click to return to original window" \
    -sound "default" \
    -execute "$HAMMERSPOON_COMMAND"

echo "✅ Notification sent!"
echo ""
echo "📋 Instructions:"
echo "   1. Click the notification that appeared"
echo "   2. It should focus the original window (ID: $WINDOW_ID)"
echo ""
echo "Test complete."