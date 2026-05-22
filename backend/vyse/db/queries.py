"""Analytics aggregation queries."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from vyse.db.models import IncidentORM


async def list_incidents(
    session: AsyncSession,
    limit: int = 50,
    offset: int = 0,
    severity_gte: int | None = None,
    incident_type: str | None = None,
    zone: str | None = None,
    camera_id: str | None = None,
    acknowledged: bool | None = None,
) -> list[IncidentORM]:
    stmt = select(IncidentORM).order_by(desc(IncidentORM.created_at)).limit(limit).offset(offset)
    if severity_gte is not None:
        stmt = stmt.where(IncidentORM.severity >= severity_gte)
    if incident_type:
        stmt = stmt.where(IncidentORM.incident_type == incident_type)
    if zone:
        stmt = stmt.where(IncidentORM.zone == zone)
    if camera_id:
        stmt = stmt.where(IncidentORM.camera_id == camera_id)
    if acknowledged is not None:
        stmt = stmt.where(IncidentORM.acknowledged == acknowledged)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def incident_by_id(session: AsyncSession, incident_id: str) -> IncidentORM | None:
    result = await session.execute(select(IncidentORM).where(IncidentORM.id == incident_id))
    return result.scalar_one_or_none()


async def severity_summary(session: AsyncSession, since: datetime | None = None) -> dict[str, int]:
    cutoff = since or datetime.now(UTC) - timedelta(days=1)
    stmt = (
        select(IncidentORM.severity, func.count(IncidentORM.id))
        .where(IncidentORM.created_at >= cutoff)
        .group_by(IncidentORM.severity)
    )
    rows = (await session.execute(stmt)).all()
    return {str(sev): cnt for sev, cnt in rows}


async def zone_breakdown(session: AsyncSession, since: datetime | None = None) -> list[dict]:
    cutoff = since or datetime.now(UTC) - timedelta(days=7)
    stmt = (
        select(IncidentORM.zone, IncidentORM.severity, func.count(IncidentORM.id))
        .where(IncidentORM.created_at >= cutoff)
        .group_by(IncidentORM.zone, IncidentORM.severity)
    )
    rows = (await session.execute(stmt)).all()
    return [{"zone": z, "severity": s, "count": c} for z, s, c in rows]


async def hourly_trend(session: AsyncSession, since: datetime | None = None) -> list[dict]:
    cutoff = since or datetime.now(UTC) - timedelta(days=7)
    stmt = (
        select(
            func.strftime("%Y-%m-%dT%H:00:00", IncidentORM.created_at).label("hour"),
            func.count(IncidentORM.id),
        )
        .where(IncidentORM.created_at >= cutoff)
        .group_by("hour")
        .order_by("hour")
    )
    rows = (await session.execute(stmt)).all()
    return [{"hour": h, "count": c} for h, c in rows]
