from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage56_standard_input_cue_copy_audit import (  # noqa: E402
    DEFAULT_AUDIT_SEEDS,
    DEFAULT_OUTPUT_DIR,
    print_stage56_summary,
    run_stage56_audit,
    write_stage56_outputs,
)


def _parse_int_list(raw: str) -> tuple[int, ...]:
    values = tuple(int(item.strip()) for item in raw.split(",") if item.strip())
    if not values:
        raise argparse.ArgumentTypeError("expected at least one integer")
    return values


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Stage 56 standard-input cue-copy audit.")
    parser.add_argument("--seeds", type=_parse_int_list, default=DEFAULT_AUDIT_SEEDS)
    parser.add_argument("--examples-per-length", type=int, default=2)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage56_audit(seeds=args.seeds, examples_per_length=args.examples_per_length)
    paths = write_stage56_outputs(result, args.output_dir)
    print_stage56_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    print(f"wrote {paths['per_run_csv']}")
    print(f"wrote {paths['failed_runs']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
