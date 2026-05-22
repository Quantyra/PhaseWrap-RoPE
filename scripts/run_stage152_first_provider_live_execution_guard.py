from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage152_first_provider_live_execution_guard import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE133_RESULTS,
    DEFAULT_STAGE151_RESULTS,
    print_stage152_summary,
    run_stage152_guard,
    write_stage152_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Guard first-provider live execution behind command authorization and metadata readiness.")
    parser.add_argument("--stage133-results", type=Path, default=DEFAULT_STAGE133_RESULTS)
    parser.add_argument("--stage151-results", type=Path, default=DEFAULT_STAGE151_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage152_guard(stage133_results_path=args.stage133_results, stage151_results_path=args.stage151_results)
    paths = write_stage152_outputs(result, args.output_dir)
    print_stage152_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
