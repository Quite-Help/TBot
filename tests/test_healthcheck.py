"""Tests for app.healthcheck module."""

import pytest

from app.healthcheck import health


@pytest.mark.asyncio
async def test_health_returns_ok_status():
    """Test that health endpoint returns ok status."""
    result = await health()

    assert result == {"status": "ok"}
