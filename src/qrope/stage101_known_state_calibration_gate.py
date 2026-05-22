from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE101_SCHEMA_VERSION = "qrope_stage101_known_state_calibration_gate_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE99_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage99_matched_fixed_width_encoding_packets" / "manifest.json"
DEFAULT_STAGE100_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage100_matched_cx_encoding_packets" / "manifest.json"
DEFAULT_STAGE4_CALIBRATION_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage4_bitstring_calibration" / "manifest.json"
DEFAULT_STAGE4_CALIBRATION_VERIFICATION = DEFAULT_ARTIFACT_ROOT / "stage4_bitstring_calibration" / "offline_verification.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage101_known_state_calibration_gate"
STATES: tuple[str, ...] = ("00", "01", "10", "11")
BITSTRING_ORDERS: tuple[str, ...] = ("q0q1", "q1q0")
MIN_DOMINANT_FRACTION = 0.80
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def expected_key_for_order(prepared_state: str, order: str) -> str:
    if order == "q0q1":
        return prepared_state
    if order == "q1q0":
        return prepared_state[::-1]
    raise ValueError(f"Unknown bitstring order: {order}")


def _counts_by_state(execution: dict[str, Any]) -> dict[str, dict[str, int]]:
    return {
        str(item.get("state")): {str(key): int(value) for key, value in item.get("counts", {}).items()}
        for item in execution.get("raw_counts_by_state", [])
    }


def _dominant(counts: dict[str, int]) -> tuple[str | None, int, int, float]:
    if not counts:
        return None, 0, 0, 0.0
    key, value = max(((str(key), int(value)) for key, value in counts.items()), key=lambda item: (item[1], item[0]))
    total = sum(int(value) for value in counts.values())
    fraction = float(value) / float(total) if total else 0.0
    return key, int(value), int(total), fraction


def infer_bitstring_order(execution: dict[str, Any], *, min_dominant_fraction: float = MIN_DOMINANT_FRACTION) -> dict[str, Any]:
    counts = _counts_by_state(execution)
    order_scores: list[dict[str, Any]] = []
    for order in BITSTRING_ORDERS:
        checks = []
        for state in STATES:
            dominant_key, dominant_count, total_count, dominant_fraction = _dominant(counts.get(state, {}))
            expected_key = expected_key_for_order(state, order)
            checks.append(
                {
                    "state": state,
                    "expected_key": expected_key,
                    "dominant_key": dominant_key,
                    "dominant_count": dominant_count,
                    "total_count": total_count,
                    "dominant_fraction": round(dominant_fraction, 12),
                    "pass": dominant_key == expected_key and dominant_fraction >= min_dominant_fraction,
                }
            )
        order_scores.append(
            {
                "order": order,
                "pass_count": sum(1 for check in checks if check["pass"]),
                "min_dominant_fraction": min((check["dominant_fraction"] for check in checks), default=0.0),
                "checks": checks,
                "pass": all(check["pass"] for check in checks),
            }
        )
    passing = [score for score in order_scores if score["pass"]]
    if len(passing) == 1:
        inferred_order = passing[0]["order"]
        outcome = "calibration_verified"
    elif len(passing) > 1:
        inferred_order = None
        outcome = "ambiguous_bitstring_order"
    else:
        inferred_order = None
        outcome = "calibration_failed"
    return {
        "outcome": outcome,
        "inferred_bitstring_order": inferred_order,
        "order_scores": order_scores,
        "min_required_dominant_fraction": min_dominant_fraction,
    }


def verify_provider_execution(
    provider: str,
    expected_order: str,
    execution: dict[str, Any] | None,
    *,
    min_dominant_fraction: float = MIN_DOMINANT_FRACTION,
) -> dict[str, Any]:
    required_fields = ["job_or_task_ids", "backend_metadata", "submitted_at_utc", "completed_at_utc", "raw_counts_by_state"]
    if execution is None:
        return {
            "provider": provider,
            "expected_bitstring_order": expected_order,
            "pass": False,
            "outcome": "missing_evidence",
            "missing_evidence": required_fields,
        }
    missing_fields = [field for field in required_fields if field not in execution or execution.get(field) in (None, "", [])]
    if missing_fields:
        return {
            "provider": provider,
            "expected_bitstring_order": expected_order,
            "pass": False,
            "outcome": "missing_required_fields",
            "missing_evidence": missing_fields,
        }
    inference = infer_bitstring_order(execution, min_dominant_fraction=min_dominant_fraction)
    return {
        "provider": provider,
        "expected_bitstring_order": expected_order,
        "pass": inference["outcome"] == "calibration_verified" and inference["inferred_bitstring_order"] == expected_order,
        "outcome": (
            "calibration_verified"
            if inference["outcome"] == "calibration_verified" and inference["inferred_bitstring_order"] == expected_order
            else "calibration_order_mismatch_or_failed"
        ),
        "job_or_task_ids": execution.get("job_or_task_ids"),
        "backend_metadata": execution.get("backend_metadata"),
        "submitted_at_utc": execution.get("submitted_at_utc"),
        "completed_at_utc": execution.get("completed_at_utc"),
        "inference": inference,
    }


def _execution_for_provider(execution_dir: Path | None, provider: str) -> dict[str, Any] | None:
    if execution_dir is None:
        return None
    path = execution_dir / f"{provider}_known_state_execution.json"
    return _load_json(path)


def _provider_records(calibration_manifest: dict[str, Any] | None) -> list[dict[str, str]]:
    if not calibration_manifest:
        return []
    records = []
    for record in calibration_manifest.get("records", []):
        records.append(
            {
                "provider": str(record.get("provider")),
                "expected_bitstring_order": str(record.get("expected_bitstring_order")),
                "packet_path": str(record.get("packet_path")),
            }
        )
    return records


def run_stage101_gate(
    *,
    stage99_manifest_path: Path = DEFAULT_STAGE99_MANIFEST,
    stage100_manifest_path: Path = DEFAULT_STAGE100_MANIFEST,
    calibration_manifest_path: Path = DEFAULT_STAGE4_CALIBRATION_MANIFEST,
    calibration_verification_path: Path = DEFAULT_STAGE4_CALIBRATION_VERIFICATION,
    execution_dir: Path | None = None,
    min_dominant_fraction: float = MIN_DOMINANT_FRACTION,
) -> dict[str, Any]:
    stage99 = _load_json(stage99_manifest_path)
    stage100 = _load_json(stage100_manifest_path)
    calibration_manifest = _load_json(calibration_manifest_path)
    calibration_verification = _load_json(calibration_verification_path)
    missing_sources = [
        str(path.as_posix())
        for path, payload in (
            (stage99_manifest_path, stage99),
            (stage100_manifest_path, stage100),
            (calibration_manifest_path, calibration_manifest),
            (calibration_verification_path, calibration_verification),
        )
        if payload is None
    ]
    provider_records = _provider_records(calibration_manifest)
    verification_records = [
        verify_provider_execution(
            record["provider"],
            record["expected_bitstring_order"],
            _execution_for_provider(execution_dir, record["provider"]),
            min_dominant_fraction=min_dominant_fraction,
        )
        for record in provider_records
    ]
    packet_freeze_ready = (
        stage99 is not None
        and stage99.get("decision") == "MATCHED_FIXED_WIDTH_ENCODING_PACKETS_FROZEN_NO_HARDWARE"
        and stage100 is not None
        and stage100.get("decision") == "MATCHED_CX_ENCODING_PACKETS_FROZEN_NO_HARDWARE"
    )
    calibration_pass = bool(verification_records) and all(record["pass"] for record in verification_records)
    decision = (
        "KNOWN_STATE_CALIBRATION_VERIFIED_READY_FOR_MATCHED_HARDWARE_EXECUTION"
        if packet_freeze_ready and calibration_pass and not missing_sources
        else "KNOWN_STATE_CALIBRATION_COUNTS_REQUIRED_BEFORE_HARDWARE_INTERPRETATION"
    )
    return {
        "schema_version": STAGE101_SCHEMA_VERSION,
        "stage": "stage101_known_state_calibration_gate",
        "status": "completed",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [
            str(stage99_manifest_path.as_posix()),
            str(stage100_manifest_path.as_posix()),
            str(calibration_manifest_path.as_posix()),
            str(calibration_verification_path.as_posix()),
        ],
        "missing_source_artifacts": missing_sources,
        "packet_freeze_ready": packet_freeze_ready,
        "stage99_decision": stage99.get("decision") if stage99 else None,
        "stage100_decision": stage100.get("decision") if stage100 else None,
        "stage4_calibration_verifier_pass": calibration_verification.get("pass") if calibration_verification else None,
        "provider_records": provider_records,
        "verification_records": verification_records,
        "known_state_calibration_pass": calibration_pass,
        "min_required_dominant_fraction": min_dominant_fraction,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "claim_boundary": {
            "supported": [
                "an executable known-state calibration evidence gate for Stage 99 and Stage 100 matched packet interpretation",
                "explicit bitstring-order inference over |00>, |01>, |10>, and |11> raw counts",
                "a hard block against interpreting matched hardware packets before calibration evidence passes",
            ],
            "excluded": [
                "completed provider calibration without raw known-state counts",
                "a noisy-hardware robustness result",
                "a provider-wide bitstring-order claim beyond the recorded backend/date/calibration metadata",
            ],
        },
        "next_gate": (
            "Supply real known-state execution JSON per provider/backend/date, then rerun this gate before executing "
            "or interpreting Stage 99 and Stage 100 matched packets."
        ),
    }


def write_stage101_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "packet_freeze_ready": result["packet_freeze_ready"],
        "known_state_calibration_pass": result["known_state_calibration_pass"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
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
            fieldnames=("provider", "expected_bitstring_order", "pass", "outcome", "missing_evidence"),
        )
        writer.writeheader()
        for record in result["verification_records"]:
            writer.writerow(
                {
                    "provider": record["provider"],
                    "expected_bitstring_order": record["expected_bitstring_order"],
                    "pass": record["pass"],
                    "outcome": record["outcome"],
                    "missing_evidence": "; ".join(record.get("missing_evidence", [])),
                }
            )
    return paths


def print_stage101_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"packet_freeze_ready: {result['packet_freeze_ready']}")
    print(f"known_state_calibration_pass: {result['known_state_calibration_pass']}")
    print(f"next_gate: {result['next_gate']}")
