from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage187_replacement_semantics_preregistration import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE186_RESULTS,
    print_stage187_summary,
    run_stage187_replacement_semantics_preregistration,
    write_stage187_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preregister replacement target/control semantics after Stage186.")
    parser.add_argument("--stage186-results", type=Path, default=DEFAULT_STAGE186_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage187_replacement_semantics_preregistration(stage186_results_path=args.stage186_results)
    paths = write_stage187_outputs(result, args.output_dir)
    print_stage187_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
