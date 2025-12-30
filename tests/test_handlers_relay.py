"""Tests for app.telegram.handlers.relay module."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram import Update

from app.telegram.handlers.relay import relay


@pytest.mark.asyncio
async def test_relay_with_text_message(mock_update, mock_context, mock_env_vars):
    """Test relay handler with text message."""
    mock_update.message.text = "Test message"
    mock_update.message.chat.id = 12345

    mock_routing = MagicMock()
    mock_routing.target_group_id = 67890
    mock_routing.display_name = "Test User"

    with patch("app.telegram.handlers.relay.resolve_group", new_callable=AsyncMock) as mock_resolve:
        mock_resolve.return_value = mock_routing

        await relay(mock_update, mock_context)

        # Verify resolve_group was called
        mock_resolve.assert_called_once_with(12345)

        # Verify message was sent
        mock_context.bot.send_message.assert_called_once_with(
            chat_id=67890,
            text="*From: Test User*\nTest message",
            parse_mode="Markdown",
        )


@pytest.mark.asyncio
async def test_relay_without_message(mock_update, mock_context, mock_env_vars):
    """Test relay handler when message is None."""
    mock_update.message = None

    with patch("app.telegram.handlers.relay.resolve_group", new_callable=AsyncMock) as mock_resolve:
        await relay(mock_update, mock_context)

        # Should return early without calling resolve_group
        mock_resolve.assert_not_called()
        mock_context.bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_relay_without_text(mock_update, mock_context, mock_env_vars):
    """Test relay handler when message has no text."""
    mock_update.message.text = None

    with patch("app.telegram.handlers.relay.resolve_group", new_callable=AsyncMock) as mock_resolve:
        await relay(mock_update, mock_context)

        # Should return early without calling resolve_group
        mock_resolve.assert_not_called()
        mock_context.bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_relay_empty_text(mock_update, mock_context, mock_env_vars):
    """Test relay handler with empty text."""
    mock_update.message.text = ""

    with patch("app.telegram.handlers.relay.resolve_group", new_callable=AsyncMock) as mock_resolve:
        await relay(mock_update, mock_context)

        # Should return early (empty string is falsy)
        mock_resolve.assert_not_called()
        mock_context.bot.send_message.assert_not_called()

