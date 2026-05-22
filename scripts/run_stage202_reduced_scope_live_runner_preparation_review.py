from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage202_reduced_scope_live_runner_preparation_review import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE193_RESULTS,
    DEFAULT_STAGE198_RESULTS,
    DEFAULT_STAGE201_RESULTS,
    print_stage202_summary,
    run_stage202_reduced_scope_live_runner_preparation_review,
    write_stage202_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review reduced-scope live-runner preparation readiness without submitting hardware.")
    parser.add_argument("--stage201-results", type=Path, default=DEFAULT_STAGE201_RESULTS)
    parser.add_argument("--stage198-results", type=Path, default=DEFAULT_STAGE198_RESULTS)
    parser.add_argument("--stage193-results", type=Path, default=DEFAULT_STAGE193_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage202_reduced_scope_live_runner_preparation_review(
        stage201_results_path=args.stage201_results,
        stage198_results_path=args.stage198_results,
        stage193_results_path=args.stage193_results,
    )
    paths = write_stage202_outputs(result, args.output_dir)
    print_stage202_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
