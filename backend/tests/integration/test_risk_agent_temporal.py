"""Phase-2 DoD: false-positive proof + true-positive proof of the Risk Agent."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from vyse.agents.risk_agent import RiskAgent
from vyse.core.config import RuleDefinition
from vyse.core.event_bus import EventBus
from vyse.core.models import BBox, DetectionEvent


def _ev(ts: datetime, ttype: str = "no-helmet") -> DetectionEvent:
    return DetectionEvent(
        frame_id=0,
        timestamp=ts,
        camera_id="cam-1",
        detection_type=ttype,
        confidence=0.9,
        bbox=BBox(0, 0, 100, 200),
        zone="machinery",
        track_id=7,
        metadata={"zone_risk": "machinery"},
    )


@pytest.mark.asyncio
async def test_brief_violation_is_suppressed():
    """A 2-second no-helmet event must NOT trigger a sustained-violation incident."""
    rule = RuleDefinition(
        id="PPE_NO_HELMET_SUSTAINED",
        trigger="no-helmet",
        window_seconds=8.0,
        min_occurrences=12,
        severity="HIGH",
        cooldown_seconds=120,
    )
    bus = EventBus()
    agent = RiskAgent(bus, rules=[rule])

    t0 = datetime.now(UTC)
    for i in range(4):  # 4 frames over ~2s — well under the 12 needed
        await agent._process(_ev(t0 + timedelta(milliseconds=500 * i)))

    assert bus.incidents.qsize() == 0


@pytest.mark.asyncio
async def test_sustained_violation_fires_once_with_dedup():
    """A 10-second sustained no-helmet stream produces exactly ONE incident (cooldown holds)."""
    rule = RuleDefinition(
        id="PPE_NO_HELMET_SUSTAINED",
        trigger="no-helmet",
        window_seconds=8.0,
        min_occurrences=12,
        severity="HIGH",
        cooldown_seconds=120,
    )
    bus = EventBus()
    agent = RiskAgent(bus, rules=[rule])

    t0 = datetime.now(UTC)
    for i in range(30):  # 30 frames over ~15s
        await agent._process(_ev(t0 + timedelta(milliseconds=500 * i)))

    assert bus.incidents.qsize() == 1
