from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.core.model import CounselorResponse
from app.services.taccount.api import create_session, create_telegram_group, get_telegram_group_link
from app.services.taccount.model import CreateSessionResponse


@pytest.mark.asyncio
async def test_create_session_happy_path():
    telegram_user_id = 12345
    counselor_id = "counselor-1"

    counselor = CounselorResponse(id="counselor-1", telegram_user_id="321", name="Joe", bio="short bio")

    with patch("app.services.taccount.api.get_counselor", new_callable=AsyncMock) as mock_get_counselor, \
         patch("app.services.taccount.api.get_hash") as mock_get_hash, \
         patch("app.services.taccount.api.create_or_get_alias", new_callable=AsyncMock) as mock_create_or_get_alias, \
         patch("app.services.taccount.api.create_telegram_group", new_callable=AsyncMock) as mock_create_telegram_group, \
         patch("app.services.taccount.api.get_telegram_group_link", new_callable=AsyncMock) as mock_get_group_link:

        def create_telegram_group_side_effects(target_user, group_name):  # noqa: ARG001
            if target_user == telegram_user_id:
                return "user_group"
            if target_user == counselor.telegram_user_id:
                return "counselor_group"
            return "unknown_group"


        # Arrange
        mock_get_counselor.return_value = counselor
        mock_get_hash.return_value = "hashed-user-id"
        mock_create_or_get_alias.return_value = "anon123"
        mock_create_telegram_group.side_effect = create_telegram_group_side_effects
        mock_get_group_link.return_value = "https://t.me/invite/link"

        # Act
        result = await create_session(telegram_user_id, counselor_id)

        # Assert
        assert isinstance(result, CreateSessionResponse)
        assert result.user_group_id == "user_group"
        assert result.user_group_link == "https://t.me/invite/link"
        assert result.counselor_group_id == "counselor_group"

        mock_get_counselor.assert_awaited_once_with(counselor_id)
        mock_get_hash.assert_called_once_with(str(telegram_user_id))
        mock_create_or_get_alias.assert_awaited_once_with("hashed-user-id")

        mock_create_telegram_group.assert_any_await(
            counselor.telegram_user_id,
            "Counseling with anon123"
        )
        mock_create_telegram_group.assert_any_await(
            telegram_user_id,
            "Counseling with Joe"
        )

        mock_get_group_link.assert_awaited_once_with("user_group")

@pytest.mark.asyncio
async def test_create_telegram_group_creates_and_returns_chat_id():
    target_user_id = 555
    group_name = "Test Group"

    mock_bot_entity = MagicMock()
    mock_bot_entity.id = 42

    mock_me = MagicMock()
    mock_me.id = 99

    mock_created_chat = MagicMock()
    mock_created_chat.chats = [MagicMock(id=777)]

    with patch("app.services.taccount.api.telegram_client", new_callable=AsyncMock) as mock_telegram_client, \
         patch("app.services.taccount.api.settings", new_callable=AsyncMock) as mock_settings:

        # Arrange
        mock_settings.bot_username = "bot"

        mock_telegram_client.get_input_entity = AsyncMock(return_value=mock_bot_entity)
        mock_telegram_client.get_me = AsyncMock(return_value=mock_me)

        mock_telegram_client.side_effect = [
            mock_created_chat,  # CreateChatRequest
            None,               # AddChatUserRequest
            None,               # EditChatAdminRequest
            None                # DeleteChatUserRequest
        ]

        mock_telegram_client.__call__ = AsyncMock(side_effect=[
            mock_created_chat,  # CreateChatRequest
            None,               # AddChatUserRequest
            None,               # EditChatAdminRequest
            None                # DeleteChatUserRequest
        ])

        # Act
        chat_id = await create_telegram_group(target_user_id, group_name)

        # Assert
        assert chat_id == 777  # noqa: PLR2004

        mock_telegram_client.get_input_entity.assert_awaited_once_with("bot")
        mock_telegram_client.get_me.assert_awaited_once()
        assert mock_telegram_client.call_count == 4  # noqa: PLR2004


@pytest.mark.asyncio
async def test_get_telegram_group_link_returns_invite_link():
    group_id = 999

    with patch("app.services.taccount.api.telegram_app", new_callable=AsyncMock) as telegram_app:
        telegram_app.export_chat_invite_link = AsyncMock(
            return_value="https://t.me/invite/abc"
        )

        result = await get_telegram_group_link(group_id)

        assert result == "https://t.me/invite/abc"
        telegram_app.export_chat_invite_link.assert_awaited_once_with(
            chat_id=group_id
        )
