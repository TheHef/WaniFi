"""Settings and test endpoints for Discord, Telegram, and Pushover."""
from fastapi import APIRouter, Depends

from ..auth import require_auth
from ..db import get_setting, set_setting
from ..models import DiscordSettingsIn, PushoverSettingsIn, TelegramSettingsIn
from ..notify import test_discord, test_pushover, test_telegram

router = APIRouter()


# ---- Discord ----------------------------------------------------------------

@router.get("/api/discord-settings")
async def get_discord_settings(_: bool = Depends(require_auth)):
    return {
        "discord_webhook_url":     "",
        "discord_webhook_url_set": bool(get_setting("discord_webhook_url")),
    }


@router.post("/api/discord-settings")
async def save_discord_settings(payload: DiscordSettingsIn, _: bool = Depends(require_auth)):
    if payload.discord_webhook_url:
        set_setting("discord_webhook_url", payload.discord_webhook_url.strip())
    return {"ok": True}


@router.post("/api/test-discord")
async def test_discord_endpoint(_: bool = Depends(require_auth)):
    ok, err = await test_discord()
    return {"ok": ok, "error": err if not ok else None}


# ---- Telegram ---------------------------------------------------------------

@router.get("/api/telegram-settings")
async def get_telegram_settings(_: bool = Depends(require_auth)):
    return {
        "telegram_bot_token":     "",
        "telegram_bot_token_set": bool(get_setting("telegram_bot_token")),
        "telegram_chat_id":       get_setting("telegram_chat_id", ""),
    }


@router.post("/api/telegram-settings")
async def save_telegram_settings(payload: TelegramSettingsIn, _: bool = Depends(require_auth)):
    if payload.telegram_bot_token:
        set_setting("telegram_bot_token", payload.telegram_bot_token.strip())
    set_setting("telegram_chat_id", payload.telegram_chat_id.strip())
    return {"ok": True}


@router.post("/api/test-telegram")
async def test_telegram_endpoint(_: bool = Depends(require_auth)):
    ok, err = await test_telegram()
    return {"ok": ok, "error": err if not ok else None}


# ---- Pushover ---------------------------------------------------------------

@router.get("/api/pushover-settings")
async def get_pushover_settings(_: bool = Depends(require_auth)):
    return {
        "pushover_app_token":     "",
        "pushover_app_token_set": bool(get_setting("pushover_app_token")),
        "pushover_user_key":      get_setting("pushover_user_key", ""),
    }


@router.post("/api/pushover-settings")
async def save_pushover_settings(payload: PushoverSettingsIn, _: bool = Depends(require_auth)):
    if payload.pushover_app_token:
        set_setting("pushover_app_token", payload.pushover_app_token.strip())
    if payload.pushover_user_key:
        set_setting("pushover_user_key", payload.pushover_user_key.strip())
    return {"ok": True}


@router.post("/api/test-pushover")
async def test_pushover_endpoint(_: bool = Depends(require_auth)):
    ok, err = await test_pushover()
    return {"ok": ok, "error": err if not ok else None}
