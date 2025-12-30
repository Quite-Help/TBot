from app.services.core.api import create_or_get_alias, get_counselors
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, ContextTypes


async def start(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    alias = await create_or_get_alias(chat_id)
    counselors = await get_counselors()

    keyboard = [[InlineKeyboardButton(c.name, callback_data=f"select:{c.id}")] for c in counselors]

    await update.message.reply_text(
        f"Welcome.\nYour anonymous alias is *{alias}*.\n\nSelect a counselor:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


start_handler = CommandHandler("start", start)
