from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage132_guarded_sdk_factory_implementation_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE128_RESULTS,
    DEFAULT_STAGE129_RESULTS,
    DEFAULT_STAGE131_RESULTS,
    print_stage132_summary,
    run_stage132_audit,
    write_stage132_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit guarded provider SDK factory implementation state.")
    parser.add_argument("--stage128-results", type=Path, default=DEFAULT_STAGE128_RESULTS)
    parser.add_argument("--stage129-results", type=Path, default=DEFAULT_STAGE129_RESULTS)
    parser.add_argument("--stage131-results", type=Path, default=DEFAULT_STAGE131_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage132_audit(
        stage128_results_path=args.stage128_results,
        stage129_results_path=args.stage129_results,
        stage131_results_path=args.stage131_results,
    )
    paths = write_stage132_outputs(result, args.output_dir)
    print_stage132_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
