from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage100_matched_cx_encoding_packet_freezer import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SOURCE_PACKET_DIR,
    DEFAULT_SOURCE_PACKET_FILES,
    print_stage100_summary,
    run_stage100_freezer,
    write_stage100_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Freeze Stage 100 matched CX encoding packets.")
    parser.add_argument("--source-packet-dir", type=Path, default=DEFAULT_SOURCE_PACKET_DIR)
    parser.add_argument("--source-packet-file", action="append", dest="source_packet_files")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    source_packet_files = tuple(args.source_packet_files) if args.source_packet_files else DEFAULT_SOURCE_PACKET_FILES
    result = run_stage100_freezer(source_packet_dir=args.source_packet_dir, source_packet_files=source_packet_files)
    paths = write_stage100_outputs(result, args.output_dir)
    print_stage100_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    print(f"wrote packets under {paths['packet_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
