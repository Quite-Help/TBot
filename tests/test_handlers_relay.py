"""Tests for app.telegram.handlers.relay module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.telegram.handlers.relay import relay


@pytest.mark.asyncio
async def test_relay_with_text_message(mock_update, mock_context):
    """Test relay handler with text message."""
    mock_update.message.text = "Test message"
    mock_update.message.chat.id = 12345

    mock_routing = MagicMock()
    mock_routing.target_group_id = 67890
    mock_routing.display_name = "Test User"

    with (
        patch("app.telegram.handlers.relay.resolve_group", new_callable=AsyncMock) as mock_resolve,
        patch("app.telegram.handlers.relay.telegram_app.bot", new_callable=AsyncMock) as mock_bot,
    ):
        mock_resolve.return_value = mock_routing

        await relay(mock_update, mock_context)

        # Verify resolve_group was called
        mock_resolve.assert_called_once_with(12345)

        # Verify message was sent
        mock_bot.send_message.assert_called_once_with(
            chat_id=mock_routing.target_group_id,
            text=f"*From: {mock_routing.display_name}*\n\n{mock_update.message.text}",
            parse_mode="Markdown",
        )


@pytest.mark.asyncio
async def test_relay_without_message(mock_update, mock_context):
    """Test relay handler when message is None."""
    mock_update.message = None

    with patch("app.telegram.handlers.relay.resolve_group", new_callable=AsyncMock) as mock_resolve:
        await relay(mock_update, mock_context)

        # Should return early without calling resolve_group
        mock_resolve.assert_not_called()
        mock_context.bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_relay_without_text(mock_update, mock_context):
    """Test relay handler when message has no text."""
    mock_update.message.text = None

    with patch("app.telegram.handlers.relay.resolve_group", new_callable=AsyncMock) as mock_resolve:
        await relay(mock_update, mock_context)

        # Should return early without calling resolve_group
        mock_resolve.assert_not_called()
        mock_context.bot.send_message.assert_not_called()


@pytest.mark.asyncio
async def test_relay_empty_text(mock_update, mock_context):
    """Test relay handler with empty text."""
    mock_update.message.text = ""

    with patch("app.telegram.handlers.relay.resolve_group", new_callable=AsyncMock) as mock_resolve:
        await relay(mock_update, mock_context)

        # Should return early (empty string is falsy)
        mock_resolve.assert_not_called()
        mock_context.bot.send_message.assert_not_called()
