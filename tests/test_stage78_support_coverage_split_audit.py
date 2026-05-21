from __future__ import annotations

import json

from qrope.stage78_support_coverage_split_audit import run_stage78_audit, write_stage78_outputs


def test_stage78_default_split_explains_same_seed_support_failure() -> None:
    result = run_stage78_audit()
    assert result["stage"] == "stage78_support_coverage_split_audit"
    assert result["status"] == "completed"
    assert result["failed_runs"] == []
    assert result["decision"]["decision"] == "SAME_SEED_SUPPORT_COVERAGE_SPLIT_EXPLAINS_STAGE77_FAILURE"
    assert result["decision"]["same_seed_train_exact_query_support_fraction_mean"] == 0.0
    assert result["decision"]["cross_seed_train_exact_query_support_fraction_mean"] == 1.0
    assert result["decision"]["pooled_train_exact_query_support_fraction_mean"] == 1.0


def test_stage78_records_per_seed_missing_support() -> None:
    result = run_stage78_audit()
    same_seed = [row for row in result["run_table"] if row["support_strategy"] == "same_seed_train"][0]
    cross_seed = [row for row in result["run_table"] if row["support_strategy"] == "cross_seed_train"][0]
    assert same_seed["exact_query_support_fraction"] == 0.0
    assert same_seed["missing_classes"]
    assert same_seed["missing_query_mods"]
    assert cross_seed["exact_query_support_fraction"] == 1.0
    assert cross_seed["missing_classes"] == []
    assert cross_seed["missing_query_mods"] == []


def test_stage78_outputs_are_written(tmp_path) -> None:
    result = run_stage78_audit(seeds=(307,))
    paths = write_stage78_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "result", "summary_csv", "per_run_csv", "failed_runs"}
    assert manifest["stage"] == "stage78_support_coverage_split_audit"
    assert saved["stage"] == "stage78_support_coverage_split_audit"
    assert (tmp_path / "summary.csv").exists()
