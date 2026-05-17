"""Event log routes."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from ..auth import require_auth
from ..db import db, log_event

router = APIRouter(prefix="/api/events")


@router.get("")
async def list_events(limit: int = 500, _: bool = Depends(require_auth)):
    limit = max(1, min(limit, 5000))
    with db() as conn:
        rows = conn.execute(
            "SELECT id, ts, level, message FROM events ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return {"events": [
        {
            "id": r["id"],
            "ts": datetime.fromtimestamp(r["ts"], tz=timezone.utc).isoformat(),
            "level": r["level"],
            "message": r["message"],
        }
        for r in rows
    ]}


@router.delete("/{event_id}")
async def delete_event(event_id: int, _: bool = Depends(require_auth)):
    with db() as conn:
        conn.execute("DELETE FROM events WHERE id=?", (event_id,))
    return {"ok": True}


@router.delete("")
async def clear_events(_: bool = Depends(require_auth)):
    with db() as conn:
        n = conn.execute("DELETE FROM events").rowcount
    log_event("info", f"Events cleared ({n} deleted)")
    return {"ok": True, "deleted": n}
