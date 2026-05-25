from __future__ import annotations

import json
from pathlib import Path
from typing import Any


STAGE219_SCHEMA_VERSION = "qrope_stage219_rope_substitution_gate_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage219_rope_substitution_gate"
STAGE30_RESULTS_PATH = Path("logs") / "automated_stage_gates" / "stage30_matched_retrieval_bridge" / "results.json"
STAGE32_RESULTS_PATH = Path("logs") / "automated_stage_gates" / "stage32_full_context_feature_bridge" / "results.json"

PRIMARY_STAGE = "stage30_matched_retrieval_bridge"
PRIMARY_PHASEWRAP_METHOD = "phasewrap_distance_adapter"
SECONDARY_STAGE = "stage32_full_context_feature_bridge"
SECONDARY_PHASEWRAP_METHOD = "phasewrap_multiscale_adapter"
ROPE_METHOD = "rope_relative"
NO_POSITION_METHOD = "no_position"
SINUSOIDAL_METHOD = "sinusoidal"

RANKING_PARITY_CRITERIA = {
    "minimum_run_count": 5,
    "minimum_phasewrap_top1": 0.9,
    "minimum_phasewrap_mrr": 0.95,
    "maximum_top1_degradation_vs_rope": 0.10,
    "maximum_mrr_degradation_vs_rope": 0.05,
    "minimum_top1_lift_vs_no_position": 0.50,
    "minimum_top1_lift_vs_sinusoidal": 0.10,
}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _method_row(result: dict[str, Any], method: str) -> dict[str, Any]:
    for row in result["table"]:
        if row["method"] == method:
            return row
    raise KeyError(f"method not present in {result.get('stage')}: {method}")


def _compare_stage(result: dict[str, Any], *, phasewrap_method: str) -> dict[str, Any]:
    phasewrap = _method_row(result, phasewrap_method)
    rope = _method_row(result, ROPE_METHOD)
    no_position = _method_row(result, NO_POSITION_METHOD)
    sinusoidal = _method_row(result, SINUSOIDAL_METHOD)
    parameter_count_equal = len({phasewrap["parameter_count"], rope["parameter_count"], no_position["parameter_count"], sinusoidal["parameter_count"]}) == 1
    run_count_equal = len({phasewrap["run_count"], rope["run_count"], no_position["run_count"], sinusoidal["run_count"]}) == 1
    top1_degradation = round(float(rope["top1_accuracy_mean"]) - float(phasewrap["top1_accuracy_mean"]), 6)
    mrr_degradation = round(float(rope["mrr_mean"]) - float(phasewrap["mrr_mean"]), 6)
    target_probability_degradation = round(float(rope["mean_target_probability_mean"]) - float(phasewrap["mean_target_probability_mean"]), 6)
    ece_degradation = round(float(phasewrap["expected_calibration_error_mean"]) - float(rope["expected_calibration_error_mean"]), 6)
    loss_degradation = round(float(phasewrap["loss_mean"]) - float(rope["loss_mean"]), 6)
    top1_lift_vs_no_position = round(float(phasewrap["top1_accuracy_mean"]) - float(no_position["top1_accuracy_mean"]), 6)
    top1_lift_vs_sinusoidal = round(float(phasewrap["top1_accuracy_mean"]) - float(sinusoidal["top1_accuracy_mean"]), 6)
    criteria = {
        "run_count_at_least_minimum": int(phasewrap["run_count"]) >= RANKING_PARITY_CRITERIA["minimum_run_count"],
        "parameter_count_matched": parameter_count_equal,
        "run_count_matched": run_count_equal,
        "phasewrap_top1_at_least_minimum": float(phasewrap["top1_accuracy_mean"]) >= RANKING_PARITY_CRITERIA["minimum_phasewrap_top1"],
        "phasewrap_mrr_at_least_minimum": float(phasewrap["mrr_mean"]) >= RANKING_PARITY_CRITERIA["minimum_phasewrap_mrr"],
        "top1_degradation_within_margin": top1_degradation <= RANKING_PARITY_CRITERIA["maximum_top1_degradation_vs_rope"],
        "mrr_degradation_within_margin": mrr_degradation <= RANKING_PARITY_CRITERIA["maximum_mrr_degradation_vs_rope"],
        "top1_lift_vs_no_position_met": top1_lift_vs_no_position >= RANKING_PARITY_CRITERIA["minimum_top1_lift_vs_no_position"],
        "top1_lift_vs_sinusoidal_met": top1_lift_vs_sinusoidal >= RANKING_PARITY_CRITERIA["minimum_top1_lift_vs_sinusoidal"],
        "rope_probability_advantage_recorded": target_probability_degradation > 0.0,
        "rope_calibration_advantage_recorded": ece_degradation > 0.0,
    }
    return {
        "stage": result["stage"],
        "dataset": result["dataset"],
        "phasewrap_method": phasewrap_method,
        "rope_method": ROPE_METHOD,
        "no_position_method": NO_POSITION_METHOD,
        "sinusoidal_method": SINUSOIDAL_METHOD,
        "model": result["model"],
        "task": result["task"],
        "train_lengths": result["train_lengths"],
        "validation_lengths": result["validation_lengths"],
        "test_lengths": result["test_lengths"],
        "phasewrap_metrics": phasewrap,
        "rope_metrics": rope,
        "no_position_metrics": no_position,
        "sinusoidal_metrics": sinusoidal,
        "degradation_vs_rope": {
            "top1_accuracy": top1_degradation,
            "mrr": mrr_degradation,
            "mean_target_probability": target_probability_degradation,
            "expected_calibration_error": ece_degradation,
            "loss": loss_degradation,
        },
        "lift_vs_controls": {
            "top1_accuracy_vs_no_position": top1_lift_vs_no_position,
            "top1_accuracy_vs_sinusoidal": top1_lift_vs_sinusoidal,
        },
        "criteria": criteria,
        "all_criteria_pass": all(criteria.values()),
    }


def run_stage219_rope_substitution_gate(
    *,
    stage30_results_path: Path = STAGE30_RESULTS_PATH,
    stage32_results_path: Path = STAGE32_RESULTS_PATH,
) -> dict[str, Any]:
    stage30 = _load_json(stage30_results_path)
    stage32 = _load_json(stage32_results_path)
    primary = _compare_stage(stage30, phasewrap_method=PRIMARY_PHASEWRAP_METHOD)
    secondary = _compare_stage(stage32, phasewrap_method=SECONDARY_PHASEWRAP_METHOD)
    blockers: list[str] = []
    if primary["stage"] != PRIMARY_STAGE:
        blockers.append(f"primary stage mismatch: {primary['stage']}")
    if secondary["stage"] != SECONDARY_STAGE:
        blockers.append(f"secondary stage mismatch: {secondary['stage']}")
    if not primary["all_criteria_pass"]:
        failed = [key for key, value in primary["criteria"].items() if not value]
        blockers.append(f"primary ranking-parity criteria failed: {failed}")
    if not secondary["all_criteria_pass"]:
        failed = [key for key, value in secondary["criteria"].items() if not value]
        blockers.append(f"secondary ranking-parity criteria failed: {failed}")
    decision = (
        "BOUNDED_PHASEWRAP_ROPE_SUBSTITUTION_SUPPORTED_WITH_MEASURED_CALIBRATION_DEGRADATION"
        if not blockers
        else "BOUNDED_PHASEWRAP_ROPE_SUBSTITUTION_NOT_SUPPORTED"
    )
    return {
        "schema_version": STAGE219_SCHEMA_VERSION,
        "stage": "stage219_rope_substitution_gate",
        "decision": decision,
        "blockers": blockers,
        "ranking_parity_criteria": RANKING_PARITY_CRITERIA,
        "adequacy_criteria": RANKING_PARITY_CRITERIA,
        "primary_benchmark": primary,
        "secondary_benchmark": secondary,
        "supported_claim": (
            "PhaseWrap-derived adapters reach ranking parity with RoPE in these bounded retrieval-bridge benchmarks: "
            "they preserve held-out retrieval top-1/MRR within the predeclared rank margin while showing measured "
            "degradation versus RoPE on probability, calibration, and loss."
        ),
        "claim_boundary": {
            "supports": [
                "bounded non-phase-cued retrieval-bridge ranking parity",
                "measured degradation versus RoPE with preserved retrieval behavior",
                "multi-seed same-parameter comparison against no-position, sinusoidal, and RoPE controls",
            ],
            "does_not_support": [
                "substitution adequacy",
                "general RoPE replacement",
                "production transformer superiority",
                "language-model-scale validation",
                "quantum advantage",
            ],
        },
    }


def write_stage219_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "decision": result["decision"],
        "blockers": result["blockers"],
        "adequacy_criteria": result["adequacy_criteria"],
        "ranking_parity_criteria": result["ranking_parity_criteria"],
        "primary_stage": result["primary_benchmark"]["stage"],
        "primary_phasewrap_method": result["primary_benchmark"]["phasewrap_method"],
        "secondary_stage": result["secondary_benchmark"]["stage"],
        "secondary_phasewrap_method": result["secondary_benchmark"]["phasewrap_method"],
        "result_path": str((output_dir / "results.json").as_posix()),
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "results": str(output_dir / "results.json"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return paths


def print_stage219_summary(result: dict[str, Any]) -> None:
    print(result["decision"])
    for label in ("primary_benchmark", "secondary_benchmark"):
        benchmark = result[label]
        degradation = benchmark["degradation_vs_rope"]
        print(
            f"{label}: {benchmark['phasewrap_method']} top1={benchmark['phasewrap_metrics']['top1_accuracy_mean']} "
            f"mrr={benchmark['phasewrap_metrics']['mrr_mean']} "
            f"target_prob_degradation={degradation['mean_target_probability']} "
            f"ece_degradation={degradation['expected_calibration_error']}"
        )
