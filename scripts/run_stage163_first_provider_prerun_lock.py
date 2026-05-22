from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage163_first_provider_prerun_lock import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE114_OUTPUT_DIR,
    DEFAULT_STAGE157_RESULTS,
    DEFAULT_STAGE162_RESULTS,
    print_stage163_summary,
    run_stage163_prerun_lock,
    write_stage163_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lock approved first-provider job shards before live execution.")
    parser.add_argument("--stage157-results", type=Path, default=DEFAULT_STAGE157_RESULTS)
    parser.add_argument("--stage162-results", type=Path, default=DEFAULT_STAGE162_RESULTS)
    parser.add_argument("--stage114-output-dir", type=Path, default=DEFAULT_STAGE114_OUTPUT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage163_prerun_lock(
        stage157_results_path=args.stage157_results,
        stage162_results_path=args.stage162_results,
        stage114_output_dir=args.stage114_output_dir,
    )
    paths = write_stage163_outputs(result, args.output_dir)
    print_stage163_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
