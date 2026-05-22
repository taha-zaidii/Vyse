"""Risk Agent — temporal rule engine. Converts noisy DetectionEvents → Incidents.

Each rule maintains a sliding window of matching events per (camera, zone, track_id).
When `min_occurrences` is exceeded within `window_seconds`, an Incident fires,
subject to a per-rule cooldown.
"""

from __future__ import annotations

from collections import defaultdict, deque
from datetime import UTC, datetime, timedelta

import structlog

from vyse.core.config import RuleDefinition, load_rules
from vyse.core.event_bus import EventBus
from vyse.core.models import DetectionEvent, Incident, Severity

logger = structlog.get_logger(__name__)


def _severity_from_name(name: str) -> Severity:
    return Severity[name.upper()]


class _RuleState:
    """Per (rule, scope-key) sliding-window state."""

    def __init__(self, rule: RuleDefinition):
        self.rule = rule
        self.events: deque[DetectionEvent] = deque()
        self.last_fired_at: datetime | None = None

    def add(self, ev: DetectionEvent) -> bool:
        """Add event, prune old, return True if this addition triggers an incident."""
        self.events.append(ev)
        cutoff = ev.timestamp - timedelta(seconds=self.rule.window_seconds)
        while self.events and self.events[0].timestamp < cutoff:
            self.events.popleft()

        if len(self.events) < self.rule.min_occurrences:
            return False

        if self.last_fired_at is not None:
            elapsed = (ev.timestamp - self.last_fired_at).total_seconds()
            if elapsed < self.rule.cooldown_seconds:
                return False

        self.last_fired_at = ev.timestamp
        return True

    def snapshot(self) -> list[DetectionEvent]:
        return list(self.events)


class RiskAgent:
    def __init__(self, bus: EventBus, rules: list[RuleDefinition] | None = None):
        self.bus = bus
        self.rules = rules or load_rules()
        self._state: dict[tuple[str, str], _RuleState] = defaultdict(lambda: None)  # type: ignore[arg-type]

    def _state_for(self, rule: RuleDefinition, ev: DetectionEvent) -> _RuleState:
        # Scope each rule by (camera, zone, track_id) so two workers' violations don't merge.
        scope = f"{ev.camera_id}::{ev.zone or '_'}::{ev.track_id or '_'}"
        key = (rule.id, scope)
        st = self._state.get(key)
        if st is None:
            st = _RuleState(rule)
            self._state[key] = st
        return st

    def _matches(self, rule: RuleDefinition, ev: DetectionEvent) -> bool:
        if not rule.enabled:
            return False
        if rule.trigger != ev.detection_type:
            return False
        return not (rule.zone is not None and rule.zone != ev.zone)

    def _apply_boosts(self, rule: RuleDefinition, ev: DetectionEvent) -> Severity:
        sev = _severity_from_name(rule.severity)
        for boost in rule.context_boosts:
            cond = boost.get("condition", "")
            upgrade = boost.get("severity_upgrade")
            if not upgrade:
                continue
            # ultra-tiny mini-evaluator: only supports `zone == "foo"` and `zone_risk == "foo"`
            if "zone ==" in cond:
                wanted = cond.split("==")[1].strip().strip('"').strip("'")
                if ev.zone == wanted:
                    sev = _severity_from_name(upgrade)
            elif "zone_risk ==" in cond:
                wanted = cond.split("==")[1].strip().strip('"').strip("'")
                if ev.metadata.get("zone_risk") == wanted:
                    sev = _severity_from_name(upgrade)
        return sev

    async def run(self) -> None:
        logger.info("risk_agent_running", rules=len(self.rules))
        while True:
            ev = await self.bus.detections.get()
            await self._process(ev)

    async def _process(self, ev: DetectionEvent) -> None:
        for rule in self.rules:
            if not self._matches(rule, ev):
                continue
            st = self._state_for(rule, ev)
            if not st.add(ev):
                continue

            sev = self._apply_boosts(rule, ev)
            events = st.snapshot()
            avg_conf = sum(e.confidence for e in events) / max(len(events), 1)
            incident = Incident(
                created_at=datetime.now(UTC),
                camera_id=ev.camera_id,
                zone=ev.zone,
                incident_type=rule.id,
                severity=sev,
                rule_id=rule.id,
                confidence_avg=avg_conf,
                trigger_event_count=len(events),
                track_id=ev.track_id,
                metadata={
                    "window_seconds": rule.window_seconds,
                    "min_occurrences": rule.min_occurrences,
                    "zone_risk": ev.metadata.get("zone_risk"),
                },
            )
            await self.bus.incidents.put(incident)
            logger.info(
                "incident_fired",
                incident_id=incident.incident_id,
                rule=rule.id,
                severity=sev.label,
                camera=ev.camera_id,
                zone=ev.zone,
                track_id=ev.track_id,
            )
