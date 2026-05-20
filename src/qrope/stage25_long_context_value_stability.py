from __future__ import annotations

import csv
import json
from pathlib import Path
from statistics import mean
from typing import Any

from .stage13_positional_adapter import METHOD_NAMES
from .stage14_attention_readout import DEFAULT_EXAMPLES_PER_TASK_LENGTH, DEFAULT_SEEDS
from .stage24_long_context_value_model import DEFAULT_CONTEXT_LENGTHS, DEFAULT_EMBED_DIM, DEFAULT_EPOCHS, run_stage24_benchmark


STAGE25_SCHEMA_VERSION = "qrope_stage25_long_context_value_stability_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage25_long_context_value_stability"
DEFAULT_INIT_SEEDS = (2401, 2411, 2423, 2437, 2459)


def _aggregate_metric(values: list[float]) -> dict[str, float]:
    return {
        "mean": round(float(mean(values)), 6),
        "min": round(float(min(values)), 6),
        "max": round(float(max(values)), 6),
    }


def _test_rows(result: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in result["table"] if row["split"] == "test"]


def run_stage25_benchmark(
    *,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    context_lengths: tuple[int, ...] = DEFAULT_CONTEXT_LENGTHS,
    examples_per_task_length: int = DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    init_seeds: tuple[int, ...] = DEFAULT_INIT_SEEDS,
    epochs: int = DEFAULT_EPOCHS,
    method_names: tuple[str, ...] = METHOD_NAMES,
    embed_dim: int = DEFAULT_EMBED_DIM,
) -> dict[str, Any]:
    per_run_rows: list[dict[str, Any]] = []
    run_records: list[dict[str, Any]] = []
    weak_run_records: list[dict[str, Any]] = []
    for init_seed in init_seeds:
        result = run_stage24_benchmark(
            seeds=seeds,
            context_lengths=context_lengths,
            examples_per_task_length=examples_per_task_length,
            epochs=epochs,
            method_names=method_names,
            init_seed=init_seed,
            embed_dim=embed_dim,
        )
        run_records.append(
            {
                "init_seed": init_seed,
                "best_method_by_test_top1_mrr": result["best_method_by_test_top1_mrr"],
                "train_row_count": result["train_row_count"],
                "validation_row_count": result["validation_row_count"],
                "test_row_count": result["test_row_count"],
            }
        )
        weak_run_records.extend({"init_seed": init_seed, **row} for row in result["failed_or_weak_runs"])
        for row in _test_rows(result):
            per_run_rows.append({"init_seed": init_seed, **row})

    summary_table: list[dict[str, Any]] = []
    for method_name in method_names:
        rows = [row for row in per_run_rows if row["method"] == method_name]
        top1 = _aggregate_metric([float(row["top1_accuracy"]) for row in rows])
        mrr = _aggregate_metric([float(row["mrr"]) for row in rows])
        prob = _aggregate_metric([float(row["mean_target_value_probability"]) for row in rows])
        rank = _aggregate_metric([float(row["mean_first_relevant_value_rank"]) for row in rows])
        summary_table.append(
            {
                "method": method_name,
                "run_count": len(rows),
                "top1_mean": top1["mean"],
                "top1_min": top1["min"],
                "top1_max": top1["max"],
                "mrr_mean": mrr["mean"],
                "mrr_min": mrr["min"],
                "mrr_max": mrr["max"],
                "mean_target_value_probability_mean": prob["mean"],
                "mean_target_value_probability_min": prob["min"],
                "mean_target_value_probability_max": prob["max"],
                "mean_first_relevant_value_rank_mean": rank["mean"],
                "mean_first_relevant_value_rank_min": rank["min"],
                "mean_first_relevant_value_rank_max": rank["max"],
            }
        )
    selection_table = sorted(
        summary_table,
        key=lambda row: (row["top1_mean"], row["mrr_mean"], row["mean_target_value_probability_mean"], row["method"]),
        reverse=True,
    )
    best_counts: dict[str, int] = {}
    for record in run_records:
        best = str(record["best_method_by_test_top1_mrr"])
        best_counts[best] = best_counts.get(best, 0) + 1
    return {
        "schema_version": STAGE25_SCHEMA_VERSION,
        "stage": "stage25_long_context_value_stability",
        "dataset": "deterministic_long_context_value_retrieval_model_stability_v1",
        "source_stage": "stage24_long_context_value_model",
        "no_hardware_submission": True,
        "seeds": list(seeds),
        "init_seeds": list(init_seeds),
        "context_lengths": list(context_lengths),
        "examples_per_task_length": examples_per_task_length,
        "epochs": epochs,
        "embed_dim": embed_dim,
        "method_names": list(method_names),
        "run_count": len(init_seeds),
        "best_method_counts": best_counts,
        "weak_run_records": weak_run_records,
        "claim_boundary": {
            "supported": [
                "A deterministic multi-initialization stability check for the Stage 24 long-context value-model comparison.",
                "Evidence about whether the Stage 24 held-out ordering persists across learned-parameter initialization seeds.",
                "Reported weak runs under a predeclared top-1 threshold.",
            ],
            "excluded": [
                "production transformer superiority",
                "full transformer-scale validation",
                "broad quantum advantage",
                "general cross-backend robustness",
                "a claim that PhaseWrap-RoPE is a validated RoPE replacement",
            ],
        },
        "run_records": run_records,
        "per_run_table": per_run_rows,
        "summary_table": summary_table,
        "selection_table": selection_table,
        "best_method_by_mean_top1_mrr": selection_table[0]["method"],
    }


def write_stage25_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "dataset": result["dataset"],
        "source_stage": result["source_stage"],
        "no_hardware_submission": result["no_hardware_submission"],
        "init_seeds": result["init_seeds"],
        "run_count": result["run_count"],
        "method_names": result["method_names"],
        "epochs": result["epochs"],
        "embed_dim": result["embed_dim"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "per_run_csv_path": str((output_dir / "per_run_results.csv").as_posix()),
        "weak_run_records_path": str((output_dir / "weak_run_records.json").as_posix()),
        "claim_boundary": result["claim_boundary"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "results": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "per_run_csv": str(output_dir / "per_run_results.csv"),
        "weak_run_records": str(output_dir / "weak_run_records.json"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "weak_run_records.json").write_text(json.dumps(result["weak_run_records"], indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["summary_table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["summary_table"])
    with (output_dir / "per_run_results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["per_run_table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["per_run_table"])
    return paths


def print_stage25_table(result: dict[str, Any]) -> None:
    columns = ("method", "run_count", "top1_mean", "top1_min", "top1_max", "mrr_mean", "mrr_min", "mrr_max", "mean_target_value_probability_mean")
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["selection_table"]:
        print(" | ".join(str(row[column]) for column in columns))
