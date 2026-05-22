from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage199_reduced_scope_attestation_packet import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE198_RESULTS,
    print_stage199_summary,
    run_stage199_reduced_scope_attestation_packet,
    write_stage199_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build reduced-scope credit attestation packet without submitting hardware.")
    parser.add_argument("--stage198-results", type=Path, default=DEFAULT_STAGE198_RESULTS)
    parser.add_argument("--budget-cap-usd", type=float, default=25.0)
    parser.add_argument("--human-credit-allowance-verified", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage199_reduced_scope_attestation_packet(
        stage198_results_path=args.stage198_results,
        budget_cap_usd=args.budget_cap_usd,
        human_credit_allowance_verified=args.human_credit_allowance_verified,
    )
    paths = write_stage199_outputs(result, args.output_dir)
    print_stage199_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    print(f"wrote {paths['scenarios_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
