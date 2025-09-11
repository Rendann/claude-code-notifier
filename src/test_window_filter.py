#!/usr/bin/env python3
"""
test_window_filter.py - Test hs.window.filter for cross-space window access

Based on Hammerspoon docs:
"This function can only return windows in the current Mission Control Space; 
if you need to address windows across different Spaces you can use the 
hs.window.filter module"

This could be the breakthrough we need!
"""

import subprocess
import time

def find_hammerspoon_cli():
    """Find Hammerspoon CLI."""
    return "/Applications/Hammerspoon.app/Contents/Frameworks/hs/hs"

def test_window_filter_basic():
    """Test basic hs.window.filter functionality."""
    print("🔍 Testing hs.window.filter Basic Functionality")
    print("=" * 46)
    
    hs_cli = find_hammerspoon_cli()
    
    script = '''
    local windowfilter = require("hs.window.filter")
    local spaces = require("hs.spaces")
    
    print("Current space: " .. spaces.focusedSpace())
    
    -- Create a window filter for VS Code windows
    print("\\n📋 Creating window filter for Code...")
    local codeFilter = windowfilter.new('Code')
    
    -- Get all Code windows via filter
    local codeWindows = codeFilter:getWindows()
    print("Windows found via filter: " .. #codeWindows)
    
    for i, win in pairs(codeWindows) do
        local title = win:title() or "NO TITLE"
        local winID = win:id()
        local winSpaces = spaces.windowSpaces(winID)
        
        local spaceInfo = "UNKNOWN"
        if winSpaces and #winSpaces > 0 then
            spaceInfo = winSpaces[1]
        end
        
        local isMinimized = win:isMinimized() and " [MINIMIZED]" or ""
        
        print("  " .. i .. ": \\"" .. title .. "\\" (Space: " .. spaceInfo .. ")" .. isMinimized)
    end
    
    -- Compare with regular window detection
    print("\\n🔄 Comparison with regular window.allWindows():")
    local window = require("hs.window")
    local allWindows = window.allWindows()
    
    local regularCodeWindows = {}
    for _, win in pairs(allWindows) do
        local app = win:application()
        if app and app:name() == "Code" then
            table.insert(regularCodeWindows, win)
        end
    end
    
    print("Regular detection: " .. #regularCodeWindows .. " windows")
    print("Filter detection: " .. #codeWindows .. " windows")
    
    if #codeWindows > #regularCodeWindows then
        print("🎉 BREAKTHROUGH: Window filter sees MORE windows!")
        print("   This suggests cross-space capability!")
    elseif #codeWindows == #regularCodeWindows then
        print("⚖️  Same count - need to check specific windows")
    else
        print("❌ Filter sees fewer windows - unexpected")
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
    
    except Exception as e:
        print(f"❌ Window filter basic test failed: {e}")

def test_window_filter_cross_space():
    """Test if window filter can find the ai_advisory_system window."""
    print("\n🎯 Critical Test: Window Filter Cross-Space Detection")
    print("=" * 51)
    print("🔍 Looking for ai_advisory_system with hs.window.filter")
    
    hs_cli = find_hammerspoon_cli()
    
    script = '''
    local windowfilter = require("hs.window.filter")
    local spaces = require("hs.spaces")
    
    print("Current space: " .. spaces.focusedSpace())
    
    -- Create window filter for Code app
    local codeFilter = windowfilter.new('Code')
    
    -- Get all windows
    local allCodeWindows = codeFilter:getWindows()
    print("\\nTotal Code windows via filter: " .. #allCodeWindows)
    
    -- Look for expected windows
    local expectedWindows = {
        "claude-code-notifier",
        "claude-config-manager", 
        "g710plus",
        "ai_advisory_system"  -- THE CRITICAL TEST
    }
    
    local foundWindows = {}
    
    print("\\n📋 DETAILED WINDOW ANALYSIS:")
    for i, win in pairs(allCodeWindows) do
        local title = win:title() or "NO TITLE"
        local winID = win:id()
        local winSpaces = spaces.windowSpaces(winID)
        local isMinimized = win:isMinimized()
        local isVisible = win:isVisible()
        
        local spaceInfo = "UNKNOWN"
        if winSpaces and #winSpaces > 0 then
            spaceInfo = winSpaces[1]
        end
        
        local flags = ""
        if isMinimized then flags = flags .. " [MINIMIZED]" end
        if not isVisible then flags = flags .. " [HIDDEN]" end
        
        print("🪟 " .. i .. ": \\"" .. title .. "\\"")
        print("   ID: " .. winID .. ", Space: " .. spaceInfo .. flags)
        
        -- Check against expected windows
        for _, expected in pairs(expectedWindows) do
            if string.find(string.lower(title), string.lower(expected)) then
                foundWindows[expected] = {
                    title = title,
                    space = spaceInfo,
                    minimized = isMinimized,
                    visible = isVisible
                }
            end
        end
    end
    
    print("\\n🔍 EXPECTED WINDOW RESULTS:")
    print("=" .. string.rep("=", 29))
    
    for _, expected in pairs(expectedWindows) do
        if foundWindows[expected] then
            print("✅ " .. expected .. " FOUND!")
            local found = foundWindows[expected]
            print("   Title: " .. found.title)
            print("   Space: " .. found.space)
            print("   Visible: " .. tostring(found.visible))
            
            -- Special attention to ai_advisory_system
            if expected == "ai_advisory_system" then
                print("   🎉 BREAKTHROUGH: Found cross-space window!")
                print("   🚀 Window filter bypasses space restrictions!")
            end
        else
            print("❌ " .. expected .. " NOT FOUND")
            if expected == "ai_advisory_system" then
                print("   💔 Still limited - cannot see cross-space windows")
            end
        end
        print("")
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
    
    except Exception as e:
        print(f"❌ Cross-space filter test failed: {e}")

def test_window_filter_focusing():
    """Test if window filter can focus cross-space windows."""
    print("\n🎯 Testing Window Filter Focusing Capabilities")
    print("=" * 43)
    
    hs_cli = find_hammerspoon_cli()
    
    script = '''
    local windowfilter = require("hs.window.filter")
    local spaces = require("hs.spaces")
    
    local currentSpace = spaces.focusedSpace()
    print("Current space: " .. currentSpace)
    
    -- Get all Code windows via filter
    local codeFilter = windowfilter.new('Code')
    local codeWindows = codeFilter:getWindows()
    
    print("Found " .. #codeWindows .. " Code windows via filter")
    
    -- Look for a window NOT in current space
    local targetWindow = nil
    local targetInfo = ""
    
    for _, win in pairs(codeWindows) do
        local winID = win:id()
        local title = win:title() or "NO TITLE"
        local winSpaces = spaces.windowSpaces(winID)
        
        if winSpaces and #winSpaces > 0 then
            local winSpace = winSpaces[1]
            if winSpace ~= currentSpace and not win:isMinimized() then
                targetWindow = win
                targetInfo = title .. " (Space " .. winSpace .. ")"
                print("\\nTarget for focusing: " .. targetInfo)
                break
            end
        end
    end
    
    if targetWindow then
        print("\\n🔄 Attempting to focus cross-space window...")
        print("⚠️  This should switch spaces if it works!")
        
        -- Try focusing the window
        local success = targetWindow:focus()
        print("Focus command result: " .. tostring(success))
        
        -- Wait and check result
        local timer = require("hs.timer")
        timer.usleep(1000000) -- 1 second
        
        local newSpace = spaces.focusedSpace()
        local focusedWin = window.focusedWindow()
        local focusedTitle = focusedWin and focusedWin:title() or "NONE"
        
        print("\\nResults:")
        print("  New space: " .. newSpace .. " (was " .. currentSpace .. ")")
        print("  Focused window: " .. focusedTitle)
        
        if newSpace ~= currentSpace then
            print("  🎉 SUCCESS: Space changed! Cross-space focusing works!")
            print("  🚀 This is the solution we've been looking for!")
        else
            print("  ❌ No space change - focusing failed")
        end
    else
        print("\\n⚠️  No cross-space windows found for focusing test")
        print("All windows are in current space, minimized, or not detected")
    end
    '''
    
    try:
        print("⚠️ WATCH FOR SPACE/WINDOW CHANGES...")
        time.sleep(1)
        
        result = subprocess.run([hs_cli, '-c', script], 
                               capture_output=True, text=True, timeout=20)
        
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                print(f"  {line}")
        
        if result.stderr:
            print(f"Errors: {result.stderr}")
    
    except Exception as e:
        print(f"❌ Window filter focusing test failed: {e}")

def main():
    """Test hs.window.filter for cross-space window access."""
    print("🔬 Hammerspoon Window Filter Cross-Space Test")
    print("=" * 44)
    print("🎯 Testing if hs.window.filter can access cross-space windows")
    print("📖 Based on docs: 'if you need to address windows across different")
    print("   Spaces you can use the hs.window.filter module'")
    print("")
    
    # Test 1: Basic window filter functionality
    test_window_filter_basic()
    
    # Test 2: Critical cross-space detection test
    test_window_filter_cross_space()
    
    # Test 3: Cross-space focusing test
    test_window_filter_focusing()
    
    print(f"\n{'='*44}")
    print("WINDOW FILTER TEST CONCLUSION")
    print(f"{'='*44}")
    print("Based on the results:")
    print("")
    print("IF ai_advisory_system was found:")
    print("🎉 hs.window.filter bypasses macOS space restrictions!")
    print("🚀 We can build cross-space notifications without Mission Control!")
    print("✅ Direct window focusing across spaces is possible!")
    print("")
    print("IF ai_advisory_system was NOT found:")
    print("💔 hs.window.filter has the same limitations")
    print("🔄 Need to use Mission Control or alternative approaches")
    print("⚠️ No breakthrough achieved")

if __name__ == "__main__":
    main()