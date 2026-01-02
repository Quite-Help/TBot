"""Tests for app.services.core.api module."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.services.core.api import (
    create_or_get_alias,
    get_counselor,
    get_counselors,
    get_group_link,
    resolve_group,
)
from app.services.core.model import (
    CounselorInfo,
    CounselorResponse,
    ResolveGroupResponse,
)


@pytest.mark.asyncio
async def test_create_or_get_alias_success():
    """Test successful alias creation/retrieval."""
    mock_response_data = {"alias": "test_alias_123"}

    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance

        result = await create_or_get_alias(12345)

        assert result == "test_alias_123"
        mock_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_create_or_get_alias_http_error():
    """Test alias creation with HTTP error."""
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
            await create_or_get_alias(12345)


@pytest.mark.asyncio
async def test_get_counselors_success():
    """Test successful counselors retrieval."""
    mock_response_data = {
        "counselors": [
            {"id": "1", "name": "John Doe"},
            {"id": "2", "name": "Jane Smith"},
        ]
    }

    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance

        result = await get_counselors()

        assert len(result) == 2  # noqa: PLR2004
        assert isinstance(result[0], CounselorInfo)
        assert result[0].id == "1"
        assert result[0].name == "John Doe"
        assert result[1].id == "2"
        assert result[1].name == "Jane Smith"


@pytest.mark.asyncio
async def test_get_counselor_success():
    """Test successful counselor retrieval."""
    mock_response_data = {"id": "1", "name": "John Doe", "bio": "Test bio"}

    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value.get = AsyncMock(return_value=mock_response)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance

        result = await get_counselor("1")

        assert isinstance(result, CounselorResponse)
        assert result.id == "1"
        assert result.name == "John Doe"
        assert result.bio == "Test bio"


@pytest.mark.asyncio
async def test_get_group_link_with_link():
    """Test group link retrieval when link exists."""
    mock_response_data = {"group_link": "https://t.me/test_group"}

    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance

        result = await get_group_link(12345, "counselor_1")

        assert result == "https://t.me/test_group"


@pytest.mark.asyncio
async def test_get_group_link_without_link():
    """Test group link retrieval when no link exists."""
    mock_response_data = {"group_link": None}

    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance

        result = await get_group_link(12345, "counselor_1")

        assert result is None


@pytest.mark.asyncio
async def test_resolve_group_success():
    """Test successful group resolution."""
    mock_response_data = {"target_group_id": 67890, "display_name": "Test User"}

    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        mock_client_instance = AsyncMock()
        mock_client_instance.__aenter__.return_value.post = AsyncMock(return_value=mock_response)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_client_instance

        result = await resolve_group(12345)

        assert isinstance(result, ResolveGroupResponse)
        assert result.target_group_id == mock_response_data["target_group_id"]
        assert result.display_name == mock_response_data["display_name"]
