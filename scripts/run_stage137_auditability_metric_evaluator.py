from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage137_auditability_metric_evaluator import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE107_WINDOW_PLANS,
    DEFAULT_STAGE136_RESULTS,
    print_stage137_summary,
    run_stage137_evaluator,
    write_stage137_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate component-reconstruction auditability metrics from provider counts.")
    parser.add_argument("--stage107-window-plans", type=Path, default=DEFAULT_STAGE107_WINDOW_PLANS)
    parser.add_argument("--stage136-results", type=Path, default=DEFAULT_STAGE136_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--provider", default=None)
    args = parser.parse_args(argv)

    result = run_stage137_evaluator(
        stage107_window_plans_path=args.stage107_window_plans,
        stage136_results_path=args.stage136_results,
        provider=args.provider,
    )
    paths = write_stage137_outputs(result, args.output_dir)
    print_stage137_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
