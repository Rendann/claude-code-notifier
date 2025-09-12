#!/usr/bin/env python3
"""
Universal App Detection Module

Detects the currently focused application at runtime without hardcoded patterns.
Provides app name, bundle ID, and window info for universal focusing.
"""

import contextlib
import logging
import subprocess
from typing import Any, Optional

logger = logging.getLogger(__name__)


class AppDetector:
    """Universal app detection without hardcoded patterns."""

    def __init__(self):
        """Initialize the app detector."""
        self._current_app_info: Optional[dict[str, Any]] = None

    def get_current_app_info(self) -> dict[str, Any]:
        """
        Get current focused app information.

        Returns:
            Dict containing:
                - name: App display name (e.g., "Visual Studio Code")
                - bundle_id: Bundle identifier (e.g., "com.microsoft.VSCode")
                - pid: Process ID
                - window_title: Current window title (if available)
        """
        try:
            # Get the frontmost app using lsappinfo
            result = subprocess.run(
                ["lsappinfo", "front"], capture_output=True, text=True, timeout=2
            )

            if result.returncode != 0:
                logger.error(f"lsappinfo front failed: {result.stderr}")
                return self._get_fallback_app_info()

            # Parse ASN (Application Serial Number)
            # Format: ASN:0x0-0x3d18d15:
            asn_line = result.stdout.strip()
            if ":" in asn_line:
                asn = asn_line.rstrip(":")
            else:
                logger.error(f"Unexpected lsappinfo front format: {asn_line}")
                return self._get_fallback_app_info()

            # Get detailed app info
            result = subprocess.run(
                ["lsappinfo", "info", "-only", "pid,bundleid,name", asn],
                capture_output=True,
                text=True,
                timeout=2,
            )

            if result.returncode != 0:
                logger.error(f"lsappinfo info failed: {result.stderr}")
                return self._get_fallback_app_info()

            # Parse the output
            info = self._parse_lsappinfo_output(result.stdout)

            # Try to get window title
            window_title = self._get_current_window_title()
            if window_title:
                info["window_title"] = window_title

            logger.info(f"Detected app: {info.get('name')} ({info.get('bundle_id')})")
            return info

        except Exception as e:
            logger.error(f"Failed to get app info: {e}")
            return self._get_fallback_app_info()

    def _parse_lsappinfo_output(self, output: str) -> dict[str, Any]:
        """Parse lsappinfo output into structured data."""
        info = {}

        for line in output.strip().split("\n"):
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip().strip('"')
                value = value.strip().strip('"')

                if key == "pid":
                    with contextlib.suppress(ValueError):
                        info["pid"] = int(value)
                elif key == "CFBundleIdentifier":
                    info["bundle_id"] = value
                elif key == "LSDisplayName":
                    info["name"] = value

        return info

    def _get_current_window_title(self) -> Optional[str]:
        """Get current window title using AppleScript."""
        try:
            script = """
            tell application "System Events"
                set frontApp to first application process whose frontmost is true
                set windowTitle to name of front window of frontApp
                return windowTitle
            end tell
            """

            result = subprocess.run(
                ["osascript", "-e", script], capture_output=True, text=True, timeout=3
            )

            if result.returncode == 0:
                return result.stdout.strip()

        except Exception as e:
            logger.debug(f"Could not get window title: {e}")

        return None

    def _get_fallback_app_info(self) -> dict[str, Any]:
        """Fallback app detection method."""
        try:
            # Try basic AppleScript approach
            script = """
            tell application "System Events"
                set frontApp to first application process whose frontmost is true
                return name of frontApp
            end tell
            """

            result = subprocess.run(
                ["osascript", "-e", script], capture_output=True, text=True, timeout=3
            )

            if result.returncode == 0:
                app_name = result.stdout.strip()
                return {
                    "name": app_name,
                    "bundle_id": "unknown",
                    "pid": 0,
                    "method": "fallback",
                }

        except Exception as e:
            logger.error(f"Fallback app detection failed: {e}")

        # Ultimate fallback
        return {
            "name": "unknown",
            "bundle_id": "unknown",
            "pid": 0,
            "method": "ultimate_fallback",
        }

    def get_app_for_hammerspoon(self) -> str:
        """
        Get app name formatted for Hammerspoon window filter.

        Returns simplified app name suitable for windowfilter.new().
        """
        info = self.get_current_app_info()
        return info.get("name", "unknown")

        # For Hammerspoon, we might need to simplify some names
        # But we'll keep it generic and let Hammerspoon handle variations

    def get_bundle_id_for_fallback(self) -> str:
        """Get bundle ID for app-level activation fallback."""
        info = self.get_current_app_info()
        return info.get("bundle_id", "unknown")

    def cache_current_app(self) -> None:
        """Cache current app info for later use."""
        self._current_app_info = self.get_current_app_info()
        logger.info(f"Cached app info: {self._current_app_info}")

    def get_cached_app_info(self) -> Optional[dict[str, Any]]:
        """Get previously cached app info."""
        return self._current_app_info


def main():
    """Test the app detector."""
    logging.basicConfig(level=logging.INFO)

    detector = AppDetector()

    print("🔍 Universal App Detection Test")
    print("=" * 35)

    info = detector.get_current_app_info()

    print("Current App Info:")
    print(f"  Name: {info.get('name', 'Unknown')}")
    print(f"  Bundle ID: {info.get('bundle_id', 'Unknown')}")
    print(f"  PID: {info.get('pid', 'Unknown')}")
    print(f"  Window Title: {info.get('window_title', 'Not available')}")
    print(f"  Detection Method: {info.get('method', 'primary')}")

    print(f"\nFor Hammerspoon: '{detector.get_app_for_hammerspoon()}'")
    print(f"For Fallback: '{detector.get_bundle_id_for_fallback()}'")


if __name__ == "__main__":
    main()
