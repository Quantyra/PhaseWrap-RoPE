from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage95_headline_interval_audit import (  # noqa: E402
    DEFAULT_ARTIFACT_ROOT,
    DEFAULT_OUTPUT_DIR,
    print_stage95_summary,
    run_stage95_audit,
    write_stage95_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Stage 95 headline interval audit.")
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage95_audit(artifact_root=args.artifact_root)
    paths = write_stage95_outputs(result, args.output_dir)
    print_stage95_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
