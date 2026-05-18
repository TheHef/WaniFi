"""Node-RED API client."""
import httpx
from typing import Optional


class NodeRedClient:
    def __init__(self, url: str, username: str = "", password: str = ""):
        self.base     = url.rstrip("/")
        self.username = username
        self.password = password
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            auth = (self.username, self.password) if self.username else None
            self._client = httpx.AsyncClient(timeout=10, verify=False, auth=auth)
        return self._client

    async def get_settings(self) -> tuple[bool, str]:
        client = await self._get_client()
        try:
            r = await client.get(f"{self.base}/settings")
            if r.status_code < 400:
                return True, "ok"
            return False, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)

    async def trigger_flow(self, endpoint: str) -> tuple[bool, str]:
        """POST to a flow's HTTP-in endpoint path."""
        client = await self._get_client()
        path = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        try:
            r = await client.post(f"{self.base}{path}", json={"source": "wanifi"})
            if r.status_code < 400:
                return True, f"Flow triggered: {path}"
            return False, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
