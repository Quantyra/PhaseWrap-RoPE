from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage125_provider_result_normalization_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE124_RESULTS,
    print_stage125_summary,
    run_stage125_audit,
    write_stage125_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit provider result normalization before guarded live SDK submission.")
    parser.add_argument("--stage124-results", type=Path, default=DEFAULT_STAGE124_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage125_audit(stage124_results_path=args.stage124_results)
    paths = write_stage125_outputs(result, args.output_dir)
    print_stage125_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
