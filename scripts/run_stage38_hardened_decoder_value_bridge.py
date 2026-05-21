from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage38_hardened_decoder_value_bridge import print_stage38_table, run_stage38_benchmark, write_stage38_outputs  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Stage 38 hardened decoder value-bridge benchmark.")
    parser.add_argument("--preflight", action="store_true", help="Run a tiny deterministic smoke benchmark.")
    args = parser.parse_args()
    if args.preflight:
        result = run_stage38_benchmark(
            data_seeds=(401,),
            model_seeds=(3803,),
            context_lengths=(128, 256, 512, 1024),
            examples_per_task_length=1,
            epochs=4,
            hidden_dim=8,
            value_embed_dim=8,
            method_names=("rope_relative", "phasewrap_multiscale_adapter"),
        )
    else:
        result = run_stage38_benchmark()
    paths = write_stage38_outputs(result)
    print_stage38_table(result)
    print(f"wrote {paths['manifest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
