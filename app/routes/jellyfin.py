"""Jellyfin settings and test endpoint."""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from ..auth import require_auth
from ..db import get_setting, set_setting
from ..jellyfin import JellyfinClient
from ..models import JellyfinSettingsIn

router = APIRouter(prefix="/api/jellyfin-settings")
test_router = APIRouter()


@router.get("")
async def get_jellyfin_settings(_: bool = Depends(require_auth)):
    return {
        "jellyfin_url":       get_setting("jellyfin_url", ""),
        "jellyfin_token_set": bool(get_setting("jellyfin_token")),
    }


@router.post("")
async def save_jellyfin_settings(payload: JellyfinSettingsIn, _: bool = Depends(require_auth)):
    set_setting("jellyfin_url", payload.jellyfin_url.strip())
    if payload.jellyfin_token:
        set_setting("jellyfin_token", payload.jellyfin_token.strip())
    return {"ok": True}


@test_router.post("/api/test-jellyfin")
async def api_test_jellyfin(_: bool = Depends(require_auth)):
    url   = get_setting("jellyfin_url", "")
    token = get_setting("jellyfin_token", "")
    if not (url and token):
        return JSONResponse(
            {"ok": False, "error": "Jellyfin URL and API token required"},
            status_code=400,
        )
    client = JellyfinClient(url, token)
    try:
        ok, msg = await client.test()
        if ok:
            return {"ok": True, "message": msg}
        return JSONResponse({"ok": False, "error": msg}, status_code=400)
    finally:
        await client.close()
