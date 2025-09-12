#!/bin/bash
# Streamlined Window Focus Hook - Capture, wait, refocus
set +e

HAMMERSPOON_CLI="/Applications/Hammerspoon.app/Contents/Frameworks/hs/hs"
[[ ! -f "$HAMMERSPOON_CLI" ]] && { echo "❌ Hammerspoon CLI not found"; exit 1; }

# Capture window ID
echo "📍 Capturing..."
WINDOW_ID=$("$HAMMERSPOON_CLI" -c "local w=hs.window.focusedWindow(); print(w and w:id() or 'ERROR')" 2>/dev/null | grep -v ERROR)
[[ -z "$WINDOW_ID" ]] && { echo "❌ No window"; exit 1; }
echo "✅ ID: $WINDOW_ID"

# Wait and refocus
echo "⏳ Waiting 5s..."
sleep 5
echo "🔄 Refocusing..."

RESULT=$("$HAMMERSPOON_CLI" -c "
local wf=require('hs.window.filter').new():setCurrentSpace(nil)
for _,w in pairs(wf:getWindows()) do
  if w:id()==$WINDOW_ID then
    w:focus()
    require('hs.timer').usleep(300000)
    local f=hs.window.focusedWindow()
    print(f and f:id()==$WINDOW_ID and 'SUCCESS' or 'PARTIAL')
    return
  end
end
print('NOT_FOUND')" 2>/dev/null)

[[ "$RESULT" == "SUCCESS" ]] && echo "🎉 SUCCESS" || echo "❌ FAILED: $RESULT"