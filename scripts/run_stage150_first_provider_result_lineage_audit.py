from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage150_first_provider_result_lineage_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE112_JOB_MANIFEST,
    DEFAULT_STAGE114_MANIFEST,
    DEFAULT_STAGE145_RESULTS,
    DEFAULT_STAGE148_RESULTS,
    DEFAULT_STAGE149_RESULTS,
    print_stage150_summary,
    run_stage150_audit,
    write_stage150_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit first-provider result lineage before provider result interpretation.")
    parser.add_argument("--stage112-job-manifest", type=Path, default=DEFAULT_STAGE112_JOB_MANIFEST)
    parser.add_argument("--stage114-manifest", type=Path, default=DEFAULT_STAGE114_MANIFEST)
    parser.add_argument("--stage145-results", type=Path, default=DEFAULT_STAGE145_RESULTS)
    parser.add_argument("--stage148-results", type=Path, default=DEFAULT_STAGE148_RESULTS)
    parser.add_argument("--stage149-results", type=Path, default=DEFAULT_STAGE149_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage150_audit(
        stage112_job_manifest_path=args.stage112_job_manifest,
        stage114_manifest_path=args.stage114_manifest,
        stage145_results_path=args.stage145_results,
        stage148_results_path=args.stage148_results,
        stage149_results_path=args.stage149_results,
    )
    paths = write_stage150_outputs(result, args.output_dir)
    print_stage150_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
