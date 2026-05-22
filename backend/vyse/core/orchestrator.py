"""Agent lifecycle. Runs all 4 agents under asyncio.TaskGroup with restart on crash.

Usage:
    async with Orchestrator() as orch:
        await orch.run_forever()
"""

from __future__ import annotations

import asyncio
import contextlib
import signal
from collections.abc import Awaitable, Callable

import structlog

from vyse.core.event_bus import EventBus

logger = structlog.get_logger(__name__)

AgentCoro = Callable[[], Awaitable[None]]


class Orchestrator:
    def __init__(self) -> None:
        self.bus = EventBus()
        self._agents: dict[str, AgentCoro] = {}
        self._shutdown = asyncio.Event()

    def register(self, name: str, coro_factory: AgentCoro) -> None:
        self._agents[name] = coro_factory

    async def __aenter__(self) -> Orchestrator:
        return self

    async def __aexit__(self, *exc) -> None:
        self._shutdown.set()

    def _install_signal_handlers(self) -> None:
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            # Windows or restricted env — fall back to KeyboardInterrupt handling
            with contextlib.suppress(NotImplementedError):
                loop.add_signal_handler(sig, self._shutdown.set)

    async def _supervised(self, name: str, factory: AgentCoro) -> None:
        """Restart-on-crash wrapper around each agent coroutine."""
        backoff = 1.0
        while not self._shutdown.is_set():
            try:
                logger.info("agent_started", agent=name)
                await factory()
                logger.info("agent_exited_clean", agent=name)
                return
            except asyncio.CancelledError:
                logger.info("agent_cancelled", agent=name)
                raise
            except Exception as e:
                logger.exception("agent_crashed", agent=name, error=str(e))
                await asyncio.sleep(min(backoff, 30.0))
                backoff = min(backoff * 2, 30.0)

    async def run_forever(self) -> None:
        self._install_signal_handlers()
        try:
            async with asyncio.TaskGroup() as tg:
                for name, factory in self._agents.items():
                    tg.create_task(self._supervised(name, factory), name=name)
                tg.create_task(self._wait_shutdown(), name="shutdown-watcher")
        except* asyncio.CancelledError:
            logger.info("orchestrator_cancelled")

    async def _wait_shutdown(self) -> None:
        await self._shutdown.wait()
        logger.info("shutdown_signal_received")
        # Allow agents one drain-cycle before TaskGroup raises CancelledError
        await asyncio.sleep(0.5)
        raise asyncio.CancelledError("shutdown requested")
