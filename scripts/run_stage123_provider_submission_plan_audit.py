from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage123_provider_submission_plan_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE118_RESULTS,
    DEFAULT_STAGE122_RESULTS,
    print_stage123_summary,
    run_stage123_audit,
    write_stage123_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit provider SDK submission plans from Stage 118 payloads.")
    parser.add_argument("--stage118-results", type=Path, default=DEFAULT_STAGE118_RESULTS)
    parser.add_argument("--stage122-results", type=Path, default=DEFAULT_STAGE122_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage123_audit(stage118_results_path=args.stage118_results, stage122_results_path=args.stage122_results)
    paths = write_stage123_outputs(result, args.output_dir)
    print_stage123_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
