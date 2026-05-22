from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage93_toy_decoder_lane_boundary_audit import (  # noqa: E402
    DEFAULT_ARTIFACT_ROOT,
    DEFAULT_OUTPUT_DIR,
    print_stage93_summary,
    run_stage93_audit,
    write_stage93_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Stage 93 toy decoder lane boundary audit.")
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage93_audit(artifact_root=args.artifact_root)
    paths = write_stage93_outputs(result, args.output_dir)
    print_stage93_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
