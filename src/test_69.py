#!/usr/bin/env python3
"""
test_69.py - Test Window ID Capture and Cross-Space Focusing

Tests the proven approach:
1. Capture focused window ID (not title)
2. Wait 5 seconds 
3. Use cross-space windowfilter to focus by ID

Based on proven GitHub #3276 workaround from APPROACHES.md.
"""

import subprocess
import time
from pathlib import Path


def get_hammerspoon_cli():
    """Get Hammerspoon CLI path."""
    hs_cli = "/Applications/Hammerspoon.app/Contents/Frameworks/hs/hs"
    if not Path(hs_cli).exists():
        print("❌ Hammerspoon CLI not found")
        return None
    return hs_cli


def capture_focused_window_id():
    """Capture the currently focused window ID."""
    print("📍 Phase 1: Capturing Focused Window ID")
    print("=" * 40)
    
    hs_cli = get_hammerspoon_cli()
    if not hs_cli:
        return None
    
    script = """
    local win = hs.window.focusedWindow()
    if win then
        local winID = win:id()
        local app = win:application():name()
        local title = win:title() or "NO_TITLE"
        
        print("WINDOW_ID:" .. winID)
        print("WINDOW_APP:" .. app)
        print("WINDOW_TITLE:" .. title)
    else
        print("ERROR:No focused window")
    end
    """
    
    try:
        result = subprocess.run([hs_cli, "-c", script], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            info = {}
            
            for line in lines:
                if line.startswith("WINDOW_ID:"):
                    info["id"] = line.split(":", 1)[1]
                elif line.startswith("WINDOW_APP:"):
                    info["app"] = line.split(":", 1)[1]
                elif line.startswith("WINDOW_TITLE:"):
                    info["title"] = line.split(":", 1)[1]
            
            if info.get("id"):
                print(f"✅ Captured Window:")
                print(f"   ID: {info['id']}")
                print(f"   App: {info.get('app', 'UNKNOWN')}")
                print(f"   Title: {info.get('title', 'UNKNOWN')}")
                return info
            
        print(f"❌ Failed to capture window: {result.stderr}")
        return None
        
    except Exception as e:
        print(f"❌ Error capturing window: {e}")
        return None


def countdown_wait():
    """Wait 5 seconds with countdown."""
    print("\n⏳ Phase 2: Waiting 5 seconds...")
    print("=" * 40)
    print("🔄 Switch to a different space/window now!")
    
    for i in range(5, 0, -1):
        print(f"   {i}...")
        time.sleep(1)
    
    print("✅ Wait complete! Attempting focus...")


def focus_window_by_id(target_window):
    """Focus window using ID and cross-space detection."""
    print("\n🎯 Phase 3: Cross-Space Window Focusing")
    print("=" * 40)
    
    hs_cli = get_hammerspoon_cli()
    if not hs_cli:
        return False
    
    window_id = target_window["id"]
    app_name = target_window.get("app", "UNKNOWN")
    
    print(f"🔍 Looking for window ID: {window_id} (App: {app_name})")
    
    script = f"""
    local windowfilter = require("hs.window.filter")
    local spaces = require("hs.spaces")
    
    local targetID = {window_id}
    local currentSpace = spaces.focusedSpace()
    
    print("Current space: " .. currentSpace)
    print("Target window ID: " .. targetID)
    print("")
    
    -- Use GitHub #3276 workaround for cross-space detection
    print("🔍 Using cross-space windowfilter detection...")
    local wf_cross = windowfilter.new()
    wf_cross:setCurrentSpace(false)  -- The magic workaround!
    local crossWindows = wf_cross:getWindows()
    
    print("Cross-space windows found: " .. #crossWindows)
    
    local targetWindow = nil
    local foundInfo = ""
    
    -- Search for our target window ID
    for i, win in pairs(crossWindows) do
        local winID = win:id()
        local winApp = win:application():name()
        local winTitle = win:title() or "NO_TITLE"
        local winSpaces = spaces.windowSpaces(winID)
        local spaceInfo = winSpaces and winSpaces[1] or "UNKNOWN"
        
        print("WIN" .. i .. ": ID=" .. winID .. " App=" .. winApp .. " Space=" .. spaceInfo)
        
        if winID == targetID then
            targetWindow = win
            foundInfo = "Found target: " .. winApp .. " '" .. winTitle .. "' (Space " .. spaceInfo .. ")"
            break
        end
    end
    
    print("")
    
    if targetWindow then
        print("✅ " .. foundInfo)
        print("🔄 Attempting to focus...")
        
        local success = targetWindow:focus()
        print("Focus command result: " .. tostring(success))
        
        -- Wait and verify
        local timer = require("hs.timer")
        timer.usleep(500000) -- 0.5 second
        
        local newFocused = hs.window.focusedWindow()
        if newFocused and newFocused:id() == targetID then
            print("🎉 SUCCESS: Window is now focused!")
            print("New focused window: " .. newFocused:application():name() .. " '" .. (newFocused:title() or "NO_TITLE") .. "'")
        else
            local currentFocused = newFocused and (newFocused:application():name() .. " '" .. (newFocused:title() or "NO_TITLE") .. "'") or "NONE"
            print("❌ FAILED: Focus did not switch to target")
            print("Currently focused: " .. currentFocused)
        end
    else
        print("❌ Target window ID " .. targetID .. " not found in cross-space results")
        print("This could be due to the Hammerspoon recency limitation")
        print("(Window may be in a space that hasn't been recently active)")
    end
    """
    
    try:
        result = subprocess.run([hs_cli, "-c", script], capture_output=True, text=True, timeout=15)
        
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                print(f"  {line}")
        
        if result.stderr:
            print(f"Errors: {result.stderr}")
        
        success = "SUCCESS: Window is now focused!" in result.stdout
        return success
        
    except Exception as e:
        print(f"❌ Error during focus attempt: {e}")
        return False


def main():
    """Test window ID capture and cross-space focusing."""
    print("🧪 Window ID Capture and Cross-Space Focus Test")
    print("=" * 48)
    print("This test will:")
    print("1. Capture your currently focused window ID")
    print("2. Wait 5 seconds for you to switch spaces/windows")
    print("3. Use cross-space detection to focus the original window")
    print()
    
    # Phase 1: Capture focused window ID
    target_window = capture_focused_window_id()
    if not target_window:
        print("\n❌ Cannot proceed without window ID")
        return
    
    # Phase 2: Wait period
    countdown_wait()
    
    # Phase 3: Focus by ID using cross-space method
    success = focus_window_by_id(target_window)
    
    # Results
    print(f"\n{'=' * 48}")
    print("TEST RESULTS")
    print(f"{'=' * 48}")
    
    if success:
        print("🎉 SUCCESS: Cross-space window focusing worked!")
        print("✅ Window ID approach is viable for Claude Code hooks")
        print("🚀 Ready to implement actual hook scripts")
    else:
        print("❌ FAILED: Cross-space focusing did not work")
        print("🤔 May need to investigate recency limitation or fallback approaches")
    
    print(f"\nTarget window ID: {target_window['id']}")
    print(f"Target app: {target_window.get('app', 'UNKNOWN')}")


if __name__ == "__main__":
    main()