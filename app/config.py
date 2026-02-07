import os

from pydantic import BaseModel


class Settings(BaseModel):
    bot_token: str
    webhook_secret: str
    public_webhook_base: str
    api_key: str
    api_hash: str
    bot_username: str
    core_api_svc_account_username: str
    core_api_svc_account_password: str
    core_api_max_auth_retires: int

    core_api_base: str

    hash_key: bytes


settings = Settings(
    bot_token=os.environ["TELEGRAM_BOT_TOKEN"],
    webhook_secret=os.environ["WEBHOOK_SECRET"],
    public_webhook_base=os.environ["PUBLIC_WEBHOOK_BASE"],
    core_api_base=os.environ["CORE_API_BASE"],
    hash_key=os.environ["HASH_KEY"].encode(),
    api_key=os.environ["API_KEY"],
    api_hash=os.environ["API_HASH"],
    bot_username=os.environ["BOT_USERNAME"],
    core_api_svc_account_username=os.environ["CORE_API_SVC_ACCOUNT_USERNAME"],
    core_api_svc_account_password=os.environ["CORE_API_SVC_ACCOUNT_PASSWORD"],
    core_api_max_auth_retires=os.environ["CORE_API_MAX_AUTH_RETIRES"],
)
