from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE138_SCHEMA_VERSION = "qrope_stage138_objective_claim_gate_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE110_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage110_replicated_advantage_claim_gate" / "results.json"
DEFAULT_STAGE137_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage137_auditability_metric_evaluator" / "results.json"
DEFAULT_STAGE148_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage148_first_provider_statistical_interpretation_gate" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage138_objective_claim_gate"
ROBUSTNESS_SUPPORTED = "PHASEWRAP_REPLICATED_ADVANTAGE_SUPPORTED_BY_STAGE105_RULE"
ROBUSTNESS_NOT_SUPPORTED = "PHASEWRAP_REPLICATED_ADVANTAGE_NOT_SUPPORTED_BY_STAGE105_RULE"
AUDITABILITY_READY = "AUDITABILITY_METRICS_READY_FOR_CLAIM_GATE"
STATISTICAL_READY = "FIRST_PROVIDER_STATISTICAL_INTERPRETATION_READY_FOR_CLAIM_GATES"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _auditability_replication_records(stage137: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not _stage137_ready_for_claim(stage137):
        return []
    provider_windows: dict[str, set[str]] = {}
    for window in stage137.get("window_records", []):
        if window.get("ready") is True:
            provider_windows.setdefault(str(window.get("provider")), set()).add(str(window.get("window_id")))

    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for record in stage137.get("comparison_summary", []):
        key = (str(record.get("provider")), str(record.get("source_lane_id")), str(record.get("circuit_template")))
        grouped.setdefault(key, []).append(record)

    out = []
    for (provider, source_lane_id, circuit_template), records in sorted(grouped.items()):
        required_windows = provider_windows.get(provider, set())
        observed_windows = {str(record.get("window_id")) for record in records if record.get("window_id") is not None}
        passing_windows = {
            str(record.get("window_id"))
            for record in records
            if record.get("window_id") is not None and record.get("passes_auditability_advantage_rule") is True
        }
        replicated = bool(required_windows) and required_windows <= observed_windows and required_windows <= passing_windows
        out.append(
            {
                "provider": provider,
                "source_lane_id": source_lane_id,
                "circuit_template": circuit_template,
                "required_window_count": len(required_windows),
                "observed_window_count": len(observed_windows),
                "passing_window_count": len(passing_windows),
                "required_windows": sorted(required_windows),
                "observed_windows": sorted(observed_windows),
                "passing_windows": sorted(passing_windows),
                "replicated_phasewrap_auditability_advantage": replicated,
            }
        )
    return out


def _stage110_terminal(stage110: dict[str, Any] | None) -> bool:
    return bool(
        isinstance(stage110, dict)
        and stage110.get("decision") in {ROBUSTNESS_SUPPORTED, ROBUSTNESS_NOT_SUPPORTED}
        and stage110.get("ready_for_stage105_aggregation") is True
        and stage110.get("stage109_ready_for_aggregation") is True
        and stage110.get("stage105_preregistered") is True
    )


def _stage137_ready_for_claim(stage137: dict[str, Any] | None) -> bool:
    return bool(
        isinstance(stage137, dict)
        and stage137.get("decision") == AUDITABILITY_READY
        and stage137.get("stage136_ready") is True
        and stage137.get("ready_window_count") == stage137.get("window_count")
        and int(stage137.get("window_count") or 0) > 0
    )


def _stage148_ready_for_claim(stage148: dict[str, Any] | None) -> bool:
    return bool(
        isinstance(stage148, dict)
        and stage148.get("decision") == STATISTICAL_READY
        and stage148.get("stage146_ready") is True
        and stage148.get("stage147_ready") is True
        and stage148.get("stage113_live_submit_provenance_ready") is True
        and stage148.get("stage113_stage115_stage152_all_first_provider_commands_authorized") is True
        and stage148.get("stage113_stage115_stage152_all_first_provider_commands_live_submit_ready") is True
        and stage148.get("ready_calibration_record_count") == stage148.get("calibration_record_count")
        and stage148.get("stage103_lower_mae_lane_count") == stage148.get("lane_record_count")
        and stage148.get("shot_noise_separated_lane_count") == stage148.get("lane_record_count")
        and int(stage148.get("calibration_record_count") or 0) > 0
        and int(stage148.get("lane_record_count") or 0) > 0
    )


def run_stage138_claim_gate(
    *,
    stage110_results_path: Path = DEFAULT_STAGE110_RESULTS,
    stage137_results_path: Path = DEFAULT_STAGE137_RESULTS,
    stage148_results_path: Path = DEFAULT_STAGE148_RESULTS,
) -> dict[str, Any]:
    stage110 = _load_json(stage110_results_path)
    stage137 = _load_json(stage137_results_path)
    stage148 = _load_json(stage148_results_path)
    sources = [(stage110_results_path, stage110), (stage137_results_path, stage137), (stage148_results_path, stage148)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    robustness_terminal = _stage110_terminal(stage110)
    robustness_supported = bool(robustness_terminal and isinstance(stage110, dict) and stage110.get("decision") == ROBUSTNESS_SUPPORTED)
    auditability_ready = _stage137_ready_for_claim(stage137)
    auditability_replication = _auditability_replication_records(stage137)
    auditability_supported = any(record["replicated_phasewrap_auditability_advantage"] for record in auditability_replication)
    statistical_ready = _stage148_ready_for_claim(stage148)
    statistical_required = bool(robustness_supported or auditability_supported)
    objective_terminal = robustness_terminal and auditability_ready and not missing_sources and (not statistical_required or statistical_ready)

    if missing_sources:
        decision = "OBJECTIVE_CLAIM_GATE_INCOMPLETE"
    elif not objective_terminal:
        decision = "OBJECTIVE_CLAIM_GATE_BLOCKED_EVIDENCE_INCOMPLETE"
    elif robustness_supported or auditability_supported:
        decision = "PHASEWRAP_NOISY_HARDWARE_OBJECTIVE_SUPPORTED"
    else:
        decision = "PHASEWRAP_NOISY_HARDWARE_OBJECTIVE_NOT_SUPPORTED"

    return {
        "schema_version": STAGE138_SCHEMA_VERSION,
        "stage": "stage138_objective_claim_gate",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage110_decision": stage110.get("decision") if isinstance(stage110, dict) else None,
        "stage137_decision": stage137.get("decision") if isinstance(stage137, dict) else None,
        "stage148_decision": stage148.get("decision") if isinstance(stage148, dict) else None,
        "stage148_stage146_ready": stage148.get("stage146_ready") if isinstance(stage148, dict) else None,
        "stage148_stage147_ready": stage148.get("stage147_ready") if isinstance(stage148, dict) else None,
        "stage148_stage113_live_submit_provenance_ready": stage148.get("stage113_live_submit_provenance_ready")
        if isinstance(stage148, dict)
        else None,
        "stage148_stage113_stage115_stage152_all_first_provider_commands_authorized": stage148.get(
            "stage113_stage115_stage152_all_first_provider_commands_authorized"
        )
        if isinstance(stage148, dict)
        else None,
        "stage148_stage113_stage115_stage152_all_first_provider_commands_live_submit_ready": stage148.get(
            "stage113_stage115_stage152_all_first_provider_commands_live_submit_ready"
        )
        if isinstance(stage148, dict)
        else None,
        "stage110_ready_for_stage105_aggregation": stage110.get("ready_for_stage105_aggregation") if isinstance(stage110, dict) else None,
        "stage137_ready_window_count": stage137.get("ready_window_count") if isinstance(stage137, dict) else None,
        "stage137_window_count": stage137.get("window_count") if isinstance(stage137, dict) else None,
        "stage148_ready_calibration_record_count": stage148.get("ready_calibration_record_count") if isinstance(stage148, dict) else None,
        "stage148_calibration_record_count": stage148.get("calibration_record_count") if isinstance(stage148, dict) else None,
        "stage148_stage103_lower_mae_lane_count": stage148.get("stage103_lower_mae_lane_count") if isinstance(stage148, dict) else None,
        "stage148_shot_noise_separated_lane_count": stage148.get("shot_noise_separated_lane_count") if isinstance(stage148, dict) else None,
        "stage148_lane_record_count": stage148.get("lane_record_count") if isinstance(stage148, dict) else None,
        "robustness_terminal": robustness_terminal,
        "robustness_supported": robustness_supported,
        "auditability_ready": auditability_ready,
        "statistical_interpretation_ready": statistical_ready,
        "statistical_interpretation_required": statistical_required,
        "auditability_replication_record_count": len(auditability_replication),
        "replicated_auditability_advantage_count": sum(
            1 for record in auditability_replication if record["replicated_phasewrap_auditability_advantage"]
        ),
        "objective_terminal": objective_terminal,
        "objective_supported": bool(objective_terminal and (robustness_supported or auditability_supported)),
        "auditability_replication_records": auditability_replication,
        "robustness_replication_records": stage110.get("replication_records", []) if isinstance(stage110, dict) else [],
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "a terminal objective-level gate for robustness or auditability outcomes",
                "separate preservation of the Stage 110 robustness rule and Stage 137 auditability rule with readiness flags checked",
                "Stage 148 statistical guardrail decision, Stage 113 live-submit provenance, and readiness-counter enforcement before supported advantage wording",
                "blocked output until both robustness and auditability evidence surfaces are terminal",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "new provider result records",
                "a noisy-hardware objective conclusion while Stage 110, Stage 137, or required Stage 148 statistical interpretation is blocked",
                "provider-wide or transformer-scale superiority beyond recorded matched fixed-width evidence",
            ],
        },
        "next_gate": (
            "Clear Stage 110, Stage 137, and Stage 148 when supported advantage wording is being considered. Only this "
            "gate should be used for the final objective wording."
        ),
    }


def write_stage138_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage110_decision": result["stage110_decision"],
        "stage137_decision": result["stage137_decision"],
        "stage148_decision": result["stage148_decision"],
        "stage148_stage146_ready": result["stage148_stage146_ready"],
        "stage148_stage147_ready": result["stage148_stage147_ready"],
        "stage148_stage113_live_submit_provenance_ready": result["stage148_stage113_live_submit_provenance_ready"],
        "stage148_stage113_stage115_stage152_all_first_provider_commands_authorized": result[
            "stage148_stage113_stage115_stage152_all_first_provider_commands_authorized"
        ],
        "stage148_stage113_stage115_stage152_all_first_provider_commands_live_submit_ready": result[
            "stage148_stage113_stage115_stage152_all_first_provider_commands_live_submit_ready"
        ],
        "stage110_ready_for_stage105_aggregation": result["stage110_ready_for_stage105_aggregation"],
        "stage137_ready_window_count": result["stage137_ready_window_count"],
        "stage137_window_count": result["stage137_window_count"],
        "stage148_ready_calibration_record_count": result["stage148_ready_calibration_record_count"],
        "stage148_calibration_record_count": result["stage148_calibration_record_count"],
        "stage148_stage103_lower_mae_lane_count": result["stage148_stage103_lower_mae_lane_count"],
        "stage148_shot_noise_separated_lane_count": result["stage148_shot_noise_separated_lane_count"],
        "stage148_lane_record_count": result["stage148_lane_record_count"],
        "robustness_terminal": result["robustness_terminal"],
        "robustness_supported": result["robustness_supported"],
        "auditability_ready": result["auditability_ready"],
        "statistical_interpretation_ready": result["statistical_interpretation_ready"],
        "statistical_interpretation_required": result["statistical_interpretation_required"],
        "auditability_replication_record_count": result["auditability_replication_record_count"],
        "replicated_auditability_advantage_count": result["replicated_auditability_advantage_count"],
        "objective_terminal": result["objective_terminal"],
        "objective_supported": result["objective_supported"],
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
                "source_lane_id",
                "circuit_template",
                "required_window_count",
                "observed_window_count",
                "passing_window_count",
                "replicated_phasewrap_auditability_advantage",
            ),
        )
        writer.writeheader()
        for record in result["auditability_replication_records"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage138_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"robustness_terminal: {result['robustness_terminal']}")
    print(f"auditability_ready: {result['auditability_ready']}")
    print(f"statistical_interpretation_ready: {result['statistical_interpretation_ready']}")
    print(f"objective_terminal: {result['objective_terminal']}")
    print(f"objective_supported: {result['objective_supported']}")
    print(f"next_gate: {result['next_gate']}")
