"""SABnzbd API client."""
import httpx
from typing import Optional


class SabnzbdClient:
    def __init__(self, url: str, api_key: str):
        self.base    = url.rstrip("/")
        self.api_key = api_key
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=10, verify=False)
        return self._client

    async def _get(self, mode: str, extra: Optional[dict] = None) -> tuple[bool, str]:
        client = await self._get_client()
        params: dict = {"mode": mode, "apikey": self.api_key, "output": "json"}
        if extra:
            params.update(extra)
        try:
            r = await client.get(f"{self.base}/api", params=params)
            if r.status_code < 400:
                return True, r.text.strip()
            return False, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)

    async def get_version(self) -> tuple[bool, str]:
        return await self._get("version")

    async def pause(self) -> tuple[bool, str]:
        ok, msg = await self._get("pause")
        return ok, "Paused" if ok else msg

    async def resume(self) -> tuple[bool, str]:
        ok, msg = await self._get("resume")
        return ok, "Resumed" if ok else msg

    async def set_speed_limit(self, percent: int) -> tuple[bool, str]:
        ok, msg = await self._get("config", {"section": "misc", "keyword": "bandwidth_perc", "value": str(percent)})
        return ok, f"Speed limit set to {percent}%" if ok else msg

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
