"""MCP server for Jira integration."""

import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from jira_mcp.client import JiraClient
from jira_mcp.config import get_settings

server = Server("jira-mcp")
client: JiraClient | None = None


def get_client() -> JiraClient:
    """Get or create Jira client."""
    global client
    if client is None:
        settings = get_settings()
        client = JiraClient(settings)
    return client


@server.list_tools()  # type: ignore[untyped-decorator, no-untyped-call]
async def list_tools() -> list[Tool]:
    """List available Jira tools."""
    return [
        Tool(
            name="get_issue",
            description="Get a Jira issue by its key (e.g., PROJ-123)",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "The issue key (e.g., PROJ-123)"}
                },
                "required": ["issue_key"],
            },
        ),
        Tool(
            name="search_issues",
            description="Search Jira issues using JQL (Jira Query Language)",
            inputSchema={
                "type": "object",
                "properties": {
                    "jql": {"type": "string", "description": "JQL query string"},
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum results to return",
                        "default": 50,
                    },
                },
                "required": ["jql"],
            },
        ),
        Tool(
            name="create_issue",
            description="Create a new Jira issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_key": {"type": "string", "description": "Project key (e.g., PROJ)"},
                    "summary": {"type": "string", "description": "Issue summary/title"},
                    "issue_type": {
                        "type": "string",
                        "description": "Issue type (e.g., Bug, Task, Story)",
                    },
                    "description": {"type": "string", "description": "Issue description"},
                },
                "required": ["project_key", "summary", "issue_type"],
            },
        ),
        Tool(
            name="update_issue",
            description="Update fields of an existing Jira issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "The issue key (e.g., PROJ-123)",
                    },
                    "fields": {"type": "object", "description": "Fields to update"},
                },
                "required": ["issue_key", "fields"],
            },
        ),
        Tool(
            name="add_comment",
            description="Add a comment to a Jira issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "The issue key (e.g., PROJ-123)",
                    },
                    "comment": {"type": "string", "description": "Comment text"},
                },
                "required": ["issue_key", "comment"],
            },
        ),
        Tool(
            name="get_projects",
            description="Get all accessible Jira projects",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="transition_issue",
            description="Transition an issue to a new status",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "The issue key (e.g., PROJ-123)",
                    },
                    "transition_id": {"type": "string", "description": "Transition ID"},
                },
                "required": ["issue_key", "transition_id"],
            },
        ),
        Tool(
            name="get_transitions",
            description="Get available transitions for an issue",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string", "description": "The issue key (e.g., PROJ-123)"}
                },
                "required": ["issue_key"],
            },
        ),
    ]


@server.call_tool()  # type: ignore[untyped-decorator]
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    jira = get_client()

    try:
        result: dict[str, Any] | list[dict[str, Any]]
        if name == "get_issue":
            result = await jira.get_issue(arguments["issue_key"])
        elif name == "search_issues":
            result = await jira.search_issues(
                arguments["jql"],
                arguments.get("max_results", 50),
            )
        elif name == "create_issue":
            result = await jira.create_issue(
                arguments["project_key"],
                arguments["summary"],
                arguments["issue_type"],
                arguments.get("description"),
            )
        elif name == "update_issue":
            await jira.update_issue(arguments["issue_key"], arguments["fields"])
            result = {"success": True, "issue_key": arguments["issue_key"]}
        elif name == "add_comment":
            result = await jira.add_comment(arguments["issue_key"], arguments["comment"])
        elif name == "get_projects":
            result = await jira.get_projects()
        elif name == "transition_issue":
            await jira.transition_issue(arguments["issue_key"], arguments["transition_id"])
            result = {"success": True, "issue_key": arguments["issue_key"]}
        elif name == "get_transitions":
            result = await jira.get_transitions(arguments["issue_key"])
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def amain() -> None:
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> None:
    """Entry point for the server."""
    import asyncio

    asyncio.run(amain())


if __name__ == "__main__":
    main()
