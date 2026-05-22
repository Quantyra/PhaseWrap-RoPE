from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage101_known_state_calibration_gate import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE100_MANIFEST,
    DEFAULT_STAGE4_CALIBRATION_MANIFEST,
    DEFAULT_STAGE4_CALIBRATION_VERIFICATION,
    DEFAULT_STAGE99_MANIFEST,
    MIN_DOMINANT_FRACTION,
    print_stage101_summary,
    run_stage101_gate,
    write_stage101_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Stage 101 known-state calibration evidence gate.")
    parser.add_argument("--stage99-manifest", type=Path, default=DEFAULT_STAGE99_MANIFEST)
    parser.add_argument("--stage100-manifest", type=Path, default=DEFAULT_STAGE100_MANIFEST)
    parser.add_argument("--calibration-manifest", type=Path, default=DEFAULT_STAGE4_CALIBRATION_MANIFEST)
    parser.add_argument("--calibration-verification", type=Path, default=DEFAULT_STAGE4_CALIBRATION_VERIFICATION)
    parser.add_argument("--execution-dir", type=Path, default=None)
    parser.add_argument("--min-dominant-fraction", type=float, default=MIN_DOMINANT_FRACTION)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage101_gate(
        stage99_manifest_path=args.stage99_manifest,
        stage100_manifest_path=args.stage100_manifest,
        calibration_manifest_path=args.calibration_manifest,
        calibration_verification_path=args.calibration_verification,
        execution_dir=args.execution_dir,
        min_dominant_fraction=args.min_dominant_fraction,
    )
    paths = write_stage101_outputs(result, args.output_dir)
    print_stage101_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
