from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage126_stage114_result_record_builder_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE114_SCHEMA,
    DEFAULT_STAGE123_RESULTS,
    DEFAULT_STAGE125_RESULTS,
    print_stage126_summary,
    run_stage126_audit,
    write_stage126_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit Stage 114 result-record assembly from provider plans and normalized counts.")
    parser.add_argument("--stage114-schema", type=Path, default=DEFAULT_STAGE114_SCHEMA)
    parser.add_argument("--stage123-results", type=Path, default=DEFAULT_STAGE123_RESULTS)
    parser.add_argument("--stage125-results", type=Path, default=DEFAULT_STAGE125_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage126_audit(
        stage114_schema_path=args.stage114_schema,
        stage123_results_path=args.stage123_results,
        stage125_results_path=args.stage125_results,
    )
    paths = write_stage126_outputs(result, args.output_dir)
    print_stage126_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
