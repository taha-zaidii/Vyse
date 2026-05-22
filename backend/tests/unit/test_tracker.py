from __future__ import annotations

from vyse.core.models import BBox
from vyse.tracking.bytetrack import SimpleTracker


def test_persistent_id_across_consecutive_frames():
    tracker = SimpleTracker(iou_threshold=0.3)
    bbox_a = BBox(100, 100, 200, 300)
    ids_t1 = tracker.update(1, [bbox_a])
    # slight movement, very high IoU — should retain id
    bbox_b = BBox(105, 102, 205, 302)
    ids_t2 = tracker.update(2, [bbox_b])
    assert ids_t1 == ids_t2 == [1]


def test_new_id_for_unrelated_detection():
    tracker = SimpleTracker(iou_threshold=0.3)
    a = BBox(100, 100, 200, 300)
    b = BBox(800, 100, 900, 300)
    ids1 = tracker.update(1, [a])
    ids2 = tracker.update(2, [b])
    assert ids1 == [1]
    assert ids2 == [2]
