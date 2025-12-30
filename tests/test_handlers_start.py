"""Tests for app.telegram.handlers.start module."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from app.telegram.handlers.start import start


@pytest.mark.asyncio
async def test_start_handler_success(mock_update, mock_env_vars):
    """Test start handler with successful API calls."""
    from app.services.core.model import CounselorInfo

    mock_alias = "test_alias_123"
    mock_counselors = [
        CounselorInfo(id="1", name="John Doe"),
        CounselorInfo(id="2", name="Jane Smith"),
    ]

    with patch("app.telegram.handlers.start.create_or_get_alias", new_callable=AsyncMock) as mock_alias_func, patch(
        "app.telegram.handlers.start.get_counselors", new_callable=AsyncMock
    ) as mock_counselors_func:
        mock_alias_func.return_value = mock_alias
        mock_counselors_func.return_value = mock_counselors

        await start(mock_update, MagicMock())

        # Verify API calls
        mock_alias_func.assert_called_once_with(mock_update.effective_chat.id)
        mock_counselors_func.assert_called_once()

        # Verify message was sent
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args

        # Check message content
        assert "Welcome" in call_args[0][0]
        assert mock_alias in call_args[0][0]

        # Check keyboard
        assert isinstance(call_args[1]["reply_markup"], InlineKeyboardMarkup)
        keyboard = call_args[1]["reply_markup"].inline_keyboard
        assert len(keyboard) == 2
        assert keyboard[0][0].text == "John Doe"
        assert keyboard[0][0].callback_data == "select:1"
        assert keyboard[1][0].text == "Jane Smith"
        assert keyboard[1][0].callback_data == "select:2"


@pytest.mark.asyncio
async def test_start_handler_empty_counselors(mock_update, mock_env_vars):
    """Test start handler with no counselors."""
    mock_alias = "test_alias_123"

    with patch("app.telegram.handlers.start.create_or_get_alias", new_callable=AsyncMock) as mock_alias_func, patch(
        "app.telegram.handlers.start.get_counselors", new_callable=AsyncMock
    ) as mock_counselors_func:
        mock_alias_func.return_value = mock_alias
        mock_counselors_func.return_value = []

        await start(mock_update, MagicMock())

        # Verify message was sent with empty keyboard
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        keyboard = call_args[1]["reply_markup"].inline_keyboard
        assert len(keyboard) == 0

