"""Tests for app.services.core.api module."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.config import settings
from app.services.core.api import (
    create_group,
    create_or_get_alias,
    get_counselor,
    get_counselors,
    get_group_link,
    resolve_group,
)
from app.services.core.model import (
    AliasRequest,
    CounselorInfo,
    CounselorResponse,
    GroupLinkRequest,
    ResolveGroupRequest,
    ResolveGroupResponse,
)


@pytest.mark.asyncio
async def test_create_or_get_alias_success():
    """Test successful alias creation/retrieval."""
    mock_response_data = {"alias": "test_alias_123"}
    telegram_user_id = 123456
    hashed_id = "hash-id"

    # Patch the .post method specifically as an AsyncMock
    with (
        patch("app.services.core.api.auth_client.post", new_callable=AsyncMock) as mock_post,
        patch("app.services.core.api.get_hash") as mock_get_hash,
    ):
        # 1. Setup the response mock
        # Note: .json() is a regular function on the response, not awaited
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        # 2. Configure our mocks
        mock_get_hash.return_value = hashed_id
        mock_post.return_value = mock_response

        # 3. Execution
        result = await create_or_get_alias(telegram_user_id)

        # 4. Assertions
        mock_get_hash.assert_called_once_with(str(telegram_user_id))

        # Ensure the post call used the correct URL and the hashed data
        expected_data = AliasRequest(telegram_user_id=hashed_id).model_dump_json()
        mock_post.assert_called_once_with(f"{settings.core_api_base}/aliases", data=expected_data)

        assert result == "test_alias_123"
        mock_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_create_or_get_alias_http_error():
    """Test alias creation handles HTTP errors correctly."""
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 500

    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        message="Internal Server Error",
        request=MagicMock(spec=httpx.Request),
        response=mock_response,
    )

    with patch("app.services.core.api.auth_client.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_response

        # 3. Assert that the specific error is raised
        with pytest.raises(httpx.HTTPStatusError) as excinfo:
            await create_or_get_alias(12345)

        assert excinfo.value.response.status_code == 500  # noqa: PLR2004
        mock_post.assert_called_once()
        mock_response.raise_for_status.assert_called_once()


@pytest.mark.asyncio
async def test_get_counselors_success():
    """Test successful counselors retrieval."""
    # 1. Setup Mock Data
    mock_response_data = [
        {"id": 1, "name": "John Doe"},
        {"id": 2, "name": "Jane Smith"},
    ]

    # 2. Patch the .get method specifically
    with patch("app.services.core.api.auth_client.get", new_callable=AsyncMock) as mock_get:
        # Configure the response mock
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        # Link the mock response to the GET call
        mock_get.return_value = mock_response

        # 3. Execution
        result = await get_counselors()

        # 4. Assertions
        mock_get.assert_called_once_with(f"{settings.core_api_base}/counselors")

        assert len(result) == 2  # noqa: PLR2004
        assert all(isinstance(item, CounselorInfo) for item in result)

        # Verify data integrity
        assert result[0].id == 1
        assert result[0].name == "John Doe"
        assert result[1].id == 2  # noqa: PLR2004
        assert result[1].name == "Jane Smith"


@pytest.mark.asyncio
async def test_get_counselor_success():
    c_id = 1111
    mock_data = {"id": c_id, "name": "Dr. Smith", "bio": "Psychology", "telegram_user_id": 123123}

    with patch("app.services.core.api.auth_client.get", new_callable=AsyncMock) as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        result = await get_counselor(c_id)

        mock_get.assert_called_once_with(f"{settings.core_api_base}/counselors/{c_id}")
        assert isinstance(result, CounselorResponse)
        assert result.id == c_id


@pytest.mark.asyncio
async def test_get_group_link_success():
    t_id, c_id = 12345, 99
    hashed_user = "hashed-12345"
    mock_link = "https://t.me/joinchat/example"

    with (
        patch("app.services.core.api.auth_client.post", new_callable=AsyncMock) as mock_post,
        patch("app.services.core.api.get_hash", return_value=hashed_user),
    ):
        mock_response = MagicMock()
        mock_response.json.return_value = {"group_link": mock_link}
        mock_post.return_value = mock_response

        result = await get_group_link(t_id, c_id)

        # Verify the request payload matches our Pydantic model expectation
        expected_payload = GroupLinkRequest(
            telegram_user_id=hashed_user, counselor_id=c_id
        ).model_dump_json()

        mock_post.assert_called_once_with(
            f"{settings.core_api_base}/groups/link", data=expected_payload
        )
        assert result == mock_link


@pytest.mark.asyncio
async def test_get_group_link_without_link():
    """Test group link retrieval when the API returns None for the link."""
    # 1. Setup Data
    telegram_id = 12345
    c_id = 11  # Ensure this is a string to match the signature
    hashed_id = "hashed-123"
    mock_response_data = {"group_link": None}

    # 2. Patch the .post method and the hashing utility
    with (
        patch("app.services.core.api.auth_client.post", new_callable=AsyncMock) as mock_post,
        patch("app.services.core.api.get_hash", return_value=hashed_id),
    ):
        # Configure response mock
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        # 3. Execution
        result = await get_group_link(telegram_id, c_id)

        # 4. Assertions
        expected_payload = GroupLinkRequest(
            telegram_user_id=hashed_id, counselor_id=c_id
        ).model_dump_json()

        mock_post.assert_called_once_with(
            f"{settings.core_api_base}/groups/link", data=expected_payload
        )
        assert result is None


@pytest.mark.asyncio
async def test_resolve_group_success():
    g_id = 777
    t_id = 999
    mock_data = {"target_group_id": t_id, "display_name": "Dr. John"}

    with patch("app.services.core.api.auth_client.post", new_callable=AsyncMock) as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_post.return_value = mock_response

        result = await resolve_group(g_id)

        expected_data = ResolveGroupRequest(group_id=g_id).model_dump_json()
        mock_post.assert_called_once_with(
            f"{settings.core_api_base}/groups/resolve", data=expected_data
        )
        assert isinstance(result, ResolveGroupResponse)
        assert result.target_group_id == t_id


@pytest.mark.asyncio
async def test_get_group_link_raises_non_404_error():
    """Test that get_group_link re-raises non-404 HTTP errors."""
    t_id, c_id = 12345, 99
    hashed_user = "hashed-12345"

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        message="Internal Server Error",
        request=MagicMock(spec=httpx.Request),
        response=mock_response,
    )

    with (
        patch("app.services.core.api.auth_client.post", new_callable=AsyncMock) as mock_post,
        patch("app.services.core.api.get_hash", return_value=hashed_user),
    ):
        mock_post.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError) as excinfo:
            await get_group_link(t_id, c_id)

        assert excinfo.value.response.status_code == 500  # noqa: PLR2004


@pytest.mark.asyncio
async def test_get_group_link_returns_none_on_404():
    """Test that get_group_link returns None on 404 error."""
    t_id, c_id = 12345, 99
    hashed_user = "hashed-12345"

    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        message="Not Found",
        request=MagicMock(spec=httpx.Request),
        response=mock_response,
    )

    with (
        patch("app.services.core.api.auth_client.post", new_callable=AsyncMock) as mock_post,
        patch("app.services.core.api.get_hash", return_value=hashed_user),
    ):
        mock_post.return_value = mock_response

        result = await get_group_link(t_id, c_id)

        assert result is None


@pytest.mark.asyncio
async def test_create_group_success():
    """Test successful group creation."""
    user_alias = "test_alias"
    user_group_link = "https://t.me/test_group"
    user_group_id = 111
    counselor_id = 222
    counselor_group_id = 333

    with patch("app.services.core.api.auth_client.post", new_callable=AsyncMock) as mock_post:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        await create_group(
            user_alias,
            user_group_link,
            user_group_id,
            counselor_id,
            counselor_group_id,
        )

        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == f"{settings.core_api_base}/groups"
        mock_response.raise_for_status.assert_called_once()
