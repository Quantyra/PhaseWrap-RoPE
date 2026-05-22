from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from qrope.stage103_robustness_metric_preregistration import expectation_from_counts


STAGE137_SCHEMA_VERSION = "qrope_stage137_auditability_metric_evaluator_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE107_WINDOW_PLANS = DEFAULT_ARTIFACT_ROOT / "stage107_window_execution_orchestrator" / "window_execution_plans.json"
DEFAULT_STAGE136_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage136_auditability_metric_preregistration" / "results.json"
DEFAULT_STAGE113_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage113_job_result_evidence_assembler" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage137_auditability_metric_evaluator"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
POSITIONAL_COMPARATOR_FAMILIES: tuple[str, ...] = ("rope_like", "sinusoidal_like", "alibi_like")
REQUIRED_EXECUTION_FIELDS: tuple[str, ...] = (
    "job_or_task_ids",
    "backend_metadata",
    "submitted_at_utc",
    "completed_at_utc",
    "raw_counts_by_row",
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


def _stage101_ready(path: Path) -> bool:
    payload = _load_json(path)
    return bool(
        isinstance(payload, dict)
        and payload.get("known_state_calibration_pass") is True
        and payload.get("decision") == "KNOWN_STATE_CALIBRATION_VERIFIED_READY_FOR_MATCHED_HARDWARE_EXECUTION"
    )


def _assembled_from_stage113(execution: dict[str, Any]) -> bool:
    return execution.get("status") == "assembled_from_stage113_results" and execution.get("no_hardware_submission") is False


def _components_from_counts(counts: dict[str, int], circuit_template: str) -> tuple[float, float]:
    component_a = expectation_from_counts(counts, "z0")
    if circuit_template == "two_ry_product_state_z_readout_v1":
        component_b = expectation_from_counts(counts, "z1")
    elif circuit_template == "two_ry_cx_parity_z_readout_v1":
        component_b = expectation_from_counts(counts, "z0z1")
    else:
        raise ValueError(f"unsupported circuit template: {circuit_template}")
    return component_a, component_b


def _counts_by_row(execution: dict[str, Any]) -> dict[str, dict[str, int]]:
    return {
        str(row.get("row_id")): {str(key): int(value) for key, value in row.get("counts", {}).items()}
        for row in execution.get("raw_counts_by_row", [])
        if isinstance(row, dict) and row.get("row_id") is not None
    }


def _packet_template_metrics(packet_template: dict[str, Any], execution_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    packet_id = str(packet_template["packet_id"])
    packet_path = Path(str(packet_template["template_path"]))
    execution_path = execution_dir / f"{packet_id}.json"
    packet = _load_json(packet_path)
    execution = _load_json(execution_path)
    missing: list[str] = []
    row_records: list[dict[str, Any]] = []
    if not isinstance(packet, dict):
        missing.append("packet_template_json")
        packet = {}
    execution_present = isinstance(execution, dict)
    if not execution_present:
        missing.append("packet_execution_json")
        execution = {}
    elif not _assembled_from_stage113(execution):
        missing.append("stage113_assembled_status")
    if execution_present:
        for field in REQUIRED_EXECUTION_FIELDS:
            if field not in execution or execution.get(field) in (None, "", []):
                missing.append(field)
    circuit_template = str(packet_template.get("circuit_template") or packet.get("fixed_width", {}).get("circuit_template"))
    counts_by_row = _counts_by_row(execution)
    errors: list[float] = []
    for row in packet.get("rows", []):
        row_id = str(row.get("row_id"))
        counts = counts_by_row.get(row_id)
        row_missing = []
        if not counts:
            row_missing.append("counts")
        target = row.get("components", {})
        if "component_a" not in target or "component_b" not in target:
            row_missing.append("target_components")
        observed_a = observed_b = None
        component_mae = None
        if not row_missing:
            observed_a, observed_b = _components_from_counts(counts, circuit_template)
            component_errors = [abs(observed_a - float(target["component_a"])), abs(observed_b - float(target["component_b"]))]
            component_mae = sum(component_errors) / len(component_errors)
            errors.append(component_mae)
        row_records.append(
            {
                "packet_id": packet_id,
                "row_id": row_id,
                "encoding_family": packet_template.get("encoding_family"),
                "source_lane_id": packet_template.get("source_lane_id"),
                "circuit_template": circuit_template,
                "observed_component_a": round(observed_a, 12) if observed_a is not None else None,
                "observed_component_b": round(observed_b, 12) if observed_b is not None else None,
                "target_component_a": target.get("component_a"),
                "target_component_b": target.get("component_b"),
                "component_reconstruction_absolute_error": round(component_mae, 12) if component_mae is not None else None,
                "ready": not row_missing,
                "missing_evidence": row_missing,
            }
        )
    row_count = int(packet_template.get("row_count") or len(packet.get("rows", [])))
    ready_row_count = sum(1 for record in row_records if record["ready"])
    if ready_row_count != row_count:
        missing.append("row_counts_or_targets_missing")
    return (
        {
            "packet_id": packet_id,
            "encoding_family": packet_template.get("encoding_family"),
            "source_lane_id": packet_template.get("source_lane_id"),
            "circuit_template": circuit_template,
            "packet_template_path": str(packet_path.as_posix()),
            "execution_path": str(execution_path.as_posix()),
            "row_count": row_count,
            "ready_row_count": ready_row_count,
            "component_reconstruction_mean_absolute_error": round(sum(errors) / len(errors), 12) if errors else None,
            "ready": not missing,
            "missing_evidence": sorted(set(missing)),
        },
        row_records,
    )


def _comparison_summary(packet_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str], dict[str, dict[str, Any]]] = {}
    for record in packet_records:
        key = (
            str(record.get("window_id")),
            str(record.get("provider")),
            str(record["source_lane_id"]),
            str(record["circuit_template"]),
        )
        grouped.setdefault(key, {})[str(record["encoding_family"])] = record
    summaries = []
    for (window_id, provider, source_lane_id, circuit_template), by_family in sorted(grouped.items()):
        phasewrap = by_family.get("phasewrap")
        phasewrap_mae = phasewrap.get("component_reconstruction_mean_absolute_error") if phasewrap else None
        lower_than = []
        for family in POSITIONAL_COMPARATOR_FAMILIES:
            comparator = by_family.get(family)
            comparator_mae = comparator.get("component_reconstruction_mean_absolute_error") if comparator else None
            if phasewrap_mae is not None and comparator_mae is not None and phasewrap_mae < comparator_mae:
                lower_than.append(family)
        summaries.append(
            {
                "window_id": window_id,
                "provider": provider,
                "source_lane_id": source_lane_id,
                "circuit_template": circuit_template,
                "phasewrap_component_reconstruction_mae": phasewrap_mae,
                "phasewrap_lower_error_than": lower_than,
                "phasewrap_present": phasewrap is not None,
                "all_positional_comparators_present": all(family in by_family for family in POSITIONAL_COMPARATOR_FAMILIES),
                "passes_auditability_advantage_rule": all(family in lower_than for family in POSITIONAL_COMPARATOR_FAMILIES),
            }
        )
    return summaries


def _comparison_groups_complete(comparison_summary: list[dict[str, Any]]) -> bool:
    return bool(comparison_summary) and all(
        record.get("phasewrap_present") is True
        and record.get("all_positional_comparators_present") is True
        and record.get("phasewrap_component_reconstruction_mae") is not None
        for record in comparison_summary
    )


def _stage113_live_submit_provenance_ready(stage113: dict[str, Any] | None) -> bool:
    if not isinstance(stage113, dict):
        return False
    runner_count = int(stage113.get("stage115_stage152_first_provider_runner_command_count") or 0)
    authorized_count = int(stage113.get("stage115_stage152_first_provider_authorized_runner_count") or 0)
    live_submit_ready_count = int(stage113.get("stage115_stage152_first_provider_live_submit_ready_count") or 0)
    return bool(
        stage113.get("decision") == "JOB_RESULTS_ASSEMBLED_INTO_STAGE109_EVIDENCE"
        and stage113.get("stage115_write_ready") is True
        and not stage113.get("stage115_write_blockers")
        and stage113.get("stage115_stage152_all_first_provider_commands_authorized") is True
        and stage113.get("stage115_stage152_all_first_provider_commands_live_submit_ready") is True
        and runner_count > 0
        and authorized_count == runner_count
        and live_submit_ready_count == runner_count
    )


def _window_record(plan: dict[str, Any], stage136_ready: bool, stage113_live_submit_ready: bool) -> dict[str, Any]:
    calibration_step = _step(plan, "known_state_calibration_execution")
    packet_step = _step(plan, "matched_packet_execution")
    calibration_execution_path = Path(str(calibration_step.get("output_path", "")))
    stage101_results_path = calibration_execution_path.parent / "stage101" / "results.json"
    execution_dir = Path(str(packet_step.get("output_dir", "")))
    packet_records = []
    row_records = []
    for packet_template in packet_step.get("packet_templates", []):
        packet_record, rows = _packet_template_metrics(packet_template, execution_dir)
        packet_record["provider"] = plan.get("provider")
        packet_record["window_id"] = plan.get("window_id")
        packet_records.append(packet_record)
        row_records.extend({**row, "provider": plan.get("provider"), "window_id": plan.get("window_id")} for row in rows)
    missing: list[str] = []
    if not stage136_ready:
        missing.append("stage136_auditability_contract_not_ready")
    if not stage113_live_submit_ready:
        missing.append("stage113_live_submit_provenance_not_ready")
    if not _stage101_ready(stage101_results_path):
        missing.append("stage101_calibration_not_verified")
    if any(not record["ready"] for record in packet_records):
        missing.append("packet_execution_counts_missing")
    comparison_summary = _comparison_summary(packet_records)
    if not _comparison_groups_complete(comparison_summary):
        missing.append("auditability_comparison_groups_incomplete")
    ready = bool(packet_records) and not missing
    return {
        "window_id": plan.get("window_id"),
        "provider": plan.get("provider"),
        "stage101_results_path": str(stage101_results_path.as_posix()),
        "packet_execution_dir": str(execution_dir.as_posix()),
        "packet_count": len(packet_records),
        "ready_packet_count": sum(1 for record in packet_records if record["ready"]),
        "ready": ready,
        "missing_evidence": sorted(set(missing)),
        "packet_records": packet_records,
        "row_records": row_records,
        "comparison_summary": comparison_summary if ready else [],
    }


def run_stage137_evaluator(
    *,
    stage107_window_plans_path: Path = DEFAULT_STAGE107_WINDOW_PLANS,
    stage136_results_path: Path = DEFAULT_STAGE136_RESULTS,
    stage113_results_path: Path = DEFAULT_STAGE113_RESULTS,
    provider: str | None = None,
) -> dict[str, Any]:
    plans = _load_json(stage107_window_plans_path)
    stage136 = _load_json(stage136_results_path)
    stage113 = _load_json(stage113_results_path)
    sources = [(stage107_window_plans_path, plans), (stage136_results_path, stage136), (stage113_results_path, stage113)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    all_window_plans = plans if isinstance(plans, list) else []
    window_plans = [
        plan for plan in all_window_plans if provider is None or plan.get("provider") == provider
    ]
    stage136_ready = bool(
        isinstance(stage136, dict) and stage136.get("decision") == "AUDITABILITY_METRIC_CONTRACT_READY_HARDWARE_COUNTS_REQUIRED"
    )
    stage113_live_submit_ready = _stage113_live_submit_provenance_ready(stage113)
    window_records = [_window_record(plan, stage136_ready, stage113_live_submit_ready) for plan in window_plans]
    ready_window_count = sum(1 for record in window_records if record["ready"])
    comparison_summary = [item for window in window_records for item in window["comparison_summary"]]
    ready = bool(window_records) and ready_window_count == len(window_records) and stage136_ready and not missing_sources
    return {
        "schema_version": STAGE137_SCHEMA_VERSION,
        "stage": "stage137_auditability_metric_evaluator",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "AUDITABILITY_METRICS_READY_FOR_CLAIM_GATE"
            if ready
            else "AUDITABILITY_METRICS_BLOCKED_HARDWARE_COUNTS_REQUIRED"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "provider_scope": provider or "all",
        "stage136_decision": stage136.get("decision") if isinstance(stage136, dict) else None,
        "stage136_ready": stage136_ready,
        "stage113_results_path": str(stage113_results_path.as_posix()),
        "stage113_decision": stage113.get("decision") if isinstance(stage113, dict) else None,
        "stage113_stage115_write_ready": stage113.get("stage115_write_ready") if isinstance(stage113, dict) else None,
        "stage113_stage115_write_blockers": stage113.get("stage115_write_blockers") if isinstance(stage113, dict) else None,
        "stage113_stage115_stage152_first_provider_runner_command_count": (
            stage113.get("stage115_stage152_first_provider_runner_command_count") if isinstance(stage113, dict) else None
        ),
        "stage113_stage115_stage152_first_provider_authorized_runner_count": (
            stage113.get("stage115_stage152_first_provider_authorized_runner_count") if isinstance(stage113, dict) else None
        ),
        "stage113_stage115_stage152_first_provider_live_submit_ready_count": (
            stage113.get("stage115_stage152_first_provider_live_submit_ready_count") if isinstance(stage113, dict) else None
        ),
        "stage113_stage115_stage152_all_first_provider_commands_authorized": (
            stage113.get("stage115_stage152_all_first_provider_commands_authorized") if isinstance(stage113, dict) else None
        ),
        "stage113_stage115_stage152_all_first_provider_commands_live_submit_ready": (
            stage113.get("stage115_stage152_all_first_provider_commands_live_submit_ready") if isinstance(stage113, dict) else None
        ),
        "stage113_live_submit_provenance_ready": stage113_live_submit_ready,
        "window_count": len(window_records),
        "available_window_count": len(all_window_plans),
        "ready_window_count": ready_window_count,
        "comparison_summary_count": len(comparison_summary),
        "auditability_advantage_count": sum(1 for record in comparison_summary if record["passes_auditability_advantage_rule"]),
        "window_records": window_records,
        "comparison_summary": comparison_summary,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "a deterministic evaluator for component reconstruction auditability metrics",
                "optional provider-scoped auditability evaluation for first-provider replicated-window evidence",
                "binding of auditability evaluation to Stage 107 packet execution counts and Stage 101 calibration results",
                "verification that packet executions preserve Stage 113 hardware-result lineage metadata",
                "verification that Stage 113 preserves Stage 115/152 all-command live-submit readiness provenance",
                "verification that PhaseWrap and every named positional comparator are present before claim-gate readiness",
                "a blocked outcome when real provider packet counts are missing",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "new provider result records",
                "a current auditability advantage claim unless this gate is ready and the advantage rule passes",
                "a robustness advantage claim",
            ],
        },
        "next_gate": (
            "Populate selected Stage 107 packet execution counts via Stage 113 assembly and pass per-window Stage 101 calibration, "
            "then rerun this evaluator before any auditability advantage wording."
        ),
    }


def write_stage137_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "stage136_decision": result["stage136_decision"],
        "stage136_ready": result["stage136_ready"],
        "stage113_results_path": result["stage113_results_path"],
        "stage113_decision": result["stage113_decision"],
        "stage113_stage115_write_ready": result["stage113_stage115_write_ready"],
        "stage113_stage115_write_blockers": result["stage113_stage115_write_blockers"],
        "stage113_stage115_stage152_first_provider_runner_command_count": result[
            "stage113_stage115_stage152_first_provider_runner_command_count"
        ],
        "stage113_stage115_stage152_first_provider_authorized_runner_count": result[
            "stage113_stage115_stage152_first_provider_authorized_runner_count"
        ],
        "stage113_stage115_stage152_first_provider_live_submit_ready_count": result[
            "stage113_stage115_stage152_first_provider_live_submit_ready_count"
        ],
        "stage113_stage115_stage152_all_first_provider_commands_authorized": result[
            "stage113_stage115_stage152_all_first_provider_commands_authorized"
        ],
        "stage113_stage115_stage152_all_first_provider_commands_live_submit_ready": result[
            "stage113_stage115_stage152_all_first_provider_commands_live_submit_ready"
        ],
        "stage113_live_submit_provenance_ready": result["stage113_live_submit_provenance_ready"],
        "window_count": result["window_count"],
        "available_window_count": result["available_window_count"],
        "ready_window_count": result["ready_window_count"],
        "comparison_summary_count": result["comparison_summary_count"],
        "auditability_advantage_count": result["auditability_advantage_count"],
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
                "window_id",
                "provider",
                "packet_count",
                "ready_packet_count",
                "ready",
                "missing_evidence",
            ),
        )
        writer.writeheader()
        for record in result["window_records"]:
            writer.writerow(
                {
                    "window_id": record["window_id"],
                    "provider": record["provider"],
                    "packet_count": record["packet_count"],
                    "ready_packet_count": record["ready_packet_count"],
                    "ready": record["ready"],
                    "missing_evidence": "; ".join(record["missing_evidence"]),
                }
            )
    return paths


def print_stage137_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"provider_scope: {result['provider_scope']}")
    print(f"ready_window_count: {result['ready_window_count']}/{result['window_count']}")
    print(f"comparison_summary_count: {result['comparison_summary_count']}")
    print(f"auditability_advantage_count: {result['auditability_advantage_count']}")
    print(f"next_gate: {result['next_gate']}")
