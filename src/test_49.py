#!/usr/bin/env python3
"""
test_49.py - Hammerspoon cross-space window focusing test

Now that Hammerspoon is installed, let's test its claimed ability to:
1. Find windows across spaces
2. Switch to the window's space 
3. Focus the specific window

This is the most promising approach from the external report.
"""

import asyncio
import subprocess
import logging
import os
from pathlib import Path

# Setup logging
project_root = Path(__file__).parent.parent
tmp_dir = project_root / "tmp"
tmp_dir.mkdir(exist_ok=True)
log_file = tmp_dir / "test_49.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def get_our_context():
    """Get our execution context for targeting."""
    project_name = Path(os.getcwd()).name
    window_title = f"Claude Code — {project_name}"
    
    return {
        'project_name': project_name,
        'window_title': window_title,
        'directory': os.getcwd()
    }


def find_hammerspoon_cli():
    """Find Hammerspoon CLI tool."""
    # Common locations for Hammerspoon CLI
    hammerspoon_paths = [
        '/usr/local/bin/hs',
        '/opt/homebrew/bin/hs',
        '/Applications/Hammerspoon.app/Contents/Frameworks/hs/hs',
        '/Applications/Hammerspoon.app/Contents/Resources/extensions/hs/hs'
    ]
    
    # Check common paths
    for path in hammerspoon_paths:
        if Path(path).exists():
            return path
    
    # Try which command
    try:
        result = subprocess.run(['which', 'hs'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    return None


def test_hammerspoon_basic():
    """Test basic Hammerspoon functionality."""
    print("🔨 Testing Hammerspoon Basic Functionality")
    print("=" * 40)
    
    hs_cli = find_hammerspoon_cli()
    if not hs_cli:
        print("❌ Hammerspoon CLI not found")
        print("💡 Make sure Hammerspoon is installed and CLI is available")
        return False
    
    print(f"✅ Hammerspoon CLI found: {hs_cli}")
    
    # Test basic functionality
    test_script = 'print("Hammerspoon CLI test successful")'
    
    try:
        result = subprocess.run([hs_cli, '-c', test_script],
                               capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("✅ Hammerspoon CLI is functional")
            if result.stdout:
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Hammerspoon CLI test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Hammerspoon test failed: {e}")
        return False


def test_hammerspoon_spaces_module():
    """Test if Hammerspoon spaces module is available."""
    print("\n🌌 Testing Hammerspoon Spaces Module")
    print("=" * 35)
    
    hs_cli = find_hammerspoon_cli()
    if not hs_cli:
        return False
    
    # Test spaces module availability
    spaces_test = '''
    local spaces = require("hs.spaces")
    if spaces then
        print("✅ hs.spaces module available")
        
        -- Test getting current space
        local currentSpace = spaces.focusedSpace()
        if currentSpace then
            print("✅ Can get current space ID: " .. currentSpace)
        else
            print("❌ Cannot get current space")
        end
        
        -- Test getting all spaces
        local allSpaces = spaces.allSpaces()
        if allSpaces then
            local count = 0
            for screen, spaceList in pairs(allSpaces) do
                for _, space in pairs(spaceList) do
                    count = count + 1
                end
            end
            print("✅ Found " .. count .. " total spaces")
        else
            print("❌ Cannot get all spaces")
        end
        
    else
        print("❌ hs.spaces module not available")
    end
    '''
    
    try:
        result = subprocess.run([hs_cli, '-c', spaces_test],
                               capture_output=True, text=True, timeout=10)
        
        if result.stdout:
            print("Spaces module test:")
            print(result.stdout)
        
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        success = "hs.spaces module available" in result.stdout
        print(f"Status: {'✅ SUCCESS' if success else '❌ FAILED'}")
        return success
        
    except Exception as e:
        print(f"❌ Spaces module test failed: {e}")
        return False


def test_hammerspoon_window_detection():
    """Test Hammerspoon's ability to detect VS Code windows."""
    print("\n🪟 Testing Hammerspoon Window Detection")
    print("=" * 35)
    
    hs_cli = find_hammerspoon_cli()
    if not hs_cli:
        return False
    
    target_context = get_our_context()
    
    # Create Lua script to detect all VS Code windows
    window_detection_script = f'''
    local application = require("hs.application")
    local window = require("hs.window")
    local spaces = require("hs.spaces")
    
    print("🔍 Hammerspoon window detection test")
    
    -- Find VS Code application
    local vscode = application.get("Code")
    if not vscode then
        print("❌ VS Code application not found")
        return
    end
    
    print("📱 Found VS Code application: " .. vscode:name())
    print("   PID: " .. vscode:pid())
    print("   Is running: " .. tostring(vscode:isRunning()))
    
    -- Get all VS Code windows
    local windows = vscode:allWindows()
    print("\\n🪟 All VS Code windows (" .. #windows .. " total):")
    
    local targetTitle = "{target_context['window_title']}"
    local targetWindow = nil
    
    for i, win in pairs(windows) do
        local title = win:title() or "[No title]"
        print("   " .. i .. ". '" .. title .. "'")
        
        -- Check if window is visible
        local isVisible = win:isVisible()
        print("      Visible: " .. tostring(isVisible))
        
        -- Try to get window's space (this is the key test)
        local windowSpaces = spaces.windowSpaces(win)
        if windowSpaces and #windowSpaces > 0 then
            print("      Space: " .. windowSpaces[1])
        else
            print("      Space: Cannot determine")
        end
        
        -- Check if this is our target
        if title == targetTitle then
            targetWindow = win
            print("      🎯 THIS IS OUR TARGET WINDOW")
        end
        
        print()
    end
    
    -- Report results
    if targetWindow then
        print("✅ Target window found: " .. targetWindow:title())
        local targetSpaces = spaces.windowSpaces(targetWindow)
        if targetSpaces and #targetSpaces > 0 then
            print("✅ Target window space: " .. targetSpaces[1])
        else
            print("❌ Cannot determine target window space")
        end
    else
        print("❌ Target window not found: " .. targetTitle)
    end
    
    -- Get current space for comparison
    local currentSpace = spaces.focusedSpace()
    print("\\n📍 Current space: " .. (currentSpace or "unknown"))
    '''
    
    try:
        result = subprocess.run([hs_cli, '-c', window_detection_script],
                               capture_output=True, text=True, timeout=15)
        
        if result.stdout:
            print("Window detection results:")
            print(result.stdout)
        
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        success = "Target window found" in result.stdout and "Target window space:" in result.stdout
        print(f"Status: {'✅ SUCCESS' if success else '❌ FAILED'}")
        return success
        
    except Exception as e:
        print(f"❌ Window detection test failed: {e}")
        return False


def test_hammerspoon_cross_space_focus():
    """Test Hammerspoon's cross-space window focusing."""
    print("\n🎯 Testing Hammerspoon Cross-Space Focus")
    print("=" * 35)
    
    hs_cli = find_hammerspoon_cli()
    if not hs_cli:
        return False
    
    target_context = get_our_context()
    
    # Create the cross-space focusing script from the report
    cross_space_script = f'''
    local spaces = require("hs.spaces")
    local application = require("hs.application")
    local window = require("hs.window")
    
    print("🎯 Hammerspoon cross-space focus test")
    
    -- Find VS Code application
    local vscode = application.get("Code")
    if not vscode then
        print("❌ VS Code application not found")
        return
    end
    
    print("📱 Found VS Code application")
    
    -- Get all windows
    local windows = vscode:allWindows()
    print("🪟 VS Code windows found: " .. #windows)
    
    local targetTitle = "{target_context['window_title']}"
    local targetWindow = nil
    
    -- Find our target window
    for _, win in pairs(windows) do
        local title = win:title()
        print("   Checking: '" .. (title or "[No title]") .. "'")
        
        if title == targetTitle then
            targetWindow = win
            print("🎯 Found target window: " .. title)
            break
        end
    end
    
    if not targetWindow then
        print("❌ Target window not found")
        return
    end
    
    -- Get window's space
    local windowSpaces = spaces.windowSpaces(targetWindow)
    
    if not windowSpaces or #windowSpaces == 0 then
        print("❌ Could not determine window's space")
        return
    end
    
    local windowSpace = windowSpaces[1]
    print("🌌 Target window is in space: " .. windowSpace)
    
    -- Get current space to see if we need to switch
    local currentSpace = spaces.focusedSpace()
    print("📍 Currently in space: " .. currentSpace)
    
    if windowSpace == currentSpace then
        print("✅ Already in same space, just focusing window")
        targetWindow:focus()
        print("✅ Window focused")
        return
    end
    
    -- THE KEY TEST: Switch to window's space
    print("🔄 ATTEMPTING CROSS-SPACE SWITCH...")
    print("   From space " .. currentSpace .. " to space " .. windowSpace)
    
    local switchSuccess = spaces.gotoSpace(windowSpace)
    
    if switchSuccess then
        print("✅ Space switch successful!")
        
        -- Small delay for space transition
        local timer = require("hs.timer")
        timer.usleep(500000) -- 0.5 seconds
        
        -- Focus the window
        targetWindow:focus()
        print("✅ Window focused after space switch")
        
    else
        print("❌ Space switch failed")
    end
    '''
    
    try:
        result = subprocess.run([hs_cli, '-c', cross_space_script],
                               capture_output=True, text=True, timeout=15)
        
        if result.stdout:
            print("Cross-space focus results:")
            print(result.stdout)
        
        if result.stderr:
            print("Errors:")
            print(result.stderr)
        
        success = "Space switch successful" in result.stdout and "Window focused after space switch" in result.stdout
        print(f"Status: {'✅ SUCCESS' if success else '❌ FAILED'}")
        return success
        
    except Exception as e:
        print(f"❌ Cross-space focus test failed: {e}")
        return False


async def test_hammerspoon_from_different_space():
    """Test Hammerspoon cross-space capabilities from different space."""
    print("\n🌌 Hammerspoon Cross-Space Test")
    print("=" * 30)
    
    print(f"\n📋 Instructions:")
    print(f"   1. Switch to different space (like ai_advisory_system)")
    print(f"   2. Hammerspoon will attempt to:")
    print(f"      • Find the claude-code-notifier window")
    print(f"      • Determine which space it's in")
    print(f"      • Switch to that space")
    print(f"      • Focus the specific window")
    print(f"   3. This is THE definitive test")
    
    print(f"\n⏰ Switch spaces now! Countdown: ", end="", flush=True)
    
    for i in range(5, 0, -1):
        print(f"{i}...", end="", flush=True)
        await asyncio.sleep(1)
    
    print(" Testing!")
    
    # Run the cross-space focus test
    success = test_hammerspoon_cross_space_focus()
    
    return success


async def main():
    """Test Hammerspoon for cross-space window focusing."""
    logger.info("=" * 60)
    logger.info("🧪 Test 49: Hammerspoon Cross-Space Window Focusing")
    logger.info("=" * 60)
    
    print("🧪 Test 49: Hammerspoon Cross-Space Window Focusing")
    print("=" * 60)
    
    print("\n💡 Testing Hammerspoon's claimed cross-space capabilities")
    print("🎯 This is the most promising approach from the external report")
    
    target_context = get_our_context()
    print(f"\n📋 Target context:")
    print(f"   Project: {target_context['project_name']}")
    print(f"   Window: {target_context['window_title']}")
    
    logger.info(f"Target context: {target_context}")
    
    # Progressive testing
    basic_success = test_hammerspoon_basic()
    if not basic_success:
        print("\n❌ Hammerspoon basic functionality failed")
        print("💡 Check Hammerspoon installation and CLI setup")
        return
    
    spaces_success = test_hammerspoon_spaces_module()
    if not spaces_success:
        print("\n❌ Hammerspoon spaces module not available")
        print("💡 Spaces module may require macOS permissions")
        return
    
    window_detection_success = test_hammerspoon_window_detection()
    if not window_detection_success:
        print("\n❌ Hammerspoon window detection failed")
        return
    
    # Current space test
    print(f"\n📍 CURRENT SPACE TEST")
    print(f"=" * 20)
    current_space_success = test_hammerspoon_cross_space_focus()
    
    # Cross-space test (the critical one)
    cross_space_success = await test_hammerspoon_from_different_space()
    
    # Final analysis
    print(f"\n{'='*60}")
    print("HAMMERSPOON CROSS-SPACE RESULTS")
    print(f"{'='*60}")
    
    print(f"\n✅ Basic Functionality: {'SUCCESS' if basic_success else 'FAILED'}")
    print(f"✅ Spaces Module: {'SUCCESS' if spaces_success else 'FAILED'}")
    print(f"✅ Window Detection: {'SUCCESS' if window_detection_success else 'FAILED'}")
    print(f"📍 Current Space Focus: {'SUCCESS' if current_space_success else 'FAILED'}")
    print(f"🌌 Cross-Space Focus: {'SUCCESS' if cross_space_success else 'FAILED'}")
    
    if cross_space_success:
        print(f"\n🎉 BREAKTHROUGH: Hammerspoon solved cross-space window focusing!")
        print(f"   ✅ Can detect windows across spaces")
        print(f"   ✅ Can switch to window's space")
        print(f"   ✅ Can focus specific window")
        print(f"\n🚀 IMPLEMENTATION READY:")
        print(f"   • Use Hammerspoon as cross-space focusing backend")
        print(f"   • Python calls Hammerspoon Lua scripts")
        print(f"   • Reliable cross-space window focusing achieved")
        
    elif window_detection_success:
        print(f"\n⚠️ Partial Success:")
        print(f"   ✅ Hammerspoon can detect windows across spaces")
        print(f"   ❌ Space switching or window focusing failed")
        print(f"   💡 May need permissions or different approach")
        
    else:
        print(f"\n❌ Hammerspoon approach failed")
        print(f"   Same fundamental limitations as other approaches")
        print(f"   External report claims appear incorrect")
    
    print(f"\n📋 Log: {log_file}")
    logger.info("Test 49 completed")


if __name__ == "__main__":
    asyncio.run(main())