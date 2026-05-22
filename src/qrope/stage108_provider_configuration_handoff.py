from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE108_SCHEMA_VERSION = "qrope_stage108_provider_configuration_handoff_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE106_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage106_hardware_execution_preflight" / "results.json"
DEFAULT_STAGE107_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage107_window_execution_orchestrator" / "manifest.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage108_provider_configuration_handoff"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _provider_template_lines(provider: str, blockers: list[str]) -> list[str]:
    if provider == "amazon_braket":
        lines = [
            "# Amazon Braket configuration for Stage 106. Fill locally; do not commit secrets.",
            "AWS_PROFILE=",
            "AWS_ACCESS_KEY_ID=",
            "AWS_SESSION_TOKEN=",
            "QROPE_BRAKET_DEVICE_ARN=",
            "QROPE_BRAKET_DEVICE_ARNS=",
            "QROPE_BRAKET_OUTPUT_S3_BUCKET=",
            "QROPE_BRAKET_AWS_REGION=",
        ]
    elif provider == "ibm_runtime":
        lines = [
            "# IBM Runtime configuration for Stage 106. Fill locally; do not commit secrets.",
            "IBM_QUANTUM_TOKEN=",
            "QISKIT_IBM_TOKEN=",
            "QROPE_IBM_BACKEND=",
            "QROPE_HARDWARE_BACKEND=",
            "IBM_QUANTUM_INSTANCE_CRN=",
        ]
    else:
        lines = [f"# Unknown provider: {provider}"]
    lines.extend(
        [
            "",
            "# Common execution guards.",
            "QROPE_HARDWARE_BUDGET_USD_CAP=",
            "QROPE_HARDWARE_QUEUE_DEPTH_CAP=",
            "",
            f"# Current Stage 106 blockers: {', '.join(blockers) if blockers else 'none'}",
        ]
    )
    return lines


def _handoff_record(record: dict[str, Any]) -> dict[str, Any]:
    provider = str(record["provider"])
    blockers = [str(item) for item in record.get("blockers", [])]
    return {
        "provider": provider,
        "stage106_status": record.get("status"),
        "blockers": blockers,
        "credential_env_present": record.get("credential_env_present", []),
        "backend_env_present": record.get("backend_env_present", []),
        "template_file": f"{provider}_stage106_env.template",
        "requires_secret_handling": True,
        "commit_template_only": True,
        "secret_values_recorded": False,
    }


def run_stage108_handoff(
    *,
    stage106_results_path: Path = DEFAULT_STAGE106_RESULTS,
    stage107_manifest_path: Path = DEFAULT_STAGE107_MANIFEST,
) -> dict[str, Any]:
    stage106 = _load_json(stage106_results_path)
    stage107 = _load_json(stage107_manifest_path)
    sources = [
        (stage106_results_path, stage106),
        (stage107_manifest_path, stage107),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    provider_records = list(stage106.get("provider_records", [])) if stage106 else []
    handoff_records = [_handoff_record(record) for record in provider_records]
    templates = {
        record["template_file"]: "\n".join(_provider_template_lines(record["provider"], record["blockers"])) + "\n"
        for record in handoff_records
    }
    ready_after_fill = bool(handoff_records) and all(record["stage106_status"] == "ready" for record in handoff_records)
    return {
        "schema_version": STAGE108_SCHEMA_VERSION,
        "stage": "stage108_provider_configuration_handoff",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "PROVIDER_CONFIGURATION_HANDOFF_PREPARED_STAGE106_STILL_BLOCKED"
            if not ready_after_fill
            else "PROVIDER_CONFIGURATION_HANDOFF_READY_STAGE106_ALREADY_CLEAR"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage106_decision": stage106.get("decision") if stage106 else None,
        "stage107_decision": stage107.get("decision") if stage107 else None,
        "ready_for_hardware_submission": bool(stage106 and stage106.get("ready_for_hardware_submission") is True),
        "provider_count": len(handoff_records),
        "handoff_records": handoff_records,
        "templates": templates,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "a non-secret provider configuration handoff for clearing Stage 106",
                "provider-specific environment templates tied to observed Stage 106 blockers",
                "a reminder that credentials and secret values must remain local and uncommitted",
            ],
            "excluded": [
                "real provider credentials",
                "backend availability discovery",
                "hardware submission",
                "completed calibration or matched packet execution",
                "a noisy-hardware robustness result",
            ],
        },
        "next_gate": (
            "Fill provider configuration locally, rerun Stage 106 with --load-dotenv, and proceed to Stage 107 only "
            "after Stage 106 reports ready."
        ),
    }


def write_stage108_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    template_dir = output_dir / "env_templates"
    template_dir.mkdir(parents=True, exist_ok=True)
    template_paths: list[str] = []
    for file_name, content in result["templates"].items():
        path = template_dir / file_name
        path.write_text(content, encoding="utf-8")
        template_paths.append(str(path.as_posix()))
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage106_decision": result["stage106_decision"],
        "stage107_decision": result["stage107_decision"],
        "ready_for_hardware_submission": result["ready_for_hardware_submission"],
        "provider_count": result["provider_count"],
        "template_paths": template_paths,
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
        "template_dir": str(template_dir),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "provider",
                "stage106_status",
                "template_file",
                "credential_env_present",
                "backend_env_present",
                "blockers",
                "secret_values_recorded",
            ),
        )
        writer.writeheader()
        for record in result["handoff_records"]:
            writer.writerow(
                {
                    "provider": record["provider"],
                    "stage106_status": record["stage106_status"],
                    "template_file": record["template_file"],
                    "credential_env_present": "; ".join(record["credential_env_present"]),
                    "backend_env_present": "; ".join(record["backend_env_present"]),
                    "blockers": "; ".join(record["blockers"]),
                    "secret_values_recorded": record["secret_values_recorded"],
                }
            )
    return paths


def print_stage108_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"provider_count: {result['provider_count']}")
    print(f"ready_for_hardware_submission: {result['ready_for_hardware_submission']}")
    print(f"next_gate: {result['next_gate']}")
