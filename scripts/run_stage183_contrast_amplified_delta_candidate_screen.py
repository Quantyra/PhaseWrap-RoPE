from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage183_contrast_amplified_delta_candidate_screen import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE177_RESULTS,
    DEFAULT_STAGE181_RESULTS,
    print_stage183_summary,
    run_stage183_contrast_amplified_delta_candidate_screen,
    write_stage183_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Screen the Stage183 contrast-amplified delta candidate under IBM-informed noise.")
    parser.add_argument("--stage177-results", type=Path, default=DEFAULT_STAGE177_RESULTS)
    parser.add_argument("--stage181-results", type=Path, default=DEFAULT_STAGE181_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage183_contrast_amplified_delta_candidate_screen(
        stage177_results_path=args.stage177_results,
        stage181_results_path=args.stage181_results,
    )
    paths = write_stage183_outputs(result, args.output_dir)
    print_stage183_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    print(f"wrote {paths['packet_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
