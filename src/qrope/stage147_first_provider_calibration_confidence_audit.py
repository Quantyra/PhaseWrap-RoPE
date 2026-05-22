from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any


STAGE147_SCHEMA_VERSION = "qrope_stage147_first_provider_calibration_confidence_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE102_TEMPLATE_DIR = DEFAULT_ARTIFACT_ROOT / "stage102_calibration_execution_package" / "execution_templates"
DEFAULT_STAGE145_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage145_first_provider_evidence_path_audit" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage147_first_provider_calibration_confidence_audit"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
MIN_DOMINANT_FRACTION = 0.80
Z_95 = 1.96


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _wilson_lower_bound(successes: int, total: int, z: float = Z_95) -> float:
    if total <= 0:
        return 0.0
    phat = float(successes) / float(total)
    z2 = z * z
    denominator = 1.0 + z2 / total
    center = phat + z2 / (2.0 * total)
    spread = z * math.sqrt((phat * (1.0 - phat) / total) + (z2 / (4.0 * total * total)))
    return (center - spread) / denominator


def _required_successes(total: int, threshold: float = MIN_DOMINANT_FRACTION) -> int | None:
    if total <= 0:
        return None
    for successes in range(total + 1):
        if _wilson_lower_bound(successes, total) >= threshold:
            return successes
    return None


def _template_path(provider: str, template_dir: Path) -> Path:
    return template_dir / f"{provider}_known_state_execution.json"


def _state_records(template: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(template, dict):
        return []
    shots = int(template.get("shots_per_state") or 0)
    required = _required_successes(shots)
    records = []
    for row in template.get("raw_counts_by_state", []):
        state = str(row.get("state"))
        records.append(
            {
                "state": state,
                "expected_dominant_key": row.get("expected_dominant_key"),
                "shots_per_state": shots,
                "minimum_stage101_dominant_count": math.ceil(MIN_DOMINANT_FRACTION * shots) if shots > 0 else None,
                "minimum_wilson95_dominant_count": required,
                "minimum_wilson95_dominant_fraction": round(float(required) / float(shots), 12)
                if required is not None and shots > 0
                else None,
                "wilson95_lower_bound_at_required_count": round(_wilson_lower_bound(required, shots), 12)
                if required is not None and shots > 0
                else None,
                "ready": shots > 0 and required is not None,
            }
        )
    return records


def run_stage147_audit(
    *,
    stage102_template_dir: Path = DEFAULT_STAGE102_TEMPLATE_DIR,
    stage145_results_path: Path = DEFAULT_STAGE145_RESULTS,
    provider: str | None = None,
) -> dict[str, Any]:
    stage145 = _load_json(stage145_results_path)
    provider_scope = provider or (str(stage145.get("first_unlock_provider", "")) if isinstance(stage145, dict) else "")
    template_path = _template_path(provider_scope, stage102_template_dir) if provider_scope else stage102_template_dir / "_missing_provider.json"
    template = _load_json(template_path)
    missing_sources = []
    if stage145 is None:
        missing_sources.append(str(stage145_results_path.as_posix()))
    if template is None:
        missing_sources.append(str(template_path.as_posix()))
    state_records = _state_records(template)
    ready = bool(provider_scope) and bool(state_records) and all(record["ready"] for record in state_records) and not missing_sources
    return {
        "schema_version": STAGE147_SCHEMA_VERSION,
        "stage": "stage147_first_provider_calibration_confidence_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "FIRST_PROVIDER_CALIBRATION_CONFIDENCE_CONTRACT_READY_COUNTS_REQUIRED"
            if ready
            else "FIRST_PROVIDER_CALIBRATION_CONFIDENCE_CONTRACT_INCOMPLETE"
        ),
        "source_artifacts": [str(stage145_results_path.as_posix()), str(template_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "provider_scope": provider_scope,
        "expected_bitstring_order": template.get("expected_bitstring_order") if isinstance(template, dict) else None,
        "state_count": len(state_records),
        "ready_state_count": sum(1 for record in state_records if record["ready"]),
        "state_records": state_records,
        "confidence_contract": {
            "stage101_min_dominant_fraction": MIN_DOMINANT_FRACTION,
            "confidence_interval": "Wilson score lower bound",
            "confidence_level": "95%",
            "calibration_interpretation": (
                "Stage 101 remains necessary. Stage 147 adds a confidence guard: each known-state dominant bitstring "
                "count should meet the Wilson 95% minimum before treating the bitstring-order calibration as confidence-supported."
            ),
        },
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "first-provider known-state calibration confidence thresholds before matched packet interpretation",
                "state-level Wilson 95% dominant-count requirements for the Stage 101 bitstring-order check",
                "a non-submitting calibration-confidence guardrail for later noisy-hardware evidence",
            ],
            "excluded": [
                "provider credential values",
                "hardware job submission",
                "real provider calibration counts",
                "readout mitigation or correction",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "After IBM Runtime known-state counts are collected, require Stage 101 to pass and compare each dominant "
            "known-state count against these Wilson 95% thresholds before interpreting matched packet counts."
        ),
    }


def write_stage147_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "provider_scope": result["provider_scope"],
        "expected_bitstring_order": result["expected_bitstring_order"],
        "state_count": result["state_count"],
        "ready_state_count": result["ready_state_count"],
        "confidence_contract": result["confidence_contract"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "secret_values_recorded": result["secret_values_recorded"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "claim_boundary": result["claim_boundary"],
        "next_gate": result["next_gate"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "state",
                "expected_dominant_key",
                "shots_per_state",
                "minimum_stage101_dominant_count",
                "minimum_wilson95_dominant_count",
                "minimum_wilson95_dominant_fraction",
                "wilson95_lower_bound_at_required_count",
                "ready",
            ),
        )
        writer.writeheader()
        for record in result["state_records"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage147_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"provider_scope: {result['provider_scope']}")
    print(f"expected_bitstring_order: {result['expected_bitstring_order']}")
    print(f"ready_state_count: {result['ready_state_count']}/{result['state_count']}")
    print(f"next_gate: {result['next_gate']}")
