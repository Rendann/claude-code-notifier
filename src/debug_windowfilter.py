#!/usr/bin/env python3
"""
Debug script to check what windowfilter cross-space detection actually finds
"""

import subprocess

def debug_windowfilter():
    hs_cli = "/Applications/Hammerspoon.app/Contents/Frameworks/hs/hs"
    
    script = """
    local windowfilter = require('hs.window.filter')
    local spaces = require('hs.spaces')
    
    print('=== DEBUGGING CROSS-SPACE WINDOWFILTER ===')
    print('Current space: ' .. spaces.focusedSpace())
    print('')
    
    -- Test cross-space windowfilter
    print('Cross-space windowfilter results:')
    local wf_cross = windowfilter.new()
    wf_cross:setCurrentSpace(false)
    local crossWindows = wf_cross:getWindows()
    
    print('Cross-space windows found: ' .. #crossWindows)
    for i, win in pairs(crossWindows) do
        local winID = win:id()
        local winApp = win:application():name()
        local winTitle = win:title() or 'NO_TITLE'
        print('WIN' .. i .. ': ID=' .. winID .. ' App=' .. winApp .. ' Title=' .. winTitle)
    end
    
    print('')
    print('=== COMPARISON: ALL WINDOWS ===')
    local allWindows = hs.window.allWindows()
    print('All windows found: ' .. #allWindows)
    for i, win in pairs(allWindows) do
        local winID = win:id()
        local winApp = win:application():name()
        local winTitle = win:title() or 'NO_TITLE'
        print('ALL' .. i .. ': ID=' .. winID .. ' App=' .. winApp .. ' Title=' .. winTitle)
    end
    """
    
    try:
        result = subprocess.run([hs_cli, "-c", script], capture_output=True, text=True, timeout=10)
        print("Exit code:", result.returncode)
        print("Output:")
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_windowfilter()