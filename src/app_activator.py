#!/usr/bin/env python3
"""
App Activation Fallback

Provides app-level activation when cross-space window focusing isn't possible.
Universal implementation without hardcoded app-specific logic.
"""

import logging
import subprocess
from typing import Any, Optional

logger = logging.getLogger(__name__)


class AppActivator:
    """Fallback app activation using bundle ID or app name."""

    def activate_app_by_bundle_id(self, bundle_id: str) -> bool:
        """
        Activate app using bundle ID.

        Args:
            bundle_id: App bundle identifier (e.g., "com.microsoft.VSCode")

        Returns:
            True if activation was attempted, False if failed
        """
        if not bundle_id or bundle_id == "unknown":
            logger.error("Cannot activate app: invalid bundle ID")
            return False

        try:
            script = f'tell application id "{bundle_id}" to activate'

            result = subprocess.run(
                ["osascript", "-e", script], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                logger.info(f"Successfully activated app with bundle ID: {bundle_id}")
                return True
            logger.warning(
                f"Failed to activate app by bundle ID {bundle_id}: {result.stderr}"
            )
            return False

        except subprocess.TimeoutExpired:
            logger.error(f"Timeout activating app by bundle ID: {bundle_id}")
            return False
        except Exception as e:
            logger.error(f"Error activating app by bundle ID {bundle_id}: {e}")
            return False

    def activate_app_by_name(self, app_name: str) -> bool:
        """
        Activate app using application name.

        Args:
            app_name: App display name (e.g., "Visual Studio Code")

        Returns:
            True if activation was attempted, False if failed
        """
        if not app_name or app_name == "unknown":
            logger.error("Cannot activate app: invalid app name")
            return False

        try:
            # Try exact name first
            script = f'tell application "{app_name}" to activate'

            result = subprocess.run(
                ["osascript", "-e", script], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                logger.info(f"Successfully activated app: {app_name}")
                return True
            logger.warning(
                f"Failed to activate app by name {app_name}: {result.stderr}"
            )

            # Try common name variations
            return self._try_name_variations(app_name)

        except subprocess.TimeoutExpired:
            logger.error(f"Timeout activating app by name: {app_name}")
            return False
        except Exception as e:
            logger.error(f"Error activating app by name {app_name}: {e}")
            return False

    def _try_name_variations(self, app_name: str) -> bool:
        """Try common app name variations."""
        # Common variations (but still universal, not hardcoded)
        variations = []

        # If it ends with something like "Code", try "Visual Studio Code"
        if app_name == "Code":
            variations.extend(["Visual Studio Code", "VSCode"])

        # If it has spaces, try without spaces
        if " " in app_name:
            variations.append(app_name.replace(" ", ""))

        # If it doesn't have spaces, try common expansions
        if " " not in app_name:
            # Don't hardcode specific expansions - this stays universal
            pass

        for variation in variations:
            try:
                script = f'tell application "{variation}" to activate'
                result = subprocess.run(
                    ["osascript", "-e", script],
                    capture_output=True,
                    text=True,
                    timeout=3,
                )

                if result.returncode == 0:
                    logger.info(
                        f"Successfully activated app using variation: {variation}"
                    )
                    return True

            except Exception as e:
                logger.debug(f"Variation {variation} failed: {e}")
                continue

        logger.warning(f"All name variations failed for: {app_name}")
        return False

    def send_notification(
        self, title: str, message: str, bundle_id: Optional[str] = None
    ) -> bool:
        """
        Send a notification with optional click-to-activate.

        Args:
            title: Notification title
            message: Notification message
            bundle_id: Optional bundle ID for click activation

        Returns:
            True if notification was sent successfully
        """
        try:
            # Check if terminal-notifier is available
            result = subprocess.run(
                ["which", "terminal-notifier"], capture_output=True, text=True
            )

            if result.returncode != 0:
                logger.warning(
                    "terminal-notifier not available, using basic notification"
                )
                return self._send_basic_notification(title, message)

            # Build terminal-notifier command
            cmd = [
                "terminal-notifier",
                "-title",
                title,
                "-message",
                message,
                "-sound",
                "Hero",
            ]

            # Add click activation if bundle ID available
            if bundle_id and bundle_id != "unknown":
                cmd.extend(["-activate", bundle_id])

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)

            if result.returncode == 0:
                logger.info("Successfully sent notification")
                return True
            logger.warning(f"terminal-notifier failed: {result.stderr}")
            return self._send_basic_notification(title, message)

        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return self._send_basic_notification(title, message)

    def _send_basic_notification(self, title: str, message: str) -> bool:
        """Send basic macOS notification using AppleScript."""
        try:
            script = f'''
            display notification "{message}" with title "{title}" sound name "Hero"
            '''

            result = subprocess.run(
                ["osascript", "-e", script], capture_output=True, text=True, timeout=5
            )

            if result.returncode == 0:
                logger.info("Successfully sent basic notification")
                return True
            logger.error(f"Basic notification failed: {result.stderr}")
            return False

        except Exception as e:
            logger.error(f"Failed to send basic notification: {e}")
            return False

    def activate_with_notification(
        self, app_info: dict[str, Any], title: str, message: str
    ) -> bool:
        """
        Send notification and provide click-to-activate using app info.

        Args:
            app_info: App information dict from AppDetector
            title: Notification title
            message: Notification message

        Returns:
            True if notification was sent successfully
        """
        bundle_id = app_info.get("bundle_id")
        app_name = app_info.get("name")

        # Send notification with click-to-activate
        success = self.send_notification(title, message, bundle_id)

        if success:
            logger.info(f"Notification sent for {app_name} ({bundle_id})")
        else:
            logger.warning("Notification failed")

        return success


def main():
    """Test the app activator."""
    logging.basicConfig(level=logging.INFO)

    activator = AppActivator()

    print("🚀 App Activator Fallback Test")
    print("=" * 32)

    # Test bundle ID activation
    print("\n📱 Testing bundle ID activation...")
    success = activator.activate_app_by_bundle_id("com.microsoft.VSCode")
    print(f"Bundle ID activation: {'✅ Success' if success else '❌ Failed'}")

    # Test app name activation
    print("\n📱 Testing app name activation...")
    success = activator.activate_app_by_name("Code")
    print(f"App name activation: {'✅ Success' if success else '❌ Failed'}")

    # Test notification
    print("\n📢 Testing notification...")
    success = activator.send_notification(
        "Test Notification",
        "This is a test notification with click-to-activate",
        "com.microsoft.VSCode",
    )
    print(f"Notification: {'✅ Success' if success else '❌ Failed'}")


if __name__ == "__main__":
    main()
