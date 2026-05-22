from __future__ import annotations

import csv
import importlib.util
import json
import os
from pathlib import Path
from typing import Any, Callable, Mapping

from qrope.stage153_simulated_noise_rehearsal import (
    DEFAULT_STAGE100_MANIFEST,
    DEFAULT_STAGE99_MANIFEST,
    _comparison_summary,
    _metric_records,
)


STAGE177_SCHEMA_VERSION = "qrope_stage177_ibm_backend_informed_noise_probe_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE159_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage159_first_provider_backend_preflight" / "results.json"
DEFAULT_STAGE169_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage169_targeted_probe_scope_selection" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage177_ibm_backend_informed_noise_probe"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
PRIMARY_MODEL_IDS = {
    "ibm_backend_median_stochastic",
    "ibm_backend_p75_stochastic",
}
LOCKED_PROVIDER = "ibm_runtime"
MIN_MARGIN_SHOT_QUANTA = 2.0


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _module_present(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _env_value(env: Mapping[str, str], *keys: str) -> str:
    for key in keys:
        value = str(env.get(key, "")).strip()
        if value:
            return value
    return ""


def _safe_float(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if result == result else None


def _quantile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = round((len(ordered) - 1) * fraction)
    return ordered[max(0, min(len(ordered) - 1, index))]


def _clamped_probability(value: float | None, *, fallback: float = 0.0) -> float:
    if value is None:
        return fallback
    return max(0.0, min(0.5, float(value)))


def _duration_to_microseconds(value: float) -> float:
    return value * 1_000_000.0 if value < 10.0 else value


def _public_backend_snapshot_from_backend(backend: Any, backend_name: str) -> dict[str, Any]:
    properties_dict: dict[str, Any] = {}
    if hasattr(backend, "properties"):
        properties = backend.properties()
        if hasattr(properties, "to_dict"):
            properties_dict = properties.to_dict()
    status = None
    if hasattr(backend, "status"):
        try:
            status = backend.status()
        except Exception:  # noqa: BLE001 - status is optional read-only metadata.
            status = None
    configuration = None
    if hasattr(backend, "configuration"):
        try:
            configuration = backend.configuration()
        except Exception:  # noqa: BLE001 - configuration is optional read-only metadata.
            configuration = None
    coupling_map = getattr(configuration, "coupling_map", None) or getattr(backend, "coupling_map", None) or []
    return {
        "backend": str(getattr(backend, "name", backend_name)() if callable(getattr(backend, "name", None)) else getattr(backend, "name", backend_name)),
        "num_qubits": getattr(backend, "num_qubits", None) or getattr(configuration, "num_qubits", None),
        "operational": getattr(status, "operational", None) if status is not None else None,
        "pending_jobs": getattr(status, "pending_jobs", None) if status is not None else None,
        "coupling_edge_count": len(list(coupling_map)) if coupling_map else 0,
        "last_update_date": str(properties_dict.get("last_update_date", "")),
        "qubits": properties_dict.get("qubits", []),
        "gates": properties_dict.get("gates", []),
    }


def _lookup_ibm_backend_snapshot(env: Mapping[str, str]) -> dict[str, Any]:
    from qiskit_ibm_runtime import QiskitRuntimeService

    token = _env_value(env, "IBM_QUANTUM_TOKEN", "QISKIT_IBM_TOKEN")
    instance = _env_value(env, "IBM_QUANTUM_INSTANCE_CRN")
    backend_name = _env_value(env, "QROPE_IBM_BACKEND", "IBM_QUANTUM_BACKEND", "QROPE_HARDWARE_BACKEND")
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token, instance=instance)
    backend = service.backend(backend_name)
    return _public_backend_snapshot_from_backend(backend, backend_name)


def _parameter_value(parameters: list[dict[str, Any]], name: str) -> float | None:
    for parameter in parameters:
        if str(parameter.get("name")) == name:
            return _safe_float(parameter.get("value"))
    return None


def _snapshot_stats(snapshot: dict[str, Any]) -> dict[str, Any]:
    readout_errors = []
    t1_us = []
    t2_us = []
    for qubit in snapshot.get("qubits", []):
        if not isinstance(qubit, list):
            continue
        readout = _parameter_value(qubit, "readout_error")
        if readout is not None:
            readout_errors.append(readout)
        t1 = _parameter_value(qubit, "T1")
        t2 = _parameter_value(qubit, "T2")
        if t1 is not None:
            t1_us.append(_duration_to_microseconds(t1))
        if t2 is not None:
            t2_us.append(_duration_to_microseconds(t2))
    gate_errors_by_width: dict[str, list[float]] = {"one_qubit": [], "two_qubit": []}
    gate_errors_by_gate: dict[str, list[float]] = {}
    for gate in snapshot.get("gates", []):
        if not isinstance(gate, dict):
            continue
        gate_name = str(gate.get("gate"))
        if gate_name == "measure":
            continue
        error = _parameter_value(gate.get("parameters", []), "gate_error")
        qubits = gate.get("qubits", [])
        if error is None or not isinstance(qubits, list):
            continue
        width = "two_qubit" if len(qubits) >= 2 else "one_qubit"
        gate_errors_by_width[width].append(error)
        gate_errors_by_gate.setdefault(gate_name, []).append(error)
    return {
        "readout_error_median": _quantile(readout_errors, 0.5),
        "readout_error_p75": _quantile(readout_errors, 0.75),
        "readout_error_count": len(readout_errors),
        "one_qubit_gate_error_median": _quantile(gate_errors_by_width["one_qubit"], 0.5),
        "one_qubit_gate_error_p75": _quantile(gate_errors_by_width["one_qubit"], 0.75),
        "two_qubit_gate_error_median": _quantile(gate_errors_by_width["two_qubit"], 0.5),
        "two_qubit_gate_error_p75": _quantile(gate_errors_by_width["two_qubit"], 0.75),
        "one_qubit_gate_error_count": len(gate_errors_by_width["one_qubit"]),
        "two_qubit_gate_error_count": len(gate_errors_by_width["two_qubit"]),
        "t1_us_median": _quantile(t1_us, 0.5),
        "t2_us_median": _quantile(t2_us, 0.5),
        "gate_error_medians_by_gate": {
            gate: _quantile(values, 0.5) for gate, values in sorted(gate_errors_by_gate.items()) if values
        },
    }


def _noise_models_from_stats(stats: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    readout_median = _clamped_probability(stats.get("readout_error_median"))
    readout_p75 = _clamped_probability(stats.get("readout_error_p75"), fallback=readout_median)
    twoq_median = _clamped_probability(stats.get("two_qubit_gate_error_median"))
    twoq_p75 = _clamped_probability(stats.get("two_qubit_gate_error_p75"), fallback=twoq_median)
    oneq_median = _clamped_probability(stats.get("one_qubit_gate_error_median"))
    coherent_proxy = min(0.05, oneq_median**0.5) if oneq_median > 0 else 0.0
    return (
        {
            "noise_model_id": "ibm_backend_median_stochastic",
            "noise_family": "ibm_backend_properties_stochastic",
            "readout_bitflip_probability": readout_median,
            "depolarizing_observable_shrink": twoq_median,
            "ry_angle_scale_error": 0.0,
            "ry_angle_offset_radians": 0.0,
            "observable_bias_component_a": 0.0,
            "observable_bias_component_b": 0.0,
        },
        {
            "noise_model_id": "ibm_backend_p75_stochastic",
            "noise_family": "ibm_backend_properties_stochastic",
            "readout_bitflip_probability": readout_p75,
            "depolarizing_observable_shrink": twoq_p75,
            "ry_angle_scale_error": 0.0,
            "ry_angle_offset_radians": 0.0,
            "observable_bias_component_a": 0.0,
            "observable_bias_component_b": 0.0,
        },
        {
            "noise_model_id": "ibm_backend_single_qubit_coherent_proxy",
            "noise_family": "ibm_backend_properties_coherent_proxy_not_measured_signed_offset",
            "readout_bitflip_probability": readout_median,
            "depolarizing_observable_shrink": twoq_median,
            "ry_angle_scale_error": coherent_proxy,
            "ry_angle_offset_radians": 0.0,
            "observable_bias_component_a": 0.0,
            "observable_bias_component_b": 0.0,
        },
    )


def _shot_quantum(record: dict[str, Any]) -> float | None:
    shot_counts = record.get("shot_counts")
    if not isinstance(shot_counts, list) or not shot_counts:
        return None
    shots = min(int(value) for value in shot_counts if int(value) > 0)
    return 1.0 / shots if shots > 0 else None


def _enrich_summary(summary: list[dict[str, Any]], metric_records: list[dict[str, Any]], locked_lanes: set[str]) -> list[dict[str, Any]]:
    metric_index = {
        (str(record.get("noise_model_id")), str(record.get("source_lane_id")), str(record.get("circuit_template")), str(record.get("encoding_family"))): record
        for record in metric_records
    }
    enriched = []
    for record in summary:
        phasewrap_metric = metric_index.get(
            (
                str(record.get("noise_model_id")),
                str(record.get("source_lane_id")),
                str(record.get("circuit_template")),
                "phasewrap",
            )
        )
        quantum = _shot_quantum(phasewrap_metric or {})
        phasewrap = record.get("phasewrap_mean_absolute_score_error")
        best_positional = record.get("best_positional_comparator_mean_absolute_score_error")
        control = record.get("no_position_control_mean_absolute_score_error")
        positional_margin = round(float(best_positional) - float(phasewrap), 12) if phasewrap is not None and best_positional is not None else None
        control_margin = round(float(control) - float(phasewrap), 12) if phasewrap is not None and control is not None else None
        positional_quanta = positional_margin / quantum if positional_margin is not None and quantum else None
        control_quanta = control_margin / quantum if control_margin is not None and quantum else None
        stable = bool(
            record.get("phasewrap_beats_all_families_including_control") is True
            and positional_quanta is not None
            and control_quanta is not None
            and positional_quanta >= MIN_MARGIN_SHOT_QUANTA
            and control_quanta >= MIN_MARGIN_SHOT_QUANTA
        )
        enriched.append(
            {
                **record,
                "locked_target_lane": str(record.get("source_lane_id")) in locked_lanes,
                "shot_quantum": quantum,
                "positional_margin": positional_margin,
                "control_margin": control_margin,
                "positional_margin_shot_quanta": round(positional_quanta, 6) if positional_quanta is not None else None,
                "control_margin_shot_quanta": round(control_quanta, 6) if control_quanta is not None else None,
                "stable_strict_target": stable,
                "primary_ibm_properties_model": str(record.get("noise_model_id")) in PRIMARY_MODEL_IDS,
            }
        )
    return enriched


def run_stage177_ibm_backend_informed_noise_probe(
    *,
    stage159_results_path: Path = DEFAULT_STAGE159_RESULTS,
    stage169_results_path: Path = DEFAULT_STAGE169_RESULTS,
    stage99_manifest_path: Path = DEFAULT_STAGE99_MANIFEST,
    stage100_manifest_path: Path = DEFAULT_STAGE100_MANIFEST,
    env: Mapping[str, str] | None = None,
    allow_backend_properties_lookup: bool = False,
    backend_snapshot_lookup: Callable[[Mapping[str, str]], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    environ = os.environ if env is None else env
    stage159 = _load_json(stage159_results_path)
    stage169 = _load_json(stage169_results_path)
    missing_sources = [
        str(path.as_posix())
        for path, payload in ((stage159_results_path, stage159), (stage169_results_path, stage169))
        if not isinstance(payload, dict)
    ]
    blockers = []
    if missing_sources:
        blockers.append("missing_source_artifacts")
    if isinstance(stage159, dict) and stage159.get("decision") != "FIRST_PROVIDER_BACKEND_PREFLIGHT_READY_AWAITING_APPROVAL":
        blockers.append("stage159_backend_preflight_not_ready")
    if isinstance(stage169, dict) and stage169.get("decision") != "TARGETED_IBM_PROBE_SCOPE_LOCKED_TO_STABLE_LANES":
        blockers.append("stage169_target_scope_not_locked")
    if not allow_backend_properties_lookup:
        blockers.append("backend_properties_lookup_not_requested")
    live_lookup_required = backend_snapshot_lookup is None
    if live_lookup_required and not _module_present("qiskit_ibm_runtime"):
        blockers.append("qiskit_ibm_runtime_missing")
    if live_lookup_required and not _env_value(environ, "IBM_QUANTUM_TOKEN", "QISKIT_IBM_TOKEN"):
        blockers.append("ibm_token_missing")
    if live_lookup_required and not _env_value(environ, "IBM_QUANTUM_INSTANCE_CRN"):
        blockers.append("ibm_instance_crn_missing")
    if live_lookup_required and not _env_value(environ, "QROPE_IBM_BACKEND", "IBM_QUANTUM_BACKEND", "QROPE_HARDWARE_BACKEND"):
        blockers.append("ibm_backend_env_missing")

    snapshot: dict[str, Any] = {}
    backend_lookup_error: dict[str, str] | None = None
    if not blockers:
        try:
            snapshot = (backend_snapshot_lookup or _lookup_ibm_backend_snapshot)(environ)
        except Exception as exc:  # noqa: BLE001 - provider failures fail closed without leaking values.
            backend_lookup_error = {"type": type(exc).__name__}
            blockers.append("backend_properties_lookup_failed")

    stats = _snapshot_stats(snapshot) if snapshot and not blockers else {}
    if snapshot and not stats.get("readout_error_count") and not stats.get("two_qubit_gate_error_count"):
        blockers.append("backend_properties_missing_error_rates")

    locked_lanes = set(stage169.get("stable_target_lanes", [])) if isinstance(stage169, dict) else set()
    noise_models = _noise_models_from_stats(stats) if not blockers else ()
    metric_records, missing_packets = _metric_records(
        [Path(path) for path in (_load_json(stage99_manifest_path) or {}).get("packet_paths", [])]
        + [Path(path) for path in (_load_json(stage100_manifest_path) or {}).get("packet_paths", [])],
        noise_models,
    ) if noise_models else ([], [])
    if missing_packets:
        blockers.append("missing_matched_packets")
    comparison_summary = _enrich_summary(_comparison_summary(metric_records), metric_records, locked_lanes) if metric_records else []
    locked_summary = [record for record in comparison_summary if record.get("locked_target_lane") is True]
    primary_stable = [record for record in locked_summary if record.get("primary_ibm_properties_model") is True and record.get("stable_strict_target") is True]
    proxy_stable = [record for record in locked_summary if record.get("primary_ibm_properties_model") is False and record.get("stable_strict_target") is True]
    primary_stable_templates = sorted({str(record.get("circuit_template")) for record in primary_stable})
    proxy_stable_templates = sorted({str(record.get("circuit_template")) for record in proxy_stable})
    if blockers:
        decision = "IBM_BACKEND_INFORMED_NOISE_PROBE_INCOMPLETE"
    elif len(primary_stable_templates) >= 2:
        decision = "IBM_BACKEND_INFORMED_SIM_SUPPORTS_TARGETED_HARDWARE_RUN"
    elif len(proxy_stable_templates) >= 2:
        decision = "IBM_BACKEND_INFORMED_SIM_SUPPORTS_ONLY_COHERENT_PROXY_NOT_HARDWARE_GO"
    else:
        decision = "IBM_BACKEND_INFORMED_SIM_DOES_NOT_SUPPORT_TARGETED_HARDWARE_RUN_YET"

    return {
        "schema_version": STAGE177_SCHEMA_VERSION,
        "stage": "stage177_ibm_backend_informed_noise_probe",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [
            str(stage159_results_path.as_posix()),
            str(stage169_results_path.as_posix()),
            str(stage99_manifest_path.as_posix()),
            str(stage100_manifest_path.as_posix()),
        ],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "backend_properties_lookup_allowed": allow_backend_properties_lookup,
        "backend_properties_lookup_attempted": bool(allow_backend_properties_lookup and not missing_sources),
        "backend_lookup_error": backend_lookup_error,
        "backend_snapshot_summary": {
            "backend": snapshot.get("backend"),
            "num_qubits": snapshot.get("num_qubits"),
            "operational": snapshot.get("operational"),
            "pending_jobs": snapshot.get("pending_jobs"),
            "coupling_edge_count": snapshot.get("coupling_edge_count"),
            "last_update_date": snapshot.get("last_update_date"),
        },
        "backend_property_stats": stats,
        "noise_models": list(noise_models),
        "locked_target_lanes": sorted(locked_lanes),
        "comparison_group_count": len(comparison_summary),
        "locked_comparison_group_count": len(locked_summary),
        "primary_stable_target_count": len(primary_stable),
        "primary_stable_templates": primary_stable_templates,
        "proxy_stable_target_count": len(proxy_stable),
        "proxy_stable_templates": proxy_stable_templates,
        "comparison_summary": comparison_summary,
        "simulated_only": True,
        "ibm_backend_properties_informed": bool(noise_models),
        "no_hardware_submission": True,
        "provider_credentials_required": allow_backend_properties_lookup,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "stability_thresholds": {
            "min_positional_margin_shot_quanta": MIN_MARGIN_SHOT_QUANTA,
            "min_control_margin_shot_quanta": MIN_MARGIN_SHOT_QUANTA,
            "primary_models": sorted(PRIMARY_MODEL_IDS),
        },
        "claim_boundary": {
            "supported": [
                "read-only IBM backend-property-informed simulated rerun over frozen Stage99/Stage100 matched packets",
                "primary decision based on measured backend stochastic properties rather than the hand-built coherent offset screen",
                "explicit separation of measured stochastic models from a non-decisive coherent proxy heuristic",
            ],
            "excluded": [
                "hardware job submission",
                "IBM token, CRN, or account secrets",
                "credit balance or bill verification",
                "a calibrated signed coherent RY offset measurement",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "Use this IBM-informed simulation as the immediate GO/NO-GO input before resolving credit or approving any live "
            "Stage133 IBM execution."
        ),
    }


def write_stage177_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        key: result[key]
        for key in (
            "schema_version",
            "stage",
            "status",
            "objective",
            "decision",
            "source_artifacts",
            "missing_source_artifacts",
            "blockers",
            "backend_properties_lookup_allowed",
            "backend_properties_lookup_attempted",
            "backend_snapshot_summary",
            "backend_property_stats",
            "noise_models",
            "locked_target_lanes",
            "comparison_group_count",
            "locked_comparison_group_count",
            "primary_stable_target_count",
            "primary_stable_templates",
            "proxy_stable_target_count",
            "proxy_stable_templates",
            "simulated_only",
            "ibm_backend_properties_informed",
            "no_hardware_submission",
            "provider_credentials_required",
            "secret_values_recorded",
            "runnable_commands_recorded",
            "stability_thresholds",
            "claim_boundary",
            "next_gate",
        )
    }
    manifest["result_path"] = str((output_dir / "results.json").as_posix())
    manifest["summary_csv_path"] = str((output_dir / "summary.csv").as_posix())
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
                "source_lane_id",
                "circuit_template",
                "locked_target_lane",
                "primary_ibm_properties_model",
                "phasewrap_mean_absolute_score_error",
                "best_positional_comparator_mean_absolute_score_error",
                "no_position_control_mean_absolute_score_error",
                "positional_margin_shot_quanta",
                "control_margin_shot_quanta",
                "stable_strict_target",
            ),
        )
        writer.writeheader()
        for record in result["comparison_summary"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage177_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"backend: {result['backend_snapshot_summary'].get('backend')}")
    print(f"primary_stable_target_count: {result['primary_stable_target_count']}")
    print(f"primary_stable_templates: {', '.join(result['primary_stable_templates'])}")
    print(f"proxy_stable_target_count: {result['proxy_stable_target_count']}")
    print(f"next_gate: {result['next_gate']}")
