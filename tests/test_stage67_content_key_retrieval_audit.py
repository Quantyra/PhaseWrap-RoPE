from __future__ import annotations

import json

from qrope.stage45_matched_decoder_only_gate import METHOD_NAMES
from qrope.stage67_content_key_retrieval_audit import (
    CONTENT_KEY_TASK,
    build_blocked_result,
    make_stage67_splits,
    run_stage67_audit,
    write_stage67_outputs,
)


def test_stage67_rows_have_visible_key_value_cue() -> None:
    splits = make_stage67_splits(seeds=(307,), examples_per_length=1)
    row = splits[CONTENT_KEY_TASK]["train"][0]
    assert row.task == CONTENT_KEY_TASK
    assert row.reference_delta == 1
    assert row.tokens[row.target_pos] == row.label_token
    assert row.tokens[row.query_pos - 1] == row.tokens[row.target_pos - 1]


def test_stage67_blocked_result_is_machine_readable() -> None:
    result = build_blocked_result()
    assert result["stage"] == "stage67_content_key_retrieval_audit"
    assert result["status"] == "blocked"
    assert result["method_names"] == list(METHOD_NAMES)
    assert result["tasks"] == [CONTENT_KEY_TASK]


def test_stage67_smoke_reports_content_key_decision_or_blocked() -> None:
    result = run_stage67_audit(
        seeds=(307,),
        examples_per_length=1,
        epochs=2,
        method_names=("no_position", "rope_relative"),
    )
    assert result["stage"] == "stage67_content_key_retrieval_audit"
    if result["status"] == "blocked":
        assert result["blocked_reason"] == "missing_optional_autograd_dependency"
        return
    assert result["status"] == "completed"
    assert result["tasks"] == [CONTENT_KEY_TASK]
    assert result["failed_runs"] == []
    assert result["decision"]["decision"] in {
        "CONTENT_KEY_RETRIEVAL_CAPACITY_NOT_ESTABLISHED",
        "CONTENT_KEY_RETRIEVAL_SOLVABLE_FOR_ALL_METHODS_NOT_PROMOTION",
        "CONTENT_KEY_RETRIEVAL_GENERALIZES_REVIEW_REQUIRED",
        "CONTENT_KEY_RETRIEVAL_WITHOUT_GENERALIZATION",
    }


def test_stage67_outputs_are_written(tmp_path) -> None:
    result = run_stage67_audit(
        seeds=(307,),
        examples_per_length=1,
        epochs=2,
        method_names=("no_position",),
    )
    paths = write_stage67_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved_name = "results.json" if result["status"] == "completed" else "preflight.json"
    saved = json.loads((tmp_path / saved_name).read_text(encoding="utf-8"))
    assert set(paths) >= {"manifest", "result", "summary_csv"}
    assert manifest["stage"] == "stage67_content_key_retrieval_audit"
    assert saved["stage"] == "stage67_content_key_retrieval_audit"
