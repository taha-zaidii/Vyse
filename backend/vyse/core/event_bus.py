"""Typed asyncio.Queue wrappers — the only mechanism agents share state.

Backpressure is intentional. If a downstream agent is slow, the upstream
will block on .put() rather than buffer indefinitely. Drop logic is opt-in
via `drop_oldest=True`.
"""

from __future__ import annotations

import asyncio
from typing import Generic, TypeVar

import structlog

from vyse.core.models import DetectionEvent, DispatchResult, Incident

T = TypeVar("T")

logger = structlog.get_logger(__name__)


class TypedQueue(Generic[T]):
    def __init__(self, name: str, maxsize: int = 256, drop_oldest: bool = False):
        self.name = name
        self._q: asyncio.Queue[T] = asyncio.Queue(maxsize=maxsize)
        self._drop_oldest = drop_oldest

    async def put(self, item: T) -> None:
        if self._drop_oldest and self._q.full():
            try:
                _ = self._q.get_nowait()
                logger.warning("queue_dropped_oldest", queue=self.name)
            except asyncio.QueueEmpty:
                pass
        await self._q.put(item)

    async def get(self) -> T:
        return await self._q.get()

    def qsize(self) -> int:
        return self._q.qsize()

    @property
    def maxsize(self) -> int:
        return self._q.maxsize


class EventBus:
    """Central registry of typed queues. Agents resolve queues by name."""

    def __init__(self) -> None:
        self.detections: TypedQueue[DetectionEvent] = TypedQueue("detections", maxsize=512)
        self.incidents: TypedQueue[Incident] = TypedQueue("incidents", maxsize=256)
        self.dispatch_results: TypedQueue[DispatchResult] = TypedQueue(
            "dispatch_results", maxsize=512, drop_oldest=True
        )

    def queue_depths(self) -> dict[str, int]:
        return {
            "detections": self.detections.qsize(),
            "incidents": self.incidents.qsize(),
            "dispatch_results": self.dispatch_results.qsize(),
        }
