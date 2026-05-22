from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from qrope.stage198_reduced_scope_preregistration import DEFAULT_OUTPUT_DIR as STAGE198_OUTPUT_DIR
from qrope.stage208_reduced_scope_calibration_validation import DEFAULT_OUTPUT_DIR as STAGE208_OUTPUT_DIR
from qrope.stage209_reduced_scope_hardware_metric_interpreter import DEFAULT_OUTPUT_DIR as STAGE209_OUTPUT_DIR
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE210_SCHEMA_VERSION = "qrope_stage210_reduced_scope_objective_conclusion_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE198_RESULTS = STAGE198_OUTPUT_DIR / "results.json"
DEFAULT_STAGE208_RESULTS = STAGE208_OUTPUT_DIR / "results.json"
DEFAULT_STAGE209_RESULTS = STAGE209_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage210_reduced_scope_objective_conclusion_100usd"
STAGE208_READY = "REDUCED_SCOPE_CALIBRATION_VALIDATED_READY_FOR_METRICS"
STAGE209_POSITIVE = "REDUCED_SCOPE_HARDWARE_POSITIVE_PHASEWRAP_ADVANTAGE"
REQUIRED_TEMPLATES: tuple[str, ...] = (
    "two_ry_cx_parity_z_readout_v1",
    "two_ry_product_state_z_readout_v1",
)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _minimum_margin(records: list[dict[str, Any]], key: str) -> float | None:
    values = [float(record[key]) for record in records if record.get(key) is not None]
    return min(values) if values else None


def _seed_pair_positive(record: dict[str, Any], required_template_count: int) -> bool:
    return bool(
        record.get("reduced_scope_hardware_positive") is True
        and int(record.get("stable_template_count") or 0) >= required_template_count
        and set(record.get("stable_templates", [])) >= set(REQUIRED_TEMPLATES)
    )


def run_stage210_reduced_scope_objective_conclusion(
    *,
    stage198_results_path: Path = DEFAULT_STAGE198_RESULTS,
    stage208_results_path: Path = DEFAULT_STAGE208_RESULTS,
    stage209_results_path: Path = DEFAULT_STAGE209_RESULTS,
) -> dict[str, Any]:
    stage198 = _load_json(stage198_results_path)
    stage208 = _load_json(stage208_results_path)
    stage209 = _load_json(stage209_results_path)
    sources = [(stage198_results_path, stage198), (stage208_results_path, stage208), (stage209_results_path, stage209)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    blockers: list[str] = []
    if missing_sources:
        blockers.append("missing_source_artifacts")
    boundary = stage198.get("interpretation_boundary", {}) if isinstance(stage198, dict) else {}
    pass_policy = boundary.get("pass_fail_policy", {})
    if not pass_policy:
        blockers.append("stage198_pass_policy_missing")
    if isinstance(stage208, dict) and stage208.get("decision") != STAGE208_READY:
        blockers.append("stage208_calibration_not_ready")
    if isinstance(stage209, dict) and stage209.get("decision") != STAGE209_POSITIVE:
        blockers.append("stage209_reduced_scope_positive_missing")
    if isinstance(stage209, dict) and stage209.get("blockers"):
        blockers.append("stage209_has_blockers")
    candidate_records = stage209.get("candidate_records", []) if isinstance(stage209, dict) else []
    comparison_summary = stage209.get("comparison_summary", []) if isinstance(stage209, dict) else []
    min_seed_pairs = int(pass_policy.get("minimum_stable_seed_pairs") or 0)
    min_templates = int(pass_policy.get("minimum_stable_templates_per_seed_pair") or 0)
    min_positional_threshold = float(pass_policy.get("minimum_scaled_best_positional_margin_shot_quanta") or 0.0)
    min_null_threshold = float(pass_policy.get("minimum_scaled_matched_null_margin_shot_quanta") or 0.0)
    positive_seed_pairs = [record for record in candidate_records if _seed_pair_positive(record, min_templates)]
    weakest_positional_margin = _minimum_margin(candidate_records, "min_positional_margin_shot_quanta")
    weakest_null_margin = _minimum_margin(candidate_records, "min_matched_null_margin_shot_quanta")
    if len(positive_seed_pairs) < min_seed_pairs:
        blockers.append("stable_seed_pair_count_below_threshold")
    if weakest_positional_margin is None or weakest_positional_margin < min_positional_threshold:
        blockers.append("positional_margin_below_threshold")
    if weakest_null_margin is None or weakest_null_margin < min_null_threshold:
        blockers.append("matched_null_margin_below_threshold")
    if len(comparison_summary) != 4:
        blockers.append("comparison_group_count_mismatch")
    if any(record.get("all_families_present") is not True for record in comparison_summary):
        blockers.append("comparison_family_coverage_incomplete")
    if stage209.get("packet_template_count") != 20 if isinstance(stage209, dict) else True:
        blockers.append("packet_template_count_mismatch")

    objective_supported = not blockers
    if missing_sources:
        decision = "REDUCED_SCOPE_OBJECTIVE_CONCLUSION_INCOMPLETE"
    elif objective_supported:
        decision = "REDUCED_SCOPE_OBJECTIVE_SUPPORTED_BY_HARDWARE_ROBUSTNESS"
    else:
        decision = "REDUCED_SCOPE_OBJECTIVE_CONCLUSION_BLOCKED_OR_NOT_SUPPORTED"

    supported_claim = (
        "Under the preregistered reduced-precision fixed-width protocol on IBM ibm_fez, PhaseWrap-RoPE's compact "
        "phase-wrap positional score showed lower normalized noise sensitivity than matched RoPE-like, sinusoidal-like, "
        "ALIBI-like, and matched nonzero null-control encodings across two seeds and two circuit templates."
        if objective_supported
        else None
    )
    return {
        "schema_version": STAGE210_SCHEMA_VERSION,
        "stage": "stage210_reduced_scope_objective_conclusion",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "objective_supported": objective_supported,
        "support_mode": "robustness" if objective_supported else None,
        "auditability_advantage_separately_supported": False,
        "supported_claim": supported_claim,
        "hardware_scope_label": boundary.get("hardware_scope_label") or (stage209.get("hardware_scope_label") if isinstance(stage209, dict) else None),
        "backend": "ibm_fez",
        "shot_count_per_packet_row": boundary.get("shots_per_row"),
        "bitstring_order": stage209.get("bitstring_order") if isinstance(stage209, dict) else None,
        "stable_seed_pair_count": len(positive_seed_pairs),
        "required_stable_seed_pair_count": min_seed_pairs,
        "stable_template_count_per_seed_pair_required": min_templates,
        "comparison_group_count": len(comparison_summary),
        "packet_template_count": stage209.get("packet_template_count") if isinstance(stage209, dict) else None,
        "weakest_positional_margin_shot_quanta": weakest_positional_margin,
        "required_positional_margin_shot_quanta": min_positional_threshold,
        "weakest_matched_null_margin_shot_quanta": weakest_null_margin,
        "required_matched_null_margin_shot_quanta": min_null_threshold,
        "candidate_records": candidate_records,
        "comparison_summary": comparison_summary,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "claim_boundary": {
            "supported": [
                "reduced-precision 2048-shot IBM ibm_fez hardware robustness advantage",
                "fixed-width matched-comparator comparison across PhaseWrap, RoPE-like, sinusoidal-like, ALIBI-like, and matched nonzero null control",
                "two independent IBM seed pairs and two circuit templates under preregistered Stage198 thresholds",
                "calibration-applied q1q0 bitstring ordering before metric interpretation",
            ],
            "excluded": [
                "full 4096-shot evidentiary-run equivalence",
                "standalone auditability advantage beyond the robustness metric surface",
                "cross-backend or provider-wide superiority",
                "transformer-scale or task-general superiority",
                "post-hoc readout mitigation or threshold changes",
                "new hardware submission",
            ],
        },
        "next_gate": "Use this as the reduced-scope hardware conclusion; pause before any full 4096-shot or cross-backend spend.",
    }


def write_stage210_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_keys = (
        "schema_version", "stage", "status", "objective", "decision", "source_artifacts",
        "missing_source_artifacts", "blockers", "objective_supported", "support_mode",
        "auditability_advantage_separately_supported", "supported_claim", "hardware_scope_label",
        "backend", "shot_count_per_packet_row", "bitstring_order", "stable_seed_pair_count",
        "required_stable_seed_pair_count", "stable_template_count_per_seed_pair_required",
        "comparison_group_count", "packet_template_count", "weakest_positional_margin_shot_quanta",
        "required_positional_margin_shot_quanta", "weakest_matched_null_margin_shot_quanta",
        "required_matched_null_margin_shot_quanta", "no_hardware_submission",
        "provider_credentials_required", "secret_values_recorded", "runnable_commands_recorded",
        "claim_boundary", "next_gate",
    )
    manifest = {key: result[key] for key in manifest_keys}
    manifest["result_path"] = str((output_dir / "results.json").as_posix())
    manifest["summary_csv_path"] = str((output_dir / "summary.csv").as_posix())
    paths = {"manifest": str(output_dir / "manifest.json"), "result": str(output_dir / "results.json"), "summary_csv": str(output_dir / "summary.csv")}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "seed_pair",
                "stable_template_count",
                "min_positional_margin_shot_quanta",
                "min_matched_null_margin_shot_quanta",
                "reduced_scope_hardware_positive",
            ),
        )
        writer.writeheader()
        for record in result["candidate_records"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage210_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"objective_supported: {result['objective_supported']}")
    print(f"support_mode: {result['support_mode']}")
    print(f"stable_seed_pair_count: {result['stable_seed_pair_count']}/{result['required_stable_seed_pair_count']}")
    print(f"weakest_positional_margin_shot_quanta: {result['weakest_positional_margin_shot_quanta']}")
    print(f"weakest_matched_null_margin_shot_quanta: {result['weakest_matched_null_margin_shot_quanta']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
