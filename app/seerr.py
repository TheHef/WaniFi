"""Seerr (Overseerr / Jellyseerr) API client."""
import httpx
from typing import Optional


class SeerrClient:
    def __init__(self, url: str, api_key: str):
        self.base    = url.rstrip("/")
        self.api_key = api_key
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=10, verify=False,
                headers={"X-Api-Key": self.api_key},
            )
        return self._client

    async def get_status(self) -> tuple[bool, str]:
        client = await self._get_client()
        try:
            r = await client.get(f"{self.base}/api/v1/status")
            if r.status_code < 400:
                return True, r.json().get("version", "ok")
            return False, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)

    async def run_job(self, job_id: str) -> tuple[bool, str]:
        client = await self._get_client()
        try:
            r = await client.post(f"{self.base}/api/v1/jobs/{job_id}/run")
            if r.status_code < 400:
                return True, f"Job '{job_id}' triggered"
            return False, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)

    async def sync_radarr(self) -> tuple[bool, str]:
        return await self.run_job("radarr-scan")

    async def sync_sonarr(self) -> tuple[bool, str]:
        return await self.run_job("sonarr-scan")

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
