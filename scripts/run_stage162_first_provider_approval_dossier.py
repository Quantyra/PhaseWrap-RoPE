from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage162_first_provider_approval_dossier import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE154_RESULTS,
    DEFAULT_STAGE157_RESULTS,
    DEFAULT_STAGE159_RESULTS,
    DEFAULT_STAGE160_RESULTS,
    DEFAULT_STAGE161_RESULTS,
    print_stage162_summary,
    run_stage162_approval_dossier,
    write_stage162_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a no-submit first-provider hardware approval dossier.")
    parser.add_argument("--stage154-results", type=Path, default=DEFAULT_STAGE154_RESULTS)
    parser.add_argument("--stage157-results", type=Path, default=DEFAULT_STAGE157_RESULTS)
    parser.add_argument("--stage159-results", type=Path, default=DEFAULT_STAGE159_RESULTS)
    parser.add_argument("--stage160-results", type=Path, default=DEFAULT_STAGE160_RESULTS)
    parser.add_argument("--stage161-results", type=Path, default=DEFAULT_STAGE161_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage162_approval_dossier(
        stage154_results_path=args.stage154_results,
        stage157_results_path=args.stage157_results,
        stage159_results_path=args.stage159_results,
        stage160_results_path=args.stage160_results,
        stage161_results_path=args.stage161_results,
    )
    paths = write_stage162_outputs(result, args.output_dir)
    print_stage162_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
