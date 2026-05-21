from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage51_decoder_path_plateau_audit import (  # noqa: E402
    DEFAULT_INPUT_ROOT,
    DEFAULT_OUTPUT_DIR,
    print_stage51_table,
    run_stage51_audit,
    write_stage51_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Stage 51 decoder-path plateau audit.")
    parser.add_argument("--input-root", type=Path, default=DEFAULT_INPUT_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage51_audit(input_root=args.input_root)
    paths = write_stage51_outputs(result, args.output_dir)
    print_stage51_table(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['results']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
