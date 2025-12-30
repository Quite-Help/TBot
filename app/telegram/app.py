from app.config import settings
from app.telegram.handlers.callbacks import callback_handler
from app.telegram.handlers.relay import relay_handler
from app.telegram.handlers.start import start_handler
from telegram.ext import Application

telegram_app = Application.builder().token(settings.bot_token).build()

telegram_app.add_handler(start_handler)
telegram_app.add_handler(callback_handler)
telegram_app.add_handler(relay_handler)


async def set_webhook():
    await telegram_app.bot.set_webhook(
        url=f"{settings.public_webhook_base}/webhook/{settings.webhook_secret}",
        allowed_updates=["message", "callback_query"],
    )
