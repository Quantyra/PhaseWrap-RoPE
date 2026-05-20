from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.automated_stage_gates import (  # noqa: E402
    ENTANGLING_CX_CIRCUIT_FAMILY,
    PRODUCT_STATE_CIRCUIT_FAMILY,
    evaluate_hardware_execution,
    evaluate_prediction_values,
)


DEFAULT_SWEEP_DIR = REPO_ROOT / "logs" / "automated_stage_gates" / "stage4_hardware_sweep"
DEFAULT_MANIFEST = DEFAULT_SWEEP_DIR / "manifest.json"
DEFAULT_OUTPUT = DEFAULT_SWEEP_DIR / "offline_verification.json"
METRIC_TOLERANCE = 1e-6

REQUIRED_RECORD_FIELDS = {
    "record_id",
    "provider",
    "backend",
    "family",
    "status",
    "shots",
    "rows",
    "packet_path",
    "execution_path",
    "evaluation_path",
    "summary_path",
}
SUPPORTED_MANIFEST_VERSIONS = {
    "stage4_hardware_sweep_manifest_v1",
    "stage4_simulation_sweep_manifest_v1",
}
SUPPORTED_FAMILIES = {PRODUCT_STATE_CIRCUIT_FAMILY, ENTANGLING_CX_CIRCUIT_FAMILY}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def json_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve_manifest_path(raw_path: str | None, manifest_path: Path) -> Path | None:
    if not raw_path:
        return None
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate
    manifest_relative = manifest_path.parent / candidate
    if manifest_relative.exists():
        return manifest_relative
    return REPO_ROOT / candidate


def select_metrics(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": payload.get("status"),
        "outcome": payload.get("outcome"),
        "gate_pass": payload.get("gate_pass"),
        "witness": payload.get("witness"),
        "control": payload.get("control"),
        "hardware_direction_positive": payload.get("hardware_direction_positive"),
        "noisy_direction_positive": payload.get("noisy_direction_positive"),
        "direction_agreement": payload.get("direction_agreement"),
        "metadata_complete": payload.get("metadata_complete"),
        "missing_metadata": payload.get("missing_metadata"),
        "comparability_pass": payload.get("comparability_pass"),
        "fail_reasons": payload.get("fail_reasons"),
    }


def metric_close(left: Any, right: Any, tolerance: float = METRIC_TOLERANCE) -> bool:
    if isinstance(left, bool) or isinstance(right, bool):
        return left is right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return abs(float(left) - float(right)) <= tolerance
    if isinstance(left, dict) and isinstance(right, dict):
        if set(left) != set(right):
            return False
        return all(metric_close(left[key], right[key], tolerance) for key in left)
    if isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right):
            return False
        return all(metric_close(a, b, tolerance) for a, b in zip(left, right))
    return left == right


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if manifest.get("manifest_version") not in SUPPORTED_MANIFEST_VERSIONS:
        errors.append(f"manifest_version must be one of {sorted(SUPPORTED_MANIFEST_VERSIONS)}")
    records = manifest.get("records")
    if not isinstance(records, list) or not records:
        errors.append("manifest must contain a non-empty records list")
        return errors
    seen: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"records[{index}] must be an object")
            continue
        missing = sorted(REQUIRED_RECORD_FIELDS - set(record))
        if missing:
            errors.append(f"records[{index}] missing required fields: {missing}")
        record_id = str(record.get("record_id", ""))
        if not record_id:
            errors.append(f"records[{index}] record_id is required")
        elif record_id in seen:
            errors.append(f"duplicate record_id: {record_id}")
        seen.add(record_id)
        status = record.get("status")
        if status not in {"completed", "missing"}:
            errors.append(f"{record_id or 'record'} status must be completed or missing")
        family = record.get("family")
        if family not in SUPPORTED_FAMILIES:
            errors.append(f"{record_id or 'record'} unsupported family: {family}")
        for numeric_field in ("shots", "rows"):
            value = record.get(numeric_field)
            if not isinstance(value, int) or value <= 0:
                errors.append(f"{record_id or 'record'} {numeric_field} must be a positive integer")
    return errors


def recompute_predictions(packet: dict[str, Any], execution: dict[str, Any]) -> dict[str, Any]:
    evaluation = evaluate_hardware_execution(packet, execution)
    rows = evaluation.get("per_row_results", [])
    labels = [float(row["label"]) for row in rows]
    witness_values = [float(row["hardware_predictions"]["witness"]) for row in rows]
    control_values = [float(row["hardware_predictions"]["control"]) for row in rows]
    return {
        "evaluation": evaluation,
        "witness": evaluate_prediction_values(labels, witness_values),
        "control": evaluate_prediction_values(labels, control_values),
        "rows": rows,
    }


def verify_record(record: dict[str, Any], manifest_path: Path) -> dict[str, Any]:
    record_id = record["record_id"]
    result: dict[str, Any] = {
        "record_id": record_id,
        "provider": record.get("provider"),
        "backend": record.get("backend"),
        "family": record.get("family"),
        "status": record.get("status"),
        "pass": False,
        "checks": [],
        "missing_artifacts": [],
    }

    def add_check(name: str, passed: bool, detail: Any = None) -> None:
        result["checks"].append({"name": name, "pass": bool(passed), "detail": detail})

    if record.get("status") == "missing":
        result["missing_artifacts"] = list(record.get("missing_required_artifacts") or [])
        add_check("record_has_real_evidence", False, record.get("todo") or "record is marked missing")
        return result

    packet_path = resolve_manifest_path(record.get("packet_path"), manifest_path)
    execution_path = resolve_manifest_path(record.get("execution_path"), manifest_path)
    evaluation_path = resolve_manifest_path(record.get("evaluation_path"), manifest_path)
    summary_path = resolve_manifest_path(record.get("summary_path"), manifest_path)
    paths = {
        "packet_path": packet_path,
        "execution_path": execution_path,
        "evaluation_path": evaluation_path,
        "summary_path": summary_path,
    }
    for name, path in paths.items():
        exists = bool(path and path.exists())
        add_check(f"{name}_exists", exists, str(path) if path else None)
        if not exists:
            result["missing_artifacts"].append(name)
    if result["missing_artifacts"]:
        return result

    assert packet_path is not None
    assert execution_path is not None
    assert evaluation_path is not None
    assert summary_path is not None
    packet = read_json(packet_path)
    execution = read_json(execution_path)
    recorded_evaluation = read_json(evaluation_path)
    summary = read_json(summary_path)
    recomputed = recompute_predictions(packet, execution)
    evaluation = recomputed["evaluation"]

    add_check("provider_matches_manifest", packet.get("provider") == record.get("provider"), packet.get("provider"))
    add_check("backend_matches_manifest", packet.get("backend") == record.get("backend"), packet.get("backend"))
    add_check("family_matches_manifest", packet.get("circuit_family") == record.get("family"), packet.get("circuit_family"))
    add_check("rows_match_manifest", len(packet.get("rows", [])) == record.get("rows"), len(packet.get("rows", [])))
    add_check("shots_match_manifest", packet.get("shot_count") == record.get("shots"), packet.get("shot_count"))
    add_check("execution_completed", execution.get("status") == "COMPLETED", execution.get("status"))
    add_check(
        "recorded_evaluation_matches_recomputed",
        metric_close(select_metrics(recorded_evaluation), select_metrics(evaluation)),
        {"recorded": select_metrics(recorded_evaluation), "recomputed": select_metrics(evaluation)},
    )
    summary_result = summary.get("result", summary)
    add_check("summary_status_matches_recomputed", summary_result.get("status") == evaluation.get("status"), summary_result.get("status"))
    add_check("summary_outcome_matches_recomputed", summary_result.get("outcome") == evaluation.get("outcome"), summary_result.get("outcome"))
    add_check(
        "witness_mae_beats_control",
        evaluation.get("witness", {}).get("mae", float("inf")) < evaluation.get("control", {}).get("mae", float("-inf")),
        {"witness": evaluation.get("witness"), "control": evaluation.get("control")},
    )
    add_check(
        "witness_rank_beats_control",
        evaluation.get("witness", {}).get("rank_correlation", float("-inf"))
        > evaluation.get("control", {}).get("rank_correlation", float("inf")),
        {"witness": evaluation.get("witness"), "control": evaluation.get("control")},
    )

    recorded_metrics = record.get("recorded_metrics")
    if recorded_metrics is not None:
        expected = {
            "witness": recorded_metrics.get("witness"),
            "control": recorded_metrics.get("control"),
            "outcome": recorded_metrics.get("outcome"),
        }
        actual = {
            "witness": evaluation.get("witness"),
            "control": evaluation.get("control"),
            "outcome": evaluation.get("outcome"),
        }
        add_check("manifest_metrics_match_recomputed", metric_close(expected, actual), {"manifest": expected, "recomputed": actual})

    job_ids = [str(job.get("job_id", "")) for job in execution.get("jobs", [])]
    table_row = {
        "backend": record.get("backend"),
        "provider": record.get("provider"),
        "family": record.get("family"),
        "shots": record.get("shots"),
        "rows": record.get("rows"),
        "witness_mae": evaluation.get("witness", {}).get("mae"),
        "witness_rank_corr": evaluation.get("witness", {}).get("rank_correlation"),
        "control_mae": evaluation.get("control", {}).get("mae"),
        "control_rank_corr": evaluation.get("control", {}).get("rank_correlation"),
        "outcome": evaluation.get("outcome"),
    }
    result.update(
        {
            "packet_id": packet.get("packet_id"),
            "job_ids": job_ids,
            "packet_sha256": json_hash(packet_path),
            "execution_sha256": json_hash(execution_path),
            "evaluation_sha256": json_hash(evaluation_path),
            "summary_sha256": json_hash(summary_path),
            "recomputed_metrics": {
                "witness": evaluation.get("witness"),
                "control": evaluation.get("control"),
                "outcome": evaluation.get("outcome"),
                "gate_pass": evaluation.get("gate_pass"),
            },
            "table_row": table_row,
        }
    )
    result["pass"] = all(check["pass"] for check in result["checks"])
    return result


def verify_sweep_manifest(manifest_path: Path) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    manifest_errors = validate_manifest(manifest)
    record_results = [] if manifest_errors else [verify_record(record, manifest_path) for record in manifest["records"]]
    missing_records = [item for item in record_results if item.get("status") == "missing" or item.get("missing_artifacts")]
    table = [item["table_row"] for item in record_results if item.get("table_row")]
    return {
        "verifier": "phasewrap_rope_stage4_hardware_sweep_offline_verifier_v1",
        "no_hardware_submission": True,
        "hardware_cost_usd": 0,
        "manifest_path": str(manifest_path),
        "manifest_sha256": json_hash(manifest_path),
        "sweep_id": manifest.get("sweep_id"),
        "claim_boundary": manifest.get("claim_boundary"),
        "budget_policy": manifest.get("budget_policy"),
        "manifest_errors": manifest_errors,
        "records": record_results,
        "missing_records": [item.get("record_id") for item in missing_records],
        "table": table,
        "pass": not manifest_errors and bool(record_results) and all(item.get("pass") for item in record_results),
    }


def print_table(rows: list[dict[str, Any]]) -> None:
    headers = [
        "backend",
        "provider",
        "family",
        "shots",
        "rows",
        "witness_mae",
        "witness_rank_corr",
        "control_mae",
        "control_rank_corr",
        "outcome",
    ]
    print(" | ".join(headers))
    print(" | ".join("---" for _ in headers))
    for row in rows:
        print(" | ".join(str(row.get(header, "")) for header in headers))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline verifier for the PhaseWrap-RoPE Stage 4 hardware sweep.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    verification = verify_sweep_manifest(args.manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if verification["table"]:
        print_table(verification["table"])
    summary = {
        "pass": verification["pass"],
        "sweep_id": verification.get("sweep_id"),
        "missing_records": verification.get("missing_records"),
        "manifest_errors": verification.get("manifest_errors"),
        "output": str(args.output),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if verification["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
