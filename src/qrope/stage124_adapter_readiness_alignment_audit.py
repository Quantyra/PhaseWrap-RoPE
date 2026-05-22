from __future__ import annotations

import csv
import importlib
import json
from pathlib import Path
from typing import Any


STAGE124_SCHEMA_VERSION = "qrope_stage124_adapter_readiness_alignment_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE106_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage106_hardware_execution_preflight" / "results.json"
DEFAULT_STAGE111_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage111_provider_sdk_backend_discovery" / "results.json"
DEFAULT_STAGE123_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage123_provider_submission_plan_audit" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage124_adapter_readiness_alignment_audit"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
ADAPTER_MODULES = {
    "amazon_braket": "qrope.provider_adapters.amazon_braket",
    "ibm_runtime": "qrope.provider_adapters.ibm_runtime",
}


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _provider_record(payload: dict[str, Any] | None, provider: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    for record in payload.get("provider_records", []):
        if record.get("provider") == provider:
            return record
    return {}


def _stage106_required(stage106: dict[str, Any] | None, provider: str) -> list[str]:
    if not isinstance(stage106, dict):
        return []
    return list(stage106.get("required_provider_env", {}).get(provider, []))


def _adapter_status(provider: str) -> dict[str, Any]:
    module = importlib.import_module(ADAPTER_MODULES[provider])
    return module.adapter_status()


def _plan_env_fields(stage123: dict[str, Any] | None, provider: str, stage123_results_path: Path) -> set[str]:
    if not isinstance(stage123, dict):
        return set()
    fields: set[str] = set()
    base = stage123_results_path.parent / "submission_plans" / provider
    for plan_path in base.glob("*/*.jsonl"):
        for line in plan_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            plan = json.loads(line)
            for key, value in plan.items():
                if key.endswith("_env") and isinstance(value, str):
                    fields.add(value)
    return fields


def _alignment_record(
    stage106: dict[str, Any] | None,
    stage111: dict[str, Any] | None,
    stage123: dict[str, Any] | None,
    provider: str,
    stage123_results_path: Path,
) -> dict[str, Any]:
    status = _adapter_status(provider)
    stage106_required = _stage106_required(stage106, provider)
    adapter_required = list(status.get("required_env", []))
    plan_env_fields = sorted(_plan_env_fields(stage123, provider, stage123_results_path))
    missing = []
    if sorted(adapter_required) != sorted(stage106_required):
        missing.append("adapter_required_env_mismatch_stage106")
    if not set(adapter_required).issubset(set(plan_env_fields)):
        missing.append("submission_plan_env_fields_do_not_cover_adapter_required_env")
    stage106_record = _provider_record(stage106, provider)
    stage111_record = _provider_record(stage111, provider)
    if stage106_record.get("status") != "blocked" or stage111_record.get("status") != "blocked":
        missing.append("current_provider_blocker_state_changed")
    if status.get("ready") is True:
        missing.append("adapter_unexpectedly_ready_before_provider_preflight")
    return {
        "provider": provider,
        "stage106_status": stage106_record.get("status"),
        "stage111_status": stage111_record.get("status"),
        "stage106_required_env": stage106_required,
        "adapter_required_env": adapter_required,
        "submission_plan_env_fields": plan_env_fields,
        "adapter_blockers": status.get("blockers", []),
        "stage106_blockers": stage106_record.get("blockers", []),
        "stage111_blockers": stage111_record.get("blockers", []),
        "missing_evidence": sorted(set(missing)),
        "ready": not missing,
    }


def run_stage124_audit(
    *,
    stage106_results_path: Path = DEFAULT_STAGE106_RESULTS,
    stage111_results_path: Path = DEFAULT_STAGE111_RESULTS,
    stage123_results_path: Path = DEFAULT_STAGE123_RESULTS,
) -> dict[str, Any]:
    stage106 = _load_json(stage106_results_path)
    stage111 = _load_json(stage111_results_path)
    stage123 = _load_json(stage123_results_path)
    sources = [(stage106_results_path, stage106), (stage111_results_path, stage111), (stage123_results_path, stage123)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    records = [_alignment_record(stage106, stage111, stage123, provider, stage123_results_path) for provider in sorted(ADAPTER_MODULES)]
    ready = all(record["ready"] for record in records) and not missing_sources
    return {
        "schema_version": STAGE124_SCHEMA_VERSION,
        "stage": "stage124_adapter_readiness_alignment_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "ADAPTER_READINESS_ALIGNED_EXECUTION_BLOCKED"
            if ready
            else "ADAPTER_READINESS_ALIGNMENT_INCOMPLETE"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage106_decision": stage106.get("decision") if isinstance(stage106, dict) else None,
        "stage111_decision": stage111.get("decision") if isinstance(stage111, dict) else None,
        "stage123_decision": stage123.get("decision") if isinstance(stage123, dict) else None,
        "provider_count": len(records),
        "aligned_provider_count": sum(1 for record in records if record["ready"]),
        "provider_records": records,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "adapter required environment contracts align with Stage 106 provider requirements",
                "Stage 123 submission-plan environment fields cover adapter requirements",
                "current provider execution remains blocked by Stage 106/111 readiness before live SDK submission",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "live provider SDK submission",
                "real provider result records",
                "Stage 113 evidence assembly",
                "a noisy-hardware robustness result",
            ],
        },
        "next_gate": (
            "Clear the Stage 106/111 provider blockers, rerun this alignment audit, then run provider SDK submitters "
            "only if adapter env contracts, submission-plan env fields, and Stage 129 cutover remain aligned."
        ),
    }


def write_stage124_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage106_decision": result["stage106_decision"],
        "stage111_decision": result["stage111_decision"],
        "stage123_decision": result["stage123_decision"],
        "provider_count": result["provider_count"],
        "aligned_provider_count": result["aligned_provider_count"],
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
            fieldnames=("provider", "stage106_status", "stage111_status", "ready", "missing_evidence"),
        )
        writer.writeheader()
        for record in result["provider_records"]:
            writer.writerow(
                {
                    "provider": record["provider"],
                    "stage106_status": record["stage106_status"],
                    "stage111_status": record["stage111_status"],
                    "ready": record["ready"],
                    "missing_evidence": "; ".join(record["missing_evidence"]),
                }
            )
    return paths


def print_stage124_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"aligned_provider_count: {result['aligned_provider_count']}/{result['provider_count']}")
    print(f"next_gate: {result['next_gate']}")
