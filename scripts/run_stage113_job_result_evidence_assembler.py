from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage113_job_result_evidence_assembler import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_PROVIDER_RESULTS,
    DEFAULT_STAGE112_JOB_MANIFEST,
    print_stage113_summary,
    run_stage113_assembler,
    write_stage113_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Assemble Stage 112 provider job results into Stage 109 evidence files.")
    parser.add_argument("--stage112-job-manifest", type=Path, default=DEFAULT_STAGE112_JOB_MANIFEST)
    parser.add_argument("--provider-results", type=Path, default=DEFAULT_PROVIDER_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--write-evidence", action="store_true")
    args = parser.parse_args(argv)

    result = run_stage113_assembler(
        stage112_job_manifest_path=args.stage112_job_manifest,
        provider_results_path=args.provider_results,
        write_evidence=args.write_evidence,
    )
    paths = write_stage113_outputs(result, args.output_dir)
    print_stage113_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
