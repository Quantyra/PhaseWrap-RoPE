from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage138_objective_claim_gate import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE110_RESULTS,
    DEFAULT_STAGE137_RESULTS,
    print_stage138_summary,
    run_stage138_claim_gate,
    write_stage138_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gate the final PhaseWrap noisy-hardware robustness-or-auditability objective claim.")
    parser.add_argument("--stage110-results", type=Path, default=DEFAULT_STAGE110_RESULTS)
    parser.add_argument("--stage137-results", type=Path, default=DEFAULT_STAGE137_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage138_claim_gate(stage110_results_path=args.stage110_results, stage137_results_path=args.stage137_results)
    paths = write_stage138_outputs(result, args.output_dir)
    print_stage138_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
