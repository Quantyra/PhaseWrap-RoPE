from __future__ import annotations

import json
from pathlib import Path

from qrope.stage51_decoder_path_plateau_audit import run_stage51_audit, write_stage51_outputs


def _write_stage(root: Path, stage_name: str, decision: dict[str, object], *, failed_runs: list[object] | None = None) -> None:
    stage_dir = root / stage_name
    stage_dir.mkdir(parents=True)
    (stage_dir / "failed_runs.json").write_text(json.dumps(failed_runs or [], indent=2), encoding="utf-8")
    manifest = {
        "stage": stage_name,
        "status": "completed",
        "method_names": ["no_position", "rope_relative", "phasewrap_bias"],
        "tasks": ["phase_cued_retrieval", "exact_offset_passkey", "tiny_text_fact_qa"],
        "decision": decision,
        "failed_runs_path": f"logs/automated_stage_gates/{stage_name}/failed_runs.json",
    }
    if stage_name == "stage45_matched_decoder_only_gate":
        manifest["gate_decision"] = manifest.pop("decision")
    (stage_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def _build_plateau_inputs(root: Path) -> None:
    _write_stage(root, "stage45_matched_decoder_only_gate", {"decision": "PROMOTION_NOT_SUPPORTED", "best_top1_by_task": {"phase_cued_retrieval": 0.0, "exact_offset_passkey": 0.0}})
    _write_stage(root, "stage46_decoder_capacity_hardening_audit", {"decision": "CAPACITY_NOT_ESTABLISHED", "best_test_task": "tiny_text_fact_qa", "best_test_method": "phasewrap_bias", "best_test_top1": 0.5})
    _write_stage(root, "stage47_adam_decoder_generalization_audit", {"decision": "TRAIN_FIT_WITH_PARTIAL_GENERALIZATION", "retrieval_generalization_task_names": []})
    _write_stage(root, "stage48_adam_decoder_stability_audit", {"decision": "TINY_QA_POSITIVE_NOT_PHASEWRAP_STABLE_RETRIEVAL_FAILED", "retrieval_best_top1": {"phase_cued_retrieval": 0.0, "exact_offset_passkey": 0.0}})
    _write_stage(root, "stage49_copy_decoder_retrieval_repair_audit", {"decision": "COPY_DECODER_PARTIALLY_REPAIRS_RETRIEVAL", "retrieval_best_top1": {"phase_cued_retrieval": 0.1, "exact_offset_passkey": 1.0}, "retrieval_best_methods": {"exact_offset_passkey": "rope_relative"}, "phasewrap_repaired_tasks": []})
    _write_stage(root, "stage50_learned_pointer_generator_decoder_audit", {"decision": "LEARNED_POINTER_GENERATOR_RETRIEVAL_REPAIR_FAILED", "retrieval_best_top1": {"phase_cued_retrieval": 0.1, "exact_offset_passkey": 0.1}, "phasewrap_retrieval_generalized_tasks": []})


def test_stage51_audit_declares_decoder_path_plateau(tmp_path: Path) -> None:
    _build_plateau_inputs(tmp_path)

    result = run_stage51_audit(input_root=tmp_path)

    assert result["stage"] == "stage51_decoder_path_plateau_audit"
    assert result["decision"]["decision"] == "BOUND_DECODER_PATH_PLATEAU"
    assert result["decision"]["fixed_copy_only_generalizes"] is True
    assert result["decision"]["final_stage_retrieval_generalized"] is False
    assert result["decision"]["phasewrap_retrieval_generalized_by_stage"] == {}
    assert "a claim that PhaseWrap-RoPE replaces RoPE" in result["claim_boundary"]["excluded"]


def test_stage51_outputs_are_written(tmp_path: Path) -> None:
    _build_plateau_inputs(tmp_path)
    result = run_stage51_audit(input_root=tmp_path)

    output_dir = tmp_path / "out"
    paths = write_stage51_outputs(result, output_dir)

    assert set(paths) == {"manifest", "results", "summary_csv"}
    manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((output_dir / "results.json").read_text(encoding="utf-8"))
    assert manifest["decision"]["decision"] == "BOUND_DECODER_PATH_PLATEAU"
    assert saved["stage_records"] == result["stage_records"]
    assert (output_dir / "summary.csv").exists()
