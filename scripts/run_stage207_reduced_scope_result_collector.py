from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage207_reduced_scope_result_collector import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE203_RESULTS,
    DEFAULT_STAGE205_RESULTS,
    print_stage207_summary,
    run_stage207_reduced_scope_result_collector,
    write_stage207_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collect reduced-scope IBM Runtime result counts for completed jobs.")
    parser.add_argument("--stage205-results", type=Path, default=DEFAULT_STAGE205_RESULTS)
    parser.add_argument("--stage203-results", type=Path, default=DEFAULT_STAGE203_RESULTS)
    parser.add_argument("--load-dotenv", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage207_reduced_scope_result_collector(
        stage205_results_path=args.stage205_results,
        stage203_results_path=args.stage203_results,
        load_dotenv=args.load_dotenv,
    )
    paths = write_stage207_outputs(result, args.output_dir)
    print_stage207_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0 if not result["blockers"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
