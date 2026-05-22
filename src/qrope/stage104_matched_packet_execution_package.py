from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE104_SCHEMA_VERSION = "qrope_stage104_matched_packet_execution_package_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE99_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage99_matched_fixed_width_encoding_packets" / "manifest.json"
DEFAULT_STAGE100_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage100_matched_cx_encoding_packets" / "manifest.json"
DEFAULT_STAGE101_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage101_known_state_calibration_gate" / "results.json"
DEFAULT_STAGE103_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage103_robustness_metric_preregistration" / "manifest.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage104_matched_packet_execution_package"
REQUIRED_EXECUTION_FIELDS: tuple[str, ...] = (
    "job_or_task_ids",
    "backend_metadata",
    "submitted_at_utc",
    "completed_at_utc",
    "raw_counts_by_row",
)
REQUIRED_ENCODING_FAMILIES: tuple[str, ...] = (
    "phasewrap",
    "rope_like",
    "sinusoidal_like",
    "alibi_like",
    "no_position_control",
)
REQUIRED_CIRCUIT_TEMPLATES: tuple[str, ...] = (
    "two_ry_product_state_z_readout_v1",
    "two_ry_cx_parity_z_readout_v1",
)
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _packet_paths(manifest: dict[str, Any] | None) -> list[Path]:
    if not manifest:
        return []
    return [Path(str(path)) for path in manifest.get("packet_paths", [])]


def _packet_contract_issues(packet: dict[str, Any]) -> list[str]:
    issues = []
    family = str(packet.get("encoding_family"))
    if family not in REQUIRED_ENCODING_FAMILIES:
        issues.append("encoding_family_not_required")
    fixed_width = packet.get("fixed_width", {})
    if not isinstance(fixed_width, dict):
        return issues + ["fixed_width_missing"]
    if fixed_width.get("measured_qubits") != 2:
        issues.append("fixed_width_measured_qubits_not_two")
    if fixed_width.get("active_qubits") != 2:
        issues.append("fixed_width_active_qubits_not_two")
    if fixed_width.get("readout") != "computational_basis":
        issues.append("fixed_width_readout_not_computational_basis")
    if fixed_width.get("circuit_template") not in REQUIRED_CIRCUIT_TEMPLATES:
        issues.append("fixed_width_circuit_template_not_required")
    return sorted(set(issues))


def _matched_group_records(packets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for packet in packets:
        key = (
            str(packet.get("provider")),
            str(packet.get("source_lane_id")),
            str(packet.get("fixed_width", {}).get("circuit_template")),
        )
        grouped.setdefault(key, []).append(packet)

    records = []
    required = set(REQUIRED_ENCODING_FAMILIES)
    for (provider, source_lane_id, circuit_template), group in sorted(grouped.items()):
        families = {str(packet.get("encoding_family")) for packet in group}
        row_counts = {int(packet.get("row_count") or len(packet.get("rows", []))) for packet in group}
        shot_counts = {int(packet.get("shot_count") or 0) for packet in group}
        row_set_hashes = {str(packet.get("source_row_set_hash")) for packet in group}
        packet_issues = {
            str(packet.get("packet_id")): _packet_contract_issues(packet)
            for packet in group
            if _packet_contract_issues(packet)
        }
        missing_families = sorted(required - families)
        extra_families = sorted(families - required)
        row_counts_match = len(row_counts) == 1 and 0 not in row_counts
        shot_counts_match = len(shot_counts) == 1 and 0 not in shot_counts
        row_sets_match = len(row_set_hashes) == 1 and "" not in row_set_hashes and "None" not in row_set_hashes
        ready = (
            not missing_families
            and not extra_families
            and len(group) == len(REQUIRED_ENCODING_FAMILIES)
            and row_counts_match
            and shot_counts_match
            and row_sets_match
            and not packet_issues
        )
        records.append(
            {
                "provider": provider,
                "source_lane_id": source_lane_id,
                "circuit_template": circuit_template,
                "packet_count": len(group),
                "required_family_count": len(REQUIRED_ENCODING_FAMILIES),
                "observed_encoding_families": sorted(families),
                "missing_encoding_families": missing_families,
                "extra_encoding_families": extra_families,
                "row_counts": sorted(row_counts),
                "shot_counts": sorted(shot_counts),
                "row_set_hashes": sorted(row_set_hashes),
                "row_counts_match": row_counts_match,
                "shot_counts_match": shot_counts_match,
                "row_sets_match": row_sets_match,
                "packet_contract_issues": packet_issues,
                "ready": ready,
            }
        )
    return records


def _row_program(row: dict[str, Any], template: str) -> str:
    if row.get("openqasm3"):
        return str(row["openqasm3"])
    params = row["circuit_parameters"]
    lines = [
        "OPENQASM 3.0;",
        "qubit[2] q;",
        "bit[2] c;",
        f"ry({params['ry_q0']}) q[0];",
        f"ry({params['ry_q1']}) q[1];",
    ]
    if template == "two_ry_cx_parity_z_readout_v1":
        lines.append("cnot q[0], q[1];")
    lines.extend(
        [
            "c[0] = measure q[0];",
            "c[1] = measure q[1];",
            "",
        ]
    )
    return "\n".join(lines)


def build_packet_execution_template(packet: dict[str, Any]) -> dict[str, Any]:
    template = str(packet["fixed_width"]["circuit_template"])
    return {
        "schema_version": STAGE104_SCHEMA_VERSION,
        "packet_id": packet["packet_id"],
        "packet_hash": packet.get("packet_hash"),
        "source_lane_id": packet.get("source_lane_id"),
        "provider": packet.get("provider"),
        "backend": packet.get("backend"),
        "encoding_family": packet.get("encoding_family"),
        "circuit_template": template,
        "status": "template_counts_required",
        "no_hardware_submission": True,
        "instructions": (
            "Replace placeholders with real calibrated provider/backend/date execution evidence after Stage 101 passes. "
            "Counts must use canonical q0q1 keys."
        ),
        "job_or_task_ids": [],
        "backend_metadata": {
            "backend": "",
            "provider": packet.get("provider"),
            "calibration_timestamp_utc": "",
            "stage101_result_path": "",
            "additional_metadata": {},
        },
        "submitted_at_utc": "",
        "completed_at_utc": "",
        "shot_count": packet.get("shot_count"),
        "raw_counts_by_row": [
            {
                "row_id": row["row_id"],
                "ideal_score": row["ideal_predictions"]["score"],
                "counts": {},
                "openqasm3": _row_program(row, template),
            }
            for row in packet.get("rows", [])
        ],
        "required_execution_fields": list(REQUIRED_EXECUTION_FIELDS),
    }


def _template_missing_fields(template: dict[str, Any]) -> list[str]:
    missing = []
    for field in REQUIRED_EXECUTION_FIELDS:
        value = template.get(field)
        if value in (None, "", [], {}):
            missing.append(field)
    backend_metadata = template.get("backend_metadata", {})
    if (
        isinstance(backend_metadata, dict)
        and (
            not backend_metadata.get("backend")
            or not backend_metadata.get("calibration_timestamp_utc")
            or not backend_metadata.get("stage101_result_path")
        )
        and "backend_metadata" not in missing
    ):
        missing.append("backend_metadata")
    if template.get("raw_counts_by_row"):
        empty_counts = [str(item.get("row_id")) for item in template["raw_counts_by_row"] if not item.get("counts")]
        if empty_counts and "raw_counts_by_row" not in missing:
            missing.append("raw_counts_by_row")
    return missing


def run_stage104_package(
    *,
    stage99_manifest_path: Path = DEFAULT_STAGE99_MANIFEST,
    stage100_manifest_path: Path = DEFAULT_STAGE100_MANIFEST,
    stage101_results_path: Path = DEFAULT_STAGE101_RESULTS,
    stage103_manifest_path: Path = DEFAULT_STAGE103_MANIFEST,
) -> dict[str, Any]:
    stage99 = _load_json(stage99_manifest_path)
    stage100 = _load_json(stage100_manifest_path)
    stage101 = _load_json(stage101_results_path)
    stage103 = _load_json(stage103_manifest_path)
    sources = [
        (stage99_manifest_path, stage99),
        (stage100_manifest_path, stage100),
        (stage101_results_path, stage101),
        (stage103_manifest_path, stage103),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    packets: list[dict[str, Any]] = []
    missing_packets: list[str] = []
    for packet_path in _packet_paths(stage99) + _packet_paths(stage100):
        packet = _load_json(packet_path)
        if packet is None:
            missing_packets.append(str(packet_path.as_posix()))
            continue
        packets.append(packet)
    templates = [build_packet_execution_template(packet) for packet in packets]
    matched_group_records = _matched_group_records(packets)
    expected_group_count = 4
    complete_matched_groups = (
        len(matched_group_records) == expected_group_count
        and all(record["ready"] for record in matched_group_records)
    )
    evidence_records = [
        {
            "packet_id": template["packet_id"],
            "provider": template["provider"],
            "source_lane_id": template["source_lane_id"],
            "encoding_family": template["encoding_family"],
            "circuit_template": template["circuit_template"],
            "template_file": f"{template['packet_id']}.json",
            "row_count": len(template["raw_counts_by_row"]),
            "shot_count": template["shot_count"],
            "missing_evidence": _template_missing_fields(template),
            "ready_for_stage103": False,
        }
        for template in templates
    ]
    expected_packet_count = 20
    complete_templates = (
        len(templates) == expected_packet_count
        and complete_matched_groups
        and not missing_sources
        and not missing_packets
    )
    stage101_pass = bool(stage101 and stage101.get("known_state_calibration_pass") is True)
    return {
        "schema_version": STAGE104_SCHEMA_VERSION,
        "stage": "stage104_matched_packet_execution_package",
        "status": "completed" if complete_templates else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "MATCHED_PACKET_EXECUTION_TEMPLATES_PREPARED_CALIBRATION_AND_COUNTS_REQUIRED"
            if complete_templates
            else "MATCHED_PACKET_EXECUTION_TEMPLATE_PACKAGE_INCOMPLETE"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "missing_packet_artifacts": missing_packets,
        "stage101_known_state_calibration_pass": stage101_pass,
        "stage103_decision": stage103.get("decision") if stage103 else None,
        "expected_packet_count": expected_packet_count,
        "expected_matched_group_count": expected_group_count,
        "template_count": len(templates),
        "matched_group_count": len(matched_group_records),
        "complete_matched_group_count": sum(1 for record in matched_group_records if record["ready"]),
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "required_execution_fields": list(REQUIRED_EXECUTION_FIELDS),
        "required_encoding_families": list(REQUIRED_ENCODING_FAMILIES),
        "required_circuit_templates": list(REQUIRED_CIRCUIT_TEMPLATES),
        "matched_group_records": matched_group_records,
        "templates": templates,
        "evidence_records": evidence_records,
        "all_or_none_interpretation_rule": (
            "Stage 103 interpretation requires Stage 101 calibration pass and canonical q0q1 raw_counts_by_row files "
            "for every Stage 99 and Stage 100 matched packet, with complete PhaseWrap/RoPE-like/sinusoidal-like/"
            "ALIBI-like/no-position groups under each provider, source lane, and circuit template."
        ),
        "claim_boundary": {
            "supported": [
                "per-packet execution JSON templates for all matched Stage 99 and Stage 100 packets",
                "validation that each provider/lane/template group contains the full fixed-width comparator family set",
                "a complete handoff contract for calibrated raw_counts_by_row evidence",
                "an all-or-none interpretation guard for the matched fixed-width hardware comparison",
            ],
            "excluded": [
                "real matched packet hardware counts",
                "completed Stage 101 calibration",
                "a noisy-hardware robustness result",
                "a PhaseWrap advantage claim",
            ],
        },
        "next_gate": (
            "After Stage 101 calibration passes, execute all Stage 99 and Stage 100 matched packets, fill every Stage 104 "
            "template with canonical q0q1 row counts and metadata, then rerun Stage 103 with --execution-dir."
        ),
    }


def write_stage104_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    template_dir = output_dir / "packet_execution_templates"
    template_dir.mkdir(parents=True, exist_ok=True)
    template_paths: list[str] = []
    for template in result["templates"]:
        path = template_dir / f"{template['packet_id']}.json"
        path.write_text(json.dumps(template, indent=2, sort_keys=True), encoding="utf-8")
        template_paths.append(str(path.as_posix()))
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "missing_packet_artifacts": result["missing_packet_artifacts"],
        "stage101_known_state_calibration_pass": result["stage101_known_state_calibration_pass"],
        "stage103_decision": result["stage103_decision"],
        "expected_packet_count": result["expected_packet_count"],
        "expected_matched_group_count": result["expected_matched_group_count"],
        "template_count": result["template_count"],
        "matched_group_count": result["matched_group_count"],
        "complete_matched_group_count": result["complete_matched_group_count"],
        "template_paths": template_paths,
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "required_encoding_families": result["required_encoding_families"],
        "required_circuit_templates": result["required_circuit_templates"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "all_or_none_interpretation_rule": result["all_or_none_interpretation_rule"],
        "claim_boundary": result["claim_boundary"],
        "next_gate": result["next_gate"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "template_dir": str(template_dir),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "packet_id",
                "provider",
                "source_lane_id",
                "encoding_family",
                "circuit_template",
                "template_file",
                "row_count",
                "shot_count",
                "missing_evidence",
                "ready_for_stage103",
            ),
        )
        writer.writeheader()
        for record in result["evidence_records"]:
            writer.writerow({**record, "missing_evidence": "; ".join(record["missing_evidence"])})
    return paths


def print_stage104_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"template_count: {result['template_count']}")
    print(f"stage101_known_state_calibration_pass: {result['stage101_known_state_calibration_pass']}")
    print(f"next_gate: {result['next_gate']}")
