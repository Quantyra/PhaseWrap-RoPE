from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
AUTOMATED_STAGE_LOG_ROOT = REPO_ROOT / "logs" / "automated_stage_gates"


def stage_log_path(*parts: str) -> Path:
    """Return a path under the repository's automated-stage log root."""
    return AUTOMATED_STAGE_LOG_ROOT.joinpath(*parts)


def repo_relative_posix(path: Path) -> str:
    """Return a stable repo-relative POSIX path when possible."""
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()
