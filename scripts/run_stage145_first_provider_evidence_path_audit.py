from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage145_first_provider_evidence_path_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE113_RESULTS,
    DEFAULT_STAGE114_MANIFEST,
    DEFAULT_STAGE115_RESULTS,
    DEFAULT_STAGE133_RESULTS,
    DEFAULT_STAGE135_RESULTS,
    DEFAULT_STAGE137_RESULTS,
    DEFAULT_STAGE144_RESULTS,
    print_stage145_summary,
    run_stage145_audit,
    write_stage145_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit the first-provider evidence path after authorized execution.")
    parser.add_argument("--stage113-results", type=Path, default=DEFAULT_STAGE113_RESULTS)
    parser.add_argument("--stage114-manifest", type=Path, default=DEFAULT_STAGE114_MANIFEST)
    parser.add_argument("--stage115-results", type=Path, default=DEFAULT_STAGE115_RESULTS)
    parser.add_argument("--stage133-results", type=Path, default=DEFAULT_STAGE133_RESULTS)
    parser.add_argument("--stage135-results", type=Path, default=DEFAULT_STAGE135_RESULTS)
    parser.add_argument("--stage137-results", type=Path, default=DEFAULT_STAGE137_RESULTS)
    parser.add_argument("--stage144-results", type=Path, default=DEFAULT_STAGE144_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage145_audit(
        stage113_results_path=args.stage113_results,
        stage114_manifest_path=args.stage114_manifest,
        stage115_results_path=args.stage115_results,
        stage133_results_path=args.stage133_results,
        stage135_results_path=args.stage135_results,
        stage137_results_path=args.stage137_results,
        stage144_results_path=args.stage144_results,
    )
    paths = write_stage145_outputs(result, args.output_dir)
    print_stage145_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
