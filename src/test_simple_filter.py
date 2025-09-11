#!/usr/bin/env python3
"""
test_simple_filter.py - Simple test of hs.window.filter

The previous test timed out, so let's test more simply to see if
hs.window.filter can be used at all.
"""

import subprocess
import time

def find_hammerspoon_cli():
    """Find Hammerspoon CLI."""
    return "/Applications/Hammerspoon.app/Contents/Frameworks/hs/hs"

def test_simple_filter():
    """Simple test to see if window filter works at all."""
    print("🔍 Simple Window Filter Test")
    print("=" * 27)
    
    hs_cli = find_hammerspoon_cli()
    
    script = '''
    print("Testing hs.window.filter availability...")
    
    local success, windowfilter = pcall(require, "hs.window.filter")
    if success then
        print("✅ hs.window.filter module loaded successfully")
        
        -- Try to create a simple filter
        local allFilter = windowfilter.new()
        if allFilter then
            print("✅ Created basic window filter")
            
            -- Try to get windows (with timeout protection)
            local windows = allFilter:getWindows()
            print("✅ Got windows from filter: " .. #windows)
            
            -- Show first few windows
            for i = 1, math.min(3, #windows) do
                local win = windows[i]
                local title = win:title() or "NO TITLE"
                local appName = win:application():name()
                print("  " .. i .. ": " .. title .. " [" .. appName .. "]")
            end
            
        else
            print("❌ Failed to create window filter")
        end
    else
        print("❌ Failed to load hs.window.filter: " .. tostring(windowfilter))
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
            
        if result.returncode != 0:
            print(f"❌ Script failed with return code: {result.returncode}")
    
    except subprocess.TimeoutExpired:
        print("❌ Test timed out - window filter may be slow or broken")
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_code_filter():
    """Test creating a filter specifically for Code app."""
    print("\n🎯 Code App Filter Test")
    print("=" * 22)
    
    hs_cli = find_hammerspoon_cli()
    
    script = '''
    local windowfilter = require("hs.window.filter")
    
    print("Creating Code app filter...")
    local codeFilter = windowfilter.new('Code')
    
    if codeFilter then
        print("✅ Code filter created")
        
        local codeWindows = codeFilter:getWindows()
        print("Code windows found: " .. #codeWindows)
        
        for i, win in pairs(codeWindows) do
            local title = win:title() or "NO TITLE"
            print("  " .. i .. ": " .. title)
        end
    else
        print("❌ Failed to create Code filter")
    end
    '''
    
    try:
        result = subprocess.run([hs_cli, '-c', script], 
                               capture_output=True, text=True, timeout=8)
        
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                print(f"  {line}")
        
        if result.stderr:
            print(f"Errors: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ Code filter test timed out")
    except Exception as e:
        print(f"❌ Code filter test failed: {e}")

def main():
    """Simple test of window filter functionality."""
    print("🧪 Simple Hammerspoon Window Filter Test")
    print("=" * 39)
    
    # Test 1: Basic functionality
    test_simple_filter()
    
    # Test 2: Code-specific filter
    test_code_filter()
    
    print(f"\n{'='*39}")
    print("If these tests work, we can proceed to cross-space testing")
    print("If they timeout/fail, window filter may not be viable")

if __name__ == "__main__":
    main()