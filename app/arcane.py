"""Arcane (getarcaneapp/arcane) API client."""
import httpx
from typing import Optional


class ArcaneClient:
    def __init__(self, url: str, token: str, env_id: str = "0"):
        self.base   = url.rstrip("/")
        self.token  = token
        self.env_id = env_id or "0"
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=10, verify=False,
                headers={"X-API-Key": self.token},
            )
        return self._client

    async def test_connection(self) -> tuple[bool, str]:
        """Validate URL, API key and environment ID in one call."""
        client = await self._get_client()
        try:
            r = await client.get(f"{self.base}/api/environments/{self.env_id}/containers/counts")
            if r.status_code < 400:
                return True, "ok"
            return False, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e) or type(e).__name__

    async def container_action(self, container_name: str, action: str) -> tuple[bool, str]:
        """Start, stop, or restart a named container."""
        client = await self._get_client()
        try:
            r = await client.get(
                f"{self.base}/api/environments/{self.env_id}/containers",
                params={
                    "search": container_name, "limit": 100,
                    "includeInternal": "true", "includeHidden": "true",
                },
            )
            if r.status_code >= 400:
                return False, f"HTTP {r.status_code}"
            containers = r.json().get("data") or []
            container_id = None
            for c in containers:
                names = c.get("names") or []
                if any(n.strip("/") == container_name for n in names):
                    container_id = c["id"]
                    break
            if not container_id:
                return False, f"Container '{container_name}' not found"
            # stop/restart block until Docker's grace period (10s default) elapses
            r2 = await client.post(
                f"{self.base}/api/environments/{self.env_id}/containers/{container_id}/{action}",
                timeout=60,
            )
            if r2.status_code < 400:
                done = {"start": "started", "stop": "stopped", "restart": "restarted"}.get(action, action)
                return True, f"Container '{container_name}' {done}"
            return False, f"HTTP {r2.status_code}"
        except Exception as e:
            return False, str(e) or type(e).__name__

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
