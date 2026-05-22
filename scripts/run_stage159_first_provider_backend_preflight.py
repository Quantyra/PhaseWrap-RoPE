from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.env_utils import load_local_dotenv  # noqa: E402
from qrope.stage159_first_provider_backend_preflight import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE158_RESULTS,
    print_stage159_summary,
    run_stage159_backend_preflight,
    write_stage159_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only first-provider backend preflight after Stage 158.")
    parser.add_argument("--stage158-results", type=Path, default=DEFAULT_STAGE158_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--load-dotenv", action="store_true")
    parser.add_argument("--allow-backend-lookup", action="store_true")
    args = parser.parse_args(argv)

    if args.load_dotenv:
        load_local_dotenv(REPO_ROOT / ".env")
    result = run_stage159_backend_preflight(
        stage158_results_path=args.stage158_results,
        allow_backend_lookup=args.allow_backend_lookup,
    )
    paths = write_stage159_outputs(result, args.output_dir)
    print_stage159_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
