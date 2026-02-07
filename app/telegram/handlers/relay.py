from telegram import Update  # noqa: TC002
from telegram.ext import ContextTypes, MessageHandler, filters

from app.services.core.api import resolve_group
from app.telegram.app import telegram_app


async def relay(update: Update, _: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    routing = await resolve_group(message.chat.id)

    await telegram_app.bot.send_message(
        chat_id=routing.target_group_id,
        text=f"*From: {routing.display_name}*\n\n{message.text}",
        parse_mode="Markdown",
    )


relay_handler = MessageHandler(filters.ChatType.GROUPS & filters.TEXT, relay)
