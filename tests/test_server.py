"""Tests for MCP server module."""

import pytest

from jira_mcp.server import list_tools


@pytest.mark.asyncio
async def test_list_tools() -> None:
    """Test that all tools are listed."""
    tools = await list_tools()

    tool_names = [tool.name for tool in tools]
    assert "get_issue" in tool_names
    assert "search_issues" in tool_names
    assert "create_issue" in tool_names
    assert "update_issue" in tool_names
    assert "add_comment" in tool_names
    assert "get_projects" in tool_names
    assert "transition_issue" in tool_names
    assert "get_transitions" in tool_names


@pytest.mark.asyncio
async def test_tool_schemas() -> None:
    """Test that all tools have valid input schemas."""
    tools = await list_tools()

    for tool in tools:
        assert tool.inputSchema is not None
        assert "type" in tool.inputSchema
        assert tool.inputSchema["type"] == "object"
