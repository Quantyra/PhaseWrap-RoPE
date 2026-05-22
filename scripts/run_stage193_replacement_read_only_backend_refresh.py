from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage193_replacement_read_only_backend_refresh import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE191_RESULTS,
    DEFAULT_STAGE192_RESULTS,
    print_stage193_summary,
    run_stage193_replacement_read_only_backend_refresh,
    write_stage193_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refresh replacement-scoped IBM backend metadata without submitting hardware jobs.")
    parser.add_argument("--stage191-results", type=Path, default=DEFAULT_STAGE191_RESULTS)
    parser.add_argument("--stage192-results", type=Path, default=DEFAULT_STAGE192_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--allow-read-only-refresh", action="store_true")
    args = parser.parse_args(argv)
    result = run_stage193_replacement_read_only_backend_refresh(
        stage191_results_path=args.stage191_results,
        stage192_results_path=args.stage192_results,
        allow_read_only_refresh=args.allow_read_only_refresh,
    )
    paths = write_stage193_outputs(result, args.output_dir)
    print_stage193_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
