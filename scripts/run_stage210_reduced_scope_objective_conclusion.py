from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage210_reduced_scope_objective_conclusion import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE198_RESULTS,
    DEFAULT_STAGE208_RESULTS,
    DEFAULT_STAGE209_RESULTS,
    print_stage210_summary,
    run_stage210_reduced_scope_objective_conclusion,
    write_stage210_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write the reduced-scope hardware objective conclusion.")
    parser.add_argument("--stage198-results", type=Path, default=DEFAULT_STAGE198_RESULTS)
    parser.add_argument("--stage208-results", type=Path, default=DEFAULT_STAGE208_RESULTS)
    parser.add_argument("--stage209-results", type=Path, default=DEFAULT_STAGE209_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage210_reduced_scope_objective_conclusion(
        stage198_results_path=args.stage198_results,
        stage208_results_path=args.stage208_results,
        stage209_results_path=args.stage209_results,
    )
    paths = write_stage210_outputs(result, args.output_dir)
    print_stage210_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0 if not result["blockers"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
