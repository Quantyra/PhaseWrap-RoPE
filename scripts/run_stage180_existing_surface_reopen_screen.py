from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage180_existing_surface_reopen_screen import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE100_MANIFEST,
    DEFAULT_STAGE177_RESULTS,
    DEFAULT_STAGE179_RESULTS,
    DEFAULT_STAGE99_MANIFEST,
    print_stage180_summary,
    run_stage180_existing_surface_reopen_screen,
    write_stage180_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Screen existing fixed-width packet surface for hardware-path reopen candidates.")
    parser.add_argument("--stage177-results", type=Path, default=DEFAULT_STAGE177_RESULTS)
    parser.add_argument("--stage179-results", type=Path, default=DEFAULT_STAGE179_RESULTS)
    parser.add_argument("--stage99-manifest", type=Path, default=DEFAULT_STAGE99_MANIFEST)
    parser.add_argument("--stage100-manifest", type=Path, default=DEFAULT_STAGE100_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage180_existing_surface_reopen_screen(
        stage177_results_path=args.stage177_results,
        stage179_results_path=args.stage179_results,
        stage99_manifest_path=args.stage99_manifest,
        stage100_manifest_path=args.stage100_manifest,
    )
    paths = write_stage180_outputs(result, args.output_dir)
    print_stage180_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
