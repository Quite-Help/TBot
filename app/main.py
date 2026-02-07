from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app.healthcheck import router as healthcheck_router
from app.telegram.app import set_webhook, telegram_app
from app.telegram.client import telegram_client
from app.telegram.handlers.callbacks import callback_handler
from app.telegram.handlers.relay import relay_handler
from app.telegram.handlers.start import start_handler
from app.telegram.webhook import router as telegram_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    # telegram bot
    await telegram_app.initialize()
    await set_webhook()
    telegram_app.add_handler(start_handler)
    telegram_app.add_handler(callback_handler)
    telegram_app.add_handler(relay_handler)

    # telegram client
    await telegram_client.start()
    yield
    # Shutdown
    # telegram bot
    await telegram_app.shutdown()
    await httpx.AsyncClient().aclose()

    # telegram client
    telegram_client.disconnect()


app = FastAPI(title="TBot Service", lifespan=lifespan)

app.include_router(telegram_router)
app.include_router(healthcheck_router)
