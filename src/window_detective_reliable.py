#!/usr/bin/env python3
"""
Reliable Window Detective - The working solution that detects both app and window changes.

Strategy:
1. Use lsappinfo for reliable app detection (like window_detective.py)
2. Add PyObjC window numbers only for same-app differentiation
3. Best of both worlds: catches app switches AND window switches
"""

import contextlib
import json
import subprocess
import time
from typing import Any, Optional

# PyObjC imports for window-level detection
try:
    from Quartz import (  # type: ignore[import-untyped]
        CGWindowListCopyWindowInfo,
        kCGNullWindowID,
        kCGWindowListOptionOnScreenOnly,
    )

    PYOBJC_AVAILABLE = True
except ImportError:
    PYOBJC_AVAILABLE = False


def _parse_lsappinfo_output(output: str) -> dict[str, str]:
    """Parse lsappinfo output into a dictionary."""
    lines = output.strip().split("\n")
    info = {}

    for line in lines:
        if "=" in line:
            key, value = line.split("=", 1)
            key = key.strip().strip('"')
            value = value.strip().strip('"')
            info[key] = value

    return info


def _normalize_app_info(info: dict[str, str]) -> dict[str, Any]:
    """Normalize lsappinfo output to consistent key names."""
    normalized_info: dict[str, Any] = {}
    if "pid" in info:
        with contextlib.suppress(ValueError):
            normalized_info["pid"] = int(info["pid"])

    if "CFBundleIdentifier" in info:
        normalized_info["bundleid"] = info["CFBundleIdentifier"]

    if "LSDisplayName" in info:
        normalized_info["name"] = info["LSDisplayName"]

    return normalized_info


def get_app_info_lsappinfo() -> dict[str, Any]:
    """Get reliable app info using lsappinfo (proven approach)."""
    try:
        # Get the front app ASN first
        front_result = subprocess.run(
            ["lsappinfo", "front"], capture_output=True, text=True, timeout=2
        )

        if front_result.returncode != 0:
            return {"error": "Failed to get front app"}

        asn = front_result.stdout.strip()
        if not asn:
            return {"error": "No front app ASN returned"}

        # Get detailed info for the front app
        result = subprocess.run(
            ["lsappinfo", "info", "-only", "pid,bundleid,name", asn],
            capture_output=True,
            text=True,
            timeout=2,
        )

        if result.returncode != 0:
            return {"error": "Failed to get focused app info"}

        # Parse and normalize the output
        info = _parse_lsappinfo_output(result.stdout)
        return _normalize_app_info(info)

    except subprocess.TimeoutExpired:
        return {"error": "Timeout getting focused window info"}
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}


def get_main_window_number(app_pid: int) -> Optional[int]:
    """Get the main window number for an app using PyObjC."""
    if not PYOBJC_AVAILABLE:
        return None

    try:
        # Get all on-screen windows
        windows = CGWindowListCopyWindowInfo(
            kCGWindowListOptionOnScreenOnly, kCGNullWindowID
        )

        # Find windows for this app
        app_windows = [w for w in windows if w.get("kCGWindowOwnerPID") == app_pid]

        if not app_windows:
            return None

        # Find main window candidates (layer 0, reasonable size)
        main_candidates = []
        for window in app_windows:
            layer = window.get("kCGWindowLayer", 1000)
            bounds = window.get("kCGWindowBounds", {})

            if bounds:
                width = bounds.get("Width", 0)
                height = bounds.get("Height", 0)

                if layer == 0 and width > 400 and height > 300:
                    main_candidates.append(window)

        if main_candidates:
            # Return first main candidate's window number
            window_num = main_candidates[0].get("kCGWindowNumber")
            return int(window_num) if window_num is not None else None

        if app_windows:
            # Fallback: largest window
            largest = max(
                app_windows,
                key=lambda w: (
                    w.get("kCGWindowBounds", {}).get("Width", 0)
                    * w.get("kCGWindowBounds", {}).get("Height", 0)
                ),
            )
            window_num = largest.get("kCGWindowNumber")
            return int(window_num) if window_num is not None else None

        return None

    except Exception:
        return None


def get_focused_window_info() -> dict[str, Any]:
    """Get comprehensive window info: reliable app detection + window numbers."""
    # First, get reliable app info
    app_info = get_app_info_lsappinfo()

    if "error" in app_info:
        return app_info

    # Add window number if possible
    app_pid = app_info.get("pid")
    if app_pid and PYOBJC_AVAILABLE:
        window_number = get_main_window_number(app_pid)
        if window_number:
            app_info["window_number"] = window_number

    return app_info


def create_window_signature(window_info: dict[str, Any]) -> str:
    """Create signature: PID:WindowNumber (or just PID if no window)."""
    if "error" in window_info:
        return "error"

    pid = window_info.get("pid", "unknown")
    window_number = window_info.get("window_number")

    if window_number:
        return f"{pid}:{window_number}"
    return f"{pid}:no_window"


def detect_window_change(
    initial_info: dict[str, Any], timeout: int = 30
) -> Optional[dict[str, Any]]:
    """Wait for window focus to change and return new window info."""
    start_time = time.time()
    initial_signature = create_window_signature(initial_info)

    print(f"⏳ Waiting up to {timeout} seconds for window change...")
    print("   (Switch to a different window or application now)")

    while time.time() - start_time < timeout:
        current_info = get_focused_window_info()

        if "error" in current_info:
            print(f"   Error getting window info: {current_info['error']}")
            time.sleep(0.5)
            continue

        current_signature = create_window_signature(current_info)

        if current_signature != initial_signature:
            print("✅ Window change detected!")
            return current_info

        time.sleep(0.5)  # Check every 500ms

    print("⚠️  No window change detected within timeout")
    return None


def interactive_test() -> None:
    """Run interactive window detection test."""
    print("🔍 Reliable Window Detective - The Working Solution")
    print("=" * 60)
    print("✅ Strategy: lsappinfo for apps + PyObjC for windows")

    # Get initial window info
    print("\n1️⃣ Getting current window information...")
    initial_info = get_focused_window_info()

    if "error" in initial_info:
        print(f"❌ Error: {initial_info['error']}")
        return

    print("📱 Current focused window:")
    print(f"   Application: {initial_info.get('name', 'Unknown')}")
    print(f"   Bundle ID: {initial_info.get('bundleid', 'Unknown')}")
    print(f"   PID: {initial_info.get('pid', 'Unknown')}")
    window_number = initial_info.get("window_number", "None")
    print(f"   🆔 Window Number: {window_number}")

    signature = create_window_signature(initial_info)
    print(f"\n🔑 Window Signature: {signature}")

    # Wait for window change
    print("\n2️⃣ Testing window change detection...")
    print("🔄 Switch to ANY different window (same app or different app)...")

    new_info = detect_window_change(initial_info, timeout=15)

    if new_info:
        print("\n📱 New focused window:")
        print(f"   Application: {new_info.get('name', 'Unknown')}")
        print(f"   Bundle ID: {new_info.get('bundleid', 'Unknown')}")
        print(f"   PID: {new_info.get('pid', 'Unknown')}")
        new_window_number = new_info.get("window_number", "None")
        print(f"   🆔 Window Number: {new_window_number}")

        new_signature = create_window_signature(new_info)
        print(f"\n🔑 New Window Signature: {new_signature}")

        # Show change analysis
        print("\n🔍 Change Analysis:")

        initial_app = initial_info.get("name", "Unknown")
        new_app = new_info.get("name", "Unknown")
        print(f"   Application: {initial_app} → {new_app}")

        initial_pid = initial_info.get("pid", "Unknown")
        new_pid = new_info.get("pid", "Unknown")
        print(f"   PID: {initial_pid} → {new_pid}")

        initial_window = initial_info.get("window_number", "None")
        new_window = new_info.get("window_number", "None")
        print(f"   Window Number: {initial_window} → {new_window}")

        if initial_pid == new_pid and initial_window != new_window:
            print("   🎯 Same application, different window!")
        elif initial_pid != new_pid:
            print("   🔄 Different application!")
        else:
            print("   🤔 Same window (should not happen)")

    print("\n✅ Test complete!")


def json_output_test() -> None:
    """Output current window info as JSON for programmatic use."""
    info = get_focused_window_info()

    # Add window signature for easy comparison
    if "error" not in info:
        info["window_signature"] = create_window_signature(info)

    print(json.dumps(info, indent=2))


def main() -> None:
    """Main entry point."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        json_output_test()
    else:
        interactive_test()


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
