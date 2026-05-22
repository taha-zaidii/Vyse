"""Vision Agent — frame ingest, multi-model inference, event emission.

One instance per camera. Runs YOLOv8 + MediaPipe + zone analysis on every
N-th frame, emits DetectionEvent objects onto the bus.
"""

from __future__ import annotations

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime

import cv2  # type: ignore[import-untyped]
import numpy as np
import structlog

from vyse.core.config import CameraConfig, get_settings, load_zones
from vyse.core.event_bus import EventBus
from vyse.core.models import BBox, DetectionEvent
from vyse.detectors.drowsiness_detector import DrowsinessDetector
from vyse.detectors.ppe_detector import PPEDetector, RawDetection
from vyse.detectors.zone_detector import CompiledZone, compile_zones, zone_for_bbox
from vyse.tracking.bytetrack import SimpleTracker

logger = structlog.get_logger(__name__)


# Classes whose absence we represent positively. e.g. a "person" bbox without
# an overlapping "helmet" bbox emits a synthetic "no-helmet" detection.
_REQUIRED_PPE = ("helmet", "vest")


class VisionAgent:
    def __init__(self, camera: CameraConfig, bus: EventBus):
        self.camera = camera
        self.bus = bus
        self.settings = get_settings()
        self._frame_id = 0
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix=f"vision-{camera.id}")
        self._tracker = SimpleTracker()
        self._ppe: PPEDetector | None = None
        self._drowsy: DrowsinessDetector | None = None
        self._zones: list[CompiledZone] = []

    def _lazy_init(self, frame: np.ndarray) -> None:
        if self._ppe is None:
            self._ppe = PPEDetector()
        if self._drowsy is None:
            self._drowsy = DrowsinessDetector()
        if not self._zones:
            h, w = frame.shape[:2]
            all_zones = load_zones()
            cam_zones = [z for z in all_zones if z.camera_id == self.camera.id]
            self._zones = compile_zones(cam_zones, w, h)

    async def run(self) -> None:
        loop = asyncio.get_event_loop()
        cap_source: int | str = (
            int(self.camera.url) if self.camera.url.isdigit() else self.camera.url
        )
        cap = cv2.VideoCapture(cap_source)
        if not cap.isOpened():
            logger.error("camera_open_failed", camera=self.camera.id, url=self.camera.url)
            return

        skip = max(1, self.settings.frame_skip)
        logger.info("vision_agent_running", camera=self.camera.id, frame_skip=skip)

        try:
            while True:
                ret, frame_bgr = cap.read()
                if not ret:
                    logger.warning("camera_frame_drop", camera=self.camera.id)
                    await asyncio.sleep(0.05)
                    continue

                self._frame_id += 1
                if self._frame_id % skip != 0:
                    continue

                self._lazy_init(frame_bgr)
                rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)

                t0 = time.perf_counter()
                ppe_dets, ears = await asyncio.gather(
                    loop.run_in_executor(self._executor, self._ppe.infer, frame_bgr),  # type: ignore[union-attr]
                    loop.run_in_executor(self._executor, self._drowsy.infer, rgb),  # type: ignore[union-attr]
                )
                dt_ms = (time.perf_counter() - t0) * 1000.0

                events = self._to_events(ppe_dets, ears)
                for ev in events:
                    await self.bus.detections.put(ev)

                if self._frame_id % 60 == 0:
                    logger.debug(
                        "vision_tick",
                        camera=self.camera.id,
                        frame=self._frame_id,
                        events=len(events),
                        inference_ms=round(dt_ms, 1),
                    )

                await asyncio.sleep(0)  # yield to event loop
        finally:
            cap.release()
            self._executor.shutdown(wait=False, cancel_futures=True)

    def _to_events(self, ppe: list[RawDetection], ears: list) -> list[DetectionEvent]:
        now = datetime.now(UTC)
        events: list[DetectionEvent] = []
        persons = [d for d in ppe if d.cls == "person"]

        # Track persons across frames
        track_ids = self._tracker.update(self._frame_id, [p.bbox for p in persons])

        # Emit raw detections (helmet, vest, phone, etc.)
        for d in ppe:
            if d.cls == "person":
                continue
            zone = zone_for_bbox(self._zones, d.bbox)
            events.append(
                DetectionEvent(
                    frame_id=self._frame_id,
                    timestamp=now,
                    camera_id=self.camera.id,
                    detection_type=d.cls,
                    confidence=d.confidence,
                    bbox=d.bbox,
                    zone=zone.name if zone else None,
                    metadata={"zone_risk": zone.risk_tier if zone else None},
                )
            )

        # Synthesize "no-helmet" / "no-vest" per person — Risk Agent gets to decide
        helmets = [d.bbox for d in ppe if d.cls == "helmet"]
        vests = [d.bbox for d in ppe if d.cls == "vest"]
        for person, tid in zip(persons, track_ids, strict=False):
            zone = zone_for_bbox(self._zones, person.bbox)
            if not _bbox_overlaps_any(person.bbox, helmets):
                events.append(
                    DetectionEvent(
                        frame_id=self._frame_id,
                        timestamp=now,
                        camera_id=self.camera.id,
                        detection_type="no-helmet",
                        confidence=person.confidence,
                        bbox=person.bbox,
                        zone=zone.name if zone else None,
                        track_id=tid,
                        metadata={"zone_risk": zone.risk_tier if zone else None},
                    )
                )
            if not _bbox_overlaps_any(person.bbox, vests):
                events.append(
                    DetectionEvent(
                        frame_id=self._frame_id,
                        timestamp=now,
                        camera_id=self.camera.id,
                        detection_type="no-vest",
                        confidence=person.confidence,
                        bbox=person.bbox,
                        zone=zone.name if zone else None,
                        track_id=tid,
                    )
                )

        # Drowsiness — one DetectionEvent per detected face below EAR threshold
        for ear_result in ears:
            if self._drowsy and self._drowsy.is_drowsy(ear_result):
                events.append(
                    DetectionEvent(
                        frame_id=self._frame_id,
                        timestamp=now,
                        camera_id=self.camera.id,
                        detection_type="ear_low",
                        confidence=1.0 - ear_result.avg_ear,
                        bbox=BBox(0, 0, 0, 0),  # face bbox attribution TODO
                        zone=None,
                        metadata={"ear": ear_result.avg_ear},
                    )
                )

        return events


def _bbox_overlaps_any(person: BBox, items: list[BBox]) -> bool:
    """True if any item bbox roughly overlaps the upper half of the person bbox."""
    if not items:
        return False
    px1, py1, px2, py2 = person.as_tuple()
    head_y_cut = py1 + (py2 - py1) * 0.4  # top 40% of person bbox
    for b in items:
        # crude overlap on x-axis + b is in person's upper region
        if b.x2 < px1 or b.x1 > px2:
            continue
        if b.y1 > head_y_cut and person.y2 < py2:
            continue
        return True
    return False
