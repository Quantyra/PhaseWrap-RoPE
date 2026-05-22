from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage110_replicated_advantage_claim_gate import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE105_MANIFEST,
    DEFAULT_STAGE109_RESULTS,
    print_stage110_summary,
    run_stage110_claim_gate,
    write_stage110_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gate replicated PhaseWrap noisy-hardware advantage claims.")
    parser.add_argument("--stage105-manifest", type=Path, default=DEFAULT_STAGE105_MANIFEST)
    parser.add_argument("--stage109-results", type=Path, default=DEFAULT_STAGE109_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage110_claim_gate(stage105_manifest_path=args.stage105_manifest, stage109_results_path=args.stage109_results)
    paths = write_stage110_outputs(result, args.output_dir)
    print_stage110_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
