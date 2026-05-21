from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage75_learned_query_support_head_audit import (  # noqa: E402
    DEFAULT_AUDIT_SEEDS,
    DEFAULT_EXAMPLES_PER_LENGTH,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SUPPORT_HEAD_EPOCHS,
    DEFAULT_SUPPORT_HEAD_LEARNING_RATE,
    print_stage75_summary,
    run_stage75_audit,
    write_stage75_outputs,
)


def _parse_int_list(raw: str) -> tuple[int, ...]:
    values = tuple(int(item.strip()) for item in raw.split(",") if item.strip())
    if not values:
        raise argparse.ArgumentTypeError("expected at least one integer")
    return values


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Stage 75 learned query-support head audit.")
    parser.add_argument("--seeds", type=_parse_int_list, default=DEFAULT_AUDIT_SEEDS)
    parser.add_argument("--examples-per-length", type=int, default=DEFAULT_EXAMPLES_PER_LENGTH)
    parser.add_argument("--support-head-epochs", type=int, default=DEFAULT_SUPPORT_HEAD_EPOCHS)
    parser.add_argument("--support-head-learning-rate", type=float, default=DEFAULT_SUPPORT_HEAD_LEARNING_RATE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage75_audit(
        seeds=args.seeds,
        examples_per_length=args.examples_per_length,
        support_head_epochs=args.support_head_epochs,
        support_head_learning_rate=args.support_head_learning_rate,
    )
    paths = write_stage75_outputs(result, args.output_dir)
    print_stage75_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    print(f"wrote {paths['per_run_csv']}")
    print(f"wrote {paths['failed_runs']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
