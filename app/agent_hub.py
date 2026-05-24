"""In-memory registry of connected WaniFi agents."""
import asyncio
import json
import time
from typing import Optional

from fastapi import WebSocket

from .config import log

# api_key → {ws, name, connected_at, pending, caps}
# caps: {"docker": bool|None, "host_command": bool|None, "ip": str, "hostname": str, "version": str}
_agents: dict[str, dict] = {}


def register(api_key: str, name: str, ws: WebSocket, caps: dict | None = None):
    old = _agents.get(api_key)
    if old:
        fut: asyncio.Future | None = old.get("pending")
        if fut and not fut.done():
            fut.set_exception(RuntimeError("Agent reconnected — previous connection replaced"))
    _agents[api_key] = {
        "ws":           ws,
        "name":         name,
        "connected_at": int(time.time()),
        "pending":      None,
        "caps":         caps or {},
    }
    log.info("Agent connected: %s", name)


def get_agent_runtime(api_key: str) -> dict | None:
    """Return live runtime info for a connected agent, or None if offline."""
    entry = _agents.get(api_key)
    if not entry:
        return None
    return {
        "connected_at": entry["connected_at"],
        "caps":         entry.get("caps") or {},
    }


def unregister(api_key: str):
    agent = _agents.pop(api_key, None)
    if agent:
        log.info("Agent disconnected: %s", agent["name"])


def online_keys() -> set[str]:
    return set(_agents.keys())


def is_online(api_key: str) -> bool:
    return api_key in _agents


def deliver_response(api_key: str, raw: str):
    """Called by agent_ws when a message arrives — resolves pending send_command Future."""
    entry = _agents.get(api_key)
    if entry:
        fut: asyncio.Future | None = entry.get("pending")
        if fut and not fut.done():
            fut.set_result(raw)


async def send_command(api_key: str, command: dict) -> Optional[dict]:
    """Send a command to an agent and wait up to 30s for the response."""
    entry = _agents.get(api_key)
    if not entry:
        return {"ok": False, "error": "Agent not connected"}

    fut: asyncio.Future = asyncio.get_running_loop().create_future()
    entry["pending"] = fut
    try:
        await entry["ws"].send_text(json.dumps(command))
        raw = await asyncio.wait_for(asyncio.shield(fut), timeout=30.0)
        return json.loads(raw)
    except asyncio.TimeoutError:
        return {"ok": False, "error": "Agent timed out"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    finally:
        entry["pending"] = None
