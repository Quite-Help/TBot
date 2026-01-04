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


def test_settings_initialization(mock_env_vars):
    """Test that settings can be created from environment variables."""
    # Test that Settings can be instantiated with the mocked env vars
    test_settings = Settings(
        bot_token=mock_env_vars["TELEGRAM_BOT_TOKEN"],
        webhook_secret=mock_env_vars["WEBHOOK_SECRET"],
        public_webhook_base=mock_env_vars["PUBLIC_WEBHOOK_BASE"],
        core_api_base=mock_env_vars["CORE_API_BASE"],
        api_key=mock_env_vars["API_KEY"],
        api_hash=mock_env_vars["API_HASH"],
        bot_username=mock_env_vars["BOT_USERNAME"],
        hash_key=mock_env_vars["HASH_KEY"].encode(),
    )

    assert test_settings.bot_token == mock_env_vars["TELEGRAM_BOT_TOKEN"]
    assert test_settings.webhook_secret == mock_env_vars["WEBHOOK_SECRET"]
    assert test_settings.public_webhook_base == mock_env_vars["PUBLIC_WEBHOOK_BASE"]
    assert test_settings.core_api_base == mock_env_vars["CORE_API_BASE"]
    assert test_settings.api_key == mock_env_vars["API_KEY"]
    assert test_settings.api_hash == mock_env_vars["API_HASH"]
    assert test_settings.bot_username == mock_env_vars["BOT_USERNAME"]
    assert test_settings.hash_key == mock_env_vars["HASH_KEY"].encode()


def test_settings_missing_env_var(monkeypatch):
    """Test that missing environment variable raises KeyError."""
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)

    with pytest.raises(KeyError):
        Settings(
            bot_token=os.environ["TELEGRAM_BOT_TOKEN"],
            webhook_secret="test",
            public_webhook_base="https://test.com",
            core_api_base="https://core.test.com",
        )
