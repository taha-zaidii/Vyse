"""Console channel — pretty-prints every incident."""

from __future__ import annotations

from datetime import UTC, datetime

import structlog

from vyse.core.models import DispatchResult, Incident, Severity

logger = structlog.get_logger(__name__)


class ConsoleChannel:
    name = "console"

    def __init__(self, threshold: Severity = Severity.LOW):
        self.threshold = threshold

    async def dispatch(self, incident: Incident) -> DispatchResult:
        logger.warning(
            "incident",
            incident_id=incident.incident_id,
            type=incident.incident_type,
            severity=incident.severity.label,
            camera=incident.camera_id,
            zone=incident.zone,
            confidence=round(incident.confidence_avg, 3),
            triggers=incident.trigger_event_count,
        )
        return DispatchResult(
            incident_id=incident.incident_id,
            channel=self.name,
            dispatched_at=datetime.now(UTC),
            status="sent",
        )

    async def test(self) -> bool:
        return True
