from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage43_generator_hardened_pointer_sequence import print_stage43_table, run_stage43_benchmark, write_stage43_outputs  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Stage 43 generator-hardened pointer-generator sequence benchmark.")
    parser.add_argument("--preflight", action="store_true", help="Run a tiny deterministic smoke benchmark.")
    args = parser.parse_args()
    if args.preflight:
        result = run_stage43_benchmark(
            data_seeds=(401,),
            model_seeds=(4307,),
            context_lengths=(128, 256, 512, 1024, 2048),
            examples_per_task_length=1,
            epochs=4,
            hidden_dim=8,
            value_embed_dim=12,
            method_names=("rope_relative", "phasewrap_multiscale_adapter"),
        )
    else:
        result = run_stage43_benchmark()
    paths = write_stage43_outputs(result)
    print_stage43_table(result)
    print(f"wrote {paths['manifest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
