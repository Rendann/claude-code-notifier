#!/usr/bin/env python3
"""
test_space_verification.py - Verify current space and window locations

The previous test showed confusing results. Let's get a clear picture of:
1. What space we're actually on
2. Where each VS Code window actually is
3. Whether the GitHub workaround found cross-space windows
"""

import subprocess

def find_hammerspoon_cli():
    """Find Hammerspoon CLI."""
    return "/Applications/Hammerspoon.app/Contents/Frameworks/hs/hs"

def test_simple_space_check():
    """Simple verification of current space and window locations."""
    print("🔍 Space and Window Verification")
    print("=" * 32)
    
    hs_cli = find_hammerspoon_cli()
    
    script = '''
    local spaces = require("hs.spaces")
    local application = require("hs.application")
    
    -- What space are we on?
    local currentSpace = spaces.focusedSpace()
    print("📍 Current space ID: " .. currentSpace)
    
    -- Get all spaces in order
    local spacesForScreen = spaces.spacesForScreen()
    print("🗺️ All spaces: [" .. table.concat(spacesForScreen, ", ") .. "]")
    
    -- Find current position
    for i, spaceID in pairs(spacesForScreen) do
        if spaceID == currentSpace then
            print("📌 Current position: " .. i .. " (of " .. #spacesForScreen .. ")")
            break
        end
    end
    
    print("")
    
    -- Find all VS Code windows and their locations
    local codeApp = application.find("Code")
    if codeApp then
        local codeWindows = codeApp:allWindows()
        print("🪟 All VS Code windows:")
        
        for i, win in pairs(codeWindows) do
            local title = win:title() or "NO TITLE"
            local winID = win:id()
            local winSpaces = spaces.windowSpaces(winID)
            local isMinimized = win:isMinimized()
            
            local spaceInfo = "UNKNOWN"
            if winSpaces and #winSpaces > 0 then
                spaceInfo = winSpaces[1]
            end
            
            local flags = isMinimized and " [MINIMIZED]" or ""
            print("  " .. i .. ": \\"" .. title .. "\\"")
            print("      Space: " .. spaceInfo .. flags)
            
            -- Check for our expected windows
            if string.find(string.lower(title), "claude-code-notifier") then
                print("      ✅ This is claude-code-notifier")
            elseif string.find(string.lower(title), "claude-config-manager") then
                print("      ✅ This is claude-config-manager") 
            elseif string.find(string.lower(title), "g710plus") then
                print("      ✅ This is g710plus")
            elseif string.find(string.lower(title), "ai_advisory") then
                print("      🎉 This is ai_advisory_system!")
            end
        end
        
        print("")
        print("📊 Summary:")
        print("   Total windows found: " .. #codeWindows)
        print("   Expected: claude-code-notifier, claude-config-manager, g710plus, ai_advisory_system")
        
    else
        print("❌ VS Code app not found")
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
        print(f"❌ Verification failed: {e}")

def main():
    """Verify current space and window locations."""
    print("📍 Space and Window Location Verification")
    print("=" * 41)
    print("🎯 Let's get a clear picture of where everything is")
    print("")
    
    test_simple_space_check()
    
    print(f"\n{'='*41}")
    print("Based on these results, we can determine:")
    print("1. What space you're actually on")
    print("2. Where each VS Code window is located") 
    print("3. Whether previous test results were accurate")

if __name__ == "__main__":
    main()