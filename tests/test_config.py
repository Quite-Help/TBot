"""Tests for app.config module."""

import os

import pytest

from app.config import Settings, settings


def test_settings_model():
    """Test Settings model structure."""

    assert settings.bot_token == "test_token"
    assert settings.webhook_secret == "test_secret"
    assert settings.public_webhook_base == "https://test.com"
    assert settings.core_api_base == "https://core.test.com"
    assert settings.taccount_api_base == "https://taccount.test.com"


def test_settings_initialization(mock_env_vars):
    """Test that settings can be created from environment variables."""
    # Test that Settings can be instantiated with the mocked env vars
    test_settings = Settings(
        bot_token=mock_env_vars["TELEGRAM_BOT_TOKEN"],
        webhook_secret=mock_env_vars["WEBHOOK_SECRET"],
        public_webhook_base=mock_env_vars["PUBLIC_WEBHOOK_BASE"],
        core_api_base=mock_env_vars["CORE_API_BASE"],
        taccount_api_base=mock_env_vars["TACCOUNT_API_BASE"],
    )

    assert test_settings.bot_token == mock_env_vars["TELEGRAM_BOT_TOKEN"]
    assert test_settings.webhook_secret == mock_env_vars["WEBHOOK_SECRET"]
    assert test_settings.public_webhook_base == mock_env_vars["PUBLIC_WEBHOOK_BASE"]
    assert test_settings.core_api_base == mock_env_vars["CORE_API_BASE"]
    assert test_settings.taccount_api_base == mock_env_vars["TACCOUNT_API_BASE"]


def test_settings_missing_env_var(monkeypatch):
    """Test that missing environment variable raises KeyError."""
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)

    with pytest.raises(KeyError):
        Settings(
            bot_token=os.environ["TELEGRAM_BOT_TOKEN"],
            webhook_secret="test",
            public_webhook_base="https://test.com",
            core_api_base="https://core.test.com",
            taccount_api_base="https://taccount.test.com",
        )
