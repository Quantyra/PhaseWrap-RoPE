from __future__ import annotations

import csv
import importlib.util
import json
import shutil
from pathlib import Path
from typing import Any


STAGE10_SCHEMA_VERSION = "qrope_stage10_small_decoder_transformer_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage10_small_decoder_transformer"
METHOD_NAMES = ("no_position", "sinusoidal", "alibi", "rope", "phasewrap_bias", "phasewrap_adapter")
DEFAULT_SEEDS = (307, 311, 313, 317, 331)
MIN_TRANSFORMER_INSTALL_FREE_BYTES = 2_000_000_000


def torch_available() -> bool:
    return importlib.util.find_spec("torch") is not None


def _disk_free_bytes(path: Path = Path.cwd()) -> int:
    return int(shutil.disk_usage(path).free)


def build_blocked_result(
    *,
    reason: str = "missing_optional_torch_dependency",
    disk_free_bytes: int | None = None,
) -> dict[str, Any]:
    free_bytes = _disk_free_bytes() if disk_free_bytes is None else int(disk_free_bytes)
    return {
        "schema_version": STAGE10_SCHEMA_VERSION,
        "stage": "stage10_small_decoder_transformer",
        "status": "blocked",
        "blocked_reason": reason,
        "disk_free_bytes": free_bytes,
        "minimum_recommended_free_bytes_for_transformer_install": MIN_TRANSFORMER_INSTALL_FREE_BYTES,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "optional_dependency_group": "transformer",
        "install_command": "python -m pip install -e \".[transformer]\"",
        "method_names": list(METHOD_NAMES),
        "seeds": list(DEFAULT_SEEDS),
        "planned_task_lanes": [
            "phase_cued_retrieval",
            "exact_offset_passkey",
            "non_synthetic_text_retrieval_or_qa",
        ],
        "claim_boundary": {
            "supported": [
                "A machine-readable preflight record for the full small decoder-only transformer milestone.",
                "A clear dependency gate showing that no full transformer run was executed in this environment.",
            ],
            "excluded": [
                "production transformer superiority",
                "full language-model validation",
                "proof that PhaseWrap-RoPE replaces RoPE",
                "broad quantum advantage",
                "general cross-backend robustness",
            ],
        },
        "artifact_policy": {
            "required_for_completed_run": [
                "manifest with model variants, seeds, tasks, and training settings",
                "per-run metrics for all seeds and variants",
                "failed-run records",
                "aggregate summary with confidence intervals",
                "non-synthetic retrieval or QA task result",
            ],
            "current_record": "blocked preflight only; no model training metrics are reported",
        },
    }


def run_stage10_preflight() -> dict[str, Any]:
    if not torch_available():
        free_bytes = _disk_free_bytes()
        if free_bytes < MIN_TRANSFORMER_INSTALL_FREE_BYTES:
            return build_blocked_result(
                reason="insufficient_disk_for_transformer_dependency_install",
                disk_free_bytes=free_bytes,
            )
        return build_blocked_result(disk_free_bytes=free_bytes)
    return {
        "schema_version": STAGE10_SCHEMA_VERSION,
        "stage": "stage10_small_decoder_transformer",
        "status": "ready",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "disk_free_bytes": _disk_free_bytes(),
        "minimum_recommended_free_bytes_for_transformer_install": MIN_TRANSFORMER_INSTALL_FREE_BYTES,
        "optional_dependency_group": "transformer",
        "method_names": list(METHOD_NAMES),
        "seeds": list(DEFAULT_SEEDS),
        "note": "Torch is available. The full training implementation can be executed from this dependency-gated path.",
    }


def write_stage10_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "optional_dependency_group": result["optional_dependency_group"],
        "method_names": result["method_names"],
        "result_path": str((output_dir / "preflight.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "claim_boundary": result.get("claim_boundary", {}),
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "preflight": str(output_dir / "preflight.json"),
        "summary_csv": str(output_dir / "summary.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "preflight.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("stage", "status", "blocked_reason", "install_command"))
        writer.writeheader()
        writer.writerow(
            {
                "stage": result["stage"],
                "status": result["status"],
                "blocked_reason": result.get("blocked_reason", ""),
                "install_command": result.get("install_command", ""),
            }
        )
    return paths


def print_stage10_summary(result: dict[str, Any]) -> None:
    print("stage | status | blocked_reason | install_command")
    print("--- | --- | --- | ---")
    print(
        " | ".join(
            (
                result["stage"],
                result["status"],
                result.get("blocked_reason", ""),
                result.get("install_command", ""),
            )
        )
    )
