"""Alert Agent — fan-out incidents to configured channels."""

from __future__ import annotations

import asyncio
from datetime import UTC

import structlog

from vyse.core.config import load_channels
from vyse.core.event_bus import EventBus
from vyse.core.models import Incident, Severity
from vyse.integrations.base import AlertChannel
from vyse.integrations.console import ConsoleChannel
from vyse.integrations.email_smtp import SMTPChannel
from vyse.integrations.webhook import WebhookChannel

logger = structlog.get_logger(__name__)


def _build_channels() -> list[AlertChannel]:
    out: list[AlertChannel] = []
    configs = load_channels()
    for c in configs:
        if not c.enabled:
            continue
        name = c.name.lower()
        threshold = Severity[c.severity_threshold.upper()]
        if name == "console":
            out.append(ConsoleChannel(threshold=threshold))
        elif name in ("slack", "teams", "webhook"):
            out.append(
                WebhookChannel(
                    name=name,
                    url=c.options["url"],
                    threshold=threshold,
                )
            )
        elif name == "email":
            out.append(SMTPChannel(threshold=threshold, **c.options))
        else:
            logger.warning("unknown_channel", name=name)
    if not out:
        # Always at least log to console in dev.
        out.append(ConsoleChannel(threshold=Severity.LOW))
    return out


class AlertAgent:
    def __init__(self, bus: EventBus):
        self.bus = bus
        self.channels: list[AlertChannel] = _build_channels()

    async def run(self) -> None:
        logger.info("alert_agent_running", channels=[c.name for c in self.channels])
        while True:
            incident: Incident = await self.bus.incidents.get()
            await self._dispatch(incident)

    async def _dispatch(self, incident: Incident) -> None:
        tasks = []
        for channel in self.channels:
            if int(incident.severity) < int(channel.threshold):
                continue
            tasks.append(self._safe_send(channel, incident))
        results = await asyncio.gather(*tasks, return_exceptions=False)
        for r in results:
            await self.bus.dispatch_results.put(r)

    async def _safe_send(self, channel: AlertChannel, incident: Incident):
        try:
            return await channel.dispatch(incident)
        except Exception as e:
            logger.exception("channel_dispatch_failed", channel=channel.name, error=str(e))
            from datetime import datetime

            from vyse.core.models import DispatchResult

            return DispatchResult(
                incident_id=incident.incident_id,
                channel=channel.name,
                dispatched_at=datetime.now(UTC),
                status="failed",
                error_msg=str(e),
            )
