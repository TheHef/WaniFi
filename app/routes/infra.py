"""Settings and test endpoints for Seerr, Portainer, TrueNAS, Unraid, and Node-RED."""
from fastapi import APIRouter, Depends

from ..auth import require_auth
from ..db import get_setting, set_setting
from ..models import (
    NodeRedSettingsIn,
    PortainerSettingsIn,
    SeerrSettingsIn,
    TrueNASSettingsIn,
    UnraidSettingsIn,
)

router = APIRouter()


# ---- Seerr ------------------------------------------------------------------

@router.get("/api/seerr-settings")
async def get_seerr_settings(_: bool = Depends(require_auth)):
    return {
        "seerr_url":         get_setting("seerr_url", ""),
        "seerr_api_key_set": bool(get_setting("seerr_api_key")),
    }


@router.post("/api/seerr-settings")
async def save_seerr_settings(payload: SeerrSettingsIn, _: bool = Depends(require_auth)):
    set_setting("seerr_url", payload.seerr_url.strip())
    if payload.seerr_api_key:
        set_setting("seerr_api_key", payload.seerr_api_key.strip())
    return {"ok": True}


@router.post("/api/test-seerr")
async def test_seerr(_: bool = Depends(require_auth)):
    from ..seerr import SeerrClient
    url     = get_setting("seerr_url", "")
    api_key = get_setting("seerr_api_key", "")
    if not (url and api_key):
        return {"ok": False, "error": "Seerr not configured"}
    client = SeerrClient(url, api_key)
    try:
        ok, msg = await client.get_status()
        return {"ok": ok, "error": None if ok else msg}
    finally:
        await client.close()


# ---- Portainer --------------------------------------------------------------

@router.get("/api/portainer-settings")
async def get_portainer_settings(_: bool = Depends(require_auth)):
    return {
        "portainer_url":       get_setting("portainer_url", ""),
        "portainer_token_set": bool(get_setting("portainer_token")),
        "portainer_env_id":    get_setting("portainer_env_id", "1"),
    }


@router.post("/api/portainer-settings")
async def save_portainer_settings(payload: PortainerSettingsIn, _: bool = Depends(require_auth)):
    set_setting("portainer_url",    payload.portainer_url.strip())
    set_setting("portainer_env_id", payload.portainer_env_id.strip() or "1")
    if payload.portainer_token:
        set_setting("portainer_token", payload.portainer_token.strip())
    return {"ok": True}


@router.post("/api/test-portainer")
async def test_portainer(_: bool = Depends(require_auth)):
    from ..portainer import PortainerClient
    url    = get_setting("portainer_url", "")
    token  = get_setting("portainer_token", "")
    env_id = get_setting("portainer_env_id", "1")
    if not (url and token):
        return {"ok": False, "error": "Portainer not configured"}
    client = PortainerClient(url, token, env_id)
    try:
        ok, msg = await client.get_endpoints()
        return {"ok": ok, "error": None if ok else msg}
    finally:
        await client.close()


# ---- TrueNAS ----------------------------------------------------------------

@router.get("/api/truenas-settings")
async def get_truenas_settings(_: bool = Depends(require_auth)):
    return {
        "truenas_url":         get_setting("truenas_url", ""),
        "truenas_api_key_set": bool(get_setting("truenas_api_key")),
    }


@router.post("/api/truenas-settings")
async def save_truenas_settings(payload: TrueNASSettingsIn, _: bool = Depends(require_auth)):
    set_setting("truenas_url", payload.truenas_url.strip())
    if payload.truenas_api_key:
        set_setting("truenas_api_key", payload.truenas_api_key.strip())
    return {"ok": True}


@router.post("/api/test-truenas")
async def test_truenas(_: bool = Depends(require_auth)):
    from ..truenas import TrueNASClient
    url     = get_setting("truenas_url", "")
    api_key = get_setting("truenas_api_key", "")
    if not (url and api_key):
        return {"ok": False, "error": "TrueNAS not configured"}
    client = TrueNASClient(url, api_key)
    try:
        ok, msg = await client.get_system_info()
        return {"ok": ok, "error": None if ok else msg}
    finally:
        await client.close()


# ---- Unraid -----------------------------------------------------------------

@router.get("/api/unraid-settings")
async def get_unraid_settings(_: bool = Depends(require_auth)):
    return {
        "unraid_url":         get_setting("unraid_url", ""),
        "unraid_api_key_set": bool(get_setting("unraid_api_key")),
    }


@router.post("/api/unraid-settings")
async def save_unraid_settings(payload: UnraidSettingsIn, _: bool = Depends(require_auth)):
    set_setting("unraid_url", payload.unraid_url.strip())
    if payload.unraid_api_key:
        set_setting("unraid_api_key", payload.unraid_api_key.strip())
    return {"ok": True}


@router.post("/api/test-unraid")
async def test_unraid(_: bool = Depends(require_auth)):
    from ..unraid import UnraidClient
    url     = get_setting("unraid_url", "")
    api_key = get_setting("unraid_api_key", "")
    if not (url and api_key):
        return {"ok": False, "error": "Unraid not configured"}
    client = UnraidClient(url, api_key)
    try:
        ok, msg = await client.get_info()
        return {"ok": ok, "error": None if ok else msg}
    finally:
        await client.close()


# ---- Node-RED ---------------------------------------------------------------

@router.get("/api/nodered-settings")
async def get_nodered_settings(_: bool = Depends(require_auth)):
    return {
        "nodered_url":          get_setting("nodered_url", ""),
        "nodered_username":     get_setting("nodered_username", ""),
        "nodered_password_set": bool(get_setting("nodered_password")),
    }


@router.post("/api/nodered-settings")
async def save_nodered_settings(payload: NodeRedSettingsIn, _: bool = Depends(require_auth)):
    set_setting("nodered_url",      payload.nodered_url.strip())
    set_setting("nodered_username", payload.nodered_username.strip())
    if payload.nodered_password:
        set_setting("nodered_password", payload.nodered_password)
    return {"ok": True}


@router.post("/api/test-nodered")
async def test_nodered(_: bool = Depends(require_auth)):
    from ..nodered import NodeRedClient
    url  = get_setting("nodered_url", "")
    user = get_setting("nodered_username", "")
    pw   = get_setting("nodered_password", "")
    if not url:
        return {"ok": False, "error": "Node-RED not configured"}
    client = NodeRedClient(url, user, pw or "")
    try:
        ok, msg = await client.get_settings()
        return {"ok": ok, "error": None if ok else msg}
    finally:
        await client.close()
