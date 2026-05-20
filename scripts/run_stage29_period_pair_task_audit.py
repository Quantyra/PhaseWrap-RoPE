from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage12_ruler_retrieval import DEFAULT_EXAMPLES_PER_TASK_LENGTH  # noqa: E402
from qrope.stage29_period_pair_task_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SEEDS,
    LOCAL_CONTEXT_LENGTHS,
    LONG_CONTEXT_LENGTHS,
    print_stage29_table,
    run_stage29_audit,
    write_stage29_outputs,
)


def _parse_int_list(raw: str) -> tuple[int, ...]:
    values = tuple(int(item.strip()) for item in raw.split(",") if item.strip())
    if not values:
        raise argparse.ArgumentTypeError("expected at least one integer")
    return values


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Stage 29 period-pair task audit.")
    parser.add_argument("--seeds", type=_parse_int_list, default=DEFAULT_SEEDS)
    parser.add_argument("--local-context-lengths", type=_parse_int_list, default=LOCAL_CONTEXT_LENGTHS)
    parser.add_argument("--long-context-lengths", type=_parse_int_list, default=LONG_CONTEXT_LENGTHS)
    parser.add_argument("--examples-per-task-length", type=int, default=DEFAULT_EXAMPLES_PER_TASK_LENGTH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage29_audit(
        seeds=args.seeds,
        local_context_lengths=args.local_context_lengths,
        long_context_lengths=args.long_context_lengths,
        examples_per_task_length=args.examples_per_task_length,
    )
    paths = write_stage29_outputs(result, args.output_dir)
    print_stage29_table(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['results']}")
    print(f"wrote {paths['local_summary_csv']}")
    print(f"wrote {paths['long_summary_csv']}")
    print(f"wrote {paths['task_summary_csv']}")
    print(f"wrote {paths['length_summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
