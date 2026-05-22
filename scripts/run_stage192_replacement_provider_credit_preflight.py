from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.env_utils import load_local_dotenv  # noqa: E402
from qrope.stage192_replacement_provider_credit_preflight import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE159_RESULTS,
    DEFAULT_STAGE176_RESULTS,
    DEFAULT_STAGE191_RESULTS,
    print_stage192_summary,
    run_stage192_replacement_provider_credit_preflight,
    write_stage192_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build no-submit replacement-run IBM provider and credit preflight.")
    parser.add_argument("--stage159-results", type=Path, default=DEFAULT_STAGE159_RESULTS)
    parser.add_argument("--stage176-results", type=Path, default=DEFAULT_STAGE176_RESULTS)
    parser.add_argument("--stage191-results", type=Path, default=DEFAULT_STAGE191_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--load-dotenv", action="store_true")
    args = parser.parse_args(argv)
    if args.load_dotenv:
        load_local_dotenv(REPO_ROOT / ".env")
    result = run_stage192_replacement_provider_credit_preflight(
        stage159_results_path=args.stage159_results,
        stage176_results_path=args.stage176_results,
        stage191_results_path=args.stage191_results,
    )
    paths = write_stage192_outputs(result, args.output_dir)
    print_stage192_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
