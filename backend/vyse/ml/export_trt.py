"""ONNX → TensorRT engine. Requires `tensorrt` (install separately, GPU only).

Usage:
    python -m vyse.ml.export_trt --onnx models/exports/ppe.onnx --engine models/exports/ppe.engine
"""

from __future__ import annotations

import argparse
from pathlib import Path


def build_engine(onnx_path: Path, engine_path: Path, fp16: bool = True) -> Path:
    try:
        import tensorrt as trt  # type: ignore[import-not-found]
    except ImportError as e:
        raise SystemExit(
            "tensorrt not installed — install on a GPU machine: "
            "`pip install nvidia-tensorrt` or use the NVIDIA container."
        ) from e

    logger = trt.Logger(trt.Logger.WARNING)
    builder = trt.Builder(logger)
    network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
    parser = trt.OnnxParser(network, logger)
    with onnx_path.open("rb") as f:
        if not parser.parse(f.read()):
            for i in range(parser.num_errors):
                print(parser.get_error(i))
            raise SystemExit("ONNX parse failed")
    config = builder.create_builder_config()
    config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, 2 << 30)
    if fp16 and builder.platform_has_fast_fp16:
        config.set_flag(trt.BuilderFlag.FP16)
    serialized = builder.build_serialized_network(network, config)
    engine_path.parent.mkdir(parents=True, exist_ok=True)
    engine_path.write_bytes(bytes(serialized))
    print(f"[ok] engine → {engine_path}")
    return engine_path


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--onnx", type=Path, required=True)
    p.add_argument("--engine", type=Path, required=True)
    p.add_argument("--fp16", action="store_true", default=True)
    args = p.parse_args()
    build_engine(args.onnx, args.engine, args.fp16)


if __name__ == "__main__":
    main()
