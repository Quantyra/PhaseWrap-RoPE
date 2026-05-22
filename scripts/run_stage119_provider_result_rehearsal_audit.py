from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage119_provider_result_rehearsal_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE114_SCHEMA,
    DEFAULT_STAGE118_RESULTS,
    print_stage119_summary,
    run_stage119_audit,
    write_stage119_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Rehearse Stage 114 provider result records from Stage 118 dry-run payloads.")
    parser.add_argument("--stage118-results", type=Path, default=DEFAULT_STAGE118_RESULTS)
    parser.add_argument("--stage114-schema", type=Path, default=DEFAULT_STAGE114_SCHEMA)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage119_audit(
        stage118_results_path=args.stage118_results,
        stage114_schema_path=args.stage114_schema,
        output_dir=args.output_dir,
    )
    paths = write_stage119_outputs(result, args.output_dir)
    print_stage119_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
