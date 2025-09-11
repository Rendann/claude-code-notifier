#!/usr/bin/env python3
"""
hammerspoon_setup.py - Hammerspoon setup and configuration helper

Guide to get Hammerspoon working with CLI access.
"""

import subprocess
from pathlib import Path

def check_hammerspoon_status():
    """Check if Hammerspoon is running and configured."""
    print("🔨 Hammerspoon Setup Check")
    print("=" * 25)
    
    # Check if Hammerspoon app exists
    app_path = Path("/Applications/Hammerspoon.app")
    if app_path.exists():
        print("✅ Hammerspoon.app found in Applications")
    else:
        print("❌ Hammerspoon.app not found in Applications")
        print("💡 Install with: brew install --cask hammerspoon")
        return False
    
    # Check if Hammerspoon is running
    try:
        result = subprocess.run(['pgrep', '-f', 'Hammerspoon'], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Hammerspoon is running")
        else:
            print("❌ Hammerspoon is not running")
            print("💡 Start Hammerspoon from Applications folder")
            return False
    except:
        print("❌ Cannot check if Hammerspoon is running")
        return False
    
    # Check CLI access
    hs_cli = "/Applications/Hammerspoon.app/Contents/Frameworks/hs/hs"
    try:
        result = subprocess.run([hs_cli, '-c', 'print("CLI test")'], 
                               capture_output=True, text=True, timeout=3)
        if result.returncode == 0:
            print("✅ Hammerspoon CLI is working")
            return True
        else:
            print("❌ Hammerspoon CLI not working")
            print(f"   Error: {result.stderr}")
            print("\n💡 SETUP REQUIRED:")
            print("   1. Open Hammerspoon.app")
            print("   2. Add this to your ~/.hammerspoon/init.lua:")
            print("      hs.ipc.cliInstall()")
            print("   3. Reload config (Cmd+R in Hammerspoon console)")
            return False
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

def create_hammerspoon_config():
    """Create basic Hammerspoon config with IPC enabled."""
    print("\n📝 Creating Hammerspoon Config")
    print("=" * 30)
    
    hammerspoon_dir = Path.home() / ".hammerspoon"
    init_file = hammerspoon_dir / "init.lua"
    
    # Create directory if it doesn't exist
    hammerspoon_dir.mkdir(exist_ok=True)
    
    # Basic config with IPC and spaces modules
    config_content = '''-- Hammerspoon configuration for Claude Code Notifier
-- This enables CLI access and loads required modules

-- Enable CLI access
hs.ipc.cliInstall()

-- Load required modules
local spaces = require("hs.spaces")
local application = require("hs.application")
local window = require("hs.window")

print("Hammerspoon loaded with CLI and spaces support")

-- Test function for Claude Code Notifier
function focusVSCodeWindow(targetTitle)
    local vscode = application.get("Code")
    if not vscode then
        return false, "VS Code not found"
    end
    
    local windows = vscode:allWindows()
    for _, win in pairs(windows) do
        if win:title() == targetTitle then
            local windowSpaces = spaces.windowSpaces(win)
            if windowSpaces and #windowSpaces > 0 then
                spaces.gotoSpace(windowSpaces[1])
                win:focus()
                return true, "Window focused"
            end
        end
    end
    
    return false, "Window not found"
end
'''
    
    # Write config file
    with open(init_file, 'w') as f:
        f.write(config_content)
    
    print(f"✅ Created config file: {init_file}")
    print("\n🔄 Next steps:")
    print("   1. Open Hammerspoon.app")
    print("   2. It should automatically load the new config")
    print("   3. Or manually reload with Cmd+R in Hammerspoon console")
    print("   4. Look for 'Hammerspoon loaded with CLI and spaces support' message")
    
    return True

def main():
    """Main setup flow."""
    print("🧪 Hammerspoon Setup for Claude Code Notifier")
    print("=" * 50)
    
    if check_hammerspoon_status():
        print("\n🎉 Hammerspoon is ready!")
        print("You can now run test_49.py")
    else:
        print("\n🛠️ Setup required...")
        create_hammerspoon_config()
        print("\n⚠️ After setup, run this script again to verify")

if __name__ == "__main__":
    main()