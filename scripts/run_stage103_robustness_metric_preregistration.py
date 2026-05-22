from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage103_robustness_metric_preregistration import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE100_MANIFEST,
    DEFAULT_STAGE101_RESULTS,
    DEFAULT_STAGE102_MANIFEST,
    DEFAULT_STAGE104_RESULTS,
    DEFAULT_STAGE99_MANIFEST,
    print_stage103_summary,
    run_stage103_preregistration,
    write_stage103_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Stage 103 robustness metric preregistration.")
    parser.add_argument("--stage99-manifest", type=Path, default=DEFAULT_STAGE99_MANIFEST)
    parser.add_argument("--stage100-manifest", type=Path, default=DEFAULT_STAGE100_MANIFEST)
    parser.add_argument("--stage101-results", type=Path, default=DEFAULT_STAGE101_RESULTS)
    parser.add_argument("--stage102-manifest", type=Path, default=DEFAULT_STAGE102_MANIFEST)
    parser.add_argument("--stage104-results", type=Path, default=DEFAULT_STAGE104_RESULTS)
    parser.add_argument("--execution-dir", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage103_preregistration(
        stage99_manifest_path=args.stage99_manifest,
        stage100_manifest_path=args.stage100_manifest,
        stage101_results_path=args.stage101_results,
        stage102_manifest_path=args.stage102_manifest,
        stage104_results_path=args.stage104_results,
        execution_dir=args.execution_dir,
    )
    paths = write_stage103_outputs(result, args.output_dir)
    print_stage103_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
