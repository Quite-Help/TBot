from telegram.ext import Application

from app.config import settings

telegram_app = Application.builder().token(settings.bot_token).build()


async def set_webhook():
    await telegram_app.bot.set_webhook(
        url=f"{settings.public_webhook_base}/webhook/{settings.webhook_secret}",
        allowed_updates=["message", "callback_query"],
    )
