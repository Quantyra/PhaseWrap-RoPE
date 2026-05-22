from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.env_utils import load_local_dotenv  # noqa: E402
from qrope.stage140_local_provider_configuration_readiness import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE139_RESULTS,
    print_stage140_summary,
    run_stage140_readiness,
    write_stage140_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check local provider env/SDK readiness without recording secrets.")
    parser.add_argument("--stage139-results", type=Path, default=DEFAULT_STAGE139_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--load-dotenv", action="store_true")
    args = parser.parse_args(argv)

    if args.load_dotenv:
        load_local_dotenv(REPO_ROOT / ".env")
    result = run_stage140_readiness(stage139_results_path=args.stage139_results)
    paths = write_stage140_outputs(result, args.output_dir)
    print_stage140_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
