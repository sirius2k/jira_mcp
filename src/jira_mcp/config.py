"""Configuration management for Jira MCP server."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    jira_url: str
    jira_username: str
    jira_api_token: str
    jira_timeout: int = 30

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
