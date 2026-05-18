"""Proxmox VE API client."""
import httpx
from typing import Optional


class ProxmoxClient:
    def __init__(self, url: str, username: str, password: str, node: str = "pve"):
        self.base     = url.rstrip("/")
        self.username = username
        self.password = password
        self.node     = node
        self._ticket: Optional[str] = None
        self._csrf:   Optional[str] = None
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=10, verify=False)
        return self._client

    async def _auth(self) -> tuple[bool, str]:
        client = await self._get_client()
        try:
            r = await client.post(
                f"{self.base}/api2/json/access/ticket",
                data={"username": self.username, "password": self.password},
            )
            if r.status_code < 400:
                data = r.json().get("data", {})
                self._ticket = data.get("ticket")
                self._csrf   = data.get("CSRFPreventionToken")
                return True, "ok"
            return False, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)

    def _headers(self) -> dict:
        h = {}
        if self._csrf:
            h["CSRFPreventionToken"] = self._csrf
        return h

    def _cookies(self) -> dict:
        return {"PVEAuthCookie": self._ticket} if self._ticket else {}

    async def get_nodes(self) -> tuple[bool, str]:
        if not self._ticket:
            ok, err = await self._auth()
            if not ok:
                return False, err
        client = await self._get_client()
        try:
            r = await client.get(
                f"{self.base}/api2/json/nodes",
                headers=self._headers(),
                cookies=self._cookies(),
            )
            if r.status_code < 400:
                nodes = [n["node"] for n in r.json().get("data", [])]
                return True, f"Nodes: {', '.join(nodes)}"
            return False, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)

    async def vm_action(self, node: str, vmid: str, action: str) -> tuple[bool, str]:
        if not self._ticket:
            ok, err = await self._auth()
            if not ok:
                return False, err
        client = await self._get_client()
        try:
            r = await client.post(
                f"{self.base}/api2/json/nodes/{node}/qemu/{vmid}/status/{action}",
                headers=self._headers(),
                cookies=self._cookies(),
            )
            if r.status_code < 400:
                return True, f"VM {vmid} {action} on node {node}"
            return False, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
