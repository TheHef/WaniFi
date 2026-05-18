"""Pydantic request models and shared validation constants."""
from typing import Optional

from pydantic import BaseModel, Field

from .config import POLL_INTERVAL_DEFAULT

VALID_TRIGGERS             = ("failover", "restored", "down", "high_latency")
VALID_ACTIONS              = ("stop", "start", "restart", "pause", "unpause")
VALID_QB_ACTIONS           = ("alt_speed_on", "alt_speed_off", "set_dl_limit", "set_ul_limit", "pause_all", "resume_all")
VALID_EMBY_ACTIONS         = ("set_bitrate_limit", "clear_bitrate_limit", "stop_all_sessions")
VALID_JELLYFIN_ACTIONS     = ("set_bitrate_limit", "clear_bitrate_limit", "stop_all_sessions")
VALID_PLEX_ACTIONS         = ("set_wan_bitrate", "clear_wan_bitrate", "stop_all_streams")


class SetupIn(BaseModel):
    password: str = Field(min_length=8, max_length=256)


class SettingsIn(BaseModel):
    unifi_host: str
    unifi_api_key: Optional[str] = None
    unifi_site: str = "default"
    primary_wan: str
    failover_wan: str
    primary_wan_name: str = ""
    failover_wan_name: str = ""
    poll_interval: int = POLL_INTERVAL_DEFAULT
    event_retention_days: int = 30
    latency_threshold_ms: int = 0
    latency_cooldown_min: int = 5


class RuleIn(BaseModel):
    rule_type: str = "docker"
    name: str = ""
    container: str = ""
    action: str = ""
    command: str = ""
    trigger: str
    enabled: bool = True


class NotifySettingsIn(BaseModel):
    ntfy_url: str = ""
    ntfy_topic: str = ""
    ntfy_token: Optional[str] = None
    ntfy_on_failover: bool = True
    ntfy_on_restored: bool = True
    ntfy_on_error: bool = False
    ntfy_on_high_latency: bool = False


class QbSettingsIn(BaseModel):
    qb_url: str = ""
    qb_username: str = ""
    qb_password: Optional[str] = None


class EmbySettingsIn(BaseModel):
    emby_url: str = ""
    emby_token: Optional[str] = None


class JellyfinSettingsIn(BaseModel):
    jellyfin_url: str = ""
    jellyfin_token: Optional[str] = None


class PlexSettingsIn(BaseModel):
    plex_url: str = ""
    plex_token: Optional[str] = None
