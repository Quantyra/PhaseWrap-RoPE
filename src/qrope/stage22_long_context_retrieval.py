from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .stage12_ruler_retrieval import (
    DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    DEFAULT_SEEDS,
    METHOD_NAMES,
    TASK_NAMES,
    evaluate_method,
    make_stage12_examples,
    _example_result_rows,
    _phasewrap_target_diagnostic,
    _task_table,
)


STAGE22_SCHEMA_VERSION = "qrope_stage22_long_context_retrieval_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage22_long_context_retrieval"
DEFAULT_CONTEXT_LENGTHS = (512, 1024, 2048, 4096)


def _length_table(examples, method_names: tuple[str, ...]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for sequence_length in sorted({example.sequence_length for example in examples}):
        length_examples = [example for example in examples if example.sequence_length == sequence_length]
        for method_name in method_names:
            row = evaluate_method(length_examples, method_name)
            row["sequence_length"] = sequence_length
            rows.append(row)
    return rows


def run_stage22_benchmark(
    *,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    context_lengths: tuple[int, ...] = DEFAULT_CONTEXT_LENGTHS,
    examples_per_task_length: int = DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    method_names: tuple[str, ...] = METHOD_NAMES,
) -> dict[str, Any]:
    examples = make_stage12_examples(
        seeds=seeds,
        context_lengths=context_lengths,
        examples_per_task_length=examples_per_task_length,
    )
    table = [evaluate_method(examples, method_name) for method_name in method_names]
    selection_table = sorted(
        table,
        key=lambda row: (row["top1_accuracy"], row["mrr"], row["mean_target_probability_mass"], row["method"]),
        reverse=True,
    )
    failed_or_weak_runs = [
        {
            "method": row["method"],
            "top1_accuracy": row["top1_accuracy"],
            "mrr": row["mrr"],
            "criterion": "top1_accuracy_below_0.5",
        }
        for row in table
        if float(row["top1_accuracy"]) < 0.5
    ]
    return {
        "schema_version": STAGE22_SCHEMA_VERSION,
        "stage": "stage22_long_context_retrieval",
        "dataset": "deterministic_long_context_ruler_style_retrieval_v1",
        "source_stage": "stage12_ruler_retrieval",
        "no_hardware_submission": True,
        "seeds": list(seeds),
        "context_lengths": list(context_lengths),
        "examples_per_task_length": examples_per_task_length,
        "row_count": len(examples),
        "method_names": list(method_names),
        "task_names": list(TASK_NAMES),
        "failed_or_weak_runs": failed_or_weak_runs,
        "task": {
            "description": "Long-context extension of the Stage 12 local RULER-style passkey, multi-needle, and aggregation retrieval packet.",
            "target_construction": "Targets are selected by explicit retrieval rules and RNG offsets, not by maximizing the PhaseWrap score.",
            "note": "This is a deterministic no-credential positional-scoring benchmark, not a trained language model or proof that PhaseWrap-RoPE replaces RoPE.",
        },
        "claim_boundary": {
            "supported": [
                "A deterministic long-context retrieval stress test using explicit passkey, multi-needle, and aggregation target rules.",
                "Evidence about whether fixed positional scoring rules remain competitive as local retrieval contexts extend to 4096 tokens.",
                "Reported weak or failed method rows under a predeclared top-1 threshold.",
            ],
            "excluded": [
                "production transformer superiority",
                "full transformer-scale validation",
                "broad quantum advantage",
                "general cross-backend robustness",
                "a claim that PhaseWrap-RoPE is a validated RoPE replacement",
            ],
        },
        "phasewrap_target_diagnostic": _phasewrap_target_diagnostic(examples),
        "table": table,
        "selection_table": selection_table,
        "task_table": _task_table(examples),
        "length_table": _length_table(examples, method_names),
        "per_example_rows": _example_result_rows(examples),
        "best_method_by_top1_mrr": selection_table[0]["method"],
    }


def write_stage22_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "dataset": result["dataset"],
        "source_stage": result["source_stage"],
        "no_hardware_submission": result["no_hardware_submission"],
        "seeds": result["seeds"],
        "context_lengths": result["context_lengths"],
        "examples_per_task_length": result["examples_per_task_length"],
        "row_count": result["row_count"],
        "method_names": result["method_names"],
        "task_names": result["task_names"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "task_summary_csv_path": str((output_dir / "task_summary.csv").as_posix()),
        "length_summary_csv_path": str((output_dir / "length_summary.csv").as_posix()),
        "per_example_csv_path": str((output_dir / "per_example_results.csv").as_posix()),
        "claim_boundary": result["claim_boundary"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "results": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "task_summary_csv": str(output_dir / "task_summary.csv"),
        "length_summary_csv": str(output_dir / "length_summary.csv"),
        "per_example_csv": str(output_dir / "per_example_results.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    public_result = {key: value for key, value in result.items() if key != "per_example_rows"}
    (output_dir / "results.json").write_text(json.dumps(public_result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["table"])
    with (output_dir / "task_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["task_table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["task_table"])
    with (output_dir / "length_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["length_table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["length_table"])
    with (output_dir / "per_example_results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["per_example_rows"][0].keys()))
        writer.writeheader()
        writer.writerows(result["per_example_rows"])
    return paths


def print_stage22_table(result: dict[str, Any]) -> None:
    columns = (
        "method",
        "row_count",
        "sequence_length_min",
        "sequence_length_max",
        "top1_accuracy",
        "mrr",
        "mean_target_probability_mass",
        "mean_first_relevant_rank",
    )
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["selection_table"]:
        print(" | ".join(str(row[column]) for column in columns))
