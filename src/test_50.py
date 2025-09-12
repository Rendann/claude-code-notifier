#!/usr/bin/env python3
"""
test_50.py - Universal Window Detection using GitHub #3276 workaround

Uses the proven working Hammerspoon approach to detect originating windows.
Process tree + Hammerspoon windowfilter with setCurrentSpace(false) + project matching.
"""

import subprocess
import os
import psutil
from pathlib import Path

def get_originating_app_from_process_tree():
    """Get originating application from process tree analysis."""
    print("🔄 Process Tree Analysis:")
    print("-" * 25)
    
    try:
        current_process = psutil.Process(os.getpid())
        
        print(f"Current Process: {current_process.name()} (PID: {os.getpid()})")
        
        # Walk up process tree looking for GUI applications
        parent = current_process.parent()
        level = 1
        
        while parent and level <= 8:
            name = parent.name().lower()
            cmdline = parent.cmdline()
            
            print(f"   Parent {level}: {parent.name()} (PID: {parent.pid})")
            
            # Look for GUI application indicators
            gui_indicators = [
                'electron', 'code', 'visual studio code',
                'terminal', 'iterm', 'iterm2',
                'intellij', 'pycharm', 'webstorm',
                'sublime', 'atom', 'cursor'
            ]
            
            # Check process name and cmdline
            found_indicator = None
            for indicator in gui_indicators:
                if indicator in name:
                    found_indicator = indicator
                    break
                if cmdline and indicator in ' '.join(cmdline).lower():
                    found_indicator = indicator
                    break
            
            if found_indicator:
                print(f"   ✅ Found GUI app indicator: '{found_indicator}'")
                return {
                    'process_name': parent.name(),
                    'pid': parent.pid,
                    'level': level,
                    'indicator': found_indicator
                }
            
            try:
                parent = parent.parent()
                level += 1
            except:
                break
        
        print("   ❌ No GUI app found in process tree")
        return None
        
    except Exception as e:
        print(f"   ❌ Process tree analysis failed: {e}")
        return None

def map_process_to_hammerspoon_app(process_info):
    """Map process information to Hammerspoon app name."""
    if not process_info:
        return None
    
    indicator = process_info.get('indicator', '').lower()
    
    # Universal mapping
    mappings = {
        'electron': 'Code',  # VS Code shows as Electron process but Code app
        'code': 'Code',
        'visual studio code': 'Code',
        'terminal': 'Terminal',
        'iterm': 'iTerm2',
        'iterm2': 'iTerm2',
        'intellij': 'IntelliJ IDEA',
        'pycharm': 'PyCharm',
        'webstorm': 'WebStorm',
        'sublime': 'Sublime Text',
        'cursor': 'Cursor'
    }
    
    return mappings.get(indicator, process_info.get('process_name', 'Unknown'))

def query_hammerspoon_cross_space_windows(app_name):
    """Query Hammerspoon using GitHub #3276 workaround for cross-space windows."""
    print(f"\n🔨 Hammerspoon Cross-Space Query (App: {app_name}):")
    print("-" * 55)
    
    try:
        hs_cli = "/Applications/Hammerspoon.app/Contents/Frameworks/hs/hs"
        if not Path(hs_cli).exists():
            print("   ❌ Hammerspoon not found")
            return []
        
        # Use the proven GitHub #3276 workaround
        script = f'''
        local windowfilter = require("hs.window.filter")
        local spaces = require("hs.spaces")
        
        print("Current space: " .. spaces.focusedSpace())
        
        -- GitHub #3276 workaround - this is the breakthrough!
        print("\\nUsing GitHub #3276 workaround...")
        
        -- Filter for current space windows
        local wf_current = windowfilter.new('{app_name}')
        wf_current:setCurrentSpace(true)
        local currentWindows = wf_current:getWindows()
        
        -- Filter for cross-space windows (THE KEY WORKAROUND!)
        local wf_cross = windowfilter.new('{app_name}')
        wf_cross:setCurrentSpace(false)  -- This is the magic!
        local crossWindows = wf_cross:getWindows()
        
        print("Current space {app_name} windows: " .. #currentWindows)
        print("Cross-space {app_name} windows: " .. #crossWindows)
        
        -- List current space windows
        for i, win in pairs(currentWindows) do
            local title = win:title() or "NO_TITLE"
            local winSpaces = spaces.windowSpaces(win:id())
            local spaceInfo = winSpaces and winSpaces[1] or "UNKNOWN"
            print("CURRENT:" .. title .. "|" .. spaceInfo .. "|" .. tostring(win:isVisible()) .. "|" .. tostring(win:isMinimized()))
        end
        
        -- List cross-space windows
        for i, win in pairs(crossWindows) do
            local title = win:title() or "NO_TITLE"
            local winSpaces = spaces.windowSpaces(win:id())
            local spaceInfo = winSpaces and winSpaces[1] or "UNKNOWN"
            print("CROSS_SPACE:" .. title .. "|" .. spaceInfo .. "|" .. tostring(win:isVisible()) .. "|" .. tostring(win:isMinimized()))
        end
        
        print("\\nTOTAL_WINDOWS:" .. (#currentWindows + #crossWindows))
        '''
        
        result = subprocess.run(
            [hs_cli, "-c", script],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            current_windows = []
            cross_windows = []
            
            print("   Hammerspoon output:")
            for line in lines:
                print(f"     {line}")
                
                if line.startswith("CURRENT:"):
                    parts = line[8:].split("|")  # Remove "CURRENT:"
                    if len(parts) >= 4:
                        title, space, visible, minimized = parts[0], parts[1], parts[2], parts[3]
                        current_windows.append({
                            'title': title,
                            'space': space,
                            'visible': visible == 'true',
                            'minimized': minimized == 'true',
                            'type': 'current_space'
                        })
                
                elif line.startswith("CROSS_SPACE:"):
                    parts = line[12:].split("|")  # Remove "CROSS_SPACE:"
                    if len(parts) >= 4:
                        title, space, visible, minimized = parts[0], parts[1], parts[2], parts[3]
                        cross_windows.append({
                            'title': title,
                            'space': space,
                            'visible': visible == 'true',
                            'minimized': minimized == 'true',
                            'type': 'cross_space'
                        })
            
            all_windows = current_windows + cross_windows
            
            print(f"\n   ✅ Found {len(all_windows)} total windows:")
            print(f"      Current space: {len(current_windows)}")
            print(f"      Cross-space: {len(cross_windows)}")
            
            return all_windows
            
        else:
            print(f"   ❌ Hammerspoon failed: {result.stderr}")
            return []
            
    except Exception as e:
        print(f"   ❌ Hammerspoon error: {e}")
        return []

def find_matching_window(windows, project_name):
    """Find window that matches the project name."""
    print(f"\n🔍 Window Matching (Project: {project_name}):")
    print("-" * 45)
    
    if not windows:
        print("   ❌ No windows to search")
        return None
    
    if not project_name or project_name == "unknown":
        print("   ❌ No project name to match against")
        return None
    
    project_lower = project_name.lower()
    matches = []
    
    print(f"   Searching {len(windows)} windows for '{project_name}':")
    
    for window in windows:
        title = window.get('title', '')
        title_lower = title.lower()
        
        print(f"     '{title}' ({window.get('type', 'unknown')}, Space {window.get('space', '?')})")
        
        if project_lower in title_lower:
            matches.append(window)
            print(f"       ✅ MATCH!")
    
    if matches:
        # Prefer visible, non-minimized windows
        best_match = None
        for match in matches:
            if match.get('visible', False) and not match.get('minimized', False):
                best_match = match
                break
        
        if not best_match:
            best_match = matches[0]  # Fallback to first match
        
        print(f"\n   ✅ Best match: '{best_match['title']}'")
        print(f"      Space: {best_match.get('space', 'Unknown')}")
        print(f"      Type: {best_match.get('type', 'unknown')}")
        print(f"      Visible: {best_match.get('visible', False)}")
        print(f"      Minimized: {best_match.get('minimized', False)}")
        
        return best_match
    else:
        print(f"   ❌ No matches found for '{project_name}'")
        return None

def test_universal_window_detection():
    """Test complete universal window detection using proven approach."""
    print("🎯 Test 50: Universal Window Detection")
    print("=" * 45)
    print("Using: Process Tree + Hammerspoon GitHub #3276 + Project Matching")
    
    # Step 1: Process tree analysis
    process_info = get_originating_app_from_process_tree()
    if not process_info:
        return None
    
    # Step 2: Map to Hammerspoon app name
    app_name = map_process_to_hammerspoon_app(process_info)
    print(f"\n✅ Mapped to Hammerspoon app: '{app_name}'")
    
    # Step 3: Get project name
    project_name = Path(os.getcwd()).name
    print(f"✅ Project name: '{project_name}'")
    
    # Step 4: Query Hammerspoon with proven workaround
    windows = query_hammerspoon_cross_space_windows(app_name)
    if not windows:
        return None
    
    # Step 5: Find matching window
    matching_window = find_matching_window(windows, project_name)
    if not matching_window:
        return None
    
    return {
        'app_name': app_name,
        'window_title': matching_window['title'],
        'window_space': matching_window.get('space'),
        'project_name': project_name,
        'process_info': process_info,
        'window_type': matching_window.get('type'),
        'all_windows_found': len(windows)
    }

def main():
    """Run test 50."""
    result = test_universal_window_detection()
    
    print(f"\n" + "=" * 60)
    print("TEST 50 RESULTS:")
    print("=" * 60)
    
    if result:
        print("✅ SUCCESS! Universal window detection working!")
        print(f"   Originating Window: '{result['window_title']}'")
        print(f"   App: {result['app_name']}")
        print(f"   Space: {result['window_space']}")
        print(f"   Project: {result['project_name']}")
        print(f"   Window Type: {result['window_type']}")
        print(f"   Total Windows Found: {result['all_windows_found']}")
        print(f"\n🎯 This gives us everything we need:")
        print(f"   - App name for Hammerspoon: '{result['app_name']}'")
        print(f"   - Window title for targeting: '{result['window_title']}'")
        print(f"   - Universal approach (no hardcoding)")
    else:
        print("❌ FAILED: Could not identify originating window")
    
    print(f"\n💡 Next: Test with different originating contexts and window switches")

if __name__ == "__main__":
    main()