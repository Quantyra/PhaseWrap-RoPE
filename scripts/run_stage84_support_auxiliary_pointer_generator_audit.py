from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage84_support_auxiliary_pointer_generator_audit import (  # noqa: E402
    DEFAULT_AUDIT_SEEDS,
    DEFAULT_EPOCHS,
    DEFAULT_EXAMPLES_PER_LENGTH,
    DEFAULT_LEARNING_RATE,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SUPPORT_AUX_WEIGHT,
    print_stage84_summary,
    run_stage84_audit,
    write_stage84_outputs,
)


def _parse_int_list(raw: str) -> tuple[int, ...]:
    values = tuple(int(item.strip()) for item in raw.split(",") if item.strip())
    if not values:
        raise argparse.ArgumentTypeError("expected at least one integer")
    return values


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Stage 84 support-auxiliary pointer-generator audit.")
    parser.add_argument("--seeds", type=_parse_int_list, default=DEFAULT_AUDIT_SEEDS)
    parser.add_argument("--examples-per-length", type=int, default=DEFAULT_EXAMPLES_PER_LENGTH)
    parser.add_argument("--epochs", type=int, default=DEFAULT_EPOCHS)
    parser.add_argument("--learning-rate", type=float, default=DEFAULT_LEARNING_RATE)
    parser.add_argument("--support-aux-weight", type=float, default=DEFAULT_SUPPORT_AUX_WEIGHT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage84_audit(
        seeds=args.seeds,
        examples_per_length=args.examples_per_length,
        epochs=args.epochs,
        learning_rate=args.learning_rate,
        support_aux_weight=args.support_aux_weight,
    )
    paths = write_stage84_outputs(result, args.output_dir)
    print_stage84_summary(result)
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
