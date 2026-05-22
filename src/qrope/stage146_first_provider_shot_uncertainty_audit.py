from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any


STAGE146_SCHEMA_VERSION = "qrope_stage146_first_provider_shot_uncertainty_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE107_WINDOW_PLANS = DEFAULT_ARTIFACT_ROOT / "stage107_window_execution_orchestrator" / "window_execution_plans.json"
DEFAULT_STAGE145_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage145_first_provider_evidence_path_audit" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage146_first_provider_shot_uncertainty_audit"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
POSITIONAL_COMPARATOR_FAMILIES: tuple[str, ...] = ("rope_like", "sinusoidal_like", "alibi_like", "no_position_control")
Z_95 = 1.96


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _step(plan: dict[str, Any], step_id: str) -> dict[str, Any]:
    for item in plan.get("steps", []):
        if item.get("step_id") == step_id:
            return item
    return {}


def _score_standard_error(shots: int) -> float:
    # Score is 0.5 + 0.25 * (observable_a + observable_b); each observable is bounded in [-1, 1].
    return math.sqrt(2.0) / (4.0 * math.sqrt(float(shots)))


def _packet_record(window: dict[str, Any], packet: dict[str, Any]) -> dict[str, Any]:
    shots = int(packet.get("shot_count") or 0)
    row_count = int(packet.get("row_count") or 0)
    score_se = _score_standard_error(shots) if shots > 0 else None
    mae_se = score_se / math.sqrt(float(row_count)) if score_se is not None and row_count > 0 else None
    return {
        "provider": window.get("provider"),
        "window_id": window.get("window_id"),
        "packet_id": packet.get("packet_id"),
        "source_lane_id": packet.get("source_lane_id"),
        "encoding_family": packet.get("encoding_family"),
        "circuit_template": packet.get("circuit_template"),
        "shot_count": shots,
        "row_count": row_count,
        "conservative_score_standard_error": round(score_se, 12) if score_se is not None else None,
        "conservative_mae_standard_error": round(mae_se, 12) if mae_se is not None else None,
        "ready": shots > 0 and row_count > 0,
        "missing_evidence": [] if shots > 0 and row_count > 0 else ["shot_count_or_row_count"],
    }


def _lane_summaries(packet_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str], dict[str, dict[str, Any]]] = {}
    for record in packet_records:
        key = (
            str(record["provider"]),
            str(record["window_id"]),
            str(record["source_lane_id"]),
            str(record["circuit_template"]),
        )
        grouped.setdefault(key, {})[str(record["encoding_family"])] = record
    summaries = []
    for (provider, window_id, source_lane_id, circuit_template), by_family in sorted(grouped.items()):
        phasewrap = by_family.get("phasewrap")
        comparator_records = [by_family.get(family) for family in POSITIONAL_COMPARATOR_FAMILIES]
        ready_records = [record for record in [phasewrap, *comparator_records] if isinstance(record, dict)]
        max_mae_se = max(
            (float(record["conservative_mae_standard_error"]) for record in ready_records if record.get("conservative_mae_standard_error") is not None),
            default=None,
        )
        difference_half_width = Z_95 * math.sqrt(2.0) * max_mae_se if max_mae_se is not None else None
        summaries.append(
            {
                "provider": provider,
                "window_id": window_id,
                "source_lane_id": source_lane_id,
                "circuit_template": circuit_template,
                "phasewrap_present": phasewrap is not None,
                "all_comparators_present": all(family in by_family for family in POSITIONAL_COMPARATOR_FAMILIES),
                "packet_family_count": len(by_family),
                "max_conservative_mae_standard_error": round(max_mae_se, 12) if max_mae_se is not None else None,
                "minimum_phasewrap_mae_margin_for_95pct_shot_noise_separation": round(difference_half_width, 12)
                if difference_half_width is not None
                else None,
                "interpretation_rule": (
                    "A later PhaseWrap lower-MAE observation on this lane is shot-noise-separated only if the "
                    "PhaseWrap-vs-best-comparator MAE margin exceeds this 95% conservative half-width."
                ),
                "ready": phasewrap is not None and all(family in by_family for family in POSITIONAL_COMPARATOR_FAMILIES),
            }
        )
    return summaries


def run_stage146_audit(
    *,
    stage107_window_plans_path: Path = DEFAULT_STAGE107_WINDOW_PLANS,
    stage145_results_path: Path = DEFAULT_STAGE145_RESULTS,
    provider: str | None = None,
) -> dict[str, Any]:
    plans = _load_json(stage107_window_plans_path)
    stage145 = _load_json(stage145_results_path)
    sources = [(stage107_window_plans_path, plans), (stage145_results_path, stage145)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    first_provider = provider or (str(stage145.get("first_unlock_provider", "")) if isinstance(stage145, dict) else "")
    window_plans = [
        plan
        for plan in plans or []
        if isinstance(plan, dict) and (not first_provider or plan.get("provider") == first_provider)
    ] if isinstance(plans, list) else []
    packet_records = []
    for window in window_plans:
        packet_step = _step(window, "matched_packet_execution")
        for packet in packet_step.get("packet_templates", []):
            packet_records.append(_packet_record(window, packet))
    lane_summaries = _lane_summaries(packet_records)
    ready_lane_count = sum(1 for record in lane_summaries if record["ready"])
    ready = bool(first_provider) and bool(packet_records) and not missing_sources and ready_lane_count == len(lane_summaries)
    return {
        "schema_version": STAGE146_SCHEMA_VERSION,
        "stage": "stage146_first_provider_shot_uncertainty_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "FIRST_PROVIDER_SHOT_UNCERTAINTY_CONTRACT_READY_HARDWARE_COUNTS_REQUIRED"
            if ready
            else "FIRST_PROVIDER_SHOT_UNCERTAINTY_CONTRACT_INCOMPLETE"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "provider_scope": first_provider,
        "window_count": len(window_plans),
        "packet_count": len(packet_records),
        "ready_packet_count": sum(1 for record in packet_records if record["ready"]),
        "lane_summary_count": len(lane_summaries),
        "ready_lane_summary_count": ready_lane_count,
        "packet_records": packet_records,
        "lane_summaries": lane_summaries,
        "statistical_contract": {
            "score_formula": "score = 0.5 + 0.25 * (observable_a + observable_b)",
            "conservative_score_standard_error": "sqrt(2) / (4 * sqrt(shots))",
            "conservative_mae_standard_error": "score_standard_error / sqrt(row_count)",
            "mae_difference_95pct_half_width": "1.96 * sqrt(2) * max(packet_mae_standard_error)",
            "advantage_interpretation": (
                "The Stage 103 lower-MAE rule remains necessary. Stage 146 adds a shot-noise separation guard: "
                "a PhaseWrap MAE margin should exceed the lane-specific 95% half-width before being described as "
                "shot-noise-separated."
            ),
        },
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "conservative shot-noise uncertainty thresholds for the first-provider matched packet plan",
                "lane-specific minimum PhaseWrap MAE margins for later shot-noise-separated interpretation",
                "a statistical guardrail that does not depend on provider credentials or hardware execution",
            ],
            "excluded": [
                "provider credential values",
                "hardware job submission",
                "real provider result records",
                "readout calibration correction",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "After IBM Runtime results are collected and Stage 103 computes observed MAE margins, compare the observed "
            "PhaseWrap-vs-best-comparator margins against these lane-specific shot-noise half-widths before wording any advantage."
        ),
    }


def write_stage146_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "window_count": result["window_count"],
        "packet_count": result["packet_count"],
        "ready_packet_count": result["ready_packet_count"],
        "lane_summary_count": result["lane_summary_count"],
        "ready_lane_summary_count": result["ready_lane_summary_count"],
        "statistical_contract": result["statistical_contract"],
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
                "packet_family_count",
                "max_conservative_mae_standard_error",
                "minimum_phasewrap_mae_margin_for_95pct_shot_noise_separation",
                "ready",
            ),
        )
        writer.writeheader()
        for record in result["lane_summaries"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage146_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"provider_scope: {result['provider_scope']}")
    print(f"window_count: {result['window_count']}")
    print(f"packet_count: {result['packet_count']}")
    print(f"ready_lane_summary_count: {result['ready_lane_summary_count']}/{result['lane_summary_count']}")
    print(f"next_gate: {result['next_gate']}")
