from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage156_first_provider_live_run_pause import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE133_RESULTS,
    DEFAULT_STAGE152_RESULTS,
    print_stage156_summary,
    run_stage156_live_run_pause,
    write_stage156_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Record the explicit pause before first-provider live hardware run.")
    parser.add_argument("--stage133-results", type=Path, default=DEFAULT_STAGE133_RESULTS)
    parser.add_argument("--stage152-results", type=Path, default=DEFAULT_STAGE152_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage156_live_run_pause(
        stage133_results_path=args.stage133_results,
        stage152_results_path=args.stage152_results,
    )
    paths = write_stage156_outputs(result, args.output_dir)
    print_stage156_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
