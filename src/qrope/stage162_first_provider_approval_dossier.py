from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE162_SCHEMA_VERSION = "qrope_stage162_first_provider_approval_dossier_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE154_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage154_simulated_hardware_go_no_go" / "results.json"
DEFAULT_STAGE157_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage157_first_provider_live_run_approval_packet" / "results.json"
DEFAULT_STAGE159_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage159_first_provider_backend_preflight" / "results.json"
DEFAULT_STAGE160_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage160_first_provider_post_run_analysis_packet" / "results.json"
DEFAULT_STAGE161_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage161_first_provider_exposure_packet" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage162_first_provider_approval_dossier"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
STAGE154_GO = "SIMULATED_NOISE_TARGETED_HARDWARE_FOLLOWUP_RECOMMENDED"
STAGE157_READY = "FIRST_PROVIDER_LIVE_RUN_APPROVAL_PACKET_READY"
STAGE159_READY = "FIRST_PROVIDER_BACKEND_PREFLIGHT_READY_AWAITING_APPROVAL"
STAGE160_READY = "FIRST_PROVIDER_POST_RUN_ANALYSIS_PACKET_READY_AWAITING_PROVIDER_RESULTS"
STAGE161_READY = "FIRST_PROVIDER_EXPOSURE_PACKET_READY_AWAITING_APPROVAL"
APPROVAL_PHRASE = "APPROVE IBM RUNTIME STAGE133 LIVE RUN"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _provider_target_count(stage154: dict[str, Any] | None, provider: str) -> int:
    if not isinstance(stage154, dict):
        return 0
    return sum(1 for record in stage154.get("recommended_targets", []) if isinstance(record, dict) and record.get("provider") == provider)


def _decision_record(stage_id: str, payload: dict[str, Any] | None, expected: str, purpose: str) -> dict[str, Any]:
    decision = payload.get("decision") if isinstance(payload, dict) else None
    return {
        "stage_id": stage_id,
        "decision": decision,
        "expected_decision": expected,
        "ready": decision == expected,
        "purpose": purpose,
    }


def run_stage162_approval_dossier(
    *,
    stage154_results_path: Path = DEFAULT_STAGE154_RESULTS,
    stage157_results_path: Path = DEFAULT_STAGE157_RESULTS,
    stage159_results_path: Path = DEFAULT_STAGE159_RESULTS,
    stage160_results_path: Path = DEFAULT_STAGE160_RESULTS,
    stage161_results_path: Path = DEFAULT_STAGE161_RESULTS,
) -> dict[str, Any]:
    stage154 = _load_json(stage154_results_path)
    stage157 = _load_json(stage157_results_path)
    stage159 = _load_json(stage159_results_path)
    stage160 = _load_json(stage160_results_path)
    stage161 = _load_json(stage161_results_path)
    sources = [
        (stage154_results_path, stage154),
        (stage157_results_path, stage157),
        (stage159_results_path, stage159),
        (stage160_results_path, stage160),
        (stage161_results_path, stage161),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    provider = str(stage157.get("first_unlock_provider") if isinstance(stage157, dict) else "ibm_runtime")
    decision_records = [
        _decision_record("stage154", stage154, STAGE154_GO, "simulated-only screen recommends targeted hardware follow-up"),
        _decision_record("stage157", stage157, STAGE157_READY, "approval packet is ready and still requires the exact approval phrase"),
        _decision_record("stage159", stage159, STAGE159_READY, "configured IBM backend resolved in a read-only preflight"),
        _decision_record("stage160", stage160, STAGE160_READY, "post-result no-submit analysis sequence is prepared"),
        _decision_record("stage161", stage161, STAGE161_READY, "job and shot exposure is quantified before approval"),
    ]
    blockers: list[str] = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    for record in decision_records:
        if not record["ready"]:
            blockers.append(f"{record['stage_id']}_not_ready")
    if provider != "ibm_runtime":
        blockers.append("first_provider_not_ibm_runtime")
    approval_phrase_required = stage157.get("approval_phrase_required") if isinstance(stage157, dict) else None
    if approval_phrase_required != APPROVAL_PHRASE:
        blockers.append("approval_phrase_mismatch")
    if isinstance(stage157, dict) and stage157.get("runnable_commands_recorded") is not False:
        blockers.append("stage157_runnable_commands_recorded")
    if isinstance(stage161, dict) and stage161.get("runnable_commands_recorded") is not False:
        blockers.append("stage161_runnable_commands_recorded")
    if isinstance(stage161, dict) and stage161.get("credit_balance_verified") is not False:
        blockers.append("stage161_credit_boundary_mismatch")
    if isinstance(stage161, dict) and int(stage161.get("missing_result_record_count") or 0) <= 0:
        blockers.append("stage161_missing_result_boundary_not_active")
    approved_job_count = int(stage157.get("authorized_first_provider_job_count") or 0) if isinstance(stage157, dict) else 0
    exposure_job_count = int(stage161.get("job_count") or 0) if isinstance(stage161, dict) else 0
    if approved_job_count != exposure_job_count:
        blockers.append("approved_job_count_exposure_mismatch")
    strict_ibm_target_count = _provider_target_count(stage154, provider)
    ready = not blockers
    decision = (
        "FIRST_PROVIDER_APPROVAL_DOSSIER_INCOMPLETE"
        if missing_sources
        else "FIRST_PROVIDER_APPROVAL_DOSSIER_READY_FOR_HUMAN_GO_NO_GO"
        if ready
        else "FIRST_PROVIDER_APPROVAL_DOSSIER_BLOCKED"
    )
    go_considerations = [
        "Stage154 simulated-only rehearsal recommends targeted hardware follow-up, not broad hardware spend.",
        "Stage159 read-only backend preflight is ready.",
        "Stage161 quantifies the pending first-provider run before approval.",
        "Stage160 defines the no-submit post-result analysis sequence needed to answer supported/not-supported.",
    ]
    no_go_considerations = [
        "No real IBM provider result records exist yet.",
        "Credit balance or dollar cost has not been verified by this packet.",
        "The run still requires explicit human approval before any Stage133 live-submit command may execute.",
        "A noisy-hardware robustness or auditability conclusion remains unsupported until Stage138 reaches a terminal decision.",
    ]
    return {
        "schema_version": STAGE162_SCHEMA_VERSION,
        "stage": "stage162_first_provider_approval_dossier",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "first_unlock_provider": provider,
        "approval_phrase_required": approval_phrase_required,
        "stage_decision_records": decision_records,
        "strict_simulated_target_count_for_provider": strict_ibm_target_count,
        "authorized_first_provider_runner_count": (
            stage157.get("authorized_first_provider_runner_count") if isinstance(stage157, dict) else None
        ),
        "authorized_first_provider_job_count": approved_job_count,
        "exposure_job_count": exposure_job_count,
        "exposure_window_count": stage161.get("window_count") if isinstance(stage161, dict) else None,
        "exposure_total_shots": stage161.get("total_shots") if isinstance(stage161, dict) else None,
        "missing_result_record_count": stage161.get("missing_result_record_count") if isinstance(stage161, dict) else None,
        "backend_lookup_ready": stage159.get("backend_lookup_ready") if isinstance(stage159, dict) else None,
        "backend_pending_jobs_at_preflight": (
            stage159.get("backend_metadata", {}).get("pending_jobs") if isinstance(stage159, dict) else None
        ),
        "go_considerations": go_considerations,
        "no_go_considerations": no_go_considerations,
        "blockers": sorted(set(blockers)),
        "approval_state": "awaiting_exact_phrase" if ready else "not_ready_for_approval",
        "no_hardware_submission": True,
        "explicit_user_approval_required": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "credit_balance_verified": False,
        "claim_boundary": {
            "supported": [
                "a single no-submit dossier joining simulated GO, approval packet readiness, backend preflight, post-run sequence, and exposure totals",
                "human GO/NO-GO readiness for the first-provider IBM Runtime run under the exact approval phrase",
                "explicit separation between approval readiness and a noisy-hardware advantage conclusion",
            ],
            "excluded": [
                "hardware job submission",
                "runnable Stage133 command strings",
                "provider credentials or secret values",
                "IBM credit balance or dollar cost verification",
                "real provider result records",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "If and only if the human decision is GO, provide the exact approval phrase. After execution, collect "
            "provider results and run the Stage160 analysis sequence before interpreting robustness or auditability."
        ),
    }


def write_stage162_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "first_unlock_provider": result["first_unlock_provider"],
        "strict_simulated_target_count_for_provider": result["strict_simulated_target_count_for_provider"],
        "authorized_first_provider_runner_count": result["authorized_first_provider_runner_count"],
        "authorized_first_provider_job_count": result["authorized_first_provider_job_count"],
        "exposure_job_count": result["exposure_job_count"],
        "exposure_window_count": result["exposure_window_count"],
        "exposure_total_shots": result["exposure_total_shots"],
        "missing_result_record_count": result["missing_result_record_count"],
        "backend_lookup_ready": result["backend_lookup_ready"],
        "backend_pending_jobs_at_preflight": result["backend_pending_jobs_at_preflight"],
        "blockers": result["blockers"],
        "approval_state": result["approval_state"],
        "no_hardware_submission": result["no_hardware_submission"],
        "explicit_user_approval_required": result["explicit_user_approval_required"],
        "provider_credentials_required": result["provider_credentials_required"],
        "secret_values_recorded": result["secret_values_recorded"],
        "runnable_commands_recorded": result["runnable_commands_recorded"],
        "credit_balance_verified": result["credit_balance_verified"],
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
        writer = csv.DictWriter(handle, fieldnames=("stage_id", "decision", "expected_decision", "ready", "purpose"))
        writer.writeheader()
        for record in result["stage_decision_records"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage162_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"approval_state: {result['approval_state']}")
    print(f"first_unlock_provider: {result['first_unlock_provider']}")
    print(f"exposure_job_count: {result['exposure_job_count']}")
    print(f"exposure_total_shots: {result['exposure_total_shots']}")
    print(f"missing_result_record_count: {result['missing_result_record_count']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
