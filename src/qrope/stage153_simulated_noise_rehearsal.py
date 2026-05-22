from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from qrope.stage103_robustness_metric_preregistration import packet_metrics


STAGE153_SCHEMA_VERSION = "qrope_stage153_simulated_noise_rehearsal_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE99_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage99_matched_fixed_width_encoding_packets" / "manifest.json"
DEFAULT_STAGE100_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage100_matched_cx_encoding_packets" / "manifest.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage153_simulated_noise_rehearsal"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
ENCODING_FAMILIES: tuple[str, ...] = (
    "phasewrap",
    "rope_like",
    "sinusoidal_like",
    "alibi_like",
    "no_position_control",
)
POSITIONAL_COMPARATOR_FAMILIES: tuple[str, ...] = ("rope_like", "sinusoidal_like", "alibi_like")
STRICT_COMPARATOR_FAMILIES: tuple[str, ...] = POSITIONAL_COMPARATOR_FAMILIES + ("no_position_control",)
DEFAULT_NOISE_MODELS: tuple[dict[str, Any], ...] = (
    {
        "noise_model_id": "ideal_deterministic_counts",
        "noise_family": "ideal",
        "readout_bitflip_probability": 0.0,
        "depolarizing_observable_shrink": 0.0,
    },
    {
        "noise_model_id": "readout_bitflip_1pct",
        "noise_family": "symmetric_readout_bitflip",
        "readout_bitflip_probability": 0.01,
        "depolarizing_observable_shrink": 0.0,
    },
    {
        "noise_model_id": "readout_bitflip_3pct",
        "noise_family": "symmetric_readout_bitflip",
        "readout_bitflip_probability": 0.03,
        "depolarizing_observable_shrink": 0.0,
    },
    {
        "noise_model_id": "observable_depolarizing_5pct",
        "noise_family": "observable_depolarizing",
        "readout_bitflip_probability": 0.0,
        "depolarizing_observable_shrink": 0.05,
    },
)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _packet_paths_from_manifest(manifest: dict[str, Any] | None) -> list[Path]:
    if not isinstance(manifest, dict):
        return []
    return [Path(str(path)) for path in manifest.get("packet_paths", [])]


def _bit_for_value(value: int) -> str:
    return "0" if value == 1 else "1"


def _counts_from_probabilities(probabilities: dict[str, float], shots: int) -> dict[str, int]:
    raw_counts = {key: probabilities[key] * shots for key in sorted(probabilities)}
    counts = {key: int(raw_counts[key]) for key in raw_counts}
    remaining = shots - sum(counts.values())
    ranked = sorted(raw_counts, key=lambda key: (raw_counts[key] - counts[key], key), reverse=True)
    for key in ranked[:remaining]:
        counts[key] += 1
    return counts


def _clamp_component(value: float) -> float:
    return max(-1.0, min(1.0, float(value)))


def _noisy_components(row: dict[str, Any], noise_model: dict[str, Any], circuit_template: str) -> tuple[float, float]:
    components = row.get("components", {})
    component_a = _clamp_component(float(components.get("component_a", 0.0)))
    component_b = _clamp_component(float(components.get("component_b", 0.0)))
    bitflip = float(noise_model.get("readout_bitflip_probability") or 0.0)
    depolarizing = float(noise_model.get("depolarizing_observable_shrink") or 0.0)
    z_shrink = max(0.0, 1.0 - 2.0 * bitflip)
    depol_shrink = max(0.0, 1.0 - depolarizing)
    if circuit_template == "two_ry_cx_parity_z_readout_v1":
        return component_a * z_shrink * depol_shrink, component_b * (z_shrink**2) * depol_shrink
    return component_a * z_shrink * depol_shrink, component_b * z_shrink * depol_shrink


def _row_counts(row: dict[str, Any], circuit_template: str, shots: int, noise_model: dict[str, Any]) -> dict[str, int]:
    component_a, component_b = _noisy_components(row, noise_model, circuit_template)
    probabilities: dict[str, float] = {}
    if circuit_template == "two_ry_product_state_z_readout_v1":
        p_z0_plus = (1.0 + component_a) / 2.0
        p_z1_plus = (1.0 + component_b) / 2.0
        for z0 in (1, -1):
            for z1 in (1, -1):
                probability = (p_z0_plus if z0 == 1 else 1.0 - p_z0_plus) * (
                    p_z1_plus if z1 == 1 else 1.0 - p_z1_plus
                )
                probabilities[f"{_bit_for_value(z0)}{_bit_for_value(z1)}"] = probability
    elif circuit_template == "two_ry_cx_parity_z_readout_v1":
        p_z0_plus = (1.0 + component_a) / 2.0
        p_parity_plus = (1.0 + component_b) / 2.0
        for z0 in (1, -1):
            for parity in (1, -1):
                z1 = z0 * parity
                probability = (p_z0_plus if z0 == 1 else 1.0 - p_z0_plus) * (
                    p_parity_plus if parity == 1 else 1.0 - p_parity_plus
                )
                probabilities[f"{_bit_for_value(z0)}{_bit_for_value(z1)}"] = probability
    else:
        raise ValueError(f"unsupported circuit template: {circuit_template}")
    return _counts_from_probabilities(probabilities, shots)


def _simulated_execution(packet: dict[str, Any], noise_model: dict[str, Any]) -> dict[str, Any]:
    circuit_template = str(packet.get("fixed_width", {}).get("circuit_template"))
    shots = int(packet.get("shot_count") or 1024)
    return {
        "status": "simulated_noise_rehearsal",
        "no_hardware_submission": True,
        "noise_model_id": noise_model["noise_model_id"],
        "raw_counts_by_row": [
            {
                "row_id": row.get("row_id"),
                "counts": _row_counts(row, circuit_template, shots, noise_model),
            }
            for row in packet.get("rows", [])
        ],
    }


def _metric_records(packet_paths: list[Path], noise_models: tuple[dict[str, Any], ...]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    for packet_path in packet_paths:
        packet = _load_json(packet_path)
        if not isinstance(packet, dict):
            missing.append({"packet_path": str(packet_path.as_posix()), "reason": "missing_packet"})
            continue
        for noise_model in noise_models:
            execution = _simulated_execution(packet, noise_model)
            record = packet_metrics(packet, execution)
            records.append(
                {
                    **record,
                    "noise_model_id": noise_model["noise_model_id"],
                    "noise_family": noise_model["noise_family"],
                    "readout_bitflip_probability": noise_model["readout_bitflip_probability"],
                    "depolarizing_observable_shrink": noise_model["depolarizing_observable_shrink"],
                    "simulated_only": True,
                }
            )
    return records, missing


def _comparison_summary(metric_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str], dict[str, dict[str, Any]]] = {}
    for record in metric_records:
        key = (
            str(record["noise_model_id"]),
            str(record.get("provider")),
            str(record["source_lane_id"]),
            str(record["circuit_template"]),
        )
        grouped.setdefault(key, {})[str(record["encoding_family"])] = record
    summaries = []
    for (noise_model_id, provider, source_lane_id, circuit_template), by_family in sorted(grouped.items()):
        phasewrap = by_family.get("phasewrap")
        phasewrap_mae = phasewrap.get("mean_absolute_score_error") if phasewrap else None
        lower_than = []
        for family in STRICT_COMPARATOR_FAMILIES:
            comparator = by_family.get(family)
            comparator_mae = comparator.get("mean_absolute_score_error") if comparator else None
            if phasewrap_mae is not None and comparator_mae is not None and phasewrap_mae < comparator_mae:
                lower_than.append(family)
        summaries.append(
            {
                "noise_model_id": noise_model_id,
                "provider": provider,
                "source_lane_id": source_lane_id,
                "circuit_template": circuit_template,
                "phasewrap_mean_absolute_score_error": phasewrap_mae,
                "best_positional_comparator_mean_absolute_score_error": min(
                    [
                        by_family[family]["mean_absolute_score_error"]
                        for family in POSITIONAL_COMPARATOR_FAMILIES
                        if family in by_family and by_family[family].get("mean_absolute_score_error") is not None
                    ],
                    default=None,
                ),
                "no_position_control_mean_absolute_score_error": (
                    by_family.get("no_position_control", {}).get("mean_absolute_score_error")
                ),
                "phasewrap_lower_error_than": lower_than,
                "all_families_present": all(family in by_family for family in ENCODING_FAMILIES),
                "phasewrap_beats_positional_comparators": all(family in lower_than for family in POSITIONAL_COMPARATOR_FAMILIES),
                "phasewrap_beats_all_families_including_control": all(family in lower_than for family in STRICT_COMPARATOR_FAMILIES),
            }
        )
    return summaries


def run_stage153_simulated_noise_rehearsal(
    *,
    stage99_manifest_path: Path = DEFAULT_STAGE99_MANIFEST,
    stage100_manifest_path: Path = DEFAULT_STAGE100_MANIFEST,
    noise_models: tuple[dict[str, Any], ...] = DEFAULT_NOISE_MODELS,
) -> dict[str, Any]:
    stage99 = _load_json(stage99_manifest_path)
    stage100 = _load_json(stage100_manifest_path)
    sources = [(stage99_manifest_path, stage99), (stage100_manifest_path, stage100)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    packet_paths = _packet_paths_from_manifest(stage99) + _packet_paths_from_manifest(stage100)
    metric_records, missing_packets = _metric_records(packet_paths, noise_models)
    comparison_summary = _comparison_summary(metric_records)
    complete_groups = [record for record in comparison_summary if record["all_families_present"] is True]
    noisy_groups = [record for record in complete_groups if record["noise_model_id"] != "ideal_deterministic_counts"]
    positional_advantage = [record for record in noisy_groups if record["phasewrap_beats_positional_comparators"] is True]
    strict_advantage = [record for record in noisy_groups if record["phasewrap_beats_all_families_including_control"] is True]
    if missing_sources or missing_packets or not complete_groups:
        decision = "SIMULATED_NOISE_REHEARSAL_INCOMPLETE"
    elif strict_advantage:
        decision = "SIMULATED_NOISE_PHASEWRAP_STRICT_ADVANTAGE_OBSERVED"
    elif positional_advantage:
        decision = "SIMULATED_NOISE_PHASEWRAP_POSITIONAL_ADVANTAGE_OBSERVED_CONTROL_NOT_BEATEN"
    else:
        decision = "SIMULATED_NOISE_PHASEWRAP_ADVANTAGE_NOT_OBSERVED"
    return {
        "schema_version": STAGE153_SCHEMA_VERSION,
        "stage": "stage153_simulated_noise_rehearsal",
        "status": "completed" if not missing_sources and not missing_packets else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "missing_packets": missing_packets,
        "noise_models": list(noise_models),
        "noise_model_count": len(noise_models),
        "packet_count": len(packet_paths),
        "metric_record_count": len(metric_records),
        "comparison_group_count": len(comparison_summary),
        "complete_comparison_group_count": len(complete_groups),
        "noisy_comparison_group_count": len(noisy_groups),
        "phasewrap_positional_advantage_group_count": len(positional_advantage),
        "phasewrap_strict_advantage_group_count": len(strict_advantage),
        "simulated_only": True,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "metric_records": metric_records,
        "comparison_summary": comparison_summary,
        "claim_boundary": {
            "supported": [
                "deterministic simulated-noise rehearsal over frozen Stage 99 and Stage 100 matched packets",
                "screening signal for whether real hardware execution is worth prioritizing",
                "separate reporting of PhaseWrap versus positional comparators and versus the no-position/control family",
            ],
            "excluded": [
                "real noisy-hardware evidence",
                "provider credential validation",
                "hardware job submission",
                "a Stage 110, Stage 138, or publication-ready noisy-hardware advantage claim",
            ],
        },
        "next_gate": (
            "Use this simulated-only result as a go/no-go screen. A real noisy-hardware conclusion still requires "
            "Stage 101/103/109/137/148/110/138 evidence from provider counts."
        ),
    }


def write_stage153_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "noise_models": result["noise_models"],
        "noise_model_count": result["noise_model_count"],
        "packet_count": result["packet_count"],
        "metric_record_count": result["metric_record_count"],
        "comparison_group_count": result["comparison_group_count"],
        "complete_comparison_group_count": result["complete_comparison_group_count"],
        "noisy_comparison_group_count": result["noisy_comparison_group_count"],
        "phasewrap_positional_advantage_group_count": result["phasewrap_positional_advantage_group_count"],
        "phasewrap_strict_advantage_group_count": result["phasewrap_strict_advantage_group_count"],
        "simulated_only": result["simulated_only"],
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
                "noise_model_id",
                "provider",
                "source_lane_id",
                "circuit_template",
                "phasewrap_mean_absolute_score_error",
                "best_positional_comparator_mean_absolute_score_error",
                "no_position_control_mean_absolute_score_error",
                "phasewrap_beats_positional_comparators",
                "phasewrap_beats_all_families_including_control",
            ),
        )
        writer.writeheader()
        for record in result["comparison_summary"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage153_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"noise_model_count: {result['noise_model_count']}")
    print(f"complete_comparison_group_count: {result['complete_comparison_group_count']}")
    print(f"phasewrap_positional_advantage_group_count: {result['phasewrap_positional_advantage_group_count']}")
    print(f"phasewrap_strict_advantage_group_count: {result['phasewrap_strict_advantage_group_count']}")
    print(f"next_gate: {result['next_gate']}")
