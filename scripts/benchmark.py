"""Mini benchmark — measure detector latency on a sample image.

Usage:
    python scripts/benchmark.py path/to/image.jpg --iters 100
"""

from __future__ import annotations

import argparse
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

import cv2  # type: ignore[import-untyped]  # noqa: E402

from vyse.detectors.ppe_detector import PPEDetector  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("image", type=Path)
    p.add_argument("--iters", type=int, default=50)
    args = p.parse_args()

    img = cv2.imread(str(args.image))
    if img is None:
        raise SystemExit(f"can't read {args.image}")

    det = PPEDetector()
    # warmup
    for _ in range(5):
        det.infer(img)

    times = []
    for _ in range(args.iters):
        t0 = time.perf_counter()
        det.infer(img)
        times.append((time.perf_counter() - t0) * 1000.0)

    print(
        f"YOLOv8 inference over {args.iters} iters:\n"
        f"  mean   {statistics.mean(times):.1f} ms\n"
        f"  median {statistics.median(times):.1f} ms\n"
        f"  p95    {statistics.quantiles(times, n=20)[-1]:.1f} ms\n"
        f"  min    {min(times):.1f} ms\n"
        f"  max    {max(times):.1f} ms"
    )


if __name__ == "__main__":
    main()
