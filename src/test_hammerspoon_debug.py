#!/usr/bin/env python3
"""
test_hammerspoon_debug.py - Debug Hammerspoon space switching issues

Based on the Hammerspoon docs, gotoSpace() opens Mission Control to perform switches.
The fact that we see Mission Control animation but no space change suggests:
1. Permission issues with Accessibility/Mission Control
2. Timing issues with Mission Control elements
3. Issues with the specific space IDs we're targeting

Let's diagnose what's happening step by step.
"""

import subprocess
import time

def find_hammerspoon_cli():
    """Find Hammerspoon CLI."""
    return "/Applications/Hammerspoon.app/Contents/Frameworks/hs/hs"

def check_hammerspoon_permissions():
    """Check if Hammerspoon has proper permissions."""
    print("🔐 Checking Hammerspoon Permissions")
    print("=" * 33)
    
    hs_cli = find_hammerspoon_cli()
    
    script = '''
    local spaces = require("hs.spaces")
    
    -- Test basic space access
    local currentSpace = spaces.focusedSpace()
    print("✅ Can get focused space: " .. (currentSpace or "nil"))
    
    -- Test spaces enumeration
    local allSpaces = spaces.allSpaces()
    if allSpaces then
        print("✅ Can enumerate all spaces")
    else
        print("❌ Cannot enumerate spaces")
    end
    
    -- Test screen spaces
    local spacesForScreen = spaces.spacesForScreen()
    if spacesForScreen then
        print("✅ Can get spaces for screen: " .. #spacesForScreen .. " spaces")
    else
        print("❌ Cannot get spaces for screen")
    end
    
    -- Test Mission Control access
    print("🎛️ Testing Mission Control access...")
    local success, error = pcall(function()
        spaces.openMissionControl()
        -- Wait briefly
        local timer = require("hs.timer")
        timer.usleep(500000) -- 0.5 seconds
        spaces.closeMissionControl()
    end)
    
    if success then
        print("✅ Mission Control access works")
    else
        print("❌ Mission Control access failed: " .. (error or "unknown"))
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
        print(f"❌ Permission check failed: {e}")

def test_mcwait_timing():
    """Test if MCwaitTime timing is affecting space switches."""
    print("\n⏱️ Testing Mission Control Timing")
    print("=" * 31)
    
    hs_cli = find_hammerspoon_cli()
    
    script = '''
    local spaces = require("hs.spaces")
    
    print("Current MCwaitTime: " .. (spaces.MCwaitTime or "nil"))
    
    -- Try increasing wait time for Mission Control
    spaces.MCwaitTime = 2.0  -- 2 seconds
    print("Set MCwaitTime to: " .. spaces.MCwaitTime)
    
    -- Test with longer wait
    local currentSpace = spaces.focusedSpace()
    local spacesForScreen = spaces.spacesForScreen()
    
    if currentSpace and spacesForScreen and #spacesForScreen >= 2 then
        -- Find a different space to try switching to
        local targetSpace = nil
        for i, spaceID in pairs(spacesForScreen) do
            if spaceID ~= currentSpace then
                targetSpace = spaceID
                break
            end
        end
        
        if targetSpace then
            print("Attempting switch with longer timing...")
            print("From: " .. currentSpace .. " To: " .. targetSpace)
            
            local success = spaces.gotoSpace(targetSpace)
            print("Switch command result: " .. tostring(success))
            
            -- Wait and check result
            local timer = require("hs.timer")
            timer.usleep(1000000) -- 1 second
            
            local newSpace = spaces.focusedSpace()
            print("New space: " .. (newSpace or "nil"))
            
            if newSpace == targetSpace then
                print("🎉 SUCCESS with longer timing!")
            else
                print("❌ Still failed with longer timing")
            end
        else
            print("❌ No target space found")
        end
    else
        print("❌ Cannot get space info for timing test")
    end
    '''
    
    try:
        print("⚠️ WATCH YOUR SCREEN - Testing longer Mission Control timing...")
        time.sleep(1)
        
        result = subprocess.run([hs_cli, '-c', script], 
                               capture_output=True, text=True, timeout=30)
        
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                print(f"  {line}")
        
        if result.stderr:
            print(f"Errors: {result.stderr}")
    
    except Exception as e:
        print(f"❌ Timing test failed: {e}")

def test_accessibility_requirements():
    """Test if Hammerspoon has necessary Accessibility permissions."""
    print("\n♿ Testing Accessibility Requirements")
    print("=" * 35)
    
    hs_cli = find_hammerspoon_cli()
    
    script = '''
    print("Testing Accessibility API access...")
    
    local ax = require("hs.axuielement")
    local success, error = pcall(function()
        local systemWideElement = ax.systemWideElement()
        if systemWideElement then
            print("✅ Can access system-wide AX element")
        else
            print("❌ Cannot access system-wide AX element")
        end
    end)
    
    if not success then
        print("❌ Accessibility API error: " .. (error or "unknown"))
        print("💡 Hammerspoon needs Accessibility permissions!")
        print("💡 Go to: System Preferences → Security & Privacy → Accessibility")
        print("💡 Add Hammerspoon to the list and enable it")
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
        print(f"❌ Accessibility test failed: {e}")

def main():
    """Debug Hammerspoon space switching issues."""
    print("🐛 Hammerspoon Space Switching Debug")
    print("=" * 38)
    print("🎯 Goal: Understand why gotoSpace() opens Mission Control but doesn't switch")
    print("")
    
    # Test 1: Check permissions
    check_hammerspoon_permissions()
    
    # Test 2: Check accessibility
    test_accessibility_requirements()
    
    # Test 3: Test timing
    test_mcwait_timing()
    
    print(f"\n{'='*38}")
    print("DEBUG RECOMMENDATIONS")
    print(f"{'='*38}")
    print("If space switching still fails:")
    print("1. ✅ Check System Preferences → Security & Privacy → Accessibility")
    print("2. ✅ Ensure Hammerspoon is enabled in Accessibility list")  
    print("3. ✅ Try increasing hs.spaces.MCwaitTime to 3.0 or higher")
    print("4. ✅ Check if 'Reduce motion' is enabled in Accessibility → Display")
    print("5. ✅ Restart Hammerspoon after permission changes")

if __name__ == "__main__":
    main()