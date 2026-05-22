from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage124_adapter_readiness_alignment_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE106_RESULTS,
    DEFAULT_STAGE111_RESULTS,
    DEFAULT_STAGE123_RESULTS,
    print_stage124_summary,
    run_stage124_audit,
    write_stage124_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit provider adapter readiness alignment with Stage 106/111 blockers and Stage 123 plans.")
    parser.add_argument("--stage106-results", type=Path, default=DEFAULT_STAGE106_RESULTS)
    parser.add_argument("--stage111-results", type=Path, default=DEFAULT_STAGE111_RESULTS)
    parser.add_argument("--stage123-results", type=Path, default=DEFAULT_STAGE123_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage124_audit(
        stage106_results_path=args.stage106_results,
        stage111_results_path=args.stage111_results,
        stage123_results_path=args.stage123_results,
    )
    paths = write_stage124_outputs(result, args.output_dir)
    print_stage124_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
