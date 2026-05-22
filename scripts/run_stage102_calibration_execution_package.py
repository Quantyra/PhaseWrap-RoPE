from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage102_calibration_execution_package import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE101_RESULTS,
    print_stage102_summary,
    run_stage102_package,
    write_stage102_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare Stage 102 known-state calibration execution templates.")
    parser.add_argument("--stage101-results", type=Path, default=DEFAULT_STAGE101_RESULTS)
    parser.add_argument("--shots-per-state", type=int, default=1000)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage102_package(stage101_results_path=args.stage101_results, shots_per_state=args.shots_per_state)
    paths = write_stage102_outputs(result, args.output_dir)
    print_stage102_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    print(f"wrote templates under {paths['template_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
