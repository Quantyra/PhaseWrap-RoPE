from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.automated_stage_gates import (
    ENTANGLING_CX_CIRCUIT_FAMILY,
    counts_to_expectations,
    evaluate_hardware_execution,
    evaluate_prediction_values,
)


DEFAULT_SWEEP_DIR = REPO_ROOT / "logs" / "automated_stage_gates" / "stage4_hardware_sweep"
DEFAULT_MANIFEST = DEFAULT_SWEEP_DIR / "manifest.json"
DEFAULT_OUTPUT = DEFAULT_SWEEP_DIR / "offline_verification.json"

MANIFEST_SCHEMA_VERSION = "qrope_stage4_hardware_sweep_manifest_v1"
VERIFIER_VERSION = "qrope_stage4_hardware_sweep_offline_verifier_v1"
METRIC_TOLERANCE = 1e-6
FORBIDDEN_SUPPORTED_CLAIMS = [
    "quantum advantage proven",
    "transformer superiority proven",
    "general cross-backend robustness established",
    "production llm improvement",
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def resolve_manifest_path(manifest_path: Path, raw_path: str | None) -> Path | None:
    if not raw_path:
        return None
    path = Path(raw_path)
    if path.is_absolute():
        return path
    repo_relative = REPO_ROOT / path
    if repo_relative.exists():
        return repo_relative
    return manifest_path.parent / path


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def mean_absolute_error(labels: list[float], predictions: list[float]) -> float:
    return evaluate_prediction_values(labels, predictions)["mae"]


def rank_correlation(labels: list[float], predictions: list[float]) -> float:
    return evaluate_prediction_values(labels, predictions)["rank_correlation"]


def raw_counts_to_expectations(counts: dict[str, int], bitstring_order: str = "q1q0") -> dict[str, Any]:
    return counts_to_expectations(counts, bitstring_order=bitstring_order)


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    required = [
        "schema_version",
        "sweep_id",
        "packet_id",
        "witness_families",
        "backends",
        "records",
        "bounded_claim_statement",
        "claim_boundary",
    ]
    for key in required:
        if key not in manifest:
            errors.append(f"manifest missing required field: {key}")
    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        errors.append(
            f"manifest schema_version must be {MANIFEST_SCHEMA_VERSION}, got {manifest.get('schema_version')}"
        )
    if not isinstance(manifest.get("witness_families"), list) or not manifest.get("witness_families"):
        errors.append("manifest witness_families must be a non-empty list")
    if not isinstance(manifest.get("backends"), list) or not manifest.get("backends"):
        errors.append("manifest backends must be a non-empty list")
    records = manifest.get("records")
    if not isinstance(records, list) or not records:
        errors.append("manifest records must be a non-empty list")
        return errors
    record_ids: set[str] = set()
    for index, record in enumerate(records):
        prefix = f"records[{index}]"
        for key in ("record_id", "provider", "backend", "family", "status", "shots", "row_count"):
            if key not in record:
                errors.append(f"{prefix} missing required field: {key}")
        record_id = str(record.get("record_id", "")).strip()
        if not record_id:
            errors.append(f"{prefix}.record_id must be non-empty")
        elif record_id in record_ids:
            errors.append(f"duplicate record_id: {record_id}")
        record_ids.add(record_id)
        if record.get("family") not in set(manifest.get("witness_families", [])):
            errors.append(f"{prefix}.family is not listed in manifest witness_families")
        if record.get("status") not in {"completed", "missing_evidence"}:
            errors.append(f"{prefix}.status must be completed or missing_evidence")
        if record.get("expected_outcome") and record.get("expected_outcome") not in {"hardware-positive", "hardware-negative"}:
            errors.append(f"{prefix}.expected_outcome must be hardware-positive or hardware-negative")
        if record.get("status") == "completed":
            for key in ("packet_path", "execution_path", "evaluation_path", "summary_path"):
                if not record.get(key):
                    errors.append(f"{prefix} completed record missing path field: {key}")
            if record.get("bitstring_order") not in {"q1q0", "q0q1"}:
                errors.append(f"{prefix} completed record bitstring_order must be q1q0 or q0q1")
        if record.get("status") == "missing_evidence" and not record.get("missing_evidence"):
            errors.append(f"{prefix} missing_evidence record must list missing_evidence")
    return errors


def compare_metric(name: str, recorded: Any, recomputed: Any, tolerance: float) -> dict[str, Any]:
    try:
        recorded_float = float(recorded)
        recomputed_float = float(recomputed)
    except (TypeError, ValueError):
        return {"name": name, "pass": False, "recorded": recorded, "recomputed": recomputed}
    return {
        "name": name,
        "pass": abs(recorded_float - recomputed_float) <= tolerance,
        "recorded": recorded_float,
        "recomputed": recomputed_float,
        "tolerance": tolerance,
    }


def _record_metric_checks(
    recorded: dict[str, Any],
    recomputed: dict[str, Any],
    expected_outcome: str | None = None,
) -> list[dict[str, Any]]:
    expected = expected_outcome or "hardware-positive"
    checks = [
        compare_metric("witness_mae", recorded.get("witness", {}).get("mae"), recomputed.get("witness", {}).get("mae"), METRIC_TOLERANCE),
        compare_metric(
            "witness_rank_correlation",
            recorded.get("witness", {}).get("rank_correlation"),
            recomputed.get("witness", {}).get("rank_correlation"),
            METRIC_TOLERANCE,
        ),
        compare_metric("control_mae", recorded.get("control", {}).get("mae"), recomputed.get("control", {}).get("mae"), METRIC_TOLERANCE),
        compare_metric(
            "control_rank_correlation",
            recorded.get("control", {}).get("rank_correlation"),
            recomputed.get("control", {}).get("rank_correlation"),
            METRIC_TOLERANCE,
        ),
    ]
    checks.extend(
        [
            {
                "name": "status_matches",
                "pass": recorded.get("status") == recomputed.get("status"),
                "recorded": recorded.get("status"),
                "recomputed": recomputed.get("status"),
            },
            {
                "name": "outcome_matches",
                "pass": recorded.get("outcome") == recomputed.get("outcome"),
                "recorded": recorded.get("outcome"),
                "recomputed": recomputed.get("outcome"),
            },
            {
                "name": "gate_pass_matches",
                "pass": recorded.get("gate_pass") is recomputed.get("gate_pass"),
                "recorded": recorded.get("gate_pass"),
                "recomputed": recomputed.get("gate_pass"),
            },
            {
                "name": "expected_outcome_matches",
                "pass": recomputed.get("outcome") == expected,
                "expected": expected,
                "recomputed": recomputed.get("outcome"),
            },
        ]
    )
    if expected == "hardware-positive":
        checks.extend(
            [
                {
                    "name": "witness_beats_control_mae",
                    "pass": recomputed.get("witness", {}).get("mae", 1.0)
                    < recomputed.get("control", {}).get("mae", 0.0),
                    "witness": recomputed.get("witness", {}).get("mae"),
                    "control": recomputed.get("control", {}).get("mae"),
                },
                {
                    "name": "witness_beats_control_rank",
                    "pass": recomputed.get("witness", {}).get("rank_correlation", -1.0)
                    > recomputed.get("control", {}).get("rank_correlation", 1.0),
                    "witness": recomputed.get("witness", {}).get("rank_correlation"),
                    "control": recomputed.get("control", {}).get("rank_correlation"),
                },
            ]
        )
    else:
        checks.extend(
            [
                {
                    "name": "negative_record_does_not_support_positive_gate",
                    "pass": recomputed.get("gate_pass") is False,
                    "gate_pass": recomputed.get("gate_pass"),
                },
                {
                    "name": "negative_record_outcome_is_hardware_negative",
                    "pass": recomputed.get("outcome") == "hardware-negative",
                    "outcome": recomputed.get("outcome"),
                },
            ]
        )
    return checks


def _job_ids_from_execution(execution: dict[str, Any]) -> list[str]:
    job_ids: list[str] = []
    for job in execution.get("jobs", []):
        for record in job.get("provider_job_records", []):
            job_id = str(record.get("job_id", "")).strip()
            if job_id:
                job_ids.append(job_id)
        if not job.get("provider_job_records"):
            job_ids.extend(item for item in str(job.get("job_id", "")).split(",") if item)
    return job_ids


def _timestamps_from_execution(execution: dict[str, Any]) -> dict[str, str | None]:
    submitted: list[str] = []
    completed: list[str] = []
    for job in execution.get("jobs", []):
        if job.get("submitted_at_utc"):
            submitted.append(str(job["submitted_at_utc"]))
        if job.get("completed_at_utc"):
            completed.append(str(job["completed_at_utc"]))
        for record in job.get("provider_job_records", []):
            if record.get("submitted_at_utc"):
                submitted.append(str(record["submitted_at_utc"]))
            if record.get("completed_at_utc"):
                completed.append(str(record["completed_at_utc"]))
    return {
        "submitted_at_utc": min(submitted) if submitted else None,
        "completed_at_utc": max(completed) if completed else None,
    }


def verify_record(manifest_path: Path, record: dict[str, Any]) -> dict[str, Any]:
    base = {
        "record_id": record.get("record_id"),
        "provider": record.get("provider"),
        "backend": record.get("backend"),
        "backend_label": record.get("backend_label"),
        "family": record.get("family"),
        "shots": record.get("shots"),
        "row_count": record.get("row_count"),
        "status": record.get("status"),
        "bitstring_order": record.get("bitstring_order"),
    }
    if record.get("status") != "completed":
        return {
            **base,
            "pass": False,
            "outcome": "missing-evidence",
            "missing_evidence": record.get("missing_evidence", []),
            "checks": [{"name": "real_evidence_present", "pass": False, "detail": record.get("missing_evidence", [])}],
        }

    missing_paths: list[str] = []
    resolved_paths: dict[str, str] = {}
    for key in ("packet_path", "execution_path", "evaluation_path", "summary_path"):
        path = resolve_manifest_path(manifest_path, record.get(key))
        if path is None or not path.exists():
            missing_paths.append(str(record.get(key)))
        else:
            resolved_paths[key] = str(path.relative_to(REPO_ROOT))
    if missing_paths:
        return {
            **base,
            "pass": False,
            "outcome": "missing-evidence",
            "missing_evidence": missing_paths,
            "checks": [{"name": "required_paths_exist", "pass": False, "detail": missing_paths}],
        }

    packet = read_json(REPO_ROOT / resolved_paths["packet_path"])
    execution = read_json(REPO_ROOT / resolved_paths["execution_path"])
    evaluation = read_json(REPO_ROOT / resolved_paths["evaluation_path"])
    summary = read_json(REPO_ROOT / resolved_paths["summary_path"])
    recomputed = evaluate_hardware_execution(packet, execution, bitstring_order=record.get("bitstring_order"))
    summary_result = summary.get("result", summary)
    summary_evaluation = summary_result.get("evaluation", summary_result)
    checks = _record_metric_checks(evaluation, recomputed, record.get("expected_outcome"))
    checks.extend(
        [
            {
                "name": "summary_status_matches_recomputed",
                "pass": summary_result.get("status") == recomputed.get("status"),
                "recorded": summary_result.get("status"),
                "recomputed": recomputed.get("status"),
            },
            {
                "name": "summary_outcome_matches_recomputed",
                "pass": summary_evaluation.get("outcome") == recomputed.get("outcome"),
                "recorded": summary_evaluation.get("outcome"),
                "recomputed": recomputed.get("outcome"),
            },
            {
                "name": "packet_family_matches_manifest",
                "pass": packet.get("circuit_family") == record.get("family"),
                "packet_family": packet.get("circuit_family"),
                "manifest_family": record.get("family"),
            },
            {
                "name": "packet_backend_matches_manifest",
                "pass": packet.get("backend") == record.get("backend"),
                "packet_backend": packet.get("backend"),
                "manifest_backend": record.get("backend"),
            },
            {
                "name": "packet_row_count_matches_manifest",
                "pass": packet.get("row_count") == record.get("row_count"),
                "packet_row_count": packet.get("row_count"),
                "manifest_row_count": record.get("row_count"),
            },
            {
                "name": "packet_shots_match_manifest",
                "pass": packet.get("shot_count") == record.get("shots"),
                "packet_shots": packet.get("shot_count"),
                "manifest_shots": record.get("shots"),
            },
            {
                "name": "evaluation_bitstring_order_matches_manifest",
                "pass": evaluation.get("bitstring_order") == record.get("bitstring_order"),
                "recorded": evaluation.get("bitstring_order"),
                "manifest_bitstring_order": record.get("bitstring_order"),
            },
        ]
    )
    timestamps = _timestamps_from_execution(execution)
    table_row = {
        "backend": record.get("backend_label") or record.get("backend"),
        "provider": record.get("provider"),
        "family": record.get("family"),
        "shots": record.get("shots"),
        "rows": record.get("row_count"),
        "witness_mae": recomputed.get("witness", {}).get("mae"),
        "witness_rank_corr": recomputed.get("witness", {}).get("rank_correlation"),
        "control_mae": recomputed.get("control", {}).get("mae"),
        "control_rank_corr": recomputed.get("control", {}).get("rank_correlation"),
        "outcome": recomputed.get("outcome"),
        "expected_outcome": record.get("expected_outcome") or "hardware-positive",
        "bitstring_order": record.get("bitstring_order"),
    }
    return {
        **base,
        "pass": all(check["pass"] for check in checks),
        "outcome": recomputed.get("outcome"),
        "gate_pass": recomputed.get("gate_pass"),
        "packet_id": packet.get("packet_id"),
        "job_ids": _job_ids_from_execution(execution),
        "submitted_at_utc": timestamps["submitted_at_utc"],
        "completed_at_utc": timestamps["completed_at_utc"],
        "paths": resolved_paths,
        "recorded_evaluation": evaluation,
        "recomputed_evaluation": recomputed,
        "checks": checks,
        "table_row": table_row,
    }


def verify_manifest(manifest_path: Path) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    schema_errors = validate_manifest(manifest)
    records = []
    if not schema_errors:
        records = [verify_record(manifest_path, record) for record in manifest["records"]]
    completed_rows = [record["table_row"] for record in records if record.get("pass") and record.get("table_row")]
    missing = [
        {"record_id": record.get("record_id"), "missing_evidence": record.get("missing_evidence", [])}
        for record in records
        if record.get("outcome") == "missing-evidence"
    ]
    verification = {
        "verifier": VERIFIER_VERSION,
        "manifest_path": display_path(manifest_path),
        "manifest_schema_version": manifest.get("schema_version"),
        "sweep_id": manifest.get("sweep_id"),
        "bounded_claim_statement": manifest.get("bounded_claim_statement"),
        "claim_boundary": manifest.get("claim_boundary"),
        "schema_errors": schema_errors,
        "records": records,
        "table": completed_rows,
        "missing_evidence": missing,
        "pass": not schema_errors and bool(records) and all(record.get("pass") for record in records),
    }
    return verification


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


def scan_public_docs_for_overclaims(paths: list[Path]) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8").lower()
        for phrase in FORBIDDEN_SUPPORTED_CLAIMS:
            if phrase in text:
                findings.append({"path": display_path(path), "phrase": phrase})
    return {"pass": not findings, "findings": findings}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline verifier for the QRoPE Stage 4 hardware sweep manifest.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    verification = verify_manifest(args.manifest)
    guardrail = scan_public_docs_for_overclaims(
        [
            REPO_ROOT / "README.md",
            REPO_ROOT / "docs" / "publication" / "qrope-paper-v1.md",
            REPO_ROOT / "docs" / "research" / "q-rope-stage4-hardware-comparison-v1.md",
            REPO_ROOT / "docs" / "research" / "q-rope-stage4-real-hardware-validation-result-v1.md",
        ]
    )
    verification["overclaim_guardrail"] = guardrail
    verification["pass"] = verification["pass"] and guardrail["pass"]
    write_json(args.output, verification)
    print_table(verification["table"])
    if verification["missing_evidence"]:
        print("\nMissing evidence records:", file=sys.stderr)
        for item in verification["missing_evidence"]:
            print(f"- {item['record_id']}: {', '.join(item['missing_evidence'])}", file=sys.stderr)
    print(json.dumps({"pass": verification["pass"], "records": len(verification["records"])}, indent=2))
    return 0 if verification["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
