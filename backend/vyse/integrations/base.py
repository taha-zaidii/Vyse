"""AlertChannel protocol — every integration implements this."""

from __future__ import annotations

from typing import Protocol

from vyse.core.models import DispatchResult, Incident, Severity


class AlertChannel(Protocol):
    name: str
    threshold: Severity

    async def dispatch(self, incident: Incident) -> DispatchResult: ...

    async def test(self) -> bool: ...
