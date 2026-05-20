from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage7_toy_transformer_ablation import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    print_stage7_table,
    run_toy_transformer_ablation,
    write_stage7_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic Stage 7 toy transformer ablation.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_toy_transformer_ablation(seed=args.seed)
    paths = write_stage7_outputs(result, args.output_dir)
    print_stage7_table(result)
    print(f"best_method: {result['best_method']}")
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['results']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
