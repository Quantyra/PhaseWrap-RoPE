from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage116_provider_runner_plan import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE111_RESULTS,
    DEFAULT_STAGE114_MANIFEST,
    DEFAULT_STAGE118_RESULTS,
    DEFAULT_STAGE129_RESULTS,
    print_stage116_summary,
    run_stage116_runner_plan,
    write_stage116_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare provider runner commands for Stage 114 job shards.")
    parser.add_argument("--stage111-results", type=Path, default=DEFAULT_STAGE111_RESULTS)
    parser.add_argument("--stage114-manifest", type=Path, default=DEFAULT_STAGE114_MANIFEST)
    parser.add_argument("--stage118-results", type=Path, default=DEFAULT_STAGE118_RESULTS)
    parser.add_argument("--stage129-results", type=Path, default=DEFAULT_STAGE129_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage116_runner_plan(
        stage111_results_path=args.stage111_results,
        stage114_manifest_path=args.stage114_manifest,
        stage118_results_path=args.stage118_results,
        stage129_results_path=args.stage129_results,
    )
    paths = write_stage116_outputs(result, args.output_dir)
    print_stage116_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
