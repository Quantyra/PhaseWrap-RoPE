from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage128_sdk_client_factory_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE106_RESULTS,
    DEFAULT_STAGE111_RESULTS,
    DEFAULT_STAGE127_RESULTS,
    print_stage128_summary,
    run_stage128_audit,
    write_stage128_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit guarded provider SDK client factory boundaries.")
    parser.add_argument("--stage106-results", type=Path, default=DEFAULT_STAGE106_RESULTS)
    parser.add_argument("--stage111-results", type=Path, default=DEFAULT_STAGE111_RESULTS)
    parser.add_argument("--stage127-results", type=Path, default=DEFAULT_STAGE127_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage128_audit(
        stage106_results_path=args.stage106_results,
        stage111_results_path=args.stage111_results,
        stage127_results_path=args.stage127_results,
    )
    paths = write_stage128_outputs(result, args.output_dir)
    print_stage128_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
