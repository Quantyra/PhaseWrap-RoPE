from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage158_first_provider_pre_execution_sanity import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE133_RESULTS,
    DEFAULT_STAGE157_RESULTS,
    print_stage158_summary,
    run_stage158_pre_execution_sanity,
    write_stage158_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check first-provider live-run pre-execution sanity without submission.")
    parser.add_argument("--stage133-results", type=Path, default=DEFAULT_STAGE133_RESULTS)
    parser.add_argument("--stage157-results", type=Path, default=DEFAULT_STAGE157_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage158_pre_execution_sanity(
        stage133_results_path=args.stage133_results,
        stage157_results_path=args.stage157_results,
    )
    paths = write_stage158_outputs(result, args.output_dir)
    print_stage158_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
