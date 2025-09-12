#!/usr/bin/env python3
"""
Claude Code Universal Notification System

Provides intelligent click-to-focus notifications for Claude Code completion.
Uses runtime detection and cross-space focusing breakthrough.
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Optional

# Add src to path for imports
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

from app_activator import AppActivator
from app_detector import AppDetector
from hammerspoon_focuser import HammerspoonFocuser

logger = logging.getLogger(__name__)


class ClaudeNotifier:
    """Main notification system with cross-space focusing."""

    def __init__(self):
        """Initialize the notification system."""
        self.app_detector = AppDetector()
        self.hammerspoon_focuser = HammerspoonFocuser()
        self.app_activator = AppActivator()

        # Determine the originating context (where Claude Code was running)
        self.originating_context = self._determine_originating_context()

        # Debug output to show what we inferred
        print("🔍 Script started - inferred originating context:")
        print(f"   Project: {self.originating_context.get('project_name', 'Unknown')}")
        print(
            f"   Expected window: {self.originating_context.get('expected_window', 'Unknown')}"
        )
        print(
            f"   Expected app: {self.originating_context.get('expected_app', 'Unknown')}"
        )

        logger.info(f"Inferred originating context: {self.originating_context}")

    def _determine_originating_context(self) -> dict[str, Any]:
        """
        Determine where Claude Code was running based on context clues.

        Returns:
            Dict with inferred originating context information
        """
        context = {}

        # Get project name from working directory
        try:
            cwd = os.getcwd()
            project_name = Path(cwd).name
            context["project_name"] = project_name

            # For VS Code, construct expected window title
            # Pattern: "Claude Code — {project_name}"
            context["expected_window"] = f"Claude Code — {project_name}"
            context["expected_app"] = "Code"  # VS Code shows as "Code"
            context["expected_bundle_id"] = "com.microsoft.VSCode"

            logger.info(
                f"Inferred context from working directory: {cwd} → project: {project_name}"
            )

        except Exception as e:
            logger.warning(f"Could not determine project context: {e}")
            context["project_name"] = "unknown"
            context["expected_window"] = "unknown"
            context["expected_app"] = "unknown"
            context["expected_bundle_id"] = "unknown"

        return context

    def should_notify(self) -> bool:
        """
        Determine if we should send a notification based on focus state.

        Returns:
            True if user has switched away from originating app
        """
        current_app_info = self.app_detector.get_current_app_info()
        current_app_name = current_app_info.get("name", "unknown")
        current_window_title = current_app_info.get("window_title", "Not available")
        originating_app_name = self.originating_app_info.get("name", "unknown")

        # Debug output to show current focus state
        print("🎯 Checking focus state:")
        print(f"   Current app: {current_app_name}")
        print(f"   Current window: {current_window_title}")
        print(f"   Originating app: {originating_app_name}")

        # Only notify if user has switched away from the originating app
        if current_app_name != originating_app_name:
            print(
                f"✅ Focus changed: {originating_app_name} → {current_app_name}, WILL NOTIFY"
            )
            logger.info(
                f"Focus changed: {originating_app_name} → {current_app_name}, will notify"
            )
            return True
        print(f"⏭️  Still focused on {originating_app_name}, SKIPPING notification")
        logger.info(f"Still focused on {originating_app_name}, skipping notification")
        return False

    def send_notification_and_focus(
        self, title: str, message: str, project_name: Optional[str] = None
    ) -> bool:
        """
        Send notification and enable click-to-focus.

        Args:
            title: Notification title
            message: Notification message
            project_name: Optional project context for window targeting

        Returns:
            True if notification was sent successfully
        """
        # Check if we should notify
        if not self.should_notify():
            return False

        # Prepare enhanced message
        app_name = self.originating_app_info.get("name", "unknown")
        enhanced_message = f"{message} in {project_name}" if project_name else message

        # Try cross-space focusing first (Hammerspoon)
        if self.hammerspoon_focuser.is_available():
            logger.info("Using Hammerspoon for cross-space focusing")

            # Send notification with enhanced click behavior
            success = self._send_hammerspoon_notification(
                title, enhanced_message, app_name, project_name
            )

            if success:
                logger.info("Successfully sent Hammerspoon-enabled notification")
                return True
            logger.warning("Hammerspoon notification failed, falling back...")

        # Fallback to app-level activation
        logger.info("Using app-level activation fallback")
        success = self.app_activator.activate_with_notification(
            self.originating_app_info, title, enhanced_message
        )

        if success:
            logger.info("Successfully sent fallback notification")
        else:
            logger.error("All notification methods failed")

        return success

    def _send_hammerspoon_notification(
        self,
        title: str,
        message: str,
        app_name: str,
        project_name: Optional[str] = None,
    ) -> bool:
        """Send notification with Hammerspoon cross-space focusing capability."""
        try:
            # For now, send the notification using the fallback method
            # but log that Hammerspoon is available for focusing
            bundle_id = self.originating_app_info.get("bundle_id")

            # Create a special enhanced notification that will trigger Hammerspoon focus
            # when clicked (we could extend terminal-notifier or create custom handler)
            success = self.app_activator.send_notification(title, message, bundle_id)

            if success:
                # The notification click will use bundle_id activation
                # In a full implementation, we'd integrate this with a custom click handler
                # that calls self.hammerspoon_focuser.focus_app_window(app_name, project_name)
                logger.info("Notification sent with Hammerspoon focusing available")
                return True

            return False

        except Exception as e:
            logger.error(f"Hammerspoon notification failed: {e}")
            return False

    def handle_claude_completion(
        self, hook_data: Optional[dict[str, Any]] = None
    ) -> bool:
        """
        Handle Claude Code completion notification.

        Args:
            hook_data: Optional JSON data from Claude Code hook

        Returns:
            True if handled successfully
        """
        try:
            # Extract project name from hook data or working directory
            project_name = self._extract_project_name(hook_data)

            # Send completion notification
            title = "Claude Code"
            message = "Task completed"

            success = self.send_notification_and_focus(title, message, project_name)

            if success:
                logger.info(
                    f"Handled completion notification for project: {project_name}"
                )
            else:
                logger.info("Completion notification skipped (user still focused)")

            return True

        except Exception as e:
            logger.error(f"Failed to handle completion: {e}")
            return False

    def handle_claude_notification(
        self, hook_data: Optional[dict[str, Any]] = None
    ) -> bool:
        """
        Handle explicit Claude Code notification.

        Args:
            hook_data: Optional JSON data from Claude Code hook

        Returns:
            True if handled successfully
        """
        try:
            # Extract message and project info
            project_name = self._extract_project_name(hook_data)

            if hook_data and "message" in hook_data:
                message = hook_data["message"]
                title = hook_data.get("title", "Claude Code")
            else:
                title = "Claude Code"
                message = "Notification"

            success = self.send_notification_and_focus(title, message, project_name)

            if success:
                logger.info(f"Handled notification for project: {project_name}")
            else:
                logger.info("Notification skipped (user still focused)")

            return True

        except Exception as e:
            logger.error(f"Failed to handle notification: {e}")
            return False

    def _extract_project_name(
        self, hook_data: Optional[dict[str, Any]]
    ) -> Optional[str]:
        """Extract project name from hook data or working directory."""
        # Try hook data first
        if hook_data and "project" in hook_data:
            return hook_data["project"]

        # Try transcript path from hook data
        if hook_data and "transcript_path" in hook_data:
            transcript_path = hook_data["transcript_path"]
            if transcript_path:
                # Extract project name from path like /Users/user/projects/my-project/.claude/transcript.md
                path_parts = Path(transcript_path).parts
                if ".claude" in path_parts:
                    claude_index = path_parts.index(".claude")
                    if claude_index > 0:
                        return path_parts[claude_index - 1]

        # Fallback to current working directory
        try:
            cwd = os.getcwd()
            return Path(cwd).name
        except Exception:
            return None


def main():
    """Main entry point for Claude Code hooks."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        # Read hook data from stdin if available
        hook_data = None
        if not sys.stdin.isatty():
            try:
                stdin_content = sys.stdin.read().strip()
                if stdin_content:
                    hook_data = json.loads(stdin_content)
                    logger.info(f"Received hook data: {hook_data}")
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse hook JSON: {e}")

        # Create notifier
        notifier = ClaudeNotifier()

        # Determine hook type from command line args or data
        if len(sys.argv) > 1:
            hook_type = sys.argv[1].lower()
        else:
            hook_type = "completion"  # default

        # Handle based on type
        if hook_type in ["completion", "stop"]:
            success = notifier.handle_claude_completion(hook_data)
        elif hook_type in ["notification", "notify"]:
            success = notifier.handle_claude_notification(hook_data)
        else:
            # Auto-detect based on data
            if hook_data and "message" in hook_data:
                success = notifier.handle_claude_notification(hook_data)
            else:
                success = notifier.handle_claude_completion(hook_data)

        sys.exit(0 if success else 1)

    except Exception as e:
        logger.error(f"Notification system failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
