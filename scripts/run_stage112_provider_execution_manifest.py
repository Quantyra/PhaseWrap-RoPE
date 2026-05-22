from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage112_provider_execution_manifest import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE107_WINDOW_PLANS,
    DEFAULT_STAGE111_RESULTS,
    print_stage112_summary,
    run_stage112_manifest,
    write_stage112_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a no-submission provider execution manifest for Stage 107 windows.")
    parser.add_argument("--stage107-window-plans", type=Path, default=DEFAULT_STAGE107_WINDOW_PLANS)
    parser.add_argument("--stage111-results", type=Path, default=DEFAULT_STAGE111_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage112_manifest(stage107_window_plans_path=args.stage107_window_plans, stage111_results_path=args.stage111_results)
    paths = write_stage112_outputs(result, args.output_dir)
    print_stage112_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    print(f"wrote {paths['job_manifest_jsonl']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
