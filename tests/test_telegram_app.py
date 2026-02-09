"""Tests for app.telegram.app module."""

from unittest.mock import AsyncMock, patch

import pytest

from app.telegram.app import set_webhook


@pytest.mark.asyncio
async def test_set_webhook_configures_webhook_correctly():
    """Test that set_webhook configures the Telegram webhook with correct parameters."""
    with patch("app.telegram.app.telegram_app") as mock_telegram_app:
        mock_telegram_app.bot.set_webhook = AsyncMock()

        await set_webhook()

        mock_telegram_app.bot.set_webhook.assert_awaited_once()
        call_kwargs = mock_telegram_app.bot.set_webhook.call_args[1]
        assert "webhook" in call_kwargs["url"]
        assert call_kwargs["allowed_updates"] == ["message", "callback_query"]
