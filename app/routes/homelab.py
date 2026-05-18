"""Settings and test endpoints for Home Assistant, Proxmox, Sonarr, and Radarr."""
from fastapi import APIRouter, Depends

from ..auth import require_auth
from ..db import get_setting, set_setting
from ..models import HomeAssistantSettingsIn, ProxmoxSettingsIn, RadarrSettingsIn, SonarrSettingsIn

router = APIRouter()


# ---- Home Assistant ---------------------------------------------------------

@router.get("/api/ha-settings")
async def get_ha_settings(_: bool = Depends(require_auth)):
    return {
        "ha_url":       get_setting("ha_url", ""),
        "ha_token_set": bool(get_setting("ha_token")),
    }


@router.post("/api/ha-settings")
async def save_ha_settings(payload: HomeAssistantSettingsIn, _: bool = Depends(require_auth)):
    set_setting("ha_url", payload.ha_url.strip())
    if payload.ha_token:
        set_setting("ha_token", payload.ha_token.strip())
    return {"ok": True}


@router.post("/api/test-ha")
async def test_ha(_: bool = Depends(require_auth)):
    from ..homeassistant import HomeAssistantClient
    url   = get_setting("ha_url", "")
    token = get_setting("ha_token", "")
    if not (url and token):
        return {"ok": False, "error": "Home Assistant not configured"}
    client = HomeAssistantClient(url, token)
    try:
        ok, msg = await client.get_version()
        return {"ok": ok, "error": None if ok else msg}
    finally:
        await client.close()


# ---- Proxmox ----------------------------------------------------------------

@router.get("/api/proxmox-settings")
async def get_proxmox_settings(_: bool = Depends(require_auth)):
    return {
        "proxmox_url":           get_setting("proxmox_url", ""),
        "proxmox_username":      get_setting("proxmox_username", ""),
        "proxmox_password_set":  bool(get_setting("proxmox_password")),
        "proxmox_node":          get_setting("proxmox_node", "pve"),
    }


@router.post("/api/proxmox-settings")
async def save_proxmox_settings(payload: ProxmoxSettingsIn, _: bool = Depends(require_auth)):
    set_setting("proxmox_url",      payload.proxmox_url.strip())
    set_setting("proxmox_username", payload.proxmox_username.strip())
    set_setting("proxmox_node",     payload.proxmox_node.strip() or "pve")
    if payload.proxmox_password:
        set_setting("proxmox_password", payload.proxmox_password)
    return {"ok": True}


@router.post("/api/test-proxmox")
async def test_proxmox(_: bool = Depends(require_auth)):
    from ..proxmox import ProxmoxClient
    url  = get_setting("proxmox_url", "")
    user = get_setting("proxmox_username", "")
    pw   = get_setting("proxmox_password", "")
    node = get_setting("proxmox_node", "pve")
    if not (url and user):
        return {"ok": False, "error": "Proxmox not configured"}
    client = ProxmoxClient(url, user, pw or "", node)
    try:
        ok, msg = await client.get_nodes()
        return {"ok": ok, "error": None if ok else msg}
    finally:
        await client.close()


# ---- Sonarr -----------------------------------------------------------------

@router.get("/api/sonarr-settings")
async def get_sonarr_settings(_: bool = Depends(require_auth)):
    return {
        "sonarr_url":         get_setting("sonarr_url", ""),
        "sonarr_api_key_set": bool(get_setting("sonarr_api_key")),
    }


@router.post("/api/sonarr-settings")
async def save_sonarr_settings(payload: SonarrSettingsIn, _: bool = Depends(require_auth)):
    set_setting("sonarr_url", payload.sonarr_url.strip())
    if payload.sonarr_api_key:
        set_setting("sonarr_api_key", payload.sonarr_api_key.strip())
    return {"ok": True}


@router.post("/api/test-sonarr")
async def test_sonarr(_: bool = Depends(require_auth)):
    from ..sonarr import SonarrClient
    url     = get_setting("sonarr_url", "")
    api_key = get_setting("sonarr_api_key", "")
    if not (url and api_key):
        return {"ok": False, "error": "Sonarr not configured"}
    client = SonarrClient(url, api_key)
    try:
        ok, msg = await client.get_status()
        return {"ok": ok, "error": None if ok else msg}
    finally:
        await client.close()


# ---- Radarr -----------------------------------------------------------------

@router.get("/api/radarr-settings")
async def get_radarr_settings(_: bool = Depends(require_auth)):
    return {
        "radarr_url":         get_setting("radarr_url", ""),
        "radarr_api_key_set": bool(get_setting("radarr_api_key")),
    }


@router.post("/api/radarr-settings")
async def save_radarr_settings(payload: RadarrSettingsIn, _: bool = Depends(require_auth)):
    set_setting("radarr_url", payload.radarr_url.strip())
    if payload.radarr_api_key:
        set_setting("radarr_api_key", payload.radarr_api_key.strip())
    return {"ok": True}


@router.post("/api/test-radarr")
async def test_radarr(_: bool = Depends(require_auth)):
    from ..radarr import RadarrClient
    url     = get_setting("radarr_url", "")
    api_key = get_setting("radarr_api_key", "")
    if not (url and api_key):
        return {"ok": False, "error": "Radarr not configured"}
    client = RadarrClient(url, api_key)
    try:
        ok, msg = await client.get_status()
        return {"ok": ok, "error": None if ok else msg}
    finally:
        await client.close()
