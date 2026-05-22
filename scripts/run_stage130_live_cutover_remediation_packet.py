from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage130_live_cutover_remediation_packet import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE106_RESULTS,
    DEFAULT_STAGE111_RESULTS,
    DEFAULT_STAGE128_RESULTS,
    DEFAULT_STAGE129_RESULTS,
    print_stage130_summary,
    run_stage130_packet,
    write_stage130_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a non-secret live cutover remediation packet.")
    parser.add_argument("--stage106-results", type=Path, default=DEFAULT_STAGE106_RESULTS)
    parser.add_argument("--stage111-results", type=Path, default=DEFAULT_STAGE111_RESULTS)
    parser.add_argument("--stage128-results", type=Path, default=DEFAULT_STAGE128_RESULTS)
    parser.add_argument("--stage129-results", type=Path, default=DEFAULT_STAGE129_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage130_packet(
        stage106_results_path=args.stage106_results,
        stage111_results_path=args.stage111_results,
        stage128_results_path=args.stage128_results,
        stage129_results_path=args.stage129_results,
    )
    paths = write_stage130_outputs(result, args.output_dir)
    print_stage130_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    print(f"wrote {paths['remediation_packet']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
