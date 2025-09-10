#!/bin/bash

# Test script for Claude Code Enhanced Notification System
# This script verifies that all components are working correctly

echo "🧪 Testing Claude Code Enhanced Notification System..."

# Source the configuration to get paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/config.sh" ]]; then
    source "$SCRIPT_DIR/config.sh"
elif [[ -f "$HOME/.claude-notifications/config.sh" ]]; then
    source "$HOME/.claude-notifications/config.sh"
else
    echo "❌ Config file not found. Please run the installer first."
    exit 1
fi

echo "📁 Testing installation at: $CLAUDE_NOTIFICATIONS_DIR"

# Test 1: Check if all required files exist
echo "🔍 Checking required files..."
required_files=("config.sh" "common.sh" "notify-completion.sh" "notify-handler.sh" "install.sh")
missing_files=()

for file in "${required_files[@]}"; do
    if [[ ! -f "$CLAUDE_NOTIFICATIONS_DIR/$file" ]]; then
        missing_files+=("$file")
    fi
done

if [[ ${#missing_files[@]} -gt 0 ]]; then
    echo "❌ Missing files: ${missing_files[*]}"
    exit 1
else
    echo "✅ All required files present"
fi

# Test 2: Check if scripts are executable
echo "🔧 Checking script permissions..."
for file in "${required_files[@]}"; do
    if [[ ! -x "$CLAUDE_NOTIFICATIONS_DIR/$file" ]]; then
        echo "❌ $file is not executable"
        exit 1
    fi
done
echo "✅ All scripts are executable"

# Test 3: Check dependencies
echo "📦 Checking dependencies..."
if ! command -v jq &> /dev/null; then
    echo "❌ jq is not installed"
    exit 1
fi

if ! command -v terminal-notifier &> /dev/null; then
    echo "❌ terminal-notifier is not installed"
    exit 1
fi
echo "✅ All dependencies available"

# Test 4: Test notification system
echo "🔔 Testing notification system..."
test_json='{"session_id":"test-123","transcript_path":"/Users/test/.claude/projects/-Users-test-project/test.jsonl","stop_hook_active":false}'

# Test completion notification (should skip because we're focused)
echo "$test_json" | "$CLAUDE_NOTIFICATIONS_DIR/notify-completion.sh"

# Test handler notification (should skip because we're focused) 
test_notification='{"session_id":"test-123","transcript_path":"/Users/test/.claude/projects/-Users-test-project/test.jsonl","title":"Test","message":"System test notification"}'
echo "$test_notification" | "$CLAUDE_NOTIFICATIONS_DIR/notify-handler.sh"

echo "✅ Notification scripts executed (check logs for details)"

# Test 5: Check log file
echo "📋 Checking log file..."
if [[ -f "$LOG_FILE" ]]; then
    echo "✅ Log file created at: $LOG_FILE"
    echo "📊 Log entries: $(wc -l < "$LOG_FILE")"
else
    echo "❌ Log file not found at: $LOG_FILE"
    exit 1
fi

# Test 6: Test manual notification
echo "🚀 Sending test notification..."
terminal-notifier -title "Claude Code Test" -message "System test successful! 🎉" -sound "Glass"

echo ""
echo "🎉 All tests passed! Your Claude Code notification system is ready to use."
echo ""
echo "📖 Next steps:"
echo "1. Launch Claude Code from any supported application"
echo "2. Switch to another app while Claude is working" 
echo "3. Get notified when Claude finishes"
echo "4. Click notifications to return to your app"
echo ""
echo "🔍 Debug logs: tail -f $LOG_FILE"
echo "📁 Installation: $CLAUDE_NOTIFICATIONS_DIR"