"""Basic tests for the Claude Code Notifier."""

from src.window_test import should_notify, test_json_parsing


def test_should_notify():
    """Test notification logic."""
    assert should_notify("vscode", "terminal") is True
    assert should_notify("vscode", "vscode") is False


def test_json_functionality():
    """Test JSON parsing functionality."""
    result = test_json_parsing()
    assert result["success"] is True
    assert "transcript_path" in result
    assert "project_name" in result
