from __future__ import annotations

import csv
import importlib.util
import json
import os
from pathlib import Path
from typing import Any, Mapping


STAGE140_SCHEMA_VERSION = "qrope_stage140_local_provider_configuration_readiness_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE139_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage139_provider_action_readiness_checklist" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage140_local_provider_configuration_readiness"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _group_keys(group: str) -> list[str]:
    return [part.strip() for part in group.split(" or ") if part.strip()]


def _present_group(env: Mapping[str, str], group: str) -> list[str]:
    return [key for key in _group_keys(group) if str(env.get(key, "")).strip()]


def _module_present(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def _sdk_readiness(provider_record: dict[str, Any]) -> dict[str, Any]:
    modules = dict(provider_record.get("sdk_modules", {}))
    observed = {module: _module_present(module) for module in modules}
    missing = sorted(module for module, present in observed.items() if not present)
    return {
        "sdk_modules": observed,
        "sdk_ready": not missing,
        "missing_sdk_modules": missing,
    }


def _env_readiness(provider_record: dict[str, Any], env: Mapping[str, str]) -> dict[str, Any]:
    provider_groups = [str(group) for group in provider_record.get("required_provider_env", [])]
    common_groups = [str(group) for group in provider_record.get("required_common_env", [])]
    group_records = []
    for scope, groups in (("provider", provider_groups), ("common", common_groups)):
        for group in groups:
            present = _present_group(env, group)
            group_records.append(
                {
                    "scope": scope,
                    "group": group,
                    "candidate_keys": _group_keys(group),
                    "present_keys": present,
                    "ready": bool(present),
                }
            )
    missing_groups = [record["group"] for record in group_records if not record["ready"]]
    return {
        "env_group_records": group_records,
        "env_ready": not missing_groups,
        "missing_env_groups": missing_groups,
        "present_env_keys": sorted({key for record in group_records for key in record["present_keys"]}),
    }


def _provider_record(provider_record: dict[str, Any], env: Mapping[str, str]) -> dict[str, Any]:
    env_status = _env_readiness(provider_record, env)
    sdk_status = _sdk_readiness(provider_record)
    ready_for_rerun = env_status["env_ready"] and sdk_status["sdk_ready"]
    return {
        "provider": provider_record.get("provider"),
        "stage139_first_blocker": provider_record.get("first_blocker"),
        "cutover_authorized": provider_record.get("cutover_authorized") is True,
        "env_ready_for_stage106": env_status["env_ready"],
        "sdk_ready_for_stage111": sdk_status["sdk_ready"],
        "ready_for_preflight_rerun": ready_for_rerun,
        "missing_env_groups": env_status["missing_env_groups"],
        "present_env_keys": env_status["present_env_keys"],
        "env_group_records": env_status["env_group_records"],
        "missing_sdk_modules": sdk_status["missing_sdk_modules"],
        "sdk_modules": sdk_status["sdk_modules"],
        "next_commands": [
            "python scripts/run_stage106_hardware_execution_preflight.py --load-dotenv",
            "python scripts/run_stage111_provider_sdk_backend_discovery.py",
            "python scripts/run_stage128_sdk_client_factory_audit.py",
            "python scripts/run_stage129_live_cutover_authorization_audit.py",
            "python scripts/run_stage130_live_cutover_remediation_packet.py",
            "python scripts/run_stage139_provider_action_readiness_checklist.py",
        ]
        if ready_for_rerun
        else [],
    }


def run_stage140_readiness(
    *,
    stage139_results_path: Path = DEFAULT_STAGE139_RESULTS,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    environ = os.environ if env is None else env
    stage139 = _load_json(stage139_results_path)
    missing_sources = [] if isinstance(stage139, dict) else [str(stage139_results_path.as_posix())]
    provider_records = [
        _provider_record(record, environ)
        for record in (stage139.get("provider_records", []) if isinstance(stage139, dict) else [])
    ]
    rerun_ready_count = sum(1 for record in provider_records if record["ready_for_preflight_rerun"])
    return {
        "schema_version": STAGE140_SCHEMA_VERSION,
        "stage": "stage140_local_provider_configuration_readiness",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "LOCAL_PROVIDER_CONFIGURATION_READY_FOR_PREFLIGHT_RERUN"
            if rerun_ready_count
            else "LOCAL_PROVIDER_CONFIGURATION_BLOCKED_ENV_OR_SDK_REQUIRED"
        ),
        "source_artifacts": [str(stage139_results_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "stage139_decision": stage139.get("decision") if isinstance(stage139, dict) else None,
        "provider_count": len(provider_records),
        "rerun_ready_provider_count": rerun_ready_count,
        "provider_records": provider_records,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "local non-secret provider configuration readiness based on environment key presence only",
                "provider SDK module availability checks before rerunning Stage 106/111/129",
                "explicit no-submission gate before provider cutover reruns",
            ],
            "excluded": [
                "provider credential values",
                "hardware job submission",
                "live provider SDK client creation",
                "real provider result records",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "For providers marked ready_for_preflight_rerun=true, rerun Stage 106 with --load-dotenv, then Stage 111, "
            "Stage 128, Stage 129, Stage 130, and Stage 139 before any Stage 133 live runner command."
        ),
    }


def write_stage140_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage139_decision": result["stage139_decision"],
        "provider_count": result["provider_count"],
        "rerun_ready_provider_count": result["rerun_ready_provider_count"],
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
                "env_ready_for_stage106",
                "sdk_ready_for_stage111",
                "ready_for_preflight_rerun",
                "missing_env_groups",
                "present_env_keys",
                "missing_sdk_modules",
            ),
        )
        writer.writeheader()
        for record in result["provider_records"]:
            writer.writerow(
                {
                    "provider": record["provider"],
                    "env_ready_for_stage106": record["env_ready_for_stage106"],
                    "sdk_ready_for_stage111": record["sdk_ready_for_stage111"],
                    "ready_for_preflight_rerun": record["ready_for_preflight_rerun"],
                    "missing_env_groups": "; ".join(record["missing_env_groups"]),
                    "present_env_keys": "; ".join(record["present_env_keys"]),
                    "missing_sdk_modules": "; ".join(record["missing_sdk_modules"]),
                }
            )
    return paths


def print_stage140_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"rerun_ready_provider_count: {result['rerun_ready_provider_count']}/{result['provider_count']}")
    print(f"next_gate: {result['next_gate']}")
