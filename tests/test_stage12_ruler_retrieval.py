from __future__ import annotations

import json

import numpy as np

from qrope.stage12_ruler_retrieval import (
    METHOD_NAMES,
    TASK_NAMES,
    attention_distribution,
    evaluate_method,
    make_stage12_examples,
    phasewrap_period_score,
    run_stage12_benchmark,
    write_stage12_outputs,
)


def test_phasewrap_period_score_is_deterministic() -> None:
    assert phasewrap_period_score(17, 41) == phasewrap_period_score(17, 41)


def test_examples_are_deterministic_and_target_rules_are_not_empty() -> None:
    first = make_stage12_examples(seeds=(401,), context_lengths=(128,), examples_per_task_length=2)
    second = make_stage12_examples(seeds=(401,), context_lengths=(128,), examples_per_task_length=2)
    assert first == second
    assert len(first) == 6
    assert {example.task for example in first} == set(TASK_NAMES)
    for example in first:
        assert example.target_rule
        assert set(example.target_positions).issubset(set(example.key_positions))
        assert all(example.tokens[position] == example.query_token for position in example.key_positions)


def test_attention_distribution_is_probability_vector() -> None:
    example = make_stage12_examples(seeds=(401,), context_lengths=(128,), examples_per_task_length=1)[0]
    distribution = attention_distribution(example, "rope_relative")
    assert distribution.shape == (example.query_pos,)
    assert np.isclose(float(np.sum(distribution)), 1.0)
    assert np.all(distribution >= 0.0)


def test_evaluate_method_reports_intervals() -> None:
    examples = make_stage12_examples(seeds=(401,), context_lengths=(128,), examples_per_task_length=2)
    metrics = evaluate_method(examples, "phasewrap_rope_8_12")
    assert metrics["row_count"] == 6
    assert 0.0 <= metrics["top1_accuracy"] <= 1.0
    assert metrics["top1_ci_low"] <= metrics["top1_accuracy"] <= metrics["top1_ci_high"]
    assert metrics["mrr_ci_low"] <= metrics["mrr"] <= metrics["mrr_ci_high"]
    assert metrics["target_probability_mass_ci_low"] <= metrics["mean_target_probability_mass"] <= metrics["target_probability_mass_ci_high"]


def test_run_benchmark_is_complete_and_not_phasewrap_oracle_selected() -> None:
    result = run_stage12_benchmark(seeds=(401, 409), context_lengths=(128, 256), examples_per_task_length=2)
    assert [row["method"] for row in result["table"]] == list(METHOD_NAMES)
    assert result["row_count"] == 24
    assert result["best_method_by_top1_mrr"] in METHOD_NAMES
    diagnostic = result["phasewrap_target_diagnostic"]
    assert diagnostic["phasewrap_oracle_target_overlap"] < 1.0
    assert all(row["phasewrap_oracle_target_overlap"] <= 1.0 for row in diagnostic["per_task"])


def test_stage12_outputs_are_written(tmp_path) -> None:
    result = run_stage12_benchmark(seeds=(401,), context_lengths=(128,), examples_per_task_length=1)
    paths = write_stage12_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "results", "summary_csv", "task_summary_csv", "per_example_csv"}
    assert manifest["stage"] == "stage12_ruler_retrieval"
    assert saved["table"] == result["table"]
    assert "per_example_rows" not in saved
    assert (tmp_path / "summary.csv").exists()
    assert (tmp_path / "task_summary.csv").exists()
    assert (tmp_path / "per_example_results.csv").exists()
