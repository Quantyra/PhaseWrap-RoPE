from __future__ import annotations

import csv
import json
import math
import re
import tempfile
from pathlib import Path
from typing import Any

from qrope.stage100_matched_cx_encoding_packet_freezer import (
    DEFAULT_SOURCE_PACKET_FILES as CX_SOURCE_PACKET_FILES,
    _openqasm3,
)
from qrope.stage153_simulated_noise_rehearsal import _comparison_summary, _metric_records
from qrope.stage177_ibm_backend_informed_noise_probe import (
    DEFAULT_OUTPUT_DIR as STAGE177_OUTPUT_DIR,
    MIN_MARGIN_SHOT_QUANTA,
    PRIMARY_MODEL_IDS,
    _enrich_summary,
)
from qrope.stage181_fixed_width_target_redesign_plan import DEFAULT_OUTPUT_DIR as STAGE181_OUTPUT_DIR
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import (
    DEFAULT_SOURCE_PACKET_DIR,
    DEFAULT_SOURCE_PACKET_FILES as PRODUCT_SOURCE_PACKET_FILES,
    ENCODING_FAMILIES,
    OBJECTIVE,
    SourceLane,
    _clamp,
    _load_source_lanes,
    _max_abs_delta,
    _round_float,
    _row_delta,
    _source_packet_paths,
    _stable_hash,
)


STAGE184_SCHEMA_VERSION = "qrope_stage184_error_orthogonalized_components_candidate_screen_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE177_RESULTS = STAGE177_OUTPUT_DIR / "results.json"
DEFAULT_STAGE181_RESULTS = STAGE181_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage184_error_orthogonalized_components_candidate_screen"
DESIGN_FAMILY_ID = "pw_error_orthogonalized_components_v1"
STAGE181_READY = "FIXED_WIDTH_TARGET_REDESIGN_PLAN_READY"
SOURCE_LANE_RE = re.compile(r"^(?P<provider>.+?)_(?P<template>product|cx)_seed(?P<seed>\d+)_")
PRODUCT_TEMPLATE = "two_ry_product_state_z_readout_v1"
CX_TEMPLATE = "two_ry_cx_parity_z_readout_v1"
MIN_STABLE_TEMPLATE_COUNT = 2
MIN_INDEPENDENT_SEEDS = 2


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _primary_noise_models(stage177: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(
        model
        for model in stage177.get("noise_models", [])
        if isinstance(model, dict) and str(model.get("noise_model_id")) in PRIMARY_MODEL_IDS
    )


def _normalized_delta(delta: float, max_abs_delta: float) -> float:
    return _clamp(delta / max(1.0, max_abs_delta), -1.0, 1.0)


def _orthogonalized_components_for_family(family: str, delta: float, max_abs_delta: float) -> tuple[float, float]:
    normalized = _normalized_delta(delta, max_abs_delta)
    phase = math.pi * normalized
    if family == "phasewrap":
        raw_a = math.sin(phase)
        raw_b = math.cos(0.5 * phase) - (2.0 / math.pi)
        scale = max(1.0, abs(raw_a), abs(raw_b))
        return _clamp(raw_a / scale), _clamp(raw_b / scale)
    if family == "rope_like":
        raw_a = math.cos(0.5 * phase) - (2.0 / math.pi)
        raw_b = math.cos(0.25 * phase) - 0.9
        scale = max(1.0, abs(raw_a), abs(raw_b))
        return _clamp(raw_a / scale), _clamp(raw_b / scale)
    if family == "sinusoidal_like":
        raw_a = math.sin(2.0 * phase)
        raw_b = math.cos(phase)
        scale = max(1.0, abs(raw_a), abs(raw_b))
        return _clamp(raw_a / scale), _clamp(raw_b / scale)
    if family == "alibi_like":
        raw_a = 1.0 - 2.0 * abs(normalized)
        raw_b = normalized
        scale = max(1.0, abs(raw_a), abs(raw_b))
        return _clamp(raw_a / scale), _clamp(raw_b / scale)
    if family == "no_position_control":
        return 0.0, 0.0
    raise ValueError(f"Unknown encoding family: {family}")


def _candidate_row(source_row: dict[str, Any], family: str, max_abs_delta: float, circuit_template: str) -> dict[str, Any]:
    delta = _row_delta(source_row)
    component_a, component_b = _orthogonalized_components_for_family(family, delta, max_abs_delta)
    ry_q0 = math.acos(_clamp(component_a))
    ry_q1 = math.acos(_clamp(component_b))
    target_score = _clamp(0.5 + 0.25 * (component_a + component_b), 0.0, 1.0)
    observable = "0.5 + 0.25 * (E[Z0] + E[Z1])"
    readout_note = None
    circuit_parameters = {
        "template": circuit_template,
        "ry_q0": _round_float(ry_q0),
        "ry_q1": _round_float(ry_q1),
        "z0_target": _round_float(component_a),
        "z1_target": _round_float(component_b),
    }
    if circuit_template == CX_TEMPLATE:
        observable = "0.5 + 0.25 * (E[Z0 after CX] + E[Z0 Z1 after CX])"
        readout_note = "Under ideal CNOT readout, E[Z0 after CX] recovers component_a and E[Z0 Z1 after CX] recovers component_b."
        circuit_parameters["entangling_gate"] = "cx q0->q1"
    row_core: dict[str, Any] = {
        "row_id": source_row["row_id"],
        "source_row_hash": source_row.get("row_hash"),
        "encoding_family": family,
        "design_family_id": DESIGN_FAMILY_ID,
        "source": source_row.get("source", {}),
        "delta": _round_float(delta),
        "normalized_delta": _round_float(_normalized_delta(delta, max_abs_delta)),
        "components": {
            "component_a": _round_float(component_a),
            "component_b": _round_float(component_b),
        },
        "circuit_parameters": circuit_parameters,
        "ideal_predictions": {
            "score": _round_float(target_score),
            "observable": observable,
        },
    }
    if readout_note:
        row_core["ideal_predictions"]["readout_note"] = readout_note
    row = {**row_core, "row_hash": _stable_hash(row_core)}
    if circuit_template == CX_TEMPLATE:
        row["openqasm3"] = _openqasm3(row)
    return row


def _packet_for_lane_family(lane: SourceLane, family: str, circuit_template: str) -> dict[str, Any]:
    rows = list(lane.payload.get("rows", []))
    max_delta = _max_abs_delta(rows)
    matched_rows = [_candidate_row(row, family, max_delta, circuit_template) for row in rows]
    entangling_gate = "cx q0->q1" if circuit_template == CX_TEMPLATE else None
    score_observable = (
        "0.5 + 0.25 * (E[Z0 after CX] + E[Z0 Z1 after CX])"
        if circuit_template == CX_TEMPLATE
        else "0.5 + 0.25 * (E[Z0] + E[Z1])"
    )
    packet_core = {
        "schema_version": STAGE184_SCHEMA_VERSION,
        "packet_version": "qrope_stage184_error_orthogonalized_components_candidate_packet_v1",
        "packet_id": f"{lane.lane_id}__{DESIGN_FAMILY_ID}__{family}",
        "source_stage": "stage4_preregistered_replication_packets",
        "source_packet_path": str(lane.path.as_posix()),
        "source_lane_id": lane.lane_id,
        "source_row_set_hash": lane.payload.get("preregistration", {}).get("row_set_hash"),
        "design_family_id": DESIGN_FAMILY_ID,
        "encoding_family": family,
        "provider": lane.payload.get("provider"),
        "backend": lane.payload.get("backend"),
        "row_count": len(matched_rows),
        "shot_count": lane.payload.get("config", {}).get("shot_count", lane.payload.get("shot_count")),
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "execution_status": "not_submitted",
        "fixed_width": {
            "measured_qubits": 2,
            "active_qubits": 2,
            "readout": "computational_basis",
            "circuit_template": circuit_template,
            "entangling_gate": entangling_gate,
            "score_observable": score_observable,
        },
        "matching_policy": {
            "row_set": "identical source rows across all encoding families within each redesigned lane",
            "qubit_count": "fixed at two measured qubits",
            "component_transform": "zero-centered component-basis rotation intended to reduce alignment with symmetric shrink/readout",
            "control_policy": "no-position control remains the preregistered zero-component control",
            "hardware_scope": "simulated candidate screen only; not hardware evidence",
        },
        "claim_boundary": (
            "Error-orthogonalized components candidate packet for simulated IBM-informed screening only; "
            "not a hardware robustness result."
        ),
        "rows": matched_rows,
    }
    return {**packet_core, "packet_hash": _stable_hash(packet_core)}


def _candidate_packets(source_packet_dir: Path, product_files: tuple[str, ...], cx_files: tuple[str, ...]) -> tuple[list[dict[str, Any]], list[str]]:
    product_lanes, missing_product = _load_source_lanes(_source_packet_paths(source_packet_dir, product_files))
    cx_lanes, missing_cx = _load_source_lanes(_source_packet_paths(source_packet_dir, cx_files))
    packets: list[dict[str, Any]] = []
    for lane in product_lanes:
        for family in ENCODING_FAMILIES:
            packets.append(_packet_for_lane_family(lane, family, PRODUCT_TEMPLATE))
    for lane in cx_lanes:
        for family in ENCODING_FAMILIES:
            packets.append(_packet_for_lane_family(lane, family, CX_TEMPLATE))
    return packets, missing_product + missing_cx


def _lane_parts(source_lane_id: str, provider: str) -> dict[str, str]:
    match = SOURCE_LANE_RE.match(source_lane_id)
    if not match:
        return {"provider_family": provider, "template_kind": "", "seed": ""}
    return {
        "provider_family": match.group("provider"),
        "template_kind": match.group("template"),
        "seed": match.group("seed"),
    }


def _candidate_records(comparison_summary: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for record in comparison_summary:
        lane = _lane_parts(str(record.get("source_lane_id")), str(record.get("provider")))
        key = (str(record.get("noise_model_id")), lane["provider_family"], lane["seed"])
        groups.setdefault(key, []).append({**record, **lane})

    records = []
    for (noise_model_id, provider_family, seed), group in sorted(groups.items()):
        stable = [record for record in group if record.get("stable_strict_target") is True]
        stable_templates = sorted({str(record.get("circuit_template")) for record in stable})
        records.append(
            {
                "noise_model_id": noise_model_id,
                "provider_family": provider_family,
                "seed": seed,
                "comparison_group_count": len(group),
                "stable_target_count": len(stable),
                "stable_template_count": len(stable_templates),
                "stable_templates": stable_templates,
                "stable_lanes": sorted({str(record.get("source_lane_id")) for record in stable}),
                "min_positional_margin_shot_quanta": min(
                    (
                        float(record.get("positional_margin_shot_quanta"))
                        for record in group
                        if record.get("positional_margin_shot_quanta") is not None
                    ),
                    default=None,
                ),
                "min_control_margin_shot_quanta": min(
                    (
                        float(record.get("control_margin_shot_quanta"))
                        for record in group
                        if record.get("control_margin_shot_quanta") is not None
                    ),
                    default=None,
                ),
                "reopen_candidate": len(stable_templates) >= MIN_STABLE_TEMPLATE_COUNT,
            }
        )
    return records


def _reopen_summary(candidate_records: list[dict[str, Any]], primary_noise_model_ids: list[str]) -> dict[str, Any]:
    passing = [record for record in candidate_records if record.get("reopen_candidate") is True]
    seeds_by_model = {
        model_id: sorted(
            {
                f"{record.get('provider_family')}:{record.get('seed')}"
                for record in passing
                if record.get("noise_model_id") == model_id and record.get("seed")
            }
        )
        for model_id in primary_noise_model_ids
    }
    passing_models = [model_id for model_id, seeds in seeds_by_model.items() if len(seeds) >= MIN_INDEPENDENT_SEEDS]
    return {
        "reopen_candidate_count": len(passing),
        "passing_noise_model_count": len(passing_models),
        "passing_noise_models": passing_models,
        "passing_seed_pairs_by_noise_model": seeds_by_model,
        "supports_hardware_reopen": len(passing_models) == len(primary_noise_model_ids) and bool(primary_noise_model_ids),
    }


def run_stage184_error_orthogonalized_components_candidate_screen(
    *,
    stage177_results_path: Path = DEFAULT_STAGE177_RESULTS,
    stage181_results_path: Path = DEFAULT_STAGE181_RESULTS,
    source_packet_dir: Path = DEFAULT_SOURCE_PACKET_DIR,
    product_source_packet_files: tuple[str, ...] = PRODUCT_SOURCE_PACKET_FILES,
    cx_source_packet_files: tuple[str, ...] = CX_SOURCE_PACKET_FILES,
) -> dict[str, Any]:
    stage177 = _load_json(stage177_results_path)
    stage181 = _load_json(stage181_results_path)
    sources = [(stage177_results_path, stage177), (stage181_results_path, stage181)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    blockers = []
    if missing_sources:
        blockers.append("missing_source_artifacts")
    if isinstance(stage181, dict) and stage181.get("decision") != STAGE181_READY:
        blockers.append("stage181_redesign_plan_not_ready")
    if isinstance(stage181, dict):
        family_ids = {str(family.get("family_id")) for family in stage181.get("design_families", []) if isinstance(family, dict)}
        if DESIGN_FAMILY_ID not in family_ids:
            blockers.append("stage181_error_orthogonalized_components_family_missing")
    noise_models = _primary_noise_models(stage177) if isinstance(stage177, dict) else ()
    if not noise_models:
        blockers.append("stage177_primary_models_missing")

    packets, missing_source_packets = _candidate_packets(source_packet_dir, product_source_packet_files, cx_source_packet_files)
    if missing_source_packets:
        blockers.append("missing_source_packets")
    expected_packet_count = (len(product_source_packet_files) + len(cx_source_packet_files)) * len(ENCODING_FAMILIES)
    if len(packets) != expected_packet_count:
        blockers.append("candidate_packet_generation_incomplete")

    metric_records: list[dict[str, Any]] = []
    missing_packets: list[dict[str, Any]] = []
    comparison_summary: list[dict[str, Any]] = []
    candidate_records: list[dict[str, Any]] = []
    reopen = {
        "reopen_candidate_count": 0,
        "passing_noise_model_count": 0,
        "passing_noise_models": [],
        "passing_seed_pairs_by_noise_model": {},
        "supports_hardware_reopen": False,
    }
    if not blockers:
        with tempfile.TemporaryDirectory(prefix="qrope_stage184_packets_") as temp_dir:
            packet_paths = _write_packets_for_metrics(packets, Path(temp_dir))
            metric_records, missing_packets = _metric_records(packet_paths, noise_models)
        if missing_packets:
            blockers.append("missing_candidate_packets")
        comparison_summary = _enrich_summary(_comparison_summary(metric_records), metric_records, set()) if metric_records else []
        candidate_records = _candidate_records(comparison_summary)
        reopen = _reopen_summary(candidate_records, [str(model["noise_model_id"]) for model in noise_models])

    if blockers:
        decision = "ERROR_ORTHOGONALIZED_COMPONENTS_CANDIDATE_SCREEN_INCOMPLETE"
    elif reopen["supports_hardware_reopen"]:
        decision = "ERROR_ORTHOGONALIZED_COMPONENTS_CANDIDATE_SUPPORTS_HARDWARE_REOPEN"
    else:
        decision = "ERROR_ORTHOGONALIZED_COMPONENTS_CANDIDATE_DOES_NOT_SUPPORT_HARDWARE_REOPEN"

    return {
        "schema_version": STAGE184_SCHEMA_VERSION,
        "stage": "stage184_error_orthogonalized_components_candidate_screen",
        "status": "completed" if not missing_sources and not blockers else "incomplete" if blockers else "completed",
        "objective": OBJECTIVE,
        "decision": decision,
        "design_family_id": DESIGN_FAMILY_ID,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "source_packet_dir": str(source_packet_dir.as_posix()),
        "missing_source_packets": missing_source_packets,
        "blockers": sorted(set(blockers)),
        "primary_noise_model_ids": [str(model["noise_model_id"]) for model in noise_models],
        "packet_count": len(packets),
        "expected_packet_count": expected_packet_count,
        "metric_record_count": len(metric_records),
        "comparison_group_count": len(comparison_summary),
        "candidate_group_count": len(candidate_records),
        "reopen_candidate_count": reopen["reopen_candidate_count"],
        "passing_noise_model_count": reopen["passing_noise_model_count"],
        "passing_noise_models": reopen["passing_noise_models"],
        "passing_seed_pairs_by_noise_model": reopen["passing_seed_pairs_by_noise_model"],
        "candidate_records": candidate_records,
        "comparison_summary": comparison_summary,
        "metric_records": metric_records,
        "packets": packets,
        "simulated_only": True,
        "ibm_backend_properties_informed": bool(noise_models),
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "hardware_path_status": "current_ibm_328_job_run_remains_archived",
        "stability_thresholds": {
            "min_positional_margin_shot_quanta": MIN_MARGIN_SHOT_QUANTA,
            "min_control_margin_shot_quanta": MIN_MARGIN_SHOT_QUANTA,
            "min_stable_template_count_for_reopen": MIN_STABLE_TEMPLATE_COUNT,
            "min_independent_seed_pairs": MIN_INDEPENDENT_SEEDS,
            "primary_models": sorted(PRIMARY_MODEL_IDS),
        },
        "claim_boundary": {
            "supported": [
                "simulated-only third redesign screen for the Stage181 error-orthogonalized components family",
                "fixed-width product and CX packet generation over matched real-source rows",
                "GO/NO-GO evidence for whether this first redesign can reopen the hardware path",
            ],
            "excluded": [
                "hardware job submission",
                "IBM token, CRN, account, or credit-balance verification",
                "a noisy-hardware robustness or auditability conclusion",
                "a claim that all Stage181 redesign families have failed",
            ],
        },
        "next_gate": (
            "If this candidate fails, test the next Stage181 redesign family or revise the preregistered control/target semantics "
            "before considering any IBM hardware reopen."
        ),
    }


def _write_packets_for_metrics(packets: list[dict[str, Any]], temp_dir: Path) -> list[Path]:
    temp_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for packet in packets:
        path = temp_dir / f"{packet['packet_id']}.json"
        path.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
        paths.append(path)
    return paths


def write_stage184_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    packet_dir = output_dir / "packets"
    packet_dir.mkdir(parents=True, exist_ok=True)
    packet_paths = []
    for packet in result["packets"]:
        path = packet_dir / f"{packet['packet_id']}.json"
        path.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
        packet_paths.append(str(path.as_posix()))

    manifest_keys = (
        "schema_version",
        "stage",
        "status",
        "objective",
        "decision",
        "design_family_id",
        "source_artifacts",
        "missing_source_artifacts",
        "source_packet_dir",
        "missing_source_packets",
        "blockers",
        "primary_noise_model_ids",
        "packet_count",
        "expected_packet_count",
        "metric_record_count",
        "comparison_group_count",
        "candidate_group_count",
        "reopen_candidate_count",
        "passing_noise_model_count",
        "passing_noise_models",
        "passing_seed_pairs_by_noise_model",
        "simulated_only",
        "ibm_backend_properties_informed",
        "no_hardware_submission",
        "provider_credentials_required",
        "secret_values_recorded",
        "runnable_commands_recorded",
        "hardware_path_status",
        "stability_thresholds",
        "claim_boundary",
        "next_gate",
    )
    manifest = {key: result[key] for key in manifest_keys}
    manifest["packet_paths"] = packet_paths
    manifest["result_path"] = str((output_dir / "results.json").as_posix())
    manifest["summary_csv_path"] = str((output_dir / "summary.csv").as_posix())
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "packet_dir": str(packet_dir),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "noise_model_id",
                "provider_family",
                "seed",
                "comparison_group_count",
                "stable_target_count",
                "stable_template_count",
                "min_positional_margin_shot_quanta",
                "min_control_margin_shot_quanta",
                "reopen_candidate",
            ),
        )
        writer.writeheader()
        for record in result["candidate_records"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage184_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"packet_count: {result['packet_count']}")
    print(f"comparison_group_count: {result['comparison_group_count']}")
    print(f"reopen_candidate_count: {result['reopen_candidate_count']}")
    print(f"next_gate: {result['next_gate']}")
