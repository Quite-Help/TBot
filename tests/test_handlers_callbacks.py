"""Tests for app.telegram.handlers.callbacks module."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from app.telegram.handlers.callbacks import callbacks


@pytest.mark.asyncio
async def test_callbacks_select_with_group_link(mock_update, mock_env_vars):
    """Test callback handler for select action with existing group link."""
    mock_update.callback_query.data = "select:counselor_1"

    mock_counselor = MagicMock()
    mock_counselor.id = "counselor_1"
    mock_counselor.name = "John Doe"
    mock_counselor.bio = "Test bio"

    with patch(
        "app.telegram.handlers.callbacks.get_counselor", new_callable=AsyncMock
    ) as mock_get_counselor, patch(
        "app.telegram.handlers.callbacks.get_group_link", new_callable=AsyncMock
    ) as mock_get_group_link:
        mock_get_counselor.return_value = mock_counselor
        mock_get_group_link.return_value = "https://t.me/test_group"

        await callbacks(mock_update, MagicMock())

        # Verify API calls
        mock_get_counselor.assert_called_once_with("counselor_1")
        mock_get_group_link.assert_called_once_with(mock_update.callback_query.message.chat.id, "counselor_1")

        # Verify message was edited
        mock_update.callback_query.message.edit_text.assert_called_once()
        call_args = mock_update.callback_query.message.edit_text.call_args

        # Check message content
        assert "John Doe" in call_args[0][0]
        assert "Test bio" in call_args[0][0]

        # Check keyboard has "Open Chat" button
        keyboard = call_args[1]["reply_markup"].inline_keyboard
        assert len(keyboard) == 2
        assert keyboard[0][0].text == "Open Chat"
        assert keyboard[0][0].url == "https://t.me/test_group"


@pytest.mark.asyncio
async def test_callbacks_select_without_group_link(mock_update, mock_env_vars):
    """Test callback handler for select action without group link."""
    mock_update.callback_query.data = "select:counselor_1"

    mock_counselor = MagicMock()
    mock_counselor.id = "counselor_1"
    mock_counselor.name = "John Doe"
    mock_counselor.bio = "Test bio"

    with patch(
        "app.telegram.handlers.callbacks.get_counselor", new_callable=AsyncMock
    ) as mock_get_counselor, patch(
        "app.telegram.handlers.callbacks.get_group_link", new_callable=AsyncMock
    ) as mock_get_group_link:
        mock_get_counselor.return_value = mock_counselor
        mock_get_group_link.return_value = None

        await callbacks(mock_update, MagicMock())

        # Verify keyboard has "Start Session" button instead
        call_args = mock_update.callback_query.message.edit_text.call_args
        keyboard = call_args[1]["reply_markup"].inline_keyboard
        assert keyboard[0][0].text == "Start Session"
        assert keyboard[0][0].callback_data == "start:counselor_1"


@pytest.mark.asyncio
async def test_callbacks_start_session(mock_update, mock_env_vars):
    """Test callback handler for start session action."""
    mock_update.callback_query.data = "start:counselor_1"

    mock_session = MagicMock()
    mock_session.user_group_link = "https://t.me/session123"

    with patch(
        "app.telegram.handlers.callbacks.create_session", new_callable=AsyncMock
    ) as mock_create_session:
        mock_create_session.return_value = mock_session

        await callbacks(mock_update, MagicMock())

        # Verify session was created
        mock_create_session.assert_called_once_with(
            mock_update.callback_query.message.chat.id, "counselor_1"
        )

        # Verify message was edited
        call_args = mock_update.callback_query.message.edit_text.call_args
        assert "Your counseling session is ready" in call_args[0][0]

        # Check keyboard
        keyboard = call_args[1]["reply_markup"].inline_keyboard
        assert len(keyboard) == 2
        assert keyboard[0][0].text == "Open Chat"
        assert keyboard[0][0].url == "https://t.me/session123"
        assert keyboard[1][0].text == "Back to Home"


@pytest.mark.asyncio
async def test_callbacks_home(mock_update, mock_env_vars):
    """Test callback handler for home action."""
    from app.services.core.model import CounselorInfo

    mock_update.callback_query.data = "home"

    mock_alias = "test_alias_123"
    mock_counselors = [
        CounselorInfo(id="1", name="John Doe"),
        CounselorInfo(id="2", name="Jane Smith"),
    ]

    with patch(
        "app.telegram.handlers.callbacks.create_or_get_alias", new_callable=AsyncMock
    ) as mock_alias_func, patch(
        "app.telegram.handlers.callbacks.get_counselors", new_callable=AsyncMock
    ) as mock_counselors_func:
        mock_alias_func.return_value = mock_alias
        mock_counselors_func.return_value = mock_counselors

        await callbacks(mock_update, MagicMock())

        # Verify API calls
        mock_alias_func.assert_called_once_with(mock_update.callback_query.message.chat.id)
        mock_counselors_func.assert_called_once()

        # Verify message was edited
        call_args = mock_update.callback_query.message.edit_text.call_args
        assert "Welcome" in call_args[0][0]
        assert mock_alias in call_args[0][0]

        # Check keyboard
        keyboard = call_args[1]["reply_markup"].inline_keyboard
        assert len(keyboard) == 2
        assert keyboard[0][0].text == "John Doe"
        assert keyboard[1][0].text == "Jane Smith"

