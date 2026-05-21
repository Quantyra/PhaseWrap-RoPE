from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage45_matched_decoder_only_gate import (  # noqa: E402
    DEFAULT_EPOCHS,
    DEFAULT_OUTPUT_DIR,
    EXAMPLES_PER_LENGTH,
    print_stage45_summary,
    run_stage45_gate,
    write_stage45_outputs,
)


def _parse_int_list(raw: str) -> tuple[int, ...]:
    values = tuple(int(item.strip()) for item in raw.split(",") if item.strip())
    if not values:
        raise argparse.ArgumentTypeError("expected at least one integer")
    return values


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Stage 45 matched decoder-only transformer gate.")
    parser.add_argument("--seeds", type=_parse_int_list, default=None)
    parser.add_argument("--examples-per-length", type=int, default=EXAMPLES_PER_LENGTH)
    parser.add_argument("--epochs", type=int, default=DEFAULT_EPOCHS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--strict", action="store_true", help="Return non-zero if the optional transformer dependency is missing.")
    args = parser.parse_args(argv)

    kwargs = {"examples_per_length": args.examples_per_length, "epochs": args.epochs}
    if args.seeds is not None:
        kwargs["seeds"] = args.seeds
    result = run_stage45_gate(**kwargs)
    paths = write_stage45_outputs(result, args.output_dir)
    print_stage45_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    if "per_seed_csv" in paths:
        print(f"wrote {paths['per_seed_csv']}")
    if "failed_runs" in paths:
        print(f"wrote {paths['failed_runs']}")
    if args.strict and result["status"] != "completed":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
