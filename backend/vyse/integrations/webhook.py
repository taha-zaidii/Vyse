"""Generic webhook channel — also powers Slack and Teams incoming-webhook URLs."""

from __future__ import annotations

from datetime import UTC, datetime

import httpx
import structlog

from vyse.core.models import DispatchResult, Incident, Severity

logger = structlog.get_logger(__name__)


SEVERITY_COLOR = {
    Severity.LOW: "#10b981",
    Severity.MEDIUM: "#f59e0b",
    Severity.HIGH: "#f97316",
    Severity.CRITICAL: "#ef4444",
}


class WebhookChannel:
    def __init__(self, name: str, url: str, threshold: Severity = Severity.MEDIUM):
        self.name = name
        self.url = url
        self.threshold = threshold

    def _payload(self, incident: Incident) -> dict:
        return {
            "text": f"[{incident.severity.label}] {incident.incident_type} @ {incident.camera_id}/{incident.zone}",
            "attachments": [
                {
                    "color": SEVERITY_COLOR.get(incident.severity, "#666"),
                    "fields": [
                        {"title": "Rule", "value": incident.rule_id, "short": True},
                        {
                            "title": "Confidence",
                            "value": f"{incident.confidence_avg:.2f}",
                            "short": True,
                        },
                        {
                            "title": "Triggers",
                            "value": str(incident.trigger_event_count),
                            "short": True,
                        },
                        {
                            "title": "Track ID",
                            "value": str(incident.track_id or "-"),
                            "short": True,
                        },
                    ],
                    "ts": int(incident.created_at.timestamp()),
                }
            ],
            "incident": incident.to_dict(),
        }

    async def dispatch(self, incident: Incident) -> DispatchResult:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(self.url, json=self._payload(incident))
        ok = 200 <= resp.status_code < 300
        return DispatchResult(
            incident_id=incident.incident_id,
            channel=self.name,
            dispatched_at=datetime.now(UTC),
            status="sent" if ok else "failed",
            response_code=resp.status_code,
            error_msg=None if ok else resp.text[:300],
        )

    async def test(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(self.url, json={"text": "Vyse webhook test"})
            return 200 <= resp.status_code < 300
        except Exception as e:
            logger.warning("webhook_test_failed", error=str(e))
            return False
