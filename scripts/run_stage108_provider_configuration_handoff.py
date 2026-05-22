from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage108_provider_configuration_handoff import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE106_RESULTS,
    DEFAULT_STAGE107_MANIFEST,
    print_stage108_summary,
    run_stage108_handoff,
    write_stage108_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare Stage 108 provider configuration handoff templates.")
    parser.add_argument("--stage106-results", type=Path, default=DEFAULT_STAGE106_RESULTS)
    parser.add_argument("--stage107-manifest", type=Path, default=DEFAULT_STAGE107_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage108_handoff(stage106_results_path=args.stage106_results, stage107_manifest_path=args.stage107_manifest)
    paths = write_stage108_outputs(result, args.output_dir)
    print_stage108_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    print(f"wrote templates under {paths['template_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
