from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage176_ibm_credit_provider_resolution_handoff import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE159_RESULTS,
    DEFAULT_STAGE170_RESULTS,
    DEFAULT_STAGE175_RESULTS,
    print_stage176_summary,
    run_stage176_resolution_handoff,
    write_stage176_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare the no-secret IBM credit/provider resolution handoff.")
    parser.add_argument("--stage159-results", type=Path, default=DEFAULT_STAGE159_RESULTS)
    parser.add_argument("--stage170-results", type=Path, default=DEFAULT_STAGE170_RESULTS)
    parser.add_argument("--stage175-results", type=Path, default=DEFAULT_STAGE175_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage176_resolution_handoff(
        stage159_results_path=args.stage159_results,
        stage170_results_path=args.stage170_results,
        stage175_results_path=args.stage175_results,
    )
    paths = write_stage176_outputs(result, args.output_dir)
    print_stage176_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
