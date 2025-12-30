from fastapi import APIRouter, HTTPException, Request

from app.config import settings
from app.telegram.app import telegram_app
from telegram import Update

router = APIRouter()


@router.post("/webhook/{secret}")
async def telegram_webhook(secret: str, request: Request):
    if secret != settings.webhook_secret:
        raise HTTPException(status_code=403, detail="Invalid webhook secret")

    payload = await request.json()
    update = Update.de_json(payload, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}
