from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram import ChatMember

from app.services.core.model import CounselorResponse
from app.services.taccount.api import create_session, get_telegram_group_link
from app.services.taccount.model import CreateSessionResponse


@pytest.mark.asyncio
async def test_create_session_happy_path():
    telegram_user_id = 12345
    telegram_user_id_for_counselor = 54321
    counselor_id = 1
    user_group_id = 222
    counselor_group_id = 333

    counselor = CounselorResponse(
        id=counselor_id,
        telegram_user_id=telegram_user_id_for_counselor,
        name="Joe",
        bio="short bio",
    )

    with (
        patch(
            "app.services.taccount.api.get_counselor", new_callable=AsyncMock
        ) as mock_get_counselor,
        patch(
            "app.services.taccount.api.telegram_client.get_input_entity", new_callable=AsyncMock
        ) as mock_get_input_entity,
        patch("app.services.taccount.api.get_hash") as mock_get_hash,
        patch("app.services.taccount.api.settings") as mock_setting,
        patch(
            "app.services.taccount.api.create_or_get_alias", new_callable=AsyncMock
        ) as mock_create_or_get_alias,
        patch(
            "app.services.taccount.api.create_telegram_group", new_callable=AsyncMock
        ) as mock_create_telegram_group,
        patch(
            "app.services.taccount.api.get_telegram_group_link", new_callable=AsyncMock
        ) as mock_get_group_link,
    ):

        def create_telegram_group_side_effects(bot_entity, target_user_id, group_name):  # noqa: ARG001
            if target_user_id == telegram_user_id:
                return user_group_id
            if target_user_id == counselor.telegram_user_id:
                return counselor_group_id
            return 999

        # Arrange
        mock_setting.bot_username = "bot-username"
        mock_get_counselor.return_value = counselor
        mock_get_hash.return_value = "hashed-user-id"
        mock_get_input_entity.return_value = mock_get_input_entity
        mock_create_or_get_alias.return_value = "anon123"
        mock_create_telegram_group.side_effect = create_telegram_group_side_effects
        mock_get_group_link.return_value = "https://t.me/invite/link"

        # Act
        result = await create_session(telegram_user_id, counselor_id)

        # Assert
        assert isinstance(result, CreateSessionResponse)
        assert result.user_group_id == user_group_id
        assert result.user_group_link == "https://t.me/invite/link"
        assert result.counselor_group_id == counselor_group_id

        mock_get_counselor.assert_awaited_once_with(counselor_id)
        mock_get_hash.assert_called_once_with(str(telegram_user_id))
        mock_create_or_get_alias.assert_awaited_once_with("hashed-user-id")
        mock_get_input_entity.assert_called_once_with("bot-username")

        mock_create_telegram_group.assert_any_await(
            mock_get_input_entity, counselor.telegram_user_id, "Counseling with anon123"
        )
        mock_create_telegram_group.assert_any_await(
            mock_get_input_entity, telegram_user_id, "Counseling with Joe"
        )

        mock_get_group_link.assert_awaited_once_with(user_group_id)


@pytest.mark.asyncio
async def test_get_telegram_group_link_returns_invite_link():
    group_id = 999
    mock_member = MagicMock()
    mock_member.status = ChatMember.ADMINISTRATOR

    mock_result = MagicMock()
    mock_result.invite_link = "https://t.me/invite/abc"

    with patch("app.services.taccount.api.telegram_app", new_callable=AsyncMock) as telegram_app:
        telegram_app.bot.create_chat_invite_link = AsyncMock(return_value=mock_result)

        telegram_app.bot.get_chat_member = AsyncMock(return_value=mock_member)

        result = await get_telegram_group_link(group_id)

        assert result == mock_result.invite_link
        telegram_app.bot.create_chat_invite_link.assert_awaited_once_with(
            chat_id=group_id, name="Auto-generated invite link"
        )
