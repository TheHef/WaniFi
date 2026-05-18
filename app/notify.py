"""Push notification dispatcher — ntfy, Discord, Telegram, Pushover."""
import httpx

from .config import NTFY_HTTP_TIMEOUT, log
from .db import get_setting


async def _send_ntfy(title: str, message: str, priority: str, tags: str) -> None:
    url_base = get_setting("ntfy_url", "")
    topic    = get_setting("ntfy_topic", "")
    token    = get_setting("ntfy_token", "")
    if not (url_base and topic):
        return
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
    except Exception as e:
        log.warning("ntfy notification failed: %s", e)


async def _send_discord(title: str, message: str) -> None:
    webhook_url = get_setting("discord_webhook_url", "")
    if not webhook_url:
        return
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(webhook_url, json={
                "username": "WaniFi",
                "content": f"**{title}**\n{message}",
            })
            resp.raise_for_status()
    except Exception as e:
        log.warning("Discord notification failed: %s", e)


async def _send_telegram(title: str, message: str) -> None:
    token   = get_setting("telegram_bot_token", "")
    chat_id = get_setting("telegram_chat_id", "")
    if not (token and chat_id):
        return
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": f"*{title}*\n{message}", "parse_mode": "Markdown"},
            )
            resp.raise_for_status()
    except Exception as e:
        log.warning("Telegram notification failed: %s", e)


async def _send_pushover(title: str, message: str) -> None:
    app_token = get_setting("pushover_app_token", "")
    user_key  = get_setting("pushover_user_key", "")
    if not (app_token and user_key):
        return
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://api.pushover.net/1/messages.json",
                json={"token": app_token, "user": user_key, "title": title, "message": message},
            )
            resp.raise_for_status()
    except Exception as e:
        log.warning("Pushover notification failed: %s", e)


async def send_notification(
    title: str,
    message: str,
    priority: str = "default",
    tags: str = "",
) -> tuple[bool, str]:
    """Dispatch to all enabled notification channels. Always returns (True, 'ok')
    unless ntfy is the only channel and it fails (for backwards-compat test endpoint)."""
    errors: list[str] = []

    if get_setting("integration_ntfy", "0") == "1":
        url_base = get_setting("ntfy_url", "")
        topic    = get_setting("ntfy_topic", "")
        token    = get_setting("ntfy_token", "")
        if url_base and topic:
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
            except Exception as e:
                log.warning("ntfy notification failed: %s", e)
                errors.append(str(e))

    if get_setting("integration_discord", "0") == "1":
        await _send_discord(title, message)

    if get_setting("integration_telegram", "0") == "1":
        await _send_telegram(title, message)

    if get_setting("integration_pushover", "0") == "1":
        await _send_pushover(title, message)

    return (False, errors[0]) if errors else (True, "ok")


async def test_ntfy() -> tuple[bool, str]:
    """Test ntfy specifically (for the test endpoint)."""
    url_base = get_setting("ntfy_url", "")
    topic    = get_setting("ntfy_topic", "")
    token    = get_setting("ntfy_token", "")
    if not (url_base and topic):
        return False, "ntfy not configured"
    url = f"{url_base.rstrip('/')}/{topic}"
    headers: dict = {"Title": "WaniFi Test", "Priority": "default"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        async with httpx.AsyncClient(timeout=NTFY_HTTP_TIMEOUT) as client:
            resp = await client.post(url, content=b"Test notification from WaniFi", headers=headers)
            resp.raise_for_status()
        return True, "ok"
    except Exception as e:
        return False, str(e)


async def test_discord() -> tuple[bool, str]:
    webhook_url = get_setting("discord_webhook_url", "")
    if not webhook_url:
        return False, "Discord not configured"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(webhook_url, json={
                "username": "WaniFi",
                "content": "**WaniFi Test**\nDiscord notifications are working.",
            })
            resp.raise_for_status()
        return True, "ok"
    except Exception as e:
        return False, str(e)


async def test_telegram() -> tuple[bool, str]:
    token   = get_setting("telegram_bot_token", "")
    chat_id = get_setting("telegram_chat_id", "")
    if not (token and chat_id):
        return False, "Telegram not configured"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": "*WaniFi Test*\nTelegram notifications are working.", "parse_mode": "Markdown"},
            )
            resp.raise_for_status()
        return True, "ok"
    except Exception as e:
        return False, str(e)


async def test_pushover() -> tuple[bool, str]:
    app_token = get_setting("pushover_app_token", "")
    user_key  = get_setting("pushover_user_key", "")
    if not (app_token and user_key):
        return False, "Pushover not configured"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://api.pushover.net/1/messages.json",
                json={"token": app_token, "user": user_key, "title": "WaniFi Test", "message": "Pushover notifications are working."},
            )
            resp.raise_for_status()
        return True, "ok"
    except Exception as e:
        return False, str(e)
