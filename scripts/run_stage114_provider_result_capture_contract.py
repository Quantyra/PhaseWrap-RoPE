from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage114_provider_result_capture_contract import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE112_JOB_MANIFEST,
    DEFAULT_STAGE113_MANIFEST,
    _load_jsonl,
    print_stage114_summary,
    run_stage114_contract,
    write_stage114_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare provider result capture contract and job shards for Stage 112 jobs.")
    parser.add_argument("--stage112-job-manifest", type=Path, default=DEFAULT_STAGE112_JOB_MANIFEST)
    parser.add_argument("--stage113-manifest", type=Path, default=DEFAULT_STAGE113_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage114_contract(stage112_job_manifest_path=args.stage112_job_manifest, stage113_manifest_path=args.stage113_manifest)
    paths = write_stage114_outputs(result, _load_jsonl(args.stage112_job_manifest) or [], args.output_dir)
    print_stage114_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    print(f"wrote {paths['schema']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
