from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage109_window_evidence_intake_validator import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE107_WINDOW_PLANS,
    print_stage109_summary,
    run_stage109_intake_validator,
    write_stage109_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate filled Stage 107 window evidence before aggregation.")
    parser.add_argument("--stage107-window-plans", type=Path, default=DEFAULT_STAGE107_WINDOW_PLANS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage109_intake_validator(stage107_window_plans_path=args.stage107_window_plans)
    paths = write_stage109_outputs(result, args.output_dir)
    print_stage109_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
