"""Authentication: session tokens + first-run setup flow."""
import secrets
import time
from typing import Optional

import bcrypt
from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse

from .config import SESSION_IDLE_TIMEOUT
from .db import delete_setting, get_setting, set_setting

# bcrypt only hashes the first 72 bytes; truncate to match the algorithm.
_BCRYPT_MAX_BYTES = 72


def _enc(password: str) -> bytes:
    return password.encode("utf-8")[:_BCRYPT_MAX_BYTES]

_sessions: dict[str, float] = {}  # token -> last-seen epoch


# ---------------------------------------------------------------------------
# Setup-state helpers
# ---------------------------------------------------------------------------
def is_setup_done() -> bool:
    return bool(get_setting("admin_password_hash"))


def set_admin_password(password: str):
    hashed = bcrypt.hashpw(_enc(password), bcrypt.gensalt()).decode("utf-8")
    set_setting("admin_password_hash", hashed)


def verify_admin_password(password: str) -> bool:
    h = get_setting("admin_password_hash")
    if not h:
        return False
    try:
        return bcrypt.checkpw(_enc(password), h.encode("utf-8"))
    except Exception:
        return False


def reset_admin_password():
    delete_setting("admin_password_hash")
    _sessions.clear()


# ---------------------------------------------------------------------------
# Session tokens
# ---------------------------------------------------------------------------
def create_session() -> str:
    _prune_sessions()
    token = secrets.token_urlsafe(32)
    _sessions[token] = time.time()
    return token


def destroy_session(token: Optional[str]):
    if token:
        _sessions.pop(token, None)


def is_session_valid(token: Optional[str]) -> bool:
    if not token:
        return False
    last = _sessions.get(token)
    if last is None:
        return False
    now = time.time()
    if now - last > SESSION_IDLE_TIMEOUT:
        _sessions.pop(token, None)
        return False
    _sessions[token] = now
    return True


def _prune_sessions():
    cutoff = time.time() - SESSION_IDLE_TIMEOUT
    stale = [t for t, ts in _sessions.items() if ts < cutoff]
    for t in stale:
        _sessions.pop(t, None)


# ---------------------------------------------------------------------------
# FastAPI dependencies
# ---------------------------------------------------------------------------
def require_auth(request: Request):
    if not is_session_valid(request.cookies.get("session")):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return True


def require_auth_redirect(request: Request):
    if not is_setup_done():
        return RedirectResponse("/setup", status_code=302)
    if not is_session_valid(request.cookies.get("session")):
        return RedirectResponse("/login", status_code=302)
    return None
