#!/usr/bin/env python3
"""
test_cross_space_window.py - Test if Hammerspoon can see the ai_advisory_system window

This is the critical test. If Hammerspoon can find ai_advisory_system on space 6
(while we're on space 5), then it truly has cross-space window visibility that
AppleScript lacks. If it can't, then it has the same limitation as AppleScript.

Expected behavior:
- ✅ Should find: claude-code-notifier (space 5), claude-config-manager (space 5), g710plus (minimized)
- ❓ Critical test: Can it find ai_advisory_system (space 6)?
"""

import subprocess
import time

def find_hammerspoon_cli():
    """Find Hammerspoon CLI."""
    return "/Applications/Hammerspoon.app/Contents/Frameworks/hs/hs"

def test_ai_advisory_window_detection():
    """Test specifically for the ai_advisory_system window that should be on space 6."""
    print("🔍 Critical Test: ai_advisory_system Window Detection")
    print("=" * 50)
    print("🎯 Looking for ai_advisory_system window on space 6")
    print("   This is the make-or-break test for cross-space visibility")
    print("")
    
    hs_cli = find_hammerspoon_cli()
    
    script = '''
    local application = require("hs.application")
    local window = require("hs.window")
    local spaces = require("hs.spaces")
    
    local currentSpace = spaces.focusedSpace()
    print("🏠 Current space: " .. currentSpace)
    print("")
    
    -- Find Code application (not Visual Studio Code)
    local codeApp = application.find("Code")
    if codeApp then
        print("✅ Found Code application")
        local codeWindows = codeApp:allWindows()
        print("📊 Total Code windows: " .. #codeWindows)
        print("")
        
        -- Look for each expected window specifically
        local expectedWindows = {
            {name = "claude-code-notifier", expectedSpace = 5},
            {name = "claude-config-manager", expectedSpace = 5},
            {name = "g710plus", expectedSpace = 3, minimized = true},
            {name = "ai_advisory_system", expectedSpace = 6}  -- THE CRITICAL TEST
        }
        
        local foundWindows = {}
        
        for i, win in pairs(codeWindows) do
            local title = win:title() or "NO TITLE"
            local winID = win:id()
            local isMinimized = win:isMinimized()
            local winSpaces = spaces.windowSpaces(winID)
            
            local spaceInfo = "UNKNOWN"
            if winSpaces and #winSpaces > 0 then
                spaceInfo = winSpaces[1]
            end
            
            local minimizedStr = isMinimized and " [MINIMIZED]" or ""
            
            print("🪟 Window " .. i .. ": \\"" .. title .. "\\"")
            print("   ID: " .. winID .. ", Space: " .. spaceInfo .. minimizedStr)
            
            -- Check against expected windows
            for _, expected in pairs(expectedWindows) do
                if string.find(string.lower(title), string.lower(expected.name)) then
                    foundWindows[expected.name] = {
                        found = true,
                        title = title,
                        space = spaceInfo,
                        minimized = isMinimized,
                        expected_space = expected.expectedSpace
                    }
                end
            end
        end
        
        print("")
        print("📋 EXPECTED WINDOW ANALYSIS:")
        print("=" * 30)
        
        for _, expected in pairs(expectedWindows) do
            local found = foundWindows[expected.name]
            if found then
                local spaceMatch = (found.space == expected.expectedSpace) and "✅" or "❌"
                local minimizedMatch = ""
                if expected.minimized then
                    minimizedMatch = found.minimized and " [MINIMIZED ✅]" or " [NOT MINIMIZED ❌]"
                end
                
                print("✅ " .. expected.name .. ":")
                print("   Found: " .. found.title)
                print("   Space: " .. found.space .. " (expected " .. expected.expectedSpace .. ") " .. spaceMatch)
                print("   " .. minimizedMatch)
                
                -- CRITICAL: ai_advisory_system test
                if expected.name == "ai_advisory_system" then
                    if found.space == expected.expectedSpace then
                        print("   🎉 BREAKTHROUGH: Hammerspoon can see cross-space windows!")
                        print("   🚀 This solves the AppleScript limitation!")
                    else
                        print("   ⚠️  Found but wrong space - still significant")
                    end
                end
            else
                print("❌ " .. expected.name .. ": NOT FOUND")
                
                -- CRITICAL: ai_advisory_system missing  
                if expected.name == "ai_advisory_system" then
                    print("   💔 LIMITATION: Same as AppleScript - cannot see cross-space windows")
                    print("   📝 Hammerspoon has same macOS restriction as AppleScript")
                end
            end
            print("")
        end
        
    else
        print("❌ Code application not found")
        
        -- Show available applications for debugging
        local allApps = application.runningApplications()
        print("🔍 Available applications containing 'code':")
        for _, app in pairs(allApps) do
            local name = app:name()
            if string.find(string.lower(name), "code") then
                print("   - " .. name .. " (" .. app:bundleID() .. ")")
            end
        end
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
        print(f"❌ Critical test failed: {e}")

def test_detailed_window_analysis():
    """Get detailed information about all found windows for comparison."""
    print("\n🔬 Detailed Window Analysis")
    print("=" * 28)
    
    hs_cli = find_hammerspoon_cli()
    
    script = '''
    local application = require("hs.application")
    local window = require("hs.window")
    local spaces = require("hs.spaces")
    
    local codeApp = application.find("Code")
    if codeApp then
        local codeWindows = codeApp:allWindows()
        
        print("📊 DETAILED WINDOW PROPERTIES:")
        for i, win in pairs(codeWindows) do
            local title = win:title() or "NO TITLE"
            local winID = win:id()
            local winSpaces = spaces.windowSpaces(winID)
            
            print("\\n🪟 Window " .. i .. ":")
            print("   Title: \\"" .. title .. "\\"")
            print("   ID: " .. winID)
            print("   Minimized: " .. tostring(win:isMinimized()))
            print("   Visible: " .. tostring(win:isVisible()))
            print("   Standard: " .. tostring(win:isStandard()))
            
            if winSpaces then
                print("   Spaces: [" .. table.concat(winSpaces, ", ") .. "]")
            else
                print("   Spaces: NONE")
            end
            
            -- Try to get more space information
            local frame = win:frame()
            if frame then
                print("   Position: (" .. frame.x .. ", " .. frame.y .. ")")
                print("   Size: " .. frame.w .. "x" .. frame.h)
            end
        end
        
        -- Summary
        print("\\n📈 SUMMARY:")
        print("   Windows found: " .. #codeWindows)
        print("   This represents the MAXIMUM Hammerspoon can see")
        print("   Compare to expected 4 windows to determine cross-space capability")
        
    else
        print("❌ Cannot perform detailed analysis - Code app not found")
    end
    '''
    
    try:
        result = subprocess.run([hs_cli, '-c', script], 
                               capture_output=True, text=True, timeout=10)
        
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                print(f"  {line}")
        
        if result.stderr:
            print(f"Errors: {result.stderr}")
    
    except Exception as e:
        print(f"❌ Detailed analysis failed: {e}")

def main():
    """Test if Hammerspoon can see cross-space windows (specifically ai_advisory_system)."""
    print("🔬 Hammerspoon Cross-Space Window Detection Test")
    print("=" * 48)
    print("🎯 CRITICAL QUESTION: Can Hammerspoon see ai_advisory_system on space 6?")
    print("")
    print("📋 Expected results:")
    print("   ✅ BREAKTHROUGH: If ai_advisory_system is found → Cross-space visibility!")
    print("   ❌ LIMITATION: If ai_advisory_system is missing → Same as AppleScript")
    print("")
    
    # Critical test: Look for ai_advisory_system specifically
    test_ai_advisory_window_detection()
    
    # Detailed analysis
    test_detailed_window_analysis()
    
    print(f"\n{'='*48}")
    print("FINAL DETERMINATION")
    print(f"{'='*48}")
    print("Based on whether ai_advisory_system was found:")
    print("")
    print("IF FOUND:")
    print("🎉 Hammerspoon has cross-space window visibility")
    print("🚀 We can build the notification system without Mission Control")
    print("✅ Direct window focusing across spaces is possible")
    print("")
    print("IF NOT FOUND:")
    print("💔 Hammerspoon has the same limitation as AppleScript")  
    print("🔄 We need to use Mission Control or keyboard shortcuts")
    print("⚠️ No better than existing approaches")

if __name__ == "__main__":
    main()