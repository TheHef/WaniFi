"""Unraid API client (v6.12+ with API key)."""
import httpx
from typing import Optional


class UnraidClient:
    def __init__(self, url: str, api_key: str):
        self.base    = url.rstrip("/")
        self.api_key = api_key
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=15, verify=False,
                headers={"x-api-key": self.api_key},
            )
        return self._client

    async def _gql(self, query: str, variables: Optional[dict] = None) -> tuple[bool, dict]:
        client = await self._get_client()
        try:
            r = await client.post(
                f"{self.base}/graphql",
                json={"query": query, "variables": variables or {}},
            )
            if r.status_code >= 400:
                return False, {"error": f"HTTP {r.status_code}"}
            data = r.json()
            if "errors" in data:
                return False, {"error": data["errors"][0].get("message", "GraphQL error")}
            return True, data.get("data", {})
        except Exception as e:
            return False, {"error": str(e)}

    async def get_info(self) -> tuple[bool, str]:
        ok, data = await self._gql("{ info { os { version } } }")
        if ok:
            return True, str(data.get("info", {}).get("os", {}).get("version", "ok"))
        return False, data.get("error", "unknown error")

    async def vm_action(self, vm_name: str, action: str) -> tuple[bool, str]:
        mutations = {
            "start":  "mutation($name: String!) { startVM(name: $name) }",
            "stop":   "mutation($name: String!) { stopVM(name: $name) }",
            "pause":  "mutation($name: String!) { pauseVM(name: $name) }",
            "resume": "mutation($name: String!) { resumeVM(name: $name) }",
        }
        if action not in mutations:
            return False, f"Unknown action: {action}"
        ok, data = await self._gql(mutations[action], {"name": vm_name})
        if ok:
            return True, f"VM '{vm_name}' {action}ed"
        return False, data.get("error", "unknown error")

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
