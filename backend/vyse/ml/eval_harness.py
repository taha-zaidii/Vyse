"""Model evaluation. Reports mAP, per-class P/R, latency to a JSON file.

Usage:
    python -m vyse.ml.eval_harness --weights models/yolov8n.pt --data data/splits/data.yaml
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


def evaluate(weights: Path, data_yaml: Path, out: Path) -> dict:
    from ultralytics import YOLO  # type: ignore[import-untyped]

    model = YOLO(str(weights))
    t0 = time.perf_counter()
    metrics = model.val(data=str(data_yaml), verbose=False)
    dt = (time.perf_counter() - t0) * 1000.0
    report = {
        "weights": str(weights),
        "data_yaml": str(data_yaml),
        "map50": float(metrics.box.map50),
        "map50_95": float(metrics.box.map),
        "per_class": {
            str(name): {
                "precision": float(p),
                "recall": float(r),
            }
            for name, p, r in zip(
                metrics.names.values(), metrics.box.p, metrics.box.r, strict=False
            )
        },
        "eval_time_ms": dt,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return report


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--weights", type=Path, required=True)
    p.add_argument("--data", type=Path, required=True)
    p.add_argument("--out", type=Path, default=Path("eval_report.json"))
    args = p.parse_args()
    evaluate(args.weights, args.data, args.out)


if __name__ == "__main__":
    main()
