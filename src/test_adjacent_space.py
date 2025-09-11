#!/usr/bin/env python3
"""
test_adjacent_space.py - Test moving to adjacent space with Hammerspoon

Specifically tests moving from current space (6) to adjacent space (5).
This builds on the successful space switching from test_space_switching.py
but focuses on controlled adjacent movement rather than arbitrary switching.
"""

import subprocess
import time

def find_hammerspoon_cli():
    """Find Hammerspoon CLI."""
    return "/Applications/Hammerspoon.app/Contents/Frameworks/hs/hs"

def test_hammerspoon_connection():
    """Verify Hammerspoon CLI is working."""
    print("🔨 Testing Hammerspoon Connection")
    print("=" * 32)
    
    hs_cli = find_hammerspoon_cli()
    
    try:
        result = subprocess.run([hs_cli, '-c', 'print("Hammerspoon connected!")'], 
                               capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("✅ Hammerspoon CLI connected")
            return True
        else:
            print(f"❌ Connection failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def get_current_space_info():
    """Get current space information using proper space ordering."""
    print("\n📍 Getting Current Space Information")
    print("=" * 35)
    
    hs_cli = find_hammerspoon_cli()
    
    script = '''
    local spaces = require("hs.spaces")
    
    local currentSpace = spaces.focusedSpace()
    if currentSpace then
        print("CURRENT_SPACE:" .. currentSpace)
        
        -- Get spaces for the main screen in their proper order
        local spacesForScreen = spaces.spacesForScreen()
        if spacesForScreen then
            print("SPACES_ORDERED:")
            for i, spaceID in pairs(spacesForScreen) do
                local marker = (spaceID == currentSpace) and " <- CURRENT" or ""
                print("  Position " .. i .. ": ID " .. spaceID .. marker)
            end
            
            -- Find current position and calculate target
            local currentPosition = nil
            for i, spaceID in pairs(spacesForScreen) do
                if spaceID == currentSpace then
                    currentPosition = i
                    break
                end
            end
            
            if currentPosition then
                print("CURRENT_POSITION:" .. currentPosition)
                
                -- Target is the previous position (6 → 5)
                local targetPosition = currentPosition - 1
                if targetPosition >= 1 and spacesForScreen[targetPosition] then
                    local targetSpace = spacesForScreen[targetPosition]
                    print("TARGET_POSITION:" .. targetPosition)
                    print("TARGET_SPACE:" .. targetSpace)
                else
                    print("ERROR:No adjacent space to the left")
                end
            else
                print("ERROR:Cannot find current position")
            end
        else
            print("ERROR:Cannot get spaces for screen")
        end
    else
        print("ERROR:Cannot get current space")
    end
    '''
    
    try:
        result = subprocess.run([hs_cli, '-c', script], 
                               capture_output=True, text=True, timeout=10)
        
        if result.stdout:
            print("Space information:")
            for line in result.stdout.strip().split('\n'):
                if line.startswith("CURRENT_SPACE:"):
                    current = line.split(":")[1]
                    print(f"  📍 Current space: {current}")
                elif line.startswith("TOTAL_SPACES:"):
                    total = line.split(":")[1]
                    print(f"  📊 Total spaces: {total}")
                elif line.startswith("TARGET_SPACE:"):
                    target = line.split(":")[1]
                    print(f"  🎯 Target space: {target}")
                elif not line.startswith("CURRENT_SPACE:") and not line.startswith("TOTAL_SPACES:") and not line.startswith("TARGET_SPACE:"):
                    if line.strip():
                        print(f"  ℹ️  {line}")
        
        if result.stderr:
            print(f"Warnings: {result.stderr}")
        
        # Parse the results
        current_space = None
        target_space = None
        current_position = None
        target_position = None
        
        for line in result.stdout.strip().split('\n'):
            if line.startswith("CURRENT_SPACE:"):
                current_space = int(line.split(":")[1])
            elif line.startswith("TARGET_SPACE:"):
                target_space = int(line.split(":")[1])
            elif line.startswith("CURRENT_POSITION:"):
                current_position = int(line.split(":")[1])
            elif line.startswith("TARGET_POSITION:"):
                target_position = int(line.split(":")[1])
        
        return current_space, target_space, current_position, target_position
    
    except Exception as e:
        print(f"❌ Space info error: {e}")
        return None, None, None, None

def test_adjacent_space_switch(current_space, target_space, current_position, target_position):
    """Test switching from current space to adjacent space by position."""
    print(f"\n🔄 Testing Adjacent Space Switch")
    print("=" * 32)
    print(f"📍 Position {current_position} (ID {current_space}) → Position {target_position} (ID {target_space})")
    
    # Validate this is a leftward move
    if target_position != current_position - 1:
        print(f"⚠️  This is not an adjacent leftward move")
        print(f"   Current position: {current_position}, Target position: {target_position}")
        response = input("   Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            print("   Test cancelled")
            return False
    
    hs_cli = find_hammerspoon_cli()
    
    switch_script = f'''
    local spaces = require("hs.spaces")
    
    print("🔄 Attempting space switch...")
    print("From space {current_space} to space {target_space}")
    
    local success = spaces.gotoSpace({target_space})
    
    if success then
        print("✅ Switch command executed")
    else
        print("❌ Switch command failed")
    end
    
    -- Wait briefly then verify
    local timer = require("hs.timer")
    timer.usleep(500000) -- 0.5 seconds
    
    local newSpace = spaces.focusedSpace()
    print("Now in space: " .. (newSpace or "unknown"))
    
    if newSpace == {target_space} then
        print("🎉 ADJACENT SPACE SWITCH SUCCESS!")
    else
        print("❌ Space switch did not work as expected")
    end
    '''
    
    print(f"⚠️  WATCH YOUR SCREEN - Switching from position {current_position} to {target_position}...")
    print(f"   (Space ID {current_space} → {target_space})")
    print("   (You should see the space change in ~2 seconds)")
    time.sleep(2)  # Give user time to observe
    
    try:
        result = subprocess.run([hs_cli, '-c', switch_script], 
                               capture_output=True, text=True, timeout=10)
        
        if result.stdout:
            print("\nSpace switch results:")
            for line in result.stdout.strip().split('\n'):
                print(f"  {line}")
        
        if result.stderr:
            print(f"Errors: {result.stderr}")
        
        success = "ADJACENT SPACE SWITCH SUCCESS!" in result.stdout
        
        if success:
            print(f"\n🎉 SUCCESS: Adjacent space switching works!")
            print(f"   Successfully moved from position {current_position} to {target_position}")
            print(f"   (Space ID {current_space} → {target_space})")
            print(f"   This confirms Hammerspoon can do controlled adjacent space navigation")
        else:
            print(f"\n❌ FAILED: Adjacent space switch did not work")
            print(f"   Could not move from position {current_position} to {target_position}")
            print(f"   (Space ID {current_space} → {target_space})")
        
        return success
    
    except Exception as e:
        print(f"❌ Space switch error: {e}")
        return False

def main():
    """Test adjacent space switching (space 6 → 5) with Hammerspoon."""
    print("🧪 Hammerspoon Adjacent Space Switch Test")
    print("=" * 42)
    print("🎯 Goal: Move from space 6 to adjacent space 5")
    print("")
    
    # Step 1: Test connection
    if not test_hammerspoon_connection():
        print("\n❌ Cannot connect to Hammerspoon")
        print("💡 Make sure Hammerspoon is running with spaces module enabled")
        return
    
    # Step 2: Get current space info
    current_space, target_space, current_position, target_position = get_current_space_info()
    
    if current_space is None:
        print("\n❌ Cannot determine current space")
        print("💡 Check Hammerspoon spaces module permissions")
        return
    
    print(f"\n📋 Space Analysis Complete")
    print(f"   Current: Position {current_position} (ID {current_space})")
    print(f"   Target: Position {target_position} (ID {target_space})")
    
    # Step 3: Perform adjacent space switch
    success = test_adjacent_space_switch(current_space, target_space, current_position, target_position)
    
    # Final summary
    print(f"\n{'='*42}")
    print("ADJACENT SPACE SWITCH TEST RESULTS")
    print(f"{'='*42}")
    
    if success:
        print("🎉 SUCCESS: Adjacent space switching works!")
        print("✅ Hammerspoon can move between adjacent spaces")
        print("🚀 Next: Implement window detection and cross-space focusing")
    else:
        print("❌ FAILED: Adjacent space switching needs debugging")
        print("🤔 Check Hammerspoon configuration and permissions")

if __name__ == "__main__":
    main()