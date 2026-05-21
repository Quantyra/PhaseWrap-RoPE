from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


STAGE51_SCHEMA_VERSION = "qrope_stage51_decoder_path_plateau_audit_v1"
DEFAULT_INPUT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_OUTPUT_DIR = DEFAULT_INPUT_ROOT / "stage51_decoder_path_plateau_audit"
RETRIEVAL_TASKS = ("phase_cued_retrieval", "exact_offset_passkey")
TINY_TEXT_TASK = "tiny_text_fact_qa"
RETRIEVAL_TOP1_THRESHOLD = 0.50


@dataclass(frozen=True)
class StageInput:
    stage_number: int
    stage_name: str
    manifest_path: Path
    diagnostic_class: str


STAGE_INPUTS = (
    StageInput(45, "stage45_matched_decoder_only_gate", Path("stage45_matched_decoder_only_gate") / "manifest.json", "matched_one_block_decoder_gate"),
    StageInput(46, "stage46_decoder_capacity_hardening_audit", Path("stage46_decoder_capacity_hardening_audit") / "manifest.json", "one_block_capacity_hardening"),
    StageInput(47, "stage47_adam_decoder_generalization_audit", Path("stage47_adam_decoder_generalization_audit") / "manifest.json", "one_block_adam_generalization"),
    StageInput(48, "stage48_adam_decoder_stability_audit", Path("stage48_adam_decoder_stability_audit") / "manifest.json", "one_block_adam_stability"),
    StageInput(49, "stage49_copy_decoder_retrieval_repair_audit", Path("stage49_copy_decoder_retrieval_repair_audit") / "manifest.json", "fixed_copy_decoder_repair"),
    StageInput(50, "stage50_learned_pointer_generator_decoder_audit", Path("stage50_learned_pointer_generator_decoder_audit") / "manifest.json", "learned_pointer_generator_decoder"),
)


def _read_manifest(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"missing manifest file: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _decision_record(manifest: dict[str, Any]) -> dict[str, Any]:
    return manifest.get("decision") or manifest.get("gate_decision") or {}


def _failed_run_count(input_root: Path, manifest: dict[str, Any]) -> int | None:
    failed_path = manifest.get("failed_runs_path")
    if not failed_path:
        return None
    path = input_root / Path(failed_path).relative_to("logs/automated_stage_gates")
    if not path.exists():
        raise FileNotFoundError(f"missing failed-runs file: {path}")
    failed = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(failed, list):
        raise ValueError(f"failed-runs file is not a list: {path}")
    return len(failed)


def _stage_record(input_root: Path, stage_input: StageInput) -> dict[str, Any]:
    manifest = _read_manifest(input_root / stage_input.manifest_path)
    decision = _decision_record(manifest)
    retrieval_best_top1 = decision.get("retrieval_best_top1") or decision.get("best_top1_by_task") or {}
    retrieval_generalized = []
    for task in RETRIEVAL_TASKS:
        value = retrieval_best_top1.get(task)
        if value is not None and float(value) >= RETRIEVAL_TOP1_THRESHOLD:
            retrieval_generalized.append(task)
    return {
        "stage_number": stage_input.stage_number,
        "stage_name": stage_input.stage_name,
        "diagnostic_class": stage_input.diagnostic_class,
        "status": manifest.get("status"),
        "decision": decision.get("decision"),
        "claim_boundary": decision.get("claim_boundary"),
        "method_names": manifest.get("method_names", []),
        "tasks": manifest.get("tasks", []),
        "retrieval_best_methods": decision.get("retrieval_best_methods") or decision.get("best_method_by_task") or {},
        "retrieval_best_top1": retrieval_best_top1,
        "retrieval_generalized_tasks": retrieval_generalized,
        "phasewrap_retrieval_generalized_tasks": decision.get("phasewrap_retrieval_generalized_tasks")
        or decision.get("phasewrap_repaired_tasks")
        or [],
        "tiny_text_best_method": decision.get("tiny_text_best_method") or decision.get("best_test_method"),
        "tiny_text_best_top1": decision.get("tiny_text_best_top1") or (
            decision.get("best_test_top1") if decision.get("best_test_task") == TINY_TEXT_TASK else None
        ),
        "failed_run_count": _failed_run_count(input_root, manifest),
    }


def _decoder_path_decision(stage_records: list[dict[str, Any]]) -> dict[str, Any]:
    final = stage_records[-1]
    any_retrieval_generalized = {
        record["stage_name"]: record["retrieval_generalized_tasks"]
        for record in stage_records
        if record["retrieval_generalized_tasks"]
    }
    phasewrap_retrieval_generalized = {
        record["stage_name"]: record["phasewrap_retrieval_generalized_tasks"]
        for record in stage_records
        if record["phasewrap_retrieval_generalized_tasks"]
    }
    learned_stage_generalizes = bool(final["retrieval_generalized_tasks"])
    fixed_copy_only_generalizes = (
        "stage49_copy_decoder_retrieval_repair_audit" in any_retrieval_generalized
        and not learned_stage_generalizes
    )
    all_failed_runs_retained = all(record["failed_run_count"] == 0 for record in stage_records if record["failed_run_count"] is not None)
    plateau = fixed_copy_only_generalizes and not phasewrap_retrieval_generalized and all_failed_runs_retained
    return {
        "decision": "BOUND_DECODER_PATH_PLATEAU" if plateau else "CONTINUE_DECODER_PATH",
        "retrieval_top1_threshold": RETRIEVAL_TOP1_THRESHOLD,
        "any_retrieval_generalized_by_stage": any_retrieval_generalized,
        "phasewrap_retrieval_generalized_by_stage": phasewrap_retrieval_generalized,
        "fixed_copy_only_generalizes": fixed_copy_only_generalizes,
        "final_stage_name": final["stage_name"],
        "final_stage_retrieval_generalized": learned_stage_generalizes,
        "all_failed_runs_retained_empty": all_failed_runs_retained,
        "claim_boundary": (
            "Stages 45-50 form a bounded decoder-path plateau: optimizer and output repairs expose useful diagnostics, "
            "but learned decoder retrieval generalization is not established and PhaseWrap does not lead a repaired retrieval lane."
            if plateau
            else "The decoder path has not yet reached a bounded plateau decision."
        ),
        "next_gate": (
            "Move beyond one-block and pointer-generator repairs into a materially stronger matched decoder-only transformer "
            "before broadening positional-method claims."
            if plateau
            else "Continue the decoder path only with a named repair that directly targets retrieval generalization."
        ),
    }


def run_stage51_audit(
    *,
    input_root: Path = DEFAULT_INPUT_ROOT,
    stage_inputs: tuple[StageInput, ...] = STAGE_INPUTS,
) -> dict[str, Any]:
    stage_records = [_stage_record(input_root, stage_input) for stage_input in stage_inputs]
    return {
        "schema_version": STAGE51_SCHEMA_VERSION,
        "stage": "stage51_decoder_path_plateau_audit",
        "source_stages": [record["stage_name"] for record in stage_records],
        "retrieval_tasks": list(RETRIEVAL_TASKS),
        "tiny_text_task": TINY_TEXT_TASK,
        "stage_records": stage_records,
        "decision": _decoder_path_decision(stage_records),
        "claim_boundary": {
            "supported": [
                "A reproducible plateau audit over the matched one-block, fixed-copy, and learned pointer-generator decoder path.",
                "A bounded claim that output repairs diagnose bottlenecks without establishing learned retrieval generation.",
                "A negative claim that Stages 45-50 do not justify RoPE-replacement or production-transformer claims.",
            ],
            "excluded": [
                "production transformer superiority",
                "full transformer-scale validation",
                "a claim that PhaseWrap-RoPE replaces RoPE",
                "broad quantum advantage",
                "a claim that the Stage 49 fixed-copy repair solves learned retrieval generation",
            ],
        },
    }


def write_stage51_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "source_stages": result["source_stages"],
        "retrieval_tasks": result["retrieval_tasks"],
        "decision": result["decision"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "results": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    rows = []
    for record in result["stage_records"]:
        rows.append(
            {
                "stage_number": record["stage_number"],
                "stage_name": record["stage_name"],
                "diagnostic_class": record["diagnostic_class"],
                "decision": record["decision"],
                "retrieval_generalized_tasks": ";".join(record["retrieval_generalized_tasks"]),
                "phasewrap_retrieval_generalized_tasks": ";".join(record["phasewrap_retrieval_generalized_tasks"]),
                "tiny_text_best_method": record["tiny_text_best_method"],
                "tiny_text_best_top1": record["tiny_text_best_top1"],
                "failed_run_count": record["failed_run_count"],
            }
        )
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return paths


def print_stage51_table(result: dict[str, Any]) -> None:
    columns = (
        "stage_name",
        "decision",
        "retrieval_generalized_tasks",
        "phasewrap_retrieval_generalized_tasks",
        "tiny_text_best_method",
        "failed_run_count",
    )
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for record in result["stage_records"]:
        row = {
            "stage_name": record["stage_name"],
            "decision": record["decision"],
            "retrieval_generalized_tasks": ",".join(record["retrieval_generalized_tasks"]) or "none",
            "phasewrap_retrieval_generalized_tasks": ",".join(record["phasewrap_retrieval_generalized_tasks"]) or "none",
            "tiny_text_best_method": record["tiny_text_best_method"],
            "failed_run_count": record["failed_run_count"],
        }
        print(" | ".join(str(row[column]) for column in columns))
    print(f"decision: {result['decision']['decision']}")
    print(f"claim_boundary: {result['decision']['claim_boundary']}")
