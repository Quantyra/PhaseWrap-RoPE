from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage165_simulated_noise_margin_stability_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE153_RESULTS,
    DEFAULT_STAGE154_RESULTS,
    print_stage165_summary,
    run_stage165_margin_stability_audit,
    write_stage165_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit simulated-noise hardware targets against shot-resolution margins.")
    parser.add_argument("--stage153-results", type=Path, default=DEFAULT_STAGE153_RESULTS)
    parser.add_argument("--stage154-results", type=Path, default=DEFAULT_STAGE154_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage165_margin_stability_audit(
        stage153_results_path=args.stage153_results,
        stage154_results_path=args.stage154_results,
    )
    paths = write_stage165_outputs(result, args.output_dir)
    print_stage165_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
