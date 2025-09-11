#!/usr/bin/env python3
"""
Interactive Window Detective - Universal window information gathering test.

This script provides a clean, interactive way to test window detection
capabilities without hard-coded application mappings.
"""

import contextlib
import json
import subprocess
import time
from typing import Any, Optional


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


def get_focused_window_info() -> dict[str, Any]:
    """Get comprehensive information about the currently focused window."""
    try:
        # Get the front app ASN first
        front_result = subprocess.run(
            ["lsappinfo", "front"], capture_output=True, text=True, timeout=2
        )

        if front_result.returncode != 0:
            return {
                "error": "Failed to get front app",
                "raw_output": front_result.stderr,
            }

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
            return {
                "error": "Failed to get focused app info",
                "raw_output": result.stderr,
            }

        # Parse and normalize the output
        info = _parse_lsappinfo_output(result.stdout)
        return _normalize_app_info(info)

    except subprocess.TimeoutExpired:
        return {"error": "Timeout getting focused window info"}
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}


def get_process_info(pid: int) -> dict[str, Any]:
    """Get detailed process information for a given PID."""
    try:
        # Get process command line
        ps_result = subprocess.run(
            ["ps", "-p", str(pid), "-o", "pid,ppid,command"],
            capture_output=True,
            text=True,
            timeout=2,
        )

        process_info: dict[str, Any] = {"pid": pid}

        if ps_result.returncode == 0:
            lines = ps_result.stdout.strip().split("\n")
            if len(lines) > 1:  # Skip header
                parts = lines[1].strip().split(None, 2)
                if len(parts) >= 3:
                    with contextlib.suppress(ValueError):
                        process_info["ppid"] = int(parts[1])
                    process_info["command"] = parts[2]

        return process_info

    except Exception as e:
        return {"error": f"Failed to get process info: {e}"}


def detect_window_change(
    initial_info: dict[str, Any], timeout: int = 30
) -> Optional[dict[str, Any]]:
    """Wait for window focus to change and return new window info."""
    start_time = time.time()
    initial_pid = initial_info.get("pid")

    print(f"⏳ Waiting up to {timeout} seconds for window change...")
    print("   (Switch to a different application now)")

    while time.time() - start_time < timeout:
        current_info = get_focused_window_info()
        current_pid = current_info.get("pid")

        if current_pid != initial_pid:
            print("✅ Window change detected!")
            return current_info

        time.sleep(0.5)  # Check every 500ms

    print("⚠️  No window change detected within timeout")
    return None


def interactive_test() -> None:
    """Run interactive window detection test."""
    print("🔍 Window Detective - Interactive Test")
    print("=" * 50)

    # Get initial window info
    print("\n1️⃣ Getting current window information...")
    initial_info = get_focused_window_info()

    if "error" in initial_info:
        print(f"❌ Error: {initial_info['error']}")
        return

    print("📱 Current focused application:")
    print(f"   Name: {initial_info.get('name', 'Unknown')}")
    print(f"   Bundle ID: {initial_info.get('bundleid', 'Unknown')}")
    print(f"   PID: {initial_info.get('pid', 'Unknown')}")

    # Get process details
    if "pid" in initial_info:
        process_info = get_process_info(initial_info["pid"])
        if "command" in process_info:
            print(f"   Command: {process_info['command']}")

    # Wait for window change
    print("\n2️⃣ Testing window change detection...")
    print("🔄 Please switch to a different application in the next 10 seconds...")

    new_info = detect_window_change(initial_info, timeout=10)

    if new_info:
        print("\n📱 New focused application:")
        print(f"   Name: {new_info.get('name', 'Unknown')}")
        print(f"   Bundle ID: {new_info.get('bundleid', 'Unknown')}")
        print(f"   PID: {new_info.get('pid', 'Unknown')}")

        if "pid" in new_info:
            process_info = get_process_info(new_info["pid"])
            if "command" in process_info:
                print(f"   Command: {process_info['command']}")

        # Show comparison
        print("\n🔍 Comparison:")
        print(f"   Changed from: {initial_info.get('name')} → {new_info.get('name')}")
        print(
            f"   Bundle ID changed: {initial_info.get('bundleid')} → {new_info.get('bundleid')}"
        )

    print("\n✅ Test complete!")


def json_output_test() -> None:
    """Output current window info as JSON for programmatic use."""
    info = get_focused_window_info()

    if "pid" in info and "error" not in info:
        process_info = get_process_info(info["pid"])
        info.update(process_info)

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
