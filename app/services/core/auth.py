from http import HTTPStatus

import httpx

from app.config import settings
from app.services.core.model import LoginRequest, LoginResponse


class BearerAuthWithRefresh(httpx.Auth):
    def __init__(self, token_url: str, client_credentials: LoginRequest, max_retries: int = 3):
        self.token_url = token_url
        self.client_credentials = client_credentials
        self.max_retries = max_retries
        self._token: str | None = None

    def sync_get_token(self):
        with httpx.Client() as client:
            resp = client.post(self.token_url, data=self.client_credentials.model_dump_json())
            return LoginResponse(**resp.json()).access_token

    def auth_flow(self, request):
        if not self._token:
            self._token = self.sync_get_token()
        request.headers["Authorization"] = f"Bearer {self._token}"
        response = yield request
        retries = 0
        while response.status_code in (401, 403, 404) and retries < self.max_retries:
            retries += 1
            self._token = self.sync_get_token()
            request.headers["Authorization"] = f"Bearer {self._token}"
            yield request

    async def _async_get_new_token(self):
        """Calls the /token endpoint to generate a new token."""
        # Note: We use a separate client to avoid recursion issues
        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, data=self.client_credentials.model_dump_json())
            if response.status_code != HTTPStatus.OK:
                # Forward the error gotten from /token if refresh fails
                response.raise_for_status()

            return LoginResponse(**response.json()).access_token

    async def async_sync_auth_flow(self, request):
        # 1. Inject existing token if it exists
        if not self._token:
            self._token = await self._async_get_new_token()

        request.headers["Authorization"] = f"Bearer {self._token}"

        # 2. Send the request
        response = yield request

        # 3. Intercept 401, 403, or 404 for retry/refresh logic
        retries = 0
        while response.status_code in (401, 403, 404) and retries < self.max_retries:
            retries += 1

            # Refresh the token
            self._token = await self._async_get_new_token()
            request.headers["Authorization"] = f"Bearer {self._token}"

            # Yield the request again for a retry
            response = yield request

        # Final response is returned automatically


_token_url = settings.core_api_base + "/account/token"
_credential = LoginRequest(
    username=settings.core_api_svc_account_username, password=settings.core_api_svc_account_password
)
_auth = BearerAuthWithRefresh(
    token_url=_token_url,
    client_credentials=_credential,
    max_retries=settings.core_api_max_auth_retires,
)
auth_client = httpx.AsyncClient(auth=_auth)
