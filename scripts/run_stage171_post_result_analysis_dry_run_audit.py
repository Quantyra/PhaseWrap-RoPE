from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage171_post_result_analysis_dry_run_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SCRIPT_ROOT,
    DEFAULT_STAGE160_RESULTS,
    DEFAULT_STAGE170_RESULTS,
    print_stage171_summary,
    run_stage171_dry_run_audit,
    write_stage171_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the no-submit post-result analysis command sequence.")
    parser.add_argument("--stage160-results", type=Path, default=DEFAULT_STAGE160_RESULTS)
    parser.add_argument("--stage170-results", type=Path, default=DEFAULT_STAGE170_RESULTS)
    parser.add_argument("--script-root", type=Path, default=DEFAULT_SCRIPT_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage171_dry_run_audit(
        stage160_results_path=args.stage160_results,
        stage170_results_path=args.stage170_results,
        script_root=args.script_root,
    )
    paths = write_stage171_outputs(result, args.output_dir)
    print_stage171_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
