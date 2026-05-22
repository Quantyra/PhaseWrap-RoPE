from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage86_dual_auxiliary_budget_sensitivity_audit import (  # noqa: E402
    DEFAULT_AUDIT_SEEDS,
    DEFAULT_EPOCH_BUDGETS,
    DEFAULT_EXAMPLES_PER_LENGTH,
    DEFAULT_LEARNING_RATE,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SUPPORT_AUX_WEIGHT,
    DEFAULT_TARGET_ATTENTION_AUX_WEIGHT,
    print_stage86_summary,
    run_stage86_audit,
    write_stage86_outputs,
)


def _parse_int_list(raw: str) -> tuple[int, ...]:
    values = tuple(int(item.strip()) for item in raw.split(",") if item.strip())
    if not values:
        raise argparse.ArgumentTypeError("expected at least one integer")
    return values


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Stage 86 dual-auxiliary budget sensitivity audit.")
    parser.add_argument("--epoch-budgets", type=_parse_int_list, default=DEFAULT_EPOCH_BUDGETS)
    parser.add_argument("--seeds", type=_parse_int_list, default=DEFAULT_AUDIT_SEEDS)
    parser.add_argument("--examples-per-length", type=int, default=DEFAULT_EXAMPLES_PER_LENGTH)
    parser.add_argument("--learning-rate", type=float, default=DEFAULT_LEARNING_RATE)
    parser.add_argument("--support-aux-weight", type=float, default=DEFAULT_SUPPORT_AUX_WEIGHT)
    parser.add_argument("--target-attention-aux-weight", type=float, default=DEFAULT_TARGET_ATTENTION_AUX_WEIGHT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage86_audit(
        epoch_budgets=args.epoch_budgets,
        seeds=args.seeds,
        examples_per_length=args.examples_per_length,
        learning_rate=args.learning_rate,
        support_aux_weight=args.support_aux_weight,
        target_attention_aux_weight=args.target_attention_aux_weight,
    )
    paths = write_stage86_outputs(result, args.output_dir)
    print_stage86_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
