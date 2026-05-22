from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage208_reduced_scope_calibration_validation import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE207_RESULTS,
    print_stage208_summary,
    run_stage208_reduced_scope_calibration_validation,
    write_stage208_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate reduced-scope known-state calibration before hardware metric interpretation.")
    parser.add_argument("--stage207-results", type=Path, default=DEFAULT_STAGE207_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage208_reduced_scope_calibration_validation(stage207_results_path=args.stage207_results)
    paths = write_stage208_outputs(result, args.output_dir)
    print_stage208_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0 if not result["blockers"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
