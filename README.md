# Jira MCP Server

MCP (Model Context Protocol) server for Jira integration.

## Setup

1. Create virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

2. Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

3. Set your Jira credentials in `.env`:
   - `JIRA_URL`: Your Jira instance URL
   - `JIRA_USERNAME`: Your Jira email
   - `JIRA_API_TOKEN`: API token from https://id.atlassian.com/manage-profile/security/api-tokens

## Usage

Run the MCP server:

```bash
jira-mcp
```

Or:

```bash
python -m jira_mcp.server
```

## Available Tools

| Tool | Description |
|------|-------------|
| `get_issue` | Get a Jira issue by key |
| `search_issues` | Search issues using JQL |
| `create_issue` | Create a new issue |
| `update_issue` | Update issue fields |
| `add_comment` | Add a comment to an issue |
| `get_projects` | List accessible projects |
| `transition_issue` | Change issue status |
| `get_transitions` | Get available transitions |

## Development

Run tests:

```bash
python -m pytest
```

Type checking:

```bash
python -m mypy src
```

Linting:

```bash
python -m ruff check src
```
