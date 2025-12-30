import os

from pydantic import BaseModel


class Settings(BaseModel):
    bot_token: str
    webhook_secret: str
    public_webhook_base: str

    core_api_base: str
    taccount_api_base: str


settings = Settings(
    bot_token=os.environ["TELEGRAM_BOT_TOKEN"],
    webhook_secret=os.environ["WEBHOOK_SECRET"],
    public_webhook_base=os.environ["PUBLIC_WEBHOOK_BASE"],
    core_api_base=os.environ["CORE_API_BASE"],
    taccount_api_base=os.environ["TACCOUNT_API_BASE"],
)
