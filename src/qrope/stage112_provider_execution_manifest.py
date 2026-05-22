from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE112_SCHEMA_VERSION = "qrope_stage112_provider_execution_manifest_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE107_WINDOW_PLANS = DEFAULT_ARTIFACT_ROOT / "stage107_window_execution_orchestrator" / "window_execution_plans.json"
DEFAULT_STAGE111_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage111_provider_sdk_backend_discovery" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage112_provider_execution_manifest"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _step(plan: dict[str, Any], step_id: str) -> dict[str, Any]:
    for item in plan.get("steps", []):
        if item.get("step_id") == step_id:
            return item
    return {}


def _stage111_provider_status(stage111: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not stage111:
        return {}
    return {str(record.get("provider")): record for record in stage111.get("provider_records", [])}


def _calibration_jobs(plan: dict[str, Any]) -> list[dict[str, Any]]:
    step = _step(plan, "known_state_calibration_execution")
    template_path = Path(str(step.get("template_path", "")))
    output_path = str(step.get("output_path", ""))
    template = _load_json(template_path)
    jobs = []
    for row in template.get("raw_counts_by_state", []) if isinstance(template, dict) else []:
        state = str(row.get("state"))
        jobs.append(
            {
                "job_id": f"{plan['window_id']}__calibration__state_{state}",
                "job_kind": "known_state_calibration",
                "window_id": plan["window_id"],
                "provider": plan["provider"],
                "state": state,
                "shots": template.get("shots_per_state"),
                "openqasm3": row.get("openqasm3"),
                "template_path": str(template_path.as_posix()),
                "target_evidence_path": output_path,
                "target_counts_container": "raw_counts_by_state",
                "target_counts_key": state,
            }
        )
    return jobs


def _packet_jobs(plan: dict[str, Any]) -> list[dict[str, Any]]:
    step = _step(plan, "matched_packet_execution")
    output_dir = Path(str(step.get("output_dir", "")))
    jobs = []
    for packet_template in step.get("packet_templates", []):
        template_path = Path(str(packet_template.get("template_path", "")))
        template = _load_json(template_path)
        packet_id = str(packet_template.get("packet_id"))
        for row in template.get("raw_counts_by_row", []) if isinstance(template, dict) else []:
            row_id = str(row.get("row_id"))
            jobs.append(
                {
                    "job_id": f"{plan['window_id']}__packet__{packet_id}__{row_id}",
                    "job_kind": "matched_packet_row",
                    "window_id": plan["window_id"],
                    "provider": plan["provider"],
                    "packet_id": packet_id,
                    "source_lane_id": packet_template.get("source_lane_id"),
                    "encoding_family": packet_template.get("encoding_family"),
                    "circuit_template": packet_template.get("circuit_template"),
                    "row_id": row_id,
                    "shots": template.get("shot_count", packet_template.get("shot_count")),
                    "openqasm3": row.get("openqasm3"),
                    "template_path": str(template_path.as_posix()),
                    "target_evidence_path": str((output_dir / f"{packet_id}.json").as_posix()),
                    "target_counts_container": "raw_counts_by_row",
                    "target_counts_key": row_id,
                }
            )
    return jobs


def _window_manifest(plan: dict[str, Any], provider_status: dict[str, Any] | None) -> dict[str, Any]:
    calibration_jobs = _calibration_jobs(plan)
    packet_jobs = _packet_jobs(plan)
    submission_ready = bool(provider_status and provider_status.get("status") == "ready")
    blockers = [] if submission_ready else ["stage111_provider_not_ready"]
    if provider_status:
        blockers.extend(str(item) for item in provider_status.get("blockers", []))
    return {
        "window_id": plan["window_id"],
        "provider": plan["provider"],
        "window_index": plan["window_index"],
        "submission_ready": submission_ready,
        "blockers": sorted(set(blockers)),
        "calibration_job_count": len(calibration_jobs),
        "packet_job_count": len(packet_jobs),
        "total_job_count": len(calibration_jobs) + len(packet_jobs),
        "calibration_jobs": calibration_jobs,
        "packet_jobs": packet_jobs,
    }


def run_stage112_manifest(
    *,
    stage107_window_plans_path: Path = DEFAULT_STAGE107_WINDOW_PLANS,
    stage111_results_path: Path = DEFAULT_STAGE111_RESULTS,
) -> dict[str, Any]:
    plans = _load_json(stage107_window_plans_path)
    stage111 = _load_json(stage111_results_path)
    sources = [
        (stage107_window_plans_path, plans),
        (stage111_results_path, stage111),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    window_plans = plans if isinstance(plans, list) else []
    provider_status = _stage111_provider_status(stage111 if isinstance(stage111, dict) else None)
    window_manifests = [_window_manifest(plan, provider_status.get(str(plan.get("provider")))) for plan in window_plans]
    submission_ready = bool(window_manifests) and all(window["submission_ready"] for window in window_manifests) and not missing_sources
    return {
        "schema_version": STAGE112_SCHEMA_VERSION,
        "stage": "stage112_provider_execution_manifest",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "PROVIDER_EXECUTION_MANIFEST_READY_FOR_SUBMISSION"
            if submission_ready
            else "PROVIDER_EXECUTION_MANIFEST_PREPARED_SUBMISSION_BLOCKED"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage111_decision": stage111.get("decision") if isinstance(stage111, dict) else None,
        "window_count": len(window_manifests),
        "submission_ready_window_count": sum(1 for window in window_manifests if window["submission_ready"]),
        "calibration_job_count": sum(window["calibration_job_count"] for window in window_manifests),
        "packet_job_count": sum(window["packet_job_count"] for window in window_manifests),
        "total_job_count": sum(window["total_job_count"] for window in window_manifests),
        "window_manifests": window_manifests,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "a deterministic provider execution manifest for Stage 107 calibration and packet circuits",
                "stable job IDs and target evidence paths for filling Stage 109-compatible result files",
                "a no-submission handoff from provider readiness gates to future execution drivers",
            ],
            "excluded": [
                "hardware job submission",
                "completed calibration counts",
                "completed matched packet counts",
                "a noisy-hardware robustness result",
            ],
        },
        "next_gate": (
            "Clear Stage 111 provider readiness, then use this manifest to drive provider-specific calibration and packet "
            "execution while writing counts to the declared target evidence files."
        ),
    }


def write_stage112_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage111_decision": result["stage111_decision"],
        "window_count": result["window_count"],
        "submission_ready_window_count": result["submission_ready_window_count"],
        "calibration_job_count": result["calibration_job_count"],
        "packet_job_count": result["packet_job_count"],
        "total_job_count": result["total_job_count"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "secret_values_recorded": result["secret_values_recorded"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "job_manifest_jsonl_path": str((output_dir / "job_manifest.jsonl").as_posix()),
        "claim_boundary": result["claim_boundary"],
        "next_gate": result["next_gate"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "job_manifest_jsonl": str(output_dir / "job_manifest.jsonl"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "job_manifest.jsonl").open("w", encoding="utf-8") as handle:
        for window in result["window_manifests"]:
            for job in window["calibration_jobs"] + window["packet_jobs"]:
                handle.write(json.dumps(job, sort_keys=True) + "\n")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("window_id", "provider", "submission_ready", "calibration_job_count", "packet_job_count", "total_job_count", "blockers"),
        )
        writer.writeheader()
        for window in result["window_manifests"]:
            writer.writerow(
                {
                    "window_id": window["window_id"],
                    "provider": window["provider"],
                    "submission_ready": window["submission_ready"],
                    "calibration_job_count": window["calibration_job_count"],
                    "packet_job_count": window["packet_job_count"],
                    "total_job_count": window["total_job_count"],
                    "blockers": "; ".join(window["blockers"]),
                }
            )
    return paths


def print_stage112_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"window_count: {result['window_count']}")
    print(f"submission_ready_window_count: {result['submission_ready_window_count']}")
    print(f"total_job_count: {result['total_job_count']}")
    print(f"next_gate: {result['next_gate']}")
