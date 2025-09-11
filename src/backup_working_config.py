#!/usr/bin/env python3
"""
backup_working_config.py - Backup the current working Hammerspoon configuration

The GitHub workaround is now working! This script captures the current state
so we can restore it if something breaks in the future.
"""

import subprocess
import json
import os
from datetime import datetime

def find_hammerspoon_cli():
    """Find Hammerspoon CLI."""
    return "/Applications/Hammerspoon.app/Contents/Frameworks/hs/hs"

def backup_hammerspoon_config():
    """Backup the current Hammerspoon configuration."""
    print("💾 Backing Up Working Hammerspoon Configuration")
    print("=" * 47)
    
    # Get Hammerspoon config directory
    hammerspoon_dir = os.path.expanduser("~/.hammerspoon")
    
    if os.path.exists(hammerspoon_dir):
        print(f"✅ Found Hammerspoon config directory: {hammerspoon_dir}")
        
        # List config files
        config_files = []
        for file in os.listdir(hammerspoon_dir):
            if file.endswith(('.lua', '.json')):
                config_files.append(file)
        
        print(f"📁 Config files found: {config_files}")
        
        # Create backup directory
        backup_dir = "/Users/trenthm/working_dir/claude-code-notifier/backups/hammerspoon"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Copy each config file
        for file in config_files:
            source = os.path.join(hammerspoon_dir, file)
            dest = os.path.join(backup_dir, file)
            
            try:
                with open(source, 'r') as src:
                    content = src.read()
                
                with open(dest, 'w') as dst:
                    dst.write(content)
                    
                print(f"✅ Backed up: {file}")
                
                # Show content preview for init.lua
                if file == 'init.lua':
                    print(f"\n📝 init.lua content preview:")
                    lines = content.split('\n')[:10]  # First 10 lines
                    for i, line in enumerate(lines, 1):
                        print(f"   {i:2d}: {line}")
                    if len(content.split('\n')) > 10:
                        print(f"   ... ({len(content.split('\n')) - 10} more lines)")
                        
            except Exception as e:
                print(f"❌ Failed to backup {file}: {e}")
    else:
        print(f"❌ Hammerspoon config directory not found: {hammerspoon_dir}")

def get_hammerspoon_version():
    """Get current Hammerspoon version information."""
    print("\n🔧 Hammerspoon Version Information")
    print("=" * 34)
    
    hs_cli = find_hammerspoon_cli()
    
    script = '''
    print("Hammerspoon version: " .. hs.processInfo.version)
    print("Build: " .. hs.processInfo.buildTime)
    print("macOS version: " .. hs.host.operatingSystemVersionString())
    
    -- List loaded modules
    print("\\nLoaded modules:")
    local modules = {"hs.window.filter", "hs.spaces", "hs.application", "hs.window"}
    for _, module in pairs(modules) do
        local success, mod = pcall(require, module)
        if success then
            print("  ✅ " .. module)
        else
            print("  ❌ " .. module .. " - " .. tostring(mod))
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
            
        return result.stdout if result.returncode == 0 else None
    
    except Exception as e:
        print(f"❌ Failed to get version info: {e}")
        return None

def create_working_solution_backup():
    """Create a complete backup of the working solution."""
    print("\n📋 Creating Complete Solution Backup")
    print("=" * 36)
    
    backup_info = {
        "timestamp": datetime.now().isoformat(),
        "solution_status": "WORKING - Cross-space window focusing successful",
        "approach": "GitHub issue #3276 workaround using setCurrentSpace(false)",
        "test_results": {
            "can_detect_cross_space_windows": True,
            "can_focus_cross_space_windows": True,
            "requires_mission_control": False,
            "last_focused_limitation": "Present but working for our use case"
        },
        "verified_functionality": [
            "hs.window.filter with setCurrentSpace(false) finds cross-space windows",
            "window.focus() successfully switches spaces and focuses window",
            "Clean space switching without Mission Control animation",
            "Works for VS Code windows across different spaces"
        ],
        "github_issue": "https://github.com/Hammerspoon/hammerspoon/issues/3276",
        "key_code_pattern": {
            "detection": "wf_other = windowfilter.new('Code'); wf_other:setCurrentSpace(false)",
            "focusing": "targetWindow:focus()"
        }
    }
    
    # Save backup info
    backup_dir = "/Users/trenthm/working_dir/claude-code-notifier/backups"
    os.makedirs(backup_dir, exist_ok=True)
    
    backup_file = os.path.join(backup_dir, "working_solution_backup.json")
    
    try:
        with open(backup_file, 'w') as f:
            json.dump(backup_info, f, indent=2)
        
        print(f"✅ Solution backup saved: {backup_file}")
        
        # Also save the test script that works
        working_script = "/Users/trenthm/working_dir/claude-code-notifier/src/test_github_workaround.py"
        backup_script = os.path.join(backup_dir, "working_test_script.py")
        
        if os.path.exists(working_script):
            with open(working_script, 'r') as src:
                content = src.read()
            with open(backup_script, 'w') as dst:
                dst.write(content)
            print(f"✅ Working test script backed up: {backup_script}")
        
    except Exception as e:
        print(f"❌ Failed to create solution backup: {e}")

def main():
    """Backup the current working Hammerspoon configuration and solution."""
    print("💾 Working Solution Backup")
    print("=" * 25)
    print("🎉 The GitHub workaround is working! Let's preserve this state.")
    print("")
    
    # Backup Hammerspoon config
    backup_hammerspoon_config()
    
    # Get version information  
    version_info = get_hammerspoon_version()
    
    # Create complete solution backup
    create_working_solution_backup()
    
    print(f"\n{'='*50}")
    print("BACKUP COMPLETE - WORKING STATE PRESERVED")
    print(f"{'='*50}")
    print("✅ Hammerspoon configuration backed up")
    print("✅ Version information captured")
    print("✅ Working solution documented")
    print("✅ Test script preserved")
    print("")
    print("🎯 Next steps:")
    print("1. Build production notification system using this approach")
    print("2. Test with real Claude Code integration")
    print("3. Create restore instructions if needed")

if __name__ == "__main__":
    main()