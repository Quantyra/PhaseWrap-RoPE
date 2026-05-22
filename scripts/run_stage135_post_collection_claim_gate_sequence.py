from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage135_post_collection_claim_gate_sequence import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE101_RESULTS,
    DEFAULT_STAGE103_RESULTS,
    DEFAULT_STAGE109_RESULTS,
    DEFAULT_STAGE110_RESULTS,
    DEFAULT_STAGE113_RESULTS,
    DEFAULT_STAGE115_RESULTS,
    DEFAULT_STAGE134_RESULTS,
    DEFAULT_STAGE136_RESULTS,
    DEFAULT_STAGE137_RESULTS,
    DEFAULT_STAGE148_RESULTS,
    DEFAULT_STAGE138_RESULTS,
    print_stage135_summary,
    run_stage135_sequence_audit,
    write_stage135_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit the post-collection gate sequence before any noisy-hardware claim.")
    parser.add_argument("--stage115-results", type=Path, default=DEFAULT_STAGE115_RESULTS)
    parser.add_argument("--stage134-results", type=Path, default=DEFAULT_STAGE134_RESULTS)
    parser.add_argument("--stage113-results", type=Path, default=DEFAULT_STAGE113_RESULTS)
    parser.add_argument("--stage101-results", type=Path, default=DEFAULT_STAGE101_RESULTS)
    parser.add_argument("--stage103-results", type=Path, default=DEFAULT_STAGE103_RESULTS)
    parser.add_argument("--stage109-results", type=Path, default=DEFAULT_STAGE109_RESULTS)
    parser.add_argument("--stage110-results", type=Path, default=DEFAULT_STAGE110_RESULTS)
    parser.add_argument("--stage136-results", type=Path, default=DEFAULT_STAGE136_RESULTS)
    parser.add_argument("--stage137-results", type=Path, default=DEFAULT_STAGE137_RESULTS)
    parser.add_argument("--stage148-results", type=Path, default=DEFAULT_STAGE148_RESULTS)
    parser.add_argument("--stage138-results", type=Path, default=DEFAULT_STAGE138_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage135_sequence_audit(
        stage115_results_path=args.stage115_results,
        stage134_results_path=args.stage134_results,
        stage113_results_path=args.stage113_results,
        stage101_results_path=args.stage101_results,
        stage103_results_path=args.stage103_results,
        stage109_results_path=args.stage109_results,
        stage110_results_path=args.stage110_results,
        stage136_results_path=args.stage136_results,
        stage137_results_path=args.stage137_results,
        stage148_results_path=args.stage148_results,
        stage138_results_path=args.stage138_results,
    )
    paths = write_stage135_outputs(result, args.output_dir)
    print_stage135_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
