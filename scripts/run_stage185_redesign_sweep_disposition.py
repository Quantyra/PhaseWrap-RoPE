from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage185_redesign_sweep_disposition import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE181_RESULTS,
    DEFAULT_STAGE182_RESULTS,
    DEFAULT_STAGE183_RESULTS,
    DEFAULT_STAGE184_RESULTS,
    print_stage185_summary,
    run_stage185_redesign_sweep_disposition,
    write_stage185_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Synthesize Stage181 redesign sweep disposition after candidate screens.")
    parser.add_argument("--stage181-results", type=Path, default=DEFAULT_STAGE181_RESULTS)
    parser.add_argument("--stage182-results", type=Path, default=DEFAULT_STAGE182_RESULTS)
    parser.add_argument("--stage183-results", type=Path, default=DEFAULT_STAGE183_RESULTS)
    parser.add_argument("--stage184-results", type=Path, default=DEFAULT_STAGE184_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage185_redesign_sweep_disposition(
        stage181_results_path=args.stage181_results,
        stage182_results_path=args.stage182_results,
        stage183_results_path=args.stage183_results,
        stage184_results_path=args.stage184_results,
    )
    paths = write_stage185_outputs(result, args.output_dir)
    print_stage185_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
