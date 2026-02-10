"""Pytest configuration and shared fixtures."""

import os
from unittest.mock import AsyncMock, MagicMock

import pytest

# Set environment variables before any imports that might use them
# This must happen at module level before pytest imports any test modules
_env_vars = {
    "TELEGRAM_BOT_TOKEN": "test_token",
    "WEBHOOK_SECRET": "test_secret",
    "PUBLIC_WEBHOOK_BASE": "https://test.com",
    "CORE_API_BASE": "https://core.test.com",
    "CORE_API_SVC_ACCOUNT_USERNAME": "test_username",
    "CORE_API_SVC_ACCOUNT_PASSWORD": "test_password",
    "CORE_API_MAX_AUTH_RETIRES": "3",
    "BOT_USERNAME": "@testbot",
    "HASH_KEY": "test-hash",
    "API_KEY": "1234",
    "API_HASH": "test-api-hash",
}

for key, value in _env_vars.items():
    os.environ.setdefault(key, value)


def pytest_configure():
    """Configure pytest - set environment variables before test collection."""
    # Ensure all required environment variables are set
    for key, value in _env_vars.items():
        os.environ[key] = value


@pytest.fixture(scope="session", autouse=True)
def setup_env_vars():
    """Set up environment variables for all tests (session-scoped, autouse)."""
    for key, value in _env_vars.items():
        os.environ[key] = value
    yield
    # Cleanup is optional - we don't need to remove them


@pytest.fixture
def mock_env_vars():
    """Return the mock environment variables dictionary."""
    return _env_vars.copy()


@pytest.fixture
def mock_httpx_response():
    """Create a mock httpx response."""

    def _create_response(status_code=200, json_data=None, text=None):
        response = MagicMock()
        response.status_code = status_code
        response.json.return_value = json_data or {}
        response.text = text or ""
        response.raise_for_status = MagicMock()
        return response

    return _create_response


@pytest.fixture
def mock_update():
    """Create a mock Telegram Update object."""
    update = MagicMock()
    update.effective_chat.id = 12345
    update.effective_user.id = 11111
    update.message = MagicMock()
    update.message.chat.id = 12345
    update.message.text = "Test message"
    update.message.reply_text = AsyncMock()
    update.callback_query = MagicMock()
    update.callback_query.message = MagicMock()
    update.callback_query.message.chat.id = 12345
    update.callback_query.message.edit_text = AsyncMock()
    update.callback_query.answer = AsyncMock()
    update.callback_query.data = "test:data"
    update.callback_query.from_user.id = 22222
    return update


@pytest.fixture
def mock_context():
    """Create a mock Telegram Context object."""
    context = MagicMock()
    context.bot = MagicMock()
    context.bot.send_message = AsyncMock()
    return context
