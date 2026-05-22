from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage143_first_provider_handoff_safety_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE142_RESULTS,
    print_stage143_summary,
    run_stage143_audit,
    write_stage143_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit the first-provider unlock handoff for secret/live-submit safety.")
    parser.add_argument("--stage142-results", type=Path, default=DEFAULT_STAGE142_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage143_audit(stage142_results_path=args.stage142_results)
    paths = write_stage143_outputs(result, args.output_dir)
    print_stage143_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
