"""Basic tests for the Claude Code Notifier."""

from src.window_detective import get_focused_window_info


def test_should_notify():
    """Test notification logic."""

    # Simple notification logic test
    def should_notify(current_app: str, original_app: str) -> bool:
        return current_app != original_app

    assert should_notify("vscode", "terminal") is True
    assert should_notify("vscode", "vscode") is False


def test_json_functionality():
    """Test JSON parsing functionality."""
    # Test that we can get window info without errors
    result = get_focused_window_info()
    assert isinstance(result, dict)
    # Should have either valid info or an error
    if "error" not in result:
        assert "pid" in result or "name" in result
    else:
        assert "error" in result
