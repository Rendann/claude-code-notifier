#!/usr/bin/env python3
"""
Hammerspoon Cross-Space Window Focuser

Implements the GitHub issue #3276 workaround for cross-space window focusing.
Uses the breakthrough solution: windowfilter with setCurrentSpace(false).
"""

import logging
import subprocess
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class HammerspoonFocuser:
    """Cross-space window focusing using Hammerspoon."""

    def __init__(self):
        """Initialize the Hammerspoon focuser."""
        self.hs_cli_path = self._find_hammerspoon_cli()

    def _find_hammerspoon_cli(self) -> Optional[str]:
        """Find Hammerspoon CLI executable."""
        possible_paths = [
            "/Applications/Hammerspoon.app/Contents/Frameworks/hs/hs",
            "/usr/local/bin/hs",
            "/opt/homebrew/bin/hs",
        ]

        for path in possible_paths:
            if Path(path).exists():
                logger.info(f"Found Hammerspoon CLI at: {path}")
                return path

        logger.warning("Hammerspoon CLI not found")
        return None

    def is_available(self) -> bool:
        """Check if Hammerspoon is available."""
        if not self.hs_cli_path:
            return False

        try:
            result = subprocess.run(
                [self.hs_cli_path, "-c", "print('test')"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            return result.returncode == 0
        except Exception as e:
            logger.debug(f"Hammerspoon availability check failed: {e}")
            return False

    def focus_app_window(
        self, app_name: str, window_title: Optional[str] = None
    ) -> bool:
        """
        Focus a window of the specified app, potentially across spaces.

        Args:
            app_name: Name of the application (e.g., "Code", "Terminal")
            window_title: Optional specific window title to target

        Returns:
            True if focus attempt was made, False if failed
        """
        if not self.is_available():
            logger.error("Hammerspoon not available")
            return False

        # Create the Lua script using the GitHub #3276 workaround
        window_search_logic = ""
        if window_title:
            window_search_logic = f'''
            -- Look for specific window title
            for _, win in pairs(otherWindows) do
                local title = win:title() or ""
                if string.find(string.lower(title), string.lower("{window_title}")) then
                    targetWindow = win
                    break
                end
            end
            targetWindow = targetWindow or otherWindows[1]  -- Fallback to first window
            '''
        else:
            window_search_logic = """
            -- Use first available window
            targetWindow = otherWindows[1]
            """

        script = f"""
        local windowfilter = require("hs.window.filter")
        local spaces = require("hs.spaces")

        -- Get current space for comparison
        local currentSpace = spaces.focusedSpace()

        -- Use the GitHub #3276 workaround for cross-space detection
        local wf_other = windowfilter.new('{app_name}')
        wf_other:setCurrentSpace(false)  -- This is the key workaround!

        -- Get windows from other spaces (includes "last focused" from each space)
        local otherWindows = wf_other:getWindows()

        if #otherWindows > 0 then
            local targetWindow = nil
            {window_search_logic}

            if targetWindow then
                -- This is the breakthrough: direct window focus switches spaces cleanly!
                local success = targetWindow:focus()

                if success then
                    print("SUCCESS:Focused cross-space window")
                    return true
                else
                    print("ERROR:Focus command failed")
                    return false
                end
            else
                print("ERROR:No matching window found")
                return false
            end
        else
            print("ERROR:No cross-space windows found")
            return false
        end
        """

        try:
            logger.info(
                f"Attempting to focus {app_name} window{f' with title containing: {window_title}' if window_title else ''}"
            )

            result = subprocess.run(
                [self.hs_cli_path, "-c", script],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                output = result.stdout.strip()
                if "SUCCESS:" in output:
                    logger.info("Successfully focused cross-space window")
                    return True
                logger.warning(f"Focus attempt had issues: {output}")
                return False
            logger.error(f"Hammerspoon script failed: {result.stderr}")
            return False

        except subprocess.TimeoutExpired:
            logger.error("Hammerspoon focus attempt timed out")
            return False
        except Exception as e:
            logger.error(f"Failed to execute Hammerspoon focus: {e}")
            return False

    def get_app_windows_info(self, app_name: str) -> dict[str, Any]:
        """
        Get information about app windows across all spaces.

        Args:
            app_name: Name of the application

        Returns:
            Dict with current and cross-space window information
        """
        if not self.is_available():
            return {"error": "Hammerspoon not available"}

        script = f"""
        local windowfilter = require("hs.window.filter")
        local spaces = require("hs.spaces")

        local currentSpace = spaces.focusedSpace()

        -- Current space windows
        local wf_current = windowfilter.new('{app_name}')
        wf_current:setCurrentSpace(true)
        local currentWindows = wf_current:getWindows()

        -- Cross-space windows (GitHub #3276 workaround)
        local wf_other = windowfilter.new('{app_name}')
        wf_other:setCurrentSpace(false)
        local otherWindows = wf_other:getWindows()

        print("CURRENT_SPACE:" .. currentSpace)
        print("CURRENT_WINDOWS:" .. #currentWindows)
        print("CROSS_SPACE_WINDOWS:" .. #otherWindows)

        -- List current space windows
        for i, win in pairs(currentWindows) do
            local title = win:title() or "NO_TITLE"
            local winSpaces = spaces.windowSpaces(win:id())
            local spaceInfo = winSpaces and winSpaces[1] or "UNKNOWN"
            print("CURRENT:" .. i .. ":" .. title .. ":" .. spaceInfo)
        end

        -- List cross-space windows
        for i, win in pairs(otherWindows) do
            local title = win:title() or "NO_TITLE"
            local winSpaces = spaces.windowSpaces(win:id())
            local spaceInfo = winSpaces and winSpaces[1] or "UNKNOWN"
            print("CROSS_SPACE:" .. i .. ":" .. title .. ":" .. spaceInfo)
        end
        """

        try:
            result = subprocess.run(
                [self.hs_cli_path, "-c", script],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                return self._parse_windows_info(result.stdout)
            logger.error(f"Failed to get windows info: {result.stderr}")
            return {"error": "Script execution failed"}

        except Exception as e:
            logger.error(f"Failed to get windows info: {e}")
            return {"error": str(e)}

    def _parse_windows_info(self, output: str) -> dict[str, Any]:
        """Parse windows info output from Hammerspoon."""
        info = {
            "current_space": None,
            "current_windows": [],
            "cross_space_windows": [],
            "total_current": 0,
            "total_cross_space": 0,
        }

        for line in output.strip().split("\n"):
            if line.startswith("CURRENT_SPACE:"):
                info["current_space"] = line.split(":", 1)[1]
            elif line.startswith("CURRENT_WINDOWS:"):
                info["total_current"] = int(line.split(":", 1)[1])
            elif line.startswith("CROSS_SPACE_WINDOWS:"):
                info["total_cross_space"] = int(line.split(":", 1)[1])
            elif line.startswith("CURRENT:"):
                parts = line.split(":", 3)
                if len(parts) >= 4:
                    info["current_windows"].append(
                        {"index": int(parts[1]), "title": parts[2], "space": parts[3]}
                    )
            elif line.startswith("CROSS_SPACE:"):
                parts = line.split(":", 3)
                if len(parts) >= 4:
                    info["cross_space_windows"].append(
                        {"index": int(parts[1]), "title": parts[2], "space": parts[3]}
                    )

        return info


def main():
    """Test the Hammerspoon focuser."""
    logging.basicConfig(level=logging.INFO)

    focuser = HammerspoonFocuser()

    print("🔨 Hammerspoon Cross-Space Focuser Test")
    print("=" * 40)

    print(f"Hammerspoon available: {focuser.is_available()}")

    if focuser.is_available():
        # Test with Code windows
        print("\n📱 Getting Code windows info...")
        info = focuser.get_app_windows_info("Code")

        print(f"Current space: {info.get('current_space', 'Unknown')}")
        print(f"Current space windows: {info.get('total_current', 0)}")
        print(f"Cross-space windows: {info.get('total_cross_space', 0)}")

        if info.get("cross_space_windows"):
            print("\nCross-space windows found:")
            for win in info["cross_space_windows"]:
                print(f"  {win['index']}: '{win['title']}' (Space {win['space']})")

            print("\n🎯 Testing cross-space focus...")
            success = focuser.focus_app_window("Code")
            print(f"Focus result: {'✅ Success' if success else '❌ Failed'}")


if __name__ == "__main__":
    main()
