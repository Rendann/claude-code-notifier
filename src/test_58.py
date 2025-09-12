#!/usr/bin/env python3
"""
test_58.py - Pseudo-TTY to Parent TTY Discovery

Test methods for a pseudo-TTY process to find its parent real TTY.
This is key for Claude Code hooks to find the originating terminal session.
"""

import os
import sys
import subprocess
import psutil
import logging
from pathlib import Path
from datetime import datetime

def setup_logging():
    """Setup logging."""
    tmp_dir = Path("./tmp")
    tmp_dir.mkdir(exist_ok=True)
    log_file = tmp_dir / "test_58.log"
    
    logger = logging.getLogger("test_58")
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
    
    logger.info(f"=== Test 58 Started - {datetime.now().isoformat()} ===")
    return logger

def detect_current_tty_status(logger):
    """Detect current TTY status and context."""
    logger.info("🔍 Current TTY Status Detection")
    
    current_pid = os.getpid()
    logger.info(f"   Current PID: {current_pid}")
    
    # Test TTY detection
    tty_status = {}
    
    # Method 1: os.ttyname()
    for fd_name, fd in [("stdin", 0), ("stdout", 1), ("stderr", 2)]:
        try:
            tty_device = os.ttyname(fd)
            tty_status[f'tty_{fd_name}'] = tty_device
            logger.info(f"   os.ttyname({fd}) [{fd_name}]: {tty_device}")
        except OSError as e:
            tty_status[f'tty_{fd_name}'] = f"FAIL: {e}"
            logger.info(f"   os.ttyname({fd}) [{fd_name}]: FAIL - {e}")
    
    # Method 2: Check if stdin/stdout are TTYs
    for fd_name, fd in [("stdin", 0), ("stdout", 1), ("stderr", 2)]:
        is_tty = os.isatty(fd)
        tty_status[f'isatty_{fd_name}'] = is_tty
        logger.info(f"   os.isatty({fd}) [{fd_name}]: {is_tty}")
    
    # Method 3: Process info
    try:
        result = subprocess.run(
            ["ps", "-o", "pid,tty,ppid,command", "-p", str(current_pid)],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                ps_line = lines[1].strip()
                parts = ps_line.split(None, 3)
                if len(parts) >= 4:
                    pid, tty, ppid, command = parts[0], parts[1], parts[2], parts[3]
                    tty_status['ps_info'] = {
                        'pid': pid, 'tty': tty, 'ppid': ppid, 'command': command
                    }
                    logger.info(f"   Process info: PID={pid}, TTY={tty}, PPID={ppid}")
                    logger.debug(f"   Command: {command}")
    except Exception as e:
        logger.debug(f"   Process info failed: {e}")
    
    return tty_status

def find_parent_tty_via_process_tree(logger):
    """Find parent real TTY by walking up the process tree."""
    logger.info("🌳 Parent TTY via Process Tree")
    
    try:
        current_pid = os.getpid()
        current_process = psutil.Process(current_pid)
        
        level = 0
        parent = current_process.parent()
        
        while parent and level < 15:
            try:
                logger.debug(f"   Level {level}: {parent.name()} (PID: {parent.pid})")
                
                # Check if this parent has a real TTY
                try:
                    result = subprocess.run(
                        ["ps", "-o", "pid,tty", "-p", str(parent.pid)],
                        capture_output=True, text=True, timeout=3
                    )
                    
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        if len(lines) > 1:
                            parts = lines[1].strip().split()
                            if len(parts) >= 2:
                                pid_str, tty = parts[0], parts[1]
                                
                                # Check if this is a real TTY (not ??)
                                if tty != '??' and tty.startswith('ttys'):
                                    real_tty = f"/dev/{tty}"
                                    logger.info(f"   Found parent with real TTY: {parent.name()} (PID: {parent.pid}) → {real_tty}")
                                    return {
                                        'process': parent,
                                        'tty': real_tty,
                                        'level': level
                                    }
                                else:
                                    logger.debug(f"     Parent TTY: {tty} (not real)")
                
                except Exception as e:
                    logger.debug(f"     TTY check failed for PID {parent.pid}: {e}")
                
                parent = parent.parent()
                level += 1
                
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                logger.debug(f"   Parent access failed at level {level}: {e}")
                break
        
        logger.info("   No parent with real TTY found")
        return None
        
    except Exception as e:
        logger.error(f"Process tree traversal failed: {e}")
        return None

def find_parent_tty_via_session_leader(logger):
    """Find parent TTY via session leader process."""
    logger.info("👑 Parent TTY via Session Leader")
    
    try:
        current_pid = os.getpid()
        
        # Get session ID
        try:
            result = subprocess.run(
                ["ps", "-o", "pid,sid,tty", "-p", str(current_pid)],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].strip().split()
                    if len(parts) >= 3:
                        pid, sid, tty = parts[0], parts[1], parts[2]
                        logger.info(f"   Current process: PID={pid}, SID={sid}, TTY={tty}")
                        
                        # Find session leader
                        if sid != pid:  # We're not the session leader
                            result2 = subprocess.run(
                                ["ps", "-o", "pid,tty,command", "-p", sid],
                                capture_output=True, text=True, timeout=5
                            )
                            
                            if result2.returncode == 0:
                                lines2 = result2.stdout.strip().split('\n')
                                if len(lines2) > 1:
                                    parts2 = lines2[1].strip().split(None, 2)
                                    if len(parts2) >= 3:
                                        leader_pid, leader_tty, leader_cmd = parts2[0], parts2[1], parts2[2]
                                        
                                        if leader_tty != '??' and leader_tty.startswith('ttys'):
                                            real_tty = f"/dev/{leader_tty}"
                                            logger.info(f"   Session leader: PID={leader_pid}, TTY={real_tty}")
                                            logger.info(f"   Leader command: {leader_cmd}")
                                            return {
                                                'leader_pid': int(leader_pid),
                                                'tty': real_tty,
                                                'command': leader_cmd
                                            }
                                        else:
                                            logger.info(f"   Session leader TTY: {leader_tty} (not real)")
                        else:
                            logger.info("   Current process is session leader")
        
        except Exception as e:
            logger.debug(f"Session leader detection failed: {e}")
        
        return None
        
    except Exception as e:
        logger.error(f"Session leader method failed: {e}")
        return None

def find_parent_tty_via_environment(logger):
    """Find parent TTY via environment variables and context."""
    logger.info("🌍 Parent TTY via Environment")
    
    # Check SSH context
    ssh_tty = os.environ.get('SSH_TTY')
    if ssh_tty:
        logger.info(f"   SSH_TTY: {ssh_tty}")
        return {'tty': ssh_tty, 'method': 'ssh_env'}
    
    # Check GPG TTY (often set to real TTY)
    gpg_tty = os.environ.get('GPG_TTY')
    if gpg_tty:
        logger.info(f"   GPG_TTY: {gpg_tty}")
        return {'tty': gpg_tty, 'method': 'gpg_env'}
    
    # Check terminal session variables
    term_program = os.environ.get('TERM_PROGRAM')
    if term_program:
        logger.info(f"   TERM_PROGRAM: {term_program}")
        
        # For iTerm2, check session ID correlation
        if term_program == 'iTerm.app':
            session_id = os.environ.get('ITERM_SESSION_ID')
            if session_id:
                logger.info(f"   ITERM_SESSION_ID: {session_id}")
                # Could potentially parse session ID to infer TTY
                # w3t0p0:UUID might correlate to ttys068 pattern
    
    logger.info("   No TTY found via environment")
    return None

def find_parent_tty_via_lsof_analysis(logger):
    """Find parent TTY by analyzing open file descriptors."""
    logger.info("📁 Parent TTY via lsof Analysis")
    
    try:
        current_pid = os.getpid()
        
        # Get all open files for current process
        result = subprocess.run(
            ["lsof", "-p", str(current_pid)],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            logger.info("   Current process file descriptors:")
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            
            tty_fds = []
            for line in lines:
                if '/dev/tty' in line or 'CHR' in line:
                    parts = line.split()
                    if len(parts) >= 9:
                        fd = parts[3]
                        type_info = parts[4]
                        device = parts[8] if len(parts) > 8 else "unknown"
                        logger.debug(f"     FD: {fd}, Type: {type_info}, Device: {device}")
                        tty_fds.append((fd, type_info, device))
            
            if tty_fds:
                logger.info(f"   Found {len(tty_fds)} TTY-related file descriptors")
                # Analysis could reveal parent TTY patterns
            else:
                logger.info("   No TTY-related file descriptors found")
        else:
            logger.debug(f"   lsof failed: {result.stderr}")
    
    except Exception as e:
        logger.debug(f"   lsof analysis failed: {e}")
    
    return None

def test_parent_shell_correlation(logger):
    """Test correlation with parent shell PID and its TTY."""
    logger.info("🐚 Parent Shell TTY Correlation")
    
    try:
        # Get parent shell PID from environment or process tree
        ppid = os.getppid()
        logger.info(f"   Direct parent PID: {ppid}")
        
        # Check parent's TTY
        result = subprocess.run(
            ["ps", "-o", "pid,tty,command", "-p", str(ppid)],
            capture_output=True, text=True, timeout=5
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].strip().split(None, 2)
                if len(parts) >= 3:
                    pid, tty, command = parts[0], parts[1], parts[2]
                    logger.info(f"   Parent process: PID={pid}, TTY={tty}")
                    logger.info(f"   Parent command: {command}")
                    
                    if tty != '??' and tty.startswith('ttys'):
                        real_tty = f"/dev/{tty}"
                        logger.info(f"   Parent has real TTY: {real_tty}")
                        return {'parent_pid': int(pid), 'tty': real_tty, 'command': command}
                    else:
                        logger.info(f"   Parent TTY: {tty} (not real, continue up tree)")
                        
                        # Try grandparent
                        try:
                            parent_proc = psutil.Process(int(pid))
                            grandparent = parent_proc.parent()
                            if grandparent:
                                result2 = subprocess.run(
                                    ["ps", "-o", "pid,tty,command", "-p", str(grandparent.pid)],
                                    capture_output=True, text=True, timeout=5
                                )
                                
                                if result2.returncode == 0:
                                    lines2 = result2.stdout.strip().split('\n')
                                    if len(lines2) > 1:
                                        parts2 = lines2[1].strip().split(None, 2)
                                        if len(parts2) >= 3:
                                            gpid, gtty, gcmd = parts2[0], parts2[1], parts2[2]
                                            logger.info(f"   Grandparent: PID={gpid}, TTY={gtty}")
                                            
                                            if gtty != '??' and gtty.startswith('ttys'):
                                                real_tty = f"/dev/{gtty}"
                                                logger.info(f"   Grandparent has real TTY: {real_tty}")
                                                return {'grandparent_pid': int(gpid), 'tty': real_tty, 'command': gcmd}
                        except Exception as e:
                            logger.debug(f"   Grandparent check failed: {e}")
        
        return None
        
    except Exception as e:
        logger.debug(f"   Parent shell correlation failed: {e}")
        return None

def main():
    """Run test 58 - pseudo-TTY to parent TTY discovery."""
    logger = setup_logging()
    
    logger.info("🎯 Test 58: Pseudo-TTY to Parent TTY Discovery")
    logger.info("=" * 54)
    logger.info("Goal: Find parent real TTY from pseudo-TTY process context")
    
    # Step 1: Detect current TTY status
    tty_status = detect_current_tty_status(logger)
    
    # Step 2: Try different methods to find parent TTY
    methods_results = {}
    
    # Method 1: Process tree traversal
    parent_tty_tree = find_parent_tty_via_process_tree(logger)
    methods_results['process_tree'] = parent_tty_tree
    
    # Method 2: Session leader
    parent_tty_session = find_parent_tty_via_session_leader(logger)
    methods_results['session_leader'] = parent_tty_session
    
    # Method 3: Environment variables
    parent_tty_env = find_parent_tty_via_environment(logger)
    methods_results['environment'] = parent_tty_env
    
    # Method 4: lsof analysis
    parent_tty_lsof = find_parent_tty_via_lsof_analysis(logger)
    methods_results['lsof_analysis'] = parent_tty_lsof
    
    # Method 5: Parent shell correlation
    parent_shell_tty = test_parent_shell_correlation(logger)
    methods_results['parent_shell'] = parent_shell_tty
    
    logger.info("=" * 60)
    logger.info("TEST 58 RESULTS:")
    logger.info("=" * 60)
    
    # Analyze results
    successful_methods = [name for name, result in methods_results.items() if result is not None]
    
    if successful_methods:
        logger.info("✅ SUCCESS: Found methods to map pseudo-TTY to parent TTY!")
        logger.info(f"   Successful methods: {', '.join(successful_methods)}")
        
        for method_name in successful_methods:
            result = methods_results[method_name]
            if isinstance(result, dict) and 'tty' in result:
                logger.info(f"   {method_name}: {result['tty']}")
        
        logger.info("🎯 This enables universal TTY-based window detection!")
        logger.info("   Claude Code hooks can find originating terminal session")
        
    else:
        logger.info("⚠️ No parent TTY found via any method")
        logger.info("   Process tree or environment-based detection needed")
    
    print(f"\n📄 Detailed logs saved to: ./tmp/test_58.log")

if __name__ == "__main__":
    main()