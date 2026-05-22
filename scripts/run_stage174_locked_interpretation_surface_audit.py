from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage174_locked_interpretation_surface_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE104_RESULTS,
    DEFAULT_STAGE163_RESULTS,
    DEFAULT_STAGE169_RESULTS,
    DEFAULT_STAGE173_RESULTS,
    print_stage174_summary,
    run_stage174_locked_interpretation_surface_audit,
    write_stage174_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit the locked IBM interpretation surface before provider results exist.")
    parser.add_argument("--stage104-results", type=Path, default=DEFAULT_STAGE104_RESULTS)
    parser.add_argument("--stage163-results", type=Path, default=DEFAULT_STAGE163_RESULTS)
    parser.add_argument("--stage169-results", type=Path, default=DEFAULT_STAGE169_RESULTS)
    parser.add_argument("--stage173-results", type=Path, default=DEFAULT_STAGE173_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage174_locked_interpretation_surface_audit(
        stage104_results_path=args.stage104_results,
        stage163_results_path=args.stage163_results,
        stage169_results_path=args.stage169_results,
        stage173_results_path=args.stage173_results,
    )
    paths = write_stage174_outputs(result, args.output_dir)
    print_stage174_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
