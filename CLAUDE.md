# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Development Commands

```bash
# Setup
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run server
jira-mcp
# or
python -m jira_mcp.server

# Testing
python -m pytest                    # Run all tests
python -m pytest -v                 # Verbose output
python -m pytest -k "test_name"     # Run specific test
python -m pytest tests/test_client.py  # Run single file

# Code quality
python -m mypy src                  # Type checking (strict mode)
python -m ruff check src            # Linting
python -m ruff check src --fix      # Auto-fix lint issues
```

## Architecture

This is an MCP (Model Context Protocol) server that provides Jira integration tools.

### Core Components

- **server.py**: MCP protocol implementation with tool definitions and call handlers. Uses `mcp.server.Server` with stdio transport.
- **client.py**: Async Jira REST API client using httpx. All methods are async and use basic auth with API tokens.
- **config.py**: Environment-based configuration using pydantic-settings. Loads from `.env` file.

### Available MCP Tools

| Tool | Description |
|------|-------------|
| `get_issue` | Get issue by key (e.g., PROJ-123) |
| `search_issues` | Search using JQL |
| `create_issue` | Create new issue |
| `update_issue` | Update issue fields |
| `add_comment` | Add comment to issue |
| `get_projects` | List accessible projects |
| `transition_issue` | Change issue status |
| `get_transitions` | Get available transitions |

### Jira API

Uses Jira REST API v3 with Atlassian Document Format (ADF) for rich text fields (description, comments).

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `JIRA_URL` | Yes | Jira instance URL (e.g., https://your-domain.atlassian.net) |
| `JIRA_USERNAME` | Yes | Jira account email |
| `JIRA_API_TOKEN` | Yes | API token from Atlassian account settings |
| `JIRA_TIMEOUT` | No | Request timeout in seconds (default: 30) |

## Testing

Tests use pytest with pytest-asyncio. Mock httpx responses for API tests - no live API calls in tests.
