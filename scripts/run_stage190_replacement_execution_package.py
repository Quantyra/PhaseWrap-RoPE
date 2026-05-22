from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage190_replacement_execution_package import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE188_RESULTS,
    DEFAULT_STAGE189_RESULTS,
    print_stage190_summary,
    run_stage190_replacement_execution_package,
    write_stage190_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build no-submit replacement-semantics execution package.")
    parser.add_argument("--stage188-results", type=Path, default=DEFAULT_STAGE188_RESULTS)
    parser.add_argument("--stage189-results", type=Path, default=DEFAULT_STAGE189_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage190_replacement_execution_package(
        stage188_results_path=args.stage188_results,
        stage189_results_path=args.stage189_results,
    )
    paths = write_stage190_outputs(result, args.output_dir)
    print_stage190_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    print(f"wrote {paths['template_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
