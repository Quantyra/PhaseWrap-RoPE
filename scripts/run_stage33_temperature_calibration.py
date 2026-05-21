from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage33_temperature_calibration import print_stage33_table, run_stage33_benchmark, write_stage33_outputs  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Stage 33 temperature-calibration audit.")
    parser.add_argument("--preflight", action="store_true", help="Run a tiny deterministic smoke benchmark.")
    args = parser.parse_args()
    if args.preflight:
        result = run_stage33_benchmark(
            data_seeds=(401,),
            model_seeds=(3203,),
            context_lengths=(128, 256, 512, 1024),
            examples_per_task_length=1,
            epochs=3,
            method_names=("rope_relative", "phasewrap_multiscale_adapter"),
        )
    else:
        result = run_stage33_benchmark()
    paths = write_stage33_outputs(result)
    print_stage33_table(result)
    print(f"wrote {paths['manifest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
