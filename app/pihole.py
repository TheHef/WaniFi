"""Pi-hole API client (supports v5 and v6)."""
import httpx
from typing import Optional


class PiholeClient:
    def __init__(self, url: str, token: str):
        self.base  = url.rstrip("/")
        self.token = token
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=10, verify=False)
        return self._client

    async def get_summary(self) -> tuple[bool, str]:
        client = await self._get_client()
        try:
            r = await client.get(
                f"{self.base}/admin/api.php",
                params={"auth": self.token, "summaryRaw": ""},
            )
            if r.status_code < 400:
                return True, "ok"
            return False, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)

    async def enable(self) -> tuple[bool, str]:
        client = await self._get_client()
        # Try v6 first
        try:
            r = await client.post(
                f"{self.base}/api/dns/blocking",
                json={"blocking": True},
                headers={"X-FTL-SID": self.token},
            )
            if r.status_code < 400:
                return True, "Pi-hole blocking enabled"
        except Exception:
            pass
        # Fallback to v5
        try:
            r = await client.get(
                f"{self.base}/admin/api.php",
                params={"auth": self.token, "enable": ""},
            )
            if r.status_code < 400:
                return True, "Pi-hole enabled"
            return False, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)

    async def disable(self) -> tuple[bool, str]:
        client = await self._get_client()
        # Try v6 first
        try:
            r = await client.post(
                f"{self.base}/api/dns/blocking",
                json={"blocking": False},
                headers={"X-FTL-SID": self.token},
            )
            if r.status_code < 400:
                return True, "Pi-hole blocking disabled"
        except Exception:
            pass
        # Fallback to v5
        try:
            r = await client.get(
                f"{self.base}/admin/api.php",
                params={"auth": self.token, "disable": ""},
            )
            if r.status_code < 400:
                return True, "Pi-hole disabled"
            return False, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
