"""Phone-in-zone detector. Thin filter over PPEDetector output."""

from __future__ import annotations

from collections.abc import Iterable

from vyse.detectors.ppe_detector import RawDetection


def filter_phones(detections: Iterable[RawDetection]) -> list[RawDetection]:
    return [d for d in detections if d.cls in ("phone", "cell phone", "mobile_phone")]
