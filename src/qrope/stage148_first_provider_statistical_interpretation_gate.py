from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE148_SCHEMA_VERSION = "qrope_stage148_first_provider_statistical_interpretation_gate_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE107_WINDOW_PLANS = DEFAULT_ARTIFACT_ROOT / "stage107_window_execution_orchestrator" / "window_execution_plans.json"
DEFAULT_STAGE146_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage146_first_provider_shot_uncertainty_audit" / "results.json"
DEFAULT_STAGE147_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage147_first_provider_calibration_confidence_audit" / "results.json"
DEFAULT_STAGE113_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage113_job_result_evidence_assembler" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage148_first_provider_statistical_interpretation_gate"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
REQUIRED_CALIBRATION_FIELDS: tuple[str, ...] = (
    "job_or_task_ids",
    "backend_metadata",
    "submitted_at_utc",
    "completed_at_utc",
    "raw_counts_by_state",
)
STAGE146_READY = "FIRST_PROVIDER_SHOT_UNCERTAINTY_CONTRACT_READY_HARDWARE_COUNTS_REQUIRED"
STAGE147_READY = "FIRST_PROVIDER_CALIBRATION_CONFIDENCE_CONTRACT_READY_COUNTS_REQUIRED"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _step(plan: dict[str, Any], step_id: str) -> dict[str, Any]:
    for item in plan.get("steps", []):
        if item.get("step_id") == step_id:
            return item
    return {}


def _dominant_count(counts: dict[str, Any], expected_key: str) -> int:
    return int(counts.get(expected_key, 0)) if isinstance(counts, dict) else 0


def _state_thresholds(stage147: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not isinstance(stage147, dict):
        return {}
    return {str(record.get("state")): record for record in stage147.get("state_records", [])}


def _lane_thresholds(stage146: dict[str, Any] | None) -> dict[tuple[str, str, str, str], dict[str, Any]]:
    if not isinstance(stage146, dict):
        return {}
    return {
        (
            str(record.get("provider")),
            str(record.get("window_id")),
            str(record.get("source_lane_id")),
            str(record.get("circuit_template")),
        ): record
        for record in stage146.get("lane_summaries", [])
    }


def _assembled_from_stage113(execution: dict[str, Any]) -> bool:
    return execution.get("status") == "assembled_from_stage113_results" and execution.get("no_hardware_submission") is False


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


def _calibration_record(plan: dict[str, Any], thresholds: dict[str, dict[str, Any]]) -> dict[str, Any]:
    calibration_step = _step(plan, "known_state_calibration_execution")
    calibration_path = Path(str(calibration_step.get("output_path", "")))
    stage101_path = calibration_path.parent / "stage101" / "results.json"
    calibration = _load_json(calibration_path)
    stage101 = _load_json(stage101_path)
    state_records = []
    missing = []
    if not isinstance(calibration, dict):
        missing.append("calibration_execution_json")
    elif not _assembled_from_stage113(calibration):
        missing.append("stage113_assembled_calibration_status")
    if isinstance(calibration, dict):
        for field in REQUIRED_CALIBRATION_FIELDS:
            if field not in calibration or calibration.get(field) in (None, "", []):
                missing.append(field)
    if not (
        isinstance(stage101, dict)
        and stage101.get("decision") == "KNOWN_STATE_CALIBRATION_VERIFIED_READY_FOR_MATCHED_HARDWARE_EXECUTION"
        and stage101.get("known_state_calibration_pass") is True
    ):
        missing.append("stage101_calibration_pass")
    rows = calibration.get("raw_counts_by_state", []) if isinstance(calibration, dict) else []
    rows_by_state = {str(row.get("state")): row for row in rows if isinstance(row, dict)}
    for state, threshold in thresholds.items():
        row = rows_by_state.get(state, {})
        expected_key = str(threshold.get("expected_dominant_key"))
        count = _dominant_count(row.get("counts", {}), expected_key)
        required = int(threshold.get("minimum_wilson95_dominant_count") or 0)
        state_records.append(
            {
                "state": state,
                "expected_dominant_key": expected_key,
                "observed_dominant_count": count,
                "minimum_wilson95_dominant_count": required,
                "passes_confidence_threshold": count >= required and required > 0,
            }
        )
    if any(not record["passes_confidence_threshold"] for record in state_records):
        missing.append("stage147_wilson95_thresholds")
    return {
        "provider": plan.get("provider"),
        "window_id": plan.get("window_id"),
        "calibration_execution_path": str(calibration_path.as_posix()),
        "stage101_results_path": str(stage101_path.as_posix()),
        "state_count": len(state_records),
        "passing_state_count": sum(1 for record in state_records if record["passes_confidence_threshold"]),
        "state_records": state_records,
        "ready": not missing and bool(state_records),
        "missing_evidence": sorted(set(missing)),
    }


def _stage103_records(plan: dict[str, Any], thresholds: dict[tuple[str, str, str, str], dict[str, Any]]) -> list[dict[str, Any]]:
    packet_step = _step(plan, "matched_packet_execution")
    stage103_path = Path(str(packet_step.get("output_dir", ""))).parent / "stage103" / "results.json"
    stage103 = _load_json(stage103_path)
    stage103_ready = bool(
        isinstance(stage103, dict)
        and stage103.get("decision") == "ROBUSTNESS_METRICS_READY_FOR_INTERPRETATION"
        and stage103.get("ready_to_interpret_hardware_metrics") is True
        and stage103.get("comparison_groups_complete") is True
        and stage103.get("stage104_matched_surface_ready") is True
        and stage103.get("stage113_live_submit_provenance_ready") is True
        and int(stage103.get("missing_execution_count") or 0) == 0
        and int(stage103.get("metric_record_count") or 0) > 0
    )
    records = []
    for summary in stage103.get("comparison_summary", []) if isinstance(stage103, dict) else []:
        summary_provider = summary.get("provider")
        provider_matches = summary_provider is None or summary_provider == plan.get("provider")
        key = (
            str(plan.get("provider")),
            str(plan.get("window_id")),
            str(summary.get("source_lane_id")),
            str(summary.get("circuit_template")),
        )
        threshold = thresholds.get(key, {})
        phasewrap = summary.get("phasewrap_mean_absolute_score_error")
        comparator = summary.get("best_comparator_mean_absolute_score_error")
        margin = None
        if phasewrap is not None and comparator is not None:
            margin = float(comparator) - float(phasewrap)
        required = threshold.get("minimum_phasewrap_mae_margin_for_95pct_shot_noise_separation")
        shot_separated = margin is not None and required is not None and margin > float(required)
        records.append(
            {
                "provider": plan.get("provider"),
                "window_id": plan.get("window_id"),
                "stage103_summary_provider": summary_provider,
                "stage103_summary_provider_matches_window": provider_matches,
                "source_lane_id": summary.get("source_lane_id"),
                "circuit_template": summary.get("circuit_template"),
                "phasewrap_mean_absolute_score_error": phasewrap,
                "best_comparator_mean_absolute_score_error": comparator,
                "phasewrap_mae_margin": round(margin, 12) if margin is not None else None,
                "minimum_shot_noise_separation_margin": required,
                "passes_stage103_lower_mae_rule": bool(
                    stage103_ready
                    and provider_matches
                    and summary.get("all_families_present") is True
                    and summary.get("phasewrap_lower_error_than")
                    and len(summary.get("phasewrap_lower_error_than", [])) >= 4
                ),
                "passes_stage146_shot_noise_separation": shot_separated,
                "stage103_ready_for_interpretation": stage103_ready,
                "stage103_ready_to_interpret_hardware_metrics": (
                    stage103.get("ready_to_interpret_hardware_metrics") if isinstance(stage103, dict) else None
                ),
                "stage103_comparison_groups_complete": stage103.get("comparison_groups_complete") if isinstance(stage103, dict) else None,
                "stage103_stage104_matched_surface_ready": (
                    stage103.get("stage104_matched_surface_ready") if isinstance(stage103, dict) else None
                ),
                "stage103_stage104_complete_matched_group_count": (
                    stage103.get("stage104_complete_matched_group_count") if isinstance(stage103, dict) else None
                ),
                "stage103_stage113_live_submit_provenance_ready": (
                    stage103.get("stage113_live_submit_provenance_ready") if isinstance(stage103, dict) else None
                ),
                "stage103_missing_execution_count": stage103.get("missing_execution_count") if isinstance(stage103, dict) else None,
                "stage103_metric_record_count": stage103.get("metric_record_count") if isinstance(stage103, dict) else None,
                "stage103_results_path": str(stage103_path.as_posix()),
            }
        )
    if not records:
        for key, threshold in thresholds.items():
            provider, window_id, source_lane_id, circuit_template = key
            if provider == str(plan.get("provider")) and window_id == str(plan.get("window_id")):
                records.append(
                    {
                        "provider": provider,
                        "window_id": window_id,
                        "stage103_summary_provider": None,
                        "stage103_summary_provider_matches_window": None,
                        "source_lane_id": source_lane_id,
                        "circuit_template": circuit_template,
                        "phasewrap_mean_absolute_score_error": None,
                        "best_comparator_mean_absolute_score_error": None,
                        "phasewrap_mae_margin": None,
                        "minimum_shot_noise_separation_margin": threshold.get(
                            "minimum_phasewrap_mae_margin_for_95pct_shot_noise_separation"
                        ),
                        "passes_stage103_lower_mae_rule": False,
                        "passes_stage146_shot_noise_separation": False,
                        "stage103_ready_for_interpretation": stage103_ready,
                        "stage103_ready_to_interpret_hardware_metrics": (
                            stage103.get("ready_to_interpret_hardware_metrics") if isinstance(stage103, dict) else None
                        ),
                        "stage103_comparison_groups_complete": stage103.get("comparison_groups_complete") if isinstance(stage103, dict) else None,
                        "stage103_stage104_matched_surface_ready": (
                            stage103.get("stage104_matched_surface_ready") if isinstance(stage103, dict) else None
                        ),
                        "stage103_stage104_complete_matched_group_count": (
                            stage103.get("stage104_complete_matched_group_count") if isinstance(stage103, dict) else None
                        ),
                        "stage103_stage113_live_submit_provenance_ready": (
                            stage103.get("stage113_live_submit_provenance_ready") if isinstance(stage103, dict) else None
                        ),
                        "stage103_missing_execution_count": stage103.get("missing_execution_count") if isinstance(stage103, dict) else None,
                        "stage103_metric_record_count": stage103.get("metric_record_count") if isinstance(stage103, dict) else None,
                        "stage103_results_path": str(stage103_path.as_posix()),
                    }
                )
    return records


def run_stage148_gate(
    *,
    stage107_window_plans_path: Path = DEFAULT_STAGE107_WINDOW_PLANS,
    stage146_results_path: Path = DEFAULT_STAGE146_RESULTS,
    stage147_results_path: Path = DEFAULT_STAGE147_RESULTS,
    stage113_results_path: Path = DEFAULT_STAGE113_RESULTS,
) -> dict[str, Any]:
    plans = _load_json(stage107_window_plans_path)
    stage146 = _load_json(stage146_results_path)
    stage147 = _load_json(stage147_results_path)
    stage113 = _load_json(stage113_results_path)
    sources = [
        (stage107_window_plans_path, plans),
        (stage146_results_path, stage146),
        (stage147_results_path, stage147),
        (stage113_results_path, stage113),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    provider = str(stage147.get("provider_scope", "")) if isinstance(stage147, dict) else ""
    stage146_ready = bool(isinstance(stage146, dict) and stage146.get("decision") == STAGE146_READY)
    stage147_ready = bool(isinstance(stage147, dict) and stage147.get("decision") == STAGE147_READY)
    window_plans = [
        plan for plan in plans or [] if isinstance(plan, dict) and (not provider or plan.get("provider") == provider)
    ] if isinstance(plans, list) else []
    calibration_records = [_calibration_record(plan, _state_thresholds(stage147)) for plan in window_plans]
    lane_records = [record for plan in window_plans for record in _stage103_records(plan, _lane_thresholds(stage146))]
    ready_calibration_count = sum(1 for record in calibration_records if record["ready"])
    lower_mae_count = sum(1 for record in lane_records if record["passes_stage103_lower_mae_rule"])
    shot_separated_count = sum(1 for record in lane_records if record["passes_stage146_shot_noise_separation"])
    stage113_live_submit_ready = _stage113_live_submit_provenance_ready(stage113)
    ready = (
        bool(provider)
        and stage146_ready
        and stage147_ready
        and stage113_live_submit_ready
        and bool(calibration_records)
        and bool(lane_records)
        and not missing_sources
        and ready_calibration_count == len(calibration_records)
        and lower_mae_count == len(lane_records)
        and shot_separated_count == len(lane_records)
    )
    return {
        "schema_version": STAGE148_SCHEMA_VERSION,
        "stage": "stage148_first_provider_statistical_interpretation_gate",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "FIRST_PROVIDER_STATISTICAL_INTERPRETATION_READY_FOR_CLAIM_GATES"
            if ready
            else "FIRST_PROVIDER_STATISTICAL_INTERPRETATION_BLOCKED_EVIDENCE_REQUIRED"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "provider_scope": provider,
        "stage146_decision": stage146.get("decision") if isinstance(stage146, dict) else None,
        "stage147_decision": stage147.get("decision") if isinstance(stage147, dict) else None,
        "stage146_ready": stage146_ready,
        "stage147_ready": stage147_ready,
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
        "window_count": len(window_plans),
        "calibration_record_count": len(calibration_records),
        "ready_calibration_record_count": ready_calibration_count,
        "lane_record_count": len(lane_records),
        "stage103_lower_mae_lane_count": lower_mae_count,
        "shot_noise_separated_lane_count": shot_separated_count,
        "calibration_records": calibration_records,
        "lane_records": lane_records,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "binding of later IBM interpretation to Stage 147 calibration-confidence thresholds",
                "binding of later IBM PhaseWrap MAE margins to Stage 146 shot-noise separation thresholds",
                "binding of final statistical interpretation to Stage 113-assembled calibration evidence with result lineage metadata",
                "binding of final statistical interpretation to Stage 113 preserved Stage 115/152 all-command live-submit readiness provenance",
                "binding of final statistical interpretation to Stage 103 ready decisions, Stage 104 matched-surface readiness, Stage 113 live-submit provenance, readiness counters, and complete comparison groups",
                "a blocked outcome until observed provider evidence satisfies both statistical guardrails",
            ],
            "excluded": [
                "provider credential values",
                "hardware job submission",
                "new provider result records",
                "readout mitigation or correction",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "After IBM Runtime evidence is assembled, rerun per-window Stage 101 and Stage 103, then rerun this gate "
            "before any Stage 110 or Stage 138 advantage wording."
        ),
    }


def write_stage148_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "stage146_decision": result["stage146_decision"],
        "stage147_decision": result["stage147_decision"],
        "stage146_ready": result["stage146_ready"],
        "stage147_ready": result["stage147_ready"],
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
        "calibration_record_count": result["calibration_record_count"],
        "ready_calibration_record_count": result["ready_calibration_record_count"],
        "lane_record_count": result["lane_record_count"],
        "stage103_lower_mae_lane_count": result["stage103_lower_mae_lane_count"],
        "shot_noise_separated_lane_count": result["shot_noise_separated_lane_count"],
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
                "provider",
                "window_id",
                "source_lane_id",
                "circuit_template",
                "phasewrap_mae_margin",
                "minimum_shot_noise_separation_margin",
                "passes_stage103_lower_mae_rule",
                "passes_stage146_shot_noise_separation",
            ),
        )
        writer.writeheader()
        for record in result["lane_records"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage148_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"provider_scope: {result['provider_scope']}")
    print(f"ready_calibration_record_count: {result['ready_calibration_record_count']}/{result['calibration_record_count']}")
    print(f"shot_noise_separated_lane_count: {result['shot_noise_separated_lane_count']}/{result['lane_record_count']}")
    print(f"next_gate: {result['next_gate']}")
