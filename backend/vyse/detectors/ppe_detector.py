"""YOLOv8-based PPE detector.

Wraps an Ultralytics model and emits raw class predictions. The Vision Agent
turns these into DetectionEvent objects (it knows the camera + frame_id context).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from vyse.core.config import get_settings
from vyse.core.models import BBox

# Classes the YOLO model is expected to output. Fine-tuned weights may map these
# names differently — keep the alias map in sync with `models/yolov8-ppe-finetuned.pt`.
PPE_CLASSES = (
    "person",
    "helmet",
    "no-helmet",
    "vest",
    "no-vest",
    "gloves",
    "goggles",
    "phone",
)


@dataclass(slots=True)
class RawDetection:
    cls: str
    confidence: float
    bbox: BBox


class PPEDetector:
    def __init__(self, weights: str | Path | None = None, device: str | None = None):
        # Lazy import — keep import-time cheap so unit tests can mock.
        from ultralytics import YOLO  # type: ignore[import-untyped]

        settings = get_settings()
        self.weights = str(weights or settings.yolo_weights)
        self.device = device or settings.yolo_device
        self.conf_threshold = settings.confidence_threshold
        self.model = YOLO(self.weights)

    def infer(self, frame: np.ndarray) -> list[RawDetection]:
        results = self.model.predict(
            frame,
            conf=self.conf_threshold,
            verbose=False,
            device=None if self.device == "auto" else self.device,
        )
        if not results:
            return []

        result = results[0]
        names = result.names  # type: ignore[union-attr]
        boxes = result.boxes  # type: ignore[union-attr]
        if boxes is None or len(boxes) == 0:
            return []

        out: list[RawDetection] = []
        for b in boxes:
            cls_idx = int(b.cls.item())
            cls_name = names[cls_idx]
            conf = float(b.conf.item())
            x1, y1, x2, y2 = (float(v) for v in b.xyxy[0].tolist())
            out.append(
                RawDetection(
                    cls=cls_name,
                    confidence=conf,
                    bbox=BBox(x1, y1, x2, y2),
                )
            )
        return out


def filter_by_classes(
    detections: Iterable[RawDetection], allow: Iterable[str]
) -> list[RawDetection]:
    allowed = set(allow)
    return [d for d in detections if d.cls in allowed]
