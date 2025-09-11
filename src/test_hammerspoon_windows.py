#!/usr/bin/env python3
"""
test_hammerspoon_windows.py - Test Hammerspoon window detection across spaces

This tests whether Hammerspoon can see and manipulate windows across all spaces,
which would solve the cross-space focusing problem without using Mission Control.

Expected VS Code windows:
1. claude-code-notifier (space 5) <- current space
2. claude-config-manager (space 5) <- current space  
3. g710plus (space 3, minimized)
4. ai_advisory_system (space 6) <- different space
"""

import subprocess
import time

def find_hammerspoon_cli():
    """Find Hammerspoon CLI."""
    return "/Applications/Hammerspoon.app/Contents/Frameworks/hs/hs"

def test_window_detection():
    """Test what windows Hammerspoon can see across all spaces."""
    print("👁️ Testing Hammerspoon Window Detection")
    print("=" * 38)
    
    hs_cli = find_hammerspoon_cli()
    
    script = '''
    local application = require("hs.application")
    local window = require("hs.window")
    local spaces = require("hs.spaces")
    
    print("🔍 Current space: " .. spaces.focusedSpace())
    print("")
    
    -- Test 1: All windows across all apps
    print("📋 ALL WINDOWS (all apps):")
    local allWindows = window.allWindows()
    print("Total windows found: " .. #allWindows)
    
    -- Test 2: Find VS Code specifically  
    local vsCodeApp = application.find("Visual Studio Code")
    if vsCodeApp then
        print("\\n📱 VS CODE APPLICATION FOUND")
        print("App name: " .. vsCodeApp:name())
        print("App bundle ID: " .. vsCodeApp:bundleID())
        
        -- Get VS Code windows
        local vsCodeWindows = vsCodeApp:allWindows()
        print("VS Code windows found: " .. #vsCodeWindows)
        
        -- List each VS Code window
        for i, win in pairs(vsCodeWindows) do
            local title = win:title() or "NO TITLE"
            local winID = win:id()
            
            -- Try to get space info for this window
            local winSpaces = spaces.windowSpaces(winID)
            local spaceInfo = "UNKNOWN"
            if winSpaces and #winSpaces > 0 then
                spaceInfo = "Space " .. winSpaces[1]
                if #winSpaces > 1 then
                    spaceInfo = spaceInfo .. " (+" .. (#winSpaces - 1) .. " more)"
                end
            end
            
            -- Check if window is minimized
            local isMinimized = win:isMinimized() and " [MINIMIZED]" or ""
            
            print("  " .. i .. ": \\"" .. title .. "\\" (ID: " .. winID .. ")")
            print("      Space: " .. spaceInfo .. isMinimized)
        end
    else
        print("\\n❌ VS CODE APPLICATION NOT FOUND")
        print("Available applications:")
        local allApps = application.runningApplications()
        for i, app in pairs(allApps) do
            if string.find(string.lower(app:name()), "code") or 
               string.find(string.lower(app:name()), "electron") then
                print("  - " .. app:name() .. " (" .. app:bundleID() .. ")")
            end
        end
    end
    
    -- Test 3: Alternative window detection methods
    print("\\n🔍 ALTERNATIVE DETECTION METHODS:")
    
    -- Try filtering all windows by app
    local codeWindows = {}
    for i, win in pairs(allWindows) do
        local app = win:application()
        if app and (app:name() == "Visual Studio Code" or 
                   string.find(app:name(), "Code") or
                   app:bundleID() == "com.microsoft.VSCode") then
            table.insert(codeWindows, win)
        end
    end
    
    print("Windows found via filtering: " .. #codeWindows)
    for i, win in pairs(codeWindows) do
        local title = win:title() or "NO TITLE"
        local app = win:application()
        print("  " .. i .. ": \\"" .. title .. "\\" [" .. app:name() .. "]")
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
        print(f"❌ Window detection failed: {e}")

def test_window_focusing():
    """Test if Hammerspoon can focus windows directly across spaces."""
    print("\n🎯 Testing Cross-Space Window Focusing")
    print("=" * 36)
    
    hs_cli = find_hammerspoon_cli()
    
    script = '''
    local application = require("hs.application")
    local window = require("hs.window")
    local spaces = require("hs.spaces")
    
    local currentSpace = spaces.focusedSpace()
    print("Current space: " .. currentSpace)
    
    -- Find VS Code
    local vsCodeApp = application.find("Visual Studio Code")
    if vsCodeApp then
        local vsCodeWindows = vsCodeApp:allWindows()
        print("Found " .. #vsCodeWindows .. " VS Code windows")
        
        -- Look for a window that's NOT in the current space
        local targetWindow = nil
        local targetWindowInfo = ""
        
        for i, win in pairs(vsCodeWindows) do
            local winID = win:id()
            local title = win:title() or "NO TITLE"
            local winSpaces = spaces.windowSpaces(winID)
            
            if winSpaces and #winSpaces > 0 then
                local winSpace = winSpaces[1]
                if winSpace ~= currentSpace and not win:isMinimized() then
                    targetWindow = win
                    targetWindowInfo = title .. " (Space " .. winSpace .. ")"
                    print("Target window: " .. targetWindowInfo)
                    break
                end
            end
        end
        
        if targetWindow then
            print("\\n🔄 Attempting direct focus (no space switch)...")
            
            -- Try different focusing methods
            local methods = {
                "focus()", 
                "becomeMain()",
                "raise()",
                "application():selectMenuItem(\\"" .. targetWindow:title() .. "\\")"
            }
            
            for i, method in pairs(methods) do
                print("\\nMethod " .. i .. ": " .. method)
                
                local success, error = pcall(function()
                    if method == "focus()" then
                        return targetWindow:focus()
                    elseif method == "becomeMain()" then
                        return targetWindow:becomeMain()
                    elseif method == "raise()" then
                        return targetWindow:raise()
                    elseif string.find(method, "selectMenuItem") then
                        local app = targetWindow:application()
                        return app:selectMenuItem("Window", targetWindow:title())
                    end
                end)
                
                if success then
                    print("  Result: " .. tostring(error))
                    
                    -- Check if focus changed
                    local timer = require("hs.timer")
                    timer.usleep(500000) -- 0.5 seconds
                    
                    local newSpace = spaces.focusedSpace()
                    local focusedWin = window.focusedWindow()
                    local focusedTitle = focusedWin and focusedWin:title() or "NONE"
                    
                    print("  New space: " .. newSpace .. " (was " .. currentSpace .. ")")
                    print("  Focused window: " .. focusedTitle)
                    
                    if newSpace ~= currentSpace then
                        print("  🎉 SUCCESS: Space changed! Method works!")
                        break
                    elseif focusedTitle == targetWindow:title() then
                        print("  🎉 SUCCESS: Window focused! (same space)")
                        break
                    else
                        print("  ❌ No change detected")
                    end
                else
                    print("  ❌ Error: " .. tostring(error))
                end
            end
        else
            print("\\n⚠️ No cross-space windows found to test focusing")
            print("All windows are in current space or minimized")
        end
    else
        print("❌ VS Code not found")
    end
    '''
    
    try:
        print("⚠️ WATCH FOR WINDOW/SPACE CHANGES...")
        time.sleep(1)
        
        result = subprocess.run([hs_cli, '-c', script], 
                               capture_output=True, text=True, timeout=20)
        
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                print(f"  {line}")
        
        if result.stderr:
            print(f"Errors: {result.stderr}")
    
    except Exception as e:
        print(f"❌ Window focusing test failed: {e}")

def test_window_spaces_mapping():
    """Test how accurately Hammerspoon can map windows to spaces."""
    print("\n🗺️ Testing Window-to-Space Mapping")
    print("=" * 33)
    
    hs_cli = find_hammerspoon_cli()
    
    script = '''
    local application = require("hs.application")
    local window = require("hs.window")
    local spaces = require("hs.spaces")
    
    -- Get all spaces on main screen
    local spacesForScreen = spaces.spacesForScreen()
    print("Spaces on screen: " .. table.concat(spacesForScreen, ", "))
    
    local vsCodeApp = application.find("Visual Studio Code")
    if vsCodeApp then
        local vsCodeWindows = vsCodeApp:allWindows()
        print("\\nVS Code window space mapping:")
        
        for i, win in pairs(vsCodeWindows) do
            local title = win:title() or "NO TITLE"
            local winID = win:id()
            local winSpaces = spaces.windowSpaces(winID)
            
            local spaceList = "NONE"
            if winSpaces and #winSpaces > 0 then
                local spaceStrings = {}
                for j, spaceID in pairs(winSpaces) do
                    table.insert(spaceStrings, tostring(spaceID))
                end
                spaceList = table.concat(spaceStrings, ", ")
            end
            
            local isMinimized = win:isMinimized() and " [MINIMIZED]" or ""
            local isVisible = win:isVisible() and " [VISIBLE]" or " [HIDDEN]"
            
            print("  " .. title .. ":")
            print("    ID: " .. winID)
            print("    Spaces: [" .. spaceList .. "]" .. isMinimized .. isVisible)
        end
        
        -- Cross-reference with expected windows
        print("\\n📋 Expected vs Found:")
        local expectedWindows = {
            "claude-code-notifier", 
            "claude-config-manager",
            "g710plus",
            "ai_advisory_system"
        }
        
        for _, expected in pairs(expectedWindows) do
            local found = false
            for _, win in pairs(vsCodeWindows) do
                local title = win:title() or ""
                if string.find(string.lower(title), string.lower(expected)) then
                    found = true
                    break
                end
            end
            
            if found then
                print("  ✅ " .. expected)
            else
                print("  ❌ " .. expected .. " - NOT FOUND")
            end
        end
    else
        print("❌ VS Code application not found")
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
        print(f"❌ Window-space mapping test failed: {e}")

def main():
    """Test Hammerspoon window detection and focusing across spaces."""
    print("🪟 Hammerspoon Cross-Space Window Testing")
    print("=" * 42)
    print("🎯 Testing if Hammerspoon can see and focus windows across all spaces")
    print("📋 Expected VS Code windows:")
    print("   1. claude-code-notifier (space 5) <- current")
    print("   2. claude-config-manager (space 5) <- current") 
    print("   3. g710plus (space 3, minimized)")
    print("   4. ai_advisory_system (space 6) <- different space")
    print("")
    
    # Test 1: Window detection
    test_window_detection()
    
    # Test 2: Window focusing
    test_window_focusing()
    
    # Test 3: Window-space mapping
    test_window_spaces_mapping()
    
    print(f"\n{'='*42}")
    print("HAMMERSPOON WINDOW ANALYSIS")
    print(f"{'='*42}")
    print("Key questions answered:")
    print("1. ✅ Can Hammerspoon see ALL windows across spaces?")
    print("2. ✅ Can Hammerspoon focus cross-space windows directly?") 
    print("3. ✅ Does Hammerspoon provide accurate window-to-space mapping?")
    print("4. If YES to all: We have the solution!")
    print("5. If NO: We'll need alternative approaches")

if __name__ == "__main__":
    main()