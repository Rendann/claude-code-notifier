#!/usr/bin/env python3
"""
test_54.py - Fixed iTerm2 AppleScript Integration

Using proper iTerm2 AppleScript syntax based on documentation:
https://iterm2.com/documentation-scripting.html
"""

import subprocess
import os
import logging
from pathlib import Path
from datetime import datetime

def setup_logging():
    """Setup verbose logging."""
    tmp_dir = Path("./tmp")
    tmp_dir.mkdir(exist_ok=True)
    log_file = tmp_dir / "test_54.log"
    
    logger = logging.getLogger("test_54")
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
    
    logger.info(f"=== Test 54 Started - {datetime.now().isoformat()} ===")
    return logger

def test_iterm_basic_structure(logger):
    """Test basic iTerm2 structure access."""
    logger.info("🏗️ Testing Basic iTerm2 Structure")
    
    script = '''
    tell application "iTerm"
        set windowCount to count of windows
        set output to "WINDOWS:" & windowCount
        
        repeat with i from 1 to windowCount
            set tabCount to count of tabs of window i
            set output to output & "\\nWIN" & i & "_TABS:" & tabCount
        end repeat
        
        return output
    end tell
    '''
    
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            for line in result.stdout.strip().split('\\n'):
                logger.info(f"   {line}")
            return True
        else:
            logger.error(f"Basic structure test failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Basic structure test error: {e}")
        return False

def test_iterm_session_properties(logger):
    """Test accessing iTerm2 session properties correctly."""
    logger.info("📋 Testing iTerm2 Session Properties")
    
    script = '''
    tell application "iTerm"
        set output to "SESSION_ENUMERATION:"
        
        repeat with w from 1 to count of windows
            repeat with t from 1 to count of tabs of window w
                repeat with s from 1 to count of sessions of tab t of window w
                    try
                        set sess to session s of tab t of window w
                        
                        -- Get basic session info
                        set sessId to unique id of sess
                        set sessTTY to tty of sess
                        
                        -- Get window and tab names differently
                        set windowName to name of window w
                        
                        set output to output & "\\nSESSION:" & sessId & "|TTY:" & sessTTY & "|WIN:" & windowName & "|W" & w & "T" & t & "S" & s
                        
                    on error errMsg
                        set output to output & "\\nERROR_W" & w & "T" & t & "S" & s & ":" & errMsg
                    end try
                end repeat
            end repeat
        end repeat
        
        return output
    end tell
    '''
    
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=15
        )
        
        if result.returncode == 0:
            for line in result.stdout.strip().split('\\n'):
                logger.info(f"   {line}")
            return result.stdout.strip().split('\\n')
        else:
            logger.error(f"Session properties test failed: {result.stderr}")
            return []
            
    except Exception as e:
        logger.error(f"Session properties test error: {e}")
        return []

def test_iterm_current_session(logger):
    """Test getting current session information."""
    logger.info("📍 Testing Current iTerm2 Session")
    
    script = '''
    tell application "iTerm"
        try
            set currentSession to current session of current window
            set currentId to unique id of currentSession
            set currentTTY to tty of currentSession
            set currentWindowName to name of current window
            
            return "CURRENT:" & currentId & "|TTY:" & currentTTY & "|WIN:" & currentWindowName
            
        on error errMsg
            return "CURRENT_ERROR:" & errMsg
        end try
    end tell
    '''
    
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            logger.info(f"   {output}")
            return output
        else:
            logger.error(f"Current session test failed: {result.stderr}")
            return None
            
    except Exception as e:
        logger.error(f"Current session test error: {e}")
        return None

def test_iterm_session_matching(logger):
    """Test matching session by TTY or other identifiers."""
    logger.info("🎯 Testing iTerm2 Session Matching")
    
    # Get our current TTY
    try:
        tty_result = subprocess.run(["tty"], capture_output=True, text=True)
        current_tty = tty_result.stdout.strip() if tty_result.returncode == 0 else "unknown"
        logger.info(f"Looking for TTY: {current_tty}")
    except:
        current_tty = "unknown"
    
    # Get our session ID
    current_session_id = os.environ.get('ITERM_SESSION_ID', 'unknown')
    logger.info(f"Looking for session ID: {current_session_id}")
    
    script = f'''
    tell application "iTerm"
        set targetTTY to "{current_tty}"
        set targetSessionId to "{current_session_id}"
        set output to "SEARCHING_FOR:" & targetTTY & "|" & targetSessionId
        
        repeat with w from 1 to count of windows
            repeat with t from 1 to count of tabs of window w
                repeat with s from 1 to count of sessions of tab t of window w
                    try
                        set sess to session s of tab t of window w
                        set sessId to unique id of sess
                        set sessTTY to tty of sess
                        set windowName to name of window w
                        
                        -- Check for matches
                        if sessTTY = targetTTY then
                            set output to output & "\\nTTY_MATCH:" & sessId & "|TTY:" & sessTTY & "|WIN:" & windowName
                        end if
                        
                        if sessId contains targetSessionId or targetSessionId contains sessId then
                            set output to output & "\\nID_MATCH:" & sessId & "|TTY:" & sessTTY & "|WIN:" & windowName
                        end if
                        
                    on error errMsg
                        -- Skip errors for now
                    end try
                end repeat
            end repeat
        end repeat
        
        return output
    end tell
    '''
    
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=15
        )
        
        if result.returncode == 0:
            for line in result.stdout.strip().split('\\n'):
                logger.info(f"   {line}")
            return result.stdout.strip().split('\\n')
        else:
            logger.error(f"Session matching test failed: {result.stderr}")
            return []
            
    except Exception as e:
        logger.error(f"Session matching test error: {e}")
        return []

def test_window_focusing(matches, logger):
    """Test focusing iTerm2 window based on session match."""
    logger.info("🎯 Testing Window Focusing")
    
    if not matches:
        logger.warning("No matches to test focusing")
        return
    
    # Find a match line
    target_window = None
    for line in matches:
        if line.startswith(("TTY_MATCH:", "ID_MATCH:")):
            # Parse: TYPE_MATCH:sessId|TTY:tty|WIN:windowName
            parts = line.split("|")
            if len(parts) >= 3:
                window_part = parts[2]
                if window_part.startswith("WIN:"):
                    target_window = window_part.replace("WIN:", "")
                    break
    
    if not target_window:
        logger.warning("No target window found in matches")
        return
    
    logger.info(f"Attempting to focus window: '{target_window}'")
    
    script = f'''
    tell application "iTerm"
        try
            repeat with w from 1 to count of windows
                if name of window w = "{target_window}" then
                    set index of window w to 1
                    activate
                    return "FOCUSED:" & name of window w
                end if
            end repeat
            return "NOT_FOUND:{target_window}"
        on error errMsg
            return "FOCUS_ERROR:" & errMsg
        end try
    end tell
    '''
    
    try:
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, timeout=10
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            logger.info(f"   Focus result: {output}")
            return output
        else:
            logger.error(f"Focus test failed: {result.stderr}")
            return None
            
    except Exception as e:
        logger.error(f"Focus test error: {e}")
        return None

def main():
    """Run test 54 - Fixed iTerm2 AppleScript integration."""
    logger = setup_logging()
    
    logger.info("🎯 Test 54: Fixed iTerm2 AppleScript Integration")
    logger.info("=" * 52)
    
    # Step 1: Test basic structure access
    if not test_iterm_basic_structure(logger):
        logger.error("Basic structure test failed - aborting")
        return
    
    # Step 2: Test session properties access
    session_data = test_iterm_session_properties(logger)
    
    # Step 3: Test current session detection
    current_session = test_iterm_current_session(logger)
    
    # Step 4: Test session matching
    matches = test_iterm_session_matching(logger)
    
    # Step 5: Test window focusing
    if matches:
        test_window_focusing(matches, logger)
    
    logger.info("=" * 60)
    logger.info("TEST 54 RESULTS:")
    logger.info("=" * 60)
    
    if matches and any(line.startswith(("TTY_MATCH:", "ID_MATCH:")) for line in matches):
        logger.info("✅ SUCCESS: iTerm2 AppleScript session matching working!")
        logger.info("🎯 We can now map sessions to windows via AppleScript!")
    else:
        logger.info("⚠️ Partial success - basic AppleScript working, but no session matches")
        logger.info("Check ./tmp/test_54.log for detailed analysis")
    
    print(f"\n📄 Detailed logs saved to: ./tmp/test_54.log")

if __name__ == "__main__":
    main()