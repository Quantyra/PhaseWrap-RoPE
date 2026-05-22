from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.env_utils import load_local_dotenv  # noqa: E402
from qrope.stage177_ibm_backend_informed_noise_probe import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE100_MANIFEST,
    DEFAULT_STAGE159_RESULTS,
    DEFAULT_STAGE169_RESULTS,
    DEFAULT_STAGE99_MANIFEST,
    print_stage177_summary,
    run_stage177_ibm_backend_informed_noise_probe,
    write_stage177_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the read-only IBM backend-property-informed simulated noise probe.")
    parser.add_argument("--stage159-results", type=Path, default=DEFAULT_STAGE159_RESULTS)
    parser.add_argument("--stage169-results", type=Path, default=DEFAULT_STAGE169_RESULTS)
    parser.add_argument("--stage99-manifest", type=Path, default=DEFAULT_STAGE99_MANIFEST)
    parser.add_argument("--stage100-manifest", type=Path, default=DEFAULT_STAGE100_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--load-dotenv", action="store_true")
    parser.add_argument(
        "--allow-backend-properties-lookup",
        action="store_true",
        help="Perform read-only IBM backend properties lookup. This does not submit hardware jobs.",
    )
    args = parser.parse_args(argv)

    if args.load_dotenv:
        load_local_dotenv(REPO_ROOT / ".env")
    result = run_stage177_ibm_backend_informed_noise_probe(
        stage159_results_path=args.stage159_results,
        stage169_results_path=args.stage169_results,
        stage99_manifest_path=args.stage99_manifest,
        stage100_manifest_path=args.stage100_manifest,
        allow_backend_properties_lookup=args.allow_backend_properties_lookup,
    )
    paths = write_stage177_outputs(result, args.output_dir)
    print_stage177_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
