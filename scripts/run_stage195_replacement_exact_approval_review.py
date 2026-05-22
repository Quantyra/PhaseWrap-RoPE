from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage195_replacement_exact_approval_review import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE194_RESULTS,
    print_stage195_summary,
    run_stage195_replacement_exact_approval_review,
    write_stage195_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review exact replacement approval phrase without submitting hardware.")
    parser.add_argument("--stage194-results", type=Path, default=DEFAULT_STAGE194_RESULTS)
    parser.add_argument("--provided-approval-phrase", default=None)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage195_replacement_exact_approval_review(
        stage194_results_path=args.stage194_results,
        provided_approval_phrase=args.provided_approval_phrase,
    )
    paths = write_stage195_outputs(result, args.output_dir)
    print_stage195_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
