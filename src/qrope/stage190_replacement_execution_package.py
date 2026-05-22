from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from qrope.stage189_replacement_hardware_readiness_review import DEFAULT_OUTPUT_DIR as STAGE189_OUTPUT_DIR
from qrope.stage188_replacement_semantics_packet_screen import DEFAULT_OUTPUT_DIR as STAGE188_OUTPUT_DIR
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE190_SCHEMA_VERSION = "qrope_stage190_replacement_execution_package_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE188_RESULTS = STAGE188_OUTPUT_DIR / "results.json"
DEFAULT_STAGE189_RESULTS = STAGE189_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage190_replacement_execution_package"
STAGE189_REOPENED = "REPLACEMENT_HARDWARE_REVIEW_REOPENED_BUT_NOT_READY_FOR_LIVE_RUN"
REQUIRED_ENCODING_FAMILIES: tuple[str, ...] = (
    "phasewrap",
    "rope_like",
    "sinusoidal_like",
    "alibi_like",
    "matched_nonzero_null_control",
)
REQUIRED_CIRCUIT_TEMPLATES: tuple[str, ...] = (
    "two_ry_product_state_z_readout_v1",
    "two_ry_cx_parity_z_readout_v1",
)
CALIBRATION_STATES: tuple[str, ...] = ("00", "01", "10", "11")


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


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
    lines.extend(["c[0] = measure q[0];", "c[1] = measure q[1];", ""])
    return "\n".join(lines)


def _calibration_openqasm(state: str) -> str:
    lines = ["OPENQASM 3.0;", "qubit[2] q;", "bit[2] c;"]
    if state[0] == "1":
        lines.append("x q[0];")
    if state[1] == "1":
        lines.append("x q[1];")
    lines.extend(["c[0] = measure q[0];", "c[1] = measure q[1];", ""])
    return "\n".join(lines)


def _selected_packets(stage188: dict[str, Any], selected_lanes: set[str]) -> list[dict[str, Any]]:
    packets = [
        packet
        for packet in stage188.get("packets", [])
        if isinstance(packet, dict)
        and packet.get("provider") == "ibm_runtime"
        and str(packet.get("source_lane_id")) in selected_lanes
    ]
    return sorted(packets, key=lambda packet: str(packet.get("packet_id")))


def _packet_execution_template(packet: dict[str, Any]) -> dict[str, Any]:
    template = str(packet["fixed_width"]["circuit_template"])
    return {
        "schema_version": STAGE190_SCHEMA_VERSION,
        "template_type": "replacement_packet_execution_counts",
        "packet_id": packet["packet_id"],
        "packet_hash": packet.get("packet_hash"),
        "semantics_id": packet.get("semantics_id"),
        "source_lane_id": packet.get("source_lane_id"),
        "provider": packet.get("provider"),
        "backend": packet.get("backend"),
        "encoding_family": packet.get("encoding_family"),
        "circuit_template": template,
        "status": "template_counts_required",
        "no_hardware_submission": True,
        "job_or_task_ids": [],
        "backend_metadata": {
            "backend": "",
            "provider": packet.get("provider"),
            "calibration_timestamp_utc": "",
            "stage190_result_path": "",
            "additional_metadata": {},
        },
        "submitted_at_utc": "",
        "completed_at_utc": "",
        "shot_count": packet.get("shot_count"),
        "raw_counts_by_row": [
            {
                "row_id": row["row_id"],
                "ideal_score": row["ideal_predictions"]["score"],
                "component_exposure": row.get("component_exposure"),
                "counts": {},
                "openqasm3": _row_program(row, template),
            }
            for row in packet.get("rows", [])
        ],
        "required_execution_fields": [
            "job_or_task_ids",
            "backend_metadata",
            "submitted_at_utc",
            "completed_at_utc",
            "raw_counts_by_row",
        ],
    }


def _calibration_template(provider: str = "ibm_runtime", *, shots_per_state: int = 1000) -> dict[str, Any]:
    return {
        "schema_version": STAGE190_SCHEMA_VERSION,
        "template_type": "replacement_known_state_calibration_counts",
        "provider": provider,
        "status": "template_counts_required",
        "no_hardware_submission": True,
        "job_or_task_ids": [],
        "backend_metadata": {
            "backend": "",
            "provider": provider,
            "calibration_timestamp_utc": "",
            "additional_metadata": {},
        },
        "submitted_at_utc": "",
        "completed_at_utc": "",
        "shots_per_state": shots_per_state,
        "raw_counts_by_state": [
            {"state": state, "expected_dominant_key": state, "counts": {}, "openqasm3": _calibration_openqasm(state)}
            for state in CALIBRATION_STATES
        ],
    }


def _matched_group_records(packets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for packet in packets:
        grouped.setdefault((str(packet.get("source_lane_id")), str(packet.get("fixed_width", {}).get("circuit_template"))), []).append(packet)
    records = []
    required = set(REQUIRED_ENCODING_FAMILIES)
    for (lane_id, template), group in sorted(grouped.items()):
        families = {str(packet.get("encoding_family")) for packet in group}
        row_counts = {int(packet.get("row_count") or len(packet.get("rows", []))) for packet in group}
        shot_counts = {int(packet.get("shot_count") or 0) for packet in group}
        records.append(
            {
                "source_lane_id": lane_id,
                "circuit_template": template,
                "packet_count": len(group),
                "observed_encoding_families": sorted(families),
                "missing_encoding_families": sorted(required - families),
                "extra_encoding_families": sorted(families - required),
                "row_counts": sorted(row_counts),
                "shot_counts": sorted(shot_counts),
                "ready": bool(
                    len(group) == len(REQUIRED_ENCODING_FAMILIES)
                    and not (required - families)
                    and not (families - required)
                    and len(row_counts) == 1
                    and len(shot_counts) == 1
                    and 0 not in row_counts
                    and 0 not in shot_counts
                    and template in REQUIRED_CIRCUIT_TEMPLATES
                ),
            }
        )
    return records


def run_stage190_replacement_execution_package(
    *,
    stage188_results_path: Path = DEFAULT_STAGE188_RESULTS,
    stage189_results_path: Path = DEFAULT_STAGE189_RESULTS,
) -> dict[str, Any]:
    stage188 = _load_json(stage188_results_path)
    stage189 = _load_json(stage189_results_path)
    sources = [(stage188_results_path, stage188), (stage189_results_path, stage189)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    blockers = []
    if missing_sources:
        blockers.append("missing_source_artifacts")
    if isinstance(stage189, dict) and stage189.get("decision") != STAGE189_REOPENED:
        blockers.append("stage189_hardware_review_not_reopened")
    selected_lanes = set(stage189.get("selected_lanes", [])) if isinstance(stage189, dict) else set()
    if not selected_lanes:
        blockers.append("selected_lanes_missing")
    packets = _selected_packets(stage188, selected_lanes) if isinstance(stage188, dict) else []
    matched_groups = _matched_group_records(packets)
    expected_packet_count = len(selected_lanes) * len(REQUIRED_ENCODING_FAMILIES)
    if len(packets) != expected_packet_count:
        blockers.append("selected_packet_count_mismatch")
    if not matched_groups or not all(record["ready"] for record in matched_groups):
        blockers.append("matched_group_contract_incomplete")
    calibration = _calibration_template()
    execution_templates = [_packet_execution_template(packet) for packet in packets]
    evidence_records = [
        {
            "template_type": "replacement_packet_execution_counts",
            "packet_id": template["packet_id"],
            "source_lane_id": template["source_lane_id"],
            "encoding_family": template["encoding_family"],
            "circuit_template": template["circuit_template"],
            "row_count": len(template["raw_counts_by_row"]),
            "shot_count": template["shot_count"],
            "ready_for_interpretation": False,
            "missing_evidence": "job_or_task_ids; backend_metadata; submitted_at_utc; completed_at_utc; raw_counts_by_row",
        }
        for template in execution_templates
    ]
    evidence_records.append(
        {
            "template_type": "replacement_known_state_calibration_counts",
            "packet_id": "",
            "source_lane_id": "",
            "encoding_family": "",
            "circuit_template": "known_state_calibration",
            "row_count": len(calibration["raw_counts_by_state"]),
            "shot_count": calibration["shots_per_state"],
            "ready_for_interpretation": False,
            "missing_evidence": "job_or_task_ids; backend_metadata; submitted_at_utc; completed_at_utc; raw_counts_by_state",
        }
    )
    if blockers:
        decision = "REPLACEMENT_EXECUTION_PACKAGE_INCOMPLETE"
    else:
        decision = "REPLACEMENT_EXECUTION_PACKAGE_PREPARED_COUNTS_AND_CALIBRATION_REQUIRED"
    return {
        "schema_version": STAGE190_SCHEMA_VERSION,
        "stage": "stage190_replacement_execution_package",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "semantics_id": stage188.get("semantics_id") if isinstance(stage188, dict) else None,
        "selected_lanes": sorted(selected_lanes),
        "selected_lane_count": len(selected_lanes),
        "expected_packet_count": expected_packet_count,
        "packet_template_count": len(execution_templates),
        "calibration_template_count": 1,
        "estimated_packet_row_job_count": sum(len(template["raw_counts_by_row"]) for template in execution_templates),
        "estimated_calibration_job_count": len(CALIBRATION_STATES),
        "estimated_total_job_count": sum(len(template["raw_counts_by_row"]) for template in execution_templates) + len(CALIBRATION_STATES),
        "matched_group_records": matched_groups,
        "execution_templates": execution_templates,
        "calibration_template": calibration,
        "evidence_records": evidence_records,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "claim_boundary": {
            "supported": [
                "replacement-semantics packet execution templates for selected IBM lanes",
                "known-state calibration template for the replacement run",
                "result-ingestion contract fields required before interpretation",
            ],
            "excluded": [
                "hardware job submission",
                "real calibration or packet counts",
                "provider credentials or runnable live-submit command strings",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "Use these templates only after IBM credit/provider review and exact human approval; filled counts must pass "
            "calibration and result-ingestion checks before any robustness interpretation."
        ),
    }


def write_stage190_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    template_dir = output_dir / "execution_templates"
    template_dir.mkdir(parents=True, exist_ok=True)
    template_paths = []
    for template in result["execution_templates"]:
        path = template_dir / f"{template['packet_id']}.json"
        path.write_text(json.dumps(template, indent=2, sort_keys=True), encoding="utf-8")
        template_paths.append(str(path.as_posix()))
    calibration_path = template_dir / "ibm_runtime_replacement_known_state_calibration.json"
    calibration_path.write_text(json.dumps(result["calibration_template"], indent=2, sort_keys=True), encoding="utf-8")
    manifest_keys = (
        "schema_version", "stage", "status", "objective", "decision", "source_artifacts",
        "missing_source_artifacts", "blockers", "semantics_id", "selected_lanes", "selected_lane_count",
        "expected_packet_count", "packet_template_count", "calibration_template_count", "estimated_packet_row_job_count",
        "estimated_calibration_job_count", "estimated_total_job_count", "no_hardware_submission",
        "provider_credentials_required", "secret_values_recorded", "runnable_commands_recorded", "claim_boundary", "next_gate",
    )
    manifest = {key: result[key] for key in manifest_keys}
    manifest["template_paths"] = template_paths
    manifest["calibration_template_path"] = str(calibration_path.as_posix())
    manifest["result_path"] = str((output_dir / "results.json").as_posix())
    manifest["summary_csv_path"] = str((output_dir / "summary.csv").as_posix())
    paths = {"manifest": str(output_dir / "manifest.json"), "result": str(output_dir / "results.json"), "summary_csv": str(output_dir / "summary.csv"), "template_dir": str(template_dir)}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("template_type", "packet_id", "source_lane_id", "encoding_family", "circuit_template", "row_count", "shot_count", "missing_evidence", "ready_for_interpretation"))
        writer.writeheader()
        for record in result["evidence_records"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage190_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"packet_template_count: {result['packet_template_count']}")
    print(f"estimated_total_job_count: {result['estimated_total_job_count']}")
    print(f"next_gate: {result['next_gate']}")
