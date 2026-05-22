from __future__ import annotations

from vyse.core.config import ZonePolygon
from vyse.core.models import BBox
from vyse.detectors.zone_detector import compile_zones, zone_for_bbox


def test_centroid_inside_polygon_detected():
    zones = [
        ZonePolygon(
            name="machinery",
            camera_id="cam-1",
            points=[(0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.2, 0.8)],
            risk_tier="machinery",
        )
    ]
    compiled = compile_zones(zones, frame_w=1000, frame_h=1000)
    inside = BBox(450, 450, 550, 550)
    outside = BBox(10, 10, 50, 50)
    assert zone_for_bbox(compiled, inside) is not None
    assert zone_for_bbox(compiled, outside) is None
