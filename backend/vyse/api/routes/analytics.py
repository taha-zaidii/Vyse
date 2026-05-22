"""Analytics aggregation endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from vyse.db import queries
from vyse.db.session import session_scope

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
async def summary() -> dict:
    async with session_scope() as session:
        sev = await queries.severity_summary(session)
    return {"severity_24h": sev}


@router.get("/zones")
async def zones() -> dict:
    async with session_scope() as session:
        rows = await queries.zone_breakdown(session)
    return {"items": rows}


@router.get("/trends")
async def trends() -> dict:
    async with session_scope() as session:
        rows = await queries.hourly_trend(session)
    return {"hourly": rows}
