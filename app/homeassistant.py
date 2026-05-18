"""Home Assistant REST API client."""
import httpx
from typing import Optional


class HomeAssistantClient:
    def __init__(self, url: str, token: str):
        self.base  = url.rstrip("/")
        self.token = token
        self._client: Optional[httpx.AsyncClient] = None

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=10, verify=False)
        return self._client

    async def get_version(self) -> tuple[bool, str]:
        client = await self._get_client()
        try:
            r = await client.get(f"{self.base}/api/", headers=self._headers())
            if r.status_code < 400:
                data = r.json()
                return True, data.get("message", "ok")
            return False, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)

    async def trigger_webhook(self, webhook_id: str) -> tuple[bool, str]:
        client = await self._get_client()
        try:
            r = await client.post(f"{self.base}/api/webhook/{webhook_id}", headers=self._headers())
            if r.status_code < 400:
                return True, f"Webhook {webhook_id!r} triggered"
            return False, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)

    async def call_service(self, domain: str, service: str, entity_id: str) -> tuple[bool, str]:
        client = await self._get_client()
        try:
            r = await client.post(
                f"{self.base}/api/services/{domain}/{service}",
                headers=self._headers(),
                json={"entity_id": entity_id},
            )
            if r.status_code < 400:
                return True, f"{domain}.{service} called for {entity_id}"
            return False, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
