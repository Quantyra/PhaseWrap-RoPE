from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE98_SCHEMA_VERSION = "qrope_stage98_noisy_hardware_robustness_goal_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage98_noisy_hardware_robustness_goal_audit"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
SOURCE_FILES: tuple[tuple[str, str], ...] = (
    ("stage4_hardware_sweep", "manifest.json"),
    ("stage4_hardware_sweep", "offline_verification.json"),
    ("stage4_bitstring_calibration", "manifest.json"),
    ("stage4_bitstring_calibration", "offline_verification.json"),
)


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential goal-framing audit for a noisy-hardware readout-robustness track.",
            "A distinction between existing bounded Stage 4 hardware-positive artifacts and the stronger matched-encoding robustness claim.",
            "A fixed-width protocol gate for comparing PhaseWrap score readout with matched positional-score encodings.",
        ],
        "excluded": [
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that noisy quantum hardware improves language models",
            "a claim that Stage 4 already proves general noisy-hardware robustness",
            "provider-wide bitstring-order validation without known-state calibration counts",
            "production transformer superiority",
            "broad quantum advantage",
        ],
    }


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _source_payloads(artifact_root: Path) -> tuple[dict[str, dict[str, Any]], list[str], list[str]]:
    payloads: dict[str, dict[str, Any]] = {}
    source_artifacts: list[str] = []
    missing_source_artifacts: list[str] = []
    for stage_dir, file_name in SOURCE_FILES:
        path = artifact_root / stage_dir / file_name
        key = f"{stage_dir}/{file_name}"
        source_artifacts.append(str(path.as_posix()))
        payload = _load_json(path)
        if payload is None:
            missing_source_artifacts.append(str(path.as_posix()))
            continue
        payloads[key] = payload
    return payloads, source_artifacts, missing_source_artifacts


def _stage4_summary(sweep_manifest: dict[str, Any] | None, sweep_verification: dict[str, Any] | None) -> dict[str, Any]:
    if not sweep_manifest or not sweep_verification:
        return {
            "active_record_count": 0,
            "active_hardware_positive_count": 0,
            "providers": [],
            "families": [],
            "fixed_width_current_records": False,
            "verifier_pass": False,
        }
    records = sweep_manifest.get("records", [])
    table = sweep_verification.get("table", [])
    providers = sorted({str(record.get("provider")) for record in records})
    families = sorted({str(record.get("family")) for record in records})
    row_counts = sorted({int(record.get("row_count", 0)) for record in records})
    shot_counts = sorted({int(record.get("shots", 0)) for record in records})
    return {
        "active_record_count": len(records),
        "active_hardware_positive_count": sum(1 for row in table if row.get("outcome") == "hardware-positive"),
        "providers": providers,
        "families": families,
        "row_counts": row_counts,
        "shot_counts": shot_counts,
        "fixed_width_current_records": bool(records) and all(str(record.get("family", "")).startswith("two_qubit") for record in records),
        "verifier_pass": sweep_verification.get("pass") is True,
        "bounded_claim_statement": sweep_manifest.get("bounded_claim_statement"),
    }


def _calibration_status(calibration_manifest: dict[str, Any] | None, calibration_verification: dict[str, Any] | None) -> dict[str, Any]:
    if not calibration_manifest or not calibration_verification:
        return {
            "packet_specs_present": calibration_manifest is not None,
            "known_state_counts_present": False,
            "verifier_status": "missing",
        }
    return {
        "packet_specs_present": True,
        "known_state_counts_present": calibration_verification.get("status") == "pass" or calibration_verification.get("pass") is True,
        "verifier_status": calibration_verification.get("status", "unknown"),
        "verifier_pass": calibration_verification.get("pass") is True,
    }


def _protocol_requirements(stage4: dict[str, Any], calibration: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "requirement": "fixed_circuit_width",
            "status": "passed" if stage4["fixed_width_current_records"] else "failed",
            "evidence": "Current Stage 4 active records are two-qubit witness families.",
            "required_for_claim": "Future matched encodings must use the same qubit count and comparable measurement observables.",
        },
        {
            "requirement": "recorded_noisy_hardware_artifacts",
            "status": "passed" if stage4["verifier_pass"] and stage4["active_hardware_positive_count"] > 0 else "failed",
            "evidence": f"{stage4['active_hardware_positive_count']} active Stage 4 records verify as hardware-positive.",
            "required_for_claim": "Use recorded raw counts, job/task IDs, backend metadata, and offline verifier recomputation.",
        },
        {
            "requirement": "matched_positional_score_encodings",
            "status": "missing",
            "evidence": "Stage 4 compares PhaseWrap witness/control records, but not matched RoPE/sinusoidal/ALiBI score encodings under equal circuit width.",
            "required_for_claim": "Add frozen fixed-width encodings for PhaseWrap, RoPE-like, sinusoidal-like, ALIBI-like, and a no-position/control family.",
        },
        {
            "requirement": "known_state_bitstring_calibration",
            "status": "passed" if calibration["known_state_counts_present"] else "missing",
            "evidence": (
                "Known-state calibration counts are present."
                if calibration["known_state_counts_present"]
                else "Calibration packet specs exist, but real known-state counts are not yet supplied."
            ),
            "required_for_claim": "Run |00>, |01>, |10>, and |11> known-state packets per provider/backend/date before provider-level decoding claims.",
        },
        {
            "requirement": "fixed_shot_budget_and_rows",
            "status": "partial",
            "evidence": f"Current records have shot counts {stage4.get('shot_counts', [])} and row counts {stage4.get('row_counts', [])}.",
            "required_for_claim": "Predeclare one fixed shot budget and row set per comparison family, or analyze shot budget as a declared factor.",
        },
        {
            "requirement": "independent_date_calibration_reruns",
            "status": "missing",
            "evidence": "Current intervals are row-bootstrap and shot-resampling diagnostics over recorded artifacts, not independent date/calibration reruns.",
            "required_for_claim": "Repeat selected packets across backend dates/calibration windows before claiming robustness beyond recorded contexts.",
        },
    ]


def _decision(requirements: list[dict[str, Any]]) -> dict[str, Any]:
    missing = [row["requirement"] for row in requirements if row["status"] in {"missing", "failed"}]
    partial = [row["requirement"] for row in requirements if row["status"] == "partial"]
    if "matched_positional_score_encodings" in missing:
        decision = "NOISY_HARDWARE_GOAL_FRAMED_MATCHED_ENCODINGS_REQUIRED"
        boundary = "Existing Stage 4 hardware positives justify the track, but matched fixed-width positional encodings are required before testing comparative robustness."
    elif missing or partial:
        decision = "NOISY_HARDWARE_GOAL_FRAMED_PROTOCOL_INCOMPLETE"
        boundary = "The noisy-hardware robustness goal is framed, but one or more required controls are incomplete."
    else:
        decision = "NOISY_HARDWARE_ROBUSTNESS_PROTOCOL_READY"
        boundary = "All protocol prerequisites are present for a fixed-width noisy-hardware robustness comparison."
    return {
        "decision": decision,
        "claim_boundary": boundary,
        "track_ready_for_real_hardware_claim": False,
        "missing_requirements": missing,
        "partial_requirements": partial,
    }


def run_stage98_audit(*, artifact_root: Path = DEFAULT_ARTIFACT_ROOT) -> dict[str, Any]:
    payloads, source_artifacts, missing_source_artifacts = _source_payloads(artifact_root)
    stage4 = _stage4_summary(
        payloads.get("stage4_hardware_sweep/manifest.json"),
        payloads.get("stage4_hardware_sweep/offline_verification.json"),
    )
    calibration = _calibration_status(
        payloads.get("stage4_bitstring_calibration/manifest.json"),
        payloads.get("stage4_bitstring_calibration/offline_verification.json"),
    )
    requirements = _protocol_requirements(stage4, calibration)
    result = {
        "schema_version": STAGE98_SCHEMA_VERSION,
        "stage": "stage98_noisy_hardware_robustness_goal_audit",
        "status": "completed",
        "objective": OBJECTIVE,
        "source_stage": "stage4_hardware_sweep",
        "source_artifacts": source_artifacts,
        "missing_source_artifacts": missing_source_artifacts,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "claim_boundary": _claim_boundary(),
        "stage4_summary": stage4,
        "bitstring_calibration_status": calibration,
        "protocol_requirements": requirements,
        "proposed_strongest_claim_if_successful": (
            "PhaseWrap-RoPE's compact positional score has bounded noisy-hardware readout robustness or auditability "
            "advantages over matched fixed-width positional-score encodings under specified backend, date, calibration, "
            "shot-budget, and bitstring-decoding conditions."
        ),
        "unsupported_claims": [
            "Noisy quantum hardware improves language-model performance.",
            "PhaseWrap-RoPE replaces RoPE.",
            "Stage 4 already proves general cross-backend robustness.",
            "Provider-wide bitstring conventions are validated without known-state calibration counts.",
        ],
        "next_gate": (
            "Freeze matched two-qubit positional-score encoding packets for PhaseWrap, RoPE-like, sinusoidal-like, "
            "ALIBI-like, and no-position/control families before any new hardware execution."
        ),
    }
    result["decision"] = _decision(requirements)
    return result


def write_stage98_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "source_stage": result["source_stage"],
        "source_artifacts": result["source_artifacts"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "decision": result["decision"],
        "claim_boundary": result["claim_boundary"],
        "missing_source_artifacts": result["missing_source_artifacts"],
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
        writer = csv.DictWriter(handle, fieldnames=("requirement", "status", "evidence", "required_for_claim"))
        writer.writeheader()
        writer.writerows(result["protocol_requirements"])
    return paths


def print_stage98_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']['decision']}")
    print(f"claim_boundary: {result['decision']['claim_boundary']}")
    print(f"next_gate: {result['next_gate']}")
