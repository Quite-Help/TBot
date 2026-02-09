"""Tests for app.services.core.auth module."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.services.core.auth import BearerAuthWithRefresh
from app.services.core.model import LoginRequest


@pytest.fixture
def credentials():
    return LoginRequest(username="test_user", password="test_pass")


@pytest.fixture
def auth_instance(credentials):
    return BearerAuthWithRefresh(
        token_url="https://api.test.com/token",
        client_credentials=credentials,
        max_retries=3,
    )


class TestBearerAuthWithRefreshInit:
    """Tests for BearerAuthWithRefresh initialization."""

    def test_init_sets_attributes(self, credentials):
        auth = BearerAuthWithRefresh(
            token_url="https://api.test.com/token",
            client_credentials=credentials,
            max_retries=5,
        )

        assert auth.token_url == "https://api.test.com/token"
        assert auth.client_credentials == credentials
        assert auth.max_retries == 5  # noqa: PLR2004
        assert auth._token is None

    def test_init_default_max_retries(self, credentials):
        auth = BearerAuthWithRefresh(
            token_url="https://api.test.com/token",
            client_credentials=credentials,
        )

        assert auth.max_retries == 3  # noqa: PLR2004


class TestSyncGetToken:
    """Tests for sync_get_token method."""

    def test_sync_get_token_success(self, auth_instance):
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "new_token_123"}

        with patch("app.services.core.auth.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__.return_value = mock_client
            mock_client.__exit__.return_value = None
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = auth_instance.sync_get_token()

            assert result == "new_token_123"
            mock_client.post.assert_called_once_with(
                auth_instance.token_url,
                data=auth_instance.client_credentials.model_dump_json(),
            )


class TestAuthFlow:
    """Tests for sync auth_flow generator."""

    def test_auth_flow_sets_token_on_first_request(self, auth_instance):
        mock_request = MagicMock()
        mock_request.headers = {}

        with patch.object(auth_instance, "sync_get_token", return_value="initial_token"):
            gen = auth_instance.auth_flow(mock_request)

            # First yield sends the request
            yielded_request = next(gen)

            assert yielded_request is mock_request
            assert mock_request.headers["Authorization"] == "Bearer initial_token"
            assert auth_instance._token == "initial_token"

    def test_auth_flow_uses_existing_token(self, auth_instance):
        auth_instance._token = "existing_token"
        mock_request = MagicMock()
        mock_request.headers = {}

        with patch.object(auth_instance, "sync_get_token") as mock_get_token:
            gen = auth_instance.auth_flow(mock_request)
            next(gen)

            mock_get_token.assert_not_called()
            assert mock_request.headers["Authorization"] == "Bearer existing_token"

    def test_auth_flow_retries_on_401(self, auth_instance):
        mock_request = MagicMock()
        mock_request.headers = {}

        mock_response_401 = MagicMock()
        mock_response_401.status_code = 401

        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200

        with patch.object(
            auth_instance, "sync_get_token", side_effect=["token1", "token2"]
        ):
            gen = auth_instance.auth_flow(mock_request)

            # First request
            next(gen)
            assert mock_request.headers["Authorization"] == "Bearer token1"

            # Send 401 response, should retry
            gen.send(mock_response_401)
            assert mock_request.headers["Authorization"] == "Bearer token2"

    def test_auth_flow_retries_on_403(self, auth_instance):
        mock_request = MagicMock()
        mock_request.headers = {}

        mock_response_403 = MagicMock()
        mock_response_403.status_code = 403

        with patch.object(
            auth_instance, "sync_get_token", side_effect=["token1", "token2"]
        ):
            gen = auth_instance.auth_flow(mock_request)
            next(gen)

            gen.send(mock_response_403)
            assert mock_request.headers["Authorization"] == "Bearer token2"

    def test_auth_flow_stops_after_max_retries(self, auth_instance):
        auth_instance.max_retries = 2
        mock_request = MagicMock()
        mock_request.headers = {}

        mock_response_401 = MagicMock()
        mock_response_401.status_code = 401

        with patch.object(
            auth_instance, "sync_get_token", side_effect=["t1", "t2", "t3", "t4"]
        ):
            gen = auth_instance.auth_flow(mock_request)
            next(gen)  # Initial request

            # First retry
            gen.send(mock_response_401)
            # Second retry
            gen.send(mock_response_401)

            # Third attempt should stop (max_retries=2 exceeded)
            with pytest.raises(StopIteration):
                gen.send(mock_response_401)

    def test_auth_flow_no_retry_on_success(self, auth_instance):
        mock_request = MagicMock()
        mock_request.headers = {}

        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200

        with patch.object(auth_instance, "sync_get_token", return_value="token1"):
            gen = auth_instance.auth_flow(mock_request)
            next(gen)

            # Send success response, generator should complete
            with pytest.raises(StopIteration):
                gen.send(mock_response_200)


class TestAsyncGetNewToken:
    """Tests for _async_get_new_token method."""

    @pytest.mark.asyncio
    async def test_async_get_new_token_success(self, auth_instance):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "async_token_456"}

        with patch("app.services.core.auth.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__.return_value = mock_client
            mock_client.__exit__.return_value = None
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            result = await auth_instance._async_get_new_token()

            assert result == "async_token_456"
            mock_client.post.assert_called_once_with(
                auth_instance.token_url,
                data=auth_instance.client_credentials.model_dump_json(),
            )

    @pytest.mark.asyncio
    async def test_async_get_new_token_raises_on_error(self, auth_instance):
        mock_response = MagicMock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            message="Internal Server Error",
            request=MagicMock(spec=httpx.Request),
            response=mock_response,
        )

        with patch("app.services.core.auth.httpx.Client") as mock_client_class:
            mock_client = MagicMock()
            mock_client.__enter__.return_value = mock_client
            mock_client.__exit__.return_value = None
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            with pytest.raises(httpx.HTTPStatusError):
                await auth_instance._async_get_new_token()


class TestAsyncAuthFlow:
    """Tests for async_sync_auth_flow method."""

    @pytest.mark.asyncio
    async def test_async_auth_flow_sets_token_on_first_request(self, auth_instance):
        mock_request = MagicMock()
        mock_request.headers = {}

        with patch.object(
            auth_instance, "_async_get_new_token", return_value="async_initial_token"
        ):
            gen = auth_instance.async_sync_auth_flow(mock_request)

            yielded_request = await gen.asend(None)

            assert yielded_request is mock_request
            assert mock_request.headers["Authorization"] == "Bearer async_initial_token"
            assert auth_instance._token == "async_initial_token"

    @pytest.mark.asyncio
    async def test_async_auth_flow_uses_existing_token(self, auth_instance):
        auth_instance._token = "existing_async_token"
        mock_request = MagicMock()
        mock_request.headers = {}

        with patch.object(auth_instance, "_async_get_new_token") as mock_get_token:
            gen = auth_instance.async_sync_auth_flow(mock_request)
            await gen.asend(None)

            mock_get_token.assert_not_called()
            assert mock_request.headers["Authorization"] == "Bearer existing_async_token"

    @pytest.mark.asyncio
    async def test_async_auth_flow_retries_on_401(self, auth_instance):
        mock_request = MagicMock()
        mock_request.headers = {}

        mock_response_401 = MagicMock()
        mock_response_401.status_code = 401

        with patch.object(
            auth_instance, "_async_get_new_token", side_effect=["token1", "token2"]
        ):
            gen = auth_instance.async_sync_auth_flow(mock_request)

            await gen.asend(None)
            assert mock_request.headers["Authorization"] == "Bearer token1"

            await gen.asend(mock_response_401)
            assert mock_request.headers["Authorization"] == "Bearer token2"

    @pytest.mark.asyncio
    async def test_async_auth_flow_retries_on_404(self, auth_instance):
        mock_request = MagicMock()
        mock_request.headers = {}

        mock_response_404 = MagicMock()
        mock_response_404.status_code = 404

        with patch.object(
            auth_instance, "_async_get_new_token", side_effect=["token1", "token2"]
        ):
            gen = auth_instance.async_sync_auth_flow(mock_request)
            await gen.asend(None)

            await gen.asend(mock_response_404)
            assert mock_request.headers["Authorization"] == "Bearer token2"

    @pytest.mark.asyncio
    async def test_async_auth_flow_stops_after_max_retries(self, auth_instance):
        auth_instance.max_retries = 2
        mock_request = MagicMock()
        mock_request.headers = {}

        mock_response_401 = MagicMock()
        mock_response_401.status_code = 401

        with patch.object(
            auth_instance, "_async_get_new_token", side_effect=["t1", "t2", "t3", "t4"]
        ):
            gen = auth_instance.async_sync_auth_flow(mock_request)
            await gen.asend(None)  # Initial

            await gen.asend(mock_response_401)  # Retry 1
            await gen.asend(mock_response_401)  # Retry 2

            with pytest.raises(StopAsyncIteration):
                await gen.asend(mock_response_401)  # Should stop

    @pytest.mark.asyncio
    async def test_async_auth_flow_no_retry_on_success(self, auth_instance):
        mock_request = MagicMock()
        mock_request.headers = {}

        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200

        with patch.object(auth_instance, "_async_get_new_token", return_value="token1"):
            gen = auth_instance.async_sync_auth_flow(mock_request)
            await gen.asend(None)

            with pytest.raises(StopAsyncIteration):
                await gen.asend(mock_response_200)
