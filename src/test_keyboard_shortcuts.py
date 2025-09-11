#!/usr/bin/env python3
"""
test_keyboard_shortcuts.py - Test keyboard shortcuts for space switching

Since hs.window.filter times out and Mission Control is too disruptive,
let's test using keyboard shortcuts to switch spaces. This might be
a good compromise - fast, reliable, and less visually disruptive.

Common space switching shortcuts:
- Ctrl+Left/Right: Move between spaces
- Ctrl+1/2/3: Go to specific space number
- Cmd+F3: Open Mission Control (then arrow keys)
"""

import subprocess
import time

def find_hammerspoon_cli():
    """Find Hammerspoon CLI."""
    return "/Applications/Hammerspoon.app/Contents/Frameworks/hs/hs"

def test_keyboard_space_switching():
    """Test space switching using keyboard shortcuts."""
    print("⌨️ Testing Keyboard Shortcut Space Switching")
    print("=" * 42)
    
    hs_cli = find_hammerspoon_cli()
    
    script = '''
    local eventtap = require("hs.eventtap")
    local spaces = require("hs.spaces")
    local timer = require("hs.timer")
    
    local currentSpace = spaces.focusedSpace()
    print("🏠 Current space: " .. currentSpace)
    
    -- Test 1: Control + Left Arrow (previous space)
    print("\\n🔄 Testing Ctrl+Left Arrow (previous space)...")
    print("⚠️  This should move to the space on the left")
    
    -- Send Ctrl+Left
    eventtap.keyStroke({"ctrl"}, "Left")
    
    -- Wait for space change
    timer.usleep(1000000) -- 1 second
    
    local newSpace1 = spaces.focusedSpace()
    print("Space after Ctrl+Left: " .. newSpace1)
    
    if newSpace1 ~= currentSpace then
        print("✅ SUCCESS: Ctrl+Left moved spaces!")
        print("   From " .. currentSpace .. " to " .. newSpace1)
        
        -- Test 2: Control + Right Arrow (next space) - to go back
        print("\\n🔄 Testing Ctrl+Right Arrow (back to original)...")
        
        timer.usleep(500000) -- 0.5 seconds
        eventtap.keyStroke({"ctrl"}, "Right")
        timer.usleep(1000000) -- 1 second
        
        local newSpace2 = spaces.focusedSpace()
        print("Space after Ctrl+Right: " .. newSpace2)
        
        if newSpace2 == currentSpace then
            print("✅ SUCCESS: Ctrl+Right returned to original space!")
            print("   Keyboard shortcuts work perfectly!")
        else
            print("⚠️  Moved but not to original space (" .. currentSpace .. ")")
        end
        
    else
        print("❌ No space change with Ctrl+Left")
        print("   Might be at leftmost space or shortcuts disabled")
        
        -- Try Ctrl+Right instead
        print("\\n🔄 Trying Ctrl+Right Arrow instead...")
        eventtap.keyStroke({"ctrl"}, "Right")
        timer.usleep(1000000)
        
        local newSpace3 = spaces.focusedSpace()
        print("Space after Ctrl+Right: " .. newSpace3)
        
        if newSpace3 ~= currentSpace then
            print("✅ SUCCESS: Ctrl+Right works!")
        else
            print("❌ Ctrl+Right also failed - shortcuts may be disabled")
        end
    end
    '''
    
    try:
        print("⚠️ WATCH YOUR SCREEN - Space should change...")
        time.sleep(1)
        
        result = subprocess.run([hs_cli, '-c', script], 
                               capture_output=True, text=True, timeout=15)
        
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                print(f"  {line}")
        
        if result.stderr:
            print(f"Errors: {result.stderr}")
    
    except Exception as e:
        print(f"❌ Keyboard shortcut test failed: {e}")

def test_numeric_space_switching():
    """Test switching to specific spaces using Ctrl+Number."""
    print("\n🔢 Testing Numeric Space Switching")
    print("=" * 32)
    
    hs_cli = find_hammerspoon_cli()
    
    script = '''
    local eventtap = require("hs.eventtap")
    local spaces = require("hs.spaces")
    local timer = require("hs.timer")
    
    local currentSpace = spaces.focusedSpace()
    print("Current space: " .. currentSpace)
    
    -- Get available spaces
    local spacesForScreen = spaces.spacesForScreen()
    print("Available spaces: " .. table.concat(spacesForScreen, ", "))
    
    -- Find current position
    local currentPosition = nil
    for i, spaceID in pairs(spacesForScreen) do
        if spaceID == currentSpace then
            currentPosition = i
            break
        end
    end
    
    if currentPosition then
        print("Current position: " .. currentPosition)
        
        -- Try to switch to position 1 if not already there
        if currentPosition ~= 1 then
            print("\\n🔄 Testing Ctrl+1 (switch to first space)...")
            
            eventtap.keyStroke({"ctrl"}, "1")
            timer.usleep(1000000) -- 1 second
            
            local newSpace = spaces.focusedSpace()
            print("Space after Ctrl+1: " .. newSpace)
            print("Expected first space: " .. spacesForScreen[1])
            
            if newSpace == spacesForScreen[1] then
                print("✅ SUCCESS: Ctrl+1 works!")
                
                -- Return to original position
                print("\\n🔄 Returning to original position...")
                eventtap.keyStroke({"ctrl"}, tostring(currentPosition))
                timer.usleep(1000000)
                
                local returnSpace = spaces.focusedSpace()
                print("Returned to space: " .. returnSpace)
                if returnSpace == currentSpace then
                    print("✅ Successfully returned to original space")
                end
            else
                print("❌ Ctrl+1 didn't work as expected")
            end
        else
            print("⚠️  Already on first space - testing Ctrl+2...")
            
            if #spacesForScreen >= 2 then
                eventtap.keyStroke({"ctrl"}, "2")
                timer.usleep(1000000)
                
                local newSpace = spaces.focusedSpace()
                print("Space after Ctrl+2: " .. newSpace)
                
                if newSpace == spacesForScreen[2] then
                    print("✅ SUCCESS: Ctrl+2 works!")
                    
                    -- Return
                    eventtap.keyStroke({"ctrl"}, "1")
                    timer.usleep(1000000)
                    print("Returned to first space")
                else
                    print("❌ Ctrl+2 didn't work")
                end
            else
                print("⚠️  Only one space available")
            end
        end
    else
        print("❌ Cannot determine current position")
    end
    '''
    
    try:
        print("⚠️ WATCH FOR SPACE CHANGES...")
        time.sleep(1)
        
        result = subprocess.run([hs_cli, '-c', script], 
                               capture_output=True, text=True, timeout=20)
        
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                print(f"  {line}")
        
        if result.stderr:
            print(f"Errors: {result.stderr}")
    
    except Exception as e:
        print(f"❌ Numeric space switching test failed: {e}")

def test_app_activation_combo():
    """Test combining app activation with space switching."""
    print("\n🎯 Testing App Activation + Space Navigation Combo")
    print("=" * 47)
    
    hs_cli = find_hammerspoon_cli()
    
    script = '''
    local application = require("hs.application")
    local eventtap = require("hs.eventtap")
    local spaces = require("hs.spaces")
    local timer = require("hs.timer")
    
    print("Current space: " .. spaces.focusedSpace())
    
    -- Find Code app
    local codeApp = application.find("Code")
    if codeApp then
        print("✅ Found Code app")
        
        -- Strategy: Activate app first, then use keyboard shortcuts to navigate windows
        print("\\n🔄 Testing app activation + window navigation...")
        
        -- Activate the app
        codeApp:activate()
        timer.usleep(500000) -- 0.5 seconds
        
        print("App activated, current space: " .. spaces.focusedSpace())
        
        -- Now try Cmd+` to cycle through windows (if available)
        print("\\n⌨️  Testing Cmd+` (cycle through app windows)...")
        eventtap.keyStroke({"cmd"}, "`")
        timer.usleep(500000)
        
        local newSpace = spaces.focusedSpace()
        print("Space after Cmd+`: " .. newSpace)
        
        -- Try Window menu approach
        print("\\n📋 Testing Window menu navigation...")
        local success = codeApp:selectMenuItem({"Window"})
        if success then
            print("✅ Can access Window menu")
        else
            print("❌ Cannot access Window menu")
        end
        
    else
        print("❌ Code app not found")
    end
    '''
    
    try:
        print("⚠️ WATCH FOR APP ACTIVATION AND WINDOW CHANGES...")
        time.sleep(1)
        
        result = subprocess.run([hs_cli, '-c', script], 
                               capture_output=True, text=True, timeout=15)
        
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                print(f"  {line}")
        
        if result.stderr:
            print(f"Errors: {result.stderr}")
    
    except Exception as e:
        print(f"❌ App activation combo test failed: {e}")

def main():
    """Test keyboard shortcuts for space switching."""
    print("⌨️ Keyboard Shortcut Space Navigation Test")
    print("=" * 40)
    print("🎯 Testing keyboard shortcuts as an alternative to Mission Control")
    print("💡 This could be fast, reliable, and less visually disruptive")
    print("")
    
    # Test 1: Basic space switching with Ctrl+Arrow
    test_keyboard_space_switching()
    
    # Test 2: Numeric space switching with Ctrl+Number
    test_numeric_space_switching()
    
    # Test 3: App activation + navigation combo
    test_app_activation_combo()
    
    print(f"\n{'='*40}")
    print("KEYBOARD SHORTCUT ANALYSIS")
    print(f"{'='*40}")
    print("Benefits of keyboard shortcuts:")
    print("✅ Fast execution (no Mission Control delay)")
    print("✅ Less visually disruptive than Mission Control")
    print("✅ Works across all spaces")
    print("✅ Can be combined with app activation")
    print("")
    print("Considerations:")
    print("⚠️ Requires user's keyboard shortcuts to be enabled")
    print("⚠️ May conflict with user's custom shortcuts")
    print("💡 Could be good fallback if user approves")

if __name__ == "__main__":
    main()