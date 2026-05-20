"""In-memory registry of connected WaniFi agents."""
import asyncio
import json
import time
from typing import Optional

from fastapi import WebSocket

from .config import log

# api_key → {"ws": WebSocket, "name": str, "connected_at": int}
_agents: dict[str, dict] = {}


def register(api_key: str, name: str, ws: WebSocket):
    _agents[api_key] = {"ws": ws, "name": name, "connected_at": int(time.time())}
    log.info("Agent connected: %s", name)


def unregister(api_key: str):
    agent = _agents.pop(api_key, None)
    if agent:
        log.info("Agent disconnected: %s", agent["name"])


def online_keys() -> set[str]:
    return set(_agents.keys())


def is_online(api_key: str) -> bool:
    return api_key in _agents


async def send_command(api_key: str, command: dict) -> Optional[dict]:
    """Send a command to an agent and wait up to 30s for a result."""
    entry = _agents.get(api_key)
    if not entry:
        return {"ok": False, "error": "Agent not connected"}
    try:
        await entry["ws"].send_text(json.dumps(command))
        # Wait for response with timeout
        raw = await asyncio.wait_for(entry["ws"].receive_text(), timeout=30.0)
        return json.loads(raw)
    except asyncio.TimeoutError:
        return {"ok": False, "error": "Agent timed out"}
    except Exception as e:
        return {"ok": False, "error": str(e)}
