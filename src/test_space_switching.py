#!/usr/bin/env python3
"""
test_space_switching.py - Basic Hammerspoon space switching test

Before trying complex window focusing, let's test if Hammerspoon can
do the most basic thing: switch spaces at all.

Tests:
1. Can we get current space ID?
2. Can we get list of all spaces?
3. Can we switch to a different space by ID?
4. Can we switch to "next space" or "previous space"?
"""

import subprocess
import time

def find_hammerspoon_cli():
    """Find Hammerspoon CLI."""
    return "/Applications/Hammerspoon.app/Contents/Frameworks/hs/hs"

def test_hammerspoon_cli():
    """Test basic CLI connectivity."""
    print("🔨 Testing Hammerspoon CLI Connection")
    print("=" * 35)
    
    hs_cli = find_hammerspoon_cli()
    
    try:
        result = subprocess.run([hs_cli, '-c', 'print("Hammerspoon CLI working!")'], 
                               capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("✅ Hammerspoon CLI is connected")
            return True
        else:
            print(f"❌ CLI failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

def test_get_spaces():
    """Test getting space information."""
    print("\n🌌 Testing Space Information Retrieval")
    print("=" * 40)
    
    hs_cli = find_hammerspoon_cli()
    
    script = '''
    local spaces = require("hs.spaces")
    
    print("🔍 Getting space information...")
    
    -- Get current space
    local currentSpace = spaces.focusedSpace()
    if currentSpace then
        print("✅ Current space ID: " .. currentSpace)
    else
        print("❌ Cannot get current space")
        return
    end
    
    -- Get all spaces
    local allSpaces = spaces.allSpaces()
    if allSpaces then
        print("✅ All spaces:")
        for screen, spaceList in pairs(allSpaces) do
            print("   Screen " .. screen .. ":")
            for i, space in pairs(spaceList) do
                local current = (space == currentSpace) and " <- CURRENT" or ""
                print("      Space " .. i .. ": ID " .. space .. current)
            end
        end
    else
        print("❌ Cannot get all spaces")
    end
    '''
    
    try:
        result = subprocess.run([hs_cli, '-c', script], 
                               capture_output=True, text=True, timeout=10)
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print(f"Errors: {result.stderr}")
        
        success = "Current space ID:" in result.stdout
        print(f"\nStatus: {'✅ SUCCESS' if success else '❌ FAILED'}")
        return success
        
    except Exception as e:
        print(f"❌ Space info test failed: {e}")
        return False

def test_space_switching():
    """Test basic space switching."""
    print("\n🔄 Testing Basic Space Switching")
    print("=" * 30)
    
    hs_cli = find_hammerspoon_cli()
    
    print("📍 Step 1: Get current space and find a different space")
    
    # First, get current space and find another space to switch to
    info_script = '''
    local spaces = require("hs.spaces")
    
    local currentSpace = spaces.focusedSpace()
    local allSpaces = spaces.allSpaces()
    
    local targetSpace = nil
    
    -- Find a different space to switch to
    for screen, spaceList in pairs(allSpaces) do
        for i, space in pairs(spaceList) do
            if space ~= currentSpace then
                targetSpace = space
                break
            end
        end
        if targetSpace then break end
    end
    
    if targetSpace then
        print("CURRENT:" .. currentSpace)
        print("TARGET:" .. targetSpace)
    else
        print("ERROR:Only one space available")
    end
    '''
    
    try:
        result = subprocess.run([hs_cli, '-c', info_script], 
                               capture_output=True, text=True, timeout=5)
        
        if "ERROR:" in result.stdout:
            print("⚠️ Only one space available - cannot test switching")
            return False
        
        if "CURRENT:" not in result.stdout or "TARGET:" not in result.stdout:
            print("❌ Could not determine spaces")
            print(result.stdout)
            return False
        
        # Parse current and target space IDs
        lines = result.stdout.strip().split('\n')
        current_space = None
        target_space = None
        
        for line in lines:
            if line.startswith("CURRENT:"):
                current_space = line.split(":")[1]
            elif line.startswith("TARGET:"):
                target_space = line.split(":")[1]
        
        if not current_space or not target_space:
            print("❌ Could not parse space IDs")
            return False
        
        print(f"✅ Current space: {current_space}")
        print(f"✅ Target space: {target_space}")
        
        print(f"\n🔄 Step 2: Attempting to switch spaces...")
        print(f"   From {current_space} → {target_space}")
        
        # Now try to switch
        switch_script = f'''
        local spaces = require("hs.spaces")
        
        print("🔄 Attempting space switch...")
        print("From space {current_space} to space {target_space}")
        
        local success = spaces.gotoSpace({target_space})
        
        if success then
            print("✅ Switch command succeeded")
        else
            print("❌ Switch command failed")
        end
        
        -- Wait a moment then check what space we're in
        local timer = require("hs.timer")
        timer.usleep(1000000) -- 1 second
        
        local newSpace = spaces.focusedSpace()
        print("Now in space: " .. (newSpace or "unknown"))
        
        if newSpace == {target_space} then
            print("✅ SPACE SWITCH SUCCESSFUL!")
        else
            print("❌ Space switch did not work")
        end
        '''
        
        print("⚠️ WATCH YOUR SCREEN - This should switch spaces if it works!")
        time.sleep(2)  # Give user time to read
        
        result = subprocess.run([hs_cli, '-c', switch_script], 
                               capture_output=True, text=True, timeout=10)
        
        if result.stdout:
            print("\nSpace switching results:")
            print(result.stdout)
        
        if result.stderr:
            print(f"Errors: {result.stderr}")
        
        success = "SPACE SWITCH SUCCESSFUL!" in result.stdout
        print(f"\nStatus: {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        if success:
            print("\n🎉 BREAKTHROUGH! Hammerspoon CAN switch spaces!")
            print("   This means cross-space window focusing might be possible!")
        else:
            print("\n❌ Hammerspoon cannot switch spaces")
            print("   Same fundamental limitation as other approaches")
        
        return success
        
    except Exception as e:
        print(f"❌ Space switching test failed: {e}")
        return False

def main():
    """Test basic Hammerspoon space switching capabilities."""
    print("🧪 Hammerspoon Basic Space Switching Test")
    print("=" * 45)
    
    print("💡 Testing the fundamental question: Can Hammerspoon switch spaces?")
    
    # Test 1: CLI connectivity
    if not test_hammerspoon_cli():
        print("\n❌ Hammerspoon CLI not working")
        print("💡 Make sure Hammerspoon is running and config loaded")
        return
    
    # Test 2: Space information
    if not test_get_spaces():
        print("\n❌ Cannot get space information")
        print("💡 Spaces module may need permissions")
        return
    
    # Test 3: Space switching (the critical test)
    switching_works = test_space_switching()
    
    print(f"\n{'='*45}")
    print("FUNDAMENTAL SPACE SWITCHING TEST RESULTS")
    print(f"{'='*45}")
    
    if switching_works:
        print("🎉 SUCCESS: Hammerspoon can switch spaces!")
        print("✅ This opens the door for cross-space window focusing")
        print("🚀 Next: Test finding windows and switching to their spaces")
    else:
        print("❌ FAILED: Hammerspoon cannot switch spaces")
        print("💡 Same limitation as all other approaches")
        print("🤔 May need system permissions or different approach")

if __name__ == "__main__":
    main()