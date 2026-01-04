from telethon import functions

from app.config import settings
from app.services.core.api import create_or_get_alias, get_counselor
from app.services.taccount.model import CreateSessionResponse
from app.telegram.app import telegram_app
from app.telegram.client import telegram_client
from app.util.hash import get_hash


async def create_session(telegram_user_id: int, counselor_id: str) -> CreateSessionResponse:
    counselor = await get_counselor(counselor_id)
    user_alias = await create_or_get_alias(get_hash(str(telegram_user_id)))
    counselor_group_id = await create_telegram_group(counselor.telegram_user_id, f"Counseling with {user_alias}")
    user_group_id = await create_telegram_group(telegram_user_id, f"Counseling with {counselor.name}")
    user_group_link = await get_telegram_group_link(user_group_id)
    return CreateSessionResponse(counselor_group_id=counselor_group_id, user_group_id=user_group_id, user_group_link=user_group_link)


async def create_telegram_group(target_user_id, group_name: str):
    bot_entity = await telegram_client.get_input_entity(settings.bot_username)

    created_chat = await telegram_client(functions.messages.CreateChatRequest(
        users=[bot_entity],
        title=group_name
    ))

    chat_id = created_chat.chats[0].id

    await telegram_client(functions.messages.AddChatUserRequest(
        chat_id=chat_id,
        user_id=target_user_id,
        fwd_limit=10
    ))

    await telegram_client(functions.messages.EditChatAdminRequest(
        chat_id=chat_id,
        user_id=bot_entity,
        is_admin=True
    ))

    me = await telegram_client.get_me()
    await telegram_client(functions.messages.DeleteChatUserRequest(
        chat_id=chat_id,
        user_id=me.id
    ))

    return chat_id

async def get_telegram_group_link(group_chat_id):
    return await telegram_app.export_chat_invite_link(chat_id=group_chat_id)
