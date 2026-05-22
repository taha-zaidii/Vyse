"""ORM mirrors of the in-memory dataclasses."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, SmallInteger, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from vyse.core.models import DispatchResult, Incident, Severity


class Base(DeclarativeBase):
    pass


class IncidentORM(Base):
    __tablename__ = "incidents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    camera_id: Mapped[str] = mapped_column(String(64), index=True)
    zone: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    incident_type: Mapped[str] = mapped_column(String(64), index=True)
    severity: Mapped[int] = mapped_column(SmallInteger, index=True)
    rule_id: Mapped[str] = mapped_column(String(64))
    confidence_avg: Mapped[float] = mapped_column(Float, default=0.0)
    trigger_event_count: Mapped[int] = mapped_column(Integer, default=0)
    track_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    frame_snapshot_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    acknowledged_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    meta_json: Mapped[dict] = mapped_column(JSON, default=dict)

    @classmethod
    def from_dataclass(cls, incident: Incident) -> IncidentORM:
        return cls(
            id=incident.incident_id,
            created_at=incident.created_at,
            camera_id=incident.camera_id,
            zone=incident.zone,
            incident_type=incident.incident_type,
            severity=int(incident.severity),
            rule_id=incident.rule_id,
            confidence_avg=incident.confidence_avg,
            trigger_event_count=incident.trigger_event_count,
            track_id=incident.track_id,
            frame_snapshot_path=incident.frame_snapshot_path,
            acknowledged=incident.acknowledged,
            acknowledged_at=incident.acknowledged_at,
            meta_json=incident.metadata,
        )

    def to_dict(self) -> dict:
        return {
            "incident_id": self.id,
            "created_at": self.created_at.isoformat(),
            "camera_id": self.camera_id,
            "zone": self.zone,
            "incident_type": self.incident_type,
            "severity": Severity(self.severity).label,
            "rule_id": self.rule_id,
            "confidence_avg": self.confidence_avg,
            "trigger_event_count": self.trigger_event_count,
            "track_id": self.track_id,
            "frame_snapshot_url": self.frame_snapshot_path,
            "acknowledged": self.acknowledged,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "metadata": self.meta_json,
        }


class AlertDispatchORM(Base):
    __tablename__ = "alert_dispatches"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id: Mapped[str] = mapped_column(String(36), index=True)
    dispatched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    channel: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(16))
    response_code: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    error_msg: Mapped[str | None] = mapped_column(Text, nullable=True)

    @classmethod
    def from_dataclass(cls, r: DispatchResult) -> AlertDispatchORM:
        return cls(
            incident_id=r.incident_id,
            dispatched_at=r.dispatched_at,
            channel=r.channel,
            status=r.status,
            response_code=r.response_code,
            error_msg=r.error_msg,
        )
