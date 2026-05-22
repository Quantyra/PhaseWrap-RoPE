from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage209_reduced_scope_hardware_metric_interpreter import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE198_RESULTS,
    DEFAULT_STAGE207_RESULTS,
    DEFAULT_STAGE208_RESULTS,
    print_stage209_summary,
    run_stage209_reduced_scope_hardware_metric_interpreter,
    write_stage209_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Interpret reduced-scope IBM hardware metrics after calibration.")
    parser.add_argument("--stage198-results", type=Path, default=DEFAULT_STAGE198_RESULTS)
    parser.add_argument("--stage207-results", type=Path, default=DEFAULT_STAGE207_RESULTS)
    parser.add_argument("--stage208-results", type=Path, default=DEFAULT_STAGE208_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage209_reduced_scope_hardware_metric_interpreter(
        stage198_results_path=args.stage198_results,
        stage207_results_path=args.stage207_results,
        stage208_results_path=args.stage208_results,
    )
    paths = write_stage209_outputs(result, args.output_dir)
    print_stage209_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0 if not result["blockers"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
