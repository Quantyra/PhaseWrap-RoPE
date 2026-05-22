from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage198_reduced_scope_preregistration import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE197_RESULTS,
    print_stage198_summary,
    run_stage198_reduced_scope_preregistration,
    write_stage198_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preregister reduced-scope replacement hardware interpretation boundary.")
    parser.add_argument("--stage197-results", type=Path, default=DEFAULT_STAGE197_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage198_reduced_scope_preregistration(stage197_results_path=args.stage197_results)
    paths = write_stage198_outputs(result, args.output_dir)
    print_stage198_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
