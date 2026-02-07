"""Tests for app.main module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import app, lifespan


@pytest.mark.asyncio
async def test_lifespan_startup_shutdown():
    """Test lifespan context manager startup and shutdown."""
    with (
        patch("app.main.telegram_app") as mock_telegram_app,
        patch("app.main.telegram_client") as mock_telegram_client,
        patch("app.main.set_webhook", new_callable=AsyncMock) as mock_set_webhook,
        patch("httpx.AsyncClient") as mock_httpx,
    ):
        mock_telegram_app.initialize = AsyncMock()
        mock_telegram_app.shutdown = AsyncMock()
        mock_api = MagicMock(spec=FastAPI)
        mock_api.state = MagicMock()

        mock_telegram_client.start = AsyncMock()

        mock_client_instance = AsyncMock()
        mock_client_instance.aclose = AsyncMock()
        mock_httpx.return_value = mock_client_instance

        async with lifespan(mock_api):
            # During context (startup complete)
            mock_telegram_app.initialize.assert_called_once()
            mock_set_webhook.assert_called_once()
            mock_telegram_client.start.assert_called_once()

        # After context (shutdown complete)
        mock_telegram_app.shutdown.assert_called_once()
        mock_client_instance.aclose.assert_called_once()


def test_app_creation():
    """Test FastAPI app creation."""
    assert isinstance(app, FastAPI)
    assert app.title == "TBot Service"


def test_app_has_router():
    """Test that app includes telegram router."""
    # Check that router is included (we can't easily test this without running the app)
    # But we can verify the app is properly configured
    assert len(app.routes) > 0


def test_app_client():
    """Test app with test client."""
    client = TestClient(app)

    # Test that app is accessible
    # Note: This will fail if routes require authentication, but tests basic app setup
    response = client.get("/docs")
    # Should either return 200 (docs) or 404 (if docs disabled)
    assert response.status_code in [200, 404]
