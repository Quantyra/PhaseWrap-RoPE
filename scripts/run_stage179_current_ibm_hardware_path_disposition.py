from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage179_current_ibm_hardware_path_disposition import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE169_RESULTS,
    DEFAULT_STAGE176_RESULTS,
    DEFAULT_STAGE177_RESULTS,
    DEFAULT_STAGE178_RESULTS,
    print_stage179_summary,
    run_stage179_current_ibm_hardware_path_disposition,
    write_stage179_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Record the current locked IBM hardware path disposition.")
    parser.add_argument("--stage169-results", type=Path, default=DEFAULT_STAGE169_RESULTS)
    parser.add_argument("--stage176-results", type=Path, default=DEFAULT_STAGE176_RESULTS)
    parser.add_argument("--stage177-results", type=Path, default=DEFAULT_STAGE177_RESULTS)
    parser.add_argument("--stage178-results", type=Path, default=DEFAULT_STAGE178_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage179_current_ibm_hardware_path_disposition(
        stage169_results_path=args.stage169_results,
        stage176_results_path=args.stage176_results,
        stage177_results_path=args.stage177_results,
        stage178_results_path=args.stage178_results,
    )
    paths = write_stage179_outputs(result, args.output_dir)
    print_stage179_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
