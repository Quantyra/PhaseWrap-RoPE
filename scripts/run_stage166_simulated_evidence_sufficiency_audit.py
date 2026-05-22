from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage166_simulated_evidence_sufficiency_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE100_MANIFEST,
    DEFAULT_STAGE153_RESULTS,
    DEFAULT_STAGE165_RESULTS,
    DEFAULT_STAGE99_MANIFEST,
    print_stage166_summary,
    run_stage166_sufficiency_audit,
    write_stage166_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit simulated evidence sufficiency for targeted versus broad claims.")
    parser.add_argument("--stage99-manifest", type=Path, default=DEFAULT_STAGE99_MANIFEST)
    parser.add_argument("--stage100-manifest", type=Path, default=DEFAULT_STAGE100_MANIFEST)
    parser.add_argument("--stage153-results", type=Path, default=DEFAULT_STAGE153_RESULTS)
    parser.add_argument("--stage165-results", type=Path, default=DEFAULT_STAGE165_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage166_sufficiency_audit(
        stage99_manifest_path=args.stage99_manifest,
        stage100_manifest_path=args.stage100_manifest,
        stage153_results_path=args.stage153_results,
        stage165_results_path=args.stage165_results,
    )
    paths = write_stage166_outputs(result, args.output_dir)
    print_stage166_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
