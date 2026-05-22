from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE110_SCHEMA_VERSION = "qrope_stage110_replicated_advantage_claim_gate_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE105_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage105_independent_rerun_protocol" / "manifest.json"
DEFAULT_STAGE109_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage109_window_evidence_intake_validator" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage110_replicated_advantage_claim_gate"
COMPARATOR_FAMILIES = ("rope_like", "sinusoidal_like", "alibi_like", "no_position_control")
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _comparison_pass(record: dict[str, Any]) -> bool:
    lower_than = {str(family) for family in record.get("phasewrap_lower_error_than", [])}
    return bool(record.get("all_families_present") is True and all(family in lower_than for family in COMPARATOR_FAMILIES))


def _window_metric_records(stage109: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not stage109:
        return []
    records = []
    for window in stage109.get("window_records", []):
        stage103_path = Path(str(window.get("stage103_results_path", "")))
        stage103 = _load_json(stage103_path)
        for summary in stage103.get("comparison_summary", []) if isinstance(stage103, dict) else []:
            records.append(
                {
                    "window_id": window.get("window_id"),
                    "provider": window.get("provider"),
                    "source_lane_id": summary.get("source_lane_id"),
                    "circuit_template": summary.get("circuit_template"),
                    "phasewrap_mean_absolute_score_error": summary.get("phasewrap_mean_absolute_score_error"),
                    "best_comparator_mean_absolute_score_error": summary.get("best_comparator_mean_absolute_score_error"),
                    "phasewrap_lower_error_than": summary.get("phasewrap_lower_error_than", []),
                    "all_families_present": summary.get("all_families_present"),
                    "stage103_results_path": str(stage103_path.as_posix()),
                    "passes_stage103_advantage_rule": _comparison_pass(summary),
                }
            )
    return records


def _replication_records(window_metrics: list[dict[str, Any]], stage109: dict[str, Any] | None) -> list[dict[str, Any]]:
    provider_windows: dict[str, set[str]] = {}
    for window in stage109.get("window_records", []) if stage109 else []:
        if window.get("ready") is True:
            provider_windows.setdefault(str(window.get("provider")), set()).add(str(window.get("window_id")))

    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for record in window_metrics:
        key = (str(record["provider"]), str(record["source_lane_id"]), str(record["circuit_template"]))
        grouped.setdefault(key, []).append(record)

    replication = []
    for (provider, source_lane_id, circuit_template), records in sorted(grouped.items()):
        required_windows = provider_windows.get(provider, set())
        observed_windows = {str(record["window_id"]) for record in records}
        passing_windows = {str(record["window_id"]) for record in records if record["passes_stage103_advantage_rule"]}
        replicated = bool(required_windows) and required_windows <= observed_windows and required_windows <= passing_windows
        replication.append(
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
                "replicated_phasewrap_advantage": replicated,
            }
        )
    return replication


def run_stage110_claim_gate(
    *,
    stage105_manifest_path: Path = DEFAULT_STAGE105_MANIFEST,
    stage109_results_path: Path = DEFAULT_STAGE109_RESULTS,
) -> dict[str, Any]:
    stage105 = _load_json(stage105_manifest_path)
    stage109 = _load_json(stage109_results_path)
    sources = [
        (stage105_manifest_path, stage105),
        (stage109_results_path, stage109),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    stage109_ready = bool(stage109 and stage109.get("decision") == "WINDOW_EVIDENCE_INTAKE_READY_FOR_STAGE105_AGGREGATION")
    window_metrics = _window_metric_records(stage109 if stage109_ready else None)
    replication = _replication_records(window_metrics, stage109 if stage109_ready else None)
    replicated = [record for record in replication if record["replicated_phasewrap_advantage"]]

    if missing_sources:
        decision = "REPLICATED_ADVANTAGE_CLAIM_GATE_INCOMPLETE"
    elif not stage109_ready:
        decision = "REPLICATED_ADVANTAGE_CLAIM_BLOCKED_EVIDENCE_INTAKE_INCOMPLETE"
    elif replicated:
        decision = "PHASEWRAP_REPLICATED_ADVANTAGE_SUPPORTED_BY_STAGE105_RULE"
    else:
        decision = "PHASEWRAP_REPLICATED_ADVANTAGE_NOT_SUPPORTED_BY_STAGE105_RULE"

    return {
        "schema_version": STAGE110_SCHEMA_VERSION,
        "stage": "stage110_replicated_advantage_claim_gate",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage105_decision": stage105.get("decision") if isinstance(stage105, dict) else None,
        "stage109_decision": stage109.get("decision") if isinstance(stage109, dict) else None,
        "stage109_ready_for_aggregation": stage109_ready,
        "window_metric_record_count": len(window_metrics),
        "replication_record_count": len(replication),
        "replicated_advantage_count": len(replicated),
        "replication_records": replication,
        "window_metric_records": window_metrics,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "a deterministic gate that binds any replicated PhaseWrap claim to Stage 109 readiness",
                "application of the preregistered Stage 103 lower-MAE rule across Stage 105 independent windows",
                "explicit reporting of not-supported outcomes when any required window fails the advantage rule",
            ],
            "excluded": [
                "real hardware submission",
                "provider credential validation",
                "a noisy-hardware advantage claim when evidence intake is incomplete",
                "provider-wide or transformer-scale superiority beyond recorded windows",
            ],
        },
        "next_gate": (
            "If Stage 109 is blocked, complete the missing window evidence first. If Stage 109 is ready, use this gate "
            "as the final automated check before describing any replicated PhaseWrap noisy-hardware advantage."
        ),
    }


def write_stage110_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage105_decision": result["stage105_decision"],
        "stage109_decision": result["stage109_decision"],
        "stage109_ready_for_aggregation": result["stage109_ready_for_aggregation"],
        "window_metric_record_count": result["window_metric_record_count"],
        "replication_record_count": result["replication_record_count"],
        "replicated_advantage_count": result["replicated_advantage_count"],
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
                "replicated_phasewrap_advantage",
            ),
        )
        writer.writeheader()
        for record in result["replication_records"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage110_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"stage109_ready_for_aggregation: {result['stage109_ready_for_aggregation']}")
    print(f"replication_record_count: {result['replication_record_count']}")
    print(f"replicated_advantage_count: {result['replicated_advantage_count']}")
    print(f"next_gate: {result['next_gate']}")
