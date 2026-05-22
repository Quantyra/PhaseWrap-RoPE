from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage181_fixed_width_target_redesign_plan import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE177_RESULTS,
    DEFAULT_STAGE179_RESULTS,
    DEFAULT_STAGE180_RESULTS,
    print_stage181_summary,
    run_stage181_fixed_width_target_redesign_plan,
    write_stage181_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare fixed-width target/circuit redesign plan after IBM path archive.")
    parser.add_argument("--stage177-results", type=Path, default=DEFAULT_STAGE177_RESULTS)
    parser.add_argument("--stage179-results", type=Path, default=DEFAULT_STAGE179_RESULTS)
    parser.add_argument("--stage180-results", type=Path, default=DEFAULT_STAGE180_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage181_fixed_width_target_redesign_plan(
        stage177_results_path=args.stage177_results,
        stage179_results_path=args.stage179_results,
        stage180_results_path=args.stage180_results,
    )
    paths = write_stage181_outputs(result, args.output_dir)
    print_stage181_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
