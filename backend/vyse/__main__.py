"""`python -m vyse` — boot the full pipeline (agents + API together)."""

from __future__ import annotations

import asyncio
import contextlib

import structlog
import uvicorn

from vyse.agents.alert_agent import AlertAgent
from vyse.agents.analytics_agent import AnalyticsAgent
from vyse.agents.risk_agent import RiskAgent
from vyse.agents.vision_agent import VisionAgent
from vyse.core.config import get_settings, load_cameras
from vyse.core.logging import configure_logging
from vyse.core.orchestrator import Orchestrator
from vyse.db.session import init_db

logger = structlog.get_logger(__name__)


async def main() -> None:
    configure_logging()
    settings = get_settings()
    await init_db()

    cameras = load_cameras()
    enabled = [c for c in cameras if c.enabled]
    if not enabled:
        logger.warning("no_cameras_enabled — running API only")

    async with Orchestrator() as orch:
        for cam in enabled:
            orch.register(f"vision::{cam.id}", VisionAgent(cam, orch.bus).run)
        orch.register("risk", RiskAgent(orch.bus).run)
        orch.register("alert", AlertAgent(orch.bus).run)
        orch.register("analytics", AnalyticsAgent(orch.bus).run)

        config = uvicorn.Config(
            "vyse.api.main:app",
            host=settings.api_host,
            port=settings.api_port,
            log_level=settings.log_level.lower(),
            lifespan="on",
        )
        server = uvicorn.Server(config)
        orch.register("api", server.serve)

        await orch.run_forever()


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
