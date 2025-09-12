#!/bin/bash

# active_focus_test_1.sh - Test if user is still on the original window
# Captures window ID, waits 5 seconds, then checks if user is still focused on same window

set +e

HAMMERSPOON_CLI="/Applications/Hammerspoon.app/Contents/Frameworks/hs/hs"

# Check Hammerspoon CLI exists
if [[ ! -f "$HAMMERSPOON_CLI" ]]; then
    echo "❌ Hammerspoon CLI not found"
    exit 1
fi

echo "🎯 Active Window Detection Test"
echo "==============================="

# Phase 1: Capture currently focused window ID
echo "📍 Capturing current window..."

ORIGINAL_ID=$("$HAMMERSPOON_CLI" -c "local w=hs.window.focusedWindow(); print(w and w:id() or 'ERROR')" 2>/dev/null)

if [[ "$ORIGINAL_ID" == "ERROR" || -z "$ORIGINAL_ID" ]]; then
    echo "❌ Failed to capture window ID"
    exit 1
fi

echo "✅ Original window ID: $ORIGINAL_ID"

# Phase 2: 5-second countdown delay
echo ""
echo "⏳ 5-second countdown (switch windows to test):"
for i in {5..1}; do
    echo "   $i..."
    sleep 1
done
echo "   Testing now!"

# Phase 3: Check current focused window
echo ""
echo "🔍 Checking current focus..."

CURRENT_ID=$("$HAMMERSPOON_CLI" -c "local w=hs.window.focusedWindow(); print(w and w:id() or 'ERROR')" 2>/dev/null)

if [[ "$CURRENT_ID" == "ERROR" || -z "$CURRENT_ID" ]]; then
    echo "❌ Failed to get current window ID"
    exit 1
fi

echo "📱 Current window ID: $CURRENT_ID"

# Phase 4: Compare and report
echo ""
echo "🧮 Comparison:"
echo "   Original: $ORIGINAL_ID"
echo "   Current:  $CURRENT_ID"

if [[ "$ORIGINAL_ID" == "$CURRENT_ID" ]]; then
    echo ""
    echo "🟢 ACTIVE - User is still on the original window"
    echo "   → No notification needed"
else
    echo ""
    echo "🔴 INACTIVE - User switched to a different window"  
    echo "   → Notification should be sent"
fi

echo ""
echo "Test complete."