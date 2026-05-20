from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .automated_stage_gates import phase_residual


STAGE10_SCHEMA_VERSION = "qrope_stage10_small_decoder_transformer_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage10_small_decoder_transformer"
METHOD_NAMES = ("no_position", "sinusoidal", "alibi", "rope", "phasewrap_bias", "phasewrap_adapter")
TASK_NAMES = ("phase_cued_retrieval", "exact_offset_passkey", "tiny_text_fact_qa")
DEFAULT_SEEDS = (307, 311, 313, 317, 331)
TRAIN_LENGTHS = (24, 32)
VALIDATION_LENGTHS = (40,)
TEST_LENGTHS = (48, 64)
EXAMPLES_PER_LENGTH = 4
VOCAB_SIZE = 128
MODEL_DIM = 8
DEFAULT_EPOCHS = 45
CAPACITY_PROBE_EPOCHS = 300

TEXT_FACTS = (
    ("paris", "france"),
    ("rome", "italy"),
    ("oslo", "norway"),
    ("lima", "peru"),
    ("cairo", "egypt"),
    ("tokyo", "japan"),
    ("nairobi", "kenya"),
    ("dublin", "ireland"),
)
TEXT_TOKEN_IDS = {
    "where": 80,
    "is": 81,
    "capital": 82,
    "of": 83,
    "answer": 84,
    "fact": 85,
    "query": 86,
    **{entity: 87 + index for index, (entity, _) in enumerate(TEXT_FACTS)},
    **{answer: 96 + index for index, (_, answer) in enumerate(TEXT_FACTS)},
}


@dataclass(frozen=True)
class Stage10Example:
    example_id: str
    seed: int
    task: str
    split: str
    sequence_length: int
    query_pos: int
    reference_delta: int
    target_pos: int
    target_delta: int
    tokens: tuple[int, ...]
    label_token: int


def autograd_available() -> bool:
    return importlib.util.find_spec("autograd") is not None


def _phasewrap_score(reference_delta: int, candidate_delta: int) -> float:
    margins = []
    for period in (8, 12):
        residual = phase_residual(reference_delta, candidate_delta, period)
        margins.append(math.cos(residual) - math.cos(2.0 * math.pi / float(period)))
    return float(margins[0] * margins[1])


def make_stage10_splits(
    *,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    examples_per_length: int = EXAMPLES_PER_LENGTH,
) -> dict[str, dict[str, list[Stage10Example]]]:
    reference_deltas = (5, 7, 8, 11, 12, 16, 19)
    split_lengths = {"train": TRAIN_LENGTHS, "validation": VALIDATION_LENGTHS, "test": TEST_LENGTHS}
    splits: dict[str, dict[str, list[Stage10Example]]] = {task: {"train": [], "validation": [], "test": []} for task in TASK_NAMES}
    for task in TASK_NAMES:
        for seed in seeds:
            rng = np.random.default_rng(seed + (0 if task == "phase_cued_retrieval" else 10_000))
            for split, lengths in split_lengths.items():
                for sequence_length in lengths:
                    query_pos = sequence_length - 1
                    for item_index in range(examples_per_length):
                        if task == "phase_cued_retrieval":
                            reference_delta = int(reference_deltas[(seed + sequence_length + item_index) % len(reference_deltas)])
                            candidates = [delta for delta in range(reference_delta, query_pos, 24) if delta >= 3]
                            target_delta = int(candidates[-1]) if candidates else reference_delta
                        elif task == "exact_offset_passkey":
                            target_delta = int(rng.integers(max(3, query_pos // 8), max(4, query_pos - 2)))
                            reference_delta = target_delta
                        else:
                            target_delta = int(rng.integers(max(6, query_pos // 4), max(7, query_pos - 3)))
                            reference_delta = target_delta
                        target_pos = query_pos - target_delta
                        tokens = [int(value) for value in rng.integers(0, VOCAB_SIZE - 16, size=sequence_length)]
                        if task == "tiny_text_fact_qa":
                            entity, answer = TEXT_FACTS[(seed + sequence_length + item_index) % len(TEXT_FACTS)]
                            label_token = TEXT_TOKEN_IDS[answer]
                            prefix = [
                                TEXT_TOKEN_IDS["fact"],
                                TEXT_TOKEN_IDS[entity],
                                TEXT_TOKEN_IDS["is"],
                                label_token,
                            ]
                            for offset, token_id in enumerate(prefix):
                                position = max(0, target_pos - len(prefix) + 1 + offset)
                                tokens[position] = token_id
                            query_tokens = [
                                TEXT_TOKEN_IDS["where"],
                                TEXT_TOKEN_IDS["is"],
                                TEXT_TOKEN_IDS[entity],
                                TEXT_TOKEN_IDS["query"],
                            ]
                            for offset, token_id in enumerate(query_tokens):
                                tokens[query_pos - len(query_tokens) + 1 + offset] = token_id
                        else:
                            label_token = int((17 * seed + 11 * sequence_length + 7 * item_index + target_delta) % (VOCAB_SIZE - 16))
                            tokens[target_pos] = label_token
                            tokens[query_pos] = VOCAB_SIZE - 1 - int(reference_delta % 16)
                        splits[task][split].append(
                            Stage10Example(
                                example_id=f"{task}_{split}_seed{seed}_L{sequence_length}_{item_index:03d}",
                                seed=seed,
                                task=task,
                                split=split,
                                sequence_length=sequence_length,
                                query_pos=query_pos,
                                reference_delta=reference_delta,
                                target_pos=target_pos,
                                target_delta=target_delta,
                                tokens=tuple(tokens),
                                label_token=label_token,
                            )
                        )
    return splits


def positional_bias(example: Stage10Example, method_name: str) -> np.ndarray:
    candidate_deltas = example.query_pos - np.arange(example.query_pos, dtype=float)
    diff = float(example.reference_delta) - candidate_deltas
    if method_name == "no_position":
        return np.zeros(example.query_pos, dtype=float)
    if method_name == "alibi":
        return -candidate_deltas / float(example.query_pos)
    if method_name == "sinusoidal":
        periods = np.array((4.0, 8.0, 16.0, 32.0), dtype=float)
        return np.mean(np.cos(2.0 * math.pi * diff[:, None] / periods[None, :]), axis=1)
    if method_name == "rope":
        inv_freq = np.array([10_000.0 ** (-2.0 * index / 32.0) for index in range(16)], dtype=float)
        return np.mean(np.cos(diff[:, None] * inv_freq[None, :]), axis=1)
    if method_name == "phasewrap_bias":
        return np.array([_phasewrap_score(example.reference_delta, int(delta)) for delta in candidate_deltas], dtype=float)
    if method_name == "phasewrap_adapter":
        raw = np.array([_phasewrap_score(example.reference_delta, int(delta)) for delta in candidate_deltas], dtype=float)
        return raw - 0.25 * np.abs(diff) / float(example.query_pos)
    raise ValueError(f"unknown method_name: {method_name}")


def _init_vector(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    size = VOCAB_SIZE * MODEL_DIM + 3 * MODEL_DIM * MODEL_DIM + MODEL_DIM * VOCAB_SIZE + 1
    return rng.normal(0.0, 0.04, size=size)


def _unpack(vector: Any):
    import autograd.numpy as anp

    index = 0
    emb_size = VOCAB_SIZE * MODEL_DIM
    emb = anp.reshape(vector[index : index + emb_size], (VOCAB_SIZE, MODEL_DIM))
    index += emb_size
    matrix_size = MODEL_DIM * MODEL_DIM
    wq = anp.reshape(vector[index : index + matrix_size], (MODEL_DIM, MODEL_DIM))
    index += matrix_size
    wk = anp.reshape(vector[index : index + matrix_size], (MODEL_DIM, MODEL_DIM))
    index += matrix_size
    wv = anp.reshape(vector[index : index + matrix_size], (MODEL_DIM, MODEL_DIM))
    index += matrix_size
    wo = anp.reshape(vector[index : index + MODEL_DIM * VOCAB_SIZE], (MODEL_DIM, VOCAB_SIZE))
    index += MODEL_DIM * VOCAB_SIZE
    return emb, wq, wk, wv, wo, vector[index]


def _softmax(values: Any):
    import autograd.numpy as anp

    shifted = values - anp.max(values)
    exp_values = anp.exp(shifted)
    return exp_values / anp.sum(exp_values)


def _row_loss(vector: Any, row: Stage10Example, method_name: str):
    import autograd.numpy as anp

    emb, wq, wk, wv, wo, pos_scale = _unpack(vector)
    hidden = emb[anp.array(row.tokens)]
    query = anp.dot(hidden[row.query_pos], wq)
    keys = anp.dot(hidden[: row.query_pos], wk)
    values = anp.dot(hidden[: row.query_pos], wv)
    attention_logits = anp.dot(keys, query) / math.sqrt(float(MODEL_DIM))
    attention_logits = attention_logits + pos_scale * anp.array(positional_bias(row, method_name))
    attention = _softmax(attention_logits)
    context = anp.dot(attention, values)
    probabilities = _softmax(anp.dot(context, wo))
    return -anp.log(probabilities[row.label_token] + 1e-12)


def _batch_loss(vector: Any, rows: list[Stage10Example], method_name: str):
    import autograd.numpy as anp

    return anp.mean(anp.array([_row_loss(vector, row, method_name) for row in rows]))


def train_small_decoder(rows: list[Stage10Example], method_name: str, *, seed: int, epochs: int = DEFAULT_EPOCHS) -> dict[str, Any]:
    from autograd import grad

    vector = _init_vector(seed)
    gradient = grad(lambda current: _batch_loss(current, rows, method_name))
    history: list[dict[str, float]] = []
    for epoch in range(epochs):
        loss_value = float(_batch_loss(vector, rows, method_name))
        vector = vector - 0.35 * gradient(vector)
        if epoch in {0, epochs // 2, epochs - 1}:
            history.append({"epoch": epoch + 1, "loss": round(loss_value, 6)})
    return {"weights": vector, "training_history": history, "final_training_loss": history[-1]["loss"]}


def _predict(vector: Any, row: Stage10Example, method_name: str) -> tuple[float, int, float]:
    import autograd.numpy as anp

    emb, wq, wk, wv, wo, pos_scale = _unpack(vector)
    hidden = emb[anp.array(row.tokens)]
    query = anp.dot(hidden[row.query_pos], wq)
    keys = anp.dot(hidden[: row.query_pos], wk)
    values = anp.dot(hidden[: row.query_pos], wv)
    attention_logits = anp.dot(keys, query) / math.sqrt(float(MODEL_DIM))
    attention_logits = attention_logits + pos_scale * anp.array(positional_bias(row, method_name))
    attention = _softmax(attention_logits)
    context = anp.dot(attention, values)
    probabilities = np.asarray(_softmax(anp.dot(context, wo)), dtype=float)
    sorted_indices = sorted(range(len(probabilities)), key=lambda index: (-float(probabilities[index]), index))
    return float(probabilities[row.label_token]), int(sorted_indices.index(row.label_token) + 1), float(probabilities[sorted_indices[0]])


def _expected_calibration_error(confidences: list[float], correctness: list[float], *, bins: int = 10) -> float:
    if len(confidences) != len(correctness):
        raise ValueError("confidences and correctness must have equal length")
    total = float(len(confidences))
    ece = 0.0
    for bin_index in range(bins):
        low = bin_index / float(bins)
        high = (bin_index + 1) / float(bins)
        if bin_index == bins - 1:
            indices = [index for index, value in enumerate(confidences) if low <= value <= high]
        else:
            indices = [index for index, value in enumerate(confidences) if low <= value < high]
        if not indices:
            continue
        avg_confidence = float(np.mean([confidences[index] for index in indices]))
        avg_accuracy = float(np.mean([correctness[index] for index in indices]))
        ece += (len(indices) / total) * abs(avg_confidence - avg_accuracy)
    return float(ece)


def evaluate_small_decoder(rows: list[Stage10Example], method_name: str, vector: Any) -> dict[str, float]:
    losses: list[float] = []
    reciprocal_ranks: list[float] = []
    top1_hits: list[float] = []
    target_probs: list[float] = []
    top1_confidences: list[float] = []
    for row in rows:
        target_probability, rank, top1_confidence = _predict(vector, row, method_name)
        losses.append(-math.log(max(target_probability, 1e-12)))
        reciprocal_ranks.append(1.0 / float(rank))
        top1_hits.append(1.0 if rank == 1 else 0.0)
        target_probs.append(target_probability)
        top1_confidences.append(top1_confidence)
    mean_loss = float(np.mean(losses))
    return {
        "row_count": len(rows),
        "loss": round(mean_loss, 6),
        "perplexity": round(float(math.exp(mean_loss)), 6),
        "top1_accuracy": round(float(np.mean(top1_hits)), 6),
        "mrr": round(float(np.mean(reciprocal_ranks)), 6),
        "mean_target_probability": round(float(np.mean(target_probs)), 6),
        "target_probability_mae": round(float(np.mean([1.0 - value for value in target_probs])), 6),
        "mean_top1_confidence": round(float(np.mean(top1_confidences)), 6),
        "expected_calibration_error": round(_expected_calibration_error(top1_confidences, top1_hits), 6),
    }


def _bootstrap_ci(values: list[float], *, seed_text: str, iterations: int = 400) -> dict[str, float]:
    rng = random.Random(int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16))
    means: list[float] = []
    for _ in range(iterations):
        sample = [values[rng.randrange(len(values))] for _ in range(len(values))]
        means.append(float(sum(sample) / len(sample)))
    means.sort()
    return {"low": round(means[int(0.025 * (iterations - 1))], 6), "high": round(means[int(0.975 * (iterations - 1))], 6)}


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential small decoder-only transformer ablation with matched seeds, tasks, model shape, optimizer, and epochs.",
            "Train-short/test-long retrieval evaluation with confidence intervals over seeds.",
        ],
        "excluded": [
            "production transformer superiority",
            "full language-model validation",
            "proof that PhaseWrap-RoPE replaces RoPE",
            "broad quantum advantage",
            "general cross-backend robustness",
        ],
    }


def build_blocked_result(*, reason: str = "missing_optional_autograd_dependency") -> dict[str, Any]:
    return {
        "schema_version": STAGE10_SCHEMA_VERSION,
        "stage": "stage10_small_decoder_transformer",
        "status": "blocked",
        "blocked_reason": reason,
        "install_command": "python -m pip install -e \".[transformer]\"",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "method_names": list(METHOD_NAMES),
        "seeds": list(DEFAULT_SEEDS),
        "claim_boundary": _claim_boundary(),
    }


def run_stage10_ablation(
    *,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    examples_per_length: int = EXAMPLES_PER_LENGTH,
    epochs: int = DEFAULT_EPOCHS,
) -> dict[str, Any]:
    if not autograd_available():
        return build_blocked_result()
    splits_by_task = make_stage10_splits(seeds=seeds, examples_per_length=examples_per_length)
    per_seed_table: list[dict[str, Any]] = []
    failed_runs: list[dict[str, Any]] = []
    for task_name, splits in splits_by_task.items():
        for seed in seeds:
            train_rows = [row for row in splits["train"] if row.seed == seed]
            validation_rows = [row for row in splits["validation"] if row.seed == seed]
            test_rows = [row for row in splits["test"] if row.seed == seed]
            for method_name in METHOD_NAMES:
                try:
                    trained = train_small_decoder(train_rows, method_name, seed=seed, epochs=epochs)
                    validation_metrics = evaluate_small_decoder(validation_rows, method_name, trained["weights"])
                    test_metrics = evaluate_small_decoder(test_rows, method_name, trained["weights"])
                    per_seed_table.append(
                        {
                            "task": task_name,
                            "seed": seed,
                            "method": method_name,
                            "epochs": epochs,
                            "train_row_count": len(train_rows),
                            "validation_loss": validation_metrics["loss"],
                            "test_loss": test_metrics["loss"],
                            "test_perplexity": test_metrics["perplexity"],
                            "test_top1_accuracy": test_metrics["top1_accuracy"],
                            "test_mrr": test_metrics["mrr"],
                            "test_mean_target_probability": test_metrics["mean_target_probability"],
                            "test_target_probability_mae": test_metrics["target_probability_mae"],
                            "test_mean_top1_confidence": test_metrics["mean_top1_confidence"],
                            "test_expected_calibration_error": test_metrics["expected_calibration_error"],
                            "final_training_loss": trained["final_training_loss"],
                            "training_history": trained["training_history"],
                        }
                    )
                except Exception as exc:  # pragma: no cover
                    failed_runs.append({"task": task_name, "seed": seed, "method": method_name, "error": str(exc)})
    aggregate_table: list[dict[str, Any]] = []
    for task_name in TASK_NAMES:
        for method_name in METHOD_NAMES:
            rows = [row for row in per_seed_table if row["task"] == task_name and row["method"] == method_name]
            if not rows:
                continue
            record: dict[str, Any] = {
                "task": task_name,
                "method": method_name,
                "seed_count": len(rows),
                "failed_run_count": len([run for run in failed_runs if run["task"] == task_name and run["method"] == method_name]),
            }
            for metric_name in (
                "test_loss",
                "test_perplexity",
                "test_top1_accuracy",
                "test_mrr",
                "test_mean_target_probability",
                "test_target_probability_mae",
                "test_mean_top1_confidence",
                "test_expected_calibration_error",
            ):
                values = [float(row[metric_name]) for row in rows]
                ci = _bootstrap_ci(values, seed_text=f"stage10:{task_name}:{method_name}:{metric_name}")
                record[f"{metric_name}_mean"] = round(float(np.mean(values)), 6)
                record[f"{metric_name}_ci_low"] = ci["low"]
                record[f"{metric_name}_ci_high"] = ci["high"]
            aggregate_table.append(record)
    best_method_by_task = {
        task_name: sorted(
            [row for row in aggregate_table if row["task"] == task_name],
            key=lambda row: (row["test_mrr_mean"], row["test_top1_accuracy_mean"], -row["test_loss_mean"], row["method"]),
            reverse=True,
        )[0]["method"]
        for task_name in TASK_NAMES
    }
    ranking_table = sorted(
        aggregate_table,
        key=lambda row: (row["task"], row["test_mrr_mean"], row["test_top1_accuracy_mean"], -row["test_loss_mean"], row["method"]),
        reverse=True,
    )
    return {
        "schema_version": STAGE10_SCHEMA_VERSION,
        "stage": "stage10_small_decoder_transformer",
        "status": "completed",
        "dataset": "synthetic_small_decoder_train_short_test_long_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "autograd_backend": True,
        "method_names": list(METHOD_NAMES),
        "tasks": list(TASK_NAMES),
        "seeds": list(seeds),
        "train_lengths": list(TRAIN_LENGTHS),
        "validation_lengths": list(VALIDATION_LENGTHS),
        "test_lengths": list(TEST_LENGTHS),
        "examples_per_length": examples_per_length,
        "model": {
            "type": "one_block_decoder_only_single_head_attention",
            "vocab_size": VOCAB_SIZE,
            "model_dim": MODEL_DIM,
            "epochs": epochs,
            "trained_parameters": "token embeddings, q/k/v projections, output projection, positional scale",
        },
        "claim_boundary": _claim_boundary(),
        "splits": {
            task_name: {
                split: {"row_count": len(rows), "lengths": sorted({row.sequence_length for row in rows})}
                for split, rows in splits.items()
            }
            for task_name, splits in splits_by_task.items()
        },
        "failed_runs": failed_runs,
        "per_seed_table": per_seed_table,
        "aggregate_table": aggregate_table,
        "ranking_table": ranking_table,
        "best_method_by_task": best_method_by_task,
        "capacity_probe": _run_capacity_probe(splits_by_task) if epochs >= DEFAULT_EPOCHS and len(seeds) >= len(DEFAULT_SEEDS) else None,
    }


def _run_capacity_probe(splits_by_task: dict[str, dict[str, list[Stage10Example]]]) -> dict[str, Any]:
    task_name = "phase_cued_retrieval"
    method_name = "rope"
    seed = DEFAULT_SEEDS[0]
    train_rows = [row for row in splits_by_task[task_name]["train"] if row.seed == seed]
    validation_rows = [row for row in splits_by_task[task_name]["validation"] if row.seed == seed]
    test_rows = [row for row in splits_by_task[task_name]["test"] if row.seed == seed]
    trained = train_small_decoder(train_rows, method_name, seed=seed, epochs=CAPACITY_PROBE_EPOCHS)
    return {
        "task": task_name,
        "method": method_name,
        "seed": seed,
        "epochs": CAPACITY_PROBE_EPOCHS,
        "purpose": "Check whether the tiny decoder can optimize the training packet and whether that fit extrapolates.",
        "train_metrics": evaluate_small_decoder(train_rows, method_name, trained["weights"]),
        "validation_metrics": evaluate_small_decoder(validation_rows, method_name, trained["weights"]),
        "test_metrics": evaluate_small_decoder(test_rows, method_name, trained["weights"]),
        "training_history": trained["training_history"],
        "interpretation": "The capacity probe is diagnostic only. It distinguishes optimizer/capacity failure from train-fit-with-poor-extrapolation when interpreting the Stage 10 result.",
    }


def run_stage10_preflight() -> dict[str, Any]:
    return run_stage10_ablation(seeds=(DEFAULT_SEEDS[0],), examples_per_length=1, epochs=2)


def write_stage10_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    result_name = "results.json" if result["status"] == "completed" else "preflight.json"
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "method_names": result["method_names"],
        "result_path": str((output_dir / result_name).as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "per_seed_csv_path": str((output_dir / "per_seed_results.csv").as_posix()) if result["status"] == "completed" else None,
        "failed_runs_path": str((output_dir / "failed_runs.json").as_posix()) if result["status"] == "completed" else None,
        "claim_boundary": result.get("claim_boundary", {}),
    }
    paths = {"manifest": str(output_dir / "manifest.json"), "result": str(output_dir / result_name), "summary_csv": str(output_dir / "summary.csv")}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / result_name).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    if result["status"] != "completed":
        with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=("stage", "status", "blocked_reason", "install_command"))
            writer.writeheader()
            writer.writerow({"stage": result["stage"], "status": result["status"], "blocked_reason": result.get("blocked_reason", ""), "install_command": result.get("install_command", "")})
        return paths
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["aggregate_table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["aggregate_table"])
    per_seed_rows = [{key: value for key, value in row.items() if key != "training_history"} for row in result["per_seed_table"]]
    with (output_dir / "per_seed_results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(per_seed_rows[0].keys()))
        writer.writeheader()
        writer.writerows(per_seed_rows)
    (output_dir / "failed_runs.json").write_text(json.dumps(result["failed_runs"], indent=2, sort_keys=True), encoding="utf-8")
    paths["per_seed_csv"] = str(output_dir / "per_seed_results.csv")
    paths["failed_runs"] = str(output_dir / "failed_runs.json")
    return paths


def print_stage10_summary(result: dict[str, Any]) -> None:
    if result["status"] != "completed":
        print("stage | status | blocked_reason | install_command")
        print("--- | --- | --- | ---")
        print(" | ".join((result["stage"], result["status"], result.get("blocked_reason", ""), result.get("install_command", ""))))
        return
    columns = ("task", "method", "seed_count", "failed_run_count", "test_loss_mean", "test_top1_accuracy_mean", "test_mrr_mean")
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["ranking_table"]:
        print(" | ".join(str(row[column]) for column in columns))
