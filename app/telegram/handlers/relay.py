from app.services.core.api import resolve_group
from telegram import Update  # noqa: TC001
from telegram.ext import ContextTypes, MessageHandler, filters


async def relay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    routing = await resolve_group(message.chat.id)

    await context.bot.send_message(
        chat_id=routing.target_group_id,
        text=f"*From: {routing.display_name}*\n{message.text}",
        parse_mode="Markdown",
    )


relay_handler = MessageHandler(filters.ChatType.GROUPS & filters.TEXT, relay)
