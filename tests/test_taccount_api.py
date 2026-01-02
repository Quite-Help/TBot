"""Tests for app.services.taccount.api module."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.services.taccount.api import create_session
from app.services.taccount.model import CreateSessionResponse


@pytest.mark.asyncio
async def test_create_session_success():
    """Test successful session creation."""
    mock_response_data = {"user_group_link": "https://t.me/session123"}

    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance

        result = await create_session(12345, "counselor_1")

        assert isinstance(result, CreateSessionResponse)
        assert result.user_group_link == "https://t.me/session123"
        mock_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_create_session_http_error():
    """Test session creation with HTTP error."""
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Error", request=MagicMock(), response=MagicMock()
        )

        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance

        with pytest.raises(httpx.HTTPStatusError):
            await create_session(12345, "counselor_1")


@pytest.mark.asyncio
async def test_create_session_request_payload():
    """Test that create_session sends correct payload."""
    mock_response_data = {"user_group_link": "https://t.me/session123"}

    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        mock_post = AsyncMock(return_value=mock_response)
        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value.post = mock_post
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance

        await create_session(12345, "counselor_1")

        # Verify the post was called with correct payload
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]["json"]["telegram_user_id"] == 12345  # noqa: PLR2004
        assert call_args[1]["json"]["counselor_id"] == "counselor_1"
