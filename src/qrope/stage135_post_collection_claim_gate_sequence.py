from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE135_SCHEMA_VERSION = "qrope_stage135_post_collection_claim_gate_sequence_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE115_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage115_provider_result_collector" / "results.json"
DEFAULT_STAGE134_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage134_runner_result_intake_alignment_audit" / "results.json"
DEFAULT_STAGE113_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage113_job_result_evidence_assembler" / "results.json"
DEFAULT_STAGE101_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage101_known_state_calibration_gate" / "results.json"
DEFAULT_STAGE103_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage103_robustness_metric_preregistration" / "results.json"
DEFAULT_STAGE109_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage109_window_evidence_intake_validator" / "results.json"
DEFAULT_STAGE110_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage110_replicated_advantage_claim_gate" / "results.json"
DEFAULT_STAGE136_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage136_auditability_metric_preregistration" / "results.json"
DEFAULT_STAGE137_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage137_auditability_metric_evaluator" / "results.json"
DEFAULT_STAGE148_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage148_first_provider_statistical_interpretation_gate" / "results.json"
DEFAULT_STAGE138_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage138_objective_claim_gate" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage135_post_collection_claim_gate_sequence"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)

TERMINAL_STAGE110_DECISIONS = {
    "PHASEWRAP_REPLICATED_ADVANTAGE_SUPPORTED_BY_STAGE105_RULE",
    "PHASEWRAP_REPLICATED_ADVANTAGE_NOT_SUPPORTED_BY_STAGE105_RULE",
}
TERMINAL_STAGE138_DECISIONS = {
    "PHASEWRAP_NOISY_HARDWARE_OBJECTIVE_SUPPORTED",
    "PHASEWRAP_NOISY_HARDWARE_OBJECTIVE_NOT_SUPPORTED",
}


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _gate_record(
    *,
    stage_id: str,
    name: str,
    result_path: Path,
    payload: dict[str, Any] | None,
    ready_decisions: set[str],
    purpose: str,
    command: str,
    blocker_hint: str,
) -> dict[str, Any]:
    decision = payload.get("decision") if isinstance(payload, dict) else None
    missing = not isinstance(payload, dict)
    ready = bool(decision in ready_decisions and not missing)
    blockers: list[str] = []
    if missing:
        blockers.append("result_artifact_missing")
    if not ready:
        blockers.append(blocker_hint)
    return {
        "stage_id": stage_id,
        "name": name,
        "result_path": str(result_path.as_posix()),
        "decision": decision,
        "ready": ready,
        "purpose": purpose,
        "command": command,
        "blockers": sorted(set(blockers)),
    }


def _claim_gate_terminal(stage110: dict[str, Any] | None) -> bool:
    return bool(isinstance(stage110, dict) and stage110.get("decision") in TERMINAL_STAGE110_DECISIONS)


def run_stage135_sequence_audit(
    *,
    stage115_results_path: Path = DEFAULT_STAGE115_RESULTS,
    stage134_results_path: Path = DEFAULT_STAGE134_RESULTS,
    stage113_results_path: Path = DEFAULT_STAGE113_RESULTS,
    stage101_results_path: Path = DEFAULT_STAGE101_RESULTS,
    stage103_results_path: Path = DEFAULT_STAGE103_RESULTS,
    stage109_results_path: Path = DEFAULT_STAGE109_RESULTS,
    stage110_results_path: Path = DEFAULT_STAGE110_RESULTS,
    stage136_results_path: Path = DEFAULT_STAGE136_RESULTS,
    stage137_results_path: Path = DEFAULT_STAGE137_RESULTS,
    stage148_results_path: Path = DEFAULT_STAGE148_RESULTS,
    stage138_results_path: Path = DEFAULT_STAGE138_RESULTS,
) -> dict[str, Any]:
    stage115 = _load_json(stage115_results_path)
    stage134 = _load_json(stage134_results_path)
    stage113 = _load_json(stage113_results_path)
    stage101 = _load_json(stage101_results_path)
    stage103 = _load_json(stage103_results_path)
    stage109 = _load_json(stage109_results_path)
    stage110 = _load_json(stage110_results_path)
    stage136 = _load_json(stage136_results_path)
    stage137 = _load_json(stage137_results_path)
    stage148 = _load_json(stage148_results_path)
    stage138 = _load_json(stage138_results_path)
    sources = [
        (stage115_results_path, stage115),
        (stage134_results_path, stage134),
        (stage113_results_path, stage113),
        (stage101_results_path, stage101),
        (stage103_results_path, stage103),
        (stage136_results_path, stage136),
        (stage137_results_path, stage137),
        (stage148_results_path, stage148),
        (stage109_results_path, stage109),
        (stage110_results_path, stage110),
        (stage138_results_path, stage138),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]

    gate_records = [
        _gate_record(
            stage_id="stage115",
            name="provider result collector handoff",
            result_path=stage115_results_path,
            payload=stage115,
            ready_decisions={"PROVIDER_RESULTS_COLLECTED_FOR_STAGE113"},
            purpose="collect every Stage 114 provider/window shard into the Stage 113 provider_job_results.jsonl input",
            command="python scripts/run_stage115_provider_result_collector.py --write-stage113-input",
            blocker_hint="stage115_provider_results_not_collected_for_stage113",
        ),
        _gate_record(
            stage_id="stage134",
            name="runner result intake alignment",
            result_path=stage134_results_path,
            payload=stage134,
            ready_decisions={"RUNNER_RESULT_INTAKE_READY_FOR_STAGE113"},
            purpose="confirm Stage 133 runner output paths and Stage 115 collector shards are aligned and ready",
            command="python scripts/run_stage134_runner_result_intake_alignment_audit.py",
            blocker_hint="stage134_runner_result_intake_not_ready",
        ),
        _gate_record(
            stage_id="stage113",
            name="job result evidence assembler",
            result_path=stage113_results_path,
            payload=stage113,
            ready_decisions={"JOB_RESULTS_ASSEMBLED_INTO_STAGE109_EVIDENCE"},
            purpose="assemble provider job counts into the declared Stage 107 evidence files used by Stage 109",
            command="python scripts/run_stage113_job_result_evidence_assembler.py --write-evidence",
            blocker_hint="stage113_evidence_not_assembled",
        ),
        _gate_record(
            stage_id="stage101",
            name="known-state calibration gate",
            result_path=stage101_results_path,
            payload=stage101,
            ready_decisions={"KNOWN_STATE_CALIBRATION_VERIFIED_READY_FOR_MATCHED_HARDWARE_EXECUTION"},
            purpose="verify bitstring order and known-state calibration before interpreting packet counts",
            command="python scripts/run_stage101_known_state_calibration_gate.py",
            blocker_hint="stage101_calibration_not_verified",
        ),
        _gate_record(
            stage_id="stage103",
            name="robustness metric recomputation",
            result_path=stage103_results_path,
            payload=stage103,
            ready_decisions={"ROBUSTNESS_METRICS_READY_FOR_INTERPRETATION"},
            purpose="recompute preregistered lower-MAE score errors for PhaseWrap and every comparator family",
            command="python scripts/run_stage103_robustness_metric_preregistration.py",
            blocker_hint="stage103_metrics_not_ready_for_interpretation",
        ),
        _gate_record(
            stage_id="stage136",
            name="auditability metric preregistration",
            result_path=stage136_results_path,
            payload=stage136,
            ready_decisions={"AUDITABILITY_METRIC_CONTRACT_READY_HARDWARE_COUNTS_REQUIRED"},
            purpose="bind any auditability wording to complete packet trace coverage and component reconstruction metrics",
            command="python scripts/run_stage136_auditability_metric_preregistration.py",
            blocker_hint="stage136_auditability_metric_contract_not_ready",
        ),
        _gate_record(
            stage_id="stage137",
            name="auditability metric evaluator",
            result_path=stage137_results_path,
            payload=stage137,
            ready_decisions={"AUDITABILITY_METRICS_READY_FOR_CLAIM_GATE"},
            purpose="evaluate component reconstruction auditability metrics from calibrated provider packet counts",
            command="python scripts/run_stage137_auditability_metric_evaluator.py",
            blocker_hint="stage137_auditability_metrics_not_ready",
        ),
        _gate_record(
            stage_id="stage148",
            name="first-provider statistical interpretation gate",
            result_path=stage148_results_path,
            payload=stage148,
            ready_decisions={"FIRST_PROVIDER_STATISTICAL_INTERPRETATION_READY_FOR_CLAIM_GATES"},
            purpose="enforce Stage 146 shot-noise and Stage 147 calibration-confidence guardrails before advantage wording",
            command="python scripts/run_stage148_first_provider_statistical_interpretation_gate.py",
            blocker_hint="stage148_statistical_interpretation_not_ready",
        ),
        _gate_record(
            stage_id="stage109",
            name="window evidence intake validator",
            result_path=stage109_results_path,
            payload=stage109,
            ready_decisions={"WINDOW_EVIDENCE_INTAKE_READY_FOR_STAGE105_AGGREGATION"},
            purpose="verify every independent window has calibration evidence, packet counts, and Stage 103 outputs",
            command="python scripts/run_stage109_window_evidence_intake_validator.py",
            blocker_hint="stage109_window_evidence_not_ready",
        ),
        _gate_record(
            stage_id="stage110",
            name="replicated advantage claim gate",
            result_path=stage110_results_path,
            payload=stage110,
            ready_decisions=TERMINAL_STAGE110_DECISIONS,
            purpose="apply the final all-window replicated advantage rule before any robustness conclusion",
            command="python scripts/run_stage110_replicated_advantage_claim_gate.py",
            blocker_hint="stage110_final_claim_gate_not_terminal",
        ),
        _gate_record(
            stage_id="stage138",
            name="objective claim gate",
            result_path=stage138_results_path,
            payload=stage138,
            ready_decisions=TERMINAL_STAGE138_DECISIONS,
            purpose="combine terminal robustness and auditability branches into final objective wording",
            command="python scripts/run_stage138_objective_claim_gate.py",
            blocker_hint="stage138_objective_claim_gate_not_terminal",
        ),
    ]

    ready_gate_count = sum(1 for record in gate_records if record["ready"])
    final_claim_gate_terminal = bool(isinstance(stage138, dict) and stage138.get("decision") in TERMINAL_STAGE138_DECISIONS)
    all_ready = ready_gate_count == len(gate_records) and not missing_sources
    decision = (
        "POST_COLLECTION_CLAIM_GATE_SEQUENCE_COMPLETE_TERMINAL_CLAIM_REACHED"
        if all_ready and final_claim_gate_terminal
        else "POST_COLLECTION_CLAIM_GATE_SEQUENCE_PREPARED_EXECUTION_BLOCKED"
    )

    return {
        "schema_version": STAGE135_SCHEMA_VERSION,
        "stage": "stage135_post_collection_claim_gate_sequence",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "gate_count": len(gate_records),
        "ready_gate_count": ready_gate_count,
        "blocked_gate_count": len(gate_records) - ready_gate_count,
        "final_claim_gate_terminal": final_claim_gate_terminal,
        "replicated_advantage_count": stage110.get("replicated_advantage_count") if isinstance(stage110, dict) else None,
        "gate_records": gate_records,
        "ordered_command_sequence": [record["command"] for record in gate_records],
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "an explicit post-collection rerun sequence from Stage 115 collection through Stage 138 objective claim gating",
                "a deterministic no-claim boundary when any downstream collection, assembly, calibration, metric, intake, or claim gate is blocked",
                "a terminal decision distinction between replicated PhaseWrap advantage supported and not supported by the preregistered rule",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "new provider result records",
                "a noisy-hardware robustness or auditability conclusion before Stage 138 reaches a terminal supported/not-supported decision",
                "provider-wide or transformer-scale superiority beyond the matched fixed-width evidence gates",
            ],
        },
        "next_gate": (
            "Clear the first blocked gate in order. No noisy-hardware robustness or auditability advantage conclusion is "
            "allowed until Stage 138 reaches a terminal supported/not-supported decision after Stage 115, Stage 134, "
            "Stage 113, Stage 101, Stage 103, Stage 136, Stage 137, Stage 148, Stage 109, and Stage 110 are ready."
        ),
    }


def write_stage135_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "gate_count": result["gate_count"],
        "ready_gate_count": result["ready_gate_count"],
        "blocked_gate_count": result["blocked_gate_count"],
        "final_claim_gate_terminal": result["final_claim_gate_terminal"],
        "replicated_advantage_count": result["replicated_advantage_count"],
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
                "stage_id",
                "name",
                "decision",
                "ready",
                "result_path",
                "command",
                "blockers",
            ),
        )
        writer.writeheader()
        for record in result["gate_records"]:
            writer.writerow(
                {
                    "stage_id": record["stage_id"],
                    "name": record["name"],
                    "decision": record["decision"],
                    "ready": record["ready"],
                    "result_path": record["result_path"],
                    "command": record["command"],
                    "blockers": "; ".join(record["blockers"]),
                }
            )
    return paths


def print_stage135_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"ready_gate_count: {result['ready_gate_count']}/{result['gate_count']}")
    print(f"final_claim_gate_terminal: {result['final_claim_gate_terminal']}")
    print(f"replicated_advantage_count: {result['replicated_advantage_count']}")
    print(f"next_gate: {result['next_gate']}")
