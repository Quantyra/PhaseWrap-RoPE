from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage160_first_provider_post_run_analysis_packet import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE113_RESULTS,
    DEFAULT_STAGE115_RESULTS,
    DEFAULT_STAGE135_RESULTS,
    DEFAULT_STAGE159_RESULTS,
    DEFAULT_STAGE164_RESULTS,
    print_stage160_summary,
    run_stage160_post_run_analysis_packet,
    write_stage160_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare the no-submit first-provider post-run analysis sequence.")
    parser.add_argument("--stage159-results", type=Path, default=DEFAULT_STAGE159_RESULTS)
    parser.add_argument("--stage164-results", type=Path, default=DEFAULT_STAGE164_RESULTS)
    parser.add_argument("--stage115-results", type=Path, default=DEFAULT_STAGE115_RESULTS)
    parser.add_argument("--stage113-results", type=Path, default=DEFAULT_STAGE113_RESULTS)
    parser.add_argument("--stage135-results", type=Path, default=DEFAULT_STAGE135_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage160_post_run_analysis_packet(
        stage159_results_path=args.stage159_results,
        stage164_results_path=args.stage164_results,
        stage115_results_path=args.stage115_results,
        stage113_results_path=args.stage113_results,
        stage135_results_path=args.stage135_results,
    )
    paths = write_stage160_outputs(result, args.output_dir)
    print_stage160_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
