from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage149_first_provider_guarded_runner_contract_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE111_RESULTS,
    DEFAULT_STAGE118_RESULTS,
    DEFAULT_STAGE129_RESULTS,
    DEFAULT_STAGE133_RESULTS,
    DEFAULT_STAGE145_RESULTS,
    print_stage149_summary,
    run_stage149_audit,
    write_stage149_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit first-provider guarded runner result-contract behavior.")
    parser.add_argument("--stage111-results", type=Path, default=DEFAULT_STAGE111_RESULTS)
    parser.add_argument("--stage118-results", type=Path, default=DEFAULT_STAGE118_RESULTS)
    parser.add_argument("--stage129-results", type=Path, default=DEFAULT_STAGE129_RESULTS)
    parser.add_argument("--stage133-results", type=Path, default=DEFAULT_STAGE133_RESULTS)
    parser.add_argument("--stage145-results", type=Path, default=DEFAULT_STAGE145_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage149_audit(
        stage111_results_path=args.stage111_results,
        stage118_results_path=args.stage118_results,
        stage129_results_path=args.stage129_results,
        stage133_results_path=args.stage133_results,
        stage145_results_path=args.stage145_results,
    )
    paths = write_stage149_outputs(result, args.output_dir)
    print_stage149_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
