"""Polygon-based zone breach detection."""

from __future__ import annotations

from dataclasses import dataclass

from shapely.geometry import Point, Polygon

from vyse.core.config import ZonePolygon
from vyse.core.models import BBox


@dataclass(slots=True)
class CompiledZone:
    name: str
    risk_tier: str
    poly: Polygon


def compile_zones(zones: list[ZonePolygon], frame_w: int, frame_h: int) -> list[CompiledZone]:
    out: list[CompiledZone] = []
    for z in zones:
        pts = [(p[0] * frame_w, p[1] * frame_h) for p in z.points]
        if len(pts) < 3:
            continue
        out.append(CompiledZone(name=z.name, risk_tier=z.risk_tier, poly=Polygon(pts)))
    return out


def zone_for_bbox(zones: list[CompiledZone], bbox: BBox) -> CompiledZone | None:
    cx, cy = bbox.centroid
    point = Point(cx, cy)
    for z in zones:
        if z.poly.contains(point):
            return z
    return None
