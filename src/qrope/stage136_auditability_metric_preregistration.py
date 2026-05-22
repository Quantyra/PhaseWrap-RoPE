from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE136_SCHEMA_VERSION = "qrope_stage136_auditability_metric_preregistration_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE99_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage99_matched_fixed_width_encoding_packets" / "manifest.json"
DEFAULT_STAGE100_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage100_matched_cx_encoding_packets" / "manifest.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage136_auditability_metric_preregistration"
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
REQUIRED_CIRCUIT_TEMPLATES: tuple[str, ...] = (
    "two_ry_product_state_z_readout_v1",
    "two_ry_cx_parity_z_readout_v1",
)
REQUIRED_ROW_FIELDS: tuple[str, ...] = (
    "row_id",
    "source_row_hash",
    "encoding_family",
    "source",
    "delta",
    "components",
    "circuit_parameters",
    "ideal_predictions",
    "row_hash",
)
REQUIRED_COMPONENT_FIELDS: tuple[str, ...] = ("component_a", "component_b")
REQUIRED_CIRCUIT_FIELDS: tuple[str, ...] = ("template", "ry_q0", "ry_q1", "z0_target", "z1_target")
REQUIRED_PACKET_FIELDS: tuple[str, ...] = (
    "packet_id",
    "source_lane_id",
    "encoding_family",
    "provider",
    "row_count",
    "fixed_width",
    "rows",
    "packet_hash",
)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _packet_paths(manifest: dict[str, Any] | None) -> list[Path]:
    if not isinstance(manifest, dict):
        return []
    return [Path(str(path)) for path in manifest.get("packet_paths", [])]


def _missing_fields(payload: dict[str, Any], fields: tuple[str, ...]) -> list[str]:
    return [field for field in fields if field not in payload or payload.get(field) in (None, "", [])]


def _row_audit_record(packet: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    missing = _missing_fields(row, REQUIRED_ROW_FIELDS)
    components = row.get("components", {})
    circuit = row.get("circuit_parameters", {})
    if not isinstance(components, dict):
        missing.append("components")
        component_missing = list(REQUIRED_COMPONENT_FIELDS)
    else:
        component_missing = _missing_fields(components, REQUIRED_COMPONENT_FIELDS)
    if not isinstance(circuit, dict):
        missing.append("circuit_parameters")
        circuit_missing = list(REQUIRED_CIRCUIT_FIELDS)
    else:
        circuit_missing = _missing_fields(circuit, REQUIRED_CIRCUIT_FIELDS)
    missing.extend(f"components.{field}" for field in component_missing)
    missing.extend(f"circuit_parameters.{field}" for field in circuit_missing)
    source = row.get("source", {})
    if not isinstance(source, dict) or "reference_delta" not in source or "candidate_delta" not in source:
        missing.append("source.reference_delta_candidate_delta")
    return {
        "packet_id": packet.get("packet_id"),
        "row_id": row.get("row_id"),
        "encoding_family": packet.get("encoding_family"),
        "source_lane_id": packet.get("source_lane_id"),
        "circuit_template": packet.get("fixed_width", {}).get("circuit_template"),
        "ready": not missing,
        "missing_audit_fields": sorted(set(missing)),
    }


def _packet_audit_record(path: Path) -> dict[str, Any]:
    packet = _load_json(path)
    if not isinstance(packet, dict):
        return {
            "packet_path": str(path.as_posix()),
            "packet_id": None,
            "encoding_family": None,
            "source_lane_id": None,
            "circuit_template": None,
            "row_count": 0,
            "ready_row_count": 0,
            "trace_coverage_fraction": 0.0,
            "ready": False,
            "missing_audit_fields": ["packet_json"],
            "row_records": [],
        }
    packet_missing = _missing_fields(packet, REQUIRED_PACKET_FIELDS)
    fixed_width = packet.get("fixed_width", {})
    if not isinstance(fixed_width, dict):
        packet_missing.append("fixed_width")
        fixed_width = {}
    if fixed_width.get("measured_qubits") != 2:
        packet_missing.append("fixed_width.measured_qubits")
    if fixed_width.get("active_qubits") != 2:
        packet_missing.append("fixed_width.active_qubits")
    if fixed_width.get("readout") != "computational_basis":
        packet_missing.append("fixed_width.readout")
    if fixed_width.get("circuit_template") not in REQUIRED_CIRCUIT_TEMPLATES:
        packet_missing.append("fixed_width.circuit_template")
    rows = packet.get("rows", [])
    if not isinstance(rows, list):
        rows = []
        packet_missing.append("rows")
    row_records = [_row_audit_record(packet, row) for row in rows if isinstance(row, dict)]
    ready_rows = sum(1 for record in row_records if record["ready"])
    row_count = int(packet.get("row_count") or len(rows))
    missing = list(packet_missing)
    if row_count != len(row_records):
        missing.append("row_count_mismatch")
    if ready_rows != row_count:
        missing.append("row_audit_fields_missing")
    trace_coverage = float(ready_rows) / float(row_count) if row_count else 0.0
    return {
        "packet_path": str(path.as_posix()),
        "packet_id": packet.get("packet_id"),
        "encoding_family": packet.get("encoding_family"),
        "source_lane_id": packet.get("source_lane_id"),
        "provider": packet.get("provider"),
        "source_row_set_hash": packet.get("source_row_set_hash"),
        "shot_count": packet.get("shot_count"),
        "circuit_template": packet.get("fixed_width", {}).get("circuit_template"),
        "row_count": row_count,
        "ready_row_count": ready_rows,
        "trace_coverage_fraction": round(trace_coverage, 12),
        "ready": not missing,
        "missing_audit_fields": sorted(set(missing)),
        "row_records": row_records,
    }


def _lane_family_records(packet_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for record in packet_records:
        key = (str(record.get("provider")), str(record.get("source_lane_id")), str(record.get("circuit_template")))
        grouped.setdefault(key, []).append(record)

    records = []
    for (provider, source_lane_id, circuit_template), packets in sorted(grouped.items()):
        families = {str(record.get("encoding_family")) for record in packets}
        complete = all(family in families for family in ENCODING_FAMILIES)
        row_counts = {int(record.get("row_count") or 0) for record in packets}
        shot_counts = {int(record.get("shot_count") or 0) for record in packets}
        row_set_hashes = {str(record.get("source_row_set_hash")) for record in packets}
        missing_families = sorted(set(ENCODING_FAMILIES) - families)
        extra_families = sorted(families - set(ENCODING_FAMILIES))
        row_counts_match = len(row_counts) == 1 and 0 not in row_counts
        shot_counts_match = len(shot_counts) == 1 and 0 not in shot_counts
        row_sets_match = len(row_set_hashes) == 1 and "" not in row_set_hashes and "None" not in row_set_hashes
        all_ready = (
            complete
            and not extra_families
            and len(packets) == len(ENCODING_FAMILIES)
            and row_counts_match
            and shot_counts_match
            and row_sets_match
            and all(record["ready"] for record in packets)
        )
        records.append(
            {
                "provider": provider,
                "source_lane_id": source_lane_id,
                "circuit_template": circuit_template,
                "packet_count": len(packets),
                "family_count": len(families),
                "families_present": sorted(families),
                "missing_encoding_families": missing_families,
                "extra_encoding_families": extra_families,
                "all_families_present": complete,
                "row_counts": sorted(row_counts),
                "shot_counts": sorted(shot_counts),
                "row_set_hashes": sorted(row_set_hashes),
                "row_counts_match": row_counts_match,
                "shot_counts_match": shot_counts_match,
                "row_sets_match": row_sets_match,
                "all_packet_audit_traces_ready": all_ready,
            }
        )
    return records


def run_stage136_preregistration(
    *,
    stage99_manifest_path: Path = DEFAULT_STAGE99_MANIFEST,
    stage100_manifest_path: Path = DEFAULT_STAGE100_MANIFEST,
) -> dict[str, Any]:
    stage99 = _load_json(stage99_manifest_path)
    stage100 = _load_json(stage100_manifest_path)
    sources = [(stage99_manifest_path, stage99), (stage100_manifest_path, stage100)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    packet_paths = _packet_paths(stage99) + _packet_paths(stage100)
    packet_records = [_packet_audit_record(path) for path in packet_paths]
    lane_family_records = _lane_family_records(packet_records)
    ready_packet_count = sum(1 for record in packet_records if record["ready"])
    all_ready = bool(packet_records) and ready_packet_count == len(packet_records) and all(
        record["all_packet_audit_traces_ready"] for record in lane_family_records
    )
    return {
        "schema_version": STAGE136_SCHEMA_VERSION,
        "stage": "stage136_auditability_metric_preregistration",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "AUDITABILITY_METRIC_CONTRACT_READY_HARDWARE_COUNTS_REQUIRED"
            if all_ready and not missing_sources
            else "AUDITABILITY_METRIC_CONTRACT_INCOMPLETE"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "packet_count": len(packet_records),
        "ready_packet_count": ready_packet_count,
        "lane_family_record_count": len(lane_family_records),
        "matched_encoding_families": list(ENCODING_FAMILIES),
        "positional_comparator_families": list(POSITIONAL_COMPARATOR_FAMILIES),
        "required_circuit_templates": list(REQUIRED_CIRCUIT_TEMPLATES),
        "packet_records": packet_records,
        "lane_family_records": lane_family_records,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "metric_specification": {
            "static_trace_metric": (
                "trace_coverage_fraction: fraction of rows with source-row hash, source deltas, two ideal score "
                "components, circuit parameters, ideal score prediction, and row hash present."
            ),
            "hardware_auditability_metric": (
                "component_reconstruction_mean_absolute_error: after Stage 101 calibration, reconstruct component_a "
                "and component_b from the same calibrated observables used by Stage 103 and compute per-row absolute "
                "error against the frozen packet components."
            ),
            "advantage_rule": (
                "PhaseWrap may be described as having an auditability advantage only for a provider, source lane, and "
                "circuit template where trace coverage is complete for every matched family and PhaseWrap's component "
                "reconstruction MAE is lower than every named positional comparator family in the same calibrated "
                "hardware evidence window. The no-position/control family remains a control, not a positional method "
                "that PhaseWrap must beat for an auditability-specific wording."
            ),
            "fixed_width_binding": (
                "Auditability metrics must use the same two measured qubits, same computational-basis readout, same "
                "row set, same circuit template, same shot budget, and same Stage 101 calibration evidence as the "
                "robustness metric gate."
            ),
        },
        "claim_boundary": {
            "supported": [
                "a preregistered auditability metric contract for Stage 99 product-state and Stage 100 CX/parity packets",
                "static trace coverage validation across every matched packet family",
                "provider/lane/template validation of complete fixed-width comparator groups for auditability metrics",
                "a hardware-count-dependent component reconstruction rule that can be evaluated after Stage 113 evidence assembly",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "new provider result records",
                "a current auditability advantage claim",
                "a robustness advantage claim",
            ],
        },
        "next_gate": (
            "After Stage 113 assembles provider counts and Stage 101 calibration passes, compute component reconstruction "
            "MAE per family/window and bind any auditability wording to the preregistered advantage rule."
        ),
    }


def write_stage136_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "packet_count": result["packet_count"],
        "ready_packet_count": result["ready_packet_count"],
        "lane_family_record_count": result["lane_family_record_count"],
        "matched_encoding_families": result["matched_encoding_families"],
        "positional_comparator_families": result["positional_comparator_families"],
        "required_circuit_templates": result["required_circuit_templates"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "secret_values_recorded": result["secret_values_recorded"],
        "metric_specification": result["metric_specification"],
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
                "packet_id",
                "encoding_family",
                "source_lane_id",
                "circuit_template",
                "row_count",
                "ready_row_count",
                "trace_coverage_fraction",
                "ready",
                "missing_audit_fields",
            ),
        )
        writer.writeheader()
        for record in result["packet_records"]:
            writer.writerow(
                {
                    "packet_id": record["packet_id"],
                    "encoding_family": record["encoding_family"],
                    "source_lane_id": record["source_lane_id"],
                    "circuit_template": record["circuit_template"],
                    "row_count": record["row_count"],
                    "ready_row_count": record["ready_row_count"],
                    "trace_coverage_fraction": record["trace_coverage_fraction"],
                    "ready": record["ready"],
                    "missing_audit_fields": "; ".join(record["missing_audit_fields"]),
                }
            )
    return paths


def print_stage136_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"ready_packet_count: {result['ready_packet_count']}/{result['packet_count']}")
    print(f"lane_family_record_count: {result['lane_family_record_count']}")
    print(f"next_gate: {result['next_gate']}")
