"""Gotify push notification client."""
import httpx

from .config import log
from .db import get_setting


async def send_gotify(title: str, message: str, priority: int = 5) -> tuple[bool, str]:
    url   = get_setting("gotify_url", "")
    token = get_setting("gotify_token", "")
    if not (url and token):
        return False, "Gotify not configured"
    try:
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            resp = await client.post(
                f"{url.rstrip('/')}/message",
                headers={"X-Gotify-Key": token},
                json={"title": title, "message": message, "priority": priority},
            )
            resp.raise_for_status()
        return True, "ok"
    except Exception as e:
        log.warning("Gotify notification failed: %s", e)
        return False, str(e)
