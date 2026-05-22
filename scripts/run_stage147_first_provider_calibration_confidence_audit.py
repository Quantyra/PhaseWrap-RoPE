from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage147_first_provider_calibration_confidence_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE102_TEMPLATE_DIR,
    DEFAULT_STAGE145_RESULTS,
    print_stage147_summary,
    run_stage147_audit,
    write_stage147_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit first-provider known-state calibration confidence thresholds.")
    parser.add_argument("--stage102-template-dir", type=Path, default=DEFAULT_STAGE102_TEMPLATE_DIR)
    parser.add_argument("--stage145-results", type=Path, default=DEFAULT_STAGE145_RESULTS)
    parser.add_argument("--provider", default=None)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage147_audit(
        stage102_template_dir=args.stage102_template_dir,
        stage145_results_path=args.stage145_results,
        provider=args.provider,
    )
    paths = write_stage147_outputs(result, args.output_dir)
    print_stage147_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
