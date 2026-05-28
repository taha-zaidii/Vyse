# Vyse - Pakistan's First Real-Time AI Workplace Safety Intelligence System

Real-time computer vision for workplace safety. Vyse ingests live camera feeds, detects PPE violations, drowsiness, restricted-zone breaches, and device misuse, and turns thousands of per-frame detections into a handful of acknowledgeable incidents using a four-agent pipeline with temporal rules.

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-3776AB.svg)](https://www.python.org/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-000.svg)](https://nextjs.org/)
[![CI](https://github.com/taha-zaidii/Vyse/actions/workflows/ci.yml/badge.svg)](https://github.com/taha-zaidii/Vyse/actions/workflows/ci.yml)

The full product and engineering spec lives in [Vyse_PRD.html](Vyse_PRD.html) — 25 sections covering market analysis, four-agent architecture, MLOps strategy, hardware tiers, compliance mapping, and a six-phase delivery plan.

## Quick start

Run the full stack with Docker:

```bash
cp .env.example .env
docker compose up --build
```

| Service       | URL                          |
| ------------- | ---------------------------- |
| Dashboard     | http://localhost:3000        |
| API + Swagger | http://localhost:8000/docs   |
| Adminer       | http://localhost:8080        |

Or run backend and dashboard separately for development:

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m vyse

# Dashboard (separate terminal)
cd dashboard
npm install
npm run dev
```

To populate the dashboard with realistic test data:

```bash
python scripts/seed_demo.py
```

## How it works

```
Camera → Vision Agent → Risk Agent → Alert Agent ─┐
                                    + Analytics Agent ──→ API ──→ Dashboard
            │              │
       YOLOv8 + MediaPipe   YAML temporal rules
       + ByteTrack tracker  + per-(camera, zone, track) cooldown
```

Each agent is an asyncio coroutine that communicates over typed queues. There is no shared mutable state, and the orchestrator restarts any agent that crashes without taking the others down. The temporal rule engine is what separates Vyse from naive per-frame detection: a two-second helmet removal does not become an incident, but a sustained violation in a machinery zone does — and gets routed to whoever is on call.

Full architecture and rationale in [PRD §10](Vyse_PRD.html#architecture).

## Repository layout

```
backend/      Python service: agents, detectors, FastAPI, DB, ML scripts
dashboard/    Next.js 14 dashboard (shadcn/ui, Tailwind, Framer Motion)
config/       rules.yaml, zones.yaml, settings.yaml
data/         Datasets (DVC-tracked, large files gitignored)
models/       YOLO weights + ONNX/TensorRT exports (DVC-tracked)
scripts/      Demo seed, local-run helper, benchmark
docs/         Architecture, deployment, contributing
```

## Stack

| Layer            | Choice                                                       |
| ---------------- | ------------------------------------------------------------ |
| Detection        | Ultralytics YOLOv8                                           |
| Face and Pose    | MediaPipe — Face Mesh for EAR, Pose for posture              |
| Tracking         | ByteTrack (persistent worker IDs across frames)              |
| Inference export | ONNX Runtime, plus TensorRT for NVIDIA Jetson deployment     |
| Service          | FastAPI, WebSockets, asyncio                                 |
| Database         | PostgreSQL with TimescaleDB in production; SQLite for dev    |
| Dashboard        | Next.js 14, shadcn/ui, Tailwind CSS, Framer Motion, Recharts |
| Observability    | structlog, Prometheus                                        |
| MLOps            | DVC for datasets, Weights and Biases for runs                |

Detailed selection notes in [PRD §11](Vyse_PRD.html#tech-stack).

## Roadmap

| Phase | Scope                                                                    |
| ----- | ------------------------------------------------------------------------ |
| P0    | Repository scaffold, typed data models, tooling. *(current)*             |
| P1    | Vision Agent emitting DetectionEvents from a live webcam.                |
| P2    | Risk Agent temporal rule engine; Slack and webhook dispatch.             |
| P3    | Postgres persistence, REST endpoints, WebSocket incident stream.         |
| P4    | All dashboard pages, fine-tuned PPE model, recorded demo.                |
| P5    | Multi-camera fan-out, LLM incident narration, Jetson TensorRT path.      |

Each phase has acceptance criteria in [PRD §24](Vyse_PRD.html#acceptance).

## Documentation

- [Vyse_PRD.html](Vyse_PRD.html) — full product requirements document
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — engineering notes, process model, failure handling
- [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) — hardware tiers, edge and production deployment
- [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) — local setup, conventions, issue template

## License

MIT. See [LICENSE](LICENSE).

---

Taha Zaidi — tahazaidi2004@gmail.com.

---
Shipping soon...
