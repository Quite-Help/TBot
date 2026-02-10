import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackQueryHandler, ContextTypes

from app.services.core.api import (
    create_group,
    create_or_get_alias,
    get_counselor,
    get_counselors,
    get_group_link,
)
from app.services.taccount.api import create_session
from app.telegram.handlers.start import welcome_message

logger = logging.getLogger(__name__)


async def callbacks(update: Update, _context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query is None:
        print(f"Update callback query is empty: {update}")
        return

    await query.answer()

    if query.message is None:
        print(f"Message does not contain chat: {query}")
        return
    user_id = query.from_user.id
    data = query.data

    if data is None or not (data.startswith("select:")  or data.startswith("start:") or data == "home"):
        print(f"Unexpected data received: {data}")
        return

    if data.startswith("select:"):
        counselor_id = int(data.split(":")[1])
        counselor = await get_counselor(counselor_id)
        group_link = await get_group_link(user_id, counselor_id)

        keyboard = [
            [InlineKeyboardButton("Open Chat", url=group_link)]
            if group_link
            else [InlineKeyboardButton("Start Session", callback_data=f"start:{counselor_id}")],
            [InlineKeyboardButton("Back to Home", callback_data="home")],
        ]

        await query.message.edit_text(
            f"*{counselor.name}*\n\n{counselor.bio}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif data.startswith("start:"):
        counselor_id = int(data.split(":")[1])
        session = await create_session(user_id, counselor_id)
        try:
            user_alias = await create_or_get_alias(user_id)
            await create_group(
                user_alias,
                session.user_group_link,
                session.user_group_id,
                counselor_id,
                session.counselor_group_id,
            )
        except Exception:
            # TODO: delete group if core api data creation fails to avoid zombie groups
            logger.exception(
                "Error creating records for user and counselor group in core api when start handler is called"
            )
            raise

        await query.message.edit_text(
            "Your counseling session is ready.\n\nClick the button below to open the chat.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton("Open Chat", url=session.user_group_link)],
                    [InlineKeyboardButton("Back to Home", callback_data="home")],
                ]
            ),
        )

    elif data == "home":
        alias = await create_or_get_alias(user_id)
        counselors = await get_counselors()
        keyboard = [
            [InlineKeyboardButton(c.name, callback_data=f"select:{c.id}")] for c in counselors
        ]
        await query.message.edit_text(
            welcome_message.format(alias=alias),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


callback_handler = CallbackQueryHandler(callbacks)
