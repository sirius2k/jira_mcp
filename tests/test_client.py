"""Tests for Jira client module."""

from unittest.mock import AsyncMock, patch

import pytest

from jira_mcp.client import JiraClient
from jira_mcp.config import Settings


@pytest.fixture
def jira_client(mock_settings: Settings) -> JiraClient:
    """Create a Jira client with mock settings."""
    return JiraClient(mock_settings)


@pytest.mark.asyncio
async def test_get_issue(jira_client: JiraClient) -> None:
    """Test getting an issue."""
    mock_response = {
        "key": "TEST-1",
        "fields": {"summary": "Test issue"},
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = lambda: None

        result = await jira_client.get_issue("TEST-1")

        assert result["key"] == "TEST-1"


@pytest.mark.asyncio
async def test_search_issues(jira_client: JiraClient) -> None:
    """Test searching issues with JQL."""
    mock_response = {
        "issues": [{"key": "TEST-1"}, {"key": "TEST-2"}],
        "total": 2,
    }

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = lambda: None

        result = await jira_client.search_issues("project = TEST")

        assert len(result["issues"]) == 2


@pytest.mark.asyncio
async def test_create_issue(jira_client: JiraClient) -> None:
    """Test creating an issue."""
    mock_response = {"key": "TEST-3", "id": "10003"}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.raise_for_status = lambda: None

        result = await jira_client.create_issue(
            project_key="TEST",
            summary="New issue",
            issue_type="Task",
        )

        assert result["key"] == "TEST-3"
