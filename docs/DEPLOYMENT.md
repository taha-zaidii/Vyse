# Vyse — Deployment Guide

Pick the tier that matches your camera count and latency target. Full matrix in [PRD §19](../Vyse_PRD.html#hardware).

## Local dev (Mac / Linux)

```bash
cp .env.example .env
docker compose up --build
```

Visit http://localhost:3000.

## Edge / Jetson (Orin Nano)

1. Flash JetPack 6+.
2. Install: `sudo apt install -y python3.11-venv ffmpeg libgl1`.
3. Export model to TensorRT:
   ```bash
   python -m vyse.ml.export_onnx --weights models/yolov8n.pt --out models/exports/ppe.onnx
   python -m vyse.ml.export_trt  --onnx models/exports/ppe.onnx --engine models/exports/ppe.engine
   ```
4. Point `VYSE_YOLO_WEIGHTS=models/exports/ppe.engine` in `.env`.
5. Run with `python -m vyse`.

## Production (Docker + Postgres + GPU)

Edit `docker-compose.yml`:

- Uncomment the `deploy.resources.reservations.devices` block under `backend` for NVIDIA GPU passthrough.
- Switch `VYSE_DB_URL` to a managed Postgres if not self-hosting.
- Put both services behind a reverse proxy (Caddy / Traefik) with TLS.

## Backup

- **DB:** standard Postgres backups.
- **Snapshots:** the `snapshots/` volume — sync to S3 / GCS if you need long-term retention.
- **Config:** version `config/*.yaml` in git.
