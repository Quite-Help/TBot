from telethon import TelegramClient

from app.config import settings

telegram_client = TelegramClient("tbot-service-session", settings.api_key, settings.api_hash)
