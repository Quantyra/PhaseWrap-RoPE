from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE174_SCHEMA_VERSION = "qrope_stage174_locked_interpretation_surface_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE104_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage104_matched_packet_execution_package" / "results.json"
DEFAULT_STAGE163_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage163_first_provider_prerun_lock" / "results.json"
DEFAULT_STAGE169_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage169_targeted_probe_scope_selection" / "results.json"
DEFAULT_STAGE173_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage173_locked_result_ingestion_contract_audit" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage174_locked_interpretation_surface_audit"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
STAGE104_READY = "MATCHED_PACKET_EXECUTION_TEMPLATES_PREPARED_CALIBRATION_AND_COUNTS_REQUIRED"
STAGE163_READY = "FIRST_PROVIDER_PRERUN_LOCK_READY_AWAITING_APPROVAL"
STAGE169_READY = "TARGETED_IBM_PROBE_SCOPE_LOCKED_TO_STABLE_LANES"
STAGE173_READY = "LOCKED_RESULT_INGESTION_CONTRACT_READY_AWAITING_PROVIDER_RESULTS"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _stage104_templates(stage104: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not isinstance(stage104, dict):
        return {}
    return {
        str(template.get("packet_id")): template
        for template in stage104.get("templates", [])
        if isinstance(template, dict) and template.get("packet_id")
    }


def _locked_jobs(stage163: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not isinstance(stage163, dict):
        return []
    jobs: list[dict[str, Any]] = []
    for lock in stage163.get("window_locks", []):
        if not isinstance(lock, dict):
            continue
        for job in _load_jsonl(Path(str(lock.get("job_shard_path") or ""))):
            jobs.append(job)
    return jobs


def _group_record(
    *,
    provider: str,
    source_lane_id: str,
    circuit_template: str,
    jobs: list[dict[str, Any]],
    templates_by_packet: dict[str, dict[str, Any]],
    required_families: list[str],
) -> dict[str, Any]:
    matched_jobs = [
        job
        for job in jobs
        if job.get("job_kind") == "matched_packet_row"
        and job.get("provider") == provider
        and job.get("source_lane_id") == source_lane_id
        and job.get("circuit_template") == circuit_template
    ]
    families = sorted({str(job.get("encoding_family")) for job in matched_jobs})
    packet_ids = sorted({str(job.get("packet_id")) for job in matched_jobs})
    row_counts_by_family: dict[str, int] = {}
    row_ids_by_family: dict[str, set[str]] = {}
    template_row_ids_by_family: dict[str, set[str]] = {}
    missing_packets: list[str] = []
    for family in required_families:
        family_jobs = [job for job in matched_jobs if job.get("encoding_family") == family]
        row_counts_by_family[family] = len(family_jobs)
        row_ids_by_family[family] = {str(job.get("row_id")) for job in family_jobs if job.get("row_id")}
        family_packet_ids = sorted({str(job.get("packet_id")) for job in family_jobs if job.get("packet_id")})
        if len(family_packet_ids) != 1:
            missing_packets.append(family)
            template_row_ids_by_family[family] = set()
            continue
        template = templates_by_packet.get(family_packet_ids[0])
        if not isinstance(template, dict):
            missing_packets.append(family)
            template_row_ids_by_family[family] = set()
            continue
        template_row_ids_by_family[family] = {
            str(row.get("row_id"))
            for row in template.get("raw_counts_by_row", [])
            if isinstance(row, dict) and row.get("row_id")
        }
    missing_families = sorted(set(required_families) - set(families))
    extra_families = sorted(set(families) - set(required_families))
    row_count_values = {row_counts_by_family.get(family, 0) for family in required_families}
    row_set_values = {tuple(sorted(row_ids_by_family.get(family, set()))) for family in required_families}
    template_mismatches = [
        family
        for family in required_families
        if row_ids_by_family.get(family, set()) != template_row_ids_by_family.get(family, set())
    ]
    blockers = []
    if missing_families:
        blockers.append("missing_encoding_families")
    if extra_families:
        blockers.append("extra_encoding_families")
    if missing_packets:
        blockers.append("stage104_packet_template_missing")
    if len(row_count_values) != 1 or 0 in row_count_values:
        blockers.append("locked_row_counts_not_equal_across_families")
    if len(row_set_values) != 1 or () in row_set_values:
        blockers.append("locked_row_sets_not_equal_across_families")
    if template_mismatches:
        blockers.append("locked_rows_do_not_match_stage104_template_rows")
    return {
        "provider": provider,
        "source_lane_id": source_lane_id,
        "circuit_template": circuit_template,
        "required_encoding_families": required_families,
        "observed_encoding_families": families,
        "missing_encoding_families": missing_families,
        "extra_encoding_families": extra_families,
        "packet_ids": packet_ids,
        "locked_row_counts_by_family": row_counts_by_family,
        "locked_row_count": next(iter(row_count_values)) if len(row_count_values) == 1 else None,
        "stage104_template_mismatch_families": sorted(set(template_mismatches)),
        "ready": not blockers,
        "blockers": sorted(set(blockers)),
    }


def run_stage174_locked_interpretation_surface_audit(
    *,
    stage104_results_path: Path = DEFAULT_STAGE104_RESULTS,
    stage163_results_path: Path = DEFAULT_STAGE163_RESULTS,
    stage169_results_path: Path = DEFAULT_STAGE169_RESULTS,
    stage173_results_path: Path = DEFAULT_STAGE173_RESULTS,
) -> dict[str, Any]:
    stage104 = _load_json(stage104_results_path)
    stage163 = _load_json(stage163_results_path)
    stage169 = _load_json(stage169_results_path)
    stage173 = _load_json(stage173_results_path)
    sources = [
        (stage104_results_path, stage104),
        (stage163_results_path, stage163),
        (stage169_results_path, stage169),
        (stage173_results_path, stage173),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    required_families = list(stage104.get("required_encoding_families", [])) if isinstance(stage104, dict) else []
    stable_lanes = set(stage169.get("stable_target_lanes", [])) if isinstance(stage169, dict) else set()
    templates_by_packet = _stage104_templates(stage104)
    jobs = _locked_jobs(stage163)
    stage104_groups = [
        group
        for group in (stage104.get("matched_group_records", []) if isinstance(stage104, dict) else [])
        if isinstance(group, dict) and group.get("provider") == "ibm_runtime" and group.get("source_lane_id") in stable_lanes
    ]
    group_records = [
        _group_record(
            provider=str(group.get("provider")),
            source_lane_id=str(group.get("source_lane_id")),
            circuit_template=str(group.get("circuit_template")),
            jobs=jobs,
            templates_by_packet=templates_by_packet,
            required_families=required_families,
        )
        for group in sorted(stage104_groups, key=lambda item: (str(item.get("source_lane_id")), str(item.get("circuit_template"))))
    ]
    calibration_jobs = [job for job in jobs if job.get("job_kind") == "known_state_calibration" and job.get("provider") == "ibm_runtime"]
    window_ids = sorted({str(job.get("window_id")) for job in jobs if job.get("provider") == "ibm_runtime"})
    calibration_count_by_window = {
        window_id: sum(1 for job in calibration_jobs if job.get("window_id") == window_id)
        for window_id in window_ids
    }
    blockers: list[str] = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    if isinstance(stage104, dict) and stage104.get("decision") != STAGE104_READY:
        blockers.append("stage104_not_ready")
    if isinstance(stage163, dict) and stage163.get("decision") != STAGE163_READY:
        blockers.append("stage163_not_ready")
    if isinstance(stage169, dict) and stage169.get("decision") != STAGE169_READY:
        blockers.append("stage169_not_ready")
    if isinstance(stage173, dict) and stage173.get("decision") != STAGE173_READY:
        blockers.append("stage173_not_ready")
    if not required_families:
        blockers.append("required_encoding_families_missing")
    if not stable_lanes:
        blockers.append("stable_lanes_missing")
    if len(group_records) != len(stable_lanes):
        blockers.append("stable_lane_group_count_mismatch")
    if any(not record["ready"] for record in group_records):
        blockers.append("locked_interpretation_groups_not_ready")
    if any(count != 4 for count in calibration_count_by_window.values()) or not calibration_count_by_window:
        blockers.append("locked_calibration_jobs_not_ready")
    matched_job_count = sum(
        1
        for job in jobs
        if job.get("job_kind") == "matched_packet_row"
        and job.get("provider") == "ibm_runtime"
        and job.get("source_lane_id") in stable_lanes
    )
    decision = (
        "LOCKED_INTERPRETATION_SURFACE_AUDIT_INCOMPLETE"
        if missing_sources
        else "LOCKED_INTERPRETATION_SURFACE_READY_AWAITING_PROVIDER_RESULTS"
        if not blockers
        else "LOCKED_INTERPRETATION_SURFACE_AUDIT_BLOCKED"
    )
    return {
        "schema_version": STAGE174_SCHEMA_VERSION,
        "stage": "stage174_locked_interpretation_surface_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage104_decision": stage104.get("decision") if isinstance(stage104, dict) else None,
        "stage163_decision": stage163.get("decision") if isinstance(stage163, dict) else None,
        "stage169_decision": stage169.get("decision") if isinstance(stage169, dict) else None,
        "stage173_decision": stage173.get("decision") if isinstance(stage173, dict) else None,
        "stable_target_lanes": sorted(stable_lanes),
        "required_encoding_families": required_families,
        "window_ids": window_ids,
        "calibration_count_by_window": calibration_count_by_window,
        "group_count": len(group_records),
        "ready_group_count": sum(1 for record in group_records if record["ready"]),
        "matched_packet_job_count": matched_job_count,
        "group_records": group_records,
        "blockers": sorted(set(blockers)),
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "claim_boundary": {
            "supported": [
                "no-submit verification that locked IBM packet-row jobs cover the Stage169 stable lanes",
                "no-submit verification that each stable lane has the full Stage104 fixed-width comparator family set",
                "no-submit verification that locked row ids match the corresponding Stage104 template rows",
                "no-submit verification that known-state calibration jobs are present in each locked IBM window",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "provider result records",
                "Stage103 robustness metric interpretation",
                "Stage137 auditability metric interpretation",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "After exact approval and provider execution, the locked result files should populate this verified "
            "interpretation surface before Stage164/115/113/103/137/148/138 are rerun."
        ),
    }


def write_stage174_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stable_target_lanes": result["stable_target_lanes"],
        "required_encoding_families": result["required_encoding_families"],
        "group_count": result["group_count"],
        "ready_group_count": result["ready_group_count"],
        "matched_packet_job_count": result["matched_packet_job_count"],
        "calibration_count_by_window": result["calibration_count_by_window"],
        "blockers": result["blockers"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "secret_values_recorded": result["secret_values_recorded"],
        "runnable_commands_recorded": result["runnable_commands_recorded"],
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
            fieldnames=("provider", "source_lane_id", "circuit_template", "ready", "locked_row_count", "observed_encoding_families", "blockers"),
        )
        writer.writeheader()
        for record in result["group_records"]:
            writer.writerow(
                {
                    "provider": record["provider"],
                    "source_lane_id": record["source_lane_id"],
                    "circuit_template": record["circuit_template"],
                    "ready": record["ready"],
                    "locked_row_count": record["locked_row_count"],
                    "observed_encoding_families": "; ".join(record["observed_encoding_families"]),
                    "blockers": "; ".join(record["blockers"]),
                }
            )
    return paths


def print_stage174_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"ready_group_count: {result['ready_group_count']}/{result['group_count']}")
    print(f"matched_packet_job_count: {result['matched_packet_job_count']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
