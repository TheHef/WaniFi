"""Settings and test endpoints for Pi-hole and AdGuard Home."""
from fastapi import APIRouter, Depends

from ..auth import require_auth
from ..db import get_setting, set_setting
from ..models import AdGuardSettingsIn, PiholeSettingsIn

router = APIRouter()


# ---- Pi-hole ----------------------------------------------------------------

@router.get("/api/pihole-settings")
async def get_pihole_settings(_: bool = Depends(require_auth)):
    return {
        "pihole_url":       get_setting("pihole_url", ""),
        "pihole_token_set": bool(get_setting("pihole_token")),
    }


@router.post("/api/pihole-settings")
async def save_pihole_settings(payload: PiholeSettingsIn, _: bool = Depends(require_auth)):
    set_setting("pihole_url", payload.pihole_url.strip())
    if payload.pihole_token:
        set_setting("pihole_token", payload.pihole_token.strip())
    return {"ok": True}


@router.post("/api/test-pihole")
async def test_pihole(_: bool = Depends(require_auth)):
    from ..pihole import PiholeClient
    url   = get_setting("pihole_url", "")
    token = get_setting("pihole_token", "")
    if not url:
        return {"ok": False, "error": "Pi-hole not configured"}
    client = PiholeClient(url, token or "")
    try:
        ok, msg = await client.get_summary()
        return {"ok": ok, "error": None if ok else msg}
    finally:
        await client.close()


# ---- AdGuard Home -----------------------------------------------------------

@router.get("/api/adguard-settings")
async def get_adguard_settings(_: bool = Depends(require_auth)):
    return {
        "adguard_url":          get_setting("adguard_url", ""),
        "adguard_username":     get_setting("adguard_username", ""),
        "adguard_password_set": bool(get_setting("adguard_password")),
    }


@router.post("/api/adguard-settings")
async def save_adguard_settings(payload: AdGuardSettingsIn, _: bool = Depends(require_auth)):
    set_setting("adguard_url",      payload.adguard_url.strip())
    set_setting("adguard_username", payload.adguard_username.strip())
    if payload.adguard_password:
        set_setting("adguard_password", payload.adguard_password)
    return {"ok": True}


@router.post("/api/test-adguard")
async def test_adguard(_: bool = Depends(require_auth)):
    from ..adguard import AdGuardClient
    url  = get_setting("adguard_url", "")
    user = get_setting("adguard_username", "")
    pw   = get_setting("adguard_password", "")
    if not url:
        return {"ok": False, "error": "AdGuard not configured"}
    client = AdGuardClient(url, user, pw or "")
    try:
        ok, msg = await client.get_status()
        return {"ok": ok, "error": None if ok else msg}
    finally:
        await client.close()
