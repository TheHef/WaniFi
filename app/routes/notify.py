"""ntfy notification settings and test endpoint."""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from ..auth import require_auth
from ..db import get_setting, set_setting
from ..models import NotifySettingsIn
from ..notify import send_notification

router = APIRouter(prefix="/api/notify-settings")
test_router = APIRouter()


@router.get("")
async def get_notify_settings(_: bool = Depends(require_auth)):
    return {
        "ntfy_url":             get_setting("ntfy_url", ""),
        "ntfy_topic":           get_setting("ntfy_topic", ""),
        "ntfy_token_set":       bool(get_setting("ntfy_token")),
        "ntfy_on_failover":     get_setting("ntfy_on_failover", "1") == "1",
        "ntfy_on_restored":     get_setting("ntfy_on_restored", "1") == "1",
        "ntfy_on_error":        get_setting("ntfy_on_error", "0") == "1",
        "ntfy_on_high_latency": get_setting("ntfy_on_high_latency", "0") == "1",
    }


@router.post("")
async def save_notify_settings(payload: NotifySettingsIn, _: bool = Depends(require_auth)):
    set_setting("ntfy_url",   payload.ntfy_url.strip())
    set_setting("ntfy_topic", payload.ntfy_topic.strip())
    if payload.ntfy_token:
        set_setting("ntfy_token", payload.ntfy_token.strip())
    set_setting("ntfy_on_failover",     "1" if payload.ntfy_on_failover else "0")
    set_setting("ntfy_on_restored",     "1" if payload.ntfy_on_restored else "0")
    set_setting("ntfy_on_error",        "1" if payload.ntfy_on_error    else "0")
    set_setting("ntfy_on_high_latency", "1" if payload.ntfy_on_high_latency else "0")
    return {"ok": True}


@test_router.post("/api/test-notify")
async def api_test_notify(_: bool = Depends(require_auth)):
    ok, err = await send_notification(
        "WaniFi Test", "Notification test from WaniFi — it works!",
        priority="default", tags="bell",
    )
    if ok:
        return {"ok": True}
    return JSONResponse({"ok": False, "error": err}, status_code=400)
