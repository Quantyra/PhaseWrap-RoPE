from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage115_provider_result_collector import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE113_PROVIDER_RESULTS,
    DEFAULT_STAGE114_MANIFEST,
    DEFAULT_STAGE114_OUTPUT_DIR,
    print_stage115_summary,
    run_stage115_collector,
    write_stage115_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Stage 114 provider result shards and collect Stage 113 input.")
    parser.add_argument("--stage114-manifest", type=Path, default=DEFAULT_STAGE114_MANIFEST)
    parser.add_argument("--stage114-output-dir", type=Path, default=DEFAULT_STAGE114_OUTPUT_DIR)
    parser.add_argument("--stage113-provider-results", type=Path, default=DEFAULT_STAGE113_PROVIDER_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--write-stage113-input", action="store_true")
    parser.add_argument("--provider", default=None)
    args = parser.parse_args(argv)

    result = run_stage115_collector(
        stage114_manifest_path=args.stage114_manifest,
        stage114_output_dir=args.stage114_output_dir,
        stage113_provider_results_path=args.stage113_provider_results,
        write_stage113_input=args.write_stage113_input,
        provider=args.provider,
    )
    paths = write_stage115_outputs(result, args.output_dir)
    print_stage115_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
