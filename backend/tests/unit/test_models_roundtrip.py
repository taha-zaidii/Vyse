"""Phase-0 DoD: dataclasses round-trip via asdict()+JSON."""

from __future__ import annotations

import json
from datetime import UTC, datetime

from vyse.core.models import BBox, DetectionEvent, Incident, Severity


def test_detection_event_serializes():
    ev = DetectionEvent(
        frame_id=1,
        timestamp=datetime(2026, 5, 22, 12, 0, tzinfo=UTC),
        camera_id="cam-1",
        detection_type="no-helmet",
        confidence=0.92,
        bbox=BBox(10, 20, 100, 200),
        zone="machinery",
        track_id=4,
        metadata={"zone_risk": "machinery"},
    )
    payload = json.dumps(ev.to_dict())
    parsed = json.loads(payload)
    assert parsed["detection_type"] == "no-helmet"
    assert parsed["zone"] == "machinery"


def test_incident_serializes_with_label():
    inc = Incident(
        camera_id="cam-1",
        zone="machinery",
        incident_type="PPE_NO_HELMET_SUSTAINED",
        severity=Severity.CRITICAL,
        rule_id="PPE_NO_HELMET_SUSTAINED",
        confidence_avg=0.83,
        trigger_event_count=14,
    )
    payload = json.loads(json.dumps(inc.to_dict()))
    assert payload["severity"] == "CRITICAL"
    assert payload["trigger_event_count"] == 14
