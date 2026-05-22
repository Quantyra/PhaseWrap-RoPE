from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage196_replacement_cost_estimate_packet import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE194_RESULTS,
    print_stage196_summary,
    run_stage196_replacement_cost_estimate_packet,
    write_stage196_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build replacement-run cost estimate packet before credit attestation.")
    parser.add_argument("--stage194-results", type=Path, default=DEFAULT_STAGE194_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage196_replacement_cost_estimate_packet(stage194_results_path=args.stage194_results)
    paths = write_stage196_outputs(result, args.output_dir)
    print_stage196_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    print(f"wrote {paths['scenarios_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
