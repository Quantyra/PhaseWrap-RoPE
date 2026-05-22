from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from qrope.stage101_known_state_calibration_gate import (
    DEFAULT_OUTPUT_DIR as DEFAULT_STAGE101_OUTPUT_DIR,
    OBJECTIVE,
    STATES,
    expected_key_for_order,
)


STAGE102_SCHEMA_VERSION = "qrope_stage102_calibration_execution_package_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE101_RESULTS = DEFAULT_STAGE101_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage102_calibration_execution_package"
REQUIRED_EXECUTION_FIELDS: tuple[str, ...] = (
    "job_or_task_ids",
    "backend_metadata",
    "submitted_at_utc",
    "completed_at_utc",
    "raw_counts_by_state",
)


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _state_preparation_openqasm(state: str) -> str:
    lines = [
        "OPENQASM 3.0;",
        "qubit[2] q;",
        "bit[2] c;",
    ]
    if state[0] == "1":
        lines.append("x q[0];")
    if state[1] == "1":
        lines.append("x q[1];")
    lines.extend(
        [
            "c[0] = measure q[0];",
            "c[1] = measure q[1];",
            "",
        ]
    )
    return "\n".join(lines)


def build_execution_template(provider_record: dict[str, Any], *, shots_per_state: int = 1000) -> dict[str, Any]:
    provider = str(provider_record["provider"])
    expected_order = str(provider_record["expected_bitstring_order"])
    return {
        "schema_version": STAGE102_SCHEMA_VERSION,
        "provider": provider,
        "expected_bitstring_order": expected_order,
        "status": "template_counts_required",
        "no_hardware_submission": True,
        "instructions": (
            "Replace placeholders with real provider/backend/date execution evidence before rerunning "
            "scripts/run_stage101_known_state_calibration_gate.py --execution-dir PATH."
        ),
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
            {
                "state": state,
                "expected_dominant_key": expected_key_for_order(state, expected_order),
                "counts": {},
                "openqasm3": _state_preparation_openqasm(state),
            }
            for state in STATES
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
        )
        and "backend_metadata" not in missing
    ):
        missing.append("backend_metadata")
    if template.get("raw_counts_by_state"):
        empty_counts = [
            str(item.get("state"))
            for item in template["raw_counts_by_state"]
            if not item.get("counts")
        ]
        if empty_counts and "raw_counts_by_state" not in missing:
            missing.append("raw_counts_by_state")
    return missing


def run_stage102_package(
    *,
    stage101_results_path: Path = DEFAULT_STAGE101_RESULTS,
    shots_per_state: int = 1000,
) -> dict[str, Any]:
    stage101 = _load_json(stage101_results_path)
    missing_sources = [] if stage101 is not None else [str(stage101_results_path.as_posix())]
    provider_records = list(stage101.get("provider_records", [])) if stage101 else []
    templates = [build_execution_template(record, shots_per_state=shots_per_state) for record in provider_records]
    evidence_records = [
        {
            "provider": template["provider"],
            "expected_bitstring_order": template["expected_bitstring_order"],
            "template_file": f"{template['provider']}_known_state_execution.json",
            "shots_per_state": template["shots_per_state"],
            "states": [row["state"] for row in template["raw_counts_by_state"]],
            "missing_evidence": _template_missing_fields(template),
            "ready_for_stage101": False,
        }
        for template in templates
    ]
    all_templates_present = bool(templates) and not missing_sources
    return {
        "schema_version": STAGE102_SCHEMA_VERSION,
        "stage": "stage102_calibration_execution_package",
        "status": "completed" if all_templates_present else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "CALIBRATION_EXECUTION_TEMPLATES_PREPARED_COUNTS_STILL_REQUIRED"
            if all_templates_present
            else "CALIBRATION_EXECUTION_TEMPLATE_PACKAGE_INCOMPLETE"
        ),
        "source_artifacts": [str(stage101_results_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "stage101_decision": stage101.get("decision") if stage101 else None,
        "stage101_known_state_calibration_pass": stage101.get("known_state_calibration_pass") if stage101 else None,
        "provider_count": len(provider_records),
        "template_count": len(templates),
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "required_execution_fields": list(REQUIRED_EXECUTION_FIELDS),
        "templates": templates,
        "evidence_records": evidence_records,
        "claim_boundary": {
            "supported": [
                "provider-specific known-state execution JSON templates for the Stage 101 calibration gate",
                "explicit |00>, |01>, |10>, and |11> preparation circuits and expected dominant keys",
                "a no-hardware handoff package for collecting calibration evidence without changing the claim boundary",
            ],
            "excluded": [
                "real known-state calibration counts",
                "completed provider calibration",
                "a noisy-hardware robustness result",
                "permission to interpret Stage 99 or Stage 100 counts before Stage 101 passes",
            ],
        },
        "next_gate": (
            "Execute the known-state circuits on the target provider/backend/date, fill the generated execution JSON "
            "templates with raw counts and metadata, then rerun Stage 101 with --execution-dir."
        ),
    }


def write_stage102_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    template_dir = output_dir / "execution_templates"
    template_dir.mkdir(parents=True, exist_ok=True)
    template_paths: list[str] = []
    for template in result["templates"]:
        path = template_dir / f"{template['provider']}_known_state_execution.json"
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
        "stage101_decision": result["stage101_decision"],
        "stage101_known_state_calibration_pass": result["stage101_known_state_calibration_pass"],
        "provider_count": result["provider_count"],
        "template_count": result["template_count"],
        "template_paths": template_paths,
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
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
            fieldnames=("provider", "expected_bitstring_order", "template_file", "shots_per_state", "states", "missing_evidence", "ready_for_stage101"),
        )
        writer.writeheader()
        for record in result["evidence_records"]:
            writer.writerow(
                {
                    **record,
                    "states": "; ".join(record["states"]),
                    "missing_evidence": "; ".join(record["missing_evidence"]),
                }
            )
    return paths


def print_stage102_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"template_count: {result['template_count']}")
    print(f"next_gate: {result['next_gate']}")
