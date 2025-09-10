#!/usr/bin/env python3
"""
Window detection proof-of-concept for Claude Code Notifier.

Tests Python's ability to gather the same window information
that the current shell scripts provide.
"""

import json
import subprocess
import sys
import time
from typing import Any


def get_current_pid() -> int:
    """Get the current process ID."""
    import os

    return os.getpid()


def _identify_app_from_process_name(process_name: str) -> str:
    """Identify application type from process name."""
    process_lower = process_name.lower()

    # Direct matches
    app_map = {
        "cursor": "cursor",
        "webstorm": "webstorm",
        "phpstorm": "phpstorm",
        "pycharm": "pycharm",
        "sublime": "sublime",
        "terminal": "terminal",
        "iterm": "iterm",
        "ghostty": "ghostty",
        "alacritty": "alacritty",
    }

    for key, value in app_map.items():
        if key in process_lower:
            return value

    # Multi-term matches
    if any(term in process_lower for term in ["idea", "intellij"]):
        return "idea"
    if any(term in process_lower for term in ["code", "vscode"]):
        return "vscode"

    return ""


def detect_originating_app_psutil() -> str:
    """Detect originating application using psutil (if available)."""
    try:
        import psutil

        current_pid = get_current_pid()

        while current_pid > 1:
            try:
                process = psutil.Process(current_pid)
                process_name = process.name()

                app_type = _identify_app_from_process_name(process_name)
                if app_type:
                    return app_type

                # Move to parent process
                current_pid = process.ppid()

            except (psutil.NoSuchProcess, psutil.AccessDenied):
                break

        return "unknown"

    except ImportError:
        return "psutil_not_available"


def detect_originating_app_subprocess() -> str:
    """Detect originating application using subprocess (fallback)."""
    current_pid = get_current_pid()

    while current_pid > 1:
        try:
            # Get process name
            result = subprocess.run(
                ["ps", "-o", "comm=", "-p", str(current_pid)],
                capture_output=True,
                text=True,
                timeout=1,
            )

            if result.returncode != 0:
                break

            process_name = result.stdout.strip()
            app_type = _identify_app_from_process_name(process_name)
            if app_type:
                return app_type

            # Get parent PID
            result = subprocess.run(
                ["ps", "-o", "ppid=", "-p", str(current_pid)],
                capture_output=True,
                text=True,
                timeout=1,
            )

            if result.returncode != 0:
                break

            parent_pid = result.stdout.strip()
            if not parent_pid:
                break

            current_pid = int(parent_pid)

        except (subprocess.TimeoutExpired, ValueError, OSError):
            break

    return "unknown"


def _map_focused_app_name(app_name: str) -> str:
    """Map focused app name to standard identifier."""
    if app_name == "IntelliJ IDEA":
        return "idea"
    if app_name in ["iTerm2", "iTerm"]:
        return "iterm"
    if app_name in ["Visual Studio Code", "Code"]:
        return "vscode"
    if app_name == "Cursor":
        return "cursor"
    if app_name == "Ghostty":
        return "ghostty"
    if app_name == "Terminal":
        return "terminal"
    return app_name.lower()


def get_focused_app() -> str:
    """Get currently focused application using lsappinfo."""
    try:
        result = subprocess.run(
            ["lsappinfo", "list"], capture_output=True, text=True, timeout=2
        )

        if result.returncode != 0:
            return "lsappinfo_failed"

        # Look for the app that's "in front"
        for line in result.stdout.split("\n"):
            if ": (in front)" in line:
                # Extract app name from line like: '"App Name".*: (in front)'
                start = line.find('"')
                if start != -1:
                    end = line.find('"', start + 1)
                    if end != -1:
                        app_name = line[start + 1 : end]
                        return _map_focused_app_name(app_name)

        return "no_app_in_front"

    except (subprocess.TimeoutExpired, OSError):
        return "lsappinfo_error"


def get_bundle_id(app_name: str) -> str:
    """Get bundle ID for application (same mapping as shell script)."""
    bundle_map = {
        "idea": "com.jetbrains.intellij",
        "cursor": "com.todesktop.230313mzl4w4u92",
        "vscode": "com.microsoft.VSCode",
        "webstorm": "com.jetbrains.WebStorm",
        "phpstorm": "com.jetbrains.PhpStorm",
        "pycharm": "com.jetbrains.PyCharm",
        "sublime": "com.sublimetext.4",
        "terminal": "com.apple.Terminal",
        "iterm": "com.googlecode.iterm2",
        "ghostty": "com.mitchellh.ghostty",
        "alacritty": "org.alacritty",
    }

    return bundle_map.get(app_name, "")


def extract_project_name(transcript_path: str) -> str:
    """Extract project name from transcript path (same logic as shell script)."""
    if transcript_path in ["unknown", ""] or not transcript_path:
        return "unknown"

    import os

    encoded_dir = os.path.basename(os.path.dirname(transcript_path))
    decoded_path = encoded_dir.replace("-", "/")

    # Remove /Users/username/ prefix and leading slash
    import re

    cleaned = re.sub(r"^/Users/[^/]*/", "", decoded_path)
    return cleaned.lstrip("/")


def test_json_parsing() -> dict[str, Any]:
    """Test JSON parsing capability."""
    test_input = {
        "transcript_path": "/Users/test/project-name/some/file.txt",
        "other_data": "test",
    }

    json_str = json.dumps(test_input)
    parsed = json.loads(json_str)

    return {
        "success": True,
        "transcript_path": parsed.get("transcript_path", "unknown"),
        "project_name": extract_project_name(parsed.get("transcript_path", "")),
    }


def should_notify(originating_app: str, focused_app: str) -> bool:
    """Determine if notification should be sent (same logic as shell script)."""
    return originating_app != focused_app


def run_performance_test() -> dict[str, Any]:
    """Test performance of different operations."""

    # Test psutil detection
    start = time.time()
    psutil_result = detect_originating_app_psutil()
    psutil_time = (time.time() - start) * 1000  # Convert to ms

    # Test subprocess detection
    start = time.time()
    subprocess_result = detect_originating_app_subprocess()
    subprocess_time = (time.time() - start) * 1000

    # Test focused app detection
    start = time.time()
    focused_result = get_focused_app()
    focused_time = (time.time() - start) * 1000

    # Test JSON parsing
    start = time.time()
    json_result = test_json_parsing()
    json_time = (time.time() - start) * 1000

    return {
        "psutil_detection": {"result": psutil_result, "time_ms": round(psutil_time, 2)},
        "subprocess_detection": {
            "result": subprocess_result,
            "time_ms": round(subprocess_time, 2),
        },
        "focused_app_detection": {
            "result": focused_result,
            "time_ms": round(focused_time, 2),
        },
        "json_parsing": {"result": json_result, "time_ms": round(json_time, 2)},
        "total_time_ms": round(psutil_time + focused_time + json_time, 2),
    }


def main() -> None:
    """Main test function."""
    print("🧪 Claude Code Notifier - Window Detection Test")
    print("=" * 50)

    # Run comprehensive test
    start_time = time.time()
    test_results = run_performance_test()
    total_time = (time.time() - start_time) * 1000

    print("\n📊 Test Results:")
    print(
        f"• psutil detection: {test_results['psutil_detection']['result']} ({test_results['psutil_detection']['time_ms']}ms)"
    )
    print(
        f"• subprocess detection: {test_results['subprocess_detection']['result']} ({test_results['subprocess_detection']['time_ms']}ms)"
    )
    print(
        f"• focused app: {test_results['focused_app_detection']['result']} ({test_results['focused_app_detection']['time_ms']}ms)"
    )
    print(f"• JSON parsing: success ({test_results['json_parsing']['time_ms']}ms)")

    print("\n⏱️  Performance Summary:")
    print(f"• Estimated operation time: {test_results['total_time_ms']}ms")
    print(f"• Total test time: {round(total_time, 2)}ms")

    # Test bundle ID mapping
    originating_app = test_results["psutil_detection"]["result"]
    if originating_app != "psutil_not_available":
        bundle_id = get_bundle_id(originating_app)
        print(f"• Bundle ID for {originating_app}: {bundle_id}")

    # Test notification logic
    focused_app = test_results["focused_app_detection"]["result"]
    if originating_app not in [
        "unknown",
        "psutil_not_available",
    ] and focused_app not in ["unknown", "lsappinfo_failed"]:
        should_send = should_notify(originating_app, focused_app)
        print(f"• Should notify ({originating_app} -> {focused_app}): {should_send}")

    # Test project name extraction
    test_path = "/Users/trenthm/working-dir/claude-code-notifier/transcript.json"
    project_name = extract_project_name(test_path)
    print(f"• Project name extraction: {project_name}")

    print("\n✅ Python window detection test completed")

    # Output JSON for programmatic use
    if len(sys.argv) > 1 and sys.argv[1] == "--json":
        print("\n" + json.dumps(test_results, indent=2))


if __name__ == "__main__":
    main()
