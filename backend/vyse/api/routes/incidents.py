"""Incidents CRUD + acknowledge endpoint."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Query

from vyse.db import queries
from vyse.db.session import session_scope

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.get("")
async def list_incidents(
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    severity_gte: int | None = None,
    incident_type: str | None = None,
    zone: str | None = None,
    camera_id: str | None = None,
    acknowledged: bool | None = None,
) -> dict:
    async with session_scope() as session:
        rows = await queries.list_incidents(
            session,
            limit=limit,
            offset=offset,
            severity_gte=severity_gte,
            incident_type=incident_type,
            zone=zone,
            camera_id=camera_id,
            acknowledged=acknowledged,
        )
    return {"items": [r.to_dict() for r in rows], "count": len(rows)}


@router.get("/{incident_id}")
async def get_incident(incident_id: str) -> dict:
    async with session_scope() as session:
        row = await queries.incident_by_id(session, incident_id)
    if row is None:
        raise HTTPException(status_code=404, detail="incident not found")
    return row.to_dict()


@router.post("/{incident_id}/acknowledge")
async def acknowledge(incident_id: str) -> dict:
    async with session_scope() as session:
        row = await queries.incident_by_id(session, incident_id)
        if row is None:
            raise HTTPException(status_code=404, detail="incident not found")
        row.acknowledged = True
        row.acknowledged_at = datetime.now(UTC)
        await session.commit()
    return {"ok": True, "acknowledged_at": row.acknowledged_at.isoformat()}
