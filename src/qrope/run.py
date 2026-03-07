from __future__ import annotations

import argparse
import json
import math
import os
import random
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .config_utils import apply_set, deep_merge, load_yaml
from .env_utils import load_local_dotenv
from .qibm import run_ibm_sampler_batch
from .qphotonic import quandela_remote_score
from .qsim import SUPPORTED_MIXING_PRESETS, SUPPORTED_READOUTS, feature_angles, simple_quantum_score, variant_phases


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Q-RoPE run bootstrap")
    parser.add_argument("--config", action="append", required=True, help="YAML config path")
    parser.add_argument("--set", dest="set_values", action="append", default=[], help="key=value override")
    parser.add_argument("--dry-run", action="store_true", help="emit stub metrics only")
    parser.add_argument("--real-run", action="store_true", help="run training/inference path")
    return parser.parse_args()


def main() -> None:
    load_local_dotenv(Path(".env"))
    args = parse_args()
    start = time.time()

    config: dict[str, Any] = {}
    for config_path in args.config:
        config = deep_merge(config, load_yaml(Path(config_path)))

    for item in args.set_values:
        if "=" not in item:
            raise ValueError(f"--set must be key=value, got: {item}")
        key, value = item.split("=", 1)
        apply_set(config, key, value)

    run_id = str(config.get("run", {}).get("id", "unset"))
    variant = str(config.get("variant", {}).get("id", "unknown"))
    dataset_block = config.get("dataset", "unknown")
    if isinstance(dataset_block, dict):
        dataset = str(dataset_block.get("name", "unknown"))
    else:
        dataset = str(dataset_block)
    seed = int(config.get("run", {}).get("seed", 0))
    backend_block = config.get("backend", "unknown")
    if isinstance(backend_block, dict):
        backend = str(backend_block.get("name", "unknown"))
        noise_model = str(backend_block.get("noise_model", "none"))
        local_readout = str(backend_block.get("local_readout", "weighted"))
        local_mixing_preset = str(backend_block.get("local_mixing_preset", "mix_v0"))
    else:
        backend = str(backend_block)
        noise_model = "none"
        local_readout = "weighted"
        local_mixing_preset = "mix_v0"

    output_root = Path(str(config.get("logging", {}).get("output_root", "logs/ablation_runs")))
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    with (run_dir / "effective_config.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, sort_keys=False)

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    qubit_count = int(config.get("model", {}).get("quantum", {}).get("qubits", 0))
    shot_count = int(config.get("model", {}).get("quantum", {}).get("shots", 0))
    layers = int(config.get("model", {}).get("quantum", {}).get("layers", 1))
    gate_count_total, circuit_depth = estimate_hardware_costs(qubit_count, layers, variant)

    do_real = args.real_run and not args.dry_run
    if do_real:
        real_metrics = run_real_experiment(
            dataset=dataset,
            seed=seed,
            backend=backend,
            variant=variant,
            local_readout=local_readout,
            local_mixing_preset=local_mixing_preset,
        )
        accuracy = real_metrics["accuracy"]
        f1 = real_metrics["f1"]
        train_loss_final = real_metrics["train_loss_final"]
        eval_loss = real_metrics["eval_loss"]
        data_mode = real_metrics["data_mode"]
    else:
        accuracy = 0.0
        f1 = 0.0
        train_loss_final = 0.0
        eval_loss = 0.0
        data_mode = "n/a"

    metrics = {
        "run_id": run_id,
        "variant": variant,
        "dataset": dataset,
        "seed": seed,
        "backend": backend,
        "accuracy": round(accuracy, 6),
        "f1": round(f1, 6),
        "train_loss_final": round(train_loss_final, 6),
        "eval_loss": round(eval_loss, 6),
        "qubit_count": qubit_count,
        "gate_count_total": gate_count_total,
        "circuit_depth": circuit_depth,
        "shot_count": shot_count,
        "noise_model": noise_model,
        "wall_time_sec": round(time.time() - start, 6),
        "timestamp_utc": now,
        "dry_run": not do_real,
        "run_mode": "real" if do_real else "dry",
        "data_mode": data_mode,
    }

    with (run_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"Wrote run artifacts: {run_dir}")
    print(f"Metrics file: {run_dir / 'metrics.json'}")


def estimate_hardware_costs(qubits: int, layers: int, variant: str) -> tuple[int, int]:
    variant_multiplier = {
        "V0": 8,
        "V1": 10,
        "V2": 12,
        "V3": 14,
        "V4": 14,
        "V4b": 14,
    }.get(variant, 10)
    gate_count = max(1, qubits) * max(1, layers) * variant_multiplier
    depth = max(1, layers) * (variant_multiplier // 2)
    return gate_count, depth


def run_real_experiment(
    dataset: str,
    seed: int,
    backend: str,
    variant: str,
    local_readout: str = "weighted",
    local_mixing_preset: str = "mix_v0",
) -> dict[str, float | str]:
    samples, data_mode = load_dataset_samples(dataset, seed)
    if backend == "sim_quandela_remote":
        samples = limit_remote_samples(samples, max_samples=12)
    train, test = split_samples(samples, train_ratio=0.8)

    if backend == "sim_quantum_statevector":
        train_loss, eval_loss, accuracy, f1 = run_quantum_backend(
            train=train,
            test=test,
            seed=seed,
            variant=variant,
            readout=local_readout,
            mixing_preset=local_mixing_preset,
        )
        data_mode = f"{data_mode}+readout_{local_readout}+mix_{local_mixing_preset}"
    elif backend == "sim_qiskit_aer":
        train_loss, eval_loss, accuracy, f1 = run_qiskit_aer_backend(train=train, test=test, seed=seed, variant=variant)
    elif backend == "sim_quandela_remote":
        quandela_result = run_quandela_remote_backend(
            train=train,
            test=test,
            seed=seed,
            variant=variant,
            platform_name=os.environ.get("QUANDELA_PLATFORM", "sim:slos").strip() or "sim:slos",
        )
        train_loss = quandela_result["train_loss"]
        eval_loss = quandela_result["eval_loss"]
        accuracy = quandela_result["accuracy"]
        f1 = quandela_result["f1"]
        data_mode = f"{data_mode}+quandela_remote_slice12+skip{quandela_result['skip_count']}"
    elif backend == "ibm_runtime_remote":
        samples = limit_remote_samples(samples, max_samples=12)
        train, test = split_samples(samples, train_ratio=0.8)
        train_loss, eval_loss, accuracy, f1 = run_ibm_remote_backend(
            train=train,
            test=test,
            seed=seed,
            variant=variant,
            backend_name=os.environ.get("IBM_QUANTUM_BACKEND", "").strip() or None,
        )
        data_mode = f"{data_mode}+ibm_runtime_slice12"
    else:
        model = fit_naive_bayes(train)
        train_loss = mean_nll(model, train)
        eval_loss = mean_nll(model, test)
        y_true = [label for _, label in test]
        y_pred = [predict(model, text) for text, _ in test]
        accuracy = compute_accuracy(y_true, y_pred)
        f1 = compute_f1_binary(y_true, y_pred)
    return {
        "accuracy": accuracy,
        "f1": f1,
        "train_loss_final": train_loss,
        "eval_loss": eval_loss,
        "data_mode": data_mode,
    }


def run_quandela_remote_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    seed: int,
    variant: str,
    platform_name: str,
) -> dict[str, float | int]:
    train_labels, train_scores, train_skips = collect_quandela_scores(
        rows=train,
        seed=seed,
        variant=variant,
        platform_name=platform_name,
    )
    test_labels, probs, test_skips = collect_quandela_scores(
        rows=test,
        seed=seed,
        variant=variant,
        platform_name=platform_name,
    )
    if len(train_scores) < 4 or len(probs) < 2:
        raise RuntimeError("Quandela skip policy retained too few samples for a meaningful run")
    threshold = sum(train_scores) / len(train_scores) if train_scores else 0.5

    y_true = test_labels
    y_pred = [1 if p1 >= threshold else 0 for p1 in probs]

    train_loss = binary_cross_entropy(train_labels, train_scores)
    eval_loss = binary_cross_entropy(y_true, probs)
    accuracy = compute_accuracy(y_true, y_pred)
    f1 = compute_f1_binary(y_true, y_pred)
    return {
        "train_loss": train_loss,
        "eval_loss": eval_loss,
        "accuracy": accuracy,
        "f1": f1,
        "skip_count": train_skips + test_skips,
    }


def limit_remote_samples(samples: list[tuple[str, int]], max_samples: int) -> list[tuple[str, int]]:
    if len(samples) <= max_samples:
        return samples
    positive = [row for row in samples if row[1] == 1]
    negative = [row for row in samples if row[1] == 0]
    half = max_samples // 2
    subset = positive[:half] + negative[:half]
    if len(subset) < max_samples:
        subset.extend(samples[len(subset):max_samples])
    return subset[:max_samples]


def run_ibm_remote_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    seed: int,
    variant: str,
    backend_name: str | None,
) -> tuple[float, float, float, float]:
    train_scores = run_ibm_sampler_batch([text for text, _ in train], variant=variant, seed=seed, backend_name=backend_name)
    threshold = sum(train_scores) / len(train_scores) if train_scores else 0.5

    probs = run_ibm_sampler_batch([text for text, _ in test], variant=variant, seed=seed, backend_name=backend_name)
    y_true = [label for _, label in test]
    y_pred = [1 if p1 >= threshold else 0 for p1 in probs]

    train_loss = binary_cross_entropy([label for _, label in train], train_scores)
    eval_loss = binary_cross_entropy(y_true, probs)
    accuracy = compute_accuracy(y_true, y_pred)
    f1 = compute_f1_binary(y_true, y_pred)
    return train_loss, eval_loss, accuracy, f1


def collect_quandela_scores(
    rows: list[tuple[str, int]],
    seed: int,
    variant: str,
    platform_name: str,
) -> tuple[list[int], list[float], int]:
    labels: list[int] = []
    scores: list[float] = []
    skipped = 0
    for text, label in rows:
        try:
            score = quandela_remote_score(text=text, variant=variant, seed=seed, platform_name=platform_name)
        except RuntimeError:
            skipped += 1
            continue
        labels.append(label)
        scores.append(score)
    return labels, scores, skipped


def run_quantum_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    seed: int,
    variant: str,
    readout: str = "weighted",
    mixing_preset: str = "mix_v0",
) -> tuple[float, float, float, float]:
    if readout not in SUPPORTED_READOUTS:
        raise ValueError(f"Unsupported local readout: {readout}")
    if mixing_preset not in SUPPORTED_MIXING_PRESETS:
        raise ValueError(f"Unsupported local mixing preset: {mixing_preset}")
    train_scores = [
        simple_quantum_score(text=t, variant=variant, seed=seed, readout=readout, mixing_preset=mixing_preset)
        for t, _ in train
    ]
    _, validation = stratified_calibration_split(train)
    validation_scores = [
        simple_quantum_score(text=t, variant=variant, seed=seed, readout=readout, mixing_preset=mixing_preset)
        for t, _ in validation
    ]
    validation_labels = [label for _, label in validation]
    threshold = calibrate_threshold(validation_scores, validation_labels)

    y_true = [label for _, label in test]
    y_pred: list[int] = []
    probs: list[float] = []
    for text, _ in test:
        p1 = simple_quantum_score(
            text=text,
            variant=variant,
            seed=seed,
            readout=readout,
            mixing_preset=mixing_preset,
        )
        probs.append(p1)
        y_pred.append(1 if p1 >= threshold else 0)

    train_loss = binary_cross_entropy([label for _, label in train], train_scores)
    eval_loss = binary_cross_entropy(y_true, probs)
    accuracy = compute_accuracy(y_true, y_pred)
    f1 = compute_f1_binary(y_true, y_pred)
    return train_loss, eval_loss, accuracy, f1


def stratified_calibration_split(
    rows: list[tuple[str, int]],
    validation_ratio: float = 0.25,
) -> tuple[list[tuple[str, int]], list[tuple[str, int]]]:
    if len(rows) < 4:
        return rows, rows

    grouped: dict[int, list[tuple[str, int]]] = {0: [], 1: []}
    for row in rows:
        grouped[row[1]].append(row)

    subtrain: list[tuple[str, int]] = []
    validation: list[tuple[str, int]] = []
    for label in (0, 1):
        bucket = sorted(grouped[label], key=calibration_row_key)
        if not bucket:
            continue
        requested = max(1, int(round(len(bucket) * validation_ratio)))
        val_count = min(requested, max(1, len(bucket) - 1))
        validation.extend(bucket[:val_count])
        subtrain.extend(bucket[val_count:])

    if not validation:
        return rows, rows
    if not subtrain:
        return validation, validation
    return subtrain, validation


def calibration_row_key(row: tuple[str, int]) -> str:
    text, label = row
    return f"{label}:{stable_text_hash(text)}"


def stable_text_hash(text: str) -> str:
    import hashlib

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def calibrate_threshold(scores: list[float], labels: list[int]) -> float:
    if not scores or not labels or len(scores) != len(labels):
        return 0.5

    candidates = threshold_candidates(scores)
    label_prior = sum(labels) / len(labels)
    best: tuple[float, float, float, float] | None = None
    best_threshold = 0.5
    score_mean = sum(scores) / len(scores)

    for threshold in candidates:
        preds = [1 if score >= threshold else 0 for score in scores]
        macro_f1 = compute_macro_f1_binary(labels, preds)
        balanced_acc = compute_balanced_accuracy(labels, preds)
        pos_rate_drift = abs((sum(preds) / len(preds)) - label_prior)
        mean_distance = abs(threshold - score_mean)
        candidate_rank = (macro_f1, balanced_acc, -pos_rate_drift, -mean_distance)
        if best is None or candidate_rank > best:
            best = candidate_rank
            best_threshold = threshold
    return best_threshold


def threshold_candidates(scores: list[float]) -> list[float]:
    ordered = sorted(set(max(0.0, min(1.0, score)) for score in scores))
    if not ordered:
        return [0.5]
    candidates = {ordered[0], ordered[-1], 0.5}
    for left, right in zip(ordered, ordered[1:]):
        candidates.add((left + right) / 2.0)
    return sorted(candidates)


def run_qiskit_aer_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    seed: int,
    variant: str,
) -> tuple[float, float, float, float]:
    try:
        from qiskit import QuantumCircuit
        from qiskit_aer import AerSimulator
    except Exception as exc:  # pragma: no cover - runtime environment dependent
        raise RuntimeError("qiskit/qiskit-aer backend requested but unavailable") from exc

    simulator = AerSimulator()
    shots = 256

    def score(text: str) -> float:
        features = feature_angles(text, n_qubits=3, seed=seed)
        phases = variant_phases(variant, 3)
        qc = QuantumCircuit(3, 1)
        for q in range(3):
            qc.ry(features[q], q)
            qc.rz(phases[q], q)
        qc.cx(0, 1)
        qc.cx(1, 2)
        qc.measure(0, 0)
        result = simulator.run(qc, shots=shots).result()
        counts = result.get_counts(qc)
        p1 = counts.get("1", 0) / shots
        return p1

    train_scores = [score(t) for t, _ in train]
    threshold = sum(train_scores) / len(train_scores) if train_scores else 0.5

    y_true = [label for _, label in test]
    probs: list[float] = []
    y_pred: list[int] = []
    for text, _ in test:
        p1 = score(text)
        probs.append(p1)
        y_pred.append(1 if p1 >= threshold else 0)

    train_loss = binary_cross_entropy([label for _, label in train], train_scores)
    eval_loss = binary_cross_entropy(y_true, probs)
    accuracy = compute_accuracy(y_true, y_pred)
    f1 = compute_f1_binary(y_true, y_pred)
    return train_loss, eval_loss, accuracy, f1


def load_dataset_samples(dataset: str, seed: int) -> tuple[list[tuple[str, int]], str]:
    path = Path("data") / f"{dataset}.jsonl"
    if path.exists():
        rows: list[tuple[str, int]] = []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                item = json.loads(line)
                rows.append((str(item["text"]), int(item["label"])))
        if len(rows) >= 20:
            return rows, "local_jsonl"
    return generate_synthetic_dataset(dataset, seed), "synthetic_fallback"


def generate_synthetic_dataset(dataset: str, seed: int) -> list[tuple[str, int]]:
    rng = random.Random(f"{dataset}:{seed}")
    positive_words = ["good", "great", "excellent", "love", "fast", "clean", "happy"]
    negative_words = ["bad", "poor", "awful", "hate", "slow", "dirty", "angry"]
    neutral_words = ["service", "product", "movie", "delivery", "quality", "price", "review"]
    rows: list[tuple[str, int]] = []
    for _ in range(360):
        label = 1 if rng.random() > 0.5 else 0
        sentiment_pool = positive_words if label == 1 else negative_words
        tokens = []
        tokens.extend(rng.sample(sentiment_pool, k=3))
        tokens.extend(rng.sample(neutral_words, k=3))
        if rng.random() < 0.15:
            opposite = negative_words if label == 1 else positive_words
            tokens.append(rng.choice(opposite))
        rng.shuffle(tokens)
        rows.append((" ".join(tokens), label))
    return rows


def split_samples(samples: list[tuple[str, int]], train_ratio: float) -> tuple[list[tuple[str, int]], list[tuple[str, int]]]:
    cutoff = int(len(samples) * train_ratio)
    return samples[:cutoff], samples[cutoff:]


def tokenize(text: str) -> list[str]:
    return [tok for tok in text.lower().split() if tok]


def fit_naive_bayes(rows: list[tuple[str, int]]) -> dict[str, Any]:
    token_counts = {0: {}, 1: {}}
    class_counts = {0: 0, 1: 0}
    vocab: set[str] = set()
    for text, label in rows:
        class_counts[label] += 1
        for tok in tokenize(text):
            vocab.add(tok)
            token_counts[label][tok] = token_counts[label].get(tok, 0) + 1
    total_tokens = {
        0: sum(token_counts[0].values()),
        1: sum(token_counts[1].values()),
    }
    return {
        "token_counts": token_counts,
        "class_counts": class_counts,
        "vocab": vocab,
        "total_tokens": total_tokens,
    }


def predict(model: dict[str, Any], text: str) -> int:
    vocab_size = max(1, len(model["vocab"]))
    total_docs = max(1, model["class_counts"][0] + model["class_counts"][1])
    scores = {}
    for cls in (0, 1):
        prior = (model["class_counts"][cls] + 1) / (total_docs + 2)
        score = math.log(prior)
        denom = model["total_tokens"][cls] + vocab_size
        for tok in tokenize(text):
            count = model["token_counts"][cls].get(tok, 0)
            score += math.log((count + 1) / denom)
        scores[cls] = score
    return 1 if scores[1] >= scores[0] else 0


def mean_nll(model: dict[str, Any], rows: list[tuple[str, int]]) -> float:
    if not rows:
        return 0.0
    vocab_size = max(1, len(model["vocab"]))
    total_docs = max(1, model["class_counts"][0] + model["class_counts"][1])
    total = 0.0
    for text, label in rows:
        prior = (model["class_counts"][label] + 1) / (total_docs + 2)
        logp = math.log(prior)
        denom = model["total_tokens"][label] + vocab_size
        for tok in tokenize(text):
            count = model["token_counts"][label].get(tok, 0)
            logp += math.log((count + 1) / denom)
        total += -logp
    return total / len(rows)


def compute_accuracy(y_true: list[int], y_pred: list[int]) -> float:
    if not y_true:
        return 0.0
    correct = sum(1 for a, b in zip(y_true, y_pred) if a == b)
    return correct / len(y_true)


def compute_f1_binary(y_true: list[int], y_pred: list[int]) -> float:
    tp = sum(1 for a, b in zip(y_true, y_pred) if a == 1 and b == 1)
    fp = sum(1 for a, b in zip(y_true, y_pred) if a == 0 and b == 1)
    fn = sum(1 for a, b in zip(y_true, y_pred) if a == 1 and b == 0)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def compute_macro_f1_binary(y_true: list[int], y_pred: list[int]) -> float:
    positive_f1 = compute_f1_binary(y_true, y_pred)
    inverted_true = [1 - value for value in y_true]
    inverted_pred = [1 - value for value in y_pred]
    negative_f1 = compute_f1_binary(inverted_true, inverted_pred)
    return (positive_f1 + negative_f1) / 2.0


def compute_balanced_accuracy(y_true: list[int], y_pred: list[int]) -> float:
    tp = sum(1 for a, b in zip(y_true, y_pred) if a == 1 and b == 1)
    tn = sum(1 for a, b in zip(y_true, y_pred) if a == 0 and b == 0)
    fp = sum(1 for a, b in zip(y_true, y_pred) if a == 0 and b == 1)
    fn = sum(1 for a, b in zip(y_true, y_pred) if a == 1 and b == 0)
    tpr = tp / (tp + fn) if (tp + fn) else 0.0
    tnr = tn / (tn + fp) if (tn + fp) else 0.0
    return (tpr + tnr) / 2.0


def binary_cross_entropy(y_true: list[int], probs: list[float]) -> float:
    if not y_true:
        return 0.0
    eps = 1e-9
    total = 0.0
    for y, p in zip(y_true, probs):
        p = max(eps, min(1.0 - eps, p))
        total += -(y * math.log(p) + (1 - y) * math.log(1 - p))
    return total / len(y_true)


if __name__ == "__main__":
    main()
