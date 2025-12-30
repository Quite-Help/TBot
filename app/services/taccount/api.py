import httpx

from app.config import settings
from app.services.taccount.model import CreateSessionResponse


async def create_session(telegram_user_id: int, counselor_id: str) -> CreateSessionResponse:
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{settings.taccount_api_base}/sessions",
            json={
                "telegram_user_id": telegram_user_id,
                "counselor_id": counselor_id,
            },
        )
        r.raise_for_status()
        return CreateSessionResponse(**r.json())
