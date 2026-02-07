from httpx import HTTPStatusError
from app.config import settings
from app.services.core.auth import auth_client
from app.services.core.model import (
    AliasRequest,
    AliasResponse,
    CounselorInfo,
    CounselorResponse,
    CreateGroupRequest,
    GroupLinkRequest,
    GroupLinkResponse,
    ResolveGroupRequest,
    ResolveGroupResponse,
)
from app.util.hash import get_hash


async def create_or_get_alias(telegram_user_id: int) -> str:
    r = await auth_client.post(
        f"{settings.core_api_base}/aliases",
        data=AliasRequest(telegram_user_id=get_hash(str(telegram_user_id))).model_dump_json(),
    )
    r.raise_for_status()
    response = AliasResponse(**r.json())
    return response.alias


async def get_counselors() -> list[CounselorInfo]:
    r = await auth_client.get(f"{settings.core_api_base}/counselors")
    r.raise_for_status()
    return [CounselorInfo(**row) for row in r.json()]


async def get_counselor(counselor_id: str) -> CounselorResponse:
    r = await auth_client.get(f"{settings.core_api_base}/counselors/{counselor_id}")
    r.raise_for_status()
    return CounselorResponse(**r.json())


async def get_group_link(telegram_user_id: int, counselor_id: str) -> str | None:
    r = await auth_client.post(
        f"{settings.core_api_base}/groups/link",
        data=GroupLinkRequest(
            telegram_user_id=get_hash(str(telegram_user_id)),
            counselor_id=counselor_id,
        ).model_dump_json(),
    )
    try:
        r.raise_for_status()
    except HTTPStatusError:
        if r.status_code == 404:  # noqa: PLR2004
            return None
        raise

    response = GroupLinkResponse(**r.json())
    return response.group_link


async def resolve_group(group_id: int) -> ResolveGroupResponse:
    r = await auth_client.post(
        f"{settings.core_api_base}/groups/resolve",
        data=ResolveGroupRequest(group_id=group_id).model_dump_json(),
    )
    r.raise_for_status()
    return ResolveGroupResponse(**r.json())


async def create_group(
    user_alias: str,
    user_group_link: str,
    user_group_id: str,
    counselor_id: str,
    counselor_group_id: str,
) -> None:
    r = await auth_client.post(
        f"{settings.core_api_base}/groups",
        data=CreateGroupRequest(
            user_alias=user_alias,
            user_group_link=user_group_link,
            user_group_id=user_group_id,
            counselor_id=counselor_id,
            counselor_group_id=counselor_group_id,
        ),
    )
    r.raise_for_status()
