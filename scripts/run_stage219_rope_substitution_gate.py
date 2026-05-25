from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage219_rope_substitution_gate import (  # noqa: E402
    print_stage219_summary,
    run_stage219_rope_substitution_gate,
    write_stage219_outputs,
)


def main() -> None:
    result = run_stage219_rope_substitution_gate()
    write_stage219_outputs(result)
    print_stage219_summary(result)


if __name__ == "__main__":
    main()
