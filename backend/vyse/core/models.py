"""Canonical typed events flowing between agents.

These are the only objects that cross agent boundaries. Each agent reads
events of one type and emits events of another. Keep them frozen + JSON-friendly.
"""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import IntEnum
from typing import Any


class Severity(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

    @property
    def label(self) -> str:
        return self.name


# --- Detection-layer types ----------------------------------------------------


@dataclass(slots=True)
class BBox:
    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def centroid(self) -> tuple[float, float]:
        return ((self.x1 + self.x2) / 2.0, (self.y1 + self.y2) / 2.0)

    def as_tuple(self) -> tuple[float, float, float, float]:
        return (self.x1, self.y1, self.x2, self.y2)


@dataclass(slots=True)
class DetectionEvent:
    """A single thing the Vision Agent observed in one frame."""

    frame_id: int
    timestamp: datetime
    camera_id: str
    detection_type: str  # "no-helmet", "ear_low", "phone", "zone_breach", ...
    confidence: float
    bbox: BBox
    zone: str | None = None
    track_id: int | None = None  # ByteTrack-assigned persistent ID
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["timestamp"] = self.timestamp.isoformat()
        return d


# --- Incident-layer types -----------------------------------------------------


@dataclass(slots=True)
class Incident:
    """A confirmed safety event, distilled by the Risk Agent from many DetectionEvents."""

    incident_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    camera_id: str = ""
    zone: str | None = None
    incident_type: str = ""
    severity: Severity = Severity.LOW
    rule_id: str = ""
    confidence_avg: float = 0.0
    trigger_event_count: int = 0
    track_id: int | None = None
    frame_snapshot_path: str | None = None
    acknowledged: bool = False
    acknowledged_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["created_at"] = self.created_at.isoformat()
        d["severity"] = self.severity.label
        if self.acknowledged_at:
            d["acknowledged_at"] = self.acknowledged_at.isoformat()
        return d


@dataclass(slots=True)
class DispatchResult:
    """Outcome of an Alert Agent's attempt to push an incident through a channel."""

    incident_id: str
    channel: str
    dispatched_at: datetime
    status: str  # "sent", "failed", "skipped"
    response_code: int | None = None
    error_msg: str | None = None
