"""Plex settings and test endpoint."""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from ..auth import require_auth
from ..db import get_setting, set_setting
from ..plex import PlexClient
from ..models import PlexSettingsIn

router = APIRouter(prefix="/api/plex-settings")
test_router = APIRouter()


@router.get("")
async def get_plex_settings(_: bool = Depends(require_auth)):
    return {
        "plex_url":       get_setting("plex_url", ""),
        "plex_token_set": bool(get_setting("plex_token")),
    }


@router.post("")
async def save_plex_settings(payload: PlexSettingsIn, _: bool = Depends(require_auth)):
    set_setting("plex_url", payload.plex_url.strip())
    if payload.plex_token:
        set_setting("plex_token", payload.plex_token.strip())
    return {"ok": True}


@test_router.post("/api/test-plex")
async def api_test_plex(_: bool = Depends(require_auth)):
    url   = get_setting("plex_url", "")
    token = get_setting("plex_token", "")
    if not (url and token):
        return JSONResponse(
            {"ok": False, "error": "Plex URL and token required"},
            status_code=400,
        )
    client = PlexClient(url, token)
    try:
        ok, msg = await client.test()
        if ok:
            return {"ok": True, "message": msg}
        return JSONResponse({"ok": False, "error": msg}, status_code=400)
    finally:
        await client.close()
