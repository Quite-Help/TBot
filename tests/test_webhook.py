"""Tests for app.telegram.webhook module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, Request
from telegram import Update

from app.telegram.webhook import telegram_webhook


@pytest.mark.asyncio
async def test_telegram_webhook_valid_secret():
    """Test webhook with valid secret."""
    mock_payload = {"update_id": 123, "message": {"text": "test"}}

    with patch("app.telegram.webhook.telegram_app") as mock_app:
        mock_app.bot = MagicMock()
        mock_update = MagicMock()
        Update.de_json = MagicMock(return_value=mock_update)
        mock_app.process_update = AsyncMock()

        mock_request = MagicMock(spec=Request)
        mock_request.json = AsyncMock(return_value=mock_payload)

        result = await telegram_webhook("test_secret", mock_request)

        assert result == {"ok": True}
        mock_app.process_update.assert_called_once_with(mock_update)


@pytest.mark.asyncio
async def test_telegram_webhook_invalid_secret():
    """Test webhook with invalid secret."""
    mock_request = MagicMock(spec=Request)

    with pytest.raises(HTTPException) as exc_info:
        await telegram_webhook("invalid_secret", mock_request)

    assert exc_info.value.status_code == 403  # noqa: PLR2004
    assert "Invalid webhook secret" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_telegram_webhook_payload_processing():
    """Test that webhook processes payload correctly."""
    mock_payload = {"update_id": 123, "message": {"text": "test"}}

    with patch("app.telegram.webhook.telegram_app") as mock_app:
        mock_app.bot = MagicMock()
        mock_update = MagicMock()
        Update.de_json = MagicMock(return_value=mock_update)
        mock_app.process_update = AsyncMock()

        mock_request = MagicMock(spec=Request)
        mock_request.json = AsyncMock(return_value=mock_payload)

        await telegram_webhook("test_secret", mock_request)

        Update.de_json.assert_called_once_with(mock_payload, mock_app.bot)
        mock_app.process_update.assert_called_once_with(mock_update)
