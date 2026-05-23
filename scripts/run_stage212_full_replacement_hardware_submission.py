from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage212_full_replacement_hardware_submission import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE190_RESULTS,
    DEFAULT_STAGE211_RESULTS,
    print_stage212_summary,
    run_stage212_full_replacement_hardware_submission,
    write_stage212_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Submit full 4096-shot replacement IBM Runtime templates after all approval/readiness gates.")
    parser.add_argument("--stage211-results", type=Path, default=DEFAULT_STAGE211_RESULTS)
    parser.add_argument("--stage190-results", type=Path, default=DEFAULT_STAGE190_RESULTS)
    parser.add_argument("--allow-live-submit", action="store_true")
    parser.add_argument("--load-dotenv", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage212_full_replacement_hardware_submission(
        stage211_results_path=args.stage211_results,
        stage190_results_path=args.stage190_results,
        allow_live_submit=args.allow_live_submit,
        load_dotenv=args.load_dotenv,
    )
    paths = write_stage212_outputs(result, args.output_dir)
    print_stage212_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0 if not result["blockers"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
