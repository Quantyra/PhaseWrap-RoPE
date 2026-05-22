from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage129_live_cutover_authorization_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE106_RESULTS,
    DEFAULT_STAGE111_RESULTS,
    DEFAULT_STAGE128_RESULTS,
    print_stage129_summary,
    run_stage129_audit,
    write_stage129_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit whether provider live SDK client cutover is authorized.")
    parser.add_argument("--stage106-results", type=Path, default=DEFAULT_STAGE106_RESULTS)
    parser.add_argument("--stage111-results", type=Path, default=DEFAULT_STAGE111_RESULTS)
    parser.add_argument("--stage128-results", type=Path, default=DEFAULT_STAGE128_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage129_audit(
        stage106_results_path=args.stage106_results,
        stage111_results_path=args.stage111_results,
        stage128_results_path=args.stage128_results,
    )
    paths = write_stage129_outputs(result, args.output_dir)
    print_stage129_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
