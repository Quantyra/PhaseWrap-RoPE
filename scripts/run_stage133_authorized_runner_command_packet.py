from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage133_authorized_runner_command_packet import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE116_RESULTS,
    DEFAULT_STAGE129_RESULTS,
    DEFAULT_STAGE132_RESULTS,
    print_stage133_summary,
    run_stage133_packet,
    write_stage133_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare authorized provider runner command templates.")
    parser.add_argument("--stage116-results", type=Path, default=DEFAULT_STAGE116_RESULTS)
    parser.add_argument("--stage129-results", type=Path, default=DEFAULT_STAGE129_RESULTS)
    parser.add_argument("--stage132-results", type=Path, default=DEFAULT_STAGE132_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage133_packet(
        stage116_results_path=args.stage116_results,
        stage129_results_path=args.stage129_results,
        stage132_results_path=args.stage132_results,
    )
    paths = write_stage133_outputs(result, args.output_dir)
    print_stage133_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
