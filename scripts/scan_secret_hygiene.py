from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MAX_TEXT_BYTES = 2_000_000
SECRET_PATTERNS = {
    "private_key_block": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    "aws_secret_assignment": re.compile(
        r"(?i)\b(?:AWS_SECRET_ACCESS_KEY|aws_secret_access_key)\b[^\S\r\n]*[:=][^\S\r\n]*[\"']?[A-Za-z0-9/+=]{20,}"
    ),
    "provider_token_assignment": re.compile(
        r"(?i)\b(?:IBM_QUANTUM_TOKEN|QISKIT_IBM_TOKEN|QUANDELA_CLOUD_TOKEN|SCALEWAY_SECRET_KEY)\b[^\S\r\n]*[:=][^\S\r\n]*[\"']?[A-Za-z0-9._/-]{12,}"
    ),
}


def _tracked_files() -> list[Path]:
    output = subprocess.check_output(["git", "ls-files"], cwd=REPO_ROOT, text=True)
    return [REPO_ROOT / line.strip() for line in output.splitlines() if line.strip()]


def _read_text(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if len(data) > MAX_TEXT_BYTES:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def main() -> int:
    findings: list[str] = []
    for path in _tracked_files():
        text = _read_text(path)
        if text is None:
            continue
        rel_path = path.relative_to(REPO_ROOT).as_posix()
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{rel_path}: matched {label}")
    if findings:
        print("Secret hygiene scan failed:")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("Secret hygiene scan passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
