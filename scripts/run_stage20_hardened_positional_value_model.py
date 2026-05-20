from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage20_hardened_positional_value_model import (  # noqa: E402
    DEFAULT_CONTEXT_LENGTHS,
    DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SEEDS,
    print_stage20_table,
    run_stage20_benchmark,
    write_stage20_outputs,
)


def _parse_int_list(raw: str) -> tuple[int, ...]:
    values = tuple(int(item.strip()) for item in raw.split(",") if item.strip())
    if not values:
        raise argparse.ArgumentTypeError("expected at least one integer")
    return values


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic Stage 20 hardened positional value-model comparison.")
    parser.add_argument("--seeds", type=_parse_int_list, default=DEFAULT_SEEDS)
    parser.add_argument("--context-lengths", type=_parse_int_list, default=DEFAULT_CONTEXT_LENGTHS)
    parser.add_argument("--examples-per-task-length", type=int, default=DEFAULT_EXAMPLES_PER_TASK_LENGTH)
    parser.add_argument("--epochs", type=int, default=500)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage20_benchmark(
        seeds=args.seeds,
        context_lengths=args.context_lengths,
        examples_per_task_length=args.examples_per_task_length,
        epochs=args.epochs,
    )
    paths = write_stage20_outputs(result, args.output_dir)
    print_stage20_table(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['results']}")
    print(f"wrote {paths['summary_csv']}")
    print(f"wrote {paths['task_summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
