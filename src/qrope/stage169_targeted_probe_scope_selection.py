from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE169_SCHEMA_VERSION = "qrope_stage169_targeted_probe_scope_selection_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE165_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage165_simulated_noise_margin_stability_audit" / "results.json"
DEFAULT_STAGE163_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage163_first_provider_prerun_lock" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage169_targeted_probe_scope_selection"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
STAGE165_READY = "SIMULATED_NOISE_STABLE_TARGETED_HARDWARE_PROBE_RECOMMENDED"
STAGE163_READY = "FIRST_PROVIDER_PRERUN_LOCK_READY_AWAITING_APPROVAL"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _locked_lane_records(stage163: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(stage163, dict):
        return []
    by_lane: dict[str, dict[str, Any]] = {}
    for lock in stage163.get("window_locks", []):
        if not isinstance(lock, dict):
            continue
        window_id = str(lock.get("window_id"))
        for job in _load_jsonl(Path(str(lock.get("job_shard_path", "")))):
            if job.get("job_kind") != "matched_packet_row":
                continue
            lane_id = str(job.get("source_lane_id"))
            record = by_lane.setdefault(
                lane_id,
                {
                    "provider": job.get("provider"),
                    "source_lane_id": lane_id,
                    "circuit_template": job.get("circuit_template"),
                    "window_ids": set(),
                    "encoding_families": set(),
                    "row_job_count": 0,
                    "shots": int(job.get("shots") or 0),
                },
            )
            record["window_ids"].add(window_id)
            record["encoding_families"].add(str(job.get("encoding_family")))
            record["row_job_count"] += 1
    return [
        {
            **record,
            "window_ids": sorted(record["window_ids"]),
            "encoding_families": sorted(record["encoding_families"]),
        }
        for record in sorted(by_lane.values(), key=lambda item: item["source_lane_id"])
    ]


def _stable_targets(stage165: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(stage165, dict):
        return []
    return [record for record in stage165.get("target_records", []) if isinstance(record, dict) and record.get("stable_target") is True]


def _excluded_targets(stage165: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(stage165, dict):
        return []
    return [record for record in stage165.get("target_records", []) if isinstance(record, dict) and record.get("stable_target") is not True]


def run_stage169_scope_selection(
    *,
    stage165_results_path: Path = DEFAULT_STAGE165_RESULTS,
    stage163_results_path: Path = DEFAULT_STAGE163_RESULTS,
) -> dict[str, Any]:
    stage165 = _load_json(stage165_results_path)
    stage163 = _load_json(stage163_results_path)
    sources = [(stage165_results_path, stage165), (stage163_results_path, stage163)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    stable_targets = _stable_targets(stage165)
    excluded_targets = _excluded_targets(stage165)
    locked_lanes = _locked_lane_records(stage163)
    stable_lane_ids = sorted({str(record.get("source_lane_id")) for record in stable_targets})
    excluded_lane_ids = sorted({str(record.get("source_lane_id")) for record in excluded_targets})
    locked_lane_ids = sorted({str(record.get("source_lane_id")) for record in locked_lanes})
    blockers = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    if isinstance(stage165, dict) and stage165.get("decision") != STAGE165_READY:
        blockers.append("stage165_not_stable_targeted_probe_ready")
    if isinstance(stage163, dict) and stage163.get("decision") != STAGE163_READY:
        blockers.append("stage163_prerun_lock_not_ready")
    if not stable_lane_ids:
        blockers.append("no_stable_target_lanes")
    if not set(stable_lane_ids).issubset(set(locked_lane_ids)):
        blockers.append("stable_target_lanes_not_covered_by_locked_shards")
    if set(excluded_lane_ids).intersection(set(stable_lane_ids)):
        blockers.append("excluded_lane_overlaps_stable_lane")
    decision = (
        "TARGETED_PROBE_SCOPE_SELECTION_INCOMPLETE"
        if missing_sources
        else "TARGETED_IBM_PROBE_SCOPE_LOCKED_TO_STABLE_LANES"
        if not blockers
        else "TARGETED_PROBE_SCOPE_SELECTION_BLOCKED"
    )
    return {
        "schema_version": STAGE169_SCHEMA_VERSION,
        "stage": "stage169_targeted_probe_scope_selection",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage165_decision": stage165.get("decision") if isinstance(stage165, dict) else None,
        "stage163_decision": stage163.get("decision") if isinstance(stage163, dict) else None,
        "stable_target_lane_count": len(stable_lane_ids),
        "stable_target_lanes": stable_lane_ids,
        "excluded_recommended_lane_count": len(excluded_lane_ids),
        "excluded_recommended_lanes": excluded_lane_ids,
        "locked_lane_count": len(locked_lane_ids),
        "locked_lanes": locked_lanes,
        "locked_lane_ids": locked_lane_ids,
        "stable_targets": stable_targets,
        "excluded_targets": excluded_targets,
        "approved_job_count": stage163.get("approved_job_count") if isinstance(stage163, dict) else None,
        "locked_total_shots": stage163.get("locked_total_shots") if isinstance(stage163, dict) else None,
        "blockers": sorted(set(blockers)),
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "explicit no-submit target selection for the current IBM hardware probe",
                "stable Stage165 source lanes are mapped against the already locked Stage163 job shards",
                "nonstable recommended lanes, including seed577 lanes, are excluded from the current probe scope",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "new job-shard generation",
                "IBM credit or provider availability validation",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "Before any IBM execution, verify credit/provider state with the user. Execute only the locked Stage163 IBM shards "
            "whose source lanes include the stable Stage165 target lanes; do not broaden to excluded recommended lanes."
        ),
    }


def write_stage169_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage165_decision": result["stage165_decision"],
        "stage163_decision": result["stage163_decision"],
        "stable_target_lane_count": result["stable_target_lane_count"],
        "stable_target_lanes": result["stable_target_lanes"],
        "excluded_recommended_lane_count": result["excluded_recommended_lane_count"],
        "locked_lane_count": result["locked_lane_count"],
        "approved_job_count": result["approved_job_count"],
        "locked_total_shots": result["locked_total_shots"],
        "blockers": result["blockers"],
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
            fieldnames=("source_lane_id", "circuit_template", "stable_target", "locked", "reason"),
        )
        writer.writeheader()
        locked = set(result["locked_lane_ids"])
        for lane_id in result["stable_target_lanes"]:
            writer.writerow(
                {
                    "source_lane_id": lane_id,
                    "circuit_template": next(
                        (item.get("circuit_template") for item in result["stable_targets"] if item.get("source_lane_id") == lane_id),
                        "",
                    ),
                    "stable_target": True,
                    "locked": lane_id in locked,
                    "reason": "selected_stable_stage165_target",
                }
            )
        for lane_id in result["excluded_recommended_lanes"]:
            writer.writerow(
                {
                    "source_lane_id": lane_id,
                    "circuit_template": next(
                        (item.get("circuit_template") for item in result["excluded_targets"] if item.get("source_lane_id") == lane_id),
                        "",
                    ),
                    "stable_target": False,
                    "locked": lane_id in locked,
                    "reason": "excluded_by_stage165_stability_filter",
                }
            )
    return paths


def print_stage169_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"stable_target_lane_count: {result['stable_target_lane_count']}")
    print(f"excluded_recommended_lane_count: {result['excluded_recommended_lane_count']}")
    print(f"locked_lane_count: {result['locked_lane_count']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
