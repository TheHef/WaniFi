"""TrueNAS SCALE REST API client."""
import httpx
from typing import Optional


class TrueNASClient:
    def __init__(self, url: str, api_key: str):
        self.base    = url.rstrip("/")
        self.api_key = api_key
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=15, verify=False,
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
        return self._client

    async def get_system_info(self) -> tuple[bool, str]:
        client = await self._get_client()
        try:
            r = await client.get(f"{self.base}/api/v2.0/system/info")
            if r.status_code < 400:
                data = r.json()
                return True, data.get("version", "ok")
            return False, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)

    async def service_action(self, service: str, action: str) -> tuple[bool, str]:
        """Start, stop, or restart a named service."""
        client = await self._get_client()
        try:
            r = await client.post(
                f"{self.base}/api/v2.0/service/{action}",
                json={"service": service},
            )
            if r.status_code < 400:
                return True, f"Service '{service}' {action}ed"
            return False, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
