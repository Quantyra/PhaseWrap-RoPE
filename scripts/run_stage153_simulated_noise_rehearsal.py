from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage153_simulated_noise_rehearsal import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE100_MANIFEST,
    DEFAULT_STAGE99_MANIFEST,
    print_stage153_summary,
    run_stage153_simulated_noise_rehearsal,
    write_stage153_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a simulated-only noisy matched-packet rehearsal.")
    parser.add_argument("--stage99-manifest", type=Path, default=DEFAULT_STAGE99_MANIFEST)
    parser.add_argument("--stage100-manifest", type=Path, default=DEFAULT_STAGE100_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage153_simulated_noise_rehearsal(
        stage99_manifest_path=args.stage99_manifest,
        stage100_manifest_path=args.stage100_manifest,
    )
    paths = write_stage153_outputs(result, args.output_dir)
    print_stage153_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
