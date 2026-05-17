"""Container listing and manual one-off actions."""
from fastapi import APIRouter, Depends, HTTPException

from ..auth import require_auth
from ..db import log_event
from ..docker_ops import VALID_ACTIONS, container_action, list_containers

router = APIRouter()


@router.get("/api/containers")
async def api_containers(_: bool = Depends(require_auth)):
    return {"containers": list_containers()}


@router.post("/api/manual/{action}/{container}")
async def api_manual(action: str, container: str, _: bool = Depends(require_auth)):
    if action not in VALID_ACTIONS:
        raise HTTPException(400, "Invalid action")
    ok, msg = container_action(container, action)
    log_event("info" if ok else "error", f"Manual {action} '{container}': {msg}")
    return {"ok": ok, "message": msg}
