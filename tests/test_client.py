"""Tests for Jira client module."""

from unittest.mock import AsyncMock, Mock, patch

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

    mock_response_obj = Mock()
    mock_response_obj.json.return_value = mock_response
    mock_response_obj.raise_for_status = Mock()

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response_obj

        result = await jira_client.get_issue("TEST-1")

        assert result["key"] == "TEST-1"


@pytest.mark.asyncio
async def test_search_issues(jira_client: JiraClient) -> None:
    """Test searching issues with JQL."""
    mock_response = {
        "issues": [{"key": "TEST-1"}, {"key": "TEST-2"}],
        "total": 2,
    }

    mock_response_obj = Mock()
    mock_response_obj.json.return_value = mock_response
    mock_response_obj.raise_for_status = Mock()

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response_obj

        result = await jira_client.search_issues("project = TEST")

        assert len(result["issues"]) == 2


@pytest.mark.asyncio
async def test_create_issue(jira_client: JiraClient) -> None:
    """Test creating an issue."""
    mock_response = {"key": "TEST-3", "id": "10003"}

    mock_response_obj = Mock()
    mock_response_obj.json.return_value = mock_response
    mock_response_obj.raise_for_status = Mock()

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response_obj

        result = await jira_client.create_issue(
            project_key="TEST",
            summary="New issue",
            issue_type="Task",
        )

        assert result["key"] == "TEST-3"


@pytest.mark.asyncio
async def test_get_comments_default_params(jira_client: JiraClient) -> None:
    """Test getting comments with default pagination parameters."""
    mock_response = {
        "startAt": 0,
        "maxResults": 50,
        "total": 3,
        "isLast": True,
        "values": [
            {
                "id": "10001",
                "author": {
                    "displayName": "John Doe",
                    "emailAddress": "john@example.com"
                },
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "First comment"
                                }
                            ]
                        }
                    ]
                },
                "created": "2024-01-15T10:00:00.000+0000",
                "updated": "2024-01-15T10:00:00.000+0000"
            },
            {
                "id": "10002",
                "author": {
                    "displayName": "Jane Smith",
                    "emailAddress": "jane@example.com"
                },
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Second comment"
                                }
                            ]
                        }
                    ]
                },
                "created": "2024-01-15T11:00:00.000+0000",
                "updated": "2024-01-15T11:00:00.000+0000"
            },
            {
                "id": "10003",
                "author": {
                    "displayName": "Bob Johnson",
                    "emailAddress": "bob@example.com"
                },
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Third comment"
                                }
                            ]
                        }
                    ]
                },
                "created": "2024-01-15T12:00:00.000+0000",
                "updated": "2024-01-15T12:00:00.000+0000"
            }
        ]
    }

    mock_response_obj = Mock()
    mock_response_obj.json.return_value = mock_response
    mock_response_obj.raise_for_status = Mock()

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response_obj

        result = await jira_client.get_comments("TEST-1")

        assert result["total"] == 3
        assert len(result["values"]) == 3
        assert result["startAt"] == 0
        assert result["maxResults"] == 50
        assert result["isLast"] is True
        assert result["values"][0]["id"] == "10001"
        assert result["values"][1]["id"] == "10002"
        assert result["values"][2]["id"] == "10003"

        # Verify API call was made with correct parameters
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == "https://test.atlassian.net/rest/api/3/issue/TEST-1/comment"
        assert call_args[1]["params"]["startAt"] == 0
        assert call_args[1]["params"]["maxResults"] == 50
        assert call_args[1]["auth"] == ("test@example.com", "test-token")
        assert call_args[1]["headers"]["Accept"] == "application/json"
        assert call_args[1]["headers"]["Content-Type"] == "application/json"


@pytest.mark.asyncio
async def test_get_comments_custom_pagination(jira_client: JiraClient) -> None:
    """Test getting comments with custom pagination parameters."""
    mock_response = {
        "startAt": 10,
        "maxResults": 20,
        "total": 50,
        "isLast": False,
        "values": [
            {
                "id": "10011",
                "author": {
                    "displayName": "User Test",
                    "emailAddress": "user@example.com"
                },
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Paginated comment"
                                }
                            ]
                        }
                    ]
                },
                "created": "2024-01-15T13:00:00.000+0000",
                "updated": "2024-01-15T13:00:00.000+0000"
            }
        ]
    }

    mock_response_obj = Mock()
    mock_response_obj.json.return_value = mock_response
    mock_response_obj.raise_for_status = Mock()

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response_obj

        result = await jira_client.get_comments("TEST-2", start_at=10, max_results=20)

        assert result["startAt"] == 10
        assert result["maxResults"] == 20
        assert result["total"] == 50
        assert result["isLast"] is False
        assert len(result["values"]) == 1

        # Verify custom pagination parameters were used
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]["params"]["startAt"] == 10
        assert call_args[1]["params"]["maxResults"] == 20


@pytest.mark.asyncio
async def test_get_comments_empty_list(jira_client: JiraClient) -> None:
    """Test getting comments when there are no comments."""
    mock_response = {
        "startAt": 0,
        "maxResults": 50,
        "total": 0,
        "isLast": True,
        "values": []
    }

    mock_response_obj = Mock()
    mock_response_obj.json.return_value = mock_response
    mock_response_obj.raise_for_status = Mock()

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response_obj

        result = await jira_client.get_comments("TEST-3")

        assert result["total"] == 0
        assert len(result["values"]) == 0
        assert result["isLast"] is True


@pytest.mark.asyncio
async def test_get_comments_single_comment(jira_client: JiraClient) -> None:
    """Test getting a single comment."""
    mock_response = {
        "startAt": 0,
        "maxResults": 50,
        "total": 1,
        "isLast": True,
        "values": [
            {
                "id": "10001",
                "author": {
                    "displayName": "Single User",
                    "emailAddress": "single@example.com"
                },
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Only comment"
                                }
                            ]
                        }
                    ]
                },
                "created": "2024-01-15T10:00:00.000+0000",
                "updated": "2024-01-15T10:00:00.000+0000"
            }
        ]
    }

    mock_response_obj = Mock()
    mock_response_obj.json.return_value = mock_response
    mock_response_obj.raise_for_status = Mock()

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response_obj

        result = await jira_client.get_comments("TEST-4")

        assert result["total"] == 1
        assert len(result["values"]) == 1
        assert result["values"][0]["id"] == "10001"


@pytest.mark.asyncio
async def test_get_comments_last_page(jira_client: JiraClient) -> None:
    """Test getting the last page of comments."""
    mock_response = {
        "startAt": 40,
        "maxResults": 50,
        "total": 45,
        "isLast": True,
        "values": [
            {
                "id": "10041",
                "author": {
                    "displayName": "Last User",
                    "emailAddress": "last@example.com"
                },
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Comment on last page"
                                }
                            ]
                        }
                    ]
                },
                "created": "2024-01-15T14:00:00.000+0000",
                "updated": "2024-01-15T14:00:00.000+0000"
            }
        ]
    }

    mock_response_obj = Mock()
    mock_response_obj.json.return_value = mock_response
    mock_response_obj.raise_for_status = Mock()

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response_obj

        result = await jira_client.get_comments("TEST-5", start_at=40)

        assert result["isLast"] is True
        assert result["startAt"] == 40
        assert result["total"] == 45


@pytest.mark.asyncio
async def test_get_comments_complex_adf_body(jira_client: JiraClient) -> None:
    """Test getting comments with complex ADF body structure."""
    mock_response = {
        "startAt": 0,
        "maxResults": 50,
        "total": 1,
        "isLast": True,
        "values": [
            {
                "id": "10001",
                "author": {
                    "displayName": "Advanced User",
                    "emailAddress": "advanced@example.com"
                },
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "This is "
                                },
                                {
                                    "type": "text",
                                    "text": "bold text",
                                    "marks": [{"type": "strong"}]
                                },
                                {
                                    "type": "text",
                                    "text": " and "
                                },
                                {
                                    "type": "text",
                                    "text": "italic text",
                                    "marks": [{"type": "em"}]
                                }
                            ]
                        },
                        {
                            "type": "bulletList",
                            "content": [
                                {
                                    "type": "listItem",
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [
                                                {
                                                    "type": "text",
                                                    "text": "First item"
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "listItem",
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [
                                                {
                                                    "type": "text",
                                                    "text": "Second item"
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                "created": "2024-01-15T15:00:00.000+0000",
                "updated": "2024-01-15T15:00:00.000+0000"
            }
        ]
    }

    mock_response_obj = Mock()
    mock_response_obj.json.return_value = mock_response
    mock_response_obj.raise_for_status = Mock()

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response_obj

        result = await jira_client.get_comments("TEST-6")

        assert result["total"] == 1
        assert len(result["values"]) == 1
        comment = result["values"][0]
        assert comment["body"]["type"] == "doc"
        assert len(comment["body"]["content"]) == 2
        assert comment["body"]["content"][0]["type"] == "paragraph"
        assert comment["body"]["content"][1]["type"] == "bulletList"


@pytest.mark.asyncio
async def test_get_comments_url_construction(jira_client: JiraClient) -> None:
    """Test that get_comments constructs the correct URL for different issue keys."""
    mock_response = {
        "startAt": 0,
        "maxResults": 50,
        "total": 0,
        "isLast": True,
        "values": []
    }

    mock_response_obj = Mock()
    mock_response_obj.json.return_value = mock_response
    mock_response_obj.raise_for_status = Mock()

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response_obj

        # Test with different issue key formats
        issue_keys = ["PROJ-123", "TEST-1", "ABC-9999"]

        for issue_key in issue_keys:
            await jira_client.get_comments(issue_key)

        # Verify all calls were made with correct URLs
        assert mock_get.call_count == 3
        calls = mock_get.call_args_list

        assert calls[0][0][0] == "https://test.atlassian.net/rest/api/3/issue/PROJ-123/comment"
        assert calls[1][0][0] == "https://test.atlassian.net/rest/api/3/issue/TEST-1/comment"
        assert calls[2][0][0] == "https://test.atlassian.net/rest/api/3/issue/ABC-9999/comment"
