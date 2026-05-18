"""Settings and test endpoints for SABnzbd, Transmission, and Deluge."""
from fastapi import APIRouter, Depends

from ..auth import require_auth
from ..db import get_setting, set_setting
from ..models import DelugeSettingsIn, NZBGetSettingsIn, SabnzbdSettingsIn, TransmissionSettingsIn

router = APIRouter()


# ---- SABnzbd ----------------------------------------------------------------

@router.get("/api/sabnzbd-settings")
async def get_sabnzbd_settings(_: bool = Depends(require_auth)):
    return {
        "sabnzbd_url":         get_setting("sabnzbd_url", ""),
        "sabnzbd_api_key_set": bool(get_setting("sabnzbd_api_key")),
    }


@router.post("/api/sabnzbd-settings")
async def save_sabnzbd_settings(payload: SabnzbdSettingsIn, _: bool = Depends(require_auth)):
    set_setting("sabnzbd_url", payload.sabnzbd_url.strip())
    if payload.sabnzbd_api_key:
        set_setting("sabnzbd_api_key", payload.sabnzbd_api_key.strip())
    return {"ok": True}


@router.post("/api/test-sabnzbd")
async def test_sabnzbd(_: bool = Depends(require_auth)):
    from ..sabnzbd import SabnzbdClient
    url     = get_setting("sabnzbd_url", "")
    api_key = get_setting("sabnzbd_api_key", "")
    if not (url and api_key):
        return {"ok": False, "error": "SABnzbd not configured"}
    client = SabnzbdClient(url, api_key)
    try:
        ok, msg = await client.get_version()
        return {"ok": ok, "error": None if ok else msg}
    finally:
        await client.close()


# ---- Transmission -----------------------------------------------------------

@router.get("/api/transmission-settings")
async def get_transmission_settings(_: bool = Depends(require_auth)):
    return {
        "transmission_url":           get_setting("transmission_url", ""),
        "transmission_username":      get_setting("transmission_username", ""),
        "transmission_password_set":  bool(get_setting("transmission_password")),
    }


@router.post("/api/transmission-settings")
async def save_transmission_settings(payload: TransmissionSettingsIn, _: bool = Depends(require_auth)):
    set_setting("transmission_url",      payload.transmission_url.strip())
    set_setting("transmission_username", payload.transmission_username.strip())
    if payload.transmission_password:
        set_setting("transmission_password", payload.transmission_password)
    return {"ok": True}


@router.post("/api/test-transmission")
async def test_transmission(_: bool = Depends(require_auth)):
    from ..transmission import TransmissionClient
    url  = get_setting("transmission_url", "")
    user = get_setting("transmission_username", "")
    pw   = get_setting("transmission_password", "")
    if not url:
        return {"ok": False, "error": "Transmission not configured"}
    client = TransmissionClient(url, user, pw or "")
    try:
        ok, msg = await client.get_session()
        return {"ok": ok, "error": None if ok else msg}
    finally:
        await client.close()


# ---- Deluge -----------------------------------------------------------------

@router.get("/api/deluge-settings")
async def get_deluge_settings(_: bool = Depends(require_auth)):
    return {
        "deluge_url":          get_setting("deluge_url", ""),
        "deluge_password_set": bool(get_setting("deluge_password")),
    }


@router.post("/api/deluge-settings")
async def save_deluge_settings(payload: DelugeSettingsIn, _: bool = Depends(require_auth)):
    set_setting("deluge_url", payload.deluge_url.strip())
    if payload.deluge_password:
        set_setting("deluge_password", payload.deluge_password)
    return {"ok": True}


@router.post("/api/test-deluge")
async def test_deluge(_: bool = Depends(require_auth)):
    from ..deluge import DelugeClient
    url = get_setting("deluge_url", "")
    pw  = get_setting("deluge_password", "")
    if not url:
        return {"ok": False, "error": "Deluge not configured"}
    client = DelugeClient(url, pw or "")
    try:
        ok, msg = await client.login()
        return {"ok": ok, "error": None if ok else msg}
    finally:
        await client.close()


# ---- NZBGet -----------------------------------------------------------------

@router.get("/api/nzbget-settings")
async def get_nzbget_settings(_: bool = Depends(require_auth)):
    return {
        "nzbget_url":          get_setting("nzbget_url", ""),
        "nzbget_username":     get_setting("nzbget_username", ""),
        "nzbget_password_set": bool(get_setting("nzbget_password")),
    }


@router.post("/api/nzbget-settings")
async def save_nzbget_settings(payload: NZBGetSettingsIn, _: bool = Depends(require_auth)):
    set_setting("nzbget_url",      payload.nzbget_url.strip())
    set_setting("nzbget_username", payload.nzbget_username.strip())
    if payload.nzbget_password:
        set_setting("nzbget_password", payload.nzbget_password)
    return {"ok": True}


@router.post("/api/test-nzbget")
async def test_nzbget(_: bool = Depends(require_auth)):
    from ..nzbget import NZBGetClient
    url  = get_setting("nzbget_url", "")
    user = get_setting("nzbget_username", "")
    pw   = get_setting("nzbget_password", "")
    if not url:
        return {"ok": False, "error": "NZBGet not configured"}
    client = NZBGetClient(url, user, pw or "")
    try:
        ok, msg = await client.get_version()
        return {"ok": ok, "error": None if ok else msg}
    finally:
        await client.close()
