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
from .qsim import (
    PAIRSTATE_CONTROL_MODES,
    SUPPORTED_MIXING_PRESETS,
    SUPPORTED_READOUTS,
    feature_angles,
    offset_sector,
    pairstate_quantum_result,
    parse_synthetic_pair_text,
    relational_witness_features,
    simple_quantum_score,
    variant_phases,
)
from .synthetic import diagnostics_to_jsonable, generate_signed_offset_binary_bundle
from .synthetic import generate_sector_parity_binary_bundle

RELATIONAL_WITNESS_FEATURE_GROUPS = {
    "group_A_sector_means": ["mu_P_small", "mu_P_large", "mu_N_small", "mu_N_large"],
    "group_B_sign_contrasts": ["delta_sign_small", "delta_sign_large"],
    "group_C_magnitude_contrasts": ["delta_mag_pos", "delta_mag_neg"],
    "group_D_task_contrast": ["delta_task"],
}

RELATIONAL_WITNESS_SCHEMA_VIEWS = {
    "means_only": ["mu_P_small", "mu_P_large", "mu_N_small", "mu_N_large"],
    "contrasts_only": ["delta_sign_small", "delta_sign_large", "delta_mag_pos", "delta_mag_neg"],
}


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
        synthetic_split_rotation = int(dataset_block.get("split_rotation", 0))
    else:
        dataset = str(dataset_block)
        synthetic_split_rotation = 0
    seed = int(config.get("run", {}).get("seed", 0))
    backend_block = config.get("backend", "unknown")
    if isinstance(backend_block, dict):
        backend = str(backend_block.get("name", "unknown"))
        noise_model = str(backend_block.get("noise_model", "none"))
        local_readout = str(backend_block.get("local_readout", "weighted"))
        local_mixing_preset = str(backend_block.get("local_mixing_preset", "mix_v0"))
        pairstate_control_mode = str(backend_block.get("pairstate_control_mode", "aligned"))
        witness_feature_mode = str(
            backend_block.get("witness_feature_mode", backend_block.get("witness_ablation_group", "full"))
        )
    else:
        backend = str(backend_block)
        noise_model = "none"
        local_readout = "weighted"
        local_mixing_preset = "mix_v0"
        pairstate_control_mode = "aligned"
        witness_feature_mode = "full"

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
            pairstate_control_mode=pairstate_control_mode,
            witness_feature_mode=witness_feature_mode,
            synthetic_split_rotation=synthetic_split_rotation,
        )
        accuracy = real_metrics["accuracy"]
        f1 = real_metrics["f1"]
        train_loss_final = real_metrics["train_loss_final"]
        eval_loss = real_metrics["eval_loss"]
        data_mode = real_metrics["data_mode"]
        dataset_diagnostics = real_metrics.get("dataset_diagnostics")
        run_diagnostics = real_metrics.get("run_diagnostics")
    else:
        accuracy = 0.0
        f1 = 0.0
        train_loss_final = 0.0
        eval_loss = 0.0
        data_mode = "n/a"
        dataset_diagnostics = None
        run_diagnostics = None

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
    if dataset_diagnostics:
        with (run_dir / "generator_diagnostics.json").open("w", encoding="utf-8") as f:
            json.dump(diagnostics_to_jsonable(dataset_diagnostics), f, indent=2)
    if run_diagnostics:
        with (run_dir / "run_diagnostics.json").open("w", encoding="utf-8") as f:
            json.dump(diagnostics_to_jsonable(run_diagnostics), f, indent=2)

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
        "V_pairstate_relational": 16,
        "V_future_sector_contrast_pairstate": 16,
        "V_future_relational_witness": 16,
        "V_control_symbolic_relational": 1,
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
    pairstate_control_mode: str = "aligned",
    witness_feature_mode: str = "full",
    synthetic_split_rotation: int = 0,
) -> dict[str, Any]:
    bundle = load_dataset_bundle(dataset, seed, split_rotation=synthetic_split_rotation)
    data_mode = bundle["data_mode"]
    dataset_diagnostics = bundle.get("dataset_diagnostics")
    if "rows" in bundle:
        samples = bundle["rows"]
        if backend == "sim_quandela_remote":
            samples = limit_remote_samples(samples, max_samples=12)
        train, test = split_samples(samples, train_ratio=0.8)
        validation = None
    else:
        train = bundle["train"]
        validation = bundle["validation"]
        test = bundle["test"]
        if backend in {"sim_quandela_remote", "ibm_runtime_remote"}:
            raise RuntimeError(f"{dataset} is local-only and unsupported on backend {backend}")

    if backend == "sim_quantum_statevector":
        train_loss, eval_loss, accuracy, f1, run_diagnostics = run_quantum_backend(
            train=train,
            test=test,
            seed=seed,
            variant=variant,
            readout=local_readout,
            mixing_preset=local_mixing_preset,
            pairstate_control_mode=pairstate_control_mode,
            witness_feature_mode=witness_feature_mode,
            validation=validation,
        )
        if variant == "V_new_explicit_interference":
            data_mode = f"{data_mode}+readout_parity_contrast+mix_interference"
        elif variant in {"V_pairstate_relational", "V_future_sector_contrast_pairstate"}:
            data_mode = f"{data_mode}+readout_sector_contrast+repr_pairstate+control_{pairstate_control_mode}"
        elif variant == "V_future_relational_witness":
            data_mode = f"{data_mode}+readout_relational_witness+head_logreg+featuremode_{witness_feature_mode}"
        elif variant == "V_control_symbolic_relational":
            data_mode = f"{data_mode}+readout_symbolic_relational+head_logreg"
        else:
            data_mode = f"{data_mode}+readout_{local_readout}+mix_{local_mixing_preset}"
    elif backend == "sim_qiskit_aer":
        train_loss, eval_loss, accuracy, f1 = run_qiskit_aer_backend(train=train, test=test, seed=seed, variant=variant)
        run_diagnostics = None
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
        run_diagnostics = None
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
        run_diagnostics = None
    else:
        model = fit_naive_bayes(train)
        train_loss = mean_nll(model, train)
        eval_loss = mean_nll(model, test)
        y_true = [label for _, label in test]
        y_pred = [predict(model, text) for text, _ in test]
        accuracy = compute_accuracy(y_true, y_pred)
        f1 = compute_f1_binary(y_true, y_pred)
        run_diagnostics = None
    return {
        "accuracy": accuracy,
        "f1": f1,
        "train_loss_final": train_loss,
        "eval_loss": eval_loss,
        "data_mode": data_mode,
        "dataset_diagnostics": dataset_diagnostics,
        "run_diagnostics": run_diagnostics,
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
    pairstate_control_mode: str = "aligned",
    witness_feature_mode: str = "full",
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any] | None]:
    if readout not in SUPPORTED_READOUTS:
        raise ValueError(f"Unsupported local readout: {readout}")
    if mixing_preset not in SUPPORTED_MIXING_PRESETS:
        raise ValueError(f"Unsupported local mixing preset: {mixing_preset}")
    if variant == "V_future_relational_witness":
        return run_relational_witness_backend(
            train=train,
            test=test,
            seed=seed,
            validation=validation,
            witness_feature_mode=witness_feature_mode,
        )
    if variant == "V_control_symbolic_relational":
        return run_symbolic_relational_control_backend(train=train, test=test, validation=validation)
    if variant in {"V_pairstate_relational", "V_future_sector_contrast_pairstate"} and pairstate_control_mode not in PAIRSTATE_CONTROL_MODES:
        raise ValueError(f"Unsupported pairstate control mode: {pairstate_control_mode}")
    if variant in {"V_pairstate_relational", "V_future_sector_contrast_pairstate"}:
        train_results = [
            pairstate_quantum_result(text=t, seed=seed, control_mode=pairstate_control_mode) for t, _ in train
        ]
        train_scores = [float(result["score"]) for result in train_results]
    else:
        train_results = None
        train_scores = [
            simple_quantum_score(text=t, variant=variant, seed=seed, readout=readout, mixing_preset=mixing_preset)
            for t, _ in train
        ]
    if validation is None:
        _, validation = stratified_calibration_split(train)
    if variant in {"V_pairstate_relational", "V_future_sector_contrast_pairstate"}:
        validation_results = [
            pairstate_quantum_result(text=t, seed=seed, control_mode=pairstate_control_mode) for t, _ in validation
        ]
        validation_scores = [float(result["score"]) for result in validation_results]
    else:
        validation_scores = [
            simple_quantum_score(text=t, variant=variant, seed=seed, readout=readout, mixing_preset=mixing_preset)
            for t, _ in validation
        ]
    validation_labels = [label for _, label in validation]
    threshold = calibrate_threshold(validation_scores, validation_labels)

    y_true = [label for _, label in test]
    y_pred: list[int] = []
    probs: list[float] = []
    per_sample_results: list[dict[str, Any]] | None = [] if variant in {"V_pairstate_relational", "V_future_sector_contrast_pairstate"} else None
    for text, _ in test:
        if variant in {"V_pairstate_relational", "V_future_sector_contrast_pairstate"}:
            result = pairstate_quantum_result(text=text, seed=seed, control_mode=pairstate_control_mode)
            p1 = float(result["score"])
            assert per_sample_results is not None
            per_sample_results.append(result)
        else:
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
    if is_synthetic_offset_rows(test):
        if variant in {"V_pairstate_relational", "V_future_sector_contrast_pairstate"}:
            diagnostics = build_pairstate_run_diagnostics(rows=test, results=per_sample_results or [])
        else:
            diagnostics = build_run_diagnostics(rows=test, scores=probs)
    else:
        diagnostics = None
    return train_loss, eval_loss, accuracy, f1, diagnostics


def sigmoid(value: float) -> float:
    if value >= 0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)


def fit_logistic_witness_head(
    features: list[list[float]],
    labels: list[int],
    steps: int = 300,
    learning_rate: float = 0.5,
    l2: float = 0.01,
) -> tuple[list[float], float]:
    if not features:
        return [], 0.0
    width = len(features[0])
    weights = [0.0] * width
    bias = 0.0
    n = len(features)
    for _ in range(steps):
        grad_w = [0.0] * width
        grad_b = 0.0
        for row, label in zip(features, labels):
            logit = bias + sum(weight * value for weight, value in zip(weights, row))
            pred = sigmoid(logit)
            error = pred - label
            for idx, value in enumerate(row):
                grad_w[idx] += error * value
            grad_b += error
        for idx in range(width):
            grad_w[idx] = grad_w[idx] / n + l2 * weights[idx]
            weights[idx] -= learning_rate * grad_w[idx]
        bias -= learning_rate * (grad_b / n)
    return weights, bias


def build_relational_witness_feature_mask(
    feature_order: list[str],
    witness_feature_mode: str,
) -> tuple[list[float], dict[str, Any]]:
    if witness_feature_mode == "full":
        mask = [1.0] * len(feature_order)
    elif witness_feature_mode in RELATIONAL_WITNESS_FEATURE_GROUPS:
        disabled = set(RELATIONAL_WITNESS_FEATURE_GROUPS[witness_feature_mode])
        mask = [0.0 if name in disabled else 1.0 for name in feature_order]
    elif witness_feature_mode in RELATIONAL_WITNESS_SCHEMA_VIEWS:
        retained = set(RELATIONAL_WITNESS_SCHEMA_VIEWS[witness_feature_mode])
        mask = [1.0 if name in retained else 0.0 for name in feature_order]
    else:
        allowed = ", ".join(["full", *RELATIONAL_WITNESS_FEATURE_GROUPS.keys(), *RELATIONAL_WITNESS_SCHEMA_VIEWS.keys()])
        raise ValueError(f"Unsupported witness_feature_mode={witness_feature_mode!r}. Allowed: {allowed}")

    group_state = {
        group_name: {
            "features": list(feature_names),
            "ablated": group_name == witness_feature_mode,
        }
        for group_name, feature_names in RELATIONAL_WITNESS_FEATURE_GROUPS.items()
    }
    retained = [name for name, keep in zip(feature_order, mask) if keep > 0]
    ablated = [name for name, keep in zip(feature_order, mask) if keep == 0]
    return mask, {
        "witness_feature_mode": witness_feature_mode,
        "witness_ablation_group": witness_feature_mode if witness_feature_mode in RELATIONAL_WITNESS_FEATURE_GROUPS else "full",
        "feature_group_state": group_state,
        "retained_features": retained,
        "ablated_features": ablated,
    }


def apply_feature_mask(matrix: list[list[float]], mask: list[float]) -> list[list[float]]:
    return [[value * keep for value, keep in zip(row, mask)] for row in matrix]


def symbolic_relational_features(text: str) -> dict[str, object]:
    sample = parse_synthetic_pair_text(text)
    sector = offset_sector(int(sample["offset"]))
    feature_order = ["sec_P_small", "sec_P_large", "sec_N_small", "sec_N_large"]
    sector_to_feature = {
        "P_small": "sec_P_small",
        "P_large": "sec_P_large",
        "N_small": "sec_N_small",
        "N_large": "sec_N_large",
    }
    active = sector_to_feature[sector]
    features = {name: 1.0 if name == active else 0.0 for name in feature_order}
    return {
        "sector": sector,
        "feature_order": feature_order,
        "features": features,
        "forbidden_inputs_absent": True,
    }


def run_relational_witness_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    seed: int,
    validation: list[tuple[str, int]] | None = None,
    witness_feature_mode: str = "full",
) -> tuple[float, float, float, float, dict[str, Any]]:
    if validation is None:
        _, validation = stratified_calibration_split(train)

    train_results = [relational_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [relational_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [relational_witness_features(text=text, seed=seed) for text, _ in test]

    feature_order = list(train_results[0]["feature_order"]) if train_results else []
    train_matrix = [[float(result["features"][name]) for name in feature_order] for result in train_results]
    validation_matrix = [[float(result["features"][name]) for name in feature_order] for result in validation_results]
    test_matrix = [[float(result["features"][name]) for name in feature_order] for result in test_results]
    feature_mask, mask_diagnostics = build_relational_witness_feature_mask(feature_order, witness_feature_mode)
    train_matrix = apply_feature_mask(train_matrix, feature_mask)
    validation_matrix = apply_feature_mask(validation_matrix, feature_mask)
    test_matrix = apply_feature_mask(test_matrix, feature_mask)

    train_labels = [label for _, label in train]
    validation_labels = [label for _, label in validation]
    test_labels = [label for _, label in test]

    weights, bias = fit_logistic_witness_head(train_matrix, train_labels)

    train_scores = [sigmoid(bias + sum(weight * value for weight, value in zip(weights, row))) for row in train_matrix]
    validation_scores = [sigmoid(bias + sum(weight * value for weight, value in zip(weights, row))) for row in validation_matrix]
    test_scores = [sigmoid(bias + sum(weight * value for weight, value in zip(weights, row))) for row in test_matrix]

    threshold = calibrate_threshold(validation_scores, validation_labels)
    y_pred = [1 if score >= threshold else 0 for score in test_scores]

    diagnostics = build_relational_witness_run_diagnostics(
        rows=test,
        results=test_results,
        feature_order=feature_order,
        weights=weights,
        bias=bias,
        mask_diagnostics=mask_diagnostics,
    )
    train_loss = binary_cross_entropy(train_labels, train_scores)
    eval_loss = binary_cross_entropy(test_labels, test_scores)
    accuracy = compute_accuracy(test_labels, y_pred)
    f1 = compute_f1_binary(test_labels, y_pred)
    return train_loss, eval_loss, accuracy, f1, diagnostics


def run_symbolic_relational_control_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    if validation is None:
        _, validation = stratified_calibration_split(train)

    train_results = [symbolic_relational_features(text=text) for text, _ in train]
    validation_results = [symbolic_relational_features(text=text) for text, _ in validation]
    test_results = [symbolic_relational_features(text=text) for text, _ in test]

    feature_order = list(train_results[0]["feature_order"]) if train_results else []
    train_matrix = [[float(result["features"][name]) for name in feature_order] for result in train_results]
    validation_matrix = [[float(result["features"][name]) for name in feature_order] for result in validation_results]
    test_matrix = [[float(result["features"][name]) for name in feature_order] for result in test_results]

    train_labels = [label for _, label in train]
    validation_labels = [label for _, label in validation]
    test_labels = [label for _, label in test]

    weights, bias = fit_logistic_witness_head(train_matrix, train_labels)
    train_scores = [sigmoid(bias + sum(weight * value for weight, value in zip(weights, row))) for row in train_matrix]
    validation_scores = [sigmoid(bias + sum(weight * value for weight, value in zip(weights, row))) for row in validation_matrix]
    test_scores = [sigmoid(bias + sum(weight * value for weight, value in zip(weights, row))) for row in test_matrix]

    threshold = calibrate_threshold(validation_scores, validation_labels)
    y_pred = [1 if score >= threshold else 0 for score in test_scores]

    diagnostics = build_symbolic_relational_run_diagnostics(
        rows=test,
        results=test_results,
        feature_order=feature_order,
        weights=weights,
        bias=bias,
    )
    train_loss = binary_cross_entropy(train_labels, train_scores)
    eval_loss = binary_cross_entropy(test_labels, test_scores)
    accuracy = compute_accuracy(test_labels, y_pred)
    f1 = compute_f1_binary(test_labels, y_pred)
    return train_loss, eval_loss, accuracy, f1, diagnostics


def is_synthetic_offset_rows(rows: list[tuple[str, int]]) -> bool:
    if not rows:
        return False
    try:
        parse_synthetic_pair_text(rows[0][0])
    except ValueError:
        return False
    return True


def build_run_diagnostics(rows: list[tuple[str, int]], scores: list[float]) -> dict[str, Any]:
    offset_groups: dict[int, list[float]] = {}
    positive_scores: list[float] = []
    negative_scores: list[float] = []
    for (text, label), score in zip(rows, scores):
        payload = parse_synthetic_pair_text(text)
        offset = int(payload["offset"])
        offset_groups.setdefault(offset, []).append(score)
        if label == 1:
            positive_scores.append(score)
        else:
            negative_scores.append(score)

    mean_by_offset = {str(offset): round(sum(vals) / len(vals), 6) for offset, vals in sorted(offset_groups.items())}
    positive_mean = sum(positive_scores) / len(positive_scores) if positive_scores else 0.0
    negative_mean = sum(negative_scores) / len(negative_scores) if negative_scores else 0.0
    overall_mean = sum(scores) / len(scores) if scores else 0.0
    return {
        "score_by_offset": mean_by_offset,
        "positive_minus_negative_offset_gap": round(positive_mean - negative_mean, 6),
        "overall_score_mean": round(overall_mean, 6),
    }


def build_pairstate_run_diagnostics(rows: list[tuple[str, int]], results: list[dict[str, Any]]) -> dict[str, Any]:
    offset_groups: dict[int, list[float]] = {}
    sector_score_groups = {key: [] for key in ("P_small", "P_large", "N_small", "N_large")}
    positive_scores: list[float] = []
    negative_scores: list[float] = []
    channel_groups = {key: [] for key in ("P_small", "P_large", "N_small", "N_large")}
    assigned_sector_groups = {key: [] for key in ("P_small", "P_large", "N_small", "N_large")}
    pre_aggregation_flags: list[bool] = []
    signed_contrasts: list[float] = []
    magnitude_balances: list[float] = []
    control_modes: set[str] = set()
    aggregation_buckets: dict[str, list[str]] | None = None

    for (text, label), result in zip(rows, results):
        payload = parse_synthetic_pair_text(text)
        score = float(result["score"])
        offset = int(payload["offset"])
        offset_groups.setdefault(offset, []).append(score)
        sector_score_groups[str(result["sector"])].append(score)
        if label == 1:
            positive_scores.append(score)
        else:
            negative_scores.append(score)
        sector_responses = result["sector_responses"]
        for key in channel_groups:
            channel_groups[key].append(float(sector_responses[key]))
        assigned_sector = str(result["sector"])
        assigned_sector_groups[assigned_sector].append(float(sector_responses[assigned_sector]))
        pre_aggregation_flags.append(bool(result["sector_resolution_pre_aggregation"]))
        signed_contrasts.append(float(result["signed_contrast"]))
        magnitude_balances.append(float(result["magnitude_balance"]))
        control_modes.add(str(result.get("control_mode", "aligned")))
        if aggregation_buckets is None:
            buckets = result.get("aggregation_buckets", {})
            aggregation_buckets = {
                "positive": list(buckets.get("positive", [])),
                "negative": list(buckets.get("negative", [])),
            }

    mean_by_offset = {str(offset): round(sum(vals) / len(vals), 6) for offset, vals in sorted(offset_groups.items())}
    mean_by_sector = {key: round(sum(vals) / len(vals), 6) if vals else 0.0 for key, vals in sector_score_groups.items()}
    positive_mean = sum(positive_scores) / len(positive_scores) if positive_scores else 0.0
    negative_mean = sum(negative_scores) / len(negative_scores) if negative_scores else 0.0
    overall_mean = (sum(positive_scores) + sum(negative_scores)) / len(results) if results else 0.0
    mean_channel_responses = {
        key: round(sum(vals) / len(vals), 6) if vals else 0.0 for key, vals in channel_groups.items()
    }
    mean_sector_responses = {
        key: round(sum(vals) / len(vals), 6) if vals else 0.0 for key, vals in assigned_sector_groups.items()
    }
    signed_contrast_mean = sum(signed_contrasts) / len(signed_contrasts) if signed_contrasts else 0.0
    magnitude_balance_mean = sum(magnitude_balances) / len(magnitude_balances) if magnitude_balances else 0.0
    return {
        "score_by_offset": mean_by_offset,
        "score_by_sector": mean_by_sector,
        "positive_minus_negative_offset_gap": round(positive_mean - negative_mean, 6),
        "overall_score_mean": round(overall_mean, 6),
        "control_mode": sorted(control_modes)[0] if len(control_modes) == 1 else "mixed",
        "aggregation_buckets": aggregation_buckets or {"positive": [], "negative": []},
        "sector_responses": mean_sector_responses,
        "channel_response_means": mean_channel_responses,
        "signed_contrast_mean": round(signed_contrast_mean, 6),
        "task_contrast_mean": round(signed_contrast_mean, 6),
        "magnitude_balance_mean": round(magnitude_balance_mean, 6),
        "sector_resolution_pre_aggregation": all(pre_aggregation_flags),
        "anti_collapse_pass": bool(aggregation_buckets) and all(pre_aggregation_flags),
    }


def build_relational_witness_run_diagnostics(
    rows: list[tuple[str, int]],
    results: list[dict[str, Any]],
    feature_order: list[str],
    weights: list[float],
    bias: float,
    mask_diagnostics: dict[str, Any],
) -> dict[str, Any]:
    sector_response_groups = {key: [] for key in ("P_small", "P_large", "N_small", "N_large")}
    task_contrasts: list[float] = []
    anti_collapse_flags: list[bool] = []
    forbidden_absent_flags: list[bool] = []
    for _, result in zip(rows, results):
        for key, value in result["sector_responses"].items():
            sector_response_groups[key].append(float(value))
        task_contrasts.append(float(result["task_contrast"]))
        anti_collapse_flags.append(bool(result["anti_collapse_pass"]))
        forbidden_absent_flags.append(bool(result["forbidden_inputs_absent"]))
    mean_sector_responses = {
        key: round(sum(values) / len(values), 6) if values else 0.0 for key, values in sector_response_groups.items()
    }
    return {
        "feature_order": feature_order,
        "coefficients": {name: round(weight, 6) for name, weight in zip(feature_order, weights)},
        "intercept": round(bias, 6),
        "witness_feature_mode": mask_diagnostics["witness_feature_mode"],
        "witness_ablation_group": mask_diagnostics["witness_ablation_group"],
        "feature_group_state": mask_diagnostics["feature_group_state"],
        "retained_features": mask_diagnostics["retained_features"],
        "ablated_features": mask_diagnostics["ablated_features"],
        "sector_responses": mean_sector_responses,
        "task_contrast_mean": round(sum(task_contrasts) / len(task_contrasts), 6) if task_contrasts else 0.0,
        "anti_collapse_pass": all(anti_collapse_flags),
        "forbidden_inputs_absent": all(forbidden_absent_flags),
    }


def build_symbolic_relational_run_diagnostics(
    rows: list[tuple[str, int]],
    results: list[dict[str, Any]],
    feature_order: list[str],
    weights: list[float],
    bias: float,
) -> dict[str, Any]:
    sector_counts = {key: 0 for key in ("P_small", "P_large", "N_small", "N_large")}
    forbidden_absent_flags: list[bool] = []
    for _, result in zip(rows, results):
        sector_counts[str(result["sector"])] += 1
        forbidden_absent_flags.append(bool(result["forbidden_inputs_absent"]))
    return {
        "feature_order": feature_order,
        "coefficients": {name: round(weight, 6) for name, weight in zip(feature_order, weights)},
        "intercept": round(bias, 6),
        "sector_counts": sector_counts,
        "forbidden_inputs_absent": all(forbidden_absent_flags),
    }


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


def load_dataset_bundle(dataset: str, seed: int, split_rotation: int = 0) -> dict[str, Any]:
    if dataset == "synthetic_offset_binary":
        bundle = generate_signed_offset_binary_bundle(seed=seed, split_rotation=split_rotation)
        return {
            "train": bundle.train,
            "validation": bundle.validation,
            "test": bundle.test,
            "data_mode": "synthetic_offset_binary",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_sector_parity_binary":
        bundle = generate_sector_parity_binary_bundle(seed=seed, split_rotation=split_rotation)
        return {
            "train": bundle.train,
            "validation": bundle.validation,
            "test": bundle.test,
            "data_mode": "synthetic_sector_parity_binary",
            "dataset_diagnostics": bundle.diagnostics,
        }

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
            return {"rows": rows, "data_mode": "local_jsonl"}
    return {"rows": generate_synthetic_dataset(dataset, seed), "data_mode": "synthetic_fallback"}


def load_dataset_samples(dataset: str, seed: int, split_rotation: int = 0) -> tuple[list[tuple[str, int]], str]:
    bundle = load_dataset_bundle(dataset, seed, split_rotation=split_rotation)
    if "rows" in bundle:
        return bundle["rows"], bundle["data_mode"]
    rows = bundle["train"] + bundle["validation"] + bundle["test"]
    return rows, bundle["data_mode"]


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
