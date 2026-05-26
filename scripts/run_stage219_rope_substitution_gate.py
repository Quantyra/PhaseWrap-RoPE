from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage219_rope_substitution_gate import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    STAGE30_RESULTS_PATH,
    STAGE32_RESULTS_PATH,
    print_stage219_summary,
    run_stage219_rope_substitution_gate,
    write_stage219_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the bounded Stage 219 ranking-parity bridge interpreter.")
    parser.add_argument("--stage30-results", type=Path, default=STAGE30_RESULTS_PATH)
    parser.add_argument("--stage32-results", type=Path, default=STAGE32_RESULTS_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage219_rope_substitution_gate(
        stage30_results_path=args.stage30_results,
        stage32_results_path=args.stage32_results,
    )
    write_stage219_outputs(result, args.output_dir)
    print_stage219_summary(result)
    return 0 if not result["blockers"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
