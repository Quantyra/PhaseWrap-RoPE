from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage91_curriculum_teacher_distilled_pointer_generator_audit import (  # noqa: E402
    DEFAULT_AUDIT_SEEDS,
    DEFAULT_EPOCHS,
    DEFAULT_EXAMPLES_PER_LENGTH,
    DEFAULT_LEARNING_RATE,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SUPPORT_AUX_WEIGHT,
    DEFAULT_TARGET_ATTENTION_AUX_WEIGHT,
    DEFAULT_TEACHER_DISTILLATION_WEIGHT,
    print_stage91_summary,
    run_stage91_audit,
    write_stage91_outputs,
)


def _parse_int_list(raw: str) -> tuple[int, ...]:
    values = tuple(int(item.strip()) for item in raw.split(",") if item.strip())
    if not values:
        raise argparse.ArgumentTypeError("expected at least one integer")
    return values


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Stage 91 curriculum teacher-distilled pointer-generator audit.")
    parser.add_argument("--seeds", type=_parse_int_list, default=DEFAULT_AUDIT_SEEDS)
    parser.add_argument("--examples-per-length", type=int, default=DEFAULT_EXAMPLES_PER_LENGTH)
    parser.add_argument("--epochs", type=int, default=DEFAULT_EPOCHS)
    parser.add_argument("--learning-rate", type=float, default=DEFAULT_LEARNING_RATE)
    parser.add_argument("--support-aux-weight", type=float, default=DEFAULT_SUPPORT_AUX_WEIGHT)
    parser.add_argument("--target-attention-aux-weight", type=float, default=DEFAULT_TARGET_ATTENTION_AUX_WEIGHT)
    parser.add_argument("--teacher-distillation-weight", type=float, default=DEFAULT_TEACHER_DISTILLATION_WEIGHT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage91_audit(
        seeds=args.seeds,
        examples_per_length=args.examples_per_length,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        support_aux_weight=args.support_aux_weight,
        target_attention_aux_weight=args.target_attention_aux_weight,
        teacher_distillation_weight=args.teacher_distillation_weight,
    )
    paths = write_stage91_outputs(result, args.output_dir)
    print_stage91_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    if "per_run_csv" in paths:
        print(f"wrote {paths['per_run_csv']}")
    if "failed_runs" in paths:
        print(f"wrote {paths['failed_runs']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

