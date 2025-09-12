#!/bin/bash

# focus_window_hook.sh - Claude Code Stop Hook  
# Reads saved window ID and focuses that window immediately

set +e

HAMMERSPOON_CLI="/Applications/Hammerspoon.app/Contents/Frameworks/hs/hs"

# Read and parse JSON input to get session_id
if [[ ! -t 0 ]]; then
    HOOK_DATA=$(cat)
    SESSION_ID=$(echo "$HOOK_DATA" | jq -r '.session_id' 2>/dev/null)
else
    SESSION_ID="interactive"
fi

# Create session-specific directory and file paths
SESSION_DIR="/tmp/claude_window_session"
SESSION_FILE="$SESSION_DIR/$SESSION_ID"

# Validate prerequisites
[[ -f "$HAMMERSPOON_CLI" && -n "$SESSION_ID" ]] || exit 1

# Validate session file exists
[[ ! -f "$SESSION_FILE" ]] && exit 1

# Load window ID from session file
source "$SESSION_FILE"

# Focus window using cross-space detection
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

# Exit with success regardless of focus result (don't show Claude Code errors)
exit 0