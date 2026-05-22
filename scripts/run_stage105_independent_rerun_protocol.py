from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage105_independent_rerun_protocol import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE101_RESULTS,
    DEFAULT_STAGE103_MANIFEST,
    DEFAULT_STAGE104_MANIFEST,
    print_stage105_summary,
    run_stage105_protocol,
    write_stage105_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare Stage 105 independent rerun protocol.")
    parser.add_argument("--stage101-results", type=Path, default=DEFAULT_STAGE101_RESULTS)
    parser.add_argument("--stage103-manifest", type=Path, default=DEFAULT_STAGE103_MANIFEST)
    parser.add_argument("--stage104-manifest", type=Path, default=DEFAULT_STAGE104_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage105_protocol(
        stage101_results_path=args.stage101_results,
        stage103_manifest_path=args.stage103_manifest,
        stage104_manifest_path=args.stage104_manifest,
    )
    paths = write_stage105_outputs(result, args.output_dir)
    print_stage105_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    print(f"wrote {paths['rerun_windows']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
