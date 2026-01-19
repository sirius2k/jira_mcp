"""Jira API client wrapper."""

from typing import Any

import httpx

from jira_mcp.config import Settings


class JiraClient:
    """Client for interacting with Jira REST API."""

    def __init__(self, settings: Settings) -> None:
        """Initialize Jira client with settings."""
        self.base_url = settings.jira_url.rstrip("/")
        self.timeout = settings.jira_timeout
        self._auth = (settings.jira_username, settings.jira_api_token)

    def _get_headers(self) -> dict[str, str]:
        """Get common headers for API requests."""
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def get_issue(self, issue_key: str) -> dict[str, Any]:
        """Get a Jira issue by key."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/rest/api/3/issue/{issue_key}",
                headers=self._get_headers(),
                auth=self._auth,
            )
            response.raise_for_status()
            return response.json()

    async def search_issues(self, jql: str, max_results: int = 50) -> dict[str, Any]:
        """Search issues using JQL."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/rest/api/3/search",
                headers=self._get_headers(),
                auth=self._auth,
                params={"jql": jql, "maxResults": max_results},
            )
            response.raise_for_status()
            return response.json()

    async def create_issue(self, project_key: str, summary: str, issue_type: str, description: str | None = None) -> dict[str, Any]:
        """Create a new Jira issue."""
        payload: dict[str, Any] = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "issuetype": {"name": issue_type},
            }
        }
        if description:
            payload["fields"]["description"] = {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]
            }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/rest/api/3/issue",
                headers=self._get_headers(),
                auth=self._auth,
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    async def update_issue(self, issue_key: str, fields: dict[str, Any]) -> None:
        """Update a Jira issue."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.put(
                f"{self.base_url}/rest/api/3/issue/{issue_key}",
                headers=self._get_headers(),
                auth=self._auth,
                json={"fields": fields},
            )
            response.raise_for_status()

    async def add_comment(self, issue_key: str, comment: str) -> dict[str, Any]:
        """Add a comment to an issue."""
        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": comment}]}]
            }
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/rest/api/3/issue/{issue_key}/comment",
                headers=self._get_headers(),
                auth=self._auth,
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    async def get_projects(self) -> list[dict[str, Any]]:
        """Get all accessible projects."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/rest/api/3/project",
                headers=self._get_headers(),
                auth=self._auth,
            )
            response.raise_for_status()
            return response.json()

    async def transition_issue(self, issue_key: str, transition_id: str) -> None:
        """Transition an issue to a new status."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/rest/api/3/issue/{issue_key}/transitions",
                headers=self._get_headers(),
                auth=self._auth,
                json={"transition": {"id": transition_id}},
            )
            response.raise_for_status()

    async def get_transitions(self, issue_key: str) -> dict[str, Any]:
        """Get available transitions for an issue."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}/rest/api/3/issue/{issue_key}/transitions",
                headers=self._get_headers(),
                auth=self._auth,
            )
            response.raise_for_status()
            return response.json()
