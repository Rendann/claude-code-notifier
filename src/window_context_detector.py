#!/usr/bin/env python3
"""
Universal Window Context Detector

Gets the current window name and app info without hardcoded patterns.
Uses AppleScript and Hammerspoon for universal window detection.
"""

import logging
import subprocess
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class WindowContextDetector:
    """Universal window context detection."""

    def get_current_window_context(self) -> dict[str, Any]:
        """
        Get current window context using universal methods.

        Returns:
            Dict with window context information:
                - app_name: Application name
                - window_title: Window title
                - bundle_id: Bundle identifier (if available)
                - detection_method: Method used for detection
        """
        # Try AppleScript first (most reliable)
        context = self._get_context_via_applescript()
        if context.get("window_title"):
            context["detection_method"] = "applescript"
            logger.info(
                f"Detected window context via AppleScript: {context['app_name']} - {context['window_title']}"
            )
            return context

        # Try Hammerspoon as fallback
        context = self._get_context_via_hammerspoon()
        if context.get("window_title"):
            context["detection_method"] = "hammerspoon"
            logger.info(
                f"Detected window context via Hammerspoon: {context['app_name']} - {context['window_title']}"
            )
            return context

        # Final fallback - basic app info only
        logger.warning("Could not detect window title, using basic app info")
        return {
            "app_name": "unknown",
            "window_title": "unknown",
            "bundle_id": "unknown",
            "detection_method": "failed",
        }

    def _get_context_via_applescript(self) -> dict[str, Any]:
        """Get window context using AppleScript."""
        try:
            script = """
            tell application "System Events"
                set frontApp to first application process whose frontmost is true
                set appName to name of frontApp
                set windowTitle to name of front window of frontApp
                return appName & "|" & windowTitle
            end tell
            """

            result = subprocess.run(
                ["osascript", "-e", script], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                parts = result.stdout.strip().split("|")
                if len(parts) >= 2:
                    app_name, window_title = parts[0], parts[1]

                    # Try to get bundle ID
                    bundle_id = self._get_bundle_id_for_app(app_name)

                    return {
                        "app_name": app_name,
                        "window_title": window_title,
                        "bundle_id": bundle_id,
                    }

        except Exception as e:
            logger.debug(f"AppleScript window detection failed: {e}")

        return {
            "app_name": "unknown",
            "window_title": "unknown",
            "bundle_id": "unknown",
        }

    def _get_context_via_hammerspoon(self) -> dict[str, Any]:
        """Get window context using Hammerspoon."""
        try:
            hs_cli = self._find_hammerspoon_cli()
            if not hs_cli:
                return {
                    "app_name": "unknown",
                    "window_title": "unknown",
                    "bundle_id": "unknown",
                }

            script = """
            local application = require("hs.application")
            local window = require("hs.window")

            -- Get focused window
            local focusedWin = window.focusedWindow()
            if focusedWin then
                local title = focusedWin:title() or "NO_TITLE"
                local app = focusedWin:application()
                if app then
                    local appName = app:name()
                    local bundleID = app:bundleID() or "unknown"
                    print("SUCCESS:" .. appName .. "|" .. title .. "|" .. bundleID)
                else
                    print("ERROR:No app for window")
                end
            else
                print("ERROR:No focused window")
            end
            """

            result = subprocess.run(
                [hs_cli, "-c", script], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                output = result.stdout.strip()
                if output.startswith("SUCCESS:"):
                    parts = output[8:].split("|")  # Remove "SUCCESS:"
                    if len(parts) >= 3:
                        app_name, window_title, bundle_id = parts[0], parts[1], parts[2]
                        return {
                            "app_name": app_name,
                            "window_title": window_title,
                            "bundle_id": bundle_id,
                        }

        except Exception as e:
            logger.debug(f"Hammerspoon window detection failed: {e}")

        return {
            "app_name": "unknown",
            "window_title": "unknown",
            "bundle_id": "unknown",
        }

    def _find_hammerspoon_cli(self) -> Optional[str]:
        """Find Hammerspoon CLI executable."""
        possible_paths = [
            "/Applications/Hammerspoon.app/Contents/Frameworks/hs/hs",
            "/usr/local/bin/hs",
            "/opt/homebrew/bin/hs",
        ]

        for path in possible_paths:
            if Path(path).exists():
                return path

        return None

    def _get_bundle_id_for_app(self, app_name: str) -> str:
        """Get bundle ID for app name using AppleScript."""
        try:
            script = f'''
            tell application "System Events"
                set frontApp to first application process whose name is "{app_name}"
                return bundle identifier of frontApp
            end tell
            '''

            result = subprocess.run(
                ["osascript", "-e", script], capture_output=True, text=True, timeout=3
            )

            if result.returncode == 0:
                bundle_id = result.stdout.strip()
                if bundle_id and bundle_id != "missing value":
                    return bundle_id

        except Exception as e:
            logger.debug(f"Bundle ID detection failed for {app_name}: {e}")

        return "unknown"

    def is_same_window_context(
        self, context1: dict[str, Any], context2: dict[str, Any]
    ) -> bool:
        """
        Compare two window contexts to see if they represent the same window.

        Args:
            context1: First window context
            context2: Second window context

        Returns:
            True if contexts represent the same window
        """
        # Primary comparison: window title
        if (
            context1.get("window_title")
            and context2.get("window_title")
            and context1["window_title"] != "unknown"
            and context2["window_title"] != "unknown"
        ):
            return context1["window_title"] == context2["window_title"]

        # Fallback comparison: app name
        if (
            context1.get("app_name")
            and context2.get("app_name")
            and context1["app_name"] != "unknown"
            and context2["app_name"] != "unknown"
        ):
            return context1["app_name"] == context2["app_name"]

        # If we can't determine, assume they're different
        logger.warning("Could not reliably compare window contexts")
        return False


def main():
    """Test the window context detector."""
    logging.basicConfig(level=logging.INFO)

    detector = WindowContextDetector()

    print("🪟 Universal Window Context Detection Test")
    print("=" * 45)

    context = detector.get_current_window_context()

    print("Current Window Context:")
    print(f"   App: {context.get('app_name', 'Unknown')}")
    print(f"   Window: {context.get('window_title', 'Unknown')}")
    print(f"   Bundle ID: {context.get('bundle_id', 'Unknown')}")
    print(f"   Method: {context.get('detection_method', 'Unknown')}")

    # Test context comparison
    print("\n🔄 Testing context comparison...")
    same_context = detector.get_current_window_context()
    is_same = detector.is_same_window_context(context, same_context)
    print(f"Same window context: {is_same}")


if __name__ == "__main__":
    main()
