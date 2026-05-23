from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage211_full_replacement_guarded_runner_readiness import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE190_RESULTS,
    DEFAULT_STAGE193_RESULTS,
    DEFAULT_STAGE194_RESULTS,
    DEFAULT_STAGE195_RESULTS,
    print_stage211_summary,
    run_stage211_full_replacement_guarded_runner_readiness,
    write_stage211_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check full 4096-shot replacement guarded runner readiness without submitting hardware.")
    parser.add_argument("--stage190-results", type=Path, default=DEFAULT_STAGE190_RESULTS)
    parser.add_argument("--stage193-results", type=Path, default=DEFAULT_STAGE193_RESULTS)
    parser.add_argument("--stage194-results", type=Path, default=DEFAULT_STAGE194_RESULTS)
    parser.add_argument("--stage195-results", type=Path, default=DEFAULT_STAGE195_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage211_full_replacement_guarded_runner_readiness(
        stage190_results_path=args.stage190_results,
        stage193_results_path=args.stage193_results,
        stage194_results_path=args.stage194_results,
        stage195_results_path=args.stage195_results,
    )
    paths = write_stage211_outputs(result, args.output_dir)
    print_stage211_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0 if not result["blockers"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
