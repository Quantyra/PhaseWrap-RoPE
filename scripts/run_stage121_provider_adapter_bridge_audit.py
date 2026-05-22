from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage121_provider_adapter_bridge_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE120_RESULTS,
    print_stage121_summary,
    run_stage121_audit,
    write_stage121_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit provider adapter import-path bridge for guarded live runners.")
    parser.add_argument("--stage120-results", type=Path, default=DEFAULT_STAGE120_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage121_audit(stage120_results_path=args.stage120_results)
    paths = write_stage121_outputs(result, args.output_dir)
    print_stage121_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
