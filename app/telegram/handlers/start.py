from app.services.core.api import create_or_get_alias, get_counselors
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, ContextTypes

welcome_message = """
*Welcome*

This is a safe space for private, one-on-one conversations with a counselor.

To protect your privacy, you'll be given a *nickname* that only this bot uses. Your real account details are never shared.
*Your nickname is {alias}*. 

When you choose a counselor, a *private chat group* will be created with *just you and this bot*.  
All messages to the counselor must be sent there. The counselor will see *only your nickname*, and your true identity remains hidden.

*Important:*
- Going forward, use your nickname when speaking to a counselor.
- Counselors will never ask for your real name or personal details. For your own privacy, *do not share* that information in the group chat or message the counselor outside of the group chat.

You'll see a list of available counselors next.  
You may talk to more than one counselor if you wish, and each conversation stays separate.

Select a counselor to see their profile from the list below. When you're ready, begin your counseling session with your desired counselor.
"""


async def start(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    alias = await create_or_get_alias(chat_id)
    counselors = await get_counselors()

    keyboard = [[InlineKeyboardButton(c.name, callback_data=f"select:{c.id}")] for c in counselors]

    await update.message.reply_text(
        welcome_message.format(alias=alias),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


start_handler = CommandHandler("start", start)
