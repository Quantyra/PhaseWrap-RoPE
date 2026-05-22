from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage203_reduced_scope_execution_package import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE190_RESULTS,
    DEFAULT_STAGE198_RESULTS,
    DEFAULT_STAGE202_RESULTS,
    print_stage203_summary,
    run_stage203_reduced_scope_execution_package,
    write_stage203_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build reduced-scope 2048-shot execution package without submitting hardware.")
    parser.add_argument("--stage202-results", type=Path, default=DEFAULT_STAGE202_RESULTS)
    parser.add_argument("--stage198-results", type=Path, default=DEFAULT_STAGE198_RESULTS)
    parser.add_argument("--stage190-results", type=Path, default=DEFAULT_STAGE190_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage203_reduced_scope_execution_package(
        stage202_results_path=args.stage202_results,
        stage198_results_path=args.stage198_results,
        stage190_results_path=args.stage190_results,
    )
    paths = write_stage203_outputs(result, args.output_dir)
    print_stage203_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    print(f"wrote {paths['template_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
