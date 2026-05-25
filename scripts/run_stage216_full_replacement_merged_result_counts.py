from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage216_full_replacement_merged_result_counts import (  # noqa: E402
    DEFAULT_ORIGINAL_STAGE214_RESULTS,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_REPLACEMENT_STAGE214_RESULTS,
    print_stage216_summary,
    run_stage216_full_replacement_merged_result_counts,
    write_stage216_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Merge original and allocated-instance full replacement result counts.")
    parser.add_argument("--original-stage214-results", type=Path, default=DEFAULT_ORIGINAL_STAGE214_RESULTS)
    parser.add_argument("--replacement-stage214-results", type=Path, default=DEFAULT_REPLACEMENT_STAGE214_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage216_full_replacement_merged_result_counts(
        original_stage214_results_path=args.original_stage214_results,
        replacement_stage214_results_path=args.replacement_stage214_results,
    )
    paths = write_stage216_outputs(result, args.output_dir)
    print_stage216_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0 if not result["blockers"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
