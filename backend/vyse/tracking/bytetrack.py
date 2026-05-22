"""Lightweight IoU-based tracker used until ByteTrack is wired in.

The full ByteTrack algorithm (`lap`-based) will live in `bytetrack_impl.py`.
This stub provides the same interface so the rest of the pipeline can develop
without blocking on the heavier dependency.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from vyse.core.models import BBox


@dataclass(slots=True)
class Track:
    track_id: int
    bbox: BBox
    last_seen_frame: int
    hits: int = 1


def _iou(a: BBox, b: BBox) -> float:
    inter_x1 = max(a.x1, b.x1)
    inter_y1 = max(a.y1, b.y1)
    inter_x2 = min(a.x2, b.x2)
    inter_y2 = min(a.y2, b.y2)
    iw = max(0.0, inter_x2 - inter_x1)
    ih = max(0.0, inter_y2 - inter_y1)
    inter = iw * ih
    area_a = max(0.0, (a.x2 - a.x1) * (a.y2 - a.y1))
    area_b = max(0.0, (b.x2 - b.x1) * (b.y2 - b.y1))
    union = area_a + area_b - inter
    if union <= 0.0:
        return 0.0
    return inter / union


@dataclass
class SimpleTracker:
    iou_threshold: float = 0.3
    max_missed_frames: int = 30
    _next_id: int = 1
    _tracks: dict[int, Track] = field(default_factory=dict)

    def update(self, frame_id: int, detections: list[BBox]) -> list[int]:
        """Assign a track_id per incoming detection. Returns list aligned with detections."""
        assigned: list[int | None] = [None] * len(detections)
        used_track_ids: set[int] = set()

        for i, det in enumerate(detections):
            best_id = None
            best_iou = self.iou_threshold
            for tid, track in self._tracks.items():
                if tid in used_track_ids:
                    continue
                iou = _iou(det, track.bbox)
                if iou > best_iou:
                    best_iou = iou
                    best_id = tid
            if best_id is not None:
                assigned[i] = best_id
                used_track_ids.add(best_id)
                self._tracks[best_id] = Track(
                    track_id=best_id,
                    bbox=det,
                    last_seen_frame=frame_id,
                    hits=self._tracks[best_id].hits + 1,
                )

        for i, det in enumerate(detections):
            if assigned[i] is None:
                tid = self._next_id
                self._next_id += 1
                self._tracks[tid] = Track(track_id=tid, bbox=det, last_seen_frame=frame_id)
                assigned[i] = tid

        stale = [
            tid
            for tid, t in self._tracks.items()
            if frame_id - t.last_seen_frame > self.max_missed_frames
        ]
        for tid in stale:
            del self._tracks[tid]

        return [a for a in assigned if a is not None]  # type: ignore[misc]

    @property
    def active_count(self) -> int:
        return len(self._tracks)
