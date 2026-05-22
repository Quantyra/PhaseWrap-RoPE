from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE160_SCHEMA_VERSION = "qrope_stage160_first_provider_post_run_analysis_packet_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE159_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage159_first_provider_backend_preflight" / "results.json"
DEFAULT_STAGE164_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage164_first_provider_result_lock_verifier" / "results.json"
DEFAULT_STAGE115_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage115_provider_result_collector" / "results.json"
DEFAULT_STAGE113_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage113_job_result_evidence_assembler" / "results.json"
DEFAULT_STAGE135_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage135_post_collection_claim_gate_sequence" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage160_first_provider_post_run_analysis_packet"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
STAGE159_READY = "FIRST_PROVIDER_BACKEND_PREFLIGHT_READY_AWAITING_APPROVAL"
PROVIDER = "ibm_runtime"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _command_records(provider: str) -> list[dict[str, Any]]:
    commands = [
        (
            "stage164",
            "verify provider results against the pre-run job-shard lock",
            "python scripts/run_stage164_first_provider_result_lock_verifier.py",
        ),
        (
            "stage115",
            "collect provider result shards into Stage 113 input",
            f"python scripts/run_stage115_provider_result_collector.py --provider {provider} --write-stage113-input",
        ),
        (
            "stage113",
            "assemble provider job results into evidence files",
            f"python scripts/run_stage113_job_result_evidence_assembler.py --provider {provider} --write-evidence",
        ),
        (
            "stage101",
            "verify known-state calibration counts",
            "python scripts/run_stage101_known_state_calibration_gate.py",
        ),
        (
            "stage103",
            "recompute preregistered robustness metrics",
            "python scripts/run_stage103_robustness_metric_preregistration.py",
        ),
        (
            "stage136",
            "refresh auditability metric contract",
            "python scripts/run_stage136_auditability_metric_preregistration.py",
        ),
        (
            "stage137",
            "evaluate provider-scoped auditability metrics",
            f"python scripts/run_stage137_auditability_metric_evaluator.py --provider {provider}",
        ),
        (
            "stage148",
            "apply first-provider statistical interpretation guard",
            "python scripts/run_stage148_first_provider_statistical_interpretation_gate.py",
        ),
        (
            "stage109",
            "validate assembled evidence intake",
            "python scripts/run_stage109_window_evidence_intake_validator.py",
        ),
        (
            "stage110",
            "apply replicated robustness claim gate",
            "python scripts/run_stage110_replicated_advantage_claim_gate.py",
        ),
        (
            "stage138",
            "apply objective claim gate",
            "python scripts/run_stage138_objective_claim_gate.py",
        ),
        (
            "stage135",
            "audit the full post-collection claim-gate sequence",
            "python scripts/run_stage135_post_collection_claim_gate_sequence.py",
        ),
    ]
    return [
        {
            "order": index,
            "stage_id": stage_id,
            "purpose": purpose,
            "command": command,
            "hardware_submission_command": False,
        }
        for index, (stage_id, purpose, command) in enumerate(commands, start=1)
    ]


def run_stage160_post_run_analysis_packet(
    *,
    stage159_results_path: Path = DEFAULT_STAGE159_RESULTS,
    stage164_results_path: Path = DEFAULT_STAGE164_RESULTS,
    stage115_results_path: Path = DEFAULT_STAGE115_RESULTS,
    stage113_results_path: Path = DEFAULT_STAGE113_RESULTS,
    stage135_results_path: Path = DEFAULT_STAGE135_RESULTS,
) -> dict[str, Any]:
    stage159 = _load_json(stage159_results_path)
    stage164 = _load_json(stage164_results_path)
    stage115 = _load_json(stage115_results_path)
    stage113 = _load_json(stage113_results_path)
    stage135 = _load_json(stage135_results_path)
    sources = [
        (stage159_results_path, stage159),
        (stage164_results_path, stage164),
        (stage115_results_path, stage115),
        (stage113_results_path, stage113),
        (stage135_results_path, stage135),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    provider = str(stage159.get("first_unlock_provider") if isinstance(stage159, dict) else PROVIDER)
    command_records = _command_records(provider)
    blockers: list[str] = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    if not isinstance(stage159, dict) or stage159.get("decision") != STAGE159_READY:
        blockers.append("stage159_backend_preflight_not_ready")
    if provider != PROVIDER:
        blockers.append("first_provider_not_ibm_runtime")
    if isinstance(stage159, dict) and stage159.get("backend_lookup_ready") is not True:
        blockers.append("stage159_backend_lookup_not_ready")
    stage164_expected_count = int(stage164.get("expected_result_record_count") or 0) if isinstance(stage164, dict) else 0
    stage164_result_count = int(stage164.get("provider_result_record_count") or 0) if isinstance(stage164, dict) else 0
    stage164_missing_count = int(stage164.get("missing_result_record_count") or 0) if isinstance(stage164, dict) else stage164_expected_count
    if isinstance(stage164, dict) and stage164.get("hash_match_count") != stage164.get("window_count"):
        blockers.append("stage164_hash_lock_mismatch")
    expected_job_count = int(stage115.get("expected_job_count") or 0) if isinstance(stage115, dict) else 0
    result_record_count = int(stage115.get("result_record_count") or 0) if isinstance(stage115, dict) else 0
    missing_job_count = int(stage115.get("missing_job_count") or 0) if isinstance(stage115, dict) else expected_job_count
    if expected_job_count <= 0:
        blockers.append("stage115_expected_job_count_missing")
    if stage164_expected_count and expected_job_count and stage164_expected_count != expected_job_count:
        blockers.append("stage164_stage115_expected_count_mismatch")
    if stage164_result_count != result_record_count:
        blockers.append("stage164_stage115_result_count_mismatch")
    if result_record_count < expected_job_count or missing_job_count != 0:
        blockers.append("provider_result_records_missing")
    if stage164_missing_count != 0:
        blockers.append("stage164_provider_result_records_missing")
    if isinstance(stage115, dict) and stage115.get("provider_scope") not in (provider, "all"):
        blockers.append("stage115_provider_scope_mismatch")
    if isinstance(stage113, dict) and stage113.get("provider_scope") not in (provider, "all", None):
        blockers.append("stage113_provider_scope_mismatch")
    if any("--allow-live-submit" in record["command"] for record in command_records):
        blockers.append("post_run_packet_contains_live_submit_command")
    if missing_sources:
        decision = "FIRST_PROVIDER_POST_RUN_ANALYSIS_PACKET_INCOMPLETE"
    elif not blockers:
        decision = "FIRST_PROVIDER_POST_RUN_ANALYSIS_SEQUENCE_READY"
    elif set(blockers) <= {
        "provider_result_records_missing",
        "stage115_expected_job_count_missing",
        "stage164_provider_result_records_missing",
        "stage164_stage115_expected_count_mismatch",
    }:
        decision = "FIRST_PROVIDER_POST_RUN_ANALYSIS_PACKET_READY_AWAITING_PROVIDER_RESULTS"
    else:
        decision = "FIRST_PROVIDER_POST_RUN_ANALYSIS_PACKET_BLOCKED"
    return {
        "schema_version": STAGE160_SCHEMA_VERSION,
        "stage": "stage160_first_provider_post_run_analysis_packet",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage159_decision": stage159.get("decision") if isinstance(stage159, dict) else None,
        "stage164_decision": stage164.get("decision") if isinstance(stage164, dict) else None,
        "stage115_decision": stage115.get("decision") if isinstance(stage115, dict) else None,
        "stage113_decision": stage113.get("decision") if isinstance(stage113, dict) else None,
        "stage135_decision": stage135.get("decision") if isinstance(stage135, dict) else None,
        "first_unlock_provider": provider,
        "approval_phrase_required": stage159.get("approval_phrase_required") if isinstance(stage159, dict) else None,
        "backend_lookup_ready": stage159.get("backend_lookup_ready") if isinstance(stage159, dict) else None,
        "stage164_hash_match_count": stage164.get("hash_match_count") if isinstance(stage164, dict) else None,
        "stage164_window_count": stage164.get("window_count") if isinstance(stage164, dict) else None,
        "stage164_expected_result_record_count": stage164_expected_count,
        "stage164_provider_result_record_count": stage164_result_count,
        "stage164_missing_result_record_count": stage164_missing_count,
        "expected_job_count": expected_job_count,
        "result_record_count": result_record_count,
        "missing_job_count": missing_job_count,
        "command_count": len(command_records),
        "command_records": command_records,
        "ordered_command_sequence": [record["command"] for record in command_records],
        "blockers": sorted(set(blockers)),
        "no_hardware_submission": True,
        "explicit_user_approval_required_for_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_hardware_commands_recorded": False,
        "claim_boundary": {
            "supported": [
                "a deterministic no-submit analysis sequence to run after IBM provider result JSONL files exist",
                "binding of the post-result analysis packet to Stage 159 backend-readiness evidence",
                "Stage 164 result-lock verification before Stage 115 collection or Stage 113 evidence assembly",
                "a guard that the packet contains no Stage 133 live-submit command",
                "an explicit missing-result boundary while IBM provider result records are absent",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "new provider result records",
                "credit balance verification",
                "a noisy-hardware robustness or auditability conclusion before the post-result sequence reaches terminal gates",
            ],
        },
        "next_gate": (
            "After explicit hardware approval and Stage 133 execution produce IBM provider result records, run this "
            "packet's command sequence in order, starting with Stage 164 lock verification, then refresh Stage 115 "
            "through Stage 138 evidence and determine whether the objective is supported or not supported."
        ),
    }


def write_stage160_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage159_decision": result["stage159_decision"],
        "stage164_decision": result["stage164_decision"],
        "stage115_decision": result["stage115_decision"],
        "stage113_decision": result["stage113_decision"],
        "stage135_decision": result["stage135_decision"],
        "first_unlock_provider": result["first_unlock_provider"],
        "backend_lookup_ready": result["backend_lookup_ready"],
        "stage164_hash_match_count": result["stage164_hash_match_count"],
        "stage164_window_count": result["stage164_window_count"],
        "stage164_expected_result_record_count": result["stage164_expected_result_record_count"],
        "stage164_provider_result_record_count": result["stage164_provider_result_record_count"],
        "stage164_missing_result_record_count": result["stage164_missing_result_record_count"],
        "expected_job_count": result["expected_job_count"],
        "result_record_count": result["result_record_count"],
        "missing_job_count": result["missing_job_count"],
        "command_count": result["command_count"],
        "blockers": result["blockers"],
        "no_hardware_submission": result["no_hardware_submission"],
        "explicit_user_approval_required_for_hardware_submission": result[
            "explicit_user_approval_required_for_hardware_submission"
        ],
        "provider_credentials_required": result["provider_credentials_required"],
        "secret_values_recorded": result["secret_values_recorded"],
        "runnable_hardware_commands_recorded": result["runnable_hardware_commands_recorded"],
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
        writer = csv.DictWriter(handle, fieldnames=("order", "stage_id", "purpose", "command", "hardware_submission_command"))
        writer.writeheader()
        for record in result["command_records"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage160_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"first_unlock_provider: {result['first_unlock_provider']}")
    print(f"result_record_count: {result['result_record_count']}/{result['expected_job_count']}")
    print(f"missing_job_count: {result['missing_job_count']}")
    print(f"command_count: {result['command_count']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
