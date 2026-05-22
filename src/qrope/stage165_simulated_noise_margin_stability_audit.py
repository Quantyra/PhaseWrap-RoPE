from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE165_SCHEMA_VERSION = "qrope_stage165_simulated_noise_margin_stability_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE153_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage153_simulated_noise_rehearsal" / "results.json"
DEFAULT_STAGE154_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage154_simulated_hardware_go_no_go" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage165_simulated_noise_margin_stability_audit"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
POSITIONAL_COMPARATOR_FIELD = "best_positional_comparator_mean_absolute_score_error"
CONTROL_FIELD = "no_position_control_mean_absolute_score_error"
MIN_POSITIONAL_QUANTA_FOR_STABLE_TARGET = 2.0
MIN_CONTROL_QUANTA_FOR_STABLE_TARGET = 2.0
MIN_STABLE_TEMPLATES_FOR_PROVIDER_TARGET = 2


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _margin(record: dict[str, Any], comparator_field: str) -> float | None:
    phasewrap = record.get("phasewrap_mean_absolute_score_error")
    comparator = record.get(comparator_field)
    if phasewrap is None or comparator is None:
        return None
    return round(float(comparator) - float(phasewrap), 12)


def _noise_model_map(stage153: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(record.get("noise_model_id")): record
        for record in stage153.get("noise_models", [])
        if isinstance(record, dict) and record.get("noise_model_id")
    }


def _metric_index(stage153: dict[str, Any]) -> dict[tuple[str, str, str, str, str], dict[str, Any]]:
    index = {}
    for record in stage153.get("metric_records", []):
        if not isinstance(record, dict):
            continue
        key = (
            str(record.get("noise_model_id")),
            str(record.get("provider")),
            str(record.get("source_lane_id")),
            str(record.get("circuit_template")),
            str(record.get("encoding_family")),
        )
        index[key] = record
    return index


def _shot_quantum(record: dict[str, Any] | None) -> float | None:
    if not isinstance(record, dict):
        return None
    shot_counts = record.get("shot_counts")
    if not isinstance(shot_counts, list) or not shot_counts:
        return None
    shots = min(int(value) for value in shot_counts if int(value) > 0)
    if shots <= 0:
        return None
    return 1.0 / shots


def _target_records(stage153: dict[str, Any], stage154: dict[str, Any]) -> list[dict[str, Any]]:
    metric_records = _metric_index(stage153)
    noise_models = _noise_model_map(stage153)
    records = []
    for target in stage154.get("recommended_targets", []):
        if not isinstance(target, dict):
            continue
        key = (
            str(target.get("noise_model_id")),
            str(target.get("provider")),
            str(target.get("source_lane_id")),
            str(target.get("circuit_template")),
            "phasewrap",
        )
        phasewrap_metric = metric_records.get(key)
        quantum = _shot_quantum(phasewrap_metric)
        positional_margin = _margin(target, POSITIONAL_COMPARATOR_FIELD)
        control_margin = _margin(target, CONTROL_FIELD)
        positional_quanta = positional_margin / quantum if positional_margin is not None and quantum else None
        control_quanta = control_margin / quantum if control_margin is not None and quantum else None
        noise_model = noise_models.get(str(target.get("noise_model_id")), {})
        stable = bool(
            positional_quanta is not None
            and control_quanta is not None
            and positional_quanta >= MIN_POSITIONAL_QUANTA_FOR_STABLE_TARGET
            and control_quanta >= MIN_CONTROL_QUANTA_FOR_STABLE_TARGET
        )
        records.append(
            {
                "noise_model_id": target.get("noise_model_id"),
                "noise_family": noise_model.get("noise_family") or target.get("noise_family"),
                "provider": target.get("provider"),
                "source_lane_id": target.get("source_lane_id"),
                "circuit_template": target.get("circuit_template"),
                "phasewrap_mean_absolute_score_error": target.get("phasewrap_mean_absolute_score_error"),
                "best_positional_comparator_mean_absolute_score_error": target.get(POSITIONAL_COMPARATOR_FIELD),
                "no_position_control_mean_absolute_score_error": target.get(CONTROL_FIELD),
                "positional_margin": positional_margin,
                "control_margin": control_margin,
                "shot_quantum": quantum,
                "positional_margin_shot_quanta": round(positional_quanta, 6) if positional_quanta is not None else None,
                "control_margin_shot_quanta": round(control_quanta, 6) if control_quanta is not None else None,
                "stable_target": stable,
                "stability_blockers": []
                if stable
                else [
                    item
                    for item, blocked in (
                        ("phasewrap_metric_record_missing", phasewrap_metric is None),
                        ("shot_quantum_missing", quantum is None),
                        (
                            "positional_margin_below_two_shot_quanta",
                            positional_quanta is None or positional_quanta < MIN_POSITIONAL_QUANTA_FOR_STABLE_TARGET,
                        ),
                        (
                            "control_margin_below_two_shot_quanta",
                            control_quanta is None or control_quanta < MIN_CONTROL_QUANTA_FOR_STABLE_TARGET,
                        ),
                    )
                    if blocked
                ],
            }
        )
    return records


def _provider_records(target_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    providers = sorted({str(record.get("provider")) for record in target_records})
    records = []
    for provider in providers:
        provider_targets = [record for record in target_records if record.get("provider") == provider]
        stable_targets = [record for record in provider_targets if record.get("stable_target") is True]
        stable_templates = sorted({str(record.get("circuit_template")) for record in stable_targets})
        stable_noise_models = sorted({str(record.get("noise_model_id")) for record in stable_targets})
        records.append(
            {
                "provider": provider,
                "target_count": len(provider_targets),
                "stable_target_count": len(stable_targets),
                "stable_template_count": len(stable_templates),
                "stable_templates": stable_templates,
                "stable_noise_models": stable_noise_models,
                "hardware_probe_recommended": len(stable_templates) >= MIN_STABLE_TEMPLATES_FOR_PROVIDER_TARGET,
            }
        )
    return records


def run_stage165_margin_stability_audit(
    *,
    stage153_results_path: Path = DEFAULT_STAGE153_RESULTS,
    stage154_results_path: Path = DEFAULT_STAGE154_RESULTS,
) -> dict[str, Any]:
    stage153 = _load_json(stage153_results_path)
    stage154 = _load_json(stage154_results_path)
    sources = [(stage153_results_path, stage153), (stage154_results_path, stage154)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    target_records = _target_records(stage153, stage154) if not missing_sources else []
    stable_targets = [record for record in target_records if record.get("stable_target") is True]
    provider_records = _provider_records(target_records)
    recommended_providers = [record["provider"] for record in provider_records if record["hardware_probe_recommended"] is True]
    if missing_sources:
        decision = "SIMULATED_NOISE_MARGIN_STABILITY_AUDIT_INCOMPLETE"
    elif recommended_providers:
        decision = "SIMULATED_NOISE_STABLE_TARGETED_HARDWARE_PROBE_RECOMMENDED"
    elif stable_targets:
        decision = "SIMULATED_NOISE_STABLE_SINGLE_TEMPLATE_SIGNAL_OBSERVED"
    else:
        decision = "SIMULATED_NOISE_STABLE_HARDWARE_PROBE_NOT_RECOMMENDED_YET"
    return {
        "schema_version": STAGE165_SCHEMA_VERSION,
        "stage": "stage165_simulated_noise_margin_stability_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage153_decision": stage153.get("decision") if isinstance(stage153, dict) else None,
        "stage154_decision": stage154.get("decision") if isinstance(stage154, dict) else None,
        "recommended_target_count": len(target_records),
        "stable_target_count": len(stable_targets),
        "provider_records": provider_records,
        "recommended_hardware_probe_providers": recommended_providers,
        "target_records": target_records,
        "stability_thresholds": {
            "min_positional_margin_shot_quanta": MIN_POSITIONAL_QUANTA_FOR_STABLE_TARGET,
            "min_control_margin_shot_quanta": MIN_CONTROL_QUANTA_FOR_STABLE_TARGET,
            "min_stable_templates_for_provider_target": MIN_STABLE_TEMPLATES_FOR_PROVIDER_TARGET,
        },
        "simulated_only": True,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "simulated-only shot-resolution audit of Stage154 recommended hardware targets",
                "target filtering that requires PhaseWrap's positional and control margins to clear at least two shot quanta",
                "provider-level hardware-probe recommendation only when stable targets appear on both fixed-width templates",
            ],
            "excluded": [
                "real noisy-hardware evidence",
                "IBM credit or provider availability validation",
                "hardware job submission",
                "a publication-ready noisy-hardware robustness or auditability claim",
            ],
        },
        "next_gate": (
            "If the user accepts the stable simulated target, pause before hardware execution to verify IBM credit/provider "
            "state together; otherwise broaden the simulated seed/noise sweep before any live spend."
        ),
    }


def write_stage165_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage153_decision": result["stage153_decision"],
        "stage154_decision": result["stage154_decision"],
        "recommended_target_count": result["recommended_target_count"],
        "stable_target_count": result["stable_target_count"],
        "recommended_hardware_probe_providers": result["recommended_hardware_probe_providers"],
        "stability_thresholds": result["stability_thresholds"],
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
                "provider",
                "source_lane_id",
                "circuit_template",
                "noise_model_id",
                "noise_family",
                "positional_margin",
                "control_margin",
                "shot_quantum",
                "positional_margin_shot_quanta",
                "control_margin_shot_quanta",
                "stable_target",
                "stability_blockers",
            ),
        )
        writer.writeheader()
        for record in result["target_records"]:
            writer.writerow(
                {
                    **{field: record.get(field) for field in writer.fieldnames if field != "stability_blockers"},
                    "stability_blockers": "; ".join(record.get("stability_blockers", [])),
                }
            )
    return paths


def print_stage165_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"recommended_target_count: {result['recommended_target_count']}")
    print(f"stable_target_count: {result['stable_target_count']}")
    print(f"recommended_hardware_probe_providers: {', '.join(result['recommended_hardware_probe_providers'])}")
    print(f"next_gate: {result['next_gate']}")
