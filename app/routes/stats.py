"""Failover statistics endpoint."""
from fastapi import APIRouter, Depends

from ..auth import require_auth
from ..db import db

router = APIRouter()


@router.get("/api/stats")
async def get_stats(_: bool = Depends(require_auth)):
    with db() as conn:
        rows = conn.execute(
            """SELECT ts, message FROM events
               WHERE message LIKE '%-> failover%'
                  OR message LIKE '%-> primary%'
                  OR message LIKE '%-> down%'
               ORDER BY ts DESC LIMIT 50"""
        ).fetchall()

    events = [{"type": _classify(r["message"]), "ts": r["ts"]} for r in rows]
    failovers = [e for e in events if e["type"] == "failover"]

    last_failover  = failovers[0]["ts"] if failovers else None
    restored_events = [e for e in events if e["type"] == "restored"]
    last_restored  = restored_events[0]["ts"] if restored_events else None

    return {
        "total_failovers": len(failovers),
        "last_failover":   last_failover,
        "last_restored":   last_restored,
        "recent_events":   events[:10],
    }


def _classify(message: str) -> str:
    if "-> failover" in message:
        return "failover"
    if "-> primary" in message:
        return "restored"
    return "down"
