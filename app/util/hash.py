import hashlib
import hmac

from app.config import settings


def get_hash(plain_text: str) -> str:
    return hmac.new(settings.hash_key, plain_text.encode(), hashlib.sha256).hexdigest()
