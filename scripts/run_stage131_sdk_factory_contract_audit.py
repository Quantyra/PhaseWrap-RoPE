from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage131_sdk_factory_contract_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE130_RESULTS,
    print_stage131_summary,
    run_stage131_audit,
    write_stage131_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit provider SDK live-client factory contracts.")
    parser.add_argument("--stage130-results", type=Path, default=DEFAULT_STAGE130_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage131_audit(stage130_results_path=args.stage130_results)
    paths = write_stage131_outputs(result, args.output_dir)
    print_stage131_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
