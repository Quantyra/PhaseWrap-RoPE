from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage191_replacement_approval_dossier import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE176_RESULTS,
    DEFAULT_STAGE188_RESULTS,
    DEFAULT_STAGE189_RESULTS,
    DEFAULT_STAGE190_RESULTS,
    print_stage191_summary,
    run_stage191_replacement_approval_dossier,
    write_stage191_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build no-submit replacement-run approval dossier.")
    parser.add_argument("--stage176-results", type=Path, default=DEFAULT_STAGE176_RESULTS)
    parser.add_argument("--stage188-results", type=Path, default=DEFAULT_STAGE188_RESULTS)
    parser.add_argument("--stage189-results", type=Path, default=DEFAULT_STAGE189_RESULTS)
    parser.add_argument("--stage190-results", type=Path, default=DEFAULT_STAGE190_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage191_replacement_approval_dossier(
        stage176_results_path=args.stage176_results,
        stage188_results_path=args.stage188_results,
        stage189_results_path=args.stage189_results,
        stage190_results_path=args.stage190_results,
    )
    paths = write_stage191_outputs(result, args.output_dir)
    print_stage191_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
