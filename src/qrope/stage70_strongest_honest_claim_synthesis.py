from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .stage45_matched_decoder_only_gate import METHOD_NAMES
from .stage52_two_block_decoder_feasibility_audit import GENERALIZATION_TOP1_THRESHOLD


STAGE70_SCHEMA_VERSION = "qrope_stage70_strongest_honest_claim_synthesis_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage70_strongest_honest_claim_synthesis"
ORIGINAL_RETRIEVAL_TASKS = ("phase_cued_retrieval", "exact_offset_passkey")


SOURCE_STAGE_DIRS: tuple[str, ...] = (
    "stage44_compact_diagnostic_plateau_audit",
    "stage45_matched_decoder_only_gate",
    "stage48_adam_decoder_stability_audit",
    "stage51_decoder_path_plateau_audit",
    "stage55_row_metadata_cue_copy_upper_bound_audit",
    "stage60_support_fallback_strictness_audit",
    "stage64_two_block_pointer_generator_capacity_audit",
    "stage65_pointer_generator_length_curriculum_audit",
    "stage66_positional_copy_expert_audit",
    "stage67_content_key_retrieval_audit",
    "stage68_content_key_auxiliary_transfer_audit",
    "stage69_original_multitask_pointer_generator_audit",
    "stage71_positional_bias_copy_upper_bound_audit",
    "stage72_phase_cued_bias_tie_support_audit",
    "stage73_phase_cued_period_pair_support_audit",
    "stage74_leave_one_seed_query_support_audit",
    "stage75_learned_query_support_head_audit",
    "stage76_integrated_support_copy_head_audit",
    "stage77_auxiliary_support_copy_head_audit",
    "stage78_support_coverage_split_audit",
    "stage79_support_complete_auxiliary_copy_head_audit",
    "stage80_support_routed_token_selector_audit",
    "stage81_soft_support_routed_token_selector_audit",
    "stage82_learned_support_routing_head_audit",
    "stage83_nonlinear_support_routing_bridge_audit",
    "stage84_support_auxiliary_pointer_generator_audit",
)

DOCUMENTED_SOURCE_ARTIFACTS: tuple[str, ...] = (
    "docs/research/q-rope-stage44-compact-diagnostic-plateau-audit-v1.md",
    "docs/research/q-rope-stage45-matched-decoder-only-gate-v1.md",
    "docs/research/q-rope-stage48-adam-decoder-stability-audit-v1.md",
    "docs/research/q-rope-stage51-decoder-path-plateau-audit-v1.md",
    "docs/research/q-rope-stage55-row-metadata-cue-copy-upper-bound-audit-v1.md",
    "docs/research/q-rope-stage60-support-fallback-strictness-audit-v1.md",
    "docs/research/q-rope-stage71-positional-bias-copy-upper-bound-audit-v1.md",
    "docs/research/q-rope-stage72-phase-cued-bias-tie-support-audit-v1.md",
    "docs/research/q-rope-stage73-phase-cued-period-pair-support-audit-v1.md",
    "docs/research/q-rope-stage74-leave-one-seed-query-support-audit-v1.md",
    "docs/research/q-rope-stage75-learned-query-support-head-audit-v1.md",
    "docs/research/q-rope-stage76-integrated-support-copy-head-audit-v1.md",
    "docs/research/q-rope-stage77-auxiliary-support-copy-head-audit-v1.md",
    "docs/research/q-rope-stage78-support-coverage-split-audit-v1.md",
    "docs/research/q-rope-stage79-support-complete-auxiliary-copy-head-audit-v1.md",
    "docs/research/q-rope-stage80-support-routed-token-selector-audit-v1.md",
    "docs/research/q-rope-stage81-soft-support-routed-token-selector-audit-v1.md",
    "docs/research/q-rope-stage82-learned-support-routing-head-audit-v1.md",
    "docs/research/q-rope-stage83-nonlinear-support-routing-bridge-audit-v1.md",
    "docs/research/q-rope-stage84-support-auxiliary-pointer-generator-audit-v1.md",
)


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _source_manifests(artifact_root: Path) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    source_artifacts: list[str] = []
    missing_source_artifacts: list[str] = []
    manifests: list[dict[str, Any]] = []
    for source_dir in SOURCE_STAGE_DIRS:
        manifest_path = artifact_root / source_dir / "manifest.json"
        source_artifacts.append(str(manifest_path.as_posix()))
        manifest = _load_json(manifest_path)
        if manifest is None:
            missing_source_artifacts.append(str(manifest_path.as_posix()))
            continue
        manifests.append(manifest)
    source_artifacts.extend(DOCUMENTED_SOURCE_ARTIFACTS)
    return manifests, source_artifacts, missing_source_artifacts


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential synthesis of current fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap evidence.",
            "A bounded strongest-honest-claim checkpoint preserving both positive evidence and failure modes.",
            "A reviewer gate for deciding whether the next step should be stronger matched transformer evidence.",
        ],
        "excluded": [
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that PhaseWrap-RoPE is currently better than RoPE in fair matched transformer settings",
            "a claim that content-key row redesign success is positional-method promotion evidence",
            "production transformer superiority",
            "full transformer-scale validation",
            "broad quantum advantage",
        ],
    }


def _retrieval_best_top1(manifest: dict[str, Any], task: str) -> float | None:
    value = manifest.get("decision", {}).get("retrieval_best_top1", {}).get(task)
    return float(value) if isinstance(value, int | float) else None


def _retrieval_best_method(manifest: dict[str, Any], task: str) -> str | None:
    value = manifest.get("decision", {}).get("retrieval_best_methods", {}).get(task)
    return value if isinstance(value, str) else None


def _is_original_retrieval_manifest(manifest: dict[str, Any]) -> bool:
    tasks = set(manifest.get("tasks", []))
    return all(task in tasks for task in ORIGINAL_RETRIEVAL_TASKS)


def _stage67_all_method_success(manifests: list[dict[str, Any]]) -> bool:
    required_methods = set(METHOD_NAMES)
    for manifest in manifests:
        if manifest.get("stage") != "stage67_content_key_retrieval_audit":
            continue
        decision = manifest.get("decision", {})
        methods = set(decision.get("retrieval_generalized_methods", []))
        top1 = _retrieval_best_top1(manifest, "content_key_retrieval")
        return required_methods.issubset(methods) and top1 is not None and top1 >= GENERALIZATION_TOP1_THRESHOLD
    return False


def _promotion_review_supported(manifests: list[dict[str, Any]]) -> bool:
    for manifest in manifests:
        if not _is_original_retrieval_manifest(manifest):
            continue
        all_generalize = True
        phasewrap_leads = True
        for task in ORIGINAL_RETRIEVAL_TASKS:
            top1 = _retrieval_best_top1(manifest, task)
            method = _retrieval_best_method(manifest, task)
            if top1 is None or top1 < GENERALIZATION_TOP1_THRESHOLD:
                all_generalize = False
            if method is None or not method.startswith("phasewrap"):
                phasewrap_leads = False
        if all_generalize and phasewrap_leads:
            return True
    return False


def _original_retrieval_failures(manifests: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for manifest in manifests:
        if not _is_original_retrieval_manifest(manifest):
            continue
        decision = manifest.get("decision", {})
        top1_by_task = decision.get("retrieval_best_top1", {})
        if not isinstance(top1_by_task, dict):
            continue
        row = {
            "stage": manifest.get("stage"),
            "decision": decision.get("decision"),
            "retrieval_best_top1": {
                task: top1_by_task.get(task)
                for task in ORIGINAL_RETRIEVAL_TASKS
                if task in top1_by_task
            },
            "retrieval_best_methods": {
                task: decision.get("retrieval_best_methods", {}).get(task)
                for task in ORIGINAL_RETRIEVAL_TASKS
                if task in top1_by_task
            },
            "tiny_text_best_top1": decision.get("tiny_text_best_top1"),
            "capacity_established": decision.get("capacity_established"),
        }
        rows.append(row)
    return rows


def _best_tiny_text(manifests: list[dict[str, Any]]) -> dict[str, Any] | None:
    best: dict[str, Any] | None = None
    for manifest in manifests:
        stage = str(manifest.get("stage"))
        if "pointer_generator" not in stage:
            continue
        decision = manifest.get("decision", {})
        value = decision.get("tiny_text_best_top1")
        if not isinstance(value, int | float):
            continue
        candidate = {
            "stage": stage,
            "method": decision.get("tiny_text_best_method"),
            "top1": float(value),
        }
        if best is None or candidate["top1"] > best["top1"]:
            best = candidate
    return best


def _positive_evidence(manifests: list[dict[str, Any]]) -> list[dict[str, Any]]:
    positives: list[dict[str, Any]] = [
        {
            "evidence": "Stage 4 hardware/readout witnesses remain bounded positive evidence for committed packet/backend/date/calibration contexts.",
            "claim_limit": "This is not transformer-scale superiority, broad quantum advantage, or cross-backend generalization without additional replication.",
            "source": "docs/publication/quickstart-results-summary-v1.md",
        },
        {
            "evidence": "Stage 44 records selected compact diagnostic recovery as a plateau rather than a promotion claim.",
            "claim_limit": "Compact diagnostics do not establish decoder-only transformer replacement.",
            "source": "docs/research/q-rope-stage44-compact-diagnostic-plateau-audit-v1.md",
        },
    ]
    if _stage67_all_method_success(manifests):
        positives.append(
            {
                "evidence": "Stage 67 solves visible content-key retrieval at held-out lengths for every tested method, including no_position.",
                "claim_limit": "Because all methods solve it, this validates the harness and row design but is not PhaseWrap-specific promotion evidence.",
                "source": "stage67_content_key_retrieval_audit",
            }
        )
    tiny_text = _best_tiny_text(manifests)
    if tiny_text is not None:
        positives.append(
            {
                "evidence": f"Recent pointer-generator variants preserve capacity and reach tiny-text held-out top-1 {tiny_text['top1']:.6f}.",
                "claim_limit": "Tiny-text QA positives are mixed downstream evidence, not original retrieval generalization.",
                "source": tiny_text["stage"],
                "method": tiny_text["method"],
            }
        )
    return positives


def _failure_modes(manifests: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = _original_retrieval_failures(manifests)
    failures: list[dict[str, Any]] = [
        {
            "failure": "No fair matched decoder/pointer-generator artifact currently supports RoPE replacement or positional-method promotion.",
            "evidence": "Recent original-row audits do not make PhaseWrap lead and generalize both original retrieval tasks.",
        },
        {
            "failure": "Content-key retrieval success does not transfer back to original phase-cued or exact-offset retrieval.",
            "evidence": "Stage 68 preserves capacity but reports no generalized original retrieval tasks.",
        },
    ]
    for row in rows:
        top1_values = [value for value in row["retrieval_best_top1"].values() if isinstance(value, int | float)]
        solved_but_not_promotional = len(top1_values) == len(ORIGINAL_RETRIEVAL_TASKS) and all(
            float(value) >= GENERALIZATION_TOP1_THRESHOLD for value in top1_values
        )
        failures.append(
            {
                "failure": (
                    "Original held-out retrieval is solved only as a non-promotional or method-nonspecific diagnostic."
                    if solved_but_not_promotional
                    else "Original held-out retrieval remains unrepaired in a recent fair-comparison audit."
                ),
                "evidence": (
                    "The artifact crosses retrieval thresholds, but does not make a PhaseWrap-led fair learned decoder claim."
                    if solved_but_not_promotional
                    else "At least one original retrieval task remains below the generalization threshold."
                ),
                "stage": row["stage"],
                "decision": row["decision"],
                "retrieval_best_top1": row["retrieval_best_top1"],
                "retrieval_best_methods": row["retrieval_best_methods"],
                "capacity_established": row["capacity_established"],
            }
        )
    return failures


def _decision(manifests: list[dict[str, Any]], missing_source_artifacts: list[str]) -> dict[str, Any]:
    if _promotion_review_supported(manifests):
        decision = "PROMOTION_REVIEW_REQUIRED"
        boundary = "At least one original-retrieval fair-comparison artifact generalizes both retrieval tasks with PhaseWrap leading; review before updating claims."
    elif _stage67_all_method_success(manifests) and not _promotion_review_supported(manifests):
        decision = "BOUND_STRONGEST_HONEST_CLAIM_WITH_RETRIEVAL_FAILURES"
        boundary = "The strongest honest claim remains bounded: PhaseWrap-RoPE has compact/auditable evidence and mixed diagnostics, while fair matched original retrieval does not yet support RoPE replacement."
    else:
        decision = "BOUND_STRONGEST_HONEST_CLAIM_INCOMPLETE_EVIDENCE"
        boundary = "The synthesis is bounded, but key source artifacts are incomplete or insufficient for the fuller evidence summary."
    return {
        "decision": decision,
        "claim_boundary": boundary,
        "generalization_top1_threshold": GENERALIZATION_TOP1_THRESHOLD,
        "promotion_review_supported": decision == "PROMOTION_REVIEW_REQUIRED",
        "content_key_all_method_success": _stage67_all_method_success(manifests),
        "missing_source_artifact_count": len(missing_source_artifacts),
    }


def run_stage70_synthesis(
    *,
    artifact_root: Path = DEFAULT_ARTIFACT_ROOT,
    method_names: tuple[str, ...] = METHOD_NAMES,
) -> dict[str, Any]:
    manifests, source_artifacts, missing_source_artifacts = _source_manifests(artifact_root)
    result = {
        "schema_version": STAGE70_SCHEMA_VERSION,
        "stage": "stage70_strongest_honest_claim_synthesis",
        "status": "completed",
        "source_stage": "stage84_support_auxiliary_pointer_generator_audit",
        "source_artifacts": source_artifacts,
        "missing_source_artifacts": missing_source_artifacts,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "method_names": list(method_names),
        "tasks": list(ORIGINAL_RETRIEVAL_TASKS) + ["content_key_retrieval", "tiny_text_fact_qa"],
        "claim_boundary": _claim_boundary(),
        "strongest_honest_claim": (
            "PhaseWrap-RoPE is a compact, auditable phase-wrap positional scoring rule with reproducible "
            "hardware/readout witnesses and mixed toy/diagnostic downstream evidence. Hard and soft "
            "support-routing diagnostics show the row family can be solved, but learned scalar, nonlinear, "
            "and in-decoder support-supervised routes still fail held-out support-to-token retrieval; fair "
            "matched decoder/pointer-generator audits do not yet support RoPE replacement or positional-method promotion."
        ),
        "unsupported_claims": [
            "PhaseWrap-RoPE replaces RoPE.",
            "PhaseWrap-RoPE is better than RoPE under current fair matched transformer comparisons.",
            "Content-key retrieval success is PhaseWrap-specific evidence.",
            "Tiny-text QA gains establish original retrieval generalization.",
            "Bounded hardware/readout witnesses establish production language-model quality gains.",
        ],
        "positive_evidence": _positive_evidence(manifests),
        "failure_modes": _failure_modes(manifests),
        "loaded_source_stage_count": len(manifests),
        "loaded_source_stages": [str(manifest.get("stage")) for manifest in manifests],
        "reviewer_next_gate": (
            "Run a stronger matched decoder-only transformer or original-row mechanism that improves held-out "
            "support-to-token retrieval for phase-cued and exact-offset rows before evaluating positional-method promotion."
        ),
    }
    result["decision"] = _decision(manifests, missing_source_artifacts)
    return result


def write_stage70_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "method_names": result["method_names"],
        "tasks": result["tasks"],
        "source_stage": result["source_stage"],
        "source_artifacts": result["source_artifacts"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "decision": result["decision"],
        "claim_boundary": result["claim_boundary"],
        "strongest_honest_claim": result["strongest_honest_claim"],
        "unsupported_claims": result["unsupported_claims"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "reviewer_next_gate": result["reviewer_next_gate"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    summary_rows = [
        {"section": "decision", "item": "decision", "value": result["decision"]["decision"]},
        {"section": "decision", "item": "claim_boundary", "value": result["decision"]["claim_boundary"]},
        {"section": "claim", "item": "strongest_honest_claim", "value": result["strongest_honest_claim"]},
        {"section": "next_gate", "item": "reviewer_next_gate", "value": result["reviewer_next_gate"]},
    ]
    summary_rows.extend(
        {"section": "unsupported_claim", "item": str(index), "value": claim}
        for index, claim in enumerate(result["unsupported_claims"], start=1)
    )
    summary_rows.extend(
        {"section": "positive_evidence", "item": str(index), "value": item["evidence"]}
        for index, item in enumerate(result["positive_evidence"], start=1)
    )
    summary_rows.extend(
        {"section": "failure_mode", "item": str(index), "value": item["failure"]}
        for index, item in enumerate(result["failure_modes"], start=1)
    )
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("section", "item", "value"))
        writer.writeheader()
        writer.writerows(summary_rows)
    return paths


def print_stage70_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']['decision']}")
    print(f"claim_boundary: {result['decision']['claim_boundary']}")
    print(f"strongest_honest_claim: {result['strongest_honest_claim']}")
    print(f"missing_source_artifacts: {len(result['missing_source_artifacts'])}")
