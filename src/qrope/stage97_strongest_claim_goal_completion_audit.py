from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .stage45_matched_decoder_only_gate import METHOD_NAMES


STAGE97_SCHEMA_VERSION = "qrope_stage97_strongest_claim_goal_completion_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage97_strongest_claim_goal_completion_audit"
OBJECTIVE = (
    "Find the strongest honest claim PhaseWrap-RoPE can support under fair "
    "RoPE/ALiBI/sinusoidal/no-position comparisons, preserving both positive evidence and failure modes."
)


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential completion audit for the active strongest-honest-claim objective.",
            "Requirement-by-requirement evidence that the current bounded claim is packaged with positives, failures, exclusions, intervals, and next gate.",
            "A completion decision for the research-claim boundary objective, not a promotion decision.",
        ],
        "excluded": [
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that PhaseWrap-RoPE is currently better than RoPE in fair matched transformer settings",
            "a claim that the promotion gate is satisfied",
            "production transformer superiority",
            "full transformer-scale validation",
            "broad quantum advantage",
        ],
    }


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _stage96_path(artifact_root: Path) -> Path:
    return artifact_root / "stage96_claim_card_audit" / "results.json"


def _contains_phrase(items: list[str], phrase: str) -> bool:
    return any(phrase.lower() in item.lower() for item in items)


def _requirement_rows(stage96: dict[str, Any] | None, missing_source_artifacts: list[str]) -> list[dict[str, Any]]:
    if stage96 is None:
        return [
            {
                "requirement": "stage96_claim_card_present",
                "status": "failed",
                "evidence": "Stage96 claim-card results are missing.",
            }
        ]
    claim_card = stage96.get("claim_card", {})
    decision = stage96.get("decision", {})
    strongest_claim = claim_card.get("strongest_honest_claim")
    supported_evidence = claim_card.get("supported_evidence", [])
    failure_modes = claim_card.get("failure_modes", [])
    unsupported_claims = claim_card.get("unsupported_claims", [])
    promotion_gate = claim_card.get("promotion_gate_status", {})
    return [
        {
            "requirement": "stage96_claim_card_present",
            "status": "passed" if stage96.get("stage") == "stage96_claim_card_audit" and not missing_source_artifacts else "failed",
            "evidence": "Stage96 claim-card results exist and have no missing source artifacts.",
        },
        {
            "requirement": "strongest_honest_claim_present",
            "status": "passed" if isinstance(strongest_claim, str) and "PhaseWrap-RoPE is a compact" in strongest_claim else "failed",
            "evidence": strongest_claim or "No strongest claim text found.",
        },
        {
            "requirement": "fair_comparison_frame_preserved",
            "status": "passed" if set(METHOD_NAMES).issubset(set(stage96.get("method_names", []))) else "failed",
            "evidence": "Method set includes no_position, sinusoidal, ALiBI, RoPE-relative, and PhaseWrap variants.",
        },
        {
            "requirement": "positive_evidence_preserved",
            "status": "passed" if len(supported_evidence) >= 4 else "failed",
            "evidence": f"{len(supported_evidence)} positive-evidence entries are present.",
        },
        {
            "requirement": "failure_modes_preserved",
            "status": "passed" if len(failure_modes) >= 4 else "failed",
            "evidence": f"{len(failure_modes)} failure-mode entries are present.",
        },
        {
            "requirement": "unsupported_claims_excluded",
            "status": (
                "passed"
                if _contains_phrase(unsupported_claims, "replaces RoPE")
                and _contains_phrase(unsupported_claims, "better than RoPE")
                and _contains_phrase(unsupported_claims, "production language-model quality")
                else "failed"
            ),
            "evidence": json.dumps(unsupported_claims, sort_keys=True),
        },
        {
            "requirement": "promotion_boundary_preserved",
            "status": (
                "passed"
                if promotion_gate.get("ready") is False
                and "free_learned_phasewrap_original_retrieval_solve" in promotion_gate.get("failed_requirements", [])
                else "failed"
            ),
            "evidence": json.dumps(promotion_gate, sort_keys=True),
        },
        {
            "requirement": "headline_intervals_preserved",
            "status": "passed" if decision.get("headline_intervals_present") is True and claim_card.get("headline_intervals") else "failed",
            "evidence": f"{len(claim_card.get('headline_intervals', []))} headline interval rows are present.",
        },
        {
            "requirement": "next_gate_preserved",
            "status": "passed" if isinstance(claim_card.get("reviewer_next_gate"), str) and "stronger learned matched decoder" in claim_card["reviewer_next_gate"] else "failed",
            "evidence": claim_card.get("reviewer_next_gate") or "No next gate found.",
        },
    ]


def _decision(requirement_rows: list[dict[str, Any]]) -> dict[str, Any]:
    failed = [row["requirement"] for row in requirement_rows if row["status"] != "passed"]
    if failed:
        return {
            "decision": "ACTIVE_GOAL_COMPLETION_AUDIT_FAILED",
            "claim_boundary": "The active strongest-claim objective is not yet fully proven by current artifacts.",
            "active_goal_complete": False,
            "failed_requirements": failed,
        }
    return {
        "decision": "ACTIVE_GOAL_COMPLETE_BOUND_STRONGEST_CLAIM",
        "claim_boundary": "The active strongest-claim objective is complete as a bounded claim: promotion remains unsupported, but the strongest honest claim, positives, failures, exclusions, intervals, and next gate are all packaged.",
        "active_goal_complete": True,
        "failed_requirements": [],
    }


def run_stage97_audit(*, artifact_root: Path = DEFAULT_ARTIFACT_ROOT, method_names: tuple[str, ...] = METHOD_NAMES) -> dict[str, Any]:
    source_path = _stage96_path(artifact_root)
    stage96 = _load_json(source_path)
    missing_source_artifacts = [] if stage96 is not None else [str(source_path.as_posix())]
    requirement_rows = _requirement_rows(stage96, missing_source_artifacts)
    result = {
        "schema_version": STAGE97_SCHEMA_VERSION,
        "stage": "stage97_strongest_claim_goal_completion_audit",
        "status": "completed",
        "objective": OBJECTIVE,
        "source_stage": "stage96_claim_card_audit",
        "source_artifacts": [str(source_path.as_posix())],
        "missing_source_artifacts": missing_source_artifacts,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "method_names": list(method_names),
        "tasks": ["phase_cued_retrieval", "exact_offset_passkey", "content_key_retrieval", "tiny_text_fact_qa"],
        "claim_boundary": _claim_boundary(),
        "requirement_rows": requirement_rows,
    }
    result["decision"] = _decision(requirement_rows)
    return result


def write_stage97_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "source_stage": result["source_stage"],
        "source_artifacts": result["source_artifacts"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "method_names": result["method_names"],
        "tasks": result["tasks"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "decision": result["decision"],
        "claim_boundary": result["claim_boundary"],
        "missing_source_artifacts": result["missing_source_artifacts"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("requirement", "status", "evidence"))
        writer.writeheader()
        writer.writerows(result["requirement_rows"])
    return paths


def print_stage97_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']['decision']}")
    print(f"claim_boundary: {result['decision']['claim_boundary']}")
    print(f"active_goal_complete: {result['decision']['active_goal_complete']}")
