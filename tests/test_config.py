"""Tests for configuration module."""

import pytest

from jira_mcp.config import Settings


def test_settings_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test settings can be loaded from environment variables."""
    monkeypatch.setenv("JIRA_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_USERNAME", "user@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token123")

    settings = Settings()

    assert settings.jira_url == "https://example.atlassian.net"
    assert settings.jira_username == "user@example.com"
    assert settings.jira_api_token == "token123"
    assert settings.jira_timeout == 30  # default value


def test_settings_custom_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test custom timeout setting."""
    monkeypatch.setenv("JIRA_URL", "https://example.atlassian.net")
    monkeypatch.setenv("JIRA_USERNAME", "user@example.com")
    monkeypatch.setenv("JIRA_API_TOKEN", "token123")
    monkeypatch.setenv("JIRA_TIMEOUT", "60")

    settings = Settings()

    assert settings.jira_timeout == 60
