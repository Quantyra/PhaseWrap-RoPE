from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage146_first_provider_shot_uncertainty_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE107_WINDOW_PLANS,
    DEFAULT_STAGE145_RESULTS,
    print_stage146_summary,
    run_stage146_audit,
    write_stage146_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit first-provider shot-noise uncertainty thresholds.")
    parser.add_argument("--stage107-window-plans", type=Path, default=DEFAULT_STAGE107_WINDOW_PLANS)
    parser.add_argument("--stage145-results", type=Path, default=DEFAULT_STAGE145_RESULTS)
    parser.add_argument("--provider", default=None)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage146_audit(
        stage107_window_plans_path=args.stage107_window_plans,
        stage145_results_path=args.stage145_results,
        provider=args.provider,
    )
    paths = write_stage146_outputs(result, args.output_dir)
    print_stage146_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
