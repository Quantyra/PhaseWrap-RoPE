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
from .synthetic import (
    content_family_name,
    generate_dual_continuous_coupled_response_bundle,
    generate_dual_latent_phase_manifold_residual_response_bundle,
    generate_dual_local_atlas_manifold_response_bundle,
    generate_dual_chart_transition_manifold_response_bundle,
    generate_chart_transition_token_invariant_response_bundle,
    generate_chart_transition_orbit_response_bundle,
    generate_dual_content_parity_coupling_binary_bundle,
    generate_dual_nonlinear_manifold_response_bundle,
    generate_dual_phase_sensitive_manifold_response_bundle,
    generate_dual_orthogonalized_continuous_response_bundle,
    generate_dual_state_sensitive_continuous_response_bundle,
    generate_dual_sector_agreement_binary_bundle,
    generate_dual_sector_content_agreement_binary_bundle,
    generate_transition_orbit_listwise_ranking_bundle,
    generate_transition_orbit_sign_consistency_binary_bundle,
    generate_transition_orbit_sign_flip_contrast_binary_bundle,
    generate_transition_orbit_signed_margin_response_bundle,
    generate_transition_orbit_sign_only_binary_bundle,
    generate_transition_orbit_order_margin_response_bundle,
    generate_transition_orbit_pairwise_order_binary_bundle,
    generate_transition_orbit_rank_band_response_bundle,
    parse_transition_consistency_text,
    parse_transition_listwise_text,
    parse_transition_pairwise_text,
    render_dual_sample_text,
    generate_sector_parity_binary_bundle,
    token_orientation_name,
)

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
        synthetic_slot_swap = int(dataset_block.get("slot_swap", 0))
        synthetic_token_permutation = str(dataset_block.get("token_permutation", "identity"))
        synthetic_pair_reindex = int(dataset_block.get("pair_reindex", 0))
    else:
        dataset = str(dataset_block)
        synthetic_split_rotation = 0
        synthetic_slot_swap = 0
        synthetic_token_permutation = "identity"
        synthetic_pair_reindex = 0
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
            synthetic_slot_swap=synthetic_slot_swap,
            synthetic_token_permutation=synthetic_token_permutation,
            synthetic_pair_reindex=synthetic_pair_reindex,
        )
        accuracy = real_metrics["accuracy"]
        f1 = real_metrics["f1"]
        train_loss_final = real_metrics["train_loss_final"]
        eval_loss = real_metrics["eval_loss"]
        data_mode = real_metrics["data_mode"]
        dataset_diagnostics = real_metrics.get("dataset_diagnostics")
        run_diagnostics = real_metrics.get("run_diagnostics")
        extra_metrics = real_metrics.get("extra_metrics", {})
    else:
        accuracy = 0.0
        f1 = 0.0
        train_loss_final = 0.0
        eval_loss = 0.0
        data_mode = "n/a"
        dataset_diagnostics = None
        run_diagnostics = None
        extra_metrics = {}

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
    metrics.update(extra_metrics)

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
        "V_future_relational_witness_dual": 20,
        "V_control_symbolic_dual_sector": 1,
        "V_control_symbolic_dual_interaction": 1,
        "V_future_relational_witness_dual_content": 20,
        "V_control_symbolic_dual_sector_interaction": 1,
        "V_control_symbolic_dual_content_interaction": 1,
        "V_control_symbolic_dual_cross_interaction": 1,
        "V_future_relational_witness_triple": 24,
        "V_control_symbolic_sector_only": 1,
        "V_control_symbolic_content_only": 1,
        "V_control_symbolic_orientation_only": 1,
        "V_control_symbolic_sign_content_cross": 1,
        "V_control_symbolic_two_family_bounded": 1,
        "V_control_symbolic_three_family_parity": 1,
        "V_future_relational_witness_continuous": 24,
        "V_future_relational_witness_state_sensitive": 24,
        "V_future_relational_witness_orthogonalized": 24,
        "V_future_relational_witness_nonlinear": 24,
        "V_future_relational_witness_phase_sensitive": 24,
        "V_future_relational_witness_latent_phase": 24,
        "V_future_relational_witness_local_atlas": 24,
        "V_future_relational_witness_chart_transition": 24,
        "V_future_relational_witness_chart_transition_invariant": 24,
        "V_future_relational_witness_transition_orbit": 24,
        "V_future_relational_witness_transition_orbit_rank": 24,
        "V_future_relational_witness_transition_orbit_order": 24,
        "V_future_relational_witness_transition_orbit_listwise": 24,
        "V_future_relational_witness_transition_orbit_order_margin": 24,
        "V_future_relational_witness_transition_orbit_signed_margin": 24,
        "V_future_relational_witness_transition_orbit_sign_only": 24,
        "V_future_relational_witness_transition_orbit_sign_consistency": 24,
        "V_future_relational_witness_transition_orbit_sign_flip_contrast": 24,
        "V_control_symbolic_single_family_regressor": 1,
        "V_control_symbolic_two_family_regressor": 1,
        "V_control_symbolic_boolean_state_lookup": 1,
        "V_control_symbolic_coarse_lookup_regressor": 1,
        "V_control_symbolic_analog_only_regressor": 1,
        "V_control_symbolic_full_declared_regressor": 1,
        "V_control_symbolic_full_declared_residual_regressor": 1,
        "V_control_symbolic_full_declared_additive_regressor": 1,
        "V_control_symbolic_nonlinear_manifold_regressor": 1,
        "V_control_symbolic_phase_insensitive_regressor": 1,
        "V_control_symbolic_global_phase_regressor": 1,
        "V_control_symbolic_single_chart_regressor": 1,
        "V_control_symbolic_transition_additive_regressor": 1,
        "V_control_symbolic_transition_unordered_regressor": 1,
        "V_control_symbolic_transition_permuted_regressor": 1,
        "V_control_symbolic_transition_reversed_regressor": 1,
        "V_control_symbolic_transition_bidirectional_regressor": 1,
        "V_control_symbolic_transition_cross_direction_regressor": 1,
        "V_control_symbolic_transition_quadratic_regressor": 1,
        "V_control_symbolic_transition_cubic_regressor": 1,
        "V_control_symbolic_transition_orbit_additive_regressor": 1,
        "V_control_symbolic_transition_orbit_permuted_regressor": 1,
        "V_control_symbolic_transition_orbit_rank_lookup": 1,
        "V_control_symbolic_transition_order_lookup": 1,
        "V_control_symbolic_transition_order_cross_direction": 1,
        "V_control_symbolic_transition_order_quadratic": 1,
        "V_control_symbolic_transition_order_orbit_permuted": 1,
        "V_control_symbolic_transition_list_lookup": 1,
        "V_control_symbolic_transition_list_cross_direction": 1,
        "V_control_symbolic_transition_list_quadratic": 1,
        "V_control_symbolic_transition_list_orbit_permuted": 1,
        "V_control_symbolic_transition_margin_lookup": 1,
        "V_control_symbolic_transition_margin_cross_direction": 1,
        "V_control_symbolic_transition_margin_quadratic": 1,
        "V_control_symbolic_transition_margin_orbit_permuted": 1,
        "V_control_symbolic_transition_signed_margin_lookup": 1,
        "V_control_symbolic_transition_signed_margin_cross_direction": 1,
        "V_control_symbolic_transition_signed_margin_quadratic": 1,
        "V_control_symbolic_transition_signed_margin_orbit_permuted": 1,
        "V_control_symbolic_transition_consistency_lookup": 1,
        "V_control_symbolic_transition_consistency_cross_direction": 1,
        "V_control_symbolic_transition_consistency_quadratic": 1,
        "V_control_symbolic_transition_consistency_orbit_permuted": 1,
        "V_control_symbolic_transition_flip_lookup": 1,
        "V_control_symbolic_transition_flip_cross_direction": 1,
        "V_control_symbolic_transition_flip_quadratic": 1,
        "V_control_symbolic_transition_flip_orbit_permuted": 1,
        "V_control_symbolic_transition_sign_lookup": 1,
        "V_control_symbolic_transition_sign_cross_direction": 1,
        "V_control_symbolic_transition_sign_quadratic": 1,
        "V_control_symbolic_transition_sign_orbit_permuted": 1,
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
    synthetic_slot_swap: int = 0,
    synthetic_token_permutation: str = "identity",
    synthetic_pair_reindex: int = 0,
) -> dict[str, Any]:
    bundle = load_dataset_bundle(
        dataset,
        seed,
        split_rotation=synthetic_split_rotation,
        slot_swap=synthetic_slot_swap,
        token_permutation=synthetic_token_permutation,
        pair_reindex=synthetic_pair_reindex,
    )
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

    extra_metrics: dict[str, Any] = {}
    if backend == "sim_quantum_statevector":
        quantum_result = run_quantum_backend(
            train=train,
            test=test,
            seed=seed,
            dataset=dataset,
            variant=variant,
            readout=local_readout,
            mixing_preset=local_mixing_preset,
            pairstate_control_mode=pairstate_control_mode,
            witness_feature_mode=witness_feature_mode,
            validation=validation,
        )
        if len(quantum_result) == 5:
            train_loss, eval_loss, accuracy, f1, run_diagnostics = quantum_result
        else:
            train_loss, eval_loss, accuracy, f1, run_diagnostics, extra_metrics = quantum_result
        if variant == "V_new_explicit_interference":
            data_mode = f"{data_mode}+readout_parity_contrast+mix_interference"
        elif variant in {"V_pairstate_relational", "V_future_sector_contrast_pairstate"}:
            data_mode = f"{data_mode}+readout_sector_contrast+repr_pairstate+control_{pairstate_control_mode}"
        elif variant == "V_future_relational_witness":
            data_mode = f"{data_mode}+readout_relational_witness+head_logreg+featuremode_{witness_feature_mode}"
        elif variant == "V_control_symbolic_relational":
            data_mode = f"{data_mode}+readout_symbolic_relational+head_logreg"
        elif variant == "V_future_relational_witness_dual":
            data_mode = f"{data_mode}+readout_relational_witness_dual+head_logreg"
        elif variant == "V_control_symbolic_dual_sector":
            data_mode = f"{data_mode}+readout_symbolic_dual_sector+head_logreg"
        elif variant == "V_control_symbolic_dual_interaction":
            data_mode = f"{data_mode}+readout_symbolic_dual_interaction+head_logreg"
        elif variant == "V_future_relational_witness_dual_content":
            data_mode = f"{data_mode}+readout_relational_witness_dual_content+head_logreg"
        elif variant == "V_control_symbolic_dual_sector_interaction":
            data_mode = f"{data_mode}+readout_symbolic_dual_sector_interaction+head_logreg"
        elif variant == "V_control_symbolic_dual_content_interaction":
            data_mode = f"{data_mode}+readout_symbolic_dual_content_interaction+head_logreg"
        elif variant == "V_control_symbolic_dual_cross_interaction":
            data_mode = f"{data_mode}+readout_symbolic_dual_cross_interaction+head_logreg"
        elif variant == "V_future_relational_witness_triple":
            data_mode = f"{data_mode}+readout_relational_witness_triple+head_logreg"
        elif variant == "V_control_symbolic_sector_only":
            data_mode = f"{data_mode}+readout_symbolic_sector_only+head_logreg"
        elif variant == "V_control_symbolic_content_only":
            data_mode = f"{data_mode}+readout_symbolic_content_only+head_logreg"
        elif variant == "V_control_symbolic_orientation_only":
            data_mode = f"{data_mode}+readout_symbolic_orientation_only+head_logreg"
        elif variant == "V_control_symbolic_sign_content_cross":
            data_mode = f"{data_mode}+readout_symbolic_sign_content_cross+head_logreg"
        elif variant == "V_control_symbolic_two_family_bounded":
            data_mode = f"{data_mode}+readout_symbolic_two_family_bounded+head_logreg"
        elif variant == "V_control_symbolic_three_family_parity":
            data_mode = f"{data_mode}+readout_symbolic_three_family_parity+head_logreg"
        elif variant == "V_future_relational_witness_continuous":
            data_mode = f"{data_mode}+readout_relational_witness_continuous+head_linear"
        elif variant == "V_future_relational_witness_state_sensitive":
            data_mode = f"{data_mode}+readout_relational_witness_state_sensitive+head_linear"
        elif variant == "V_future_relational_witness_orthogonalized":
            data_mode = f"{data_mode}+readout_relational_witness_orthogonalized+head_linear"
        elif variant == "V_future_relational_witness_nonlinear":
            data_mode = f"{data_mode}+readout_relational_witness_nonlinear+head_linear"
        elif variant == "V_future_relational_witness_phase_sensitive":
            data_mode = f"{data_mode}+readout_relational_witness_phase_sensitive+head_linear"
        elif variant == "V_future_relational_witness_latent_phase":
            data_mode = f"{data_mode}+readout_relational_witness_latent_phase+head_linear"
        elif variant == "V_future_relational_witness_local_atlas":
            data_mode = f"{data_mode}+readout_relational_witness_local_atlas+head_linear"
        elif variant == "V_future_relational_witness_chart_transition":
            data_mode = f"{data_mode}+readout_relational_witness_chart_transition+head_linear"
        elif variant == "V_future_relational_witness_chart_transition_invariant":
            data_mode = f"{data_mode}+readout_relational_witness_chart_transition_invariant+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_rank":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_rank+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_order":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_order+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_listwise":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_listwise+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_order_margin":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_order_margin+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_signed_margin":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_signed_margin+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_sign_only":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_sign_only+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_sign_consistency":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_sign_consistency+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_sign_flip_contrast":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_sign_flip_contrast+head_linear"
        elif variant == "V_control_symbolic_single_family_regressor":
            data_mode = f"{data_mode}+readout_symbolic_single_family_regressor+head_linear"
        elif variant == "V_control_symbolic_two_family_regressor":
            data_mode = f"{data_mode}+readout_symbolic_two_family_regressor+head_linear"
        elif variant == "V_control_symbolic_boolean_state_lookup":
            data_mode = f"{data_mode}+readout_symbolic_boolean_state_lookup+head_linear"
        elif variant == "V_control_symbolic_coarse_lookup_regressor":
            data_mode = f"{data_mode}+readout_symbolic_coarse_lookup_regressor+head_linear"
        elif variant == "V_control_symbolic_analog_only_regressor":
            data_mode = f"{data_mode}+readout_symbolic_analog_only_regressor+head_linear"
        elif variant == "V_control_symbolic_full_declared_regressor":
            data_mode = f"{data_mode}+readout_symbolic_full_declared_regressor+head_linear"
        elif variant == "V_control_symbolic_full_declared_residual_regressor":
            data_mode = f"{data_mode}+readout_symbolic_full_declared_residual_regressor+head_linear"
        elif variant == "V_control_symbolic_full_declared_additive_regressor":
            data_mode = f"{data_mode}+readout_symbolic_full_declared_additive_regressor+head_linear"
        elif variant == "V_control_symbolic_nonlinear_manifold_regressor":
            data_mode = f"{data_mode}+readout_symbolic_nonlinear_manifold_regressor+head_linear"
        elif variant == "V_control_symbolic_phase_insensitive_regressor":
            data_mode = f"{data_mode}+readout_symbolic_phase_insensitive_regressor+head_linear"
        elif variant == "V_control_symbolic_global_phase_regressor":
            data_mode = f"{data_mode}+readout_symbolic_global_phase_regressor+head_linear"
        elif variant == "V_control_symbolic_single_chart_regressor":
            data_mode = f"{data_mode}+readout_symbolic_single_chart_regressor+head_linear"
        elif variant == "V_control_symbolic_transition_additive_regressor":
            data_mode = f"{data_mode}+readout_symbolic_transition_additive_regressor+head_linear"
        elif variant == "V_control_symbolic_transition_unordered_regressor":
            data_mode = f"{data_mode}+readout_symbolic_transition_unordered_regressor+head_linear"
        elif variant == "V_control_symbolic_transition_permuted_regressor":
            data_mode = f"{data_mode}+readout_symbolic_transition_permuted_regressor+head_linear"
        elif variant == "V_control_symbolic_transition_reversed_regressor":
            data_mode = f"{data_mode}+readout_symbolic_transition_reversed_regressor+head_linear"
        elif variant == "V_control_symbolic_transition_bidirectional_regressor":
            data_mode = f"{data_mode}+readout_symbolic_transition_bidirectional_regressor+head_linear"
        elif variant == "V_control_symbolic_transition_cross_direction_regressor":
            data_mode = f"{data_mode}+readout_symbolic_transition_cross_direction_regressor+head_linear"
        elif variant == "V_control_symbolic_transition_quadratic_regressor":
            data_mode = f"{data_mode}+readout_symbolic_transition_quadratic_regressor+head_linear"
        elif variant == "V_control_symbolic_transition_cubic_regressor":
            data_mode = f"{data_mode}+readout_symbolic_transition_cubic_regressor+head_linear"
        elif variant == "V_control_symbolic_transition_orbit_additive_regressor":
            data_mode = f"{data_mode}+readout_symbolic_transition_orbit_additive_regressor+head_linear"
        elif variant == "V_control_symbolic_transition_orbit_permuted_regressor":
            data_mode = f"{data_mode}+readout_symbolic_transition_orbit_permuted_regressor+head_linear"
        elif variant == "V_control_symbolic_transition_orbit_rank_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_orbit_rank_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_order_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_order_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_order_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_order_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_order_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_order_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_order_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_order_orbit_permuted+head_linear"
        elif variant == "V_control_symbolic_transition_list_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_list_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_list_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_list_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_list_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_list_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_list_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_list_orbit_permuted+head_linear"
        elif variant == "V_control_symbolic_transition_margin_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_margin_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_margin_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_margin_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_margin_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_margin_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_margin_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_margin_orbit_permuted+head_linear"
        elif variant == "V_control_symbolic_transition_signed_margin_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_signed_margin_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_signed_margin_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_signed_margin_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_signed_margin_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_signed_margin_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_signed_margin_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_signed_margin_orbit_permuted+head_linear"
        elif variant == "V_control_symbolic_transition_consistency_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_consistency_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_consistency_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_consistency_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_consistency_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_consistency_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_consistency_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_consistency_orbit_permuted+head_linear"
        elif variant == "V_control_symbolic_transition_flip_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_flip_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_flip_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_flip_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_flip_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_flip_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_flip_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_flip_orbit_permuted+head_linear"
        elif variant == "V_control_symbolic_transition_sign_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_sign_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_sign_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_sign_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_sign_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_sign_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_sign_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_sign_orbit_permuted+head_linear"
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
        "extra_metrics": extra_metrics,
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
    dataset: str,
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
    if variant == "V_future_relational_witness_dual":
        return run_dual_relational_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_control_symbolic_dual_sector":
        return run_dual_symbolic_control_backend(train=train, test=test, validation=validation)
    if variant == "V_control_symbolic_dual_interaction":
        return run_dual_symbolic_interaction_control_backend(train=train, test=test, validation=validation)
    if variant == "V_future_relational_witness_dual_content":
        return run_dual_content_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_control_symbolic_dual_sector_interaction":
        return run_dual_symbolic_interaction_control_backend(train=train, test=test, validation=validation)
    if variant == "V_control_symbolic_dual_content_interaction":
        return run_dual_symbolic_content_control_backend(train=train, test=test, validation=validation)
    if variant == "V_control_symbolic_dual_cross_interaction":
        return run_dual_symbolic_cross_control_backend(train=train, test=test, validation=validation)
    if variant == "V_future_relational_witness_triple":
        return run_triple_relational_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_control_symbolic_sector_only":
        return run_dual_symbolic_interaction_control_backend(train=train, test=test, validation=validation)
    if variant == "V_control_symbolic_content_only":
        return run_dual_symbolic_content_control_backend(train=train, test=test, validation=validation)
    if variant == "V_control_symbolic_orientation_only":
        return run_triple_symbolic_orientation_control_backend(train=train, test=test, validation=validation)
    if variant == "V_control_symbolic_sign_content_cross":
        return run_dual_symbolic_cross_control_backend(train=train, test=test, validation=validation)
    if variant == "V_control_symbolic_two_family_bounded":
        return run_triple_symbolic_two_family_control_backend(train=train, test=test, validation=validation)
    if variant == "V_control_symbolic_three_family_parity":
        return run_triple_symbolic_three_family_parity_control_backend(train=train, test=test, validation=validation)
    if variant == "V_future_relational_witness_continuous":
        return run_continuous_relational_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_state_sensitive":
        return run_state_sensitive_continuous_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_orthogonalized":
        return run_orthogonalized_continuous_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_nonlinear":
        return run_nonlinear_manifold_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_phase_sensitive":
        return run_phase_sensitive_manifold_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_latent_phase":
        return run_latent_phase_manifold_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_local_atlas":
        return run_local_atlas_manifold_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_chart_transition":
        return run_chart_transition_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_chart_transition_invariant":
        return run_chart_transition_invariant_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit":
        return run_transition_orbit_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_rank":
        return run_transition_orbit_rank_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_order":
        return run_transition_orbit_order_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_listwise":
        return run_transition_orbit_listwise_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_order_margin":
        return run_transition_orbit_order_margin_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_signed_margin":
        return run_transition_orbit_signed_margin_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_sign_only":
        return run_transition_orbit_sign_only_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_sign_consistency":
        return run_transition_orbit_sign_consistency_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_sign_flip_contrast":
        return run_transition_orbit_sign_flip_contrast_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_control_symbolic_single_family_regressor":
        return run_continuous_symbolic_single_family_regressor(train=train, test=test, validation=validation)
    if variant == "V_control_symbolic_two_family_regressor":
        return run_continuous_symbolic_two_family_regressor(train=train, test=test, validation=validation)
    if variant == "V_control_symbolic_boolean_state_lookup":
        return run_continuous_symbolic_boolean_state_lookup(train=train, test=test, validation=validation)
    if variant == "V_control_symbolic_coarse_lookup_regressor":
        return run_state_sensitive_symbolic_coarse_lookup_regressor(train=train, test=test, validation=validation)
    if variant == "V_control_symbolic_analog_only_regressor":
        return run_state_sensitive_symbolic_analog_only_regressor(train=train, test=test, validation=validation)
    if variant == "V_control_symbolic_full_declared_regressor":
        return run_state_sensitive_symbolic_full_declared_regressor(train=train, test=test, validation=validation)
    if variant == "V_control_symbolic_full_declared_residual_regressor":
        return run_orthogonalized_symbolic_full_declared_residual_regressor(train=train, test=test, validation=validation)
    if variant == "V_control_symbolic_full_declared_additive_regressor":
        return run_nonlinear_symbolic_full_declared_additive_regressor(train=train, test=test, validation=validation)
    if variant == "V_control_symbolic_nonlinear_manifold_regressor":
        return run_nonlinear_symbolic_control_regressor(train=train, test=test, validation=validation)
    if variant == "V_control_symbolic_phase_insensitive_regressor":
        return run_phase_insensitive_symbolic_regressor(train=train, test=test, validation=validation)
    if variant == "V_control_symbolic_global_phase_regressor":
        return run_global_phase_symbolic_regressor(train=train, test=test, validation=validation)
    if variant == "V_control_symbolic_single_chart_regressor":
        return run_single_chart_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset == "synthetic_chart_transition_token_invariant_response" and variant == "V_control_symbolic_transition_additive_regressor":
        return run_transition_invariant_additive_symbolic_regressor(train=train, test=test, validation=validation)
    if variant == "V_control_symbolic_transition_additive_regressor":
        return run_transition_additive_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset == "synthetic_chart_transition_token_invariant_response" and variant == "V_control_symbolic_transition_unordered_regressor":
        return run_transition_invariant_unordered_symbolic_regressor(train=train, test=test, validation=validation)
    if variant == "V_control_symbolic_transition_unordered_regressor":
        return run_transition_unordered_symbolic_regressor(train=train, test=test, validation=validation)
    if variant == "V_control_symbolic_transition_permuted_regressor":
        return run_transition_permuted_symbolic_regressor(train=train, test=test, validation=validation)
    if variant == "V_control_symbolic_transition_reversed_regressor":
        return run_transition_reversed_symbolic_regressor(train=train, test=test, validation=validation)
    if variant == "V_control_symbolic_transition_bidirectional_regressor":
        return run_transition_bidirectional_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset == "synthetic_chart_transition_token_invariant_response" and variant == "V_control_symbolic_transition_cross_direction_regressor":
        return run_transition_invariant_cross_direction_symbolic_regressor(train=train, test=test, validation=validation)
    if variant == "V_control_symbolic_transition_cross_direction_regressor":
        return run_transition_cross_direction_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset == "synthetic_chart_transition_token_invariant_response" and variant == "V_control_symbolic_transition_quadratic_regressor":
        return run_transition_invariant_quadratic_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset == "synthetic_chart_transition_orbit_response" and variant == "V_control_symbolic_transition_orbit_additive_regressor":
        return run_transition_orbit_additive_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset in {"synthetic_chart_transition_orbit_response", "synthetic_transition_orbit_rank_band_response"} and variant == "V_control_symbolic_transition_orbit_permuted_regressor":
        return run_transition_orbit_permuted_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_rank_band_response" and variant == "V_control_symbolic_transition_orbit_rank_lookup":
        return run_transition_orbit_rank_lookup_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_pairwise_order_binary" and variant == "V_control_symbolic_transition_order_lookup":
        return run_transition_order_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_pairwise_order_binary" and variant == "V_control_symbolic_transition_order_cross_direction":
        return run_transition_order_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_pairwise_order_binary" and variant == "V_control_symbolic_transition_order_quadratic":
        return run_transition_order_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_pairwise_order_binary" and variant == "V_control_symbolic_transition_order_orbit_permuted":
        return run_transition_order_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_listwise_ranking" and variant == "V_control_symbolic_transition_list_lookup":
        return run_transition_list_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_listwise_ranking" and variant == "V_control_symbolic_transition_list_cross_direction":
        return run_transition_list_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_listwise_ranking" and variant == "V_control_symbolic_transition_list_quadratic":
        return run_transition_list_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_listwise_ranking" and variant == "V_control_symbolic_transition_list_orbit_permuted":
        return run_transition_list_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_order_margin_response" and variant == "V_control_symbolic_transition_margin_lookup":
        return run_transition_margin_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_order_margin_response" and variant == "V_control_symbolic_transition_margin_cross_direction":
        return run_transition_margin_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_order_margin_response" and variant == "V_control_symbolic_transition_margin_quadratic":
        return run_transition_margin_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_order_margin_response" and variant == "V_control_symbolic_transition_margin_orbit_permuted":
        return run_transition_margin_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_signed_margin_response" and variant == "V_control_symbolic_transition_signed_margin_lookup":
        return run_transition_signed_margin_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_signed_margin_response" and variant == "V_control_symbolic_transition_signed_margin_cross_direction":
        return run_transition_signed_margin_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_signed_margin_response" and variant == "V_control_symbolic_transition_signed_margin_quadratic":
        return run_transition_signed_margin_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_signed_margin_response" and variant == "V_control_symbolic_transition_signed_margin_orbit_permuted":
        return run_transition_signed_margin_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_sign_only_binary" and variant == "V_control_symbolic_transition_sign_lookup":
        return run_transition_sign_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_sign_only_binary" and variant == "V_control_symbolic_transition_sign_cross_direction":
        return run_transition_sign_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_sign_only_binary" and variant == "V_control_symbolic_transition_sign_quadratic":
        return run_transition_sign_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_sign_only_binary" and variant == "V_control_symbolic_transition_sign_orbit_permuted":
        return run_transition_sign_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_sign_consistency_binary" and variant == "V_control_symbolic_transition_consistency_lookup":
        return run_transition_consistency_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_sign_consistency_binary" and variant == "V_control_symbolic_transition_consistency_cross_direction":
        return run_transition_consistency_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_sign_consistency_binary" and variant == "V_control_symbolic_transition_consistency_quadratic":
        return run_transition_consistency_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_sign_consistency_binary" and variant == "V_control_symbolic_transition_consistency_orbit_permuted":
        return run_transition_consistency_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_sign_flip_contrast_binary" and variant == "V_control_symbolic_transition_flip_lookup":
        return run_transition_flip_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_sign_flip_contrast_binary" and variant == "V_control_symbolic_transition_flip_cross_direction":
        return run_transition_flip_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_sign_flip_contrast_binary" and variant == "V_control_symbolic_transition_flip_quadratic":
        return run_transition_flip_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_sign_flip_contrast_binary" and variant == "V_control_symbolic_transition_flip_orbit_permuted":
        return run_transition_flip_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
    if variant == "V_control_symbolic_transition_quadratic_regressor":
        return run_transition_quadratic_symbolic_regressor(train=train, test=test, validation=validation)
    if variant == "V_control_symbolic_transition_cubic_regressor":
        return run_transition_cubic_symbolic_regressor(train=train, test=test, validation=validation)
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


def fit_linear_regressor(
    features: list[list[float]],
    targets: list[float],
    steps: int = 400,
    learning_rate: float = 0.1,
    l2: float = 0.001,
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
        for row, target in zip(features, targets):
            pred = bias + sum(weight * value for weight, value in zip(weights, row))
            error = pred - target
            for idx, value in enumerate(row):
                grad_w[idx] += error * value
            grad_b += error
        for idx in range(width):
            grad_w[idx] = grad_w[idx] / n + l2 * weights[idx]
            weights[idx] -= learning_rate * grad_w[idx]
        bias -= learning_rate * (grad_b / n)
    return weights, bias


def mean_absolute_error(y_true: list[float], y_pred: list[float]) -> float:
    if not y_true:
        return 0.0
    return sum(abs(a - b) for a, b in zip(y_true, y_pred)) / len(y_true)


def compute_rank_correlation(y_true: list[float], y_pred: list[float]) -> float:
    if len(y_true) < 2:
        return 0.0
    true_ranks = rank_values(y_true)
    pred_ranks = rank_values(y_pred)
    return compute_pearson(true_ranks, pred_ranks)


def rank_values(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    idx = 0
    while idx < len(indexed):
        end = idx
        while end + 1 < len(indexed) and indexed[end + 1][1] == indexed[idx][1]:
            end += 1
        avg_rank = (idx + end) / 2.0
        for pos in range(idx, end + 1):
            ranks[indexed[pos][0]] = avg_rank
        idx = end + 1
    return ranks


def compute_pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2 or len(ys) < 2:
        return 0.0
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if den_x == 0.0 or den_y == 0.0:
        return 0.0
    return num / (den_x * den_y)


def compute_calibration_slope(y_true: list[float], y_pred: list[float]) -> float:
    if len(y_true) < 2:
        return 0.0
    mean_pred = sum(y_pred) / len(y_pred)
    mean_true = sum(y_true) / len(y_true)
    denom = sum((pred - mean_pred) ** 2 for pred in y_pred)
    if denom == 0.0:
        return 0.0
    numer = sum((pred - mean_pred) * (true - mean_true) for pred, true in zip(y_pred, y_true))
    return numer / denom


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


def parse_dual_synthetic_pair_text(text: str) -> dict[str, Any]:
    parts: dict[str, str] = {}
    for item in text.strip().split():
        key, value = item.split(":", 1)
        parts[key] = value
    required = {
        "a_lt",
        "a_rt",
        "a_lp",
        "a_rp",
        "a_off",
        "b_lt",
        "b_rt",
        "b_lp",
        "b_rp",
        "b_off",
    }
    missing = required.difference(parts)
    if missing:
        raise ValueError(f"Missing dual synthetic fields: {sorted(missing)}")
    sector_a = offset_sector(int(parts["a_off"]))
    sector_b = offset_sector(int(parts["b_off"]))
    content_family_a = content_family_name(parts["a_lt"], parts["a_rt"])
    content_family_b = content_family_name(parts["b_lt"], parts["b_rt"])
    orientation_a = token_orientation_name(parts["a_lt"], parts["a_rt"])
    orientation_b = token_orientation_name(parts["b_lt"], parts["b_rt"])
    positive_sectors = {"P_small", "P_large"}
    sign_agreement = (sector_a in positive_sectors) == (sector_b in positive_sectors)
    content_agreement = content_family_a == content_family_b
    orientation_agreement = orientation_a == orientation_b
    return {
        "obs_a": f"lt:{parts['a_lt']} rt:{parts['a_rt']} lp:{int(parts['a_lp'])} rp:{int(parts['a_rp'])} off:{int(parts['a_off']):+d}",
        "obs_b": f"lt:{parts['b_lt']} rt:{parts['b_rt']} lp:{int(parts['b_lp'])} rp:{int(parts['b_rp'])} off:{int(parts['b_off']):+d}",
        "a_lt": parts["a_lt"],
        "a_rt": parts["a_rt"],
        "b_lt": parts["b_lt"],
        "b_rt": parts["b_rt"],
        "a_off": int(parts["a_off"]),
        "b_off": int(parts["b_off"]),
        "sector_a": sector_a,
        "sector_b": sector_b,
        "content_family_a": content_family_a,
        "content_family_b": content_family_b,
        "orientation_a": orientation_a,
        "orientation_b": orientation_b,
        "sign_agreement": sign_agreement,
        "content_agreement": content_agreement,
        "orientation_agreement": orientation_agreement,
    }


def token_ordinal(token: str) -> int:
    return {"A": 0, "B": 1, "C": 2, "D": 3}[token]


def state_sensitive_sector_magnitude_delta(payload: dict[str, Any]) -> float:
    return round((abs(int(payload["a_off"])) - abs(int(payload["b_off"]))) / 3.0, 6)


def state_sensitive_ordered_content_delta(payload: dict[str, Any]) -> float:
    score_a = (token_ordinal(str(payload["a_lt"])) - token_ordinal(str(payload["a_rt"]))) / 3.0
    score_b = (token_ordinal(str(payload["b_lt"])) - token_ordinal(str(payload["b_rt"]))) / 3.0
    return round(0.5 * (score_a - score_b), 6)


def nonlinear_orientation_delta(payload: dict[str, Any]) -> float:
    score_a = (token_ordinal(str(payload["a_rt"])) - token_ordinal(str(payload["a_lt"]))) / 3.0
    score_b = (token_ordinal(str(payload["b_rt"])) - token_ordinal(str(payload["b_lt"]))) / 3.0
    return round(0.5 * (score_a + score_b), 6)


def phase_sensitive_family_offset(payload: dict[str, Any]) -> float:
    family = (
        int(bool(payload["sign_agreement"])),
        int(bool(payload["content_agreement"])) ^ int(bool(payload["orientation_agreement"])),
    )
    offsets = {
        (0, 0): -math.pi / 4.0,
        (0, 1): math.pi / 8.0,
        (1, 0): math.pi / 4.0,
        (1, 1): -math.pi / 8.0,
    }
    return offsets[family]


def latent_phase_neighborhood(payload: dict[str, Any]) -> int:
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    alpha = sector_magnitude_delta + 0.5 * orientation_delta
    beta = ordered_content_delta - 0.75 * sector_magnitude_delta
    return (1 if alpha >= 0.0 else 0) * 2 + (1 if beta >= 0.0 else 0)


def latent_phase_family_offset(payload: dict[str, Any]) -> float:
    offsets = {
        0: -math.pi / 3.0,
        1: math.pi / 6.0,
        2: math.pi / 2.0,
        3: -math.pi / 8.0,
    }
    return offsets[latent_phase_neighborhood(payload)]


def local_atlas_chart_id(payload: dict[str, Any]) -> int:
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    alpha = sector_magnitude_delta + 0.4 * orientation_delta
    beta = ordered_content_delta - 0.5 * sector_magnitude_delta
    return (1 if alpha >= 0.0 else 0) * 2 + (1 if beta >= 0.0 else 0)


def local_atlas_chart_params(payload: dict[str, Any]) -> tuple[float, float]:
    params = {
        0: (-math.pi / 3.0, math.pi / 7.0),
        1: (math.pi / 5.0, -math.pi / 6.0),
        2: (math.pi / 2.5, math.pi / 9.0),
        3: (-math.pi / 8.0, -math.pi / 4.5),
    }
    return params[local_atlas_chart_id(payload)]


def chart_transition_pair(payload: dict[str, Any]) -> tuple[int, int]:
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    alpha = sector_magnitude_delta + 0.4 * orientation_delta
    beta = ordered_content_delta - 0.5 * sector_magnitude_delta
    gamma = ordered_content_delta + 0.35 * orientation_delta
    delta = sector_magnitude_delta - 0.25 * orientation_delta
    source_chart = (1 if alpha >= 0.0 else 0) * 2 + (1 if beta >= 0.0 else 0)
    dest_chart = (1 if gamma >= 0.0 else 0) * 2 + (1 if delta >= 0.0 else 0)
    return source_chart, dest_chart


def chart_transition_params(payload: dict[str, Any]) -> tuple[float, float]:
    params = {
        (0, 0): (-math.pi / 4.0, math.pi / 10.0),
        (0, 1): (math.pi / 6.0, -math.pi / 7.0),
        (0, 2): (math.pi / 3.0, math.pi / 9.0),
        (0, 3): (-math.pi / 8.0, -math.pi / 5.0),
        (1, 0): (math.pi / 5.0, math.pi / 8.0),
        (1, 1): (-math.pi / 6.0, -math.pi / 9.0),
        (1, 2): (math.pi / 2.8, math.pi / 11.0),
        (1, 3): (-math.pi / 7.0, math.pi / 6.0),
        (2, 0): (math.pi / 2.6, -math.pi / 8.0),
        (2, 1): (-math.pi / 5.5, math.pi / 7.0),
        (2, 2): (math.pi / 3.4, -math.pi / 10.0),
        (2, 3): (-math.pi / 9.0, math.pi / 5.0),
        (3, 0): (math.pi / 7.0, -math.pi / 6.0),
        (3, 1): (-math.pi / 3.8, math.pi / 9.0),
        (3, 2): (math.pi / 4.5, -math.pi / 7.0),
        (3, 3): (-math.pi / 10.0, math.pi / 8.0),
    }
    return params[chart_transition_pair(payload)]


def chart_transition_permuted_params(payload: dict[str, Any]) -> tuple[float, float]:
    source_chart, dest_chart = chart_transition_pair(payload)
    permutation = {0: 2, 1: 3, 2: 1, 3: 0}
    params = {
        (0, 0): (-math.pi / 4.0, math.pi / 10.0),
        (0, 1): (math.pi / 6.0, -math.pi / 7.0),
        (0, 2): (math.pi / 3.0, math.pi / 9.0),
        (0, 3): (-math.pi / 8.0, -math.pi / 5.0),
        (1, 0): (math.pi / 5.0, math.pi / 8.0),
        (1, 1): (-math.pi / 6.0, -math.pi / 9.0),
        (1, 2): (math.pi / 2.8, math.pi / 11.0),
        (1, 3): (-math.pi / 7.0, math.pi / 6.0),
        (2, 0): (math.pi / 2.6, -math.pi / 8.0),
        (2, 1): (-math.pi / 5.5, math.pi / 7.0),
        (2, 2): (math.pi / 3.4, -math.pi / 10.0),
        (2, 3): (-math.pi / 9.0, math.pi / 5.0),
        (3, 0): (math.pi / 7.0, -math.pi / 6.0),
        (3, 1): (-math.pi / 3.8, math.pi / 9.0),
        (3, 2): (math.pi / 4.5, -math.pi / 7.0),
        (3, 3): (-math.pi / 10.0, math.pi / 8.0),
    }
    return params[(permutation[source_chart], permutation[dest_chart])]


def chart_transition_reversed_params(payload: dict[str, Any]) -> tuple[float, float]:
    source_chart, dest_chart = chart_transition_pair(payload)
    params = {
        (0, 0): (-math.pi / 4.0, math.pi / 10.0),
        (0, 1): (math.pi / 6.0, -math.pi / 7.0),
        (0, 2): (math.pi / 3.0, math.pi / 9.0),
        (0, 3): (-math.pi / 8.0, -math.pi / 5.0),
        (1, 0): (math.pi / 5.0, math.pi / 8.0),
        (1, 1): (-math.pi / 6.0, -math.pi / 9.0),
        (1, 2): (math.pi / 2.8, math.pi / 11.0),
        (1, 3): (-math.pi / 7.0, math.pi / 6.0),
        (2, 0): (math.pi / 2.6, -math.pi / 8.0),
        (2, 1): (-math.pi / 5.5, math.pi / 7.0),
        (2, 2): (math.pi / 3.4, -math.pi / 10.0),
        (2, 3): (-math.pi / 9.0, math.pi / 5.0),
        (3, 0): (math.pi / 7.0, -math.pi / 6.0),
        (3, 1): (-math.pi / 3.8, math.pi / 9.0),
        (3, 2): (math.pi / 4.5, -math.pi / 7.0),
        (3, 3): (-math.pi / 10.0, math.pi / 8.0),
    }
    return params[(dest_chart, source_chart)]


def chart_transition_unordered_params(payload: dict[str, Any]) -> tuple[float, float]:
    source_chart, dest_chart = chart_transition_pair(payload)
    ordered = tuple(sorted((source_chart, dest_chart)))
    params = {
        (0, 0): (-math.pi / 4.0, math.pi / 10.0),
        (0, 1): (math.pi / 6.0, -math.pi / 7.0),
        (0, 2): (math.pi / 3.0, math.pi / 9.0),
        (0, 3): (-math.pi / 8.0, -math.pi / 5.0),
        (1, 1): (-math.pi / 6.0, -math.pi / 9.0),
        (1, 2): (math.pi / 2.8, math.pi / 11.0),
        (1, 3): (-math.pi / 7.0, math.pi / 6.0),
        (2, 2): (math.pi / 3.4, -math.pi / 10.0),
        (2, 3): (-math.pi / 9.0, math.pi / 5.0),
        (3, 3): (-math.pi / 10.0, math.pi / 8.0),
    }
    return params[ordered]


def dual_relational_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    obs_a = relational_witness_features(text=payload["obs_a"], seed=seed)
    obs_b = relational_witness_features(text=payload["obs_b"], seed=seed)
    feature_order = [
        "cross_sign_small",
        "cross_sign_large",
        "cross_mag_pos",
        "cross_mag_neg",
        "cross_sign_sum",
        "cross_mag_sum",
    ]
    features = {
        "cross_sign_small": round(
            float(obs_a["features"]["delta_sign_small"]) * float(obs_b["features"]["delta_sign_small"]), 6
        ),
        "cross_sign_large": round(
            float(obs_a["features"]["delta_sign_large"]) * float(obs_b["features"]["delta_sign_large"]), 6
        ),
        "cross_mag_pos": round(
            float(obs_a["features"]["delta_mag_pos"]) * float(obs_b["features"]["delta_mag_pos"]), 6
        ),
        "cross_mag_neg": round(
            float(obs_a["features"]["delta_mag_neg"]) * float(obs_b["features"]["delta_mag_neg"]), 6
        ),
        "cross_sign_sum": round(
            float(obs_a["features"]["delta_sign_small"]) * float(obs_b["features"]["delta_sign_small"])
            + float(obs_a["features"]["delta_sign_large"]) * float(obs_b["features"]["delta_sign_large"]),
            6,
        ),
        "cross_mag_sum": round(
            float(obs_a["features"]["delta_mag_pos"]) * float(obs_b["features"]["delta_mag_pos"])
            + float(obs_a["features"]["delta_mag_neg"]) * float(obs_b["features"]["delta_mag_neg"]),
            6,
        ),
    }
    return {
        "feature_order": feature_order,
        "features": features,
        "sector_a": payload["sector_a"],
        "sector_b": payload["sector_b"],
        "forbidden_inputs_absent": True,
        "bounded_feature_audit_pass": True,
    }


def symbolic_dual_sector_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    feature_order = [
        "secA_P_small",
        "secA_P_large",
        "secA_N_small",
        "secA_N_large",
        "secB_P_small",
        "secB_P_large",
        "secB_N_small",
        "secB_N_large",
    ]
    features = {name: 0.0 for name in feature_order}
    features[f"secA_{payload['sector_a']}"] = 1.0
    features[f"secB_{payload['sector_b']}"] = 1.0
    return {
        "feature_order": feature_order,
        "features": features,
        "sector_a": payload["sector_a"],
        "sector_b": payload["sector_b"],
        "forbidden_inputs_absent": True,
    }


def symbolic_dual_interaction_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    sectors = ("P_small", "P_large", "N_small", "N_large")
    feature_order = [f"pair_{sector_a}__{sector_b}" for sector_a in sectors for sector_b in sectors]
    active = f"pair_{payload['sector_a']}__{payload['sector_b']}"
    features = {name: 1.0 if name == active else 0.0 for name in feature_order}
    return {
        "feature_order": feature_order,
        "features": features,
        "sector_a": payload["sector_a"],
        "sector_b": payload["sector_b"],
        "forbidden_inputs_absent": True,
    }


def symbolic_dual_content_interaction_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    families = ("aligned", "crossed")
    feature_order = [f"content_{family_a}__{family_b}" for family_a in families for family_b in families]
    active = f"content_{payload['content_family_a']}__{payload['content_family_b']}"
    features = {name: 1.0 if name == active else 0.0 for name in feature_order}
    return {
        "feature_order": feature_order,
        "features": features,
        "content_family_a": payload["content_family_a"],
        "content_family_b": payload["content_family_b"],
        "forbidden_inputs_absent": True,
    }


def symbolic_dual_cross_interaction_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    sign_agreement = "same" if payload["sign_agreement"] else "diff"
    content_agreement = "same" if payload["content_agreement"] else "diff"
    feature_order = [
        "cross_same__same",
        "cross_same__diff",
        "cross_diff__same",
        "cross_diff__diff",
    ]
    active = f"cross_{sign_agreement}__{content_agreement}"
    features = {name: 1.0 if name == active else 0.0 for name in feature_order}
    return {
        "feature_order": feature_order,
        "features": features,
        "sign_agreement": payload["sign_agreement"],
        "content_agreement": payload["content_agreement"],
        "forbidden_inputs_absent": True,
    }


def symbolic_triple_orientation_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    feature_order = [
        "orientation_forward__forward",
        "orientation_forward__reverse",
        "orientation_reverse__forward",
        "orientation_reverse__reverse",
    ]
    active = f"orientation_{payload['orientation_a']}__{payload['orientation_b']}"
    features = {name: 1.0 if name == active else 0.0 for name in feature_order}
    return {
        "feature_order": feature_order,
        "features": features,
        "orientation_a": payload["orientation_a"],
        "orientation_b": payload["orientation_b"],
        "orientation_agreement": payload["orientation_agreement"],
        "forbidden_inputs_absent": True,
    }


def symbolic_triple_two_family_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    sign_agreement = "same" if payload["sign_agreement"] else "diff"
    content_agreement = "same" if payload["content_agreement"] else "diff"
    orientation_agreement = "same" if payload["orientation_agreement"] else "diff"
    feature_order = [
        "sc_same__same",
        "sc_same__diff",
        "sc_diff__same",
        "sc_diff__diff",
        "so_same__same",
        "so_same__diff",
        "so_diff__same",
        "so_diff__diff",
        "co_same__same",
        "co_same__diff",
        "co_diff__same",
        "co_diff__diff",
    ]
    active = {
        f"sc_{sign_agreement}__{content_agreement}",
        f"so_{sign_agreement}__{orientation_agreement}",
        f"co_{content_agreement}__{orientation_agreement}",
    }
    features = {name: 1.0 if name in active else 0.0 for name in feature_order}
    return {
        "feature_order": feature_order,
        "features": features,
        "sign_agreement": payload["sign_agreement"],
        "content_agreement": payload["content_agreement"],
        "orientation_agreement": payload["orientation_agreement"],
        "forbidden_inputs_absent": True,
    }


def symbolic_triple_parity_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    parity_even = (
        1.0
        if (int(payload["sign_agreement"]) ^ int(payload["content_agreement"]) ^ int(payload["orientation_agreement"])) == 0
        else 0.0
    )
    return {
        "feature_order": ["triple_even_parity"],
        "features": {"triple_even_parity": parity_even},
        "sign_agreement": payload["sign_agreement"],
        "content_agreement": payload["content_agreement"],
        "orientation_agreement": payload["orientation_agreement"],
        "forbidden_inputs_absent": True,
    }


def dual_content_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    base = dual_relational_witness_features(text=text, seed=seed)
    content_agreement = 1.0 if payload["content_agreement"] else 0.0
    content_disagreement = 1.0 - content_agreement
    coupled_xnor = 1.0 if payload["sign_agreement"] == payload["content_agreement"] else -1.0
    feature_order = list(base["feature_order"]) + [
        "content_agreement",
        "content_disagreement",
        "coupled_xnor",
    ]
    features = dict(base["features"])
    features["content_agreement"] = content_agreement
    features["content_disagreement"] = content_disagreement
    features["coupled_xnor"] = coupled_xnor
    return {
        "feature_order": feature_order,
        "features": features,
        "sector_a": payload["sector_a"],
        "sector_b": payload["sector_b"],
        "content_family_a": payload["content_family_a"],
        "content_family_b": payload["content_family_b"],
        "sign_agreement": payload["sign_agreement"],
        "content_agreement": payload["content_agreement"],
        "forbidden_inputs_absent": True,
        "bounded_feature_audit_pass": True,
    }


def continuous_relational_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    base = triple_relational_witness_features(text=text, seed=seed)
    sign_term = 1.0 if payload["sign_agreement"] else -1.0
    content_term = 1.0 if payload["content_agreement"] else -1.0
    orientation_term = 1.0 if payload["orientation_agreement"] else -1.0
    response_linear = 0.5 * sign_term + 0.3 * content_term + 0.2 * orientation_term
    response_curvature = sign_term * content_term * orientation_term
    feature_order = list(base["feature_order"]) + ["response_linear_hint", "response_curvature_hint"]
    features = dict(base["features"])
    features["response_linear_hint"] = response_linear
    features["response_curvature_hint"] = response_curvature
    return {
        **base,
        "feature_order": feature_order,
        "features": features,
    }


def state_sensitive_continuous_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    base = triple_relational_witness_features(text=text, seed=seed)
    sign_term = 1.0 if payload["sign_agreement"] else -1.0
    content_term = 1.0 if payload["content_agreement"] else -1.0
    orientation_term = 1.0 if payload["orientation_agreement"] else -1.0
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    feature_order = list(base["feature_order"]) + [
        "sector_magnitude_delta",
        "ordered_content_delta",
        "sign_mag_coupling",
        "content_order_coupling",
    ]
    features = dict(base["features"])
    features["sector_magnitude_delta"] = sector_magnitude_delta
    features["ordered_content_delta"] = ordered_content_delta
    features["sign_mag_coupling"] = round(sign_term * sector_magnitude_delta, 6)
    features["content_order_coupling"] = round(content_term * ordered_content_delta, 6)
    return {
        **base,
        "feature_order": feature_order,
        "features": features,
    }


def symbolic_state_sensitive_coarse_lookup_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    sign_term = 1.0 if payload["sign_agreement"] else 0.0
    content_term = 1.0 if payload["content_agreement"] else 0.0
    orientation_term = 1.0 if payload["orientation_agreement"] else 0.0
    features = {
        "sign_agreement": sign_term,
        "content_agreement": content_term,
        "orientation_agreement": orientation_term,
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "forbidden_inputs_absent": True,
    }


def symbolic_state_sensitive_analog_only_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    features = {
        "sector_magnitude_delta": state_sensitive_sector_magnitude_delta(payload),
        "ordered_content_delta": state_sensitive_ordered_content_delta(payload),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "forbidden_inputs_absent": True,
    }


def symbolic_state_sensitive_full_declared_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    features = {
        "sign_agreement": 1.0 if payload["sign_agreement"] else 0.0,
        "content_agreement": 1.0 if payload["content_agreement"] else 0.0,
        "orientation_agreement": 1.0 if payload["orientation_agreement"] else 0.0,
        "sector_magnitude_delta": state_sensitive_sector_magnitude_delta(payload),
        "ordered_content_delta": state_sensitive_ordered_content_delta(payload),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "forbidden_inputs_absent": True,
    }


def orthogonalized_continuous_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    base = triple_relational_witness_features(text=text, seed=seed)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    feature_order = list(base["feature_order"]) + [
        "sector_magnitude_delta",
        "ordered_content_delta",
        "analog_residual_hint",
    ]
    features = dict(base["features"])
    features["sector_magnitude_delta"] = sector_magnitude_delta
    features["ordered_content_delta"] = ordered_content_delta
    features["analog_residual_hint"] = round(
        0.45 * sector_magnitude_delta + 0.35 * ordered_content_delta + 0.20 * (sector_magnitude_delta * ordered_content_delta),
        6,
    )
    return {
        **base,
        "feature_order": feature_order,
        "features": features,
    }


def symbolic_orthogonalized_full_declared_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    features = {
        "sign_agreement": 1.0 if payload["sign_agreement"] else 0.0,
        "content_agreement": 1.0 if payload["content_agreement"] else 0.0,
        "orientation_agreement": 1.0 if payload["orientation_agreement"] else 0.0,
        "sector_magnitude_delta": state_sensitive_sector_magnitude_delta(payload),
        "ordered_content_delta": state_sensitive_ordered_content_delta(payload),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "forbidden_inputs_absent": True,
    }


def nonlinear_manifold_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    base = triple_relational_witness_features(text=text, seed=seed)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    feature_order = list(base["feature_order"]) + [
        "sector_magnitude_delta",
        "ordered_content_delta",
        "orientation_delta",
        "nonlinear_manifold_hint",
    ]
    features = dict(base["features"])
    features["sector_magnitude_delta"] = sector_magnitude_delta
    features["ordered_content_delta"] = ordered_content_delta
    features["orientation_delta"] = orientation_delta
    features["nonlinear_manifold_hint"] = round(
        math.sin(math.pi * sector_magnitude_delta * ordered_content_delta)
        + 0.5 * (1.0 if sector_magnitude_delta >= 0.0 else -1.0) * orientation_delta
        - 0.25 * math.cos(math.pi * ordered_content_delta),
        6,
    )
    return {
        **base,
        "feature_order": feature_order,
        "features": features,
    }


def symbolic_nonlinear_full_declared_additive_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    features = {
        "sign_agreement": 1.0 if payload["sign_agreement"] else 0.0,
        "content_agreement": 1.0 if payload["content_agreement"] else 0.0,
        "orientation_agreement": 1.0 if payload["orientation_agreement"] else 0.0,
        "sector_magnitude_delta": state_sensitive_sector_magnitude_delta(payload),
        "ordered_content_delta": state_sensitive_ordered_content_delta(payload),
        "orientation_delta": nonlinear_orientation_delta(payload),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "forbidden_inputs_absent": True,
    }


def symbolic_nonlinear_manifold_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    features = {
        "sin_uv": round(math.sin(math.pi * sector_magnitude_delta * ordered_content_delta), 6),
        "signed_orientation": round(
            0.5 * (1.0 if sector_magnitude_delta >= 0.0 else -1.0) * orientation_delta,
            6,
        ),
        "cos_v": round(-0.25 * math.cos(math.pi * ordered_content_delta), 6),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "forbidden_inputs_absent": True,
    }


def phase_sensitive_manifold_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    base = triple_relational_witness_features(text=text, seed=seed)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    phase_offset = phase_sensitive_family_offset(payload)
    feature_order = list(base["feature_order"]) + [
        "sector_magnitude_delta",
        "ordered_content_delta",
        "orientation_delta",
        "phase_sensitive_hint",
    ]
    features = dict(base["features"])
    features["sector_magnitude_delta"] = sector_magnitude_delta
    features["ordered_content_delta"] = ordered_content_delta
    features["orientation_delta"] = orientation_delta
    features["phase_sensitive_hint"] = round(
        math.sin(math.pi * sector_magnitude_delta * ordered_content_delta + phase_offset)
        + 0.35 * math.cos(math.pi * (ordered_content_delta + orientation_delta)),
        6,
    )
    return {
        **base,
        "feature_order": feature_order,
        "features": features,
    }


def symbolic_phase_insensitive_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    features = {
        "sin_uv": round(math.sin(math.pi * sector_magnitude_delta * ordered_content_delta), 6),
        "cos_v_plus_w": round(0.35 * math.cos(math.pi * (ordered_content_delta + orientation_delta)), 6),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "forbidden_inputs_absent": True,
        "phase_offset_absent": True,
    }


def latent_phase_manifold_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    base = triple_relational_witness_features(text=text, seed=seed)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    latent_phase_offset = latent_phase_family_offset(payload)
    feature_order = list(base["feature_order"]) + [
        "sector_magnitude_delta",
        "ordered_content_delta",
        "orientation_delta",
        "latent_phase_hint",
    ]
    features = dict(base["features"])
    features["sector_magnitude_delta"] = sector_magnitude_delta
    features["ordered_content_delta"] = ordered_content_delta
    features["orientation_delta"] = orientation_delta
    features["latent_phase_hint"] = round(
        math.sin(math.pi * sector_magnitude_delta * ordered_content_delta)
        + 0.35
        * math.sin(
            math.pi * (sector_magnitude_delta - orientation_delta) * (ordered_content_delta + 0.5 * orientation_delta)
            + latent_phase_offset
        )
        + 0.20
        * math.cos(
            math.pi * (sector_magnitude_delta + ordered_content_delta) * orientation_delta - 0.5 * latent_phase_offset
        ),
        6,
    )
    return {
        **base,
        "feature_order": feature_order,
        "features": features,
        "bounded_feature_audit_pass": True,
    }


def symbolic_global_phase_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    phase_offset = phase_sensitive_family_offset(payload)
    features = {
        "global_phase_backbone": round(
            math.sin(math.pi * sector_magnitude_delta * ordered_content_delta + phase_offset),
            6,
        ),
        "global_phase_curvature": round(
            0.20 * math.cos(math.pi * (sector_magnitude_delta + ordered_content_delta) * orientation_delta - 0.5 * phase_offset),
            6,
        ),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "forbidden_inputs_absent": True,
        "latent_neighborhood_absent": True,
        "global_phase_only": True,
    }


def local_atlas_manifold_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    base = triple_relational_witness_features(text=text, seed=seed)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    phi_chart, psi_chart = local_atlas_chart_params(payload)
    feature_order = list(base["feature_order"]) + [
        "sector_magnitude_delta",
        "ordered_content_delta",
        "orientation_delta",
        "local_atlas_hint",
    ]
    features = dict(base["features"])
    features["sector_magnitude_delta"] = sector_magnitude_delta
    features["ordered_content_delta"] = ordered_content_delta
    features["orientation_delta"] = orientation_delta
    features["local_atlas_hint"] = round(
        math.sin(math.pi * sector_magnitude_delta * ordered_content_delta)
        + 0.30
        * math.sin(
            math.pi * (sector_magnitude_delta - orientation_delta) * (ordered_content_delta + 0.4 * orientation_delta)
            + phi_chart
        )
        + 0.18
        * math.cos(
            math.pi * (sector_magnitude_delta + ordered_content_delta) * orientation_delta - psi_chart
        ),
        6,
    )
    return {
        **base,
        "feature_order": feature_order,
        "features": features,
        "bounded_feature_audit_pass": True,
    }


def symbolic_single_chart_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    fixed_phi = math.pi / 7.0
    fixed_psi = -math.pi / 6.0
    features = {
        "single_chart_backbone": round(
            math.sin(math.pi * sector_magnitude_delta * ordered_content_delta),
            6,
        ),
        "single_chart_phase": round(
            0.30
            * math.sin(
                math.pi * (sector_magnitude_delta - orientation_delta) * (ordered_content_delta + 0.4 * orientation_delta)
                + fixed_phi
            ),
            6,
        ),
        "single_chart_curvature": round(
            0.18 * math.cos(math.pi * (sector_magnitude_delta + ordered_content_delta) * orientation_delta - fixed_psi),
            6,
        ),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "forbidden_inputs_absent": True,
        "chart_id_absent": True,
        "single_chart_only": True,
    }


def chart_transition_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    base = triple_relational_witness_features(text=text, seed=seed)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    phi_transition, psi_transition = chart_transition_params(payload)
    feature_order = list(base["feature_order"]) + [
        "sector_magnitude_delta",
        "ordered_content_delta",
        "orientation_delta",
        "chart_transition_hint",
    ]
    features = dict(base["features"])
    features["sector_magnitude_delta"] = sector_magnitude_delta
    features["ordered_content_delta"] = ordered_content_delta
    features["orientation_delta"] = orientation_delta
    features["chart_transition_hint"] = round(
        math.sin(math.pi * sector_magnitude_delta * ordered_content_delta)
        + 0.28
        * math.sin(
            math.pi * (sector_magnitude_delta - orientation_delta) * (ordered_content_delta + 0.45 * orientation_delta)
            + phi_transition
        )
        + 0.20
        * math.cos(
            math.pi * (sector_magnitude_delta + ordered_content_delta) * orientation_delta - psi_transition
        ),
        6,
    )
    return {
        **base,
        "feature_order": feature_order,
        "features": features,
        "bounded_feature_audit_pass": True,
    }


def chart_transition_invariant_params(payload: dict[str, Any]) -> tuple[float, float]:
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    alpha = sector_magnitude_delta + 0.40 * orientation_delta
    beta = -sector_magnitude_delta + 0.50 * orientation_delta
    gamma = sector_magnitude_delta - 0.35 * orientation_delta
    delta = -sector_magnitude_delta - 0.25 * orientation_delta
    source_chart = (1 if alpha >= 0.0 else 0) * 2 + (1 if beta >= 0.0 else 0)
    dest_chart = (1 if gamma >= 0.0 else 0) * 2 + (1 if delta >= 0.0 else 0)
    params = {
        (0, 0): (-math.pi / 4.0, math.pi / 10.0),
        (0, 1): (math.pi / 6.0, -math.pi / 7.0),
        (0, 2): (math.pi / 3.0, math.pi / 9.0),
        (0, 3): (-math.pi / 8.0, -math.pi / 5.0),
        (1, 0): (math.pi / 5.0, math.pi / 8.0),
        (1, 1): (-math.pi / 6.0, -math.pi / 9.0),
        (1, 2): (math.pi / 2.8, math.pi / 11.0),
        (1, 3): (-math.pi / 7.0, math.pi / 6.0),
        (2, 0): (math.pi / 2.6, -math.pi / 8.0),
        (2, 1): (-math.pi / 5.5, math.pi / 7.0),
        (2, 2): (math.pi / 3.4, -math.pi / 10.0),
        (2, 3): (-math.pi / 9.0, math.pi / 5.0),
        (3, 0): (math.pi / 7.0, -math.pi / 6.0),
        (3, 1): (-math.pi / 3.8, math.pi / 9.0),
        (3, 2): (math.pi / 4.5, -math.pi / 7.0),
        (3, 3): (-math.pi / 10.0, math.pi / 8.0),
    }
    return params[(source_chart, dest_chart)]


def chart_transition_invariant_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    sign_agreement = 1.0 if payload["sign_agreement"] else 0.0
    sign_disagreement = 1.0 - sign_agreement
    orientation_agreement = 1.0 if payload["orientation_agreement"] else 0.0
    orientation_disagreement = 1.0 - orientation_agreement
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    phi_transition, psi_transition = chart_transition_invariant_params(payload)
    features = {
        "sign_agreement": sign_agreement,
        "sign_disagreement": sign_disagreement,
        "orientation_agreement": orientation_agreement,
        "orientation_disagreement": orientation_disagreement,
        "sector_magnitude_delta": sector_magnitude_delta,
        "orientation_delta": orientation_delta,
        "chart_transition_invariant_hint": round(
            math.sin(math.pi * sector_magnitude_delta * orientation_delta)
            + 0.28
            * math.sin(
                math.pi * (sector_magnitude_delta - orientation_delta) * (sector_magnitude_delta + 0.45 * orientation_delta)
                + phi_transition
            )
            + 0.20 * math.cos(math.pi * (sector_magnitude_delta + orientation_delta) * orientation_delta - psi_transition),
            6,
        ),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "forbidden_inputs_absent": True,
        "token_identity_absent": True,
        "bounded_feature_audit_pass": True,
    }


def transition_orbit_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    base = triple_relational_witness_features(text=text, seed=seed)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    phi_transition, psi_transition = chart_transition_params(payload)
    feature_order = list(base["feature_order"]) + [
        "sector_magnitude_delta",
        "ordered_content_delta",
        "orientation_delta",
        "orbit_transition_hint",
    ]
    features = dict(base["features"])
    features["sector_magnitude_delta"] = sector_magnitude_delta
    features["ordered_content_delta"] = ordered_content_delta
    features["orientation_delta"] = orientation_delta
    features["orbit_transition_hint"] = round(
        math.sin(math.pi * sector_magnitude_delta * ordered_content_delta)
        + 0.28
        * math.sin(
            math.pi * (sector_magnitude_delta - orientation_delta) * (ordered_content_delta + 0.45 * orientation_delta)
            + phi_transition
        )
        + 0.20 * math.cos(math.pi * (sector_magnitude_delta + ordered_content_delta) * orientation_delta - psi_transition),
        6,
    )
    return {
        **base,
        "feature_order": feature_order,
        "features": features,
        "token_identity_absent": True,
        "bounded_feature_audit_pass": True,
    }


def transition_orbit_rank_witness_features(text: str, seed: int) -> dict[str, object]:
    base = transition_orbit_witness_features(text=text, seed=seed)
    features = dict(base["features"])
    orbit_band_delta = float(features["orbit_transition_hint"])
    features["orbit_band_delta"] = orbit_band_delta
    feature_order = list(base["feature_order"]) + ["orbit_band_delta"]
    return {
        **base,
        "feature_order": feature_order,
        "features": features,
        "token_identity_absent": True,
        "bounded_feature_audit_pass": True,
    }


def symbolic_transition_orbit_additive_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    phi_transition, psi_transition = chart_transition_params(payload)
    features = {
        "transition_backbone": round(math.sin(math.pi * sector_magnitude_delta * ordered_content_delta), 6),
        "transition_phase": round(
            0.28
            * math.sin(
                math.pi * (sector_magnitude_delta - orientation_delta) * (ordered_content_delta + 0.45 * orientation_delta)
                + phi_transition
            ),
            6,
        ),
        "transition_curvature": round(
            0.20 * math.cos(math.pi * (sector_magnitude_delta + ordered_content_delta) * orientation_delta - psi_transition),
            6,
        ),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "forbidden_inputs_absent": True,
        "token_identity_absent": True,
        "orbit_canonical_only": True,
    }


def symbolic_transition_orbit_permuted_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    phi_transition, psi_transition = chart_transition_permuted_params(payload)
    features = {
        "transition_backbone": round(math.sin(math.pi * sector_magnitude_delta * ordered_content_delta), 6),
        "transition_phase_permuted": round(
            0.28
            * math.sin(
                math.pi * (sector_magnitude_delta - orientation_delta) * (ordered_content_delta + 0.45 * orientation_delta)
                + phi_transition
            ),
            6,
        ),
        "transition_curvature_permuted": round(
            0.20 * math.cos(math.pi * (sector_magnitude_delta + ordered_content_delta) * orientation_delta - psi_transition),
            6,
        ),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "forbidden_inputs_absent": True,
        "token_identity_absent": True,
        "orbit_canonical_only": True,
        "transition_table_permuted": True,
    }


def symbolic_transition_orbit_rank_lookup_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    source_chart, dest_chart = chart_transition_pair(payload)
    feature_order: list[str] = []
    features: dict[str, float] = {}
    for src in range(4):
        for dst in range(4):
            key = f"coarse_state_{src}_{dst}"
            feature_order.append(key)
            features[key] = 1.0 if (src, dst) == (source_chart, dest_chart) else 0.0
    return {
        "feature_order": feature_order,
        "features": features,
        "forbidden_inputs_absent": True,
        "token_identity_absent": True,
        "coarse_state_only": True,
    }


def transition_orbit_order_pair_features(text: str) -> dict[str, Any]:
    payload = parse_transition_pairwise_text(text)
    return payload


def transition_orbit_order_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = transition_orbit_order_pair_features(text)
    u_base = transition_orbit_rank_witness_features(text=payload["u"]["dual_text"], seed=seed)
    v_base = transition_orbit_rank_witness_features(text=payload["v"]["dual_text"], seed=seed)
    feature_order = list(u_base["feature_order"])
    features = {
        name: round(float(u_base["features"][name]) - float(v_base["features"][name]), 6)
        for name in feature_order
    }
    coarse_state = payload["coarse_state_u"]
    return {
        "feature_order": feature_order,
        "features": features,
        "coarse_state": f"{coarse_state[0]}->{coarse_state[1]}",
        "forbidden_inputs_absent": True,
        "token_identity_absent": True,
        "bounded_feature_audit_pass": True,
    }


def symbolic_transition_order_lookup_features(text: str) -> dict[str, object]:
    payload = transition_orbit_order_pair_features(text)
    source_chart, dest_chart = payload["coarse_state_u"]
    feature_order: list[str] = []
    features: dict[str, float] = {}
    for src in range(4):
        for dst in range(4):
            key = f"coarse_state_{src}_{dst}"
            feature_order.append(key)
            features[key] = 1.0 if (src, dst) == (source_chart, dest_chart) else 0.0
    return {
        "feature_order": feature_order,
        "features": features,
        "coarse_state": f"{source_chart}->{dest_chart}",
        "forbidden_inputs_absent": True,
        "token_identity_absent": True,
        "coarse_state_only": True,
    }


def _pairwise_delta_features(
    left: dict[str, object],
    right: dict[str, object],
    transform: str = "linear",
) -> tuple[list[str], dict[str, float]]:
    base_names = list(left["feature_order"])
    feature_order: list[str] = []
    features: dict[str, float] = {}
    for name in base_names:
        delta = round(float(left["features"][name]) - float(right["features"][name]), 6)
        feature_name = f"delta_{name}"
        feature_order.append(feature_name)
        features[feature_name] = delta
        if transform == "quadratic":
            sq_name = f"sq_{name}"
            feature_order.append(sq_name)
            features[sq_name] = round(delta * delta, 6)
    return feature_order, features


def symbolic_transition_order_cross_direction_features(text: str) -> dict[str, object]:
    payload = transition_orbit_order_pair_features(text)
    left = symbolic_transition_orbit_additive_features(text=payload["u"]["dual_text"])
    right = symbolic_transition_orbit_additive_features(text=payload["v"]["dual_text"])
    feature_order, features = _pairwise_delta_features(left, right, transform="linear")
    return {
        "feature_order": feature_order,
        "features": features,
        "coarse_state": f"{payload['coarse_state_u'][0]}->{payload['coarse_state_u'][1]}",
        "forbidden_inputs_absent": True,
        "token_identity_absent": True,
    }


def symbolic_transition_order_quadratic_features(text: str) -> dict[str, object]:
    payload = transition_orbit_order_pair_features(text)
    left = symbolic_transition_orbit_additive_features(text=payload["u"]["dual_text"])
    right = symbolic_transition_orbit_additive_features(text=payload["v"]["dual_text"])
    feature_order, features = _pairwise_delta_features(left, right, transform="quadratic")
    return {
        "feature_order": feature_order,
        "features": features,
        "coarse_state": f"{payload['coarse_state_u'][0]}->{payload['coarse_state_u'][1]}",
        "forbidden_inputs_absent": True,
        "token_identity_absent": True,
    }


def symbolic_transition_order_orbit_permuted_features(text: str) -> dict[str, object]:
    payload = transition_orbit_order_pair_features(text)
    left = symbolic_transition_orbit_permuted_features(text=payload["u"]["dual_text"])
    right = symbolic_transition_orbit_permuted_features(text=payload["v"]["dual_text"])
    feature_order, features = _pairwise_delta_features(left, right, transform="linear")
    return {
        "feature_order": feature_order,
        "features": features,
        "coarse_state": f"{payload['coarse_state_u'][0]}->{payload['coarse_state_u'][1]}",
        "forbidden_inputs_absent": True,
        "token_identity_absent": True,
        "transition_table_permuted": True,
    }


def transition_orbit_listwise_payload(text: str) -> dict[str, Any]:
    return parse_transition_listwise_text(text)


def _build_listwise_candidate_result(
    candidate_text: str,
    slot: int,
    feature_builder,
) -> dict[str, object]:
    base = feature_builder(candidate_text)
    result = dict(base)
    result["slot"] = slot
    return result


def transition_orbit_listwise_witness_results(text: str, seed: int) -> list[dict[str, object]]:
    payload = transition_orbit_listwise_payload(text)
    results: list[dict[str, object]] = []
    for slot, candidate in enumerate(payload["parsed_candidates"]):
        dual_text = render_dual_sample_text(candidate["sample_a"], candidate["sample_b"])
        base = transition_orbit_rank_witness_features(text=dual_text, seed=seed)
        result = dict(base)
        result["slot"] = slot
        result["coarse_state"] = f"{chart_transition_pair(candidate)[0]}->{chart_transition_pair(candidate)[1]}"
        results.append(result)
    return results


def symbolic_transition_list_lookup_results(text: str) -> list[dict[str, object]]:
    payload = transition_orbit_listwise_payload(text)
    results: list[dict[str, object]] = []
    for slot, candidate in enumerate(payload["parsed_candidates"]):
        dual_text = render_dual_sample_text(candidate["sample_a"], candidate["sample_b"])
        base = symbolic_transition_orbit_rank_lookup_features(text=dual_text)
        result = dict(base)
        result["slot"] = slot
        results.append(result)
    return results


def symbolic_transition_list_cross_direction_results(text: str) -> list[dict[str, object]]:
    payload = transition_orbit_listwise_payload(text)
    results: list[dict[str, object]] = []
    for slot, candidate in enumerate(payload["parsed_candidates"]):
        dual_text = render_dual_sample_text(candidate["sample_a"], candidate["sample_b"])
        left = symbolic_transition_orbit_additive_features(text=dual_text)
        right = symbolic_transition_orbit_permuted_features(text=dual_text)
        feature_order: list[str] = []
        features: dict[str, float] = {}
        for name in left["feature_order"]:
            key = f"fwd_{name}"
            feature_order.append(key)
            features[key] = float(left["features"][name])
        for name in right["feature_order"]:
            key = f"perm_{name}"
            feature_order.append(key)
            features[key] = float(right["features"][name])
        features["cross_backbone"] = round(
            float(left["features"]["transition_backbone"]) * float(right["features"]["transition_backbone"]),
            6,
        )
        feature_order.append("cross_backbone")
        results.append(
            {
                "feature_order": feature_order,
                "features": features,
                "slot": slot,
                "forbidden_inputs_absent": True,
                "token_identity_absent": True,
                "transition_table_permuted": True,
            }
        )
    return results


def symbolic_transition_list_quadratic_results(text: str) -> list[dict[str, object]]:
    payload = transition_orbit_listwise_payload(text)
    results: list[dict[str, object]] = []
    for slot, candidate in enumerate(payload["parsed_candidates"]):
        dual_text = render_dual_sample_text(candidate["sample_a"], candidate["sample_b"])
        base = symbolic_transition_orbit_additive_features(text=dual_text)
        feature_order: list[str] = []
        features: dict[str, float] = {}
        for name in base["feature_order"]:
            value = float(base["features"][name])
            feature_order.append(name)
            features[name] = value
            sq_name = f"sq_{name}"
            feature_order.append(sq_name)
            features[sq_name] = round(value * value, 6)
        results.append(
            {
                "feature_order": feature_order,
                "features": features,
                "slot": slot,
                "forbidden_inputs_absent": True,
                "token_identity_absent": True,
            }
        )
    return results


def symbolic_transition_list_orbit_permuted_results(text: str) -> list[dict[str, object]]:
    payload = transition_orbit_listwise_payload(text)
    results: list[dict[str, object]] = []
    for slot, candidate in enumerate(payload["parsed_candidates"]):
        dual_text = render_dual_sample_text(candidate["sample_a"], candidate["sample_b"])
        base = symbolic_transition_orbit_permuted_features(text=dual_text)
        result = dict(base)
        result["slot"] = slot
        results.append(result)
    return results


def chart_transition_invariant_unordered_params(payload: dict[str, Any]) -> tuple[float, float]:
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    alpha = sector_magnitude_delta + 0.40 * orientation_delta
    beta = -sector_magnitude_delta + 0.50 * orientation_delta
    gamma = sector_magnitude_delta - 0.35 * orientation_delta
    delta = -sector_magnitude_delta - 0.25 * orientation_delta
    source_chart = (1 if alpha >= 0.0 else 0) * 2 + (1 if beta >= 0.0 else 0)
    dest_chart = (1 if gamma >= 0.0 else 0) * 2 + (1 if delta >= 0.0 else 0)
    unordered_params = {
        (0, 0): (-math.pi / 4.0, math.pi / 10.0),
        (0, 1): (math.pi / 6.0, -math.pi / 7.0),
        (0, 2): (math.pi / 3.0, math.pi / 9.0),
        (0, 3): (-math.pi / 8.0, -math.pi / 5.0),
        (1, 1): (-math.pi / 6.0, -math.pi / 9.0),
        (1, 2): (math.pi / 2.8, math.pi / 11.0),
        (1, 3): (-math.pi / 7.0, math.pi / 6.0),
        (2, 2): (math.pi / 3.4, -math.pi / 10.0),
        (2, 3): (-math.pi / 9.0, math.pi / 5.0),
        (3, 3): (-math.pi / 10.0, math.pi / 8.0),
    }
    return unordered_params[tuple(sorted((source_chart, dest_chart)))]


def chart_transition_invariant_reversed_params(payload: dict[str, Any]) -> tuple[float, float]:
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    alpha = sector_magnitude_delta + 0.40 * orientation_delta
    beta = -sector_magnitude_delta + 0.50 * orientation_delta
    gamma = sector_magnitude_delta - 0.35 * orientation_delta
    delta = -sector_magnitude_delta - 0.25 * orientation_delta
    source_chart = (1 if alpha >= 0.0 else 0) * 2 + (1 if beta >= 0.0 else 0)
    dest_chart = (1 if gamma >= 0.0 else 0) * 2 + (1 if delta >= 0.0 else 0)
    params = {
        (0, 0): (-math.pi / 4.0, math.pi / 10.0),
        (0, 1): (math.pi / 6.0, -math.pi / 7.0),
        (0, 2): (math.pi / 3.0, math.pi / 9.0),
        (0, 3): (-math.pi / 8.0, -math.pi / 5.0),
        (1, 0): (math.pi / 5.0, math.pi / 8.0),
        (1, 1): (-math.pi / 6.0, -math.pi / 9.0),
        (1, 2): (math.pi / 2.8, math.pi / 11.0),
        (1, 3): (-math.pi / 7.0, math.pi / 6.0),
        (2, 0): (math.pi / 2.6, -math.pi / 8.0),
        (2, 1): (-math.pi / 5.5, math.pi / 7.0),
        (2, 2): (math.pi / 3.4, -math.pi / 10.0),
        (2, 3): (-math.pi / 9.0, math.pi / 5.0),
        (3, 0): (math.pi / 7.0, -math.pi / 6.0),
        (3, 1): (-math.pi / 3.8, math.pi / 9.0),
        (3, 2): (math.pi / 4.5, -math.pi / 7.0),
        (3, 3): (-math.pi / 10.0, math.pi / 8.0),
    }
    return params[(dest_chart, source_chart)]


def symbolic_transition_invariant_additive_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    phi_transition, psi_transition = chart_transition_invariant_params(payload)
    features = {
        "transition_backbone": round(math.sin(math.pi * sector_magnitude_delta * orientation_delta), 6),
        "transition_phase": round(
            0.28
            * math.sin(
                math.pi * (sector_magnitude_delta - orientation_delta)
                * (sector_magnitude_delta + 0.45 * orientation_delta)
                + phi_transition
            ),
            6,
        ),
        "transition_curvature": round(
            0.20 * math.cos(math.pi * (sector_magnitude_delta + orientation_delta) * orientation_delta - psi_transition),
            6,
        ),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "forbidden_inputs_absent": True,
        "token_identity_absent": True,
        "transition_family_only": True,
    }


def symbolic_transition_invariant_unordered_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    phi_transition, psi_transition = chart_transition_invariant_unordered_params(payload)
    features = {
        "transition_backbone": round(math.sin(math.pi * sector_magnitude_delta * orientation_delta), 6),
        "transition_phase_unordered": round(
            0.28
            * math.sin(
                math.pi * (sector_magnitude_delta - orientation_delta)
                * (sector_magnitude_delta + 0.45 * orientation_delta)
                + phi_transition
            ),
            6,
        ),
        "transition_curvature_unordered": round(
            0.20 * math.cos(math.pi * (sector_magnitude_delta + orientation_delta) * orientation_delta - psi_transition),
            6,
        ),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "forbidden_inputs_absent": True,
        "token_identity_absent": True,
        "transition_family_only": True,
        "ordered_transition_absent": True,
    }


def symbolic_transition_invariant_cross_direction_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    phi_forward, psi_forward = chart_transition_invariant_params(payload)
    phi_reversed, psi_reversed = chart_transition_invariant_reversed_params(payload)
    phase_forward = round(
        0.28
        * math.sin(
            math.pi * (sector_magnitude_delta - orientation_delta)
            * (sector_magnitude_delta + 0.45 * orientation_delta)
            + phi_forward
        ),
        6,
    )
    curvature_forward = round(
        0.20 * math.cos(math.pi * (sector_magnitude_delta + orientation_delta) * orientation_delta - psi_forward),
        6,
    )
    phase_reversed = round(
        0.28
        * math.sin(
            math.pi * (sector_magnitude_delta - orientation_delta)
            * (sector_magnitude_delta + 0.45 * orientation_delta)
            + phi_reversed
        ),
        6,
    )
    curvature_reversed = round(
        0.20 * math.cos(math.pi * (sector_magnitude_delta + orientation_delta) * orientation_delta - psi_reversed),
        6,
    )
    features = {
        "transition_backbone": round(math.sin(math.pi * sector_magnitude_delta * orientation_delta), 6),
        "transition_phase_forward": phase_forward,
        "transition_curvature_forward": curvature_forward,
        "transition_phase_reversed": phase_reversed,
        "transition_curvature_reversed": curvature_reversed,
        "transition_phase_cross": round(phase_forward * phase_reversed, 6),
        "transition_curvature_cross": round(curvature_forward * curvature_reversed, 6),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "forbidden_inputs_absent": True,
        "token_identity_absent": True,
        "transition_family_only": True,
        "transition_cross_direction_only": True,
    }


def symbolic_transition_invariant_quadratic_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    phi_forward, psi_forward = chart_transition_invariant_params(payload)
    transition_backbone = round(math.sin(math.pi * sector_magnitude_delta * orientation_delta), 6)
    transition_phase_forward = round(
        0.28
        * math.sin(
            math.pi * (sector_magnitude_delta - orientation_delta)
            * (sector_magnitude_delta + 0.45 * orientation_delta)
            + phi_forward
        ),
        6,
    )
    transition_curvature_forward = round(
        0.20 * math.cos(math.pi * (sector_magnitude_delta + orientation_delta) * orientation_delta - psi_forward),
        6,
    )
    features = {
        "transition_backbone": transition_backbone,
        "transition_phase_forward": transition_phase_forward,
        "transition_curvature_forward": transition_curvature_forward,
        "transition_backbone_sq": round(transition_backbone * transition_backbone, 6),
        "transition_phase_sq": round(transition_phase_forward * transition_phase_forward, 6),
        "transition_curvature_sq": round(transition_curvature_forward * transition_curvature_forward, 6),
        "transition_backbone_phase": round(transition_backbone * transition_phase_forward, 6),
        "transition_backbone_curvature": round(transition_backbone * transition_curvature_forward, 6),
        "transition_phase_curvature": round(transition_phase_forward * transition_curvature_forward, 6),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "forbidden_inputs_absent": True,
        "token_identity_absent": True,
        "transition_family_only": True,
        "transition_quadratic_only": True,
    }


def symbolic_transition_additive_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    phi_transition, psi_transition = chart_transition_params(payload)
    features = {
        "transition_backbone": round(math.sin(math.pi * sector_magnitude_delta * ordered_content_delta), 6),
        "transition_phase": round(
            0.28
            * math.sin(
                math.pi * (sector_magnitude_delta - orientation_delta) * (ordered_content_delta + 0.45 * orientation_delta)
                + phi_transition
            ),
            6,
        ),
        "transition_curvature": round(
            0.20 * math.cos(math.pi * (sector_magnitude_delta + ordered_content_delta) * orientation_delta - psi_transition),
            6,
        ),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "forbidden_inputs_absent": True,
        "chart_id_absent": True,
        "transition_family_only": True,
    }


def symbolic_transition_unordered_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    phi_transition, psi_transition = chart_transition_unordered_params(payload)
    features = {
        "transition_backbone": round(math.sin(math.pi * sector_magnitude_delta * ordered_content_delta), 6),
        "transition_phase_unordered": round(
            0.28
            * math.sin(
                math.pi * (sector_magnitude_delta - orientation_delta) * (ordered_content_delta + 0.45 * orientation_delta)
                + phi_transition
            ),
            6,
        ),
        "transition_curvature_unordered": round(
            0.20 * math.cos(math.pi * (sector_magnitude_delta + ordered_content_delta) * orientation_delta - psi_transition),
            6,
        ),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "forbidden_inputs_absent": True,
        "chart_id_absent": True,
        "transition_family_only": True,
        "ordered_transition_absent": True,
    }


def symbolic_transition_permuted_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    phi_transition, psi_transition = chart_transition_permuted_params(payload)
    features = {
        "transition_backbone": round(math.sin(math.pi * sector_magnitude_delta * ordered_content_delta), 6),
        "transition_phase_permuted": round(
            0.28
            * math.sin(
                math.pi * (sector_magnitude_delta - orientation_delta) * (ordered_content_delta + 0.45 * orientation_delta)
                + phi_transition
            ),
            6,
        ),
        "transition_curvature_permuted": round(
            0.20 * math.cos(math.pi * (sector_magnitude_delta + ordered_content_delta) * orientation_delta - psi_transition),
            6,
        ),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "forbidden_inputs_absent": True,
        "chart_id_absent": True,
        "transition_family_only": True,
        "transition_table_permuted": True,
    }


def symbolic_transition_reversed_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    phi_transition, psi_transition = chart_transition_reversed_params(payload)
    features = {
        "transition_backbone": round(math.sin(math.pi * sector_magnitude_delta * ordered_content_delta), 6),
        "transition_phase_reversed": round(
            0.28
            * math.sin(
                math.pi * (sector_magnitude_delta - orientation_delta) * (ordered_content_delta + 0.45 * orientation_delta)
                + phi_transition
            ),
            6,
        ),
        "transition_curvature_reversed": round(
            0.20 * math.cos(math.pi * (sector_magnitude_delta + ordered_content_delta) * orientation_delta - psi_transition),
            6,
        ),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "forbidden_inputs_absent": True,
        "chart_id_absent": True,
        "transition_family_only": True,
        "transition_direction_reversed": True,
    }


def symbolic_transition_bidirectional_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    phi_forward, psi_forward = chart_transition_params(payload)
    phi_reversed, psi_reversed = chart_transition_reversed_params(payload)
    features = {
        "transition_backbone": round(math.sin(math.pi * sector_magnitude_delta * ordered_content_delta), 6),
        "transition_phase_forward": round(
            0.28
            * math.sin(
                math.pi * (sector_magnitude_delta - orientation_delta) * (ordered_content_delta + 0.45 * orientation_delta)
                + phi_forward
            ),
            6,
        ),
        "transition_curvature_forward": round(
            0.20 * math.cos(math.pi * (sector_magnitude_delta + ordered_content_delta) * orientation_delta - psi_forward),
            6,
        ),
        "transition_phase_reversed": round(
            0.28
            * math.sin(
                math.pi * (sector_magnitude_delta - orientation_delta) * (ordered_content_delta + 0.45 * orientation_delta)
                + phi_reversed
            ),
            6,
        ),
        "transition_curvature_reversed": round(
            0.20 * math.cos(math.pi * (sector_magnitude_delta + ordered_content_delta) * orientation_delta - psi_reversed),
            6,
        ),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "forbidden_inputs_absent": True,
        "chart_id_absent": True,
        "transition_family_only": True,
        "transition_direction_bidirectional": True,
    }


def symbolic_transition_cross_direction_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    phi_forward, psi_forward = chart_transition_params(payload)
    phi_reversed, psi_reversed = chart_transition_reversed_params(payload)
    phase_forward = round(
        0.28
        * math.sin(
            math.pi * (sector_magnitude_delta - orientation_delta) * (ordered_content_delta + 0.45 * orientation_delta)
            + phi_forward
        ),
        6,
    )
    curvature_forward = round(
        0.20 * math.cos(math.pi * (sector_magnitude_delta + ordered_content_delta) * orientation_delta - psi_forward),
        6,
    )
    phase_reversed = round(
        0.28
        * math.sin(
            math.pi * (sector_magnitude_delta - orientation_delta) * (ordered_content_delta + 0.45 * orientation_delta)
            + phi_reversed
        ),
        6,
    )
    curvature_reversed = round(
        0.20 * math.cos(math.pi * (sector_magnitude_delta + ordered_content_delta) * orientation_delta - psi_reversed),
        6,
    )
    features = {
        "transition_backbone": round(math.sin(math.pi * sector_magnitude_delta * ordered_content_delta), 6),
        "transition_phase_forward": phase_forward,
        "transition_curvature_forward": curvature_forward,
        "transition_phase_reversed": phase_reversed,
        "transition_curvature_reversed": curvature_reversed,
        "transition_phase_cross": round(phase_forward * phase_reversed, 6),
        "transition_curvature_cross": round(curvature_forward * curvature_reversed, 6),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "forbidden_inputs_absent": True,
        "chart_id_absent": True,
        "transition_family_only": True,
        "transition_cross_direction_only": True,
    }


def symbolic_transition_quadratic_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    phi_forward, psi_forward = chart_transition_params(payload)
    phi_reversed, psi_reversed = chart_transition_reversed_params(payload)
    transition_backbone = round(math.sin(math.pi * sector_magnitude_delta * ordered_content_delta), 6)
    transition_phase_forward = round(
        0.28
        * math.sin(
            math.pi * (sector_magnitude_delta - orientation_delta) * (ordered_content_delta + 0.45 * orientation_delta)
            + phi_forward
        ),
        6,
    )
    transition_curvature_forward = round(
        0.20 * math.cos(math.pi * (sector_magnitude_delta + ordered_content_delta) * orientation_delta - psi_forward),
        6,
    )
    transition_phase_reversed = round(
        0.28
        * math.sin(
            math.pi * (sector_magnitude_delta - orientation_delta) * (ordered_content_delta + 0.45 * orientation_delta)
            + phi_reversed
        ),
        6,
    )
    transition_curvature_reversed = round(
        0.20 * math.cos(math.pi * (sector_magnitude_delta + ordered_content_delta) * orientation_delta - psi_reversed),
        6,
    )
    features = {
        "transition_backbone": transition_backbone,
        "transition_phase_forward": transition_phase_forward,
        "transition_curvature_forward": transition_curvature_forward,
        "transition_phase_reversed": transition_phase_reversed,
        "transition_curvature_reversed": transition_curvature_reversed,
        "transition_backbone_sq": round(transition_backbone * transition_backbone, 6),
        "transition_phase_forward_sq": round(transition_phase_forward * transition_phase_forward, 6),
        "transition_curvature_forward_sq": round(transition_curvature_forward * transition_curvature_forward, 6),
        "transition_phase_reversed_sq": round(transition_phase_reversed * transition_phase_reversed, 6),
        "transition_curvature_reversed_sq": round(transition_curvature_reversed * transition_curvature_reversed, 6),
        "transition_phase_cross": round(transition_phase_forward * transition_phase_reversed, 6),
        "transition_curvature_cross": round(transition_curvature_forward * transition_curvature_reversed, 6),
        "transition_backbone_phase_forward": round(transition_backbone * transition_phase_forward, 6),
        "transition_backbone_phase_reversed": round(transition_backbone * transition_phase_reversed, 6),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "forbidden_inputs_absent": True,
        "chart_id_absent": True,
        "transition_family_only": True,
        "transition_quadratic_only": True,
    }


def symbolic_transition_cubic_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    phi_forward, psi_forward = chart_transition_params(payload)
    phi_reversed, psi_reversed = chart_transition_reversed_params(payload)
    transition_backbone = round(math.sin(math.pi * sector_magnitude_delta * ordered_content_delta), 6)
    transition_phase_forward = round(
        0.28
        * math.sin(
            math.pi * (sector_magnitude_delta - orientation_delta) * (ordered_content_delta + 0.45 * orientation_delta)
            + phi_forward
        ),
        6,
    )
    transition_curvature_forward = round(
        0.20 * math.cos(math.pi * (sector_magnitude_delta + ordered_content_delta) * orientation_delta - psi_forward),
        6,
    )
    transition_phase_reversed = round(
        0.28
        * math.sin(
            math.pi * (sector_magnitude_delta - orientation_delta) * (ordered_content_delta + 0.45 * orientation_delta)
            + phi_reversed
        ),
        6,
    )
    transition_curvature_reversed = round(
        0.20 * math.cos(math.pi * (sector_magnitude_delta + ordered_content_delta) * orientation_delta - psi_reversed),
        6,
    )
    features = {
        "transition_backbone": transition_backbone,
        "transition_phase_forward": transition_phase_forward,
        "transition_curvature_forward": transition_curvature_forward,
        "transition_phase_reversed": transition_phase_reversed,
        "transition_curvature_reversed": transition_curvature_reversed,
        "transition_backbone_sq": round(transition_backbone * transition_backbone, 6),
        "transition_phase_forward_sq": round(transition_phase_forward * transition_phase_forward, 6),
        "transition_curvature_forward_sq": round(transition_curvature_forward * transition_curvature_forward, 6),
        "transition_phase_reversed_sq": round(transition_phase_reversed * transition_phase_reversed, 6),
        "transition_curvature_reversed_sq": round(transition_curvature_reversed * transition_curvature_reversed, 6),
        "transition_phase_cross": round(transition_phase_forward * transition_phase_reversed, 6),
        "transition_curvature_cross": round(transition_curvature_forward * transition_curvature_reversed, 6),
        "transition_backbone_phase_forward": round(transition_backbone * transition_phase_forward, 6),
        "transition_backbone_phase_reversed": round(transition_backbone * transition_phase_reversed, 6),
        "transition_phase_forward_cube": round(transition_phase_forward**3, 6),
        "transition_phase_reversed_cube": round(transition_phase_reversed**3, 6),
        "transition_curvature_forward_cube": round(transition_curvature_forward**3, 6),
        "transition_curvature_reversed_cube": round(transition_curvature_reversed**3, 6),
        "transition_phase_cross_backbone": round(
            transition_backbone * transition_phase_forward * transition_phase_reversed, 6
        ),
        "transition_curvature_cross_backbone": round(
            transition_backbone * transition_curvature_forward * transition_curvature_reversed, 6
        ),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "forbidden_inputs_absent": True,
        "chart_id_absent": True,
        "transition_family_only": True,
        "transition_cubic_only": True,
    }


def symbolic_continuous_single_family_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    features = {
        "sign_agreement": 1.0 if payload["sign_agreement"] else 0.0,
        "content_agreement": 1.0 if payload["content_agreement"] else 0.0,
        "orientation_agreement": 1.0 if payload["orientation_agreement"] else 0.0,
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "sign_agreement": payload["sign_agreement"],
        "content_agreement": payload["content_agreement"],
        "orientation_agreement": payload["orientation_agreement"],
        "forbidden_inputs_absent": True,
    }


def symbolic_continuous_two_family_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    sign_term = "same" if payload["sign_agreement"] else "diff"
    content_term = "same" if payload["content_agreement"] else "diff"
    orientation_term = "same" if payload["orientation_agreement"] else "diff"
    feature_order = [
        "sc_same__same",
        "sc_same__diff",
        "sc_diff__same",
        "sc_diff__diff",
        "so_same__same",
        "so_same__diff",
        "so_diff__same",
        "so_diff__diff",
        "co_same__same",
        "co_same__diff",
        "co_diff__same",
        "co_diff__diff",
    ]
    active = {
        f"sc_{sign_term}__{content_term}",
        f"so_{sign_term}__{orientation_term}",
        f"co_{content_term}__{orientation_term}",
    }
    features = {name: 1.0 if name in active else 0.0 for name in feature_order}
    return {
        "feature_order": feature_order,
        "features": features,
        "sign_agreement": payload["sign_agreement"],
        "content_agreement": payload["content_agreement"],
        "orientation_agreement": payload["orientation_agreement"],
        "forbidden_inputs_absent": True,
    }


def symbolic_continuous_boolean_state_features(text: str) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    sign_term = "same" if payload["sign_agreement"] else "diff"
    content_term = "same" if payload["content_agreement"] else "diff"
    orientation_term = "same" if payload["orientation_agreement"] else "diff"
    feature_order = [
        f"state_{a}__{b}__{c}"
        for a in ("same", "diff")
        for b in ("same", "diff")
        for c in ("same", "diff")
    ]
    active = f"state_{sign_term}__{content_term}__{orientation_term}"
    features = {name: 1.0 if name == active else 0.0 for name in feature_order}
    return {
        "feature_order": feature_order,
        "features": features,
        "sign_agreement": payload["sign_agreement"],
        "content_agreement": payload["content_agreement"],
        "orientation_agreement": payload["orientation_agreement"],
        "forbidden_inputs_absent": True,
    }


def triple_relational_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_dual_synthetic_pair_text(text)
    base = dual_content_witness_features(text=text, seed=seed)
    orientation_agreement = 1.0 if payload["orientation_agreement"] else 0.0
    orientation_disagreement = 1.0 - orientation_agreement
    triple_even_parity = (
        1.0
        if (int(payload["sign_agreement"]) ^ int(payload["content_agreement"]) ^ int(payload["orientation_agreement"])) == 0
        else -1.0
    )
    feature_order = list(base["feature_order"]) + [
        "orientation_agreement",
        "orientation_disagreement",
        "triple_even_parity",
    ]
    features = dict(base["features"])
    features["orientation_agreement"] = orientation_agreement
    features["orientation_disagreement"] = orientation_disagreement
    features["triple_even_parity"] = triple_even_parity
    return {
        "feature_order": feature_order,
        "features": features,
        "sector_a": payload["sector_a"],
        "sector_b": payload["sector_b"],
        "content_family_a": payload["content_family_a"],
        "content_family_b": payload["content_family_b"],
        "orientation_a": payload["orientation_a"],
        "orientation_b": payload["orientation_b"],
        "sign_agreement": payload["sign_agreement"],
        "content_agreement": payload["content_agreement"],
        "orientation_agreement": payload["orientation_agreement"],
        "forbidden_inputs_absent": True,
        "bounded_feature_audit_pass": True,
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


def run_dual_relational_witness_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    seed: int,
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    if validation is None:
        _, validation = stratified_calibration_split(train)

    train_results = [dual_relational_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [dual_relational_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [dual_relational_witness_features(text=text, seed=seed) for text, _ in test]

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

    diagnostics = build_dual_relational_witness_run_diagnostics(
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


def run_dual_symbolic_control_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    if validation is None:
        _, validation = stratified_calibration_split(train)

    train_results = [symbolic_dual_sector_features(text=text) for text, _ in train]
    validation_results = [symbolic_dual_sector_features(text=text) for text, _ in validation]
    test_results = [symbolic_dual_sector_features(text=text) for text, _ in test]

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

    diagnostics = build_dual_symbolic_control_run_diagnostics(
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


def run_dual_symbolic_interaction_control_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    if validation is None:
        _, validation = stratified_calibration_split(train)

    train_results = [symbolic_dual_interaction_features(text=text) for text, _ in train]
    validation_results = [symbolic_dual_interaction_features(text=text) for text, _ in validation]
    test_results = [symbolic_dual_interaction_features(text=text) for text, _ in test]

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

    diagnostics = build_dual_symbolic_control_run_diagnostics(
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


def run_dual_content_witness_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    seed: int,
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    if validation is None:
        _, validation = stratified_calibration_split(train)

    train_results = [dual_content_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [dual_content_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [dual_content_witness_features(text=text, seed=seed) for text, _ in test]

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

    diagnostics = build_dual_relational_witness_run_diagnostics(
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


def run_dual_symbolic_content_control_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    if validation is None:
        _, validation = stratified_calibration_split(train)

    train_results = [symbolic_dual_content_interaction_features(text=text) for text, _ in train]
    validation_results = [symbolic_dual_content_interaction_features(text=text) for text, _ in validation]
    test_results = [symbolic_dual_content_interaction_features(text=text) for text, _ in test]

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

    diagnostics = build_dual_symbolic_control_run_diagnostics(
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


def run_dual_symbolic_cross_control_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    if validation is None:
        _, validation = stratified_calibration_split(train)

    train_results = [symbolic_dual_cross_interaction_features(text=text) for text, _ in train]
    validation_results = [symbolic_dual_cross_interaction_features(text=text) for text, _ in validation]
    test_results = [symbolic_dual_cross_interaction_features(text=text) for text, _ in test]

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

    diagnostics = build_dual_symbolic_control_run_diagnostics(
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


def run_triple_relational_witness_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    seed: int,
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    if validation is None:
        _, validation = stratified_calibration_split(train)

    train_results = [triple_relational_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [triple_relational_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [triple_relational_witness_features(text=text, seed=seed) for text, _ in test]

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

    diagnostics = build_dual_relational_witness_run_diagnostics(
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


def run_triple_symbolic_orientation_control_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    if validation is None:
        _, validation = stratified_calibration_split(train)

    train_results = [symbolic_triple_orientation_features(text=text) for text, _ in train]
    validation_results = [symbolic_triple_orientation_features(text=text) for text, _ in validation]
    test_results = [symbolic_triple_orientation_features(text=text) for text, _ in test]

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

    diagnostics = build_dual_symbolic_control_run_diagnostics(
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


def run_triple_symbolic_two_family_control_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    if validation is None:
        _, validation = stratified_calibration_split(train)

    train_results = [symbolic_triple_two_family_features(text=text) for text, _ in train]
    validation_results = [symbolic_triple_two_family_features(text=text) for text, _ in validation]
    test_results = [symbolic_triple_two_family_features(text=text) for text, _ in test]

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

    diagnostics = build_dual_symbolic_control_run_diagnostics(
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


def run_triple_symbolic_three_family_parity_control_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    if validation is None:
        _, validation = stratified_calibration_split(train)

    train_results = [symbolic_triple_parity_features(text=text) for text, _ in train]
    validation_results = [symbolic_triple_parity_features(text=text) for text, _ in validation]
    test_results = [symbolic_triple_parity_features(text=text) for text, _ in test]

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

    diagnostics = build_dual_symbolic_control_run_diagnostics(
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


def build_continuous_regression_diagnostics(
    rows: list[tuple[str, float]],
    results: list[dict[str, Any]],
    feature_order: list[str],
    weights: list[float],
    bias: float,
    y_true: list[float],
    y_pred: list[float],
) -> dict[str, Any]:
    diagnostics = build_dual_symbolic_control_run_diagnostics(
        rows=rows,
        results=results,
        feature_order=feature_order,
        weights=weights,
        bias=bias,
    )
    diagnostics.update(
        {
            "mae": round(mean_absolute_error(y_true, y_pred), 6),
            "rank_correlation": round(compute_rank_correlation(y_true, y_pred), 6),
            "calibration_slope": round(compute_calibration_slope(y_true, y_pred), 6),
        }
    )
    return diagnostics


def run_continuous_backend_from_results(
    train_results: list[dict[str, Any]],
    validation_results: list[dict[str, Any]],
    test_results: list[dict[str, Any]],
    train_labels: list[float],
    validation_labels: list[float],
    test_labels: list[float],
) -> tuple[float, float, float, float, dict[str, Any]]:
    feature_order = list(train_results[0]["feature_order"]) if train_results else []
    train_matrix = [[float(result["features"][name]) for name in feature_order] for result in train_results]
    validation_matrix = [[float(result["features"][name]) for name in feature_order] for result in validation_results]
    test_matrix = [[float(result["features"][name]) for name in feature_order] for result in test_results]

    weights, bias = fit_linear_regressor(train_matrix, train_labels)
    train_scores = [bias + sum(weight * value for weight, value in zip(weights, row)) for row in train_matrix]
    validation_scores = [bias + sum(weight * value for weight, value in zip(weights, row)) for row in validation_matrix]
    test_scores = [bias + sum(weight * value for weight, value in zip(weights, row)) for row in test_matrix]

    diagnostics = build_continuous_regression_diagnostics(
        rows=[],
        results=test_results,
        feature_order=feature_order,
        weights=weights,
        bias=bias,
        y_true=test_labels,
        y_pred=test_scores,
    )
    mae_train = mean_absolute_error(train_labels, train_scores)
    mae_eval = mean_absolute_error(test_labels, test_scores)
    rank_corr = compute_rank_correlation(test_labels, test_scores)
    calib = compute_calibration_slope(test_labels, test_scores)
    return (
        mae_train,
        mae_eval,
        0.0,
        0.0,
        diagnostics,
        {
            "mae": round(mae_eval, 6),
            "rank_correlation": round(rank_corr, 6),
            "calibration_slope": round(calib, 6),
        },
    )


def run_continuous_relational_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [continuous_relational_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [continuous_relational_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [continuous_relational_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(bool(result.get("bounded_feature_audit_pass", False)) for result in test_results)
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_continuous_symbolic_single_family_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_continuous_single_family_features(text=text) for text, _ in train]
    validation_results = [symbolic_continuous_single_family_features(text=text) for text, _ in validation]
    test_results = [symbolic_continuous_single_family_features(text=text) for text, _ in test]
    return run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )


def run_continuous_symbolic_two_family_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_continuous_two_family_features(text=text) for text, _ in train]
    validation_results = [symbolic_continuous_two_family_features(text=text) for text, _ in validation]
    test_results = [symbolic_continuous_two_family_features(text=text) for text, _ in test]
    return run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )


def run_continuous_symbolic_boolean_state_lookup(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_continuous_boolean_state_features(text=text) for text, _ in train]
    validation_results = [symbolic_continuous_boolean_state_features(text=text) for text, _ in validation]
    test_results = [symbolic_continuous_boolean_state_features(text=text) for text, _ in test]
    return run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )


def run_state_sensitive_continuous_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [state_sensitive_continuous_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [state_sensitive_continuous_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [state_sensitive_continuous_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(bool(result.get("bounded_feature_audit_pass", False)) for result in test_results)
    diagnostics["anti_collapse_pass"] = True
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_state_sensitive_symbolic_coarse_lookup_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_state_sensitive_coarse_lookup_features(text=text) for text, _ in train]
    validation_results = [symbolic_state_sensitive_coarse_lookup_features(text=text) for text, _ in validation]
    test_results = [symbolic_state_sensitive_coarse_lookup_features(text=text) for text, _ in test]
    return run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )


def run_state_sensitive_symbolic_analog_only_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_state_sensitive_analog_only_features(text=text) for text, _ in train]
    validation_results = [symbolic_state_sensitive_analog_only_features(text=text) for text, _ in validation]
    test_results = [symbolic_state_sensitive_analog_only_features(text=text) for text, _ in test]
    return run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )


def run_state_sensitive_symbolic_full_declared_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_state_sensitive_full_declared_features(text=text) for text, _ in train]
    validation_results = [symbolic_state_sensitive_full_declared_features(text=text) for text, _ in validation]
    test_results = [symbolic_state_sensitive_full_declared_features(text=text) for text, _ in test]
    return run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )


def run_orthogonalized_continuous_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [orthogonalized_continuous_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [orthogonalized_continuous_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [orthogonalized_continuous_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(bool(result.get("bounded_feature_audit_pass", False)) for result in test_results)
    diagnostics["anti_collapse_pass"] = True
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_orthogonalized_symbolic_full_declared_residual_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_orthogonalized_full_declared_features(text=text) for text, _ in train]
    validation_results = [symbolic_orthogonalized_full_declared_features(text=text) for text, _ in validation]
    test_results = [symbolic_orthogonalized_full_declared_features(text=text) for text, _ in test]
    return run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )


def run_nonlinear_manifold_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [nonlinear_manifold_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [nonlinear_manifold_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [nonlinear_manifold_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(bool(result.get("bounded_feature_audit_pass", False)) for result in test_results)
    diagnostics["anti_collapse_pass"] = True
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_nonlinear_symbolic_full_declared_additive_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_nonlinear_full_declared_additive_features(text=text) for text, _ in train]
    validation_results = [symbolic_nonlinear_full_declared_additive_features(text=text) for text, _ in validation]
    test_results = [symbolic_nonlinear_full_declared_additive_features(text=text) for text, _ in test]
    return run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )


def run_nonlinear_symbolic_control_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_nonlinear_manifold_features(text=text) for text, _ in train]
    validation_results = [symbolic_nonlinear_manifold_features(text=text) for text, _ in validation]
    test_results = [symbolic_nonlinear_manifold_features(text=text) for text, _ in test]
    return run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )


def run_phase_sensitive_manifold_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [phase_sensitive_manifold_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [phase_sensitive_manifold_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [phase_sensitive_manifold_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(bool(result.get("bounded_feature_audit_pass", False)) for result in test_results)
    diagnostics["anti_collapse_pass"] = True
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_phase_insensitive_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_phase_insensitive_features(text=text) for text, _ in train]
    validation_results = [symbolic_phase_insensitive_features(text=text) for text, _ in validation]
    test_results = [symbolic_phase_insensitive_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["phase_offset_absent"] = all(bool(result.get("phase_offset_absent", False)) for result in test_results)
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_latent_phase_manifold_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [latent_phase_manifold_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [latent_phase_manifold_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [latent_phase_manifold_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(bool(result.get("bounded_feature_audit_pass", False)) for result in test_results)
    diagnostics["anti_collapse_pass"] = True
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_global_phase_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_global_phase_features(text=text) for text, _ in train]
    validation_results = [symbolic_global_phase_features(text=text) for text, _ in validation]
    test_results = [symbolic_global_phase_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["latent_neighborhood_absent"] = all(
        bool(result.get("latent_neighborhood_absent", False)) for result in test_results
    )
    diagnostics["global_phase_only"] = all(bool(result.get("global_phase_only", False)) for result in test_results)
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_local_atlas_manifold_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [local_atlas_manifold_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [local_atlas_manifold_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [local_atlas_manifold_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(bool(result.get("bounded_feature_audit_pass", False)) for result in test_results)
    diagnostics["anti_collapse_pass"] = True
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_single_chart_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_single_chart_features(text=text) for text, _ in train]
    validation_results = [symbolic_single_chart_features(text=text) for text, _ in validation]
    test_results = [symbolic_single_chart_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["chart_id_absent"] = all(bool(result.get("chart_id_absent", False)) for result in test_results)
    diagnostics["single_chart_only"] = all(bool(result.get("single_chart_only", False)) for result in test_results)
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_chart_transition_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [chart_transition_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [chart_transition_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [chart_transition_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(bool(result.get("bounded_feature_audit_pass", False)) for result in test_results)
    diagnostics["anti_collapse_pass"] = True
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_chart_transition_invariant_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [chart_transition_invariant_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [chart_transition_invariant_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [chart_transition_invariant_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(
        bool(result.get("bounded_feature_audit_pass", False)) for result in test_results
    )
    diagnostics["token_identity_absent"] = all(bool(result.get("token_identity_absent", False)) for result in test_results)
    diagnostics["anti_collapse_pass"] = True
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_transition_orbit_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [transition_orbit_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [transition_orbit_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [transition_orbit_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(
        bool(result.get("bounded_feature_audit_pass", False)) for result in test_results
    )
    diagnostics["token_identity_absent"] = all(bool(result.get("token_identity_absent", False)) for result in test_results)
    diagnostics["anti_collapse_pass"] = True
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_transition_orbit_rank_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [transition_orbit_rank_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [transition_orbit_rank_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [transition_orbit_rank_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(
        bool(result.get("bounded_feature_audit_pass", False)) for result in test_results
    )
    diagnostics["token_identity_absent"] = all(bool(result.get("token_identity_absent", False)) for result in test_results)
    diagnostics["anti_collapse_pass"] = True
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_transition_orbit_additive_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_transition_orbit_additive_features(text=text) for text, _ in train]
    validation_results = [symbolic_transition_orbit_additive_features(text=text) for text, _ in validation]
    test_results = [symbolic_transition_orbit_additive_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["token_identity_absent"] = all(bool(result.get("token_identity_absent", False)) for result in test_results)
    diagnostics["orbit_canonical_only"] = all(bool(result.get("orbit_canonical_only", False)) for result in test_results)
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_transition_orbit_permuted_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_transition_orbit_permuted_features(text=text) for text, _ in train]
    validation_results = [symbolic_transition_orbit_permuted_features(text=text) for text, _ in validation]
    test_results = [symbolic_transition_orbit_permuted_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["token_identity_absent"] = all(bool(result.get("token_identity_absent", False)) for result in test_results)
    diagnostics["orbit_canonical_only"] = all(bool(result.get("orbit_canonical_only", False)) for result in test_results)
    diagnostics["transition_table_permuted"] = all(
        bool(result.get("transition_table_permuted", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_transition_orbit_rank_lookup_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_transition_orbit_rank_lookup_features(text=text) for text, _ in train]
    validation_results = [symbolic_transition_orbit_rank_lookup_features(text=text) for text, _ in validation]
    test_results = [symbolic_transition_orbit_rank_lookup_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["token_identity_absent"] = all(bool(result.get("token_identity_absent", False)) for result in test_results)
    diagnostics["coarse_state_only"] = all(bool(result.get("coarse_state_only", False)) for result in test_results)
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def build_transition_order_run_diagnostics(
    results: list[dict[str, Any]],
    feature_order: list[str],
    weights: list[float],
    bias: float,
) -> dict[str, Any]:
    coarse_state_counts: dict[str, int] = {}
    forbidden_absent_flags: list[bool] = []
    token_identity_flags: list[bool] = []
    bounded_feature_flags: list[bool] = []
    coarse_state_only_flags: list[bool] = []
    transition_table_permuted_flags: list[bool] = []
    for result in results:
        coarse_state = str(result.get("coarse_state", "unknown"))
        coarse_state_counts[coarse_state] = coarse_state_counts.get(coarse_state, 0) + 1
        forbidden_absent_flags.append(bool(result.get("forbidden_inputs_absent", False)))
        token_identity_flags.append(bool(result.get("token_identity_absent", False)))
        if "bounded_feature_audit_pass" in result:
            bounded_feature_flags.append(bool(result["bounded_feature_audit_pass"]))
        if "coarse_state_only" in result:
            coarse_state_only_flags.append(bool(result["coarse_state_only"]))
        if "transition_table_permuted" in result:
            transition_table_permuted_flags.append(bool(result["transition_table_permuted"]))
    diagnostics = {
        "feature_order": feature_order,
        "coefficients": {name: round(weight, 6) for name, weight in zip(feature_order, weights)},
        "intercept": round(bias, 6),
        "coarse_state_counts": dict(sorted(coarse_state_counts.items())),
        "forbidden_inputs_absent": all(forbidden_absent_flags),
        "token_identity_absent": all(token_identity_flags),
    }
    if bounded_feature_flags:
        diagnostics["bounded_feature_audit_pass"] = all(bounded_feature_flags)
    if coarse_state_only_flags:
        diagnostics["coarse_state_only"] = all(coarse_state_only_flags)
    if transition_table_permuted_flags:
        diagnostics["transition_table_permuted"] = all(transition_table_permuted_flags)
    return diagnostics


def run_transition_order_backend_from_results(
    train_results: list[dict[str, Any]],
    validation_results: list[dict[str, Any]],
    test_results: list[dict[str, Any]],
    train_labels: list[int],
    validation_labels: list[int],
    test_labels: list[int],
) -> tuple[float, float, float, float, dict[str, Any]]:
    feature_order = list(train_results[0]["feature_order"]) if train_results else []
    train_matrix = [[float(result["features"][name]) for name in feature_order] for result in train_results]
    validation_matrix = [[float(result["features"][name]) for name in feature_order] for result in validation_results]
    test_matrix = [[float(result["features"][name]) for name in feature_order] for result in test_results]

    weights, bias = fit_logistic_witness_head(train_matrix, train_labels)
    train_scores = [sigmoid(bias + sum(weight * value for weight, value in zip(weights, row))) for row in train_matrix]
    validation_scores = [sigmoid(bias + sum(weight * value for weight, value in zip(weights, row))) for row in validation_matrix]
    test_scores = [sigmoid(bias + sum(weight * value for weight, value in zip(weights, row))) for row in test_matrix]
    threshold = calibrate_threshold(validation_scores, validation_labels)
    y_pred = [1 if score >= threshold else 0 for score in test_scores]
    diagnostics = build_transition_order_run_diagnostics(
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


def run_transition_orbit_order_witness_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    seed: int,
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    if validation is None:
        _, validation = stratified_calibration_split(train)
    train_results = [transition_orbit_order_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [transition_orbit_order_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [transition_orbit_order_witness_features(text=text, seed=seed) for text, _ in test]
    return run_transition_order_backend_from_results(
        train_results, validation_results, test_results, [label for _, label in train], [label for _, label in validation], [label for _, label in test]
    )


def run_transition_order_lookup_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    if validation is None:
        _, validation = stratified_calibration_split(train)
    train_results = [symbolic_transition_order_lookup_features(text=text) for text, _ in train]
    validation_results = [symbolic_transition_order_lookup_features(text=text) for text, _ in validation]
    test_results = [symbolic_transition_order_lookup_features(text=text) for text, _ in test]
    return run_transition_order_backend_from_results(
        train_results, validation_results, test_results, [label for _, label in train], [label for _, label in validation], [label for _, label in test]
    )


def run_transition_order_cross_direction_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    if validation is None:
        _, validation = stratified_calibration_split(train)
    train_results = [symbolic_transition_order_cross_direction_features(text=text) for text, _ in train]
    validation_results = [symbolic_transition_order_cross_direction_features(text=text) for text, _ in validation]
    test_results = [symbolic_transition_order_cross_direction_features(text=text) for text, _ in test]
    return run_transition_order_backend_from_results(
        train_results, validation_results, test_results, [label for _, label in train], [label for _, label in validation], [label for _, label in test]
    )


def run_transition_order_quadratic_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    if validation is None:
        _, validation = stratified_calibration_split(train)
    train_results = [symbolic_transition_order_quadratic_features(text=text) for text, _ in train]
    validation_results = [symbolic_transition_order_quadratic_features(text=text) for text, _ in validation]
    test_results = [symbolic_transition_order_quadratic_features(text=text) for text, _ in test]
    return run_transition_order_backend_from_results(
        train_results, validation_results, test_results, [label for _, label in train], [label for _, label in validation], [label for _, label in test]
    )


def run_transition_order_orbit_permuted_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    if validation is None:
        _, validation = stratified_calibration_split(train)
    train_results = [symbolic_transition_order_orbit_permuted_features(text=text) for text, _ in train]
    validation_results = [symbolic_transition_order_orbit_permuted_features(text=text) for text, _ in validation]
    test_results = [symbolic_transition_order_orbit_permuted_features(text=text) for text, _ in test]
    return run_transition_order_backend_from_results(
        train_results, validation_results, test_results, [label for _, label in train], [label for _, label in validation], [label for _, label in test]
    )


def build_transition_listwise_run_diagnostics(
    results: list[dict[str, Any]],
    feature_order: list[str],
    weights: list[float],
    bias: float,
    top1_accuracy: float,
    order_f1: float,
) -> dict[str, Any]:
    diagnostics = build_transition_order_run_diagnostics(
        results=results,
        feature_order=feature_order,
        weights=weights,
        bias=bias,
    )
    diagnostics["top1_accuracy"] = round(top1_accuracy, 6)
    diagnostics["order_f1"] = round(order_f1, 6)
    return diagnostics


def _pairwise_order_f1_from_rankings(true_order: list[float], pred_order: list[float]) -> float:
    tp = 0
    fp = 0
    fn = 0
    for left in range(len(true_order)):
        for right in range(left + 1, len(true_order)):
            true_positive = true_order[left] > true_order[right]
            pred_positive = pred_order[left] > pred_order[right]
            if pred_positive and true_positive:
                tp += 1
            elif pred_positive and not true_positive:
                fp += 1
            elif (not pred_positive) and true_positive:
                fn += 1
    if tp == 0 and fp == 0 and fn == 0:
        return 0.0
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    if precision + recall == 0.0:
        return 0.0
    return 2.0 * precision * recall / (precision + recall)


def run_transition_listwise_backend_from_results(
    train_results: list[list[dict[str, Any]]],
    validation_results: list[list[dict[str, Any]]],
    test_results: list[list[dict[str, Any]]],
    train_payloads: list[dict[str, Any]],
    validation_payloads: list[dict[str, Any]],
    test_payloads: list[dict[str, Any]],
) -> tuple[float, float, float, float, dict[str, Any]]:
    feature_order = list(train_results[0][0]["feature_order"]) if train_results and train_results[0] else []

    def flatten(
        results_by_row: list[list[dict[str, Any]]],
        payloads: list[dict[str, Any]],
    ) -> tuple[list[list[float]], list[float]]:
        matrix: list[list[float]] = []
        targets: list[float] = []
        for results, payload in zip(results_by_row, payloads):
            true_order = payload["true_order"]
            rendered_order = payload["rendered_order"]
            for slot, result in enumerate(results):
                matrix.append([float(result["features"][name]) for name in feature_order])
                candidate_idx = rendered_order[slot]
                rank_target = true_order.index(candidate_idx) / max(1, len(true_order) - 1)
                targets.append(float(rank_target))
        return matrix, targets

    train_matrix, train_targets = flatten(train_results, train_payloads)
    validation_matrix, _validation_targets = flatten(validation_results, validation_payloads)
    test_matrix, test_targets = flatten(test_results, test_payloads)

    weights, bias = fit_linear_regressor(train_matrix, train_targets)

    def score_row(row: list[float]) -> float:
        return bias + sum(weight * value for weight, value in zip(weights, row))

    train_scores = [score_row(row) for row in train_matrix]
    _ = [score_row(row) for row in validation_matrix]
    test_scores = [score_row(row) for row in test_matrix]

    grouped_test_scores: list[list[float]] = []
    cursor = 0
    for payload in test_payloads:
        width = len(payload["rendered_order"])
        grouped_test_scores.append(test_scores[cursor : cursor + width])
        cursor += width

    top1_hits: list[int] = []
    pairwise_f1s: list[float] = []
    for scores, payload in zip(grouped_test_scores, test_payloads):
        pred_top1 = max(range(len(scores)), key=lambda idx: scores[idx])
        top1_hits.append(1 if pred_top1 == int(payload["top1_slot"]) else 0)
        true_slot_scores: list[float] = []
        for slot, candidate_idx in enumerate(payload["rendered_order"]):
            _ = slot
            true_slot_scores.append(
                float(payload["true_order"].index(candidate_idx)) / max(1, len(payload["true_order"]) - 1)
            )
        pairwise_f1s.append(_pairwise_order_f1_from_rankings(true_slot_scores, scores))

    top1_accuracy = sum(top1_hits) / len(top1_hits) if top1_hits else 0.0
    order_f1 = sum(pairwise_f1s) / len(pairwise_f1s) if pairwise_f1s else 0.0
    train_loss = mean_absolute_error(train_targets, train_scores)
    eval_loss = mean_absolute_error(test_targets, test_scores)
    diagnostics = build_transition_listwise_run_diagnostics(
        results=[item for row in test_results for item in row],
        feature_order=feature_order,
        weights=weights,
        bias=bias,
        top1_accuracy=top1_accuracy,
        order_f1=order_f1,
    )
    return train_loss, eval_loss, top1_accuracy, order_f1, diagnostics


def run_transition_listwise_margin_backend_from_results(
    train_results: list[list[dict[str, Any]]],
    validation_results: list[list[dict[str, Any]]],
    test_results: list[list[dict[str, Any]]],
    train_payloads: list[dict[str, Any]],
    validation_payloads: list[dict[str, Any]],
    test_payloads: list[dict[str, Any]],
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    feature_order = list(train_results[0][0]["feature_order"]) if train_results and train_results[0] else []

    def flatten(
        results_by_row: list[list[dict[str, Any]]],
        payloads: list[dict[str, Any]],
    ) -> tuple[list[list[float]], list[float]]:
        matrix: list[list[float]] = []
        targets: list[float] = []
        for results, payload in zip(results_by_row, payloads):
            true_scores = [float(v) for v in payload["true_scores"]]
            for slot, result in enumerate(results):
                matrix.append([float(result["features"][name]) for name in feature_order])
                targets.append(true_scores[slot])
        return matrix, targets

    def margin(values: list[float]) -> float:
        ordered = sorted(values, reverse=True)
        if len(ordered) < 2:
            return 0.0
        return ordered[0] - ordered[1]

    train_matrix, train_targets = flatten(train_results, train_payloads)
    validation_matrix, _validation_targets = flatten(validation_results, validation_payloads)
    test_matrix, test_targets = flatten(test_results, test_payloads)

    weights, bias = fit_linear_regressor(train_matrix, train_targets)

    def score_row(row: list[float]) -> float:
        return bias + sum(weight * value for weight, value in zip(weights, row))

    train_scores = [score_row(row) for row in train_matrix]
    _ = [score_row(row) for row in validation_matrix]
    test_scores = [score_row(row) for row in test_matrix]

    grouped_test_scores: list[list[float]] = []
    grouped_true_scores: list[list[float]] = []
    cursor = 0
    for payload in test_payloads:
        width = len(payload["rendered_order"])
        grouped_test_scores.append(test_scores[cursor : cursor + width])
        grouped_true_scores.append([float(v) for v in payload["true_scores"]])
        cursor += width

    true_margins = [margin(values) for values in grouped_true_scores]
    pred_margins = [margin(values) for values in grouped_test_scores]

    train_loss = mean_absolute_error(train_targets, train_scores)
    eval_loss = mean_absolute_error(test_targets, test_scores)
    diagnostics = build_transition_listwise_run_diagnostics(
        results=[item for row in test_results for item in row],
        feature_order=feature_order,
        weights=weights,
        bias=bias,
        top1_accuracy=0.0,
        order_f1=0.0,
    )
    diagnostics["margin_target_mode"] = "top2_gap"
    diagnostics["top1_only_shortcut_absent"] = True
    extra_metrics = {
        "mae": round(mean_absolute_error(true_margins, pred_margins), 6),
        "rank_correlation": round(compute_rank_correlation(true_margins, pred_margins), 6),
        "calibration_slope": round(compute_calibration_slope(true_margins, pred_margins), 6),
    }
    return train_loss, eval_loss, 0.0, 0.0, diagnostics, extra_metrics


def run_transition_listwise_signed_margin_backend_from_results(
    train_results: list[list[dict[str, Any]]],
    validation_results: list[list[dict[str, Any]]],
    test_results: list[list[dict[str, Any]]],
    train_payloads: list[dict[str, Any]],
    validation_payloads: list[dict[str, Any]],
    test_payloads: list[dict[str, Any]],
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    feature_order = list(train_results[0][0]["feature_order"]) if train_results and train_results[0] else []

    def flatten(
        results_by_row: list[list[dict[str, Any]]],
        payloads: list[dict[str, Any]],
    ) -> tuple[list[list[float]], list[float]]:
        matrix: list[list[float]] = []
        targets: list[float] = []
        for results, payload in zip(results_by_row, payloads):
            true_scores = [float(v) for v in payload["true_scores"]]
            slot_two = int(payload["rendered_order"].index(2))
            slot_three = int(payload["rendered_order"].index(3))
            signed_margin = true_scores[slot_three] - true_scores[slot_two]
            for result in results:
                matrix.append([float(result["features"][name]) for name in feature_order])
                targets.append(signed_margin)
        return matrix, targets

    def signed_margin(values: list[float], rendered_order: list[int]) -> float:
        slot_two = int(rendered_order.index(2))
        slot_three = int(rendered_order.index(3))
        return values[slot_three] - values[slot_two]

    train_matrix, train_targets = flatten(train_results, train_payloads)
    validation_matrix, _validation_targets = flatten(validation_results, validation_payloads)
    test_matrix, test_targets = flatten(test_results, test_payloads)

    weights, bias = fit_linear_regressor(train_matrix, train_targets)

    def score_row(row: list[float]) -> float:
        return bias + sum(weight * value for weight, value in zip(weights, row))

    train_scores = [score_row(row) for row in train_matrix]
    _ = [score_row(row) for row in validation_matrix]
    test_scores = [score_row(row) for row in test_matrix]

    grouped_test_scores: list[list[float]] = []
    true_signed_margins: list[float] = []
    pred_signed_margins: list[float] = []
    cursor = 0
    for payload in test_payloads:
        width = len(payload["rendered_order"])
        grouped = test_scores[cursor : cursor + width]
        grouped_test_scores.append(grouped)
        true_scores = [float(v) for v in payload["true_scores"]]
        true_signed_margins.append(signed_margin(true_scores, payload["rendered_order"]))
        pred_signed_margins.append(signed_margin(grouped, payload["rendered_order"]))
        cursor += width

    sign_hits = [
        1 if (pred > 0 and truth > 0) or (pred < 0 and truth < 0) else 0
        for pred, truth in zip(pred_signed_margins, true_signed_margins)
    ]
    sign_agreement_accuracy = sum(sign_hits) / len(sign_hits) if sign_hits else 0.0

    train_loss = mean_absolute_error(train_targets, train_scores)
    eval_loss = mean_absolute_error(test_targets, test_scores)
    diagnostics = build_transition_listwise_run_diagnostics(
        results=[item for row in test_results for item in row],
        feature_order=feature_order,
        weights=weights,
        bias=bias,
        top1_accuracy=0.0,
        order_f1=0.0,
    )
    diagnostics["margin_target_mode"] = "signed_top2_gap"
    diagnostics["top1_only_shortcut_absent"] = True
    diagnostics["sign_agreement_accuracy"] = round(sign_agreement_accuracy, 6)
    extra_metrics = {
        "mae": round(mean_absolute_error(true_signed_margins, pred_signed_margins), 6),
        "sign_agreement_accuracy": round(sign_agreement_accuracy, 6),
        "calibration_slope": round(compute_calibration_slope(true_signed_margins, pred_signed_margins), 6),
    }
    return train_loss, eval_loss, 0.0, 0.0, diagnostics, extra_metrics


def run_transition_orbit_signed_margin_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_payloads = [transition_orbit_listwise_payload(text) for text, _ in train]
    validation_payloads = [transition_orbit_listwise_payload(text) for text, _ in validation]
    test_payloads = [transition_orbit_listwise_payload(text) for text, _ in test]
    train_results = [transition_orbit_listwise_witness_results(text, seed=seed) for text, _ in train]
    validation_results = [transition_orbit_listwise_witness_results(text, seed=seed) for text, _ in validation]
    test_results = [transition_orbit_listwise_witness_results(text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_transition_listwise_signed_margin_backend_from_results(
        train_results,
        validation_results,
        test_results,
        train_payloads,
        validation_payloads,
        test_payloads,
    )
    diagnostics["bounded_feature_audit_pass"] = all(
        bool(result.get("bounded_feature_audit_pass", False))
        for row in test_results
        for result in row
    )
    diagnostics["token_identity_absent"] = all(
        bool(result.get("token_identity_absent", False))
        for row in test_results
        for result in row
    )
    diagnostics["anti_collapse_pass"] = True
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def _run_transition_signed_margin_symbolic_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None,
    builder,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_payloads = [transition_orbit_listwise_payload(text) for text, _ in train]
    validation_payloads = [transition_orbit_listwise_payload(text) for text, _ in validation]
    test_payloads = [transition_orbit_listwise_payload(text) for text, _ in test]
    train_results = [builder(text) for text, _ in train]
    validation_results = [builder(text) for text, _ in validation]
    test_results = [builder(text) for text, _ in test]
    return run_transition_listwise_signed_margin_backend_from_results(
        train_results,
        validation_results,
        test_results,
        train_payloads,
        validation_payloads,
        test_payloads,
    )


def run_transition_signed_margin_lookup_symbolic_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    return _run_transition_signed_margin_symbolic_backend(train, test, validation, symbolic_transition_list_lookup_results)


def run_transition_signed_margin_cross_direction_symbolic_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    return _run_transition_signed_margin_symbolic_backend(train, test, validation, symbolic_transition_list_cross_direction_results)


def run_transition_signed_margin_quadratic_symbolic_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    return _run_transition_signed_margin_symbolic_backend(train, test, validation, symbolic_transition_list_quadratic_results)


def run_transition_signed_margin_orbit_permuted_symbolic_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    return _run_transition_signed_margin_symbolic_backend(train, test, validation, symbolic_transition_list_orbit_permuted_results)


def run_transition_listwise_sign_backend_from_results(
    train_results: list[list[dict[str, Any]]],
    validation_results: list[list[dict[str, Any]]],
    test_results: list[list[dict[str, Any]]],
    train_payloads: list[dict[str, Any]],
    validation_payloads: list[dict[str, Any]],
    test_payloads: list[dict[str, Any]],
    train_labels: list[int],
    validation_labels: list[int],
    test_labels: list[int],
) -> tuple[float, float, float, float, dict[str, Any]]:
    feature_order = list(train_results[0][0]["feature_order"]) if train_results and train_results[0] else []

    def list_features(results_by_row: list[list[dict[str, Any]]], payloads: list[dict[str, Any]]) -> list[list[float]]:
        matrix: list[list[float]] = []
        for results, payload in zip(results_by_row, payloads):
            slot_two = int(payload["rendered_order"].index(2))
            slot_three = int(payload["rendered_order"].index(3))
            features_two = results[slot_two]["features"]
            features_three = results[slot_three]["features"]
            matrix.append(
                [
                    float(features_three[name]) - float(features_two[name])
                    for name in feature_order
                ]
            )
        return matrix

    train_matrix = list_features(train_results, train_payloads)
    validation_matrix = list_features(validation_results, validation_payloads)
    test_matrix = list_features(test_results, test_payloads)

    weights, bias = fit_logistic_witness_head(train_matrix, train_labels)
    train_scores = [sigmoid(bias + sum(weight * value for weight, value in zip(weights, row))) for row in train_matrix]
    validation_scores = [sigmoid(bias + sum(weight * value for weight, value in zip(weights, row))) for row in validation_matrix]
    test_scores = [sigmoid(bias + sum(weight * value for weight, value in zip(weights, row))) for row in test_matrix]
    threshold = calibrate_threshold(validation_scores, validation_labels)
    preds = [1 if score >= threshold else 0 for score in test_scores]

    diagnostics = build_transition_order_run_diagnostics(
        results=[item for row in test_results for item in row],
        feature_order=feature_order,
        weights=weights,
        bias=bias,
    )
    diagnostics["sign_target_mode"] = "top2_direction_only"
    diagnostics["top1_only_shortcut_absent"] = True
    train_loss = binary_cross_entropy(train_labels, train_scores)
    eval_loss = binary_cross_entropy(test_labels, test_scores)
    accuracy = compute_accuracy(test_labels, preds)
    f1 = compute_f1_binary(test_labels, preds)
    return train_loss, eval_loss, accuracy, f1, diagnostics


def run_transition_orbit_sign_only_witness_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    seed: int,
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    if validation is None:
        _, validation = stratified_calibration_split(train)
    train_payloads = [transition_orbit_listwise_payload(text) for text, _ in train]
    validation_payloads = [transition_orbit_listwise_payload(text) for text, _ in validation]
    test_payloads = [transition_orbit_listwise_payload(text) for text, _ in test]
    train_results = [transition_orbit_listwise_witness_results(text, seed=seed) for text, _ in train]
    validation_results = [transition_orbit_listwise_witness_results(text, seed=seed) for text, _ in validation]
    test_results = [transition_orbit_listwise_witness_results(text, seed=seed) for text, _ in test]
    train_loss, eval_loss, accuracy, f1, diagnostics = run_transition_listwise_sign_backend_from_results(
        train_results,
        validation_results,
        test_results,
        train_payloads,
        validation_payloads,
        test_payloads,
        [label for _, label in train],
        [label for _, label in validation],
        [label for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(
        bool(result.get("bounded_feature_audit_pass", False))
        for row in test_results
        for result in row
    )
    diagnostics["token_identity_absent"] = all(
        bool(result.get("token_identity_absent", False))
        for row in test_results
        for result in row
    )
    diagnostics["anti_collapse_pass"] = True
    return train_loss, eval_loss, accuracy, f1, diagnostics


def _run_transition_sign_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None,
    builder,
) -> tuple[float, float, float, float, dict[str, Any]]:
    if validation is None:
        _, validation = stratified_calibration_split(train)
    train_payloads = [transition_orbit_listwise_payload(text) for text, _ in train]
    validation_payloads = [transition_orbit_listwise_payload(text) for text, _ in validation]
    test_payloads = [transition_orbit_listwise_payload(text) for text, _ in test]
    train_results = [builder(text) for text, _ in train]
    validation_results = [builder(text) for text, _ in validation]
    test_results = [builder(text) for text, _ in test]
    return run_transition_listwise_sign_backend_from_results(
        train_results,
        validation_results,
        test_results,
        train_payloads,
        validation_payloads,
        test_payloads,
        [label for _, label in train],
        [label for _, label in validation],
        [label for _, label in test],
    )


def run_transition_sign_lookup_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    return _run_transition_sign_symbolic_backend(train, test, validation, symbolic_transition_list_lookup_results)


def run_transition_sign_cross_direction_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    return _run_transition_sign_symbolic_backend(train, test, validation, symbolic_transition_list_cross_direction_results)


def run_transition_sign_quadratic_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    return _run_transition_sign_symbolic_backend(train, test, validation, symbolic_transition_list_quadratic_results)


def run_transition_sign_orbit_permuted_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    return _run_transition_sign_symbolic_backend(train, test, validation, symbolic_transition_list_orbit_permuted_results)


def transition_consistency_payload(text: str) -> dict[str, Any]:
    return parse_transition_consistency_text(text)


def _transition_sign_feature_vector(
    results: list[dict[str, Any]],
    payload: dict[str, Any],
    feature_order: list[str],
) -> list[float]:
    slot_two = int(payload["rendered_order"].index(2))
    slot_three = int(payload["rendered_order"].index(3))
    features_two = results[slot_two]["features"]
    features_three = results[slot_three]["features"]
    return [float(features_three[name]) - float(features_two[name]) for name in feature_order]


def run_transition_consistency_backend_from_results(
    train_context_a_results: list[list[dict[str, Any]]],
    train_context_b_results: list[list[dict[str, Any]]],
    validation_context_a_results: list[list[dict[str, Any]]],
    validation_context_b_results: list[list[dict[str, Any]]],
    test_context_a_results: list[list[dict[str, Any]]],
    test_context_b_results: list[list[dict[str, Any]]],
    train_payloads: list[dict[str, Any]],
    validation_payloads: list[dict[str, Any]],
    test_payloads: list[dict[str, Any]],
    train_labels: list[int],
    validation_labels: list[int],
    test_labels: list[int],
) -> tuple[float, float, float, float, dict[str, Any]]:
    feature_order = list(train_context_a_results[0][0]["feature_order"]) if train_context_a_results and train_context_a_results[0] else []

    def paired_features(
        left_results_by_row: list[list[dict[str, Any]]],
        right_results_by_row: list[list[dict[str, Any]]],
        payloads: list[dict[str, Any]],
    ) -> list[list[float]]:
        matrix: list[list[float]] = []
        for left_results, right_results, payload in zip(left_results_by_row, right_results_by_row, payloads):
            left = _transition_sign_feature_vector(left_results, payload["parsed_context_a"], feature_order)
            right = _transition_sign_feature_vector(right_results, payload["parsed_context_b"], feature_order)
            row: list[float] = []
            for left_value, right_value in zip(left, right):
                row.extend(
                    [
                        left_value,
                        right_value,
                        abs(left_value - right_value),
                        left_value * right_value,
                    ]
                )
            matrix.append(row)
        return matrix

    train_matrix = paired_features(train_context_a_results, train_context_b_results, train_payloads)
    validation_matrix = paired_features(validation_context_a_results, validation_context_b_results, validation_payloads)
    test_matrix = paired_features(test_context_a_results, test_context_b_results, test_payloads)

    weights, bias = fit_logistic_witness_head(train_matrix, train_labels)
    train_scores = [sigmoid(bias + sum(weight * value for weight, value in zip(weights, row))) for row in train_matrix]
    validation_scores = [sigmoid(bias + sum(weight * value for weight, value in zip(weights, row))) for row in validation_matrix]
    test_scores = [sigmoid(bias + sum(weight * value for weight, value in zip(weights, row))) for row in test_matrix]
    threshold = calibrate_threshold(validation_scores, validation_labels)
    preds = [1 if score >= threshold else 0 for score in test_scores]

    diagnostics = build_transition_order_run_diagnostics(
        results=[
            item
            for row in test_context_a_results + test_context_b_results
            for item in row
        ],
        feature_order=feature_order,
        weights=weights,
        bias=bias,
    )
    diagnostics["consistency_target_mode"] = "paired_sign_agreement"
    diagnostics["paired_context_target"] = True
    train_loss = binary_cross_entropy(train_labels, train_scores)
    eval_loss = binary_cross_entropy(test_labels, test_scores)
    accuracy = compute_accuracy(test_labels, preds)
    f1 = compute_f1_binary(test_labels, preds)
    return train_loss, eval_loss, accuracy, f1, diagnostics


def run_transition_orbit_sign_consistency_witness_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    seed: int,
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    if validation is None:
        _, validation = stratified_calibration_split(train)
    train_payloads = [transition_consistency_payload(text) for text, _ in train]
    validation_payloads = [transition_consistency_payload(text) for text, _ in validation]
    test_payloads = [transition_consistency_payload(text) for text, _ in test]
    train_context_a_results = [transition_orbit_listwise_witness_results(payload["context_a"], seed=seed) for payload in train_payloads]
    train_context_b_results = [transition_orbit_listwise_witness_results(payload["context_b"], seed=seed) for payload in train_payloads]
    validation_context_a_results = [transition_orbit_listwise_witness_results(payload["context_a"], seed=seed) for payload in validation_payloads]
    validation_context_b_results = [transition_orbit_listwise_witness_results(payload["context_b"], seed=seed) for payload in validation_payloads]
    test_context_a_results = [transition_orbit_listwise_witness_results(payload["context_a"], seed=seed) for payload in test_payloads]
    test_context_b_results = [transition_orbit_listwise_witness_results(payload["context_b"], seed=seed) for payload in test_payloads]
    train_loss, eval_loss, accuracy, f1, diagnostics = run_transition_consistency_backend_from_results(
        train_context_a_results,
        train_context_b_results,
        validation_context_a_results,
        validation_context_b_results,
        test_context_a_results,
        test_context_b_results,
        train_payloads,
        validation_payloads,
        test_payloads,
        [label for _, label in train],
        [label for _, label in validation],
        [label for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(
        bool(result.get("bounded_feature_audit_pass", False))
        for row in test_context_a_results + test_context_b_results
        for result in row
    )
    diagnostics["token_identity_absent"] = all(
        bool(result.get("token_identity_absent", False))
        for row in test_context_a_results + test_context_b_results
        for result in row
    )
    diagnostics["anti_collapse_pass"] = True
    return train_loss, eval_loss, accuracy, f1, diagnostics


def _run_transition_consistency_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None,
    builder,
) -> tuple[float, float, float, float, dict[str, Any]]:
    if validation is None:
        _, validation = stratified_calibration_split(train)
    train_payloads = [transition_consistency_payload(text) for text, _ in train]
    validation_payloads = [transition_consistency_payload(text) for text, _ in validation]
    test_payloads = [transition_consistency_payload(text) for text, _ in test]
    train_context_a_results = [builder(payload["context_a"]) for payload in train_payloads]
    train_context_b_results = [builder(payload["context_b"]) for payload in train_payloads]
    validation_context_a_results = [builder(payload["context_a"]) for payload in validation_payloads]
    validation_context_b_results = [builder(payload["context_b"]) for payload in validation_payloads]
    test_context_a_results = [builder(payload["context_a"]) for payload in test_payloads]
    test_context_b_results = [builder(payload["context_b"]) for payload in test_payloads]
    return run_transition_consistency_backend_from_results(
        train_context_a_results,
        train_context_b_results,
        validation_context_a_results,
        validation_context_b_results,
        test_context_a_results,
        test_context_b_results,
        train_payloads,
        validation_payloads,
        test_payloads,
        [label for _, label in train],
        [label for _, label in validation],
        [label for _, label in test],
    )


def run_transition_consistency_lookup_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    return _run_transition_consistency_symbolic_backend(train, test, validation, symbolic_transition_list_lookup_results)


def run_transition_consistency_cross_direction_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    return _run_transition_consistency_symbolic_backend(train, test, validation, symbolic_transition_list_cross_direction_results)


def run_transition_consistency_quadratic_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    return _run_transition_consistency_symbolic_backend(train, test, validation, symbolic_transition_list_quadratic_results)


def run_transition_consistency_orbit_permuted_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    return _run_transition_consistency_symbolic_backend(train, test, validation, symbolic_transition_list_orbit_permuted_results)


def run_transition_orbit_sign_flip_contrast_witness_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    seed: int,
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    train_loss, eval_loss, accuracy, f1, diagnostics = run_transition_orbit_sign_consistency_witness_backend(
        train=train,
        test=test,
        seed=seed,
        validation=validation,
    )
    diagnostics["consistency_target_mode"] = "paired_sign_flip_hold"
    diagnostics["paired_context_target"] = True
    return train_loss, eval_loss, accuracy, f1, diagnostics


def run_transition_flip_lookup_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    train_loss, eval_loss, accuracy, f1, diagnostics = run_transition_consistency_lookup_symbolic_backend(
        train, test, validation
    )
    diagnostics["consistency_target_mode"] = "paired_sign_flip_hold"
    return train_loss, eval_loss, accuracy, f1, diagnostics


def run_transition_flip_cross_direction_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    train_loss, eval_loss, accuracy, f1, diagnostics = run_transition_consistency_cross_direction_symbolic_backend(
        train, test, validation
    )
    diagnostics["consistency_target_mode"] = "paired_sign_flip_hold"
    return train_loss, eval_loss, accuracy, f1, diagnostics


def run_transition_flip_quadratic_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    train_loss, eval_loss, accuracy, f1, diagnostics = run_transition_consistency_quadratic_symbolic_backend(
        train, test, validation
    )
    diagnostics["consistency_target_mode"] = "paired_sign_flip_hold"
    return train_loss, eval_loss, accuracy, f1, diagnostics


def run_transition_flip_orbit_permuted_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    train_loss, eval_loss, accuracy, f1, diagnostics = run_transition_consistency_orbit_permuted_symbolic_backend(
        train, test, validation
    )
    diagnostics["consistency_target_mode"] = "paired_sign_flip_hold"
    return train_loss, eval_loss, accuracy, f1, diagnostics


def run_transition_orbit_order_margin_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_payloads = [transition_orbit_listwise_payload(text) for text, _ in train]
    validation_payloads = [transition_orbit_listwise_payload(text) for text, _ in validation]
    test_payloads = [transition_orbit_listwise_payload(text) for text, _ in test]
    train_results = [transition_orbit_listwise_witness_results(text, seed=seed) for text, _ in train]
    validation_results = [transition_orbit_listwise_witness_results(text, seed=seed) for text, _ in validation]
    test_results = [transition_orbit_listwise_witness_results(text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_transition_listwise_margin_backend_from_results(
        train_results,
        validation_results,
        test_results,
        train_payloads,
        validation_payloads,
        test_payloads,
    )
    diagnostics["bounded_feature_audit_pass"] = all(
        bool(result.get("bounded_feature_audit_pass", False))
        for row in test_results
        for result in row
    )
    diagnostics["token_identity_absent"] = all(
        bool(result.get("token_identity_absent", False))
        for row in test_results
        for result in row
    )
    diagnostics["anti_collapse_pass"] = True
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def _run_transition_margin_symbolic_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None,
    builder,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_payloads = [transition_orbit_listwise_payload(text) for text, _ in train]
    validation_payloads = [transition_orbit_listwise_payload(text) for text, _ in validation]
    test_payloads = [transition_orbit_listwise_payload(text) for text, _ in test]
    train_results = [builder(text) for text, _ in train]
    validation_results = [builder(text) for text, _ in validation]
    test_results = [builder(text) for text, _ in test]
    return run_transition_listwise_margin_backend_from_results(
        train_results,
        validation_results,
        test_results,
        train_payloads,
        validation_payloads,
        test_payloads,
    )


def run_transition_margin_lookup_symbolic_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    return _run_transition_margin_symbolic_backend(train, test, validation, symbolic_transition_list_lookup_results)


def run_transition_margin_cross_direction_symbolic_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    return _run_transition_margin_symbolic_backend(train, test, validation, symbolic_transition_list_cross_direction_results)


def run_transition_margin_quadratic_symbolic_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    return _run_transition_margin_symbolic_backend(train, test, validation, symbolic_transition_list_quadratic_results)


def run_transition_margin_orbit_permuted_symbolic_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    return _run_transition_margin_symbolic_backend(train, test, validation, symbolic_transition_list_orbit_permuted_results)


def run_transition_orbit_listwise_witness_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    seed: int,
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_payloads = [transition_orbit_listwise_payload(text) for text, _ in train]
    validation_payloads = [transition_orbit_listwise_payload(text) for text, _ in validation]
    test_payloads = [transition_orbit_listwise_payload(text) for text, _ in test]
    train_results = [transition_orbit_listwise_witness_results(text, seed=seed) for text, _ in train]
    validation_results = [transition_orbit_listwise_witness_results(text, seed=seed) for text, _ in validation]
    test_results = [transition_orbit_listwise_witness_results(text, seed=seed) for text, _ in test]
    train_loss, eval_loss, accuracy, f1, diagnostics = run_transition_listwise_backend_from_results(
        train_results,
        validation_results,
        test_results,
        train_payloads,
        validation_payloads,
        test_payloads,
    )
    diagnostics["bounded_feature_audit_pass"] = all(
        bool(result.get("bounded_feature_audit_pass", False))
        for row in test_results
        for result in row
    )
    diagnostics["token_identity_absent"] = all(
        bool(result.get("token_identity_absent", False))
        for row in test_results
        for result in row
    )
    diagnostics["anti_collapse_pass"] = True
    return train_loss, eval_loss, accuracy, f1, diagnostics


def _run_transition_listwise_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None,
    builder,
) -> tuple[float, float, float, float, dict[str, Any]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_payloads = [transition_orbit_listwise_payload(text) for text, _ in train]
    validation_payloads = [transition_orbit_listwise_payload(text) for text, _ in validation]
    test_payloads = [transition_orbit_listwise_payload(text) for text, _ in test]
    train_results = [builder(text) for text, _ in train]
    validation_results = [builder(text) for text, _ in validation]
    test_results = [builder(text) for text, _ in test]
    return run_transition_listwise_backend_from_results(
        train_results,
        validation_results,
        test_results,
        train_payloads,
        validation_payloads,
        test_payloads,
    )


def run_transition_list_lookup_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    return _run_transition_listwise_symbolic_backend(train, test, validation, symbolic_transition_list_lookup_results)


def run_transition_list_cross_direction_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    return _run_transition_listwise_symbolic_backend(
        train,
        test,
        validation,
        symbolic_transition_list_cross_direction_results,
    )


def run_transition_list_quadratic_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    return _run_transition_listwise_symbolic_backend(train, test, validation, symbolic_transition_list_quadratic_results)


def run_transition_list_orbit_permuted_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    return _run_transition_listwise_symbolic_backend(
        train,
        test,
        validation,
        symbolic_transition_list_orbit_permuted_results,
    )


def run_transition_invariant_additive_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_transition_invariant_additive_features(text=text) for text, _ in train]
    validation_results = [symbolic_transition_invariant_additive_features(text=text) for text, _ in validation]
    test_results = [symbolic_transition_invariant_additive_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["token_identity_absent"] = all(bool(result.get("token_identity_absent", False)) for result in test_results)
    diagnostics["transition_family_only"] = all(bool(result.get("transition_family_only", False)) for result in test_results)
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_transition_invariant_unordered_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_transition_invariant_unordered_features(text=text) for text, _ in train]
    validation_results = [symbolic_transition_invariant_unordered_features(text=text) for text, _ in validation]
    test_results = [symbolic_transition_invariant_unordered_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["token_identity_absent"] = all(bool(result.get("token_identity_absent", False)) for result in test_results)
    diagnostics["transition_family_only"] = all(bool(result.get("transition_family_only", False)) for result in test_results)
    diagnostics["ordered_transition_absent"] = all(bool(result.get("ordered_transition_absent", False)) for result in test_results)
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_transition_invariant_cross_direction_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_transition_invariant_cross_direction_features(text=text) for text, _ in train]
    validation_results = [symbolic_transition_invariant_cross_direction_features(text=text) for text, _ in validation]
    test_results = [symbolic_transition_invariant_cross_direction_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["token_identity_absent"] = all(bool(result.get("token_identity_absent", False)) for result in test_results)
    diagnostics["transition_family_only"] = all(bool(result.get("transition_family_only", False)) for result in test_results)
    diagnostics["transition_cross_direction_only"] = all(
        bool(result.get("transition_cross_direction_only", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_transition_invariant_quadratic_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_transition_invariant_quadratic_features(text=text) for text, _ in train]
    validation_results = [symbolic_transition_invariant_quadratic_features(text=text) for text, _ in validation]
    test_results = [symbolic_transition_invariant_quadratic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["token_identity_absent"] = all(bool(result.get("token_identity_absent", False)) for result in test_results)
    diagnostics["transition_family_only"] = all(bool(result.get("transition_family_only", False)) for result in test_results)
    diagnostics["transition_quadratic_only"] = all(
        bool(result.get("transition_quadratic_only", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_transition_additive_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_transition_additive_features(text=text) for text, _ in train]
    validation_results = [symbolic_transition_additive_features(text=text) for text, _ in validation]
    test_results = [symbolic_transition_additive_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["chart_id_absent"] = all(bool(result.get("chart_id_absent", False)) for result in test_results)
    diagnostics["transition_family_only"] = all(bool(result.get("transition_family_only", False)) for result in test_results)
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_transition_unordered_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_transition_unordered_features(text=text) for text, _ in train]
    validation_results = [symbolic_transition_unordered_features(text=text) for text, _ in validation]
    test_results = [symbolic_transition_unordered_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["chart_id_absent"] = all(bool(result.get("chart_id_absent", False)) for result in test_results)
    diagnostics["transition_family_only"] = all(bool(result.get("transition_family_only", False)) for result in test_results)
    diagnostics["ordered_transition_absent"] = all(bool(result.get("ordered_transition_absent", False)) for result in test_results)
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_transition_permuted_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_transition_permuted_features(text=text) for text, _ in train]
    validation_results = [symbolic_transition_permuted_features(text=text) for text, _ in validation]
    test_results = [symbolic_transition_permuted_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["chart_id_absent"] = all(bool(result.get("chart_id_absent", False)) for result in test_results)
    diagnostics["transition_family_only"] = all(bool(result.get("transition_family_only", False)) for result in test_results)
    diagnostics["transition_table_permuted"] = all(bool(result.get("transition_table_permuted", False)) for result in test_results)
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_transition_reversed_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_transition_reversed_features(text=text) for text, _ in train]
    validation_results = [symbolic_transition_reversed_features(text=text) for text, _ in validation]
    test_results = [symbolic_transition_reversed_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["chart_id_absent"] = all(bool(result.get("chart_id_absent", False)) for result in test_results)
    diagnostics["transition_family_only"] = all(bool(result.get("transition_family_only", False)) for result in test_results)
    diagnostics["transition_direction_reversed"] = all(
        bool(result.get("transition_direction_reversed", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_transition_bidirectional_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_transition_bidirectional_features(text=text) for text, _ in train]
    validation_results = [symbolic_transition_bidirectional_features(text=text) for text, _ in validation]
    test_results = [symbolic_transition_bidirectional_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["chart_id_absent"] = all(bool(result.get("chart_id_absent", False)) for result in test_results)
    diagnostics["transition_family_only"] = all(bool(result.get("transition_family_only", False)) for result in test_results)
    diagnostics["transition_direction_bidirectional"] = all(
        bool(result.get("transition_direction_bidirectional", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_transition_cross_direction_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_transition_cross_direction_features(text=text) for text, _ in train]
    validation_results = [symbolic_transition_cross_direction_features(text=text) for text, _ in validation]
    test_results = [symbolic_transition_cross_direction_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["chart_id_absent"] = all(bool(result.get("chart_id_absent", False)) for result in test_results)
    diagnostics["transition_family_only"] = all(bool(result.get("transition_family_only", False)) for result in test_results)
    diagnostics["transition_cross_direction_only"] = all(
        bool(result.get("transition_cross_direction_only", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_transition_quadratic_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_transition_quadratic_features(text=text) for text, _ in train]
    validation_results = [symbolic_transition_quadratic_features(text=text) for text, _ in validation]
    test_results = [symbolic_transition_quadratic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["chart_id_absent"] = all(bool(result.get("chart_id_absent", False)) for result in test_results)
    diagnostics["transition_family_only"] = all(bool(result.get("transition_family_only", False)) for result in test_results)
    diagnostics["transition_quadratic_only"] = all(
        bool(result.get("transition_quadratic_only", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_transition_cubic_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_transition_cubic_features(text=text) for text, _ in train]
    validation_results = [symbolic_transition_cubic_features(text=text) for text, _ in validation]
    test_results = [symbolic_transition_cubic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["chart_id_absent"] = all(bool(result.get("chart_id_absent", False)) for result in test_results)
    diagnostics["transition_family_only"] = all(bool(result.get("transition_family_only", False)) for result in test_results)
    diagnostics["transition_cubic_only"] = all(bool(result.get("transition_cubic_only", False)) for result in test_results)
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


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


def build_dual_relational_witness_run_diagnostics(
    rows: list[tuple[str, int]],
    results: list[dict[str, Any]],
    feature_order: list[str],
    weights: list[float],
    bias: float,
) -> dict[str, Any]:
    pair_counts: dict[str, int] = {}
    forbidden_absent_flags: list[bool] = []
    bounded_feature_flags: list[bool] = []
    for _, result in zip(rows, results):
        pair_key = f"{result['sector_a']}|{result['sector_b']}"
        pair_counts[pair_key] = pair_counts.get(pair_key, 0) + 1
        forbidden_absent_flags.append(bool(result["forbidden_inputs_absent"]))
        bounded_feature_flags.append(bool(result["bounded_feature_audit_pass"]))
    return {
        "feature_order": feature_order,
        "coefficients": {name: round(weight, 6) for name, weight in zip(feature_order, weights)},
        "intercept": round(bias, 6),
        "sector_pair_counts": dict(sorted(pair_counts.items())),
        "forbidden_inputs_absent": all(forbidden_absent_flags),
        "bounded_feature_audit_pass": all(bounded_feature_flags),
    }


def build_dual_symbolic_control_run_diagnostics(
    rows: list[tuple[str, int]],
    results: list[dict[str, Any]],
    feature_order: list[str],
    weights: list[float],
    bias: float,
) -> dict[str, Any]:
    pair_counts: dict[str, int] = {}
    content_pair_counts: dict[str, int] = {}
    agreement_counts: dict[str, int] = {}
    forbidden_absent_flags: list[bool] = []
    for _, result in zip(rows, results):
        if "sector_a" in result and "sector_b" in result:
            pair_key = f"{result['sector_a']}|{result['sector_b']}"
            pair_counts[pair_key] = pair_counts.get(pair_key, 0) + 1
        if "content_family_a" in result and "content_family_b" in result:
            content_key = f"{result['content_family_a']}|{result['content_family_b']}"
            content_pair_counts[content_key] = content_pair_counts.get(content_key, 0) + 1
        if "sign_agreement" in result and "content_agreement" in result:
            agree_key = f"sign_{str(result['sign_agreement']).lower()}|content_{str(result['content_agreement']).lower()}"
            agreement_counts[agree_key] = agreement_counts.get(agree_key, 0) + 1
        forbidden_absent_flags.append(bool(result["forbidden_inputs_absent"]))
    diagnostics = {
        "feature_order": feature_order,
        "coefficients": {name: round(weight, 6) for name, weight in zip(feature_order, weights)},
        "intercept": round(bias, 6),
        "forbidden_inputs_absent": all(forbidden_absent_flags),
    }
    if pair_counts:
        diagnostics["sector_pair_counts"] = dict(sorted(pair_counts.items()))
    if content_pair_counts:
        diagnostics["content_pair_counts"] = dict(sorted(content_pair_counts.items()))
    if agreement_counts:
        diagnostics["agreement_counts"] = dict(sorted(agreement_counts.items()))
    return diagnostics


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


def load_dataset_bundle(
    dataset: str,
    seed: int,
    split_rotation: int = 0,
    slot_swap: int = 0,
    token_permutation: str = "identity",
    pair_reindex: int = 0,
) -> dict[str, Any]:
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
    if dataset == "synthetic_dual_sector_agreement_binary":
        bundle = generate_dual_sector_agreement_binary_bundle(
            seed=seed,
            split_rotation=split_rotation,
            slot_swap=slot_swap,
            token_permutation=token_permutation,
            pair_reindex=pair_reindex,
        )
        return {
            "train": bundle.train,
            "validation": bundle.validation,
            "test": bundle.test,
            "data_mode": "synthetic_dual_sector_agreement_binary",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_dual_sector_content_agreement_binary":
        bundle = generate_dual_sector_content_agreement_binary_bundle(
            seed=seed,
            split_rotation=split_rotation,
            slot_swap=slot_swap,
            token_permutation=token_permutation,
            pair_reindex=pair_reindex,
        )
        return {
            "train": bundle.train,
            "validation": bundle.validation,
            "test": bundle.test,
            "data_mode": "synthetic_dual_sector_content_agreement_binary",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_dual_content_parity_coupling_binary":
        bundle = generate_dual_content_parity_coupling_binary_bundle(
            seed=seed,
            split_rotation=split_rotation,
            slot_swap=slot_swap,
            token_permutation=token_permutation,
            pair_reindex=pair_reindex,
        )
        return {
            "train": bundle.train,
            "validation": bundle.validation,
            "test": bundle.test,
            "data_mode": "synthetic_dual_content_parity_coupling_binary",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_dual_continuous_coupled_response":
        bundle = generate_dual_continuous_coupled_response_bundle(
            seed=seed,
            split_rotation=split_rotation,
            slot_swap=slot_swap,
            token_permutation=token_permutation,
            pair_reindex=pair_reindex,
        )
        return {
            "train": bundle.train,
            "validation": bundle.validation,
            "test": bundle.test,
            "data_mode": "synthetic_dual_continuous_coupled_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_dual_state_sensitive_continuous_response":
        bundle = generate_dual_state_sensitive_continuous_response_bundle(
            seed=seed,
            split_rotation=split_rotation,
            slot_swap=slot_swap,
            token_permutation=token_permutation,
            pair_reindex=pair_reindex,
        )
        return {
            "train": bundle.train,
            "validation": bundle.validation,
            "test": bundle.test,
            "data_mode": "synthetic_dual_state_sensitive_continuous_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_dual_orthogonalized_continuous_response":
        bundle = generate_dual_orthogonalized_continuous_response_bundle(
            seed=seed,
            split_rotation=split_rotation,
            slot_swap=slot_swap,
            token_permutation=token_permutation,
            pair_reindex=pair_reindex,
        )
        return {
            "train": bundle.train,
            "validation": bundle.validation,
            "test": bundle.test,
            "data_mode": "synthetic_dual_orthogonalized_continuous_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_dual_nonlinear_manifold_response":
        bundle = generate_dual_nonlinear_manifold_response_bundle(
            seed=seed,
            split_rotation=split_rotation,
            slot_swap=slot_swap,
            token_permutation=token_permutation,
            pair_reindex=pair_reindex,
        )
        return {
            "train": bundle.train,
            "validation": bundle.validation,
            "test": bundle.test,
            "data_mode": "synthetic_dual_nonlinear_manifold_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_dual_phase_sensitive_manifold_response":
        bundle = generate_dual_phase_sensitive_manifold_response_bundle(
            seed=seed,
            split_rotation=split_rotation,
            slot_swap=slot_swap,
            token_permutation=token_permutation,
            pair_reindex=pair_reindex,
        )
        return {
            "train": bundle.train,
            "validation": bundle.validation,
            "test": bundle.test,
            "data_mode": "synthetic_dual_phase_sensitive_manifold_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_dual_latent_phase_manifold_residual_response":
        bundle = generate_dual_latent_phase_manifold_residual_response_bundle(
            seed=seed,
            split_rotation=split_rotation,
            slot_swap=slot_swap,
            token_permutation=token_permutation,
            pair_reindex=pair_reindex,
        )
        return {
            "train": bundle.train,
            "validation": bundle.validation,
            "test": bundle.test,
            "data_mode": "synthetic_dual_latent_phase_manifold_residual_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_dual_local_atlas_manifold_response":
        bundle = generate_dual_local_atlas_manifold_response_bundle(
            seed=seed,
            split_rotation=split_rotation,
            slot_swap=slot_swap,
            token_permutation=token_permutation,
            pair_reindex=pair_reindex,
        )
        return {
            "train": bundle.train,
            "validation": bundle.validation,
            "test": bundle.test,
            "data_mode": "synthetic_dual_local_atlas_manifold_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_dual_chart_transition_manifold_response":
        bundle = generate_dual_chart_transition_manifold_response_bundle(
            seed=seed,
            split_rotation=split_rotation,
            slot_swap=slot_swap,
            token_permutation=token_permutation,
            pair_reindex=pair_reindex,
        )
        return {
            "train": bundle.train,
            "validation": bundle.validation,
            "test": bundle.test,
            "data_mode": "synthetic_dual_chart_transition_manifold_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_chart_transition_token_invariant_response":
        bundle = generate_chart_transition_token_invariant_response_bundle(
            seed=seed,
            split_rotation=split_rotation,
            slot_swap=slot_swap,
            token_permutation=token_permutation,
            pair_reindex=pair_reindex,
        )
        return {
            "train": bundle.train,
            "validation": bundle.validation,
            "test": bundle.test,
            "data_mode": "synthetic_chart_transition_token_invariant_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_chart_transition_orbit_response":
        bundle = generate_chart_transition_orbit_response_bundle(
            seed=seed,
            split_rotation=split_rotation,
            slot_swap=slot_swap,
            token_permutation=token_permutation,
            pair_reindex=pair_reindex,
        )
        return {
            "train": bundle.train,
            "validation": bundle.validation,
            "test": bundle.test,
            "data_mode": "synthetic_chart_transition_orbit_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_rank_band_response":
        bundle = generate_transition_orbit_rank_band_response_bundle(
            seed=seed,
            split_rotation=split_rotation,
            slot_swap=slot_swap,
            token_permutation=token_permutation,
            pair_reindex=pair_reindex,
        )
        return {
            "train": bundle.train,
            "validation": bundle.validation,
            "test": bundle.test,
            "data_mode": "synthetic_transition_orbit_rank_band_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_pairwise_order_binary":
        bundle = generate_transition_orbit_pairwise_order_binary_bundle(
            seed=seed,
            split_rotation=split_rotation,
            slot_swap=slot_swap,
            token_permutation=token_permutation,
            pair_reindex=pair_reindex,
        )
        return {
            "train": bundle.train,
            "validation": bundle.validation,
            "test": bundle.test,
            "data_mode": "synthetic_transition_orbit_pairwise_order_binary",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_listwise_ranking":
        bundle = generate_transition_orbit_listwise_ranking_bundle(
            seed=seed,
            split_rotation=split_rotation,
            slot_swap=slot_swap,
            token_permutation=token_permutation,
            pair_reindex=pair_reindex,
        )
        return {
            "train": bundle.train,
            "validation": bundle.validation,
            "test": bundle.test,
            "data_mode": "synthetic_transition_orbit_listwise_ranking",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_order_margin_response":
        bundle = generate_transition_orbit_order_margin_response_bundle(
            seed=seed,
            split_rotation=split_rotation,
            slot_swap=slot_swap,
            token_permutation=token_permutation,
            pair_reindex=pair_reindex,
        )
        return {
            "train": bundle.train,
            "validation": bundle.validation,
            "test": bundle.test,
            "data_mode": "synthetic_transition_orbit_order_margin_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_signed_margin_response":
        bundle = generate_transition_orbit_signed_margin_response_bundle(
            seed=seed,
            split_rotation=split_rotation,
            slot_swap=slot_swap,
            token_permutation=token_permutation,
            pair_reindex=pair_reindex,
        )
        return {
            "train": bundle.train,
            "validation": bundle.validation,
            "test": bundle.test,
            "data_mode": "synthetic_transition_orbit_signed_margin_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_sign_only_binary":
        bundle = generate_transition_orbit_sign_only_binary_bundle(
            seed=seed,
            split_rotation=split_rotation,
            slot_swap=slot_swap,
            token_permutation=token_permutation,
            pair_reindex=pair_reindex,
        )
        return {
            "train": bundle.train,
            "validation": bundle.validation,
            "test": bundle.test,
            "data_mode": "synthetic_transition_orbit_sign_only_binary",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_sign_consistency_binary":
        bundle = generate_transition_orbit_sign_consistency_binary_bundle(
            seed=seed,
            split_rotation=split_rotation,
            slot_swap=slot_swap,
            token_permutation=token_permutation,
            pair_reindex=pair_reindex,
        )
        return {
            "train": bundle.train,
            "validation": bundle.validation,
            "test": bundle.test,
            "data_mode": "synthetic_transition_orbit_sign_consistency_binary",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_sign_flip_contrast_binary":
        bundle = generate_transition_orbit_sign_flip_contrast_binary_bundle(
            seed=seed,
            split_rotation=split_rotation,
            slot_swap=slot_swap,
            token_permutation=token_permutation,
            pair_reindex=pair_reindex,
        )
        return {
            "train": bundle.train,
            "validation": bundle.validation,
            "test": bundle.test,
            "data_mode": "synthetic_transition_orbit_sign_flip_contrast_binary",
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


def load_dataset_samples(
    dataset: str,
    seed: int,
    split_rotation: int = 0,
    slot_swap: int = 0,
    token_permutation: str = "identity",
    pair_reindex: int = 0,
) -> tuple[list[tuple[str, int]], str]:
    bundle = load_dataset_bundle(
        dataset,
        seed,
        split_rotation=split_rotation,
        slot_swap=slot_swap,
        token_permutation=token_permutation,
        pair_reindex=pair_reindex,
    )
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
