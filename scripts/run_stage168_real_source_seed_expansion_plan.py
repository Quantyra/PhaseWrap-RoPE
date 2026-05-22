from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage168_real_source_seed_expansion_plan import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE4_MANIFEST,
    DEFAULT_STAGE167_RESULTS,
    print_stage168_summary,
    run_stage168_expansion_plan,
    write_stage168_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Plan real source-seed expansion before broadening hardware scope.")
    parser.add_argument("--stage4-manifest", type=Path, default=DEFAULT_STAGE4_MANIFEST)
    parser.add_argument("--stage167-results", type=Path, default=DEFAULT_STAGE167_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage168_expansion_plan(
        stage4_manifest_path=args.stage4_manifest,
        stage167_results_path=args.stage167_results,
    )
    paths = write_stage168_outputs(result, args.output_dir)
    print_stage168_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
