from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage26_compact_kv_qa import (  # noqa: E402
    CONTEXT_LENGTHS,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SEEDS,
    EXAMPLES_PER_LENGTH,
    print_stage26_table,
    run_stage26_benchmark,
    write_stage26_outputs,
)


def _parse_int_list(raw: str) -> tuple[int, ...]:
    values = tuple(int(item.strip()) for item in raw.split(",") if item.strip())
    if not values:
        raise argparse.ArgumentTypeError("expected at least one integer")
    return values


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic Stage 26 compact key-value QA retrieval benchmark.")
    parser.add_argument("--seeds", type=_parse_int_list, default=DEFAULT_SEEDS)
    parser.add_argument("--context-lengths", type=_parse_int_list, default=CONTEXT_LENGTHS)
    parser.add_argument("--examples-per-length", type=int, default=EXAMPLES_PER_LENGTH)
    parser.add_argument("--epochs", type=int, default=260)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage26_benchmark(
        seeds=args.seeds,
        context_lengths=args.context_lengths,
        examples_per_length=args.examples_per_length,
        epochs=args.epochs,
    )
    paths = write_stage26_outputs(result, args.output_dir)
    print_stage26_table(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['results']}")
    print(f"wrote {paths['summary_csv']}")
    print(f"wrote {paths['weak_runs']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
