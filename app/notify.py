"""ntfy push notification client."""
import httpx

from .config import NTFY_HTTP_TIMEOUT, log
from .db import get_setting


async def send_notification(
    title: str,
    message: str,
    priority: str = "default",
    tags: str = "",
) -> tuple[bool, str]:
    url_base = get_setting("ntfy_url", "")
    topic    = get_setting("ntfy_topic", "")
    token    = get_setting("ntfy_token", "")
    if not (url_base and topic):
        return False, "ntfy not configured"

    url = f"{url_base.rstrip('/')}/{topic}"
    headers: dict = {"Title": title, "Priority": priority}
    if tags:
        headers["Tags"] = tags
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        async with httpx.AsyncClient(timeout=NTFY_HTTP_TIMEOUT) as client:
            resp = await client.post(url, content=message.encode(), headers=headers)
            resp.raise_for_status()
        return True, "ok"
    except Exception as e:
        log.warning("ntfy notification failed: %s", e)
        return False, str(e)
