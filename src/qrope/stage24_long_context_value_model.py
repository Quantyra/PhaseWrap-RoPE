from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

from .stage13_positional_adapter import METHOD_NAMES
from .stage14_attention_readout import DEFAULT_EXAMPLES_PER_TASK_LENGTH, DEFAULT_SEEDS, TASK_NAMES, make_stage14_examples
from .stage20_hardened_positional_value_model import (
    evaluate_hardened_positional_value_model,
    train_hardened_positional_value_model,
)


STAGE24_SCHEMA_VERSION = "qrope_stage24_long_context_value_model_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage24_long_context_value_model"
DEFAULT_CONTEXT_LENGTHS = (512, 1024, 2048, 4096)
TRAIN_LENGTHS = (512, 1024)
VALIDATION_LENGTHS = (2048,)
TEST_LENGTHS = (4096,)
DEFAULT_EPOCHS = 360
DEFAULT_INIT_SEED = 2401
DEFAULT_EMBED_DIM = 16


def split_long_context_value_rows(rows: list[Any]) -> dict[str, list[Any]]:
    return {
        "train": [row for row in rows if row.sequence_length in TRAIN_LENGTHS],
        "validation": [row for row in rows if row.sequence_length in VALIDATION_LENGTHS],
        "test": [row for row in rows if row.sequence_length in TEST_LENGTHS],
    }


def _public_training_record(record: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in record.items() if key != "params"}


def run_stage24_benchmark(
    *,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    context_lengths: tuple[int, ...] = DEFAULT_CONTEXT_LENGTHS,
    examples_per_task_length: int = DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    epochs: int = DEFAULT_EPOCHS,
    method_names: tuple[str, ...] = METHOD_NAMES,
    init_seed: int = DEFAULT_INIT_SEED,
    embed_dim: int = DEFAULT_EMBED_DIM,
) -> dict[str, Any]:
    rows = make_stage14_examples(
        seeds=seeds,
        context_lengths=context_lengths,
        examples_per_task_length=examples_per_task_length,
    )
    splits = split_long_context_value_rows(rows)
    table: list[dict[str, Any]] = []
    task_table: list[dict[str, Any]] = []
    training_records: list[dict[str, Any]] = []
    failed_or_weak_runs: list[dict[str, Any]] = []
    for method_name in method_names:
        training = train_hardened_positional_value_model(
            splits["train"],
            method_name,
            epochs=epochs,
            seed=init_seed,
            embed_dim=embed_dim,
        )
        training_records.append(_public_training_record(training))
        params = {key: np.array(value, dtype=float) for key, value in training["params"].items()}
        for split_name in ("train", "validation", "test"):
            row = evaluate_hardened_positional_value_model(splits[split_name], method_name, params, split_name=split_name)
            table.append(row)
            if split_name == "test" and float(row["top1_accuracy"]) < 0.5:
                failed_or_weak_runs.append(
                    {
                        "method": method_name,
                        "top1_accuracy": row["top1_accuracy"],
                        "mrr": row["mrr"],
                        "criterion": "test_top1_accuracy_below_0.5",
                    }
                )
        for task_name in TASK_NAMES:
            task_rows = [row for row in splits["test"] if row.task == task_name]
            task_result = evaluate_hardened_positional_value_model(
                task_rows,
                method_name,
                params,
                split_name=f"test:{task_name}",
            )
            task_result["task"] = task_name
            task_table.append(task_result)

    test_rows = [row for row in table if row["split"] == "test"]
    selection_table = sorted(
        test_rows,
        key=lambda row: (row["top1_accuracy"], row["mrr"], row["mean_target_value_probability"], row["method"]),
        reverse=True,
    )
    return {
        "schema_version": STAGE24_SCHEMA_VERSION,
        "stage": "stage24_long_context_value_model",
        "dataset": "deterministic_long_context_value_retrieval_model_v1",
        "source_stage": "stage22_long_context_retrieval",
        "no_hardware_submission": True,
        "seeds": list(seeds),
        "context_lengths": list(context_lengths),
        "train_lengths": list(TRAIN_LENGTHS),
        "validation_lengths": list(VALIDATION_LENGTHS),
        "test_lengths": list(TEST_LENGTHS),
        "examples_per_task_length": examples_per_task_length,
        "train_row_count": len(splits["train"]),
        "validation_row_count": len(splits["validation"]),
        "test_row_count": len(splits["test"]),
        "method_names": list(method_names),
        "task_names": list(TASK_NAMES),
        "epochs": epochs,
        "init_seed": init_seed,
        "model": {
            "type": "learned_positional_attention_with_hardened_value_output_long_context",
            "embed_dim": embed_dim,
            "optimizer": "full_batch_adam",
            "trained_parameters": "attention feature weights, value embeddings, output projection, output bias",
        },
        "failed_or_weak_runs": failed_or_weak_runs,
        "claim_boundary": {
            "supported": [
                "A deterministic compact value-retrieval model over explicit long-context retrieval rows.",
                "Evidence about whether PhaseWrap-derived features remain competitive after adding learned value embeddings and output projection.",
                "Train-short/test-long evaluation with failed or weak runs reported under a predeclared top-1 threshold.",
            ],
            "excluded": [
                "production transformer superiority",
                "full transformer-scale validation",
                "broad quantum advantage",
                "general cross-backend robustness",
                "a claim that PhaseWrap-RoPE is a validated RoPE replacement",
            ],
        },
        "training_records": training_records,
        "table": table,
        "selection_table": selection_table,
        "task_table": task_table,
        "best_method_by_test_top1_mrr": selection_table[0]["method"],
    }


def write_stage24_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "dataset": result["dataset"],
        "source_stage": result["source_stage"],
        "no_hardware_submission": result["no_hardware_submission"],
        "train_lengths": result["train_lengths"],
        "validation_lengths": result["validation_lengths"],
        "test_lengths": result["test_lengths"],
        "train_row_count": result["train_row_count"],
        "validation_row_count": result["validation_row_count"],
        "test_row_count": result["test_row_count"],
        "method_names": result["method_names"],
        "task_names": result["task_names"],
        "epochs": result["epochs"],
        "init_seed": result["init_seed"],
        "model": result["model"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "task_summary_csv_path": str((output_dir / "task_summary.csv").as_posix()),
        "claim_boundary": result["claim_boundary"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "results": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "task_summary_csv": str(output_dir / "task_summary.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["table"])
    with (output_dir / "task_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["task_table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["task_table"])
    return paths


def print_stage24_table(result: dict[str, Any]) -> None:
    columns = ("method", "split", "row_count", "top1_accuracy", "mrr", "mean_target_value_probability", "mean_first_relevant_value_rank")
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["table"]:
        print(" | ".join(str(row[column]) for column in columns))
