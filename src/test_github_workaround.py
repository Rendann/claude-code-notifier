#!/usr/bin/env python3
"""
test_github_workaround.py - Test GitHub issue #3276 workaround

Based on GitHub issue: https://github.com/Hammerspoon/hammerspoon/issues/3276

The issue reveals that hs.window.filter has a bug where it only returns:
- All windows in current space  
- Only the LAST FOCUSED window from other spaces

Workaround suggested by @Sleepful:
```lua
self.wf_current = hs.window.filter.new()
self.wf_current:setCurrentSpace(true)
self.wf_other = hs.window.filter.new() 
self.wf_other:setCurrentSpace(false)
```

This might let us find ai_advisory_system if it was the last focused window on space 6!
"""

import subprocess
import time

def find_hammerspoon_cli():
    """Find Hammerspoon CLI."""
    return "/Applications/Hammerspoon.app/Contents/Frameworks/hs/hs"

def test_current_space_filter():
    """Test the setCurrentSpace workaround from GitHub issue."""
    print("🔧 Testing GitHub Issue #3276 Workaround")
    print("=" * 40)
    print("🎯 Testing setCurrentSpace(true) vs setCurrentSpace(false)")
    
    hs_cli = find_hammerspoon_cli()
    
    script = '''
    local windowfilter = require("hs.window.filter")
    local spaces = require("hs.spaces")
    
    print("Current space: " .. spaces.focusedSpace())
    
    -- Method from GitHub issue
    print("\\n📋 Creating separate filters for current vs other spaces...")
    
    -- Filter for current space windows
    local wf_current = windowfilter.new('Code')
    wf_current:setCurrentSpace(true)
    
    -- Filter for other space windows  
    local wf_other = windowfilter.new('Code')
    wf_other:setCurrentSpace(false)
    
    print("✅ Filters created")
    
    -- Get windows from current space
    print("\\n🏠 CURRENT SPACE WINDOWS:")
    local currentWindows = wf_current:getWindows()
    print("Count: " .. #currentWindows)
    
    for i, win in pairs(currentWindows) do
        local title = win:title() or "NO TITLE"
        local winSpaces = spaces.windowSpaces(win:id())
        local spaceInfo = winSpaces and winSpaces[1] or "UNKNOWN"
        print("  " .. i .. ": \\"" .. title .. "\\" (Space " .. spaceInfo .. ")")
    end
    
    -- Get windows from other spaces  
    print("\\n🌌 OTHER SPACE WINDOWS:")
    local otherWindows = wf_other:getWindows()
    print("Count: " .. #otherWindows)
    
    for i, win in pairs(otherWindows) do
        local title = win:title() or "NO TITLE"
        local winSpaces = spaces.windowSpaces(win:id())
        local spaceInfo = winSpaces and winSpaces[1] or "UNKNOWN"
        print("  " .. i .. ": \\"" .. title .. "\\" (Space " .. spaceInfo .. ")")
        
        -- CHECK FOR AI_ADVISORY_SYSTEM
        if string.find(string.lower(title), "ai_advisory") then
            print("  🎉 FOUND AI_ADVISORY_SYSTEM IN OTHER SPACES!")
            print("     This means the workaround works!")
        end
    end
    
    -- Summary
    local totalFound = #currentWindows + #otherWindows
    print("\\n📊 SUMMARY:")
    print("Current space windows: " .. #currentWindows)
    print("Other space windows: " .. #otherWindows)
    print("Total windows: " .. totalFound)
    
    if #otherWindows > 0 then
        print("✅ SUCCESS: Can see windows in other spaces!")
        print("💡 This solves the cross-space detection problem!")
    else
        print("❌ No other-space windows found")
        print("💭 Either no windows in other spaces, or they weren't last-focused")
    end
    '''
    
    try:
        result = subprocess.run([hs_cli, '-c', script], 
                               capture_output=True, text=True, timeout=15)
        
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                print(f"  {line}")
        
        if result.stderr:
            print(f"Errors: {result.stderr}")
    
    except subprocess.TimeoutExpired:
        print("❌ Test timed out")
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_cross_space_focusing():
    """Test if we can focus windows found in other spaces."""
    print("\n🎯 Testing Cross-Space Window Focusing")
    print("=" * 37)
    
    hs_cli = find_hammerspoon_cli()
    
    script = '''
    local windowfilter = require("hs.window.filter")
    local spaces = require("hs.spaces")
    local timer = require("hs.timer")
    
    local currentSpace = spaces.focusedSpace()
    print("Current space: " .. currentSpace)
    
    -- Get windows from other spaces
    local wf_other = windowfilter.new('Code')
    wf_other:setCurrentSpace(false)
    
    local otherWindows = wf_other:getWindows()
    print("Other-space windows found: " .. #otherWindows)
    
    if #otherWindows > 0 then
        local targetWindow = otherWindows[1]
        local title = targetWindow:title() or "NO TITLE"
        local winSpaces = spaces.windowSpaces(targetWindow:id())
        local targetSpace = winSpaces and winSpaces[1] or "UNKNOWN"
        
        print("\\nTarget window: \\"" .. title .. "\\" (Space " .. targetSpace .. ")")
        print("\\n🔄 Attempting to focus cross-space window...")
        print("⚠️  This should switch spaces if it works!")
        
        -- Try to focus the window
        local success = targetWindow:focus()
        print("Focus result: " .. tostring(success))
        
        -- Wait and check
        timer.usleep(1000000) -- 1 second
        
        local newSpace = spaces.focusedSpace()
        print("\\nSpace after focus attempt: " .. newSpace .. " (was " .. currentSpace .. ")")
        
        if newSpace ~= currentSpace then
            print("🎉 SUCCESS: Focused cross-space window!")
            print("🚀 Space changed from " .. currentSpace .. " to " .. newSpace)
            print("✅ This is the solution we need!")
        else
            print("❌ No space change - focus may have failed")
        end
    else
        print("⚠️  No other-space windows to test focusing")
    end
    '''
    
    try:
        print("⚠️ WATCH FOR SPACE CHANGES...")
        time.sleep(1)
        
        result = subprocess.run([hs_cli, '-c', script], 
                               capture_output=True, text=True, timeout=15)
        
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                print(f"  {line}")
        
        if result.stderr:
            print(f"Errors: {result.stderr}")
    
    except subprocess.TimeoutExpired:
        print("❌ Focus test timed out")
    except Exception as e:
        print(f"❌ Focus test failed: {e}")

def main():
    """Test GitHub issue workaround for cross-space window access."""
    print("🐛 GitHub Issue #3276 Workaround Test")
    print("=" * 36)
    print("🔗 Issue: https://github.com/Hammerspoon/hammerspoon/issues/3276")
    print("💡 Bug: window.filter only returns last-focused window from other spaces")
    print("🔧 Workaround: Use setCurrentSpace(false) to get other-space windows")
    print("")
    
    # Test 1: Current vs other space filters
    test_current_space_filter()
    
    # Test 2: Focus cross-space windows
    test_cross_space_focusing()
    
    print(f"\n{'='*36}")
    print("GITHUB WORKAROUND ANALYSIS")
    print(f"{'='*36}")
    print("Key insights:")
    print("1. If ai_advisory_system was found → Workaround succeeds!")
    print("2. If focusing worked → We have complete cross-space solution!")
    print("3. If only partial results → Need to track windows over time")
    print("4. The 'last-focused' limitation means we need window history")

if __name__ == "__main__":
    main()