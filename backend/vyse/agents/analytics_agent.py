"""Analytics Agent — persists incidents + dispatch results, computes aggregations."""

from __future__ import annotations

import asyncio

import structlog

from vyse.core.event_bus import EventBus
from vyse.db.models import AlertDispatchORM, IncidentORM
from vyse.db.session import session_scope

logger = structlog.get_logger(__name__)


class AnalyticsAgent:
    def __init__(self, bus: EventBus):
        self.bus = bus

    async def run(self) -> None:
        logger.info("analytics_agent_running")
        await asyncio.gather(
            self._consume_incidents(),
            self._consume_dispatches(),
        )

    async def _consume_incidents(self) -> None:
        while True:
            incident = await self.bus.incidents.get()
            try:
                async with session_scope() as session:
                    session.add(IncidentORM.from_dataclass(incident))
                    await session.commit()
            except Exception as e:
                logger.exception("incident_persist_failed", error=str(e))

    async def _consume_dispatches(self) -> None:
        while True:
            result = await self.bus.dispatch_results.get()
            try:
                async with session_scope() as session:
                    session.add(AlertDispatchORM.from_dataclass(result))
                    await session.commit()
            except Exception as e:
                logger.exception("dispatch_persist_failed", error=str(e))
