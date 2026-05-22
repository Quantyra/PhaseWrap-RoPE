from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage197_replacement_cost_constrained_scope_review import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE188_RESULTS,
    DEFAULT_STAGE196_RESULTS,
    print_stage197_summary,
    run_stage197_replacement_cost_constrained_scope_review,
    write_stage197_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review cost-constrained replacement hardware scope options.")
    parser.add_argument("--stage188-results", type=Path, default=DEFAULT_STAGE188_RESULTS)
    parser.add_argument("--stage196-results", type=Path, default=DEFAULT_STAGE196_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage197_replacement_cost_constrained_scope_review(
        stage188_results_path=args.stage188_results,
        stage196_results_path=args.stage196_results,
    )
    paths = write_stage197_outputs(result, args.output_dir)
    print_stage197_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    print(f"wrote {paths['scope_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
