from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app.telegram.app import set_webhook, telegram_app
from app.telegram.webhook import router as telegram_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    await telegram_app.initialize()
    await set_webhook()
    yield
    # Shutdown
    await telegram_app.shutdown()
    await httpx.AsyncClient().aclose()


app = FastAPI(title="TBot Service", lifespan=lifespan)

app.include_router(telegram_router)
