from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
README = REPO_ROOT / "README.md"
VERIFIER = REPO_ROOT / "scripts" / "verify_stage4_hardware_packet.py"


def _extract_expected_summary(text: str) -> dict[str, Any]:
    match = re.search(r"Expected verifier summary:\s*```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if not match:
        raise RuntimeError("README.md does not contain an Expected verifier summary JSON block")
    return json.loads(match.group(1))


def _normalize(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload)
    if "job_ids" in normalized:
        normalized["job_ids"] = list(normalized["job_ids"])
    return normalized


def main() -> int:
    expected = _extract_expected_summary(README.read_text(encoding="utf-8"))
    completed = subprocess.run(
        [sys.executable, str(VERIFIER)],
        cwd=REPO_ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if completed.returncode != 0:
        sys.stderr.write(completed.stderr)
        sys.stderr.write(completed.stdout)
        return completed.returncode
    actual = json.loads(completed.stdout)
    if _normalize(actual) != _normalize(expected):
        print(
            json.dumps(
                {
                    "pass": False,
                    "reason": "README expected verifier summary does not match verifier output",
                    "expected": expected,
                    "actual": actual,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1
    print(json.dumps({"pass": True, "checked": "README expected verifier summary"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
