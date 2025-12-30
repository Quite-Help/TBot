import httpx

from app.config import settings
from app.services.core.model import (
    AliasResponse,
    CounselorInfo,
    CounselorResponse,
    CounselorsResponse,
    GroupLinkResponse,
    ResolveGroupResponse,
)


async def create_or_get_alias(telegram_user_id: int) -> str:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{settings.core_api_base}/aliases/start",
            json={"telegram_user_id": telegram_user_id},
        )
        r.raise_for_status()
        response = AliasResponse(**r.json())
        return response.alias


async def get_counselors() -> list[CounselorInfo]:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{settings.core_api_base}/counselors")
        r.raise_for_status()
        response = CounselorsResponse(**r.json())
        return response.counselors


async def get_counselor(counselor_id: str) -> CounselorResponse:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{settings.core_api_base}/counselors/{counselor_id}")
        r.raise_for_status()
        return CounselorResponse(**r.json())


async def get_group_link(telegram_user_id: int, counselor_id: str) -> str | None:
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{settings.core_api_base}/sessions/group-link",
            params={
                "telegram_user_id": telegram_user_id,
                "counselor_id": counselor_id,
            },
        )
        r.raise_for_status()
        response = GroupLinkResponse(**r.json())
        return response.group_link


async def resolve_group(group_id: int) -> ResolveGroupResponse:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{settings.core_api_base}/sessions/resolve",
            json={"group_id": group_id},
        )
        r.raise_for_status()
        return ResolveGroupResponse(**r.json())
