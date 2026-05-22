"""Read-only config endpoints (rules, zones, cameras)."""

from __future__ import annotations

from fastapi import APIRouter

from vyse.core import config

router = APIRouter(prefix="/config", tags=["config"])


@router.get("/rules")
async def list_rules() -> dict:
    return {"items": [r.model_dump() for r in config.load_rules()]}


@router.get("/zones")
async def list_zones() -> dict:
    return {"items": [z.model_dump() for z in config.load_zones()]}


@router.get("/cameras")
async def list_cameras() -> dict:
    return {"items": [c.model_dump() for c in config.load_cameras()]}
