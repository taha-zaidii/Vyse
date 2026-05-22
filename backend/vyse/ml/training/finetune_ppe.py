"""Fine-tune YOLOv8 on a Roboflow-format PPE dataset with W&B logging.

Usage:
    python -m vyse.ml.training.finetune_ppe \
        --data data/splits/data.yaml \
        --weights yolov8n.pt \
        --epochs 50 \
        --project vyse-ppe \
        --wandb-project vyse
"""

from __future__ import annotations

import argparse
from pathlib import Path


def train(args: argparse.Namespace) -> None:
    from ultralytics import YOLO  # type: ignore[import-untyped]

    try:
        import wandb  # type: ignore[import-not-found]

        wandb.init(project=args.wandb_project, name=args.project, config=vars(args))
    except ImportError:
        wandb = None  # type: ignore[assignment]

    model = YOLO(args.weights)
    model.train(
        data=args.data,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch=args.batch,
        project=str(args.runs_dir),
        name=args.project,
        device=args.device,
        patience=args.patience,
    )
    if wandb is not None:
        wandb.finish()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path, required=True)
    p.add_argument("--weights", type=str, default="yolov8n.pt")
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--batch", type=int, default=16)
    p.add_argument("--patience", type=int, default=10)
    p.add_argument("--device", type=str, default="0")
    p.add_argument("--project", type=str, default="vyse-ppe-finetune")
    p.add_argument("--runs-dir", type=Path, default=Path("runs"))
    p.add_argument("--wandb-project", type=str, default="vyse")
    train(p.parse_args())


if __name__ == "__main__":
    main()
