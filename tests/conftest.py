"""Pytest fixtures for Jira MCP tests."""

import pytest

from jira_mcp.config import Settings


@pytest.fixture
def mock_settings() -> Settings:
    """Provide mock settings for testing."""
    return Settings(
        jira_url="https://test.atlassian.net",
        jira_username="test@example.com",
        jira_api_token="test-token",
        jira_timeout=30,
    )
