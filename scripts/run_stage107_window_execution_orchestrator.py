from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage107_window_execution_orchestrator import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE102_MANIFEST,
    DEFAULT_STAGE105_WINDOWS,
    DEFAULT_STAGE106_MANIFEST,
    print_stage107_summary,
    run_stage107_orchestrator,
    write_stage107_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare Stage 107 independent-window execution orchestration plan.")
    parser.add_argument("--stage102-manifest", type=Path, default=DEFAULT_STAGE102_MANIFEST)
    parser.add_argument("--stage105-windows", type=Path, default=DEFAULT_STAGE105_WINDOWS)
    parser.add_argument("--stage106-manifest", type=Path, default=DEFAULT_STAGE106_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage107_orchestrator(
        stage102_manifest_path=args.stage102_manifest,
        stage105_windows_path=args.stage105_windows,
        stage106_manifest_path=args.stage106_manifest,
    )
    paths = write_stage107_outputs(result, args.output_dir)
    print_stage107_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    print(f"wrote {paths['window_plans']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
