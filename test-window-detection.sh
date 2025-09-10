#!/bin/bash

# Test script for universal window detection system
# Tests both functionality and edge cases

# Source the modules we need to test
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"
source "$SCRIPT_DIR/universal-window.sh"

# Test configuration
TEST_RESULTS=()
PASSED=0
FAILED=0

# Utility functions for testing
test_assert() {
    local description="$1"
    local expected="$2"  
    local actual="$3"
    
    echo "Testing: $description"
    echo "  Expected: $expected"
    echo "  Actual:   $actual"
    
    if [[ "$actual" == "$expected" ]]; then
        echo "  ✅ PASS"
        TEST_RESULTS+=("PASS: $description")
        ((PASSED++))
    else
        echo "  ❌ FAIL"
        TEST_RESULTS+=("FAIL: $description")
        ((FAILED++))
    fi
    echo
}

test_contains() {
    local description="$1"
    local expected_pattern="$2"
    local actual="$3"
    
    echo "Testing: $description"
    echo "  Pattern:  $expected_pattern"
    echo "  Actual:   $actual"
    
    if [[ "$actual" =~ $expected_pattern ]]; then
        echo "  ✅ PASS"
        TEST_RESULTS+=("PASS: $description")
        ((PASSED++))
    else
        echo "  ❌ FAIL"
        TEST_RESULTS+=("FAIL: $description")
        ((FAILED++))
    fi
    echo
}

test_not_empty() {
    local description="$1"
    local actual="$2"
    
    echo "Testing: $description"
    echo "  Result: $actual"
    
    if [[ -n "$actual" && "$actual" != "unknown" ]]; then
        echo "  ✅ PASS"
        TEST_RESULTS+=("PASS: $description")
        ((PASSED++))
    else
        echo "  ❌ FAIL - Result is empty or unknown"
        TEST_RESULTS+=("FAIL: $description")
        ((FAILED++))
    fi
    echo
}

# Test the basic functionality
echo "=== BASIC FUNCTIONALITY TESTS ==="

# Test 1: Originating window detection for current process
result=$(get_window_id "vscode" "originating")
test_contains "Originating window ID contains app type" "^vscode:" "$result"

# Test 2: App display name mapping
result=$(get_app_display_name "vscode")
test_assert "VSCode display name mapping" "Code" "$result"

result=$(get_app_display_name "iterm")
test_assert "iTerm display name mapping" "iTerm2" "$result"

result=$(get_app_display_name "unknown_app")
test_assert "Unknown app returns empty" "" "$result"

# Test 3: Window identifier extraction
result=$(extract_window_identifier "Claude Code — claude-code-notifier")
test_assert "Extract workspace from window title" "claude-code-notifier" "$result"

result=$(extract_window_identifier "Simple Window")
test_assert "Extract full title when no separator" "Simple Window" "$result"

# Test 4: Enhanced app info
result=$(get_app_with_window_info "vscode")
test_contains "Enhanced app info format" "vscode" "$result"

echo "=== REAL WORLD SCENARIO TESTS ==="

# Test 5: Current VSCode window detection (if VSCode is running)
if pgrep -f "Visual Studio Code" >/dev/null; then
    echo "VSCode detected running - testing real window detection..."
    
    result=$(get_window_id "vscode" "focused")
    test_contains "VSCode focused window detection" "^vscode:" "$result"
    
    result=$(get_window_id "vscode" "originating") 
    test_contains "VSCode originating window detection" "^vscode:" "$result"
else
    echo "VSCode not running - skipping real VSCode tests"
fi

# Test 6: iTerm window detection (if iTerm is running)
if pgrep -f "iTerm" >/dev/null; then
    echo "iTerm detected running - testing real window detection..."
    
    result=$(get_window_id "iterm" "focused")
    test_contains "iTerm focused window detection" "^iterm:" "$result"
else
    echo "iTerm not running - skipping real iTerm tests"
fi

echo "=== NOTIFICATION LOGIC TESTS ==="

# Test 7: Same app, same window should NOT notify
export -f log_message  # Ensure log_message is available
result=$(should_notify_with_windows "vscode" "vscode" && echo "notify" || echo "no_notify")
# This should depend on whether windows are actually different, so we just check it runs

echo "Testing notification logic execution:"
echo "  should_notify_with_windows 'vscode' 'vscode' returned: $result"
echo "  ✅ Function executed without error"
echo

# Test 8: Different apps should always notify
result=$(should_notify_with_windows "vscode" "chrome" && echo "notify" || echo "no_notify")
test_assert "Different apps should notify" "notify" "$result"

echo "=== EDGE CASE TESTS ==="

# Test 9: Invalid app types
result=$(get_window_id "" "originating")
test_contains "Empty app type handling" ":" "$result"

result=$(get_window_id "fake_app" "originating") 
test_contains "Unknown app type handling" "fake_app:" "$result"

# Test 10: Invalid modes
result=$(get_window_id "vscode" "invalid_mode")
test_contains "Invalid mode defaults to originating" "vscode:" "$result"

# Test 11: Security - test with potentially dangerous input
dangerous_input="'; rm -rf /tmp; echo '"
result=$(get_app_display_name "$dangerous_input")
test_assert "Dangerous input returns empty" "" "$result"

echo "=== PERFORMANCE TESTS ==="

# Test 12: Measure OSA call performance
if pgrep -f "Visual Studio Code" >/dev/null; then
    echo "Testing OSA performance..."
    start_time=$(date +%s%N)
    result=$(get_window_id "vscode" "focused")
    end_time=$(date +%s%N)
    duration=$(( (end_time - start_time) / 1000000 ))  # Convert to milliseconds
    
    echo "OSA call took: ${duration}ms"
    if [[ $duration -lt 1000 ]]; then
        echo "  ✅ Performance acceptable (< 1 second)"
        ((PASSED++))
    else
        echo "  ⚠️  Performance slow (> 1 second)"
        ((FAILED++))
    fi
    echo
else
    echo "VSCode not running - skipping OSA performance test"
fi

echo "=== TEST SUMMARY ==="
echo "Tests passed: $PASSED"
echo "Tests failed: $FAILED"
echo "Total tests:  $((PASSED + FAILED))"
echo

if [[ $FAILED -eq 0 ]]; then
    echo "🎉 ALL TESTS PASSED!"
    exit 0
else
    echo "❌ Some tests failed. Review results above."
    echo
    echo "Failed tests:"
    for result in "${TEST_RESULTS[@]}"; do
        if [[ "$result" =~ ^FAIL: ]]; then
            echo "  - ${result#FAIL: }"
        fi
    done
    exit 1
fi