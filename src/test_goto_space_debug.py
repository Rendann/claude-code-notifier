#!/usr/bin/env python3
"""
test_goto_space_debug.py - Deep debug of gotoSpace() failure

The gotoSpace() function returns nil instead of true, indicating it's detecting
an error condition. Let's investigate what's causing this failure.

Based on Hammerspoon docs, gotoSpace() can fail if:
1. The target space doesn't exist
2. The space is invalid or not accessible  
3. There are restrictions on space switching
4. The current space state prevents switching
"""

import subprocess
import time

def find_hammerspoon_cli():
    """Find Hammerspoon CLI."""
    return "/Applications/Hammerspoon.app/Contents/Frameworks/hs/hs"

def test_space_validation():
    """Test if target space IDs are valid before attempting switches."""
    print("🔍 Testing Space ID Validation")
    print("=" * 28)
    
    hs_cli = find_hammerspoon_cli()
    
    script = '''
    local spaces = require("hs.spaces")
    
    local currentSpace = spaces.focusedSpace()
    local spacesForScreen = spaces.spacesForScreen()
    local allSpaces = spaces.allSpaces()
    
    print("Current space: " .. currentSpace)
    print("Spaces on screen:")
    for i, spaceID in pairs(spacesForScreen) do
        local current = (spaceID == currentSpace) and " <- CURRENT" or ""
        print("  " .. i .. ": " .. spaceID .. current)
    end
    
    -- Validate each space exists in allSpaces
    print("\\nValidating spaces exist in allSpaces:")
    local mainScreenUUID = nil
    for screenUUID, screenSpaces in pairs(allSpaces) do
        mainScreenUUID = screenUUID -- assume first screen is main
        break
    end
    
    if mainScreenUUID and allSpaces[mainScreenUUID] then
        local validSpaces = allSpaces[mainScreenUUID]
        
        for i, spaceID in pairs(spacesForScreen) do
            local found = false
            for j, validSpace in pairs(validSpaces) do
                if validSpace == spaceID then
                    found = true
                    break
                end
            end
            
            if found then
                print("  ✅ Space " .. spaceID .. " is valid")
            else
                print("  ❌ Space " .. spaceID .. " NOT FOUND in allSpaces!")
            end
        end
    end
    
    -- Test space type validation
    print("\\nTesting space types:")
    for i, spaceID in pairs(spacesForScreen) do
        local spaceType = spaces.spaceType(spaceID)
        if spaceType then
            print("  Space " .. spaceID .. ": " .. spaceType)
        else
            print("  Space " .. spaceID .. ": UNKNOWN TYPE")
        end
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
        print(f"❌ Space validation failed: {e}")

def test_minimal_space_switch():
    """Test the most minimal possible space switch to isolate the issue."""
    print("\n🎯 Testing Minimal Space Switch")
    print("=" * 29)
    
    hs_cli = find_hammerspoon_cli()
    
    script = '''
    local spaces = require("hs.spaces")
    
    local currentSpace = spaces.focusedSpace()
    local spacesForScreen = spaces.spacesForScreen()
    
    print("Current space: " .. currentSpace)
    
    -- Find the first different space
    local targetSpace = nil
    for i, spaceID in pairs(spacesForScreen) do
        if spaceID ~= currentSpace then
            targetSpace = spaceID
            print("Target space: " .. targetSpace)
            break
        end
    end
    
    if targetSpace then
        print("\\n🔄 Attempting minimal switch...")
        print("From: " .. currentSpace .. " → To: " .. targetSpace)
        
        -- Try the switch and capture any error
        local success, error = pcall(function()
            return spaces.gotoSpace(targetSpace)
        end)
        
        if success then
            local switchResult = error -- pcall returns result as second value on success
            print("Switch result: " .. tostring(switchResult))
            
            if switchResult == true then
                print("✅ gotoSpace returned true")
                
                -- Check if we actually switched
                local timer = require("hs.timer")
                timer.usleep(2000000) -- 2 seconds
                
                local newSpace = spaces.focusedSpace()
                print("New space: " .. newSpace)
                
                if newSpace == targetSpace then
                    print("🎉 SWITCH SUCCESSFUL!")
                else
                    print("❌ Switch reported success but space didn't change")
                end
            elseif switchResult == nil then
                print("❌ gotoSpace returned nil (error condition)")
                print("💡 This suggests gotoSpace detected an invalid state")
            else
                print("⚠️ gotoSpace returned: " .. tostring(switchResult))
            end
        else
            print("❌ gotoSpace threw error: " .. tostring(error))
        end
    else
        print("❌ No target space found (only one space?)")
    end
    '''
    
    try:
        print("⚠️ WATCH YOUR SCREEN - Testing minimal space switch...")
        time.sleep(1)
        
        result = subprocess.run([hs_cli, '-c', script], 
                               capture_output=True, text=True, timeout=15)
        
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                print(f"  {line}")
        
        if result.stderr:
            print(f"Errors: {result.stderr}")
    
    except Exception as e:
        print(f"❌ Minimal switch test failed: {e}")

def test_sip_and_restrictions():
    """Test for macOS restrictions that might prevent space switching."""
    print("\n🛡️ Testing macOS Restrictions")
    print("=" * 27)
    
    hs_cli = find_hammerspoon_cli()
    
    script = '''
    local spaces = require("hs.spaces")
    
    -- Check if displays have separate spaces
    local separateSpaces = spaces.screensHaveSeparateSpaces()
    print("Displays have separate spaces: " .. tostring(separateSpaces))
    
    -- Check current space details
    local currentSpace = spaces.focusedSpace()
    local spaceDisplay = spaces.spaceDisplay(currentSpace)
    print("Current space display: " .. (spaceDisplay or "unknown"))
    
    -- Check if any spaces are fullscreen
    local spacesForScreen = spaces.spacesForScreen()
    print("\\nChecking for fullscreen spaces:")
    
    local hasFullscreen = false
    for i, spaceID in pairs(spacesForScreen) do
        local spaceType = spaces.spaceType(spaceID)
        print("  Space " .. spaceID .. ": " .. (spaceType or "unknown"))
        
        if spaceType == "fullscreen" then
            hasFullscreen = true
        end
    end
    
    if hasFullscreen then
        print("⚠️ Found fullscreen spaces - these can interfere with switching")
    else
        print("✅ No fullscreen spaces detected")
    end
    
    -- Test if we can at least open/close Mission Control
    print("\\nTesting Mission Control operations:")
    local mcSuccess, mcError = pcall(function()
        spaces.openMissionControl()
        local timer = require("hs.timer")
        timer.usleep(1000000) -- 1 second
        spaces.closeMissionControl()
        timer.usleep(500000) -- 0.5 seconds
        return true
    end)
    
    if mcSuccess then
        print("✅ Mission Control open/close works")
    else
        print("❌ Mission Control operations failed: " .. (mcError or "unknown"))
    end
    '''
    
    try:
        print("⚠️ WATCH YOUR SCREEN - Testing Mission Control operations...")
        time.sleep(1)
        
        result = subprocess.run([hs_cli, '-c', script], 
                               capture_output=True, text=True, timeout=15)
        
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                print(f"  {line}")
        
        if result.stderr:
            print(f"Errors: {result.stderr}")
    
    except Exception as e:
        print(f"❌ Restrictions test failed: {e}")

def main():
    """Deep debug why gotoSpace() returns nil."""
    print("🔬 Deep Debug: gotoSpace() Failure Analysis")
    print("=" * 44)
    print("🎯 Goal: Understand why gotoSpace() returns nil instead of true")
    print("")
    
    # Test 1: Validate space IDs
    test_space_validation()
    
    # Test 2: Minimal switch test
    test_minimal_space_switch()
    
    # Test 3: Check for macOS restrictions
    test_sip_and_restrictions()
    
    print(f"\n{'='*44}")
    print("DIAGNOSIS SUMMARY")
    print(f"{'='*44}")
    print("Based on test results:")
    print("1. If spaces are valid but gotoSpace() returns nil:")
    print("   → There may be a macOS policy preventing automation of space switching")
    print("2. If Mission Control operations work but switching doesn't:")
    print("   → The issue is specifically with the space switching mechanism")
    print("3. If fullscreen spaces are detected:")
    print("   → Try switching when no fullscreen apps are active")
    print("4. Next steps:")
    print("   → Consider using keyboard shortcuts via hs.eventtap.keyStroke()")
    print("   → Try the hs.spaces.watcher to monitor space changes")

if __name__ == "__main__":
    main()