from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage217_full_replacement_calibration_validation import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE216_RESULTS,
    print_stage217_summary,
    run_stage217_full_replacement_calibration_validation,
    write_stage217_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate full replacement known-state calibration counts.")
    parser.add_argument("--stage216-results", type=Path, default=DEFAULT_STAGE216_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage217_full_replacement_calibration_validation(stage216_results_path=args.stage216_results)
    paths = write_stage217_outputs(result, args.output_dir)
    print_stage217_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0 if not result["blockers"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
