"""Layered configuration: env vars + YAML files, typed via Pydantic."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

CONFIG_DIR = Path(__file__).resolve().parents[3] / "config"


class CameraConfig(BaseModel):
    id: str
    name: str
    url: str  # rtsp://… | file path | "0" for webcam
    enabled: bool = True
    target_fps: int = 15
    zones: list[str] = Field(default_factory=list)


class ZonePolygon(BaseModel):
    name: str
    camera_id: str
    points: list[tuple[float, float]]  # normalized 0..1 coords
    risk_tier: str = "general"  # "general" | "machinery" | "restricted"


class RuleDefinition(BaseModel):
    id: str
    trigger: str
    window_seconds: float
    min_occurrences: int
    severity: str = "MEDIUM"
    cooldown_seconds: int = 60
    zone: str | None = None
    context_boosts: list[dict[str, Any]] = Field(default_factory=list)
    enabled: bool = True


class AlertChannelConfig(BaseModel):
    name: str  # "slack", "teams", "webhook", "email", "console"
    enabled: bool = True
    severity_threshold: str = "MEDIUM"
    options: dict[str, Any] = Field(default_factory=dict)  # URLs, creds, etc.


class Settings(BaseSettings):
    """Top-level service settings (env-driven)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="VYSE_",
        extra="ignore",
    )

    env: str = "dev"
    log_level: str = "INFO"
    log_json: bool = True

    db_url: str = "sqlite+aiosqlite:///./vyse.db"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_key: str | None = None

    # Inference
    yolo_weights: str = "yolov8n.pt"
    yolo_device: str = "auto"  # "cpu" | "cuda" | "auto"
    inference_target_fps: int = 15
    confidence_threshold: float = 0.45
    frame_skip: int = 2

    # Storage
    snapshot_dir: str = "./snapshots"
    snapshot_retention_days: int = 30


def _load_yaml(path: Path) -> Any:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_cameras(path: Path | None = None) -> list[CameraConfig]:
    raw = _load_yaml(path or CONFIG_DIR / "settings.yaml") or {}
    return [CameraConfig(**c) for c in raw.get("cameras", [])]


def load_zones(path: Path | None = None) -> list[ZonePolygon]:
    raw = _load_yaml(path or CONFIG_DIR / "zones.yaml") or {}
    return [ZonePolygon(**z) for z in raw.get("zones", [])]


def load_rules(path: Path | None = None) -> list[RuleDefinition]:
    raw = _load_yaml(path or CONFIG_DIR / "rules.yaml") or {}
    return [RuleDefinition(**r) for r in raw.get("rules", [])]


def load_channels(path: Path | None = None) -> list[AlertChannelConfig]:
    raw = _load_yaml(path or CONFIG_DIR / "settings.yaml") or {}
    return [AlertChannelConfig(**c) for c in raw.get("channels", [])]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
