from telegram.constants import ChatMemberStatus
from telethon import functions
from telethon.tl import types

from app.config import settings
from app.services.core.api import create_or_get_alias, get_counselor
from app.services.taccount.model import CreateSessionResponse
from app.telegram.app import telegram_app
from app.telegram.client import telegram_client
from app.util.helpers import sanitize_supergroup_id_to_negative


async def create_session(telegram_user_id: int, counselor_id: int) -> CreateSessionResponse:
    bot_entity = await telegram_client.get_input_entity(settings.bot_username)
    counselor = await get_counselor(counselor_id)
    user_alias = await create_or_get_alias(telegram_user_id)
    counselor_group_id = await create_telegram_group(
        bot_entity, counselor.telegram_user_id, f"Counseling with {user_alias}"
    )
    user_group_id = await create_telegram_group(
        bot_entity, telegram_user_id, f"Counseling with {counselor.name}"
    )
    user_group_link = await get_telegram_group_link(user_group_id)
    return CreateSessionResponse(
        counselor_group_id=counselor_group_id,
        user_group_id=user_group_id,
        user_group_link=user_group_link,
    )


async def create_telegram_group(bot_entity, target_user_id, group_name: str) -> int:
    target_user = types.InputPeerUser(
        user_id=target_user_id,
        access_hash=0,  # Telethon fills this
    )

    created_chat = await telegram_client(
        functions.messages.CreateChatRequest(users=[bot_entity, target_user], title=group_name)
    )

    basic_chat = created_chat.updates.chats[0]
    print(f"✅ Group created (ID: {basic_chat.id})")

    # Migrate to supergroup
    migrate_result = await telegram_client(functions.messages.MigrateChatRequest(basic_chat.id))
    supergroup_id = migrate_result.chats[1].id
    print(f"Supergroup created: {supergroup_id}")

    # Promote bot to admin
    await telegram_client(
        functions.channels.EditAdminRequest(
            channel=supergroup_id,
            user_id=bot_entity,
            admin_rights=types.ChatAdminRights(
                change_info=True,
                post_messages=True,
                edit_messages=True,
                delete_messages=True,
                ban_users=True,
                invite_users=True,
                pin_messages=True,
                add_admins=False,
                anonymous=False,
                manage_call=True,
                other=True,
            ),
            rank="Admin",
        )
    )
    print("Bot promoted to admin")

    # Remove service account (creator)
    await telegram_client(
        functions.channels.LeaveChannelRequest(
            channel=supergroup_id,
        )
    )
    print("Service account removed")

    return supergroup_id


async def get_telegram_group_link(group_chat_id: int) -> str:
    print(f"Group chat id: {group_chat_id}")
    member = await telegram_app.bot.get_chat_member(sanitize_supergroup_id_to_negative(group_chat_id), telegram_app.bot.id)
    if member.status not in (
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER,
    ):
        raise RuntimeError("Bot must be admin to create invite links")

    result = await telegram_app.bot.create_chat_invite_link(
        chat_id=group_chat_id, name="Auto-generated invite link"
    )

    return result.invite_link
