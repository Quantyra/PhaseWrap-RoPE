from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage170_ibm_hardware_pause_resolution_packet import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE159_RESULTS,
    DEFAULT_STAGE161_RESULTS,
    DEFAULT_STAGE162_RESULTS,
    DEFAULT_STAGE163_RESULTS,
    DEFAULT_STAGE169_RESULTS,
    print_stage170_summary,
    run_stage170_pause_packet,
    write_stage170_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the non-submitting IBM hardware pause resolution packet.")
    parser.add_argument("--stage159-results", type=Path, default=DEFAULT_STAGE159_RESULTS)
    parser.add_argument("--stage161-results", type=Path, default=DEFAULT_STAGE161_RESULTS)
    parser.add_argument("--stage162-results", type=Path, default=DEFAULT_STAGE162_RESULTS)
    parser.add_argument("--stage163-results", type=Path, default=DEFAULT_STAGE163_RESULTS)
    parser.add_argument("--stage169-results", type=Path, default=DEFAULT_STAGE169_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage170_pause_packet(
        stage159_results_path=args.stage159_results,
        stage161_results_path=args.stage161_results,
        stage162_results_path=args.stage162_results,
        stage163_results_path=args.stage163_results,
        stage169_results_path=args.stage169_results,
    )
    paths = write_stage170_outputs(result, args.output_dir)
    print_stage170_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
