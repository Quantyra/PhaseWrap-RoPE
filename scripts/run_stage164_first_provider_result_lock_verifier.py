from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage164_first_provider_result_lock_verifier import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE163_RESULTS,
    print_stage164_summary,
    run_stage164_result_lock_verifier,
    write_stage164_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify provider results against the first-provider pre-run lock.")
    parser.add_argument("--stage163-results", type=Path, default=DEFAULT_STAGE163_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage164_result_lock_verifier(stage163_results_path=args.stage163_results)
    paths = write_stage164_outputs(result, args.output_dir)
    print_stage164_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
