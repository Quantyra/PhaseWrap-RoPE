from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage42_trainable_pointer_generator_sequence import print_stage42_table, run_stage42_benchmark, write_stage42_outputs  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Stage 42 trainable pointer-generator sequence benchmark.")
    parser.add_argument("--preflight", action="store_true", help="Run a tiny deterministic smoke benchmark.")
    args = parser.parse_args()
    if args.preflight:
        result = run_stage42_benchmark(
            data_seeds=(401,),
            model_seeds=(4201,),
            context_lengths=(128, 256, 512, 1024, 2048),
            examples_per_task_length=1,
            epochs=4,
            hidden_dim=8,
            value_embed_dim=12,
            method_names=("rope_relative", "phasewrap_multiscale_adapter"),
        )
    else:
        result = run_stage42_benchmark()
    paths = write_stage42_outputs(result)
    print_stage42_table(result)
    print(f"wrote {paths['manifest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
