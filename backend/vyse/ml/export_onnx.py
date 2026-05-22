"""Export an Ultralytics YOLOv8 .pt → ONNX for portable / CPU-fast inference.

Usage:
    python -m vyse.ml.export_onnx --weights models/yolov8n.pt --out models/exports/ppe.onnx
"""

from __future__ import annotations

import argparse
from pathlib import Path


def export(weights: Path, out: Path, imgsz: int = 640, opset: int = 12) -> Path:
    from ultralytics import YOLO  # type: ignore[import-untyped]

    out.parent.mkdir(parents=True, exist_ok=True)
    model = YOLO(str(weights))
    exported = model.export(format="onnx", imgsz=imgsz, opset=opset, dynamic=True)
    exported_path = Path(exported)
    if exported_path != out:
        exported_path.rename(out)
    print(f"[ok] exported → {out}")
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--weights", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--opset", type=int, default=12)
    args = p.parse_args()
    export(args.weights, args.out, args.imgsz, args.opset)


if __name__ == "__main__":
    main()
