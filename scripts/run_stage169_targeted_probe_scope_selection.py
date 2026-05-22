from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage169_targeted_probe_scope_selection import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE163_RESULTS,
    DEFAULT_STAGE165_RESULTS,
    print_stage169_summary,
    run_stage169_scope_selection,
    write_stage169_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Select the current no-submit targeted IBM probe scope.")
    parser.add_argument("--stage165-results", type=Path, default=DEFAULT_STAGE165_RESULTS)
    parser.add_argument("--stage163-results", type=Path, default=DEFAULT_STAGE163_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage169_scope_selection(
        stage165_results_path=args.stage165_results,
        stage163_results_path=args.stage163_results,
    )
    paths = write_stage169_outputs(result, args.output_dir)
    print_stage169_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
