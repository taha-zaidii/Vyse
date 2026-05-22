# Vyse — Architecture Notes

Companion to the PRD. Use the PRD ([Vyse_PRD.html](../Vyse_PRD.html)) for the canonical spec; this file is for engineering-detail follow-ups that live close to the code.

## Process model

A single `python -m vyse` process boots:

1. The orchestrator (`vyse.core.orchestrator.Orchestrator`) under `asyncio.TaskGroup`.
2. One `VisionAgent` coroutine per enabled camera in `config/settings.yaml`.
3. One `RiskAgent` coroutine consuming all detection events.
4. One `AlertAgent` coroutine fanning out to configured channels.
5. One `AnalyticsAgent` coroutine writing incidents + dispatch results to the DB.
6. The FastAPI app (`vyse.api.main:app`) served by uvicorn, sharing the same event loop.

All cross-agent communication happens via `EventBus` (three typed `asyncio.Queue`s). No shared mutable state.

## Failure model

- A crashing agent is restarted by the orchestrator with exponential backoff (1s → 30s).
- Camera disconnects are retried inside `VisionAgent` with backoff before the agent itself exits.
- On SIGTERM/SIGINT, the orchestrator sets a shutdown event; agents drain their current item then exit.
- Webhook failures are captured to `alert_dispatches` and surfaced via Prometheus (no retry storms).

## Concurrency boundaries

- CPU/GPU-bound inference (YOLO, MediaPipe) runs in a `ThreadPoolExecutor` per VisionAgent.
- The asyncio event loop never blocks on inference — `loop.run_in_executor` keeps it responsive.
- DB writes use `sqlalchemy[asyncio]` with `asyncpg` (prod) or `aiosqlite` (dev).

## Where to make changes

| You want to…                          | Edit                                                  |
| ------------------------------------- | ----------------------------------------------------- |
| Add a new detection type              | `vyse/detectors/` + emit event in `vision_agent.py`   |
| Change rule logic                     | `config/rules.yaml` (no code change)                  |
| Add an alert channel                  | New module under `vyse/integrations/`, register in `alert_agent.py` |
| Add an API endpoint                   | `vyse/api/routes/`                                    |
| Add a dashboard page                  | `dashboard/app/<route>/page.tsx`                      |
| Add a chart                           | `dashboard/components/`                               |
