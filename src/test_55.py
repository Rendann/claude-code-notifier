#!/usr/bin/env python3
"""
test_55.py - Shell PID to Window Mapping via Hammerspoon Only

Test if we can map from shell PID to specific window using only Hammerspoon,
without any AppleScript. Goal: Universal approach that works for all apps.
"""

import subprocess
import os
import psutil
import logging
from pathlib import Path
from datetime import datetime

def setup_logging():
    """Setup verbose logging."""
    tmp_dir = Path("./tmp")
    tmp_dir.mkdir(exist_ok=True)
    log_file = tmp_dir / "test_55.log"
    
    logger = logging.getLogger("test_55")
    logger.setLevel(logging.DEBUG)
    
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info(f"=== Test 55 Started - {datetime.now().isoformat()} ===")
    return logger

def get_shell_pid_and_context(logger):
    """Get shell PID and related context."""
    logger.info("🐚 Getting Shell PID and Context")
    
    # Get shell PID
    shell_pid = os.getpid()  # This is Python process, we want parent shell
    try:
        current_process = psutil.Process(shell_pid)
        parent = current_process.parent()
        if parent and parent.name().lower() in ['zsh', 'bash', 'sh']:
            shell_pid = parent.pid
            logger.info(f"   Shell PID: {shell_pid} ({parent.name()})")
        else:
            logger.info(f"   Using current process PID: {shell_pid}")
    except:
        logger.info(f"   Using current process PID: {shell_pid}")
    
    # Get environment context
    context = {
        'shell_pid': shell_pid,
        'tty': os.environ.get('TTY', 'unknown'),
        'term_program': os.environ.get('TERM_PROGRAM', 'unknown'),
        'iterm_session_id': os.environ.get('ITERM_SESSION_ID', 'unknown'),
        'pwd': os.getcwd()
    }
    
    for key, value in context.items():
        logger.info(f"   {key}: {value}")
    
    # Try to get TTY via command
    try:
        tty_result = subprocess.run(["tty"], capture_output=True, text=True)
        if tty_result.returncode == 0:
            context['current_tty'] = tty_result.stdout.strip()
            logger.info(f"   current_tty: {context['current_tty']}")
    except:
        pass
    
    return context

def get_process_tree_to_gui_app(shell_pid, logger):
    """Get process tree from shell PID to GUI application with robust error handling."""
    logger.info(f"🔄 Process Tree Analysis from Shell PID {shell_pid}")
    
    # Method 1: Try psutil with robust error handling
    processes = []
    gui_app = None
    
    try:
        current = psutil.Process(shell_pid)
        level = 0
        max_levels = 15
        
        while current and level < max_levels:
            try:
                proc_info = {
                    'level': level,
                    'pid': current.pid,
                    'name': current.name(),
                    'cmdline': [],
                    'method': 'psutil'
                }
                
                # Safely get cmdline
                try:
                    proc_info['cmdline'] = current.cmdline()
                except (psutil.AccessDenied, psutil.NoSuchProcess, OSError):
                    proc_info['cmdline'] = []
                
                processes.append(proc_info)
                logger.debug(f"   Level {level}: {proc_info['name']} (PID: {proc_info['pid']})")
                
                # Try to get parent - with comprehensive error handling
                try:
                    parent = current.parent()
                    if parent is None:
                        logger.debug(f"   Reached root at level {level}")
                        break
                    current = parent
                    level += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, OSError) as e:
                    logger.debug(f"   Parent access failed at level {level}: {e}")
                    break
                
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, OSError) as e:
                logger.debug(f"   Process access failed at level {level}: {e}")
                break
        
        logger.info(f"   Collected {len(processes)} processes via psutil")
        
    except Exception as e:
        logger.warning(f"   psutil method failed: {e}")
        processes = []
    
    # Method 2: Fallback to ps command parsing if psutil failed or incomplete
    if len(processes) < 3:  # If we didn't get a good chain
        logger.info("   Using ps command fallback for process tree")
        ps_processes = get_process_tree_via_ps(shell_pid, logger)
        if ps_processes:
            processes.extend(ps_processes)
            logger.info(f"   Added {len(ps_processes)} processes via ps command")
    
    # Find GUI app in the collected processes
    gui_indicators = ['iterm', 'iterm2', 'terminal', 'code', 'electron', 'cursor', 'intellij', 'pycharm', 'webstorm']
    
    for proc in reversed(processes):  # Check from top down (parent to child)
        name_lower = proc['name'].lower()
        for indicator in gui_indicators:
            if indicator in name_lower:
                gui_app = proc
                logger.info(f"   Found GUI app: {proc['name']} (PID: {proc['pid']}) via {proc.get('method', 'unknown')}")
                break
        if gui_app:
            break
    
    if not gui_app:
        # Method 3: Try direct app discovery
        gui_app = find_gui_app_direct(logger)
    
    return processes, gui_app

def get_process_tree_via_ps(shell_pid, logger):
    """Fallback method using ps command to build process tree."""
    try:
        # Get full process info
        result = subprocess.run(
            ["ps", "-eo", "pid,ppid,comm"], 
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode != 0:
            return []
        
        # Parse ps output into dict
        pid_to_info = {}
        for line in result.stdout.strip().split('\n')[1:]:  # Skip header
            parts = line.strip().split()
            if len(parts) >= 3:
                pid = int(parts[0])
                ppid = int(parts[1])
                comm = parts[2]
                pid_to_info[pid] = {'ppid': ppid, 'name': comm, 'pid': pid}
        
        # Build chain from shell_pid upward
        processes = []
        current_pid = shell_pid
        level = 0
        
        while current_pid in pid_to_info and level < 10:
            proc_info = pid_to_info[current_pid]
            processes.append({
                'level': level,
                'pid': current_pid,
                'name': proc_info['name'],
                'cmdline': [],
                'method': 'ps_command'
            })
            
            logger.debug(f"   ps Level {level}: {proc_info['name']} (PID: {current_pid})")
            
            # Move to parent
            parent_pid = proc_info['ppid']
            if parent_pid == current_pid or parent_pid <= 1:
                break
            
            current_pid = parent_pid
            level += 1
        
        return processes
        
    except Exception as e:
        logger.debug(f"   ps command fallback failed: {e}")
        return []

def find_gui_app_direct(logger):
    """Direct method to find GUI applications using system tools."""
    logger.info("   Trying direct GUI app discovery")
    
    # Method: Find common GUI apps that might be running
    gui_apps = ['iTerm2', 'Terminal', 'Code', 'Cursor', 'IntelliJ IDEA', 'PyCharm']
    
    try:
        # Use pgrep to find running processes
        for app_name in gui_apps:
            try:
                result = subprocess.run(
                    ["pgrep", "-f", app_name], 
                    capture_output=True, text=True, timeout=5
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    pids = [int(pid) for pid in result.stdout.strip().split('\n') if pid.strip()]
                    if pids:
                        main_pid = pids[0]  # Take first PID
                        logger.info(f"   Found {app_name} via pgrep: PID {main_pid}")
                        
                        return {
                            'level': -1,  # Special marker for direct discovery
                            'pid': main_pid,
                            'name': app_name,
                            'cmdline': [],
                            'method': 'direct_pgrep'
                        }
            except Exception as e:
                logger.debug(f"   pgrep for {app_name} failed: {e}")
        
        logger.warning("   No GUI apps found via direct discovery")
        return None
        
    except Exception as e:
        logger.debug(f"   Direct discovery failed: {e}")
        return None

def query_hammerspoon_by_pid(pid, app_name, logger):
    """Query Hammerspoon for windows by PID."""
    logger.info(f"🔨 Hammerspoon PID Query: {app_name} (PID: {pid})")
    
    try:
        hs_cli = "/Applications/Hammerspoon.app/Contents/Frameworks/hs/hs"
        if not Path(hs_cli).exists():
            logger.error("Hammerspoon CLI not found")
            return []
        
        script = f'''
        local application = require("hs.application")
        local spaces = require("hs.spaces")
        
        print("Querying PID: {pid}")
        
        -- Get application by PID
        local app = application.applicationForPID({pid})
        if app then
            local appName = app:name()
            print("APP_FOUND:" .. appName)
            
            -- Get all windows for this app
            local windows = app:allWindows()
            print("WINDOW_COUNT:" .. #windows)
            
            for i, win in pairs(windows) do
                local title = win:title() or "NO_TITLE"
                local winSpaces = spaces.windowSpaces(win:id())
                local spaceInfo = winSpaces and winSpaces[1] or "UNKNOWN"
                local isVisible = win:isVisible()
                local isMinimized = win:isMinimized()
                
                print("WINDOW:" .. title .. "|SPACE:" .. spaceInfo .. "|VIS:" .. tostring(isVisible) .. "|MIN:" .. tostring(isMinimized))
            end
            
        else
            print("NO_APP_FOR_PID:" .. {pid})
        end
        '''
        
        result = subprocess.run(
            [hs_cli, "-c", script],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            windows = []
            
            for line in lines:
                logger.info(f"   {line}")
                
                if line.startswith("WINDOW:"):
                    # Parse: WINDOW:title|SPACE:space|VIS:visible|MIN:minimized
                    parts = line.split("|")
                    if len(parts) >= 4:
                        title = parts[0].replace("WINDOW:", "")
                        space = parts[1].replace("SPACE:", "")
                        visible = parts[2].replace("VIS:", "")
                        minimized = parts[3].replace("MIN:", "")
                        
                        windows.append({
                            'title': title,
                            'space': space,
                            'visible': visible == 'true',
                            'minimized': minimized == 'true'
                        })
            
            return windows
            
        else:
            logger.error(f"Hammerspoon query failed: {result.stderr}")
            return []
            
    except Exception as e:
        logger.error(f"Hammerspoon query error: {e}")
        return []

def correlate_shell_to_window(shell_context, windows, logger):
    """Correlate shell context to specific window using multiple strategies."""
    logger.info("🎯 Shell Context → Window Correlation (Hammerspoon Only)")
    
    shell_pid = shell_context['shell_pid']
    tty = shell_context.get('current_tty', 'unknown')
    session_id = shell_context.get('iterm_session_id', 'unknown')
    term_program = shell_context.get('term_program', 'unknown')
    
    logger.info(f"   Shell PID: {shell_pid}")
    logger.info(f"   TTY: {tty}")
    logger.info(f"   Session ID: {session_id}")
    logger.info(f"   Term Program: {term_program}")
    logger.info(f"   Available windows: {len(windows)}")
    
    # List all available windows for debugging
    for i, window in enumerate(windows):
        logger.debug(f"      {i}: {window['title']} (Space: {window['space']}, Visible: {window['visible']})")
    
    # Strategy 1: Session ID parsing (iTerm2 specific)
    if session_id != 'unknown' and ':' in session_id and 'iterm' in term_program.lower():
        session_match = parse_iterm_session_id(session_id, windows, logger)
        if session_match:
            return session_match
    
    # Strategy 2: TTY-based correlation with enhanced matching
    if tty != 'unknown' and tty.startswith('/dev/ttys'):
        tty_match = correlate_by_tty(tty, shell_pid, windows, logger)
        if tty_match:
            return tty_match
    
    # Strategy 3: Process-specific correlation
    proc_match = correlate_by_process_context(shell_context, windows, logger)
    if proc_match:
        return proc_match
    
    # Strategy 4: Smart heuristics based on window state
    heuristic_match = select_by_window_heuristics(windows, logger)
    if heuristic_match:
        return heuristic_match
    
    logger.warning("   No correlation found via any strategy")
    return None

def parse_iterm_session_id(session_id, windows, logger):
    """Parse iTerm2 session ID to find target window."""
    logger.info("   Strategy 1: iTerm2 Session ID Parsing")
    
    try:
        # Session ID format: w3t0p0:C90DBB62-28DA-4BAB-9A5E-9093071FF06C
        # w3t0p0 = Window 3, Tab 0, Pane 0
        session_prefix = session_id.split(':')[0]
        logger.info(f"   Session prefix: {session_prefix}")
        
        if session_prefix.startswith('w') and 't' in session_prefix and 'p' in session_prefix:
            # Parse w3t0p0 format
            parts = session_prefix[1:]  # Remove 'w'
            t_index = parts.find('t')
            p_index = parts.find('p')
            
            if t_index > 0 and p_index > t_index:
                window_num = int(parts[:t_index])
                tab_num = int(parts[t_index+1:p_index])
                pane_num = int(parts[p_index+1:])
                
                logger.info(f"   Parsed: Window {window_num}, Tab {tab_num}, Pane {pane_num}")
                
                # iTerm2 uses 0-based indexing, but session shows 1-based
                # Try both interpretations
                for window_index in [window_num, window_num - 1]:
                    if 0 <= window_index < len(windows):
                        target_window = windows[window_index]
                        logger.info(f"   Session parsing match: Index {window_index} → {target_window['title']}")
                        return target_window
                
        else:
            logger.debug(f"   Unrecognized session format: {session_prefix}")
            
    except (ValueError, IndexError) as e:
        logger.debug(f"   Session parsing error: {e}")
    
    return None

def correlate_by_tty(tty, shell_pid, windows, logger):
    """Correlate using TTY information and system process data."""
    logger.info("   Strategy 2: TTY-based Correlation")
    
    try:
        # Extract TTY suffix: /dev/ttys068 → 068
        tty_suffix = tty.replace('/dev/ttys', '')
        logger.info(f"   TTY suffix: {tty_suffix}")
        
        # Check ps output to see if we can correlate shell PID to TTY
        result = subprocess.run(
            ["ps", "-o", "pid,tty,command", "-p", str(shell_pid)],
            capture_output=True, text=True, timeout=5
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                ps_line = lines[1]
                logger.debug(f"   ps output for shell: {ps_line}")
                
                # If TTY shows in ps output, we have confirmation
                if tty_suffix in ps_line:
                    logger.info(f"   TTY correlation confirmed via ps")
                    
                    # For now, return first visible window as we can't directly map TTY to window
                    # Future enhancement: could use lsof or other tools for precise mapping
                    visible_windows = [w for w in windows if w['visible'] and not w['minimized']]
                    if visible_windows:
                        logger.info(f"   TTY heuristic: selecting first visible window")
                        return visible_windows[0]
    
    except Exception as e:
        logger.debug(f"   TTY correlation error: {e}")
    
    return None

def correlate_by_process_context(shell_context, windows, logger):
    """Correlate using broader process context."""
    logger.info("   Strategy 3: Process Context Correlation")
    
    # For VS Code: look for project-related window
    if shell_context.get('term_program') == 'vscode':
        project_name = Path(shell_context['pwd']).name
        logger.info(f"   VS Code context: looking for project '{project_name}'")
        
        for window in windows:
            if project_name.lower() in window['title'].lower():
                logger.info(f"   Project name match: {window['title']}")
                return window
    
    # For other contexts: could add similar logic
    logger.debug("   No process context correlation found")
    return None

def select_by_window_heuristics(windows, logger):
    """Select window using smart heuristics."""
    logger.info("   Strategy 4: Window Heuristics")
    
    # Heuristic 1: Single visible, non-minimized window
    active_windows = [w for w in windows if w['visible'] and not w['minimized']]
    if len(active_windows) == 1:
        logger.info(f"   Single active window: {active_windows[0]['title']}")
        return active_windows[0]
    
    # Heuristic 2: First visible window (most recently active)
    if active_windows:
        logger.info(f"   First active window heuristic: {active_windows[0]['title']}")
        return active_windows[0]
    
    # Heuristic 3: Any non-minimized window
    non_minimized = [w for w in windows if not w['minimized']]
    if non_minimized:
        logger.info(f"   First non-minimized window: {non_minimized[0]['title']}")
        return non_minimized[0]
    
    # Heuristic 4: First window as last resort
    if windows:
        logger.info(f"   Fallback to first window: {windows[0]['title']}")
        return windows[0]
    
    logger.warning("   No windows available for heuristic selection")
    return None

def test_hammerspoon_focus(target_window, app_name, logger):
    """Test focusing the target window via Hammerspoon."""
    logger.info(f"🎯 Testing Hammerspoon Focus: {target_window['title']}")
    
    try:
        hs_cli = "/Applications/Hammerspoon.app/Contents/Frameworks/hs/hs"
        
        script = f'''
        local windowfilter = require("hs.window.filter")
        local application = require("hs.application")
        
        print("Attempting to focus: {target_window['title']}")
        
        -- Use windowfilter with cross-space capability (GitHub #3276 workaround)
        local wf = windowfilter.new('{app_name}')
        wf:setCurrentSpace(false)  -- This is the key for cross-space detection
        local windows = wf:getWindows()
        
        print("Cross-space windows found: " .. #windows)
        
        for _, win in pairs(windows) do
            local title = win:title() or "NO_TITLE"
            print("Found window: " .. title)
            
            if title == "{target_window['title']}" then
                print("MATCH - Focusing window: " .. title)
                win:focus()
                return "SUCCESS_FOCUSED:" .. title
            end
        end
        
        return "NOT_FOUND:{target_window['title']}"
        '''
        
        result = subprocess.run(
            [hs_cli, "-c", script],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    logger.info(f"   {line}")
        else:
            logger.error(f"Hammerspoon focus failed: {result.stderr}")
            
    except Exception as e:
        logger.error(f"Focus test error: {e}")

def main():
    """Run test 55 - Shell PID to window via Hammerspoon only."""
    logger = setup_logging()
    
    logger.info("🎯 Test 55: Shell PID → Window via Hammerspoon Only")
    logger.info("=" * 54)
    logger.info("Goal: Map shell PID to specific window using only Hammerspoon")
    
    # Step 1: Get shell PID and context
    shell_context = get_shell_pid_and_context(logger)
    
    # Step 2: Process tree to GUI app
    processes, gui_app = get_process_tree_to_gui_app(shell_context['shell_pid'], logger)
    
    if not gui_app:
        logger.error("❌ No GUI application found in process tree")
        return
    
    # Step 3: Query Hammerspoon for windows by GUI app PID
    windows = query_hammerspoon_by_pid(gui_app['pid'], gui_app['name'], logger)
    
    if not windows:
        logger.error("❌ No windows found via Hammerspoon")
        return
    
    # Step 4: Correlate shell context to specific window
    target_window = correlate_shell_to_window(shell_context, windows, logger)
    
    if not target_window:
        logger.warning("⚠️ Could not correlate shell to specific window")
        logger.info("Available windows:")
        for i, window in enumerate(windows):
            logger.info(f"   {i}: {window['title']}")
        return
    
    # Step 5: Test focusing via Hammerspoon
    test_hammerspoon_focus(target_window, gui_app['name'], logger)
    
    logger.info("=" * 60)
    logger.info("TEST 55 RESULTS:")
    logger.info("=" * 60)
    
    if target_window:
        logger.info("✅ Shell PID → Window correlation successful!")
        logger.info(f"   Shell PID: {shell_context['shell_pid']}")
        logger.info(f"   GUI App: {gui_app['name']} (PID: {gui_app['pid']})")
        logger.info(f"   Target Window: {target_window['title']}")
        logger.info("🎯 Hammerspoon-only approach working!")
    else:
        logger.info("❌ Shell PID → Window correlation failed")
        logger.info("May need additional correlation strategies")
    
    print(f"\n📄 Detailed logs saved to: ./tmp/test_55.log")

if __name__ == "__main__":
    main()