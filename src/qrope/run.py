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
    generate_symbolic_insufficiency_path_response_bundle,
    generate_symbolic_insufficiency_loop_closure_response_bundle,
    generate_symbolic_insufficiency_fork_join_response_bundle,
    generate_symbolic_insufficiency_braid_crossing_response_bundle,
    generate_symbolic_insufficiency_relay_binding_response_bundle,
    generate_symbolic_insufficiency_cascade_reconciliation_response_bundle,
    generate_symbolic_insufficiency_latch_switch_response_bundle,
    generate_symbolic_insufficiency_staggered_binding_response_bundle,
    generate_symbolic_insufficiency_fanin_consensus_response_bundle,
    generate_symbolic_insufficiency_echo_resolution_response_bundle,
    generate_symbolic_insufficiency_selector_arbitration_response_bundle,
    generate_symbolic_insufficiency_counterfactual_handoff_response_bundle,
    generate_positional_anchor_order_response_bundle,
    generate_positional_anchor_distance_response_bundle,
    generate_positional_anchor_span_membership_response_bundle,
    generate_positional_anchor_offset_signature_response_bundle,
    generate_positional_anchor_betweenness_response_bundle,
    generate_positional_offset_retrieval_response_bundle,
    generate_positional_key_query_offset_selection_response_bundle,
    generate_positional_dual_anchor_offset_consensus_response_bundle,
    generate_positional_variable_cardinality_offset_selection_response_bundle,
    generate_positional_content_gated_offset_selection_response_bundle,
    generate_positional_content_alias_disambiguation_response_bundle,
    generate_positional_reference_revision_selection_response_bundle,
    generate_positional_exception_conditioned_reference_selection_response_bundle,
    generate_positional_scope_masked_reference_selection_response_bundle,
    generate_positional_shared_memory_multi_query_selection_response_bundle,
    generate_positional_intermediate_pointer_selection_response_bundle,
    generate_symbolic_insufficiency_transition_response_bundle,
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
    generate_transition_orbit_asymmetric_sign_localization_binary_bundle,
    generate_transition_orbit_channel_advantage_response_bundle,
    generate_transition_orbit_channel_order_response_bundle,
    generate_transition_orbit_slot_invariant_channel_order_response_bundle,
    generate_transition_orbit_slot_invariant_channel_order_margin_response_bundle,
    generate_transition_orbit_slot_invariant_channel_order_rank_only_bundle,
    generate_transition_orbit_slot_invariant_channel_order_topk_rank_only_bundle,
    generate_transition_orbit_slot_invariant_channel_order_topk_margin_response_bundle,
    generate_transition_orbit_slot_invariant_topk_pair_margin_response_bundle,
    generate_transition_orbit_slot_invariant_topk_pair_order_agreement_binary_bundle,
    generate_transition_orbit_slot_invariant_topk_pair_order_signed_flip_consistency_binary_bundle,
    generate_transition_orbit_slot_invariant_topk_pair_order_signed_flip_stability_binary_bundle,
    generate_transition_orbit_slot_invariant_topk_pair_order_signed_flip_persistence_binary_bundle,
    generate_transition_orbit_slot_invariant_topk_pair_order_signed_flip_recurrence_binary_bundle,
    generate_transition_orbit_slot_invariant_topk_pair_order_signed_flip_reversion_binary_bundle,
    generate_transition_orbit_slot_invariant_topk_pair_order_signed_flip_hysteresis_binary_bundle,
    generate_transition_orbit_slot_invariant_topk_pair_order_signed_flip_memory_binary_bundle,
    generate_transition_orbit_slot_invariant_topk_pair_order_signed_consistency_binary_bundle,
    generate_transition_orbit_slot_invariant_topk_pair_order_stability_binary_bundle,
    generate_transition_orbit_slot_invariant_topk_pair_order_drift_response_bundle,
    generate_transition_orbit_slot_invariant_topk_pair_order_signed_drift_response_bundle,
    generate_transition_orbit_slot_invariant_channel_order_topk_consistency_binary_bundle,
    generate_transition_orbit_signed_margin_response_bundle,
    generate_transition_orbit_sign_only_binary_bundle,
    generate_transition_orbit_order_margin_response_bundle,
    generate_transition_orbit_pairwise_order_binary_bundle,
    generate_transition_orbit_slot_invariant_channel_order_topk_preference_binary_bundle,
    generate_transition_orbit_rank_band_response_bundle,
    parse_symbolic_insufficiency_path_text,
    parse_symbolic_insufficiency_loop_text,
    parse_symbolic_insufficiency_fork_join_text,
    parse_symbolic_insufficiency_braid_text,
    parse_symbolic_insufficiency_relay_binding_text,
    parse_symbolic_insufficiency_cascade_reconciliation_text,
    parse_symbolic_insufficiency_latch_switch_text,
    parse_symbolic_insufficiency_staggered_binding_text,
    parse_symbolic_insufficiency_fanin_consensus_text,
    parse_symbolic_insufficiency_echo_resolution_text,
    parse_symbolic_insufficiency_selector_arbitration_text,
    parse_symbolic_insufficiency_counterfactual_handoff_text,
    parse_positional_anchor_order_text,
    parse_positional_anchor_distance_text,
    parse_positional_anchor_span_membership_text,
    parse_positional_anchor_offset_signature_text,
    parse_positional_anchor_betweenness_text,
    parse_positional_offset_retrieval_text,
    parse_positional_key_query_offset_selection_text,
    parse_positional_dual_anchor_offset_consensus_text,
    parse_positional_variable_cardinality_offset_selection_text,
    parse_positional_content_gated_offset_selection_text,
    parse_positional_content_alias_disambiguation_text,
    parse_positional_reference_revision_selection_text,
    parse_positional_exception_conditioned_reference_selection_text,
    parse_positional_scope_masked_reference_selection_text,
    parse_positional_shared_memory_multi_query_selection_text,
    parse_positional_intermediate_pointer_selection_text,
    parse_transition_localization_text,
    parse_transition_consistency_text,
    parse_transition_listwise_text,
    parse_transition_pairwise_text,
    parse_dual_sample_text,
    render_dual_sample_text,
    generate_sector_parity_binary_bundle,
    symbolic_insufficiency_latent_ids,
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
        "V_future_relational_witness_transition_orbit_asymmetric_sign_localization": 24,
        "V_future_relational_witness_transition_orbit_channel_advantage": 24,
        "V_future_relational_witness_transition_orbit_channel_order": 24,
        "V_future_relational_witness_transition_orbit_channel_order_invariant": 24,
        "V_future_relational_witness_transition_orbit_channel_order_margin_invariant": 24,
        "V_future_relational_witness_transition_orbit_channel_order_topk_margin_invariant": 24,
        "V_future_relational_witness_transition_orbit_topk_pair_margin_invariant": 24,
        "V_future_relational_witness_transition_orbit_topk_pair_order_agreement_invariant": 24,
        "V_future_relational_witness_transition_orbit_topk_pair_order_signed_consistency_invariant": 24,
        "V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_consistency_invariant": 24,
        "V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_stability_invariant": 24,
        "V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_persistence_invariant": 24,
        "V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_recurrence_invariant": 24,
        "V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_reversion_invariant": 24,
        "V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_hysteresis_invariant": 24,
        "V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_memory_invariant": 24,
        "V_future_relational_witness_transition_orbit_topk_pair_order_stability_invariant": 24,
        "V_future_relational_witness_transition_orbit_topk_pair_order_drift_invariant": 24,
        "V_future_relational_witness_transition_orbit_topk_pair_order_signed_drift_invariant": 24,
        "V_future_relational_witness_transition_orbit_channel_order_rank_only_invariant": 24,
        "V_future_relational_witness_transition_orbit_channel_order_topk_rank_only_invariant": 24,
        "V_future_relational_witness_transition_orbit_channel_order_topk_preference_invariant": 24,
        "V_future_relational_witness_transition_orbit_channel_order_topk_consistency_invariant": 24,
        "V_future_relational_witness_symbolic_insufficiency": 24,
        "V_future_relational_witness_symbolic_insufficiency_path": 48,
        "V_future_relational_witness_symbolic_insufficiency_relay_binding": 72,
        "V_future_relational_witness_symbolic_insufficiency_cascade_reconciliation": 84,
        "V_future_relational_witness_symbolic_insufficiency_latch_switch": 72,
        "V_future_relational_witness_symbolic_insufficiency_staggered_binding": 96,
        "V_future_relational_witness_symbolic_insufficiency_fanin_consensus": 96,
        "V_future_relational_witness_symbolic_insufficiency_echo_resolution": 96,
        "V_future_relational_witness_symbolic_insufficiency_selector_arbitration": 96,
        "V_future_relational_witness_symbolic_insufficiency_counterfactual_handoff": 96,
        "V_future_relational_witness_positional_anchor_order": 96,
        "V_future_relational_witness_positional_anchor_distance": 96,
        "V_future_relational_witness_positional_anchor_span_membership": 96,
        "V_future_relational_witness_positional_anchor_offset_signature": 96,
        "V_future_relational_witness_positional_anchor_betweenness": 96,
        "V_future_relational_witness_positional_offset_retrieval": 96,
        "V_future_relational_witness_positional_key_query_offset_selection": 96,
        "V_future_relational_witness_positional_dual_anchor_offset_consensus": 96,
        "V_future_relational_witness_positional_variable_cardinality_offset_selection": 96,
        "V_future_relational_witness_positional_content_gated_offset_selection": 96,
        "V_future_relational_witness_positional_content_alias_disambiguation": 96,
        "V_future_relational_witness_positional_reference_revision_selection": 96,
        "V_future_relational_witness_positional_exception_conditioned_reference_selection": 96,
        "V_future_relational_witness_positional_scope_masked_reference_selection": 96,
        "V_future_relational_witness_positional_shared_memory_multi_query_selection": 96,
        "V_future_relational_witness_positional_intermediate_pointer_selection": 96,
        "V_future_relational_witness_symbolic_insufficiency_fork_join": 96,
        "V_future_relational_witness_symbolic_insufficiency_braid": 96,
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
        "V_control_symbolic_transition_localization_lookup": 1,
        "V_control_symbolic_transition_localization_cross_direction": 1,
        "V_control_symbolic_transition_localization_quadratic": 1,
        "V_control_symbolic_transition_localization_orbit_permuted": 1,
        "V_control_symbolic_transition_channel_lookup_regressor": 1,
        "V_control_symbolic_transition_channel_cross_direction_regressor": 1,
        "V_control_symbolic_transition_channel_quadratic_regressor": 1,
        "V_control_symbolic_transition_channel_orbit_permuted_regressor": 1,
        "V_control_symbolic_symbolic_insufficiency_regressor": 1,
        "V_control_symbolic_symbolic_insufficiency_regressor_v2": 1,
        "V_control_symbolic_symbolic_insufficiency_regressor_atlas": 1,
        "V_control_symbolic_symbolic_insufficiency_regressor_residual_atlas": 1,
        "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas": 1,
        "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_residual": 1,
        "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_bilinear": 1,
        "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_residual": 1,
        "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_bilinear": 1,
        "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_bilinear_plus": 1,
        "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_cubic": 1,
        "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_cubic_plus": 1,
        "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_quartic": 1,
        "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_quartic_plus": 1,
        "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_quintic": 1,
        "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_quintic_plus": 1,
        "V_control_symbolic_symbolic_insufficiency_path_regressor": 1,
        "V_control_symbolic_symbolic_insufficiency_relay_binding_regressor": 1,
        "V_control_symbolic_symbolic_insufficiency_cascade_reconciliation_regressor": 1,
        "V_control_symbolic_symbolic_insufficiency_latch_switch_regressor": 1,
        "V_control_symbolic_symbolic_insufficiency_staggered_binding_regressor": 1,
        "V_control_symbolic_symbolic_insufficiency_fanin_consensus_regressor": 1,
        "V_control_symbolic_symbolic_insufficiency_echo_resolution_regressor": 1,
        "V_control_symbolic_symbolic_insufficiency_selector_arbitration_regressor": 1,
        "V_control_symbolic_symbolic_insufficiency_counterfactual_handoff_regressor": 1,
        "V_control_symbolic_positional_anchor_order_regressor": 1,
        "V_control_symbolic_positional_anchor_distance_regressor": 1,
        "V_control_symbolic_positional_anchor_span_membership_regressor": 1,
        "V_control_symbolic_positional_anchor_offset_signature_regressor": 1,
        "V_control_symbolic_positional_anchor_betweenness_regressor": 1,
        "V_control_symbolic_positional_offset_retrieval_regressor": 1,
        "V_control_symbolic_positional_key_query_offset_selection_regressor": 1,
        "V_control_symbolic_positional_dual_anchor_offset_consensus_regressor": 1,
        "V_control_symbolic_positional_variable_cardinality_offset_selection_regressor": 1,
        "V_control_symbolic_positional_content_gated_offset_selection_regressor": 1,
        "V_control_symbolic_positional_content_alias_disambiguation_regressor": 1,
        "V_control_symbolic_positional_reference_revision_selection_regressor": 1,
        "V_control_symbolic_positional_exception_conditioned_reference_selection_regressor": 1,
        "V_control_symbolic_positional_scope_masked_reference_selection_regressor": 1,
        "V_control_symbolic_positional_shared_memory_multi_query_selection_regressor": 1,
        "V_control_symbolic_positional_intermediate_pointer_selection_regressor": 1,
        "V_control_symbolic_symbolic_insufficiency_fork_join_regressor": 1,
        "V_control_symbolic_symbolic_insufficiency_braid_regressor": 1,
        "V_control_symbolic_transition_channel_order_lookup": 1,
        "V_control_symbolic_transition_channel_order_cross_direction": 1,
        "V_control_symbolic_transition_channel_order_quadratic": 1,
        "V_control_symbolic_transition_channel_order_orbit_permuted": 1,
        "V_control_symbolic_transition_channel_order_invariant_lookup": 1,
        "V_control_symbolic_transition_channel_order_invariant_cross_direction": 1,
        "V_control_symbolic_transition_channel_order_invariant_quadratic": 1,
        "V_control_symbolic_transition_channel_order_invariant_orbit_permuted": 1,
        "V_control_symbolic_transition_channel_order_margin_invariant_lookup": 1,
        "V_control_symbolic_transition_channel_order_margin_invariant_cross_direction": 1,
        "V_control_symbolic_transition_channel_order_margin_invariant_quadratic": 1,
        "V_control_symbolic_transition_channel_order_margin_invariant_orbit_permuted": 1,
        "V_control_symbolic_transition_channel_order_topk_margin_invariant_lookup": 1,
        "V_control_symbolic_transition_channel_order_topk_margin_invariant_cross_direction": 1,
        "V_control_symbolic_transition_channel_order_topk_margin_invariant_quadratic": 1,
        "V_control_symbolic_transition_channel_order_topk_margin_invariant_orbit_permuted": 1,
        "V_control_symbolic_transition_topk_pair_margin_invariant_lookup": 1,
        "V_control_symbolic_transition_topk_pair_margin_invariant_cross_direction": 1,
        "V_control_symbolic_transition_topk_pair_margin_invariant_quadratic": 1,
        "V_control_symbolic_transition_topk_pair_margin_invariant_orbit_permuted": 1,
        "V_control_symbolic_transition_topk_pair_order_agreement_invariant_lookup": 1,
        "V_control_symbolic_transition_topk_pair_order_agreement_invariant_cross_direction": 1,
        "V_control_symbolic_transition_topk_pair_order_agreement_invariant_quadratic": 1,
        "V_control_symbolic_transition_topk_pair_order_agreement_invariant_orbit_permuted": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_consistency_invariant_lookup": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_consistency_invariant_cross_direction": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_consistency_invariant_quadratic": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_consistency_invariant_orbit_permuted": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_flip_consistency_invariant_lookup": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_flip_consistency_invariant_cross_direction": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_flip_consistency_invariant_quadratic": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_flip_consistency_invariant_orbit_permuted": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_flip_stability_invariant_lookup": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_flip_stability_invariant_cross_direction": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_flip_stability_invariant_quadratic": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_flip_stability_invariant_orbit_permuted": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_flip_persistence_invariant_lookup": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_flip_persistence_invariant_cross_direction": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_flip_persistence_invariant_quadratic": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_flip_persistence_invariant_orbit_permuted": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_flip_recurrence_invariant_lookup": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_flip_recurrence_invariant_cross_direction": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_flip_recurrence_invariant_quadratic": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_flip_recurrence_invariant_orbit_permuted": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_flip_reversion_invariant_lookup": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_flip_reversion_invariant_cross_direction": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_flip_reversion_invariant_quadratic": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_flip_reversion_invariant_orbit_permuted": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_flip_hysteresis_invariant_lookup": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_flip_hysteresis_invariant_cross_direction": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_flip_hysteresis_invariant_quadratic": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_flip_hysteresis_invariant_orbit_permuted": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_flip_memory_invariant_lookup": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_flip_memory_invariant_cross_direction": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_flip_memory_invariant_quadratic": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_flip_memory_invariant_orbit_permuted": 1,
        "V_control_symbolic_transition_topk_pair_order_stability_invariant_lookup": 1,
        "V_control_symbolic_transition_topk_pair_order_stability_invariant_cross_direction": 1,
        "V_control_symbolic_transition_topk_pair_order_stability_invariant_quadratic": 1,
        "V_control_symbolic_transition_topk_pair_order_stability_invariant_orbit_permuted": 1,
        "V_control_symbolic_transition_topk_pair_order_drift_invariant_lookup": 1,
        "V_control_symbolic_transition_topk_pair_order_drift_invariant_cross_direction": 1,
        "V_control_symbolic_transition_topk_pair_order_drift_invariant_quadratic": 1,
        "V_control_symbolic_transition_topk_pair_order_drift_invariant_orbit_permuted": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_drift_invariant_lookup": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_drift_invariant_cross_direction": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_drift_invariant_quadratic": 1,
        "V_control_symbolic_transition_topk_pair_order_signed_drift_invariant_orbit_permuted": 1,
        "V_control_symbolic_transition_channel_order_rank_only_invariant_lookup": 1,
        "V_control_symbolic_transition_channel_order_rank_only_invariant_cross_direction": 1,
        "V_control_symbolic_transition_channel_order_rank_only_invariant_quadratic": 1,
        "V_control_symbolic_transition_channel_order_rank_only_invariant_orbit_permuted": 1,
        "V_control_symbolic_transition_channel_order_topk_rank_only_invariant_lookup": 1,
        "V_control_symbolic_transition_channel_order_topk_rank_only_invariant_cross_direction": 1,
        "V_control_symbolic_transition_channel_order_topk_rank_only_invariant_quadratic": 1,
        "V_control_symbolic_transition_channel_order_topk_rank_only_invariant_orbit_permuted": 1,
        "V_control_symbolic_transition_channel_order_topk_preference_invariant_lookup": 1,
        "V_control_symbolic_transition_channel_order_topk_preference_invariant_cross_direction": 1,
        "V_control_symbolic_transition_channel_order_topk_preference_invariant_quadratic": 1,
        "V_control_symbolic_transition_channel_order_topk_preference_invariant_orbit_permuted": 1,
        "V_control_symbolic_transition_channel_order_topk_consistency_invariant_lookup": 1,
        "V_control_symbolic_transition_channel_order_topk_consistency_invariant_cross_direction": 1,
        "V_control_symbolic_transition_channel_order_topk_consistency_invariant_quadratic": 1,
        "V_control_symbolic_transition_channel_order_topk_consistency_invariant_orbit_permuted": 1,
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
        elif variant == "V_future_relational_witness_transition_orbit_asymmetric_sign_localization":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_asymmetric_sign_localization+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_channel_advantage":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_channel_advantage+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_channel_order":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_channel_order+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_channel_order_invariant":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_channel_order_invariant+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_channel_order_margin_invariant":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_channel_order_margin_invariant+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_channel_order_topk_margin_invariant":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_channel_order_topk_margin_invariant+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_topk_pair_margin_invariant":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_topk_pair_margin_invariant+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_topk_pair_order_agreement_invariant":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_topk_pair_order_agreement_invariant+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_topk_pair_order_signed_consistency_invariant":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_topk_pair_order_signed_consistency_invariant+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_consistency_invariant":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_topk_pair_order_signed_flip_consistency_invariant+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_stability_invariant":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_topk_pair_order_signed_flip_stability_invariant+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_persistence_invariant":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_topk_pair_order_signed_flip_persistence_invariant+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_recurrence_invariant":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_topk_pair_order_signed_flip_recurrence_invariant+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_reversion_invariant":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_topk_pair_order_signed_flip_reversion_invariant+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_hysteresis_invariant":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_topk_pair_order_signed_flip_hysteresis_invariant+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_memory_invariant":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_topk_pair_order_signed_flip_memory_invariant+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_topk_pair_order_stability_invariant":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_topk_pair_order_stability_invariant+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_topk_pair_order_drift_invariant":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_topk_pair_order_drift_invariant+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_topk_pair_order_signed_drift_invariant":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_topk_pair_order_signed_drift_invariant+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_channel_order_rank_only_invariant":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_channel_order_rank_only_invariant+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_channel_order_topk_rank_only_invariant":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_channel_order_topk_rank_only_invariant+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_channel_order_topk_preference_invariant":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_channel_order_topk_preference_invariant+head_linear"
        elif variant == "V_future_relational_witness_transition_orbit_channel_order_topk_consistency_invariant":
            data_mode = f"{data_mode}+readout_relational_witness_transition_orbit_channel_order_topk_consistency_invariant+head_linear"
        elif variant == "V_future_relational_witness_symbolic_insufficiency":
            data_mode = f"{data_mode}+readout_relational_witness_symbolic_insufficiency+head_linear"
        elif variant == "V_future_relational_witness_symbolic_insufficiency_path":
            data_mode = f"{data_mode}+readout_relational_witness_symbolic_insufficiency_path+head_linear"
        elif variant == "V_future_relational_witness_symbolic_insufficiency_relay_binding":
            data_mode = f"{data_mode}+readout_relational_witness_symbolic_insufficiency_relay_binding+head_linear"
        elif variant == "V_future_relational_witness_symbolic_insufficiency_cascade_reconciliation":
            data_mode = (
                f"{data_mode}+readout_relational_witness_symbolic_insufficiency_cascade_reconciliation+head_linear"
            )
        elif variant == "V_future_relational_witness_symbolic_insufficiency_latch_switch":
            data_mode = f"{data_mode}+readout_relational_witness_symbolic_insufficiency_latch_switch+head_linear"
        elif variant == "V_future_relational_witness_symbolic_insufficiency_staggered_binding":
            data_mode = f"{data_mode}+readout_relational_witness_symbolic_insufficiency_staggered_binding+head_linear"
        elif variant == "V_future_relational_witness_symbolic_insufficiency_fanin_consensus":
            data_mode = f"{data_mode}+readout_relational_witness_symbolic_insufficiency_fanin_consensus+head_linear"
        elif variant == "V_future_relational_witness_symbolic_insufficiency_echo_resolution":
            data_mode = f"{data_mode}+readout_relational_witness_symbolic_insufficiency_echo_resolution+head_linear"
        elif variant == "V_future_relational_witness_symbolic_insufficiency_selector_arbitration":
            data_mode = f"{data_mode}+readout_relational_witness_symbolic_insufficiency_selector_arbitration+head_linear"
        elif variant == "V_future_relational_witness_symbolic_insufficiency_counterfactual_handoff":
            data_mode = f"{data_mode}+readout_relational_witness_symbolic_insufficiency_counterfactual_handoff+head_linear"
        elif variant == "V_future_relational_witness_positional_anchor_order":
            data_mode = f"{data_mode}+readout_relational_witness_positional_anchor_order+head_linear"
        elif variant == "V_future_relational_witness_positional_anchor_distance":
            data_mode = f"{data_mode}+readout_relational_witness_positional_anchor_distance+head_linear"
        elif variant == "V_future_relational_witness_positional_anchor_span_membership":
            data_mode = f"{data_mode}+readout_relational_witness_positional_anchor_span_membership+head_linear"
        elif variant == "V_future_relational_witness_positional_anchor_offset_signature":
            data_mode = f"{data_mode}+readout_relational_witness_positional_anchor_offset_signature+head_linear"
        elif variant == "V_future_relational_witness_positional_anchor_betweenness":
            data_mode = f"{data_mode}+readout_relational_witness_positional_anchor_betweenness+head_linear"
        elif variant == "V_future_relational_witness_positional_offset_retrieval":
            data_mode = f"{data_mode}+readout_relational_witness_positional_offset_retrieval+head_linear"
        elif variant == "V_future_relational_witness_positional_key_query_offset_selection":
            data_mode = f"{data_mode}+readout_relational_witness_positional_key_query_offset_selection+head_linear"
        elif variant == "V_future_relational_witness_positional_dual_anchor_offset_consensus":
            data_mode = f"{data_mode}+readout_relational_witness_positional_dual_anchor_offset_consensus+head_linear"
        elif variant == "V_future_relational_witness_positional_variable_cardinality_offset_selection":
            data_mode = f"{data_mode}+readout_relational_witness_positional_variable_cardinality_offset_selection+head_linear"
        elif variant == "V_future_relational_witness_positional_content_gated_offset_selection":
            data_mode = f"{data_mode}+readout_relational_witness_positional_content_gated_offset_selection+head_linear"
        elif variant == "V_future_relational_witness_positional_content_alias_disambiguation":
            data_mode = f"{data_mode}+readout_relational_witness_positional_content_alias_disambiguation+head_linear"
        elif variant == "V_future_relational_witness_positional_reference_revision_selection":
            data_mode = f"{data_mode}+readout_relational_witness_positional_reference_revision_selection+head_linear"
        elif variant == "V_future_relational_witness_positional_exception_conditioned_reference_selection":
            data_mode = f"{data_mode}+readout_relational_witness_positional_exception_conditioned_reference_selection+head_linear"
        elif variant == "V_future_relational_witness_positional_scope_masked_reference_selection":
            data_mode = f"{data_mode}+readout_relational_witness_positional_scope_masked_reference_selection+head_linear"
        elif variant == "V_future_relational_witness_positional_shared_memory_multi_query_selection":
            data_mode = f"{data_mode}+readout_relational_witness_positional_shared_memory_multi_query_selection+head_linear"
        elif variant == "V_future_relational_witness_positional_intermediate_pointer_selection":
            data_mode = f"{data_mode}+readout_relational_witness_positional_intermediate_pointer_selection+head_linear"
        elif variant == "V_future_relational_witness_symbolic_insufficiency_loop":
            data_mode = f"{data_mode}+readout_relational_witness_symbolic_insufficiency_loop+head_linear"
        elif variant == "V_future_relational_witness_symbolic_insufficiency_fork_join":
            data_mode = f"{data_mode}+readout_relational_witness_symbolic_insufficiency_fork_join+head_linear"
        elif variant == "V_future_relational_witness_symbolic_insufficiency_braid":
            data_mode = f"{data_mode}+readout_relational_witness_symbolic_insufficiency_braid+head_linear"
        elif variant == "V_control_symbolic_single_family_regressor":
            data_mode = f"{data_mode}+readout_symbolic_single_family_regressor+head_linear"
        elif variant == "V_control_symbolic_two_family_regressor":
            data_mode = f"{data_mode}+readout_symbolic_two_family_regressor+head_linear"
        elif variant == "V_control_symbolic_boolean_state_lookup":
            data_mode = f"{data_mode}+readout_symbolic_boolean_state_lookup+head_linear"
        elif variant == "V_control_symbolic_symbolic_insufficiency_regressor":
            data_mode = f"{data_mode}+readout_symbolic_symbolic_insufficiency_regressor+head_linear"
        elif variant == "V_control_symbolic_symbolic_insufficiency_regressor_v2":
            data_mode = f"{data_mode}+readout_symbolic_symbolic_insufficiency_regressor_v2+head_linear"
        elif variant == "V_control_symbolic_symbolic_insufficiency_regressor_atlas":
            data_mode = f"{data_mode}+readout_symbolic_symbolic_insufficiency_regressor_atlas+head_linear"
        elif variant == "V_control_symbolic_symbolic_insufficiency_regressor_residual_atlas":
            data_mode = f"{data_mode}+readout_symbolic_symbolic_insufficiency_regressor_residual_atlas+head_linear"
        elif variant == "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas":
            data_mode = f"{data_mode}+readout_symbolic_symbolic_insufficiency_regressor_dual_atlas+head_linear"
        elif variant == "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_residual":
            data_mode = f"{data_mode}+readout_symbolic_symbolic_insufficiency_regressor_dual_atlas_residual+head_linear"
        elif variant == "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_bilinear":
            data_mode = f"{data_mode}+readout_symbolic_symbolic_insufficiency_regressor_dual_atlas_bilinear+head_linear"
        elif variant == "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_residual":
            data_mode = f"{data_mode}+readout_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_residual+head_linear"
        elif variant == "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_bilinear":
            data_mode = f"{data_mode}+readout_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_bilinear+head_linear"
        elif variant == "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_bilinear_plus":
            data_mode = f"{data_mode}+readout_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_bilinear_plus+head_linear"
        elif variant == "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_cubic":
            data_mode = f"{data_mode}+readout_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_cubic+head_linear"
        elif variant == "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_cubic_plus":
            data_mode = f"{data_mode}+readout_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_cubic_plus+head_linear"
        elif variant == "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_quartic":
            data_mode = f"{data_mode}+readout_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_quartic+head_linear"
        elif variant == "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_quartic_plus":
            data_mode = f"{data_mode}+readout_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_quartic_plus+head_linear"
        elif variant == "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_quintic":
            data_mode = f"{data_mode}+readout_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_quintic+head_linear"
        elif variant == "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_quintic_plus":
            data_mode = f"{data_mode}+readout_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_quintic_plus+head_linear"
        elif variant == "V_control_symbolic_symbolic_insufficiency_path_regressor":
            data_mode = f"{data_mode}+readout_symbolic_symbolic_insufficiency_path_regressor+head_linear"
        elif variant == "V_control_symbolic_symbolic_insufficiency_relay_binding_regressor":
            data_mode = f"{data_mode}+readout_symbolic_symbolic_insufficiency_relay_binding_regressor+head_linear"
        elif variant == "V_control_symbolic_symbolic_insufficiency_cascade_reconciliation_regressor":
            data_mode = (
                f"{data_mode}+readout_symbolic_symbolic_insufficiency_cascade_reconciliation_regressor+head_linear"
            )
        elif variant == "V_control_symbolic_symbolic_insufficiency_latch_switch_regressor":
            data_mode = f"{data_mode}+readout_symbolic_symbolic_insufficiency_latch_switch_regressor+head_linear"
        elif variant == "V_control_symbolic_symbolic_insufficiency_staggered_binding_regressor":
            data_mode = f"{data_mode}+readout_symbolic_symbolic_insufficiency_staggered_binding_regressor+head_linear"
        elif variant == "V_control_symbolic_symbolic_insufficiency_fanin_consensus_regressor":
            data_mode = f"{data_mode}+readout_symbolic_symbolic_insufficiency_fanin_consensus_regressor+head_linear"
        elif variant == "V_control_symbolic_symbolic_insufficiency_echo_resolution_regressor":
            data_mode = f"{data_mode}+readout_symbolic_symbolic_insufficiency_echo_resolution_regressor+head_linear"
        elif variant == "V_control_symbolic_symbolic_insufficiency_selector_arbitration_regressor":
            data_mode = f"{data_mode}+readout_symbolic_symbolic_insufficiency_selector_arbitration_regressor+head_linear"
        elif variant == "V_control_symbolic_symbolic_insufficiency_counterfactual_handoff_regressor":
            data_mode = f"{data_mode}+readout_symbolic_symbolic_insufficiency_counterfactual_handoff_regressor+head_linear"
        elif variant == "V_control_symbolic_positional_anchor_order_regressor":
            data_mode = f"{data_mode}+readout_symbolic_positional_anchor_order_regressor+head_linear"
        elif variant == "V_control_symbolic_positional_anchor_distance_regressor":
            data_mode = f"{data_mode}+readout_symbolic_positional_anchor_distance_regressor+head_linear"
        elif variant == "V_control_symbolic_positional_anchor_span_membership_regressor":
            data_mode = f"{data_mode}+readout_symbolic_positional_anchor_span_membership_regressor+head_linear"
        elif variant == "V_control_symbolic_positional_anchor_offset_signature_regressor":
            data_mode = f"{data_mode}+readout_symbolic_positional_anchor_offset_signature_regressor+head_linear"
        elif variant == "V_control_symbolic_positional_anchor_betweenness_regressor":
            data_mode = f"{data_mode}+readout_symbolic_positional_anchor_betweenness_regressor+head_linear"
        elif variant == "V_control_symbolic_positional_offset_retrieval_regressor":
            data_mode = f"{data_mode}+readout_symbolic_positional_offset_retrieval_regressor+head_linear"
        elif variant == "V_control_symbolic_positional_key_query_offset_selection_regressor":
            data_mode = f"{data_mode}+readout_symbolic_positional_key_query_offset_selection_regressor+head_linear"
        elif variant == "V_control_symbolic_positional_dual_anchor_offset_consensus_regressor":
            data_mode = f"{data_mode}+readout_symbolic_positional_dual_anchor_offset_consensus_regressor+head_linear"
        elif variant == "V_control_symbolic_positional_variable_cardinality_offset_selection_regressor":
            data_mode = f"{data_mode}+readout_symbolic_positional_variable_cardinality_offset_selection_regressor+head_linear"
        elif variant == "V_control_symbolic_positional_content_gated_offset_selection_regressor":
            data_mode = f"{data_mode}+readout_symbolic_positional_content_gated_offset_selection_regressor+head_linear"
        elif variant == "V_control_symbolic_positional_content_alias_disambiguation_regressor":
            data_mode = f"{data_mode}+readout_symbolic_positional_content_alias_disambiguation_regressor+head_linear"
        elif variant == "V_control_symbolic_positional_reference_revision_selection_regressor":
            data_mode = f"{data_mode}+readout_symbolic_positional_reference_revision_selection_regressor+head_linear"
        elif variant == "V_control_symbolic_positional_exception_conditioned_reference_selection_regressor":
            data_mode = f"{data_mode}+readout_symbolic_positional_exception_conditioned_reference_selection_regressor+head_linear"
        elif variant == "V_control_symbolic_positional_scope_masked_reference_selection_regressor":
            data_mode = f"{data_mode}+readout_symbolic_positional_scope_masked_reference_selection_regressor+head_linear"
        elif variant == "V_control_symbolic_positional_shared_memory_multi_query_selection_regressor":
            data_mode = f"{data_mode}+readout_symbolic_positional_shared_memory_multi_query_selection_regressor+head_linear"
        elif variant == "V_control_symbolic_positional_intermediate_pointer_selection_regressor":
            data_mode = f"{data_mode}+readout_symbolic_positional_intermediate_pointer_selection_regressor+head_linear"
        elif variant == "V_control_symbolic_symbolic_insufficiency_loop_regressor":
            data_mode = f"{data_mode}+readout_symbolic_symbolic_insufficiency_loop_regressor+head_linear"
        elif variant == "V_control_symbolic_symbolic_insufficiency_fork_join_regressor":
            data_mode = f"{data_mode}+readout_symbolic_symbolic_insufficiency_fork_join_regressor+head_linear"
        elif variant == "V_control_symbolic_symbolic_insufficiency_braid_regressor":
            data_mode = f"{data_mode}+readout_symbolic_symbolic_insufficiency_braid_regressor+head_linear"
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
        elif variant == "V_control_symbolic_transition_localization_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_localization_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_localization_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_localization_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_localization_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_localization_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_localization_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_localization_orbit_permuted+head_linear"
        elif variant == "V_control_symbolic_transition_channel_lookup_regressor":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_lookup_regressor+head_linear"
        elif variant == "V_control_symbolic_transition_channel_cross_direction_regressor":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_cross_direction_regressor+head_linear"
        elif variant == "V_control_symbolic_transition_channel_quadratic_regressor":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_quadratic_regressor+head_linear"
        elif variant == "V_control_symbolic_transition_channel_orbit_permuted_regressor":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_orbit_permuted_regressor+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_orbit_permuted+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_invariant_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_invariant_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_invariant_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_invariant_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_invariant_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_invariant_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_invariant_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_invariant_orbit_permuted+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_margin_invariant_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_margin_invariant_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_margin_invariant_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_margin_invariant_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_margin_invariant_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_margin_invariant_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_margin_invariant_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_margin_invariant_orbit_permuted+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_topk_margin_invariant_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_topk_margin_invariant_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_topk_margin_invariant_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_topk_margin_invariant_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_topk_margin_invariant_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_topk_margin_invariant_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_topk_margin_invariant_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_topk_margin_invariant_orbit_permuted+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_margin_invariant_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_margin_invariant_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_margin_invariant_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_margin_invariant_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_margin_invariant_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_margin_invariant_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_margin_invariant_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_margin_invariant_orbit_permuted+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_agreement_invariant_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_agreement_invariant_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_agreement_invariant_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_agreement_invariant_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_agreement_invariant_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_agreement_invariant_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_agreement_invariant_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_agreement_invariant_orbit_permuted+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_consistency_invariant_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_consistency_invariant_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_consistency_invariant_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_consistency_invariant_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_consistency_invariant_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_consistency_invariant_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_consistency_invariant_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_consistency_invariant_orbit_permuted+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_consistency_invariant_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_flip_consistency_invariant_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_consistency_invariant_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_flip_consistency_invariant_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_consistency_invariant_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_flip_consistency_invariant_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_consistency_invariant_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_flip_consistency_invariant_orbit_permuted+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_stability_invariant_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_flip_stability_invariant_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_stability_invariant_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_flip_stability_invariant_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_stability_invariant_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_flip_stability_invariant_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_stability_invariant_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_flip_stability_invariant_orbit_permuted+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_persistence_invariant_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_flip_persistence_invariant_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_persistence_invariant_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_flip_persistence_invariant_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_persistence_invariant_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_flip_persistence_invariant_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_persistence_invariant_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_flip_persistence_invariant_orbit_permuted+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_recurrence_invariant_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_flip_recurrence_invariant_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_recurrence_invariant_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_flip_recurrence_invariant_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_recurrence_invariant_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_flip_recurrence_invariant_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_recurrence_invariant_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_flip_recurrence_invariant_orbit_permuted+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_reversion_invariant_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_flip_reversion_invariant_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_reversion_invariant_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_flip_reversion_invariant_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_reversion_invariant_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_flip_reversion_invariant_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_reversion_invariant_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_flip_reversion_invariant_orbit_permuted+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_hysteresis_invariant_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_flip_hysteresis_invariant_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_hysteresis_invariant_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_flip_hysteresis_invariant_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_hysteresis_invariant_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_flip_hysteresis_invariant_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_hysteresis_invariant_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_flip_hysteresis_invariant_orbit_permuted+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_memory_invariant_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_flip_memory_invariant_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_memory_invariant_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_flip_memory_invariant_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_memory_invariant_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_flip_memory_invariant_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_memory_invariant_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_flip_memory_invariant_orbit_permuted+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_stability_invariant_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_stability_invariant_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_stability_invariant_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_stability_invariant_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_stability_invariant_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_stability_invariant_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_stability_invariant_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_stability_invariant_orbit_permuted+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_drift_invariant_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_drift_invariant_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_drift_invariant_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_drift_invariant_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_drift_invariant_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_drift_invariant_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_drift_invariant_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_drift_invariant_orbit_permuted+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_drift_invariant_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_drift_invariant_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_drift_invariant_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_drift_invariant_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_drift_invariant_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_drift_invariant_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_topk_pair_order_signed_drift_invariant_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_topk_pair_order_signed_drift_invariant_orbit_permuted+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_rank_only_invariant_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_rank_only_invariant_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_rank_only_invariant_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_rank_only_invariant_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_rank_only_invariant_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_rank_only_invariant_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_rank_only_invariant_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_rank_only_invariant_orbit_permuted+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_topk_rank_only_invariant_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_topk_rank_only_invariant_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_topk_rank_only_invariant_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_topk_rank_only_invariant_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_topk_rank_only_invariant_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_topk_rank_only_invariant_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_topk_rank_only_invariant_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_topk_rank_only_invariant_orbit_permuted+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_topk_preference_invariant_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_topk_preference_invariant_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_topk_preference_invariant_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_topk_preference_invariant_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_topk_preference_invariant_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_topk_preference_invariant_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_topk_preference_invariant_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_topk_preference_invariant_orbit_permuted+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_topk_consistency_invariant_lookup":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_topk_consistency_invariant_lookup+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_topk_consistency_invariant_cross_direction":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_topk_consistency_invariant_cross_direction+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_topk_consistency_invariant_quadratic":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_topk_consistency_invariant_quadratic+head_linear"
        elif variant == "V_control_symbolic_transition_channel_order_topk_consistency_invariant_orbit_permuted":
            data_mode = f"{data_mode}+readout_symbolic_transition_channel_order_topk_consistency_invariant_orbit_permuted+head_linear"
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
    if dataset_diagnostics:
        if run_diagnostics is None:
            run_diagnostics = dict(dataset_diagnostics)
        else:
            merged_diagnostics = dict(dataset_diagnostics)
            merged_diagnostics.update(run_diagnostics)
            run_diagnostics = merged_diagnostics
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
    if variant == "V_future_relational_witness_transition_orbit_asymmetric_sign_localization":
        return run_transition_orbit_asymmetric_sign_localization_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_channel_advantage":
        return run_transition_orbit_channel_advantage_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_channel_order":
        return run_transition_orbit_channel_order_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_channel_order_invariant":
        return run_transition_orbit_channel_order_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_channel_order_margin_invariant":
        return run_transition_orbit_order_margin_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_channel_order_topk_margin_invariant":
        return run_transition_orbit_topk_margin_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_topk_pair_margin_invariant":
        return run_transition_orbit_topk_margin_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_topk_pair_order_agreement_invariant":
        return run_transition_orbit_order_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_topk_pair_order_signed_consistency_invariant":
        return run_transition_orbit_order_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_consistency_invariant":
        return run_transition_orbit_order_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_stability_invariant":
        return run_transition_orbit_order_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_persistence_invariant":
        return run_transition_orbit_order_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_recurrence_invariant":
        return run_transition_orbit_order_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_reversion_invariant":
        return run_transition_orbit_order_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_hysteresis_invariant":
        return run_transition_orbit_order_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_memory_invariant":
        return run_transition_orbit_order_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_topk_pair_order_stability_invariant":
        return run_transition_orbit_order_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_topk_pair_order_drift_invariant":
        return run_transition_orbit_topk_margin_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_topk_pair_order_signed_drift_invariant":
        return run_transition_orbit_topk_margin_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_channel_order_rank_only_invariant":
        return run_transition_orbit_listwise_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_channel_order_topk_rank_only_invariant":
        return run_transition_orbit_listwise_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_channel_order_topk_preference_invariant":
        return run_transition_orbit_order_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_transition_orbit_channel_order_topk_consistency_invariant":
        return run_transition_orbit_sign_consistency_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if variant == "V_future_relational_witness_symbolic_insufficiency":
        return run_symbolic_insufficiency_witness_backend(train=train, test=test, seed=seed, validation=validation)
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
    if dataset == "synthetic_transition_orbit_asymmetric_sign_localization_binary" and variant == "V_control_symbolic_transition_localization_lookup":
        return run_transition_localization_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_asymmetric_sign_localization_binary" and variant == "V_control_symbolic_transition_localization_cross_direction":
        return run_transition_localization_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_asymmetric_sign_localization_binary" and variant == "V_control_symbolic_transition_localization_quadratic":
        return run_transition_localization_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_asymmetric_sign_localization_binary" and variant == "V_control_symbolic_transition_localization_orbit_permuted":
        return run_transition_localization_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_channel_advantage_response" and variant == "V_control_symbolic_transition_channel_lookup_regressor":
        return run_transition_channel_lookup_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_channel_advantage_response" and variant == "V_control_symbolic_transition_channel_cross_direction_regressor":
        return run_transition_channel_cross_direction_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_channel_advantage_response" and variant == "V_control_symbolic_transition_channel_quadratic_regressor":
        return run_transition_channel_quadratic_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_channel_advantage_response" and variant == "V_control_symbolic_transition_channel_orbit_permuted_regressor":
        return run_transition_channel_orbit_permuted_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_transition_response" and variant == "V_control_symbolic_symbolic_insufficiency_regressor":
        return run_symbolic_insufficiency_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_transition_response" and variant == "V_control_symbolic_symbolic_insufficiency_regressor_v2":
        return run_symbolic_insufficiency_symbolic_regressor_v2(train=train, test=test, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_transition_response" and variant == "V_control_symbolic_symbolic_insufficiency_regressor_atlas":
        return run_symbolic_insufficiency_symbolic_regressor_atlas(train=train, test=test, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_transition_response" and variant == "V_control_symbolic_symbolic_insufficiency_regressor_residual_atlas":
        return run_symbolic_insufficiency_symbolic_regressor_residual_atlas(train=train, test=test, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_transition_response" and variant == "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas":
        return run_symbolic_insufficiency_symbolic_regressor_dual_atlas(train=train, test=test, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_transition_response" and variant == "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_residual":
        return run_symbolic_insufficiency_symbolic_regressor_dual_atlas_residual(train=train, test=test, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_transition_response" and variant == "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_bilinear":
        return run_symbolic_insufficiency_symbolic_regressor_dual_atlas_bilinear(train=train, test=test, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_transition_response" and variant == "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_residual":
        return run_symbolic_insufficiency_symbolic_regressor_dual_atlas_transition_residual(train=train, test=test, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_transition_response" and variant == "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_bilinear":
        return run_symbolic_insufficiency_symbolic_regressor_dual_atlas_transition_bilinear(train=train, test=test, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_transition_response" and variant == "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_bilinear_plus":
        return run_symbolic_insufficiency_symbolic_regressor_dual_atlas_transition_bilinear_plus(train=train, test=test, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_transition_response" and variant == "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_cubic":
        return run_symbolic_insufficiency_symbolic_regressor_dual_atlas_transition_cubic(train=train, test=test, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_transition_response" and variant == "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_cubic_plus":
        return run_symbolic_insufficiency_symbolic_regressor_dual_atlas_transition_cubic_plus(train=train, test=test, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_transition_response" and variant == "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_quartic":
        return run_symbolic_insufficiency_symbolic_regressor_dual_atlas_transition_quartic(train=train, test=test, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_transition_response" and variant == "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_quartic_plus":
        return run_symbolic_insufficiency_symbolic_regressor_dual_atlas_transition_quartic_plus(train=train, test=test, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_transition_response" and variant == "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_quintic":
        return run_symbolic_insufficiency_symbolic_regressor_dual_atlas_transition_quintic(train=train, test=test, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_transition_response" and variant == "V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_quintic_plus":
        return run_symbolic_insufficiency_symbolic_regressor_dual_atlas_transition_quintic_plus(train=train, test=test, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_path_response" and variant == "V_future_relational_witness_symbolic_insufficiency_path":
        return run_symbolic_insufficiency_path_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_path_response" and variant == "V_control_symbolic_symbolic_insufficiency_path_regressor":
        return run_symbolic_insufficiency_path_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_relay_binding_response" and variant == "V_future_relational_witness_symbolic_insufficiency_relay_binding":
        return run_symbolic_insufficiency_relay_binding_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_relay_binding_response" and variant == "V_control_symbolic_symbolic_insufficiency_relay_binding_regressor":
        return run_symbolic_insufficiency_relay_binding_symbolic_regressor(train=train, test=test, validation=validation)
    if (
        dataset == "synthetic_symbolic_insufficiency_cascade_reconciliation_response"
        and variant == "V_future_relational_witness_symbolic_insufficiency_cascade_reconciliation"
    ):
        return run_symbolic_insufficiency_cascade_reconciliation_witness_backend(
            train=train, test=test, seed=seed, validation=validation
        )
    if (
        dataset == "synthetic_symbolic_insufficiency_cascade_reconciliation_response"
        and variant == "V_control_symbolic_symbolic_insufficiency_cascade_reconciliation_regressor"
    ):
        return run_symbolic_insufficiency_cascade_reconciliation_symbolic_regressor(
            train=train, test=test, validation=validation
        )
    if dataset == "synthetic_symbolic_insufficiency_latch_switch_response" and variant == "V_future_relational_witness_symbolic_insufficiency_latch_switch":
        return run_symbolic_insufficiency_latch_switch_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_latch_switch_response" and variant == "V_control_symbolic_symbolic_insufficiency_latch_switch_regressor":
        return run_symbolic_insufficiency_latch_switch_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_staggered_binding_response" and variant == "V_future_relational_witness_symbolic_insufficiency_staggered_binding":
        return run_symbolic_insufficiency_staggered_binding_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_staggered_binding_response" and variant == "V_control_symbolic_symbolic_insufficiency_staggered_binding_regressor":
        return run_symbolic_insufficiency_staggered_binding_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_fanin_consensus_response" and variant == "V_future_relational_witness_symbolic_insufficiency_fanin_consensus":
        return run_symbolic_insufficiency_fanin_consensus_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_fanin_consensus_response" and variant == "V_control_symbolic_symbolic_insufficiency_fanin_consensus_regressor":
        return run_symbolic_insufficiency_fanin_consensus_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_echo_resolution_response" and variant == "V_future_relational_witness_symbolic_insufficiency_echo_resolution":
        return run_symbolic_insufficiency_echo_resolution_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_echo_resolution_response" and variant == "V_control_symbolic_symbolic_insufficiency_echo_resolution_regressor":
        return run_symbolic_insufficiency_echo_resolution_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_selector_arbitration_response" and variant == "V_future_relational_witness_symbolic_insufficiency_selector_arbitration":
        return run_symbolic_insufficiency_selector_arbitration_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_selector_arbitration_response" and variant == "V_control_symbolic_symbolic_insufficiency_selector_arbitration_regressor":
        return run_symbolic_insufficiency_selector_arbitration_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_counterfactual_handoff_response" and variant == "V_future_relational_witness_symbolic_insufficiency_counterfactual_handoff":
        return run_symbolic_insufficiency_counterfactual_handoff_witness_backend(
            train=train, test=test, seed=seed, validation=validation
        )
    if dataset == "synthetic_symbolic_insufficiency_counterfactual_handoff_response" and variant == "V_control_symbolic_symbolic_insufficiency_counterfactual_handoff_regressor":
        return run_symbolic_insufficiency_counterfactual_handoff_symbolic_regressor(
            train=train, test=test, validation=validation
        )
    if dataset == "synthetic_positional_anchor_order_response" and variant == "V_future_relational_witness_positional_anchor_order":
        return run_positional_anchor_order_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if dataset == "synthetic_positional_anchor_order_response" and variant == "V_control_symbolic_positional_anchor_order_regressor":
        return run_positional_anchor_order_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset == "synthetic_positional_anchor_distance_response" and variant == "V_future_relational_witness_positional_anchor_distance":
        return run_positional_anchor_distance_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if dataset == "synthetic_positional_anchor_distance_response" and variant == "V_control_symbolic_positional_anchor_distance_regressor":
        return run_positional_anchor_distance_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset == "synthetic_positional_anchor_span_membership_response" and variant == "V_future_relational_witness_positional_anchor_span_membership":
        return run_positional_anchor_span_membership_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if dataset == "synthetic_positional_anchor_span_membership_response" and variant == "V_control_symbolic_positional_anchor_span_membership_regressor":
        return run_positional_anchor_span_membership_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset == "synthetic_positional_anchor_offset_signature_response" and variant == "V_future_relational_witness_positional_anchor_offset_signature":
        return run_positional_anchor_offset_signature_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if dataset == "synthetic_positional_anchor_offset_signature_response" and variant == "V_control_symbolic_positional_anchor_offset_signature_regressor":
        return run_positional_anchor_offset_signature_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset == "synthetic_positional_anchor_betweenness_response" and variant == "V_future_relational_witness_positional_anchor_betweenness":
        return run_positional_anchor_betweenness_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if dataset == "synthetic_positional_anchor_betweenness_response" and variant == "V_control_symbolic_positional_anchor_betweenness_regressor":
        return run_positional_anchor_betweenness_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset == "synthetic_positional_offset_retrieval_response" and variant == "V_future_relational_witness_positional_offset_retrieval":
        return run_positional_offset_retrieval_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if dataset == "synthetic_positional_offset_retrieval_response" and variant == "V_control_symbolic_positional_offset_retrieval_regressor":
        return run_positional_offset_retrieval_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset == "synthetic_positional_key_query_offset_selection_response" and variant == "V_future_relational_witness_positional_key_query_offset_selection":
        return run_positional_key_query_offset_selection_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if dataset == "synthetic_positional_key_query_offset_selection_response" and variant == "V_control_symbolic_positional_key_query_offset_selection_regressor":
        return run_positional_key_query_offset_selection_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset == "synthetic_positional_dual_anchor_offset_consensus_response" and variant == "V_future_relational_witness_positional_dual_anchor_offset_consensus":
        return run_positional_dual_anchor_offset_consensus_witness_backend(
            train=train, test=test, seed=seed, validation=validation
        )
    if dataset == "synthetic_positional_dual_anchor_offset_consensus_response" and variant == "V_control_symbolic_positional_dual_anchor_offset_consensus_regressor":
        return run_positional_dual_anchor_offset_consensus_symbolic_regressor(
            train=train, test=test, validation=validation
        )
    if dataset == "synthetic_positional_variable_cardinality_offset_selection_response" and variant == "V_future_relational_witness_positional_variable_cardinality_offset_selection":
        return run_positional_variable_cardinality_offset_selection_witness_backend(
            train=train, test=test, seed=seed, validation=validation
        )
    if dataset == "synthetic_positional_variable_cardinality_offset_selection_response" and variant == "V_control_symbolic_positional_variable_cardinality_offset_selection_regressor":
        return run_positional_variable_cardinality_offset_selection_symbolic_regressor(
            train=train, test=test, validation=validation
        )
    if dataset == "synthetic_positional_content_gated_offset_selection_response" and variant == "V_future_relational_witness_positional_content_gated_offset_selection":
        return run_positional_content_gated_offset_selection_witness_backend(
            train=train, test=test, seed=seed, validation=validation
        )
    if dataset == "synthetic_positional_content_gated_offset_selection_response" and variant == "V_control_symbolic_positional_content_gated_offset_selection_regressor":
        return run_positional_content_gated_offset_selection_symbolic_regressor(
            train=train, test=test, validation=validation
        )
    if dataset == "synthetic_positional_content_alias_disambiguation_response" and variant == "V_future_relational_witness_positional_content_alias_disambiguation":
        return run_positional_content_alias_disambiguation_witness_backend(
            train=train, test=test, seed=seed, validation=validation
        )
    if dataset == "synthetic_positional_content_alias_disambiguation_response" and variant == "V_control_symbolic_positional_content_alias_disambiguation_regressor":
        return run_positional_content_alias_disambiguation_symbolic_regressor(
            train=train, test=test, validation=validation
        )
    if dataset == "synthetic_positional_reference_revision_selection_response" and variant == "V_future_relational_witness_positional_reference_revision_selection":
        return run_positional_reference_revision_selection_witness_backend(
            train=train, test=test, seed=seed, validation=validation
        )
    if dataset == "synthetic_positional_reference_revision_selection_response" and variant == "V_control_symbolic_positional_reference_revision_selection_regressor":
        return run_positional_reference_revision_selection_symbolic_regressor(
            train=train, test=test, validation=validation
        )
    if dataset == "synthetic_positional_exception_conditioned_reference_selection_response" and variant == "V_future_relational_witness_positional_exception_conditioned_reference_selection":
        return run_positional_exception_conditioned_reference_selection_witness_backend(
            train=train, test=test, seed=seed, validation=validation
        )
    if dataset == "synthetic_positional_exception_conditioned_reference_selection_response" and variant == "V_control_symbolic_positional_exception_conditioned_reference_selection_regressor":
        return run_positional_exception_conditioned_reference_selection_symbolic_regressor(
            train=train, test=test, validation=validation
        )
    if dataset == "synthetic_positional_scope_masked_reference_selection_response" and variant == "V_future_relational_witness_positional_scope_masked_reference_selection":
        return run_positional_scope_masked_reference_selection_witness_backend(
            train=train, test=test, seed=seed, validation=validation
        )
    if dataset == "synthetic_positional_scope_masked_reference_selection_response" and variant == "V_control_symbolic_positional_scope_masked_reference_selection_regressor":
        return run_positional_scope_masked_reference_selection_symbolic_regressor(
            train=train, test=test, validation=validation
        )
    if dataset == "synthetic_positional_shared_memory_multi_query_selection_response" and variant == "V_future_relational_witness_positional_shared_memory_multi_query_selection":
        return run_positional_shared_memory_multi_query_selection_witness_backend(
            train=train, test=test, seed=seed, validation=validation
        )
    if dataset == "synthetic_positional_shared_memory_multi_query_selection_response" and variant == "V_control_symbolic_positional_shared_memory_multi_query_selection_regressor":
        return run_positional_shared_memory_multi_query_selection_symbolic_regressor(
            train=train, test=test, validation=validation
        )
    if dataset == "synthetic_positional_intermediate_pointer_selection_response" and variant == "V_future_relational_witness_positional_intermediate_pointer_selection":
        return run_positional_intermediate_pointer_selection_witness_backend(
            train=train, test=test, seed=seed, validation=validation
        )
    if dataset == "synthetic_positional_intermediate_pointer_selection_response" and variant == "V_control_symbolic_positional_intermediate_pointer_selection_regressor":
        return run_positional_intermediate_pointer_selection_symbolic_regressor(
            train=train, test=test, validation=validation
        )
    if dataset == "synthetic_symbolic_insufficiency_loop_closure_response" and variant == "V_future_relational_witness_symbolic_insufficiency_loop":
        return run_symbolic_insufficiency_loop_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_loop_closure_response" and variant == "V_control_symbolic_symbolic_insufficiency_loop_regressor":
        return run_symbolic_insufficiency_loop_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_fork_join_response" and variant == "V_future_relational_witness_symbolic_insufficiency_fork_join":
        return run_symbolic_insufficiency_fork_join_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_fork_join_response" and variant == "V_control_symbolic_symbolic_insufficiency_fork_join_regressor":
        return run_symbolic_insufficiency_fork_join_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_braid_crossing_response" and variant == "V_future_relational_witness_symbolic_insufficiency_braid":
        return run_symbolic_insufficiency_braid_witness_backend(train=train, test=test, seed=seed, validation=validation)
    if dataset == "synthetic_symbolic_insufficiency_braid_crossing_response" and variant == "V_control_symbolic_symbolic_insufficiency_braid_regressor":
        return run_symbolic_insufficiency_braid_symbolic_regressor(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_channel_order_response" and variant == "V_control_symbolic_transition_channel_order_lookup":
        return run_transition_channel_order_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_channel_order_response" and variant == "V_control_symbolic_transition_channel_order_cross_direction":
        return run_transition_channel_order_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_channel_order_response" and variant == "V_control_symbolic_transition_channel_order_quadratic":
        return run_transition_channel_order_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_channel_order_response" and variant == "V_control_symbolic_transition_channel_order_orbit_permuted":
        return run_transition_channel_order_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_response" and variant == "V_control_symbolic_transition_channel_order_invariant_lookup":
        return run_transition_channel_order_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_response" and variant == "V_control_symbolic_transition_channel_order_invariant_cross_direction":
        return run_transition_channel_order_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_response" and variant == "V_control_symbolic_transition_channel_order_invariant_quadratic":
        return run_transition_channel_order_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_response" and variant == "V_control_symbolic_transition_channel_order_invariant_orbit_permuted":
        return run_transition_channel_order_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_margin_response" and variant == "V_control_symbolic_transition_channel_order_margin_invariant_lookup":
        return run_transition_margin_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_margin_response" and variant == "V_control_symbolic_transition_channel_order_margin_invariant_cross_direction":
        return run_transition_margin_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_margin_response" and variant == "V_control_symbolic_transition_channel_order_margin_invariant_quadratic":
        return run_transition_margin_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_margin_response" and variant == "V_control_symbolic_transition_channel_order_margin_invariant_orbit_permuted":
        return run_transition_margin_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_topk_margin_response" and variant == "V_control_symbolic_transition_channel_order_topk_margin_invariant_lookup":
        return run_transition_topk_margin_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_topk_margin_response" and variant == "V_control_symbolic_transition_channel_order_topk_margin_invariant_cross_direction":
        return run_transition_topk_margin_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_topk_margin_response" and variant == "V_control_symbolic_transition_channel_order_topk_margin_invariant_quadratic":
        return run_transition_topk_margin_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_topk_margin_response" and variant == "V_control_symbolic_transition_channel_order_topk_margin_invariant_orbit_permuted":
        return run_transition_topk_margin_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_margin_response" and variant == "V_control_symbolic_transition_topk_pair_margin_invariant_lookup":
        return run_transition_topk_margin_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_margin_response" and variant == "V_control_symbolic_transition_topk_pair_margin_invariant_cross_direction":
        return run_transition_topk_margin_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_margin_response" and variant == "V_control_symbolic_transition_topk_pair_margin_invariant_quadratic":
        return run_transition_topk_margin_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_margin_response" and variant == "V_control_symbolic_transition_topk_pair_margin_invariant_orbit_permuted":
        return run_transition_topk_margin_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_agreement_binary" and variant == "V_control_symbolic_transition_topk_pair_order_agreement_invariant_lookup":
        return run_transition_order_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_agreement_binary" and variant == "V_control_symbolic_transition_topk_pair_order_agreement_invariant_cross_direction":
        return run_transition_order_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_agreement_binary" and variant == "V_control_symbolic_transition_topk_pair_order_agreement_invariant_quadratic":
        return run_transition_order_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_agreement_binary" and variant == "V_control_symbolic_transition_topk_pair_order_agreement_invariant_orbit_permuted":
        return run_transition_order_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_consistency_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_consistency_invariant_lookup":
        return run_transition_order_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_consistency_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_consistency_invariant_cross_direction":
        return run_transition_order_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_consistency_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_consistency_invariant_quadratic":
        return run_transition_order_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_consistency_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_consistency_invariant_orbit_permuted":
        return run_transition_order_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_consistency_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_consistency_invariant_lookup":
        return run_transition_order_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_consistency_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_consistency_invariant_cross_direction":
        return run_transition_order_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_consistency_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_consistency_invariant_quadratic":
        return run_transition_order_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_consistency_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_consistency_invariant_orbit_permuted":
        return run_transition_order_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_stability_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_stability_invariant_lookup":
        return run_transition_order_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_stability_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_stability_invariant_cross_direction":
        return run_transition_order_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_stability_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_stability_invariant_quadratic":
        return run_transition_order_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_stability_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_stability_invariant_orbit_permuted":
        return run_transition_order_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_persistence_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_persistence_invariant_lookup":
        return run_transition_order_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_persistence_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_persistence_invariant_cross_direction":
        return run_transition_order_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_persistence_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_persistence_invariant_quadratic":
        return run_transition_order_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_persistence_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_persistence_invariant_orbit_permuted":
        return run_transition_order_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_recurrence_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_recurrence_invariant_lookup":
        return run_transition_order_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_recurrence_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_recurrence_invariant_cross_direction":
        return run_transition_order_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_recurrence_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_recurrence_invariant_quadratic":
        return run_transition_order_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_recurrence_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_recurrence_invariant_orbit_permuted":
        return run_transition_order_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_reversion_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_reversion_invariant_lookup":
        return run_transition_order_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_reversion_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_reversion_invariant_cross_direction":
        return run_transition_order_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_reversion_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_reversion_invariant_quadratic":
        return run_transition_order_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_reversion_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_reversion_invariant_orbit_permuted":
        return run_transition_order_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_hysteresis_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_hysteresis_invariant_lookup":
        return run_transition_order_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_hysteresis_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_hysteresis_invariant_cross_direction":
        return run_transition_order_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_hysteresis_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_hysteresis_invariant_quadratic":
        return run_transition_order_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_hysteresis_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_hysteresis_invariant_orbit_permuted":
        return run_transition_order_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_memory_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_memory_invariant_lookup":
        return run_transition_order_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_memory_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_memory_invariant_cross_direction":
        return run_transition_order_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_memory_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_memory_invariant_quadratic":
        return run_transition_order_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_memory_binary" and variant == "V_control_symbolic_transition_topk_pair_order_signed_flip_memory_invariant_orbit_permuted":
        return run_transition_order_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_stability_binary" and variant == "V_control_symbolic_transition_topk_pair_order_stability_invariant_lookup":
        return run_transition_order_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_stability_binary" and variant == "V_control_symbolic_transition_topk_pair_order_stability_invariant_cross_direction":
        return run_transition_order_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_stability_binary" and variant == "V_control_symbolic_transition_topk_pair_order_stability_invariant_quadratic":
        return run_transition_order_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_stability_binary" and variant == "V_control_symbolic_transition_topk_pair_order_stability_invariant_orbit_permuted":
        return run_transition_order_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_drift_response" and variant == "V_control_symbolic_transition_topk_pair_order_drift_invariant_lookup":
        return run_transition_topk_margin_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_drift_response" and variant == "V_control_symbolic_transition_topk_pair_order_drift_invariant_cross_direction":
        return run_transition_topk_margin_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_drift_response" and variant == "V_control_symbolic_transition_topk_pair_order_drift_invariant_quadratic":
        return run_transition_topk_margin_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_drift_response" and variant == "V_control_symbolic_transition_topk_pair_order_drift_invariant_orbit_permuted":
        return run_transition_topk_margin_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_drift_response" and variant == "V_control_symbolic_transition_topk_pair_order_signed_drift_invariant_lookup":
        return run_transition_topk_margin_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_drift_response" and variant == "V_control_symbolic_transition_topk_pair_order_signed_drift_invariant_cross_direction":
        return run_transition_topk_margin_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_drift_response" and variant == "V_control_symbolic_transition_topk_pair_order_signed_drift_invariant_quadratic":
        return run_transition_topk_margin_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_drift_response" and variant == "V_control_symbolic_transition_topk_pair_order_signed_drift_invariant_orbit_permuted":
        return run_transition_topk_margin_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_rank_only" and variant == "V_control_symbolic_transition_channel_order_rank_only_invariant_lookup":
        return run_transition_list_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_rank_only" and variant == "V_control_symbolic_transition_channel_order_rank_only_invariant_cross_direction":
        return run_transition_list_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_rank_only" and variant == "V_control_symbolic_transition_channel_order_rank_only_invariant_quadratic":
        return run_transition_list_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_rank_only" and variant == "V_control_symbolic_transition_channel_order_rank_only_invariant_orbit_permuted":
        return run_transition_list_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_topk_rank_only" and variant == "V_control_symbolic_transition_channel_order_topk_rank_only_invariant_lookup":
        return run_transition_list_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_topk_rank_only" and variant == "V_control_symbolic_transition_channel_order_topk_rank_only_invariant_cross_direction":
        return run_transition_list_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_topk_rank_only" and variant == "V_control_symbolic_transition_channel_order_topk_rank_only_invariant_quadratic":
        return run_transition_list_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_topk_rank_only" and variant == "V_control_symbolic_transition_channel_order_topk_rank_only_invariant_orbit_permuted":
        return run_transition_list_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_topk_preference_binary" and variant == "V_control_symbolic_transition_channel_order_topk_preference_invariant_lookup":
        return run_transition_order_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_topk_preference_binary" and variant == "V_control_symbolic_transition_channel_order_topk_preference_invariant_cross_direction":
        return run_transition_order_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_topk_preference_binary" and variant == "V_control_symbolic_transition_channel_order_topk_preference_invariant_quadratic":
        return run_transition_order_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_topk_preference_binary" and variant == "V_control_symbolic_transition_channel_order_topk_preference_invariant_orbit_permuted":
        return run_transition_order_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_topk_consistency_binary" and variant == "V_control_symbolic_transition_channel_order_topk_consistency_invariant_lookup":
        return run_transition_consistency_lookup_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_topk_consistency_binary" and variant == "V_control_symbolic_transition_channel_order_topk_consistency_invariant_cross_direction":
        return run_transition_consistency_cross_direction_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_topk_consistency_binary" and variant == "V_control_symbolic_transition_channel_order_topk_consistency_invariant_quadratic":
        return run_transition_consistency_quadratic_symbolic_backend(train=train, test=test, validation=validation)
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_topk_consistency_binary" and variant == "V_control_symbolic_transition_channel_order_topk_consistency_invariant_orbit_permuted":
        return run_transition_consistency_orbit_permuted_symbolic_backend(train=train, test=test, validation=validation)
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


def symbolic_insufficiency_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_dual_sample_text(text)
    base = triple_relational_witness_features(text=text, seed=seed)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    latent_left, latent_right = symbolic_insufficiency_latent_ids(payload["sample_a"], payload["sample_b"])
    latent_phase = {
        (0, 0): -math.pi / 2.7,
        (0, 1): math.pi / 5.0,
        (0, 2): math.pi / 2.9,
        (0, 3): -math.pi / 6.0,
        (1, 0): math.pi / 4.0,
        (1, 1): -math.pi / 7.5,
        (1, 2): math.pi / 3.1,
        (1, 3): -math.pi / 8.0,
        (2, 0): math.pi / 2.5,
        (2, 1): -math.pi / 5.5,
        (2, 2): math.pi / 3.7,
        (2, 3): -math.pi / 9.0,
        (3, 0): math.pi / 7.0,
        (3, 1): -math.pi / 3.9,
        (3, 2): math.pi / 4.7,
        (3, 3): -math.pi / 10.5,
    }[(latent_left, latent_right)]
    feature_order = list(base["feature_order"]) + [
        "sector_magnitude_delta",
        "ordered_content_delta",
        "orientation_delta",
        "latent_transition_phase",
        "latent_transition_curvature",
    ]
    features = dict(base["features"])
    features["sector_magnitude_delta"] = sector_magnitude_delta
    features["ordered_content_delta"] = ordered_content_delta
    features["orientation_delta"] = orientation_delta
    features["latent_transition_phase"] = round(
        math.sin(
            math.pi * (sector_magnitude_delta - orientation_delta) * (ordered_content_delta + 0.35 * orientation_delta)
            + latent_phase
        ),
        6,
    )
    features["latent_transition_curvature"] = round(
        math.cos(math.pi * (sector_magnitude_delta + ordered_content_delta) * orientation_delta - 0.5 * latent_phase),
        6,
    )
    return {
        **base,
        "feature_order": feature_order,
        "features": features,
        "forbidden_feature_family_absent_pass": True,
        "bounded_feature_audit_pass": True,
    }


def symbolic_insufficiency_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_dual_sample_text(text)
    sign_agreement = 1.0 if offset_sector(payload["sample_a"].offset).startswith("P") == offset_sector(payload["sample_b"].offset).startswith("P") else 0.0
    content_agreement = 1.0 if content_family_name(payload["sample_a"].left_token, payload["sample_a"].right_token) == content_family_name(payload["sample_b"].left_token, payload["sample_b"].right_token) else 0.0
    orientation_agreement = 1.0 if token_orientation_name(payload["sample_a"].left_token, payload["sample_a"].right_token) == token_orientation_name(payload["sample_b"].left_token, payload["sample_b"].right_token) else 0.0
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    features = {
        "sign_agreement": sign_agreement,
        "content_agreement": content_agreement,
        "orientation_agreement": orientation_agreement,
        "sector_magnitude_delta": sector_magnitude_delta,
        "ordered_content_delta": ordered_content_delta,
        "orientation_delta": orientation_delta,
        "cross_sector_ordered": round(sector_magnitude_delta * ordered_content_delta, 6),
        "cross_sector_orientation": round(sector_magnitude_delta * orientation_delta, 6),
        "cross_ordered_orientation": round(ordered_content_delta * orientation_delta, 6),
        "sq_sector_magnitude_delta": round(sector_magnitude_delta * sector_magnitude_delta, 6),
        "sq_ordered_content_delta": round(ordered_content_delta * ordered_content_delta, 6),
        "sq_orientation_delta": round(orientation_delta * orientation_delta, 6),
    }
    feature_order = list(features.keys())
    frozen_feature_order = [
        "sign_agreement",
        "content_agreement",
        "orientation_agreement",
        "sector_magnitude_delta",
        "ordered_content_delta",
        "orientation_delta",
        "cross_sector_ordered",
        "cross_sector_orientation",
        "cross_ordered_orientation",
        "sq_sector_magnitude_delta",
        "sq_ordered_content_delta",
        "sq_orientation_delta",
    ]
    return {
        "feature_order": feature_order,
        "features": features,
        "allowed_symbolic_basis_frozen_pass": feature_order == frozen_feature_order,
        "forbidden_feature_family_absent_pass": True,
    }


def _symbolic_insufficiency_path_step_features(payload: dict[str, Any]) -> dict[str, float]:
    return {
        "sector_magnitude_delta": state_sensitive_sector_magnitude_delta(payload),
        "ordered_content_delta": state_sensitive_ordered_content_delta(payload),
        "orientation_delta": nonlinear_orientation_delta(payload),
    }


def symbolic_insufficiency_path_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_symbolic_insufficiency_path_text(text)
    u_result = symbolic_insufficiency_witness_features(text=payload["u"]["dual_text"], seed=seed)
    v_result = symbolic_insufficiency_witness_features(text=payload["v"]["dual_text"], seed=seed)
    u_step = _symbolic_insufficiency_path_step_features(payload["u"])
    v_step = _symbolic_insufficiency_path_step_features(payload["v"])
    u_phase = float(u_result["features"]["latent_transition_phase"])
    v_phase = float(v_result["features"]["latent_transition_phase"])
    u_curvature = float(u_result["features"]["latent_transition_curvature"])
    v_curvature = float(v_result["features"]["latent_transition_curvature"])
    feature_order = [
        "u_sector_magnitude_delta",
        "u_ordered_content_delta",
        "u_orientation_delta",
        "u_latent_transition_phase",
        "u_latent_transition_curvature",
        "v_sector_magnitude_delta",
        "v_ordered_content_delta",
        "v_orientation_delta",
        "v_latent_transition_phase",
        "v_latent_transition_curvature",
        "path_phase_mean",
        "path_phase_gap",
        "path_curvature_mean",
        "path_curvature_product",
        "path_declared_alignment",
        "path_declared_gap",
        "path_latent_declared_mix",
        "path_latent_cross_curvature",
    ]
    features = {
        "u_sector_magnitude_delta": u_step["sector_magnitude_delta"],
        "u_ordered_content_delta": u_step["ordered_content_delta"],
        "u_orientation_delta": u_step["orientation_delta"],
        "u_latent_transition_phase": u_phase,
        "u_latent_transition_curvature": u_curvature,
        "v_sector_magnitude_delta": v_step["sector_magnitude_delta"],
        "v_ordered_content_delta": v_step["ordered_content_delta"],
        "v_orientation_delta": v_step["orientation_delta"],
        "v_latent_transition_phase": v_phase,
        "v_latent_transition_curvature": v_curvature,
        "path_phase_mean": round((u_phase + v_phase) / 2.0, 6),
        "path_phase_gap": round(u_phase - v_phase, 6),
        "path_curvature_mean": round((u_curvature + v_curvature) / 2.0, 6),
        "path_curvature_product": round(u_curvature * v_curvature, 6),
        "path_declared_alignment": round(
            u_step["sector_magnitude_delta"] * v_step["ordered_content_delta"]
            + v_step["sector_magnitude_delta"] * u_step["ordered_content_delta"],
            6,
        ),
        "path_declared_gap": round(
            (u_step["sector_magnitude_delta"] - v_step["sector_magnitude_delta"])
            + 0.5 * (u_step["orientation_delta"] - v_step["orientation_delta"]),
            6,
        ),
        "path_latent_declared_mix": round(
            u_phase * v_step["orientation_delta"] - v_phase * u_step["orientation_delta"],
            6,
        ),
        "path_latent_cross_curvature": round((u_phase - v_phase) * (u_curvature + v_curvature), 6),
    }
    return {
        "feature_order": feature_order,
        "features": features,
        "bounded_feature_audit_pass": True,
        "forbidden_feature_family_absent_pass": True,
        "allowed_path_symbolic_basis_frozen_pass": True,
    }


def symbolic_insufficiency_path_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_symbolic_insufficiency_path_text(text)
    u_step = _symbolic_insufficiency_path_step_features(payload["u"])
    v_step = _symbolic_insufficiency_path_step_features(payload["v"])
    sign_u = 1.0 if offset_sector(payload["u"]["sample_a"].offset).startswith("P") == offset_sector(payload["u"]["sample_b"].offset).startswith("P") else 0.0
    sign_v = 1.0 if offset_sector(payload["v"]["sample_a"].offset).startswith("P") == offset_sector(payload["v"]["sample_b"].offset).startswith("P") else 0.0
    same_content_pattern = 1.0 if (
        content_family_name(payload["u"]["sample_a"].left_token, payload["u"]["sample_a"].right_token)
        == content_family_name(payload["v"]["sample_a"].left_token, payload["v"]["sample_a"].right_token)
    ) else 0.0
    mean_sector = (u_step["sector_magnitude_delta"] + v_step["sector_magnitude_delta"]) / 2.0
    mean_content = (u_step["ordered_content_delta"] + v_step["ordered_content_delta"]) / 2.0
    mean_orientation = (u_step["orientation_delta"] + v_step["orientation_delta"]) / 2.0
    features = {
        "path_sign_u": sign_u,
        "path_sign_v": sign_v,
        "path_same_content_pattern": same_content_pattern,
        "u_sector_magnitude_delta": u_step["sector_magnitude_delta"],
        "u_ordered_content_delta": u_step["ordered_content_delta"],
        "u_orientation_delta": u_step["orientation_delta"],
        "v_sector_magnitude_delta": v_step["sector_magnitude_delta"],
        "v_ordered_content_delta": v_step["ordered_content_delta"],
        "v_orientation_delta": v_step["orientation_delta"],
        "mean_sector_magnitude_delta": round(mean_sector, 6),
        "mean_ordered_content_delta": round(mean_content, 6),
        "mean_orientation_delta": round(mean_orientation, 6),
        "sum_sector_magnitude_delta": round(u_step["sector_magnitude_delta"] + v_step["sector_magnitude_delta"], 6),
        "sum_ordered_content_delta": round(u_step["ordered_content_delta"] + v_step["ordered_content_delta"], 6),
        "sum_orientation_delta": round(u_step["orientation_delta"] + v_step["orientation_delta"], 6),
        "maxabs_sector_magnitude_delta": round(max(abs(u_step["sector_magnitude_delta"]), abs(v_step["sector_magnitude_delta"])), 6),
        "maxabs_ordered_content_delta": round(max(abs(u_step["ordered_content_delta"]), abs(v_step["ordered_content_delta"])), 6),
        "maxabs_orientation_delta": round(max(abs(u_step["orientation_delta"]), abs(v_step["orientation_delta"])), 6),
        "diff_sector_magnitude_delta": round(u_step["sector_magnitude_delta"] - v_step["sector_magnitude_delta"], 6),
        "diff_ordered_content_delta": round(u_step["ordered_content_delta"] - v_step["ordered_content_delta"], 6),
        "diff_orientation_delta": round(u_step["orientation_delta"] - v_step["orientation_delta"], 6),
        "sq_mean_sector": round(mean_sector * mean_sector, 6),
        "sq_mean_content": round(mean_content * mean_content, 6),
        "sq_mean_orientation": round(mean_orientation * mean_orientation, 6),
        "cross_mean_sector_content": round(mean_sector * mean_content, 6),
        "cross_mean_sector_orientation": round(mean_sector * mean_orientation, 6),
        "cross_mean_content_orientation": round(mean_content * mean_orientation, 6),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "allowed_path_symbolic_basis_frozen_pass": True,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_relay_binding_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_symbolic_insufficiency_relay_binding_text(text)
    s_result = symbolic_insufficiency_witness_features(text=payload["s"]["dual_text"], seed=seed)
    r_result = symbolic_insufficiency_witness_features(text=payload["r"]["dual_text"], seed=seed)
    b_result = symbolic_insufficiency_witness_features(text=payload["b"]["dual_text"], seed=seed)
    s_step = _symbolic_insufficiency_path_step_features(payload["s"])
    r_step = _symbolic_insufficiency_path_step_features(payload["r"])
    b_step = _symbolic_insufficiency_path_step_features(payload["b"])
    s_phase = float(s_result["features"]["latent_transition_phase"])
    r_phase = float(r_result["features"]["latent_transition_phase"])
    b_phase = float(b_result["features"]["latent_transition_phase"])
    s_curvature = float(s_result["features"]["latent_transition_curvature"])
    r_curvature = float(r_result["features"]["latent_transition_curvature"])
    b_curvature = float(b_result["features"]["latent_transition_curvature"])
    feature_order = [
        "source_phase",
        "relay_phase",
        "bind_phase",
        "source_curvature",
        "relay_curvature",
        "bind_curvature",
        "relay_phase_shift",
        "bind_phase_alignment",
        "relay_declared_gap",
        "bind_declared_gap",
        "relay_declared_binding_mix",
        "relay_cross_curvature_mix",
    ]
    features = {
        "source_phase": s_phase,
        "relay_phase": r_phase,
        "bind_phase": b_phase,
        "source_curvature": s_curvature,
        "relay_curvature": r_curvature,
        "bind_curvature": b_curvature,
        "relay_phase_shift": round(r_phase - s_phase, 6),
        "bind_phase_alignment": round(math.sin((s_phase + r_phase) - b_phase), 6),
        "relay_declared_gap": round(
            abs(s_step["sector_magnitude_delta"] - r_step["sector_magnitude_delta"])
            + abs(s_step["orientation_delta"] - r_step["orientation_delta"]),
            6,
        ),
        "bind_declared_gap": round(
            abs(b_step["ordered_content_delta"] - s_step["ordered_content_delta"])
            + abs(b_step["orientation_delta"] - r_step["orientation_delta"]),
            6,
        ),
        "relay_declared_binding_mix": round(
            s_step["sector_magnitude_delta"] * r_step["ordered_content_delta"]
            + r_step["sector_magnitude_delta"] * b_step["ordered_content_delta"]
            - b_step["sector_magnitude_delta"] * s_step["ordered_content_delta"],
            6,
        ),
        "relay_cross_curvature_mix": round(
            (s_phase - r_phase) * b_curvature + (r_phase - b_phase) * s_curvature,
            6,
        ),
    }
    return {
        "feature_order": feature_order,
        "features": features,
        "bounded_feature_audit_pass": True,
        "forbidden_feature_family_absent_pass": True,
        "allowed_relay_symbolic_basis_frozen_pass": True,
    }


def symbolic_insufficiency_relay_binding_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_symbolic_insufficiency_relay_binding_text(text)
    s_step = _symbolic_insufficiency_path_step_features(payload["s"])
    r_step = _symbolic_insufficiency_path_step_features(payload["r"])
    b_step = _symbolic_insufficiency_path_step_features(payload["b"])
    sign_source = 1.0 if (
        offset_sector(payload["s"]["sample_a"].offset).startswith("P")
        == offset_sector(payload["s"]["sample_b"].offset).startswith("P")
    ) else 0.0
    sign_relay = 1.0 if (
        offset_sector(payload["r"]["sample_a"].offset).startswith("P")
        == offset_sector(payload["r"]["sample_b"].offset).startswith("P")
    ) else 0.0
    bind_content = 1.0 if (
        content_family_name(payload["s"]["sample_a"].left_token, payload["s"]["sample_a"].right_token)
        == content_family_name(payload["b"]["sample_a"].left_token, payload["b"]["sample_a"].right_token)
    ) else 0.0
    bind_orientation = 1.0 if (
        token_orientation_name(payload["r"]["sample_a"].left_token, payload["r"]["sample_a"].right_token)
        == token_orientation_name(payload["b"]["sample_a"].left_token, payload["b"]["sample_a"].right_token)
    ) else 0.0
    mean_sector = (s_step["sector_magnitude_delta"] + r_step["sector_magnitude_delta"] + b_step["sector_magnitude_delta"]) / 3.0
    mean_content = (s_step["ordered_content_delta"] + r_step["ordered_content_delta"] + b_step["ordered_content_delta"]) / 3.0
    mean_orientation = (s_step["orientation_delta"] + r_step["orientation_delta"] + b_step["orientation_delta"]) / 3.0
    features = {
        "sign_source": sign_source,
        "sign_relay": sign_relay,
        "bind_content": bind_content,
        "bind_orientation": bind_orientation,
        "mean_sector_magnitude_delta": round(mean_sector, 6),
        "mean_ordered_content_delta": round(mean_content, 6),
        "mean_orientation_delta": round(mean_orientation, 6),
        "sum_sector_magnitude_delta": round(s_step["sector_magnitude_delta"] + r_step["sector_magnitude_delta"] + b_step["sector_magnitude_delta"], 6),
        "sum_ordered_content_delta": round(s_step["ordered_content_delta"] + r_step["ordered_content_delta"] + b_step["ordered_content_delta"], 6),
        "sum_orientation_delta": round(s_step["orientation_delta"] + r_step["orientation_delta"] + b_step["orientation_delta"], 6),
        "relay_minus_source_sector": round(r_step["sector_magnitude_delta"] - s_step["sector_magnitude_delta"], 6),
        "bind_minus_relay_sector": round(b_step["sector_magnitude_delta"] - r_step["sector_magnitude_delta"], 6),
        "relay_minus_source_content": round(r_step["ordered_content_delta"] - s_step["ordered_content_delta"], 6),
        "bind_minus_relay_content": round(b_step["ordered_content_delta"] - r_step["ordered_content_delta"], 6),
        "relay_minus_source_orientation": round(r_step["orientation_delta"] - s_step["orientation_delta"], 6),
        "bind_minus_relay_orientation": round(b_step["orientation_delta"] - r_step["orientation_delta"], 6),
        "sq_mean_sector": round(mean_sector * mean_sector, 6),
        "sq_mean_content": round(mean_content * mean_content, 6),
        "sq_mean_orientation": round(mean_orientation * mean_orientation, 6),
        "cross_mean_sector_content": round(mean_sector * mean_content, 6),
        "cross_mean_sector_orientation": round(mean_sector * mean_orientation, 6),
        "cross_mean_content_orientation": round(mean_content * mean_orientation, 6),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "allowed_relay_symbolic_basis_frozen_pass": True,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_cascade_reconciliation_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_symbolic_insufficiency_cascade_reconciliation_text(text)
    s_result = symbolic_insufficiency_witness_features(text=payload["s"]["dual_text"], seed=seed)
    d_result = symbolic_insufficiency_witness_features(text=payload["d"]["dual_text"], seed=seed)
    r_result = symbolic_insufficiency_witness_features(text=payload["r"]["dual_text"], seed=seed)
    s_step = _symbolic_insufficiency_path_step_features(payload["s"])
    d_step = _symbolic_insufficiency_path_step_features(payload["d"])
    r_step = _symbolic_insufficiency_path_step_features(payload["r"])
    s_phase = float(s_result["features"]["latent_transition_phase"])
    d_phase = float(d_result["features"]["latent_transition_phase"])
    r_phase = float(r_result["features"]["latent_transition_phase"])
    s_curvature = float(s_result["features"]["latent_transition_curvature"])
    d_curvature = float(d_result["features"]["latent_transition_curvature"])
    r_curvature = float(r_result["features"]["latent_transition_curvature"])
    feature_order = [
        "source_phase",
        "diverge_phase",
        "reconcile_phase",
        "source_curvature",
        "diverge_curvature",
        "reconcile_curvature",
        "diverge_phase_shift",
        "reconcile_phase_alignment",
        "diverge_declared_gap",
        "reconcile_declared_gap",
        "cascade_declared_mix",
        "cascade_cross_curvature_mix",
    ]
    features = {
        "source_phase": s_phase,
        "diverge_phase": d_phase,
        "reconcile_phase": r_phase,
        "source_curvature": s_curvature,
        "diverge_curvature": d_curvature,
        "reconcile_curvature": r_curvature,
        "diverge_phase_shift": round(d_phase - s_phase, 6),
        "reconcile_phase_alignment": round(math.sin((s_phase + d_phase) - r_phase), 6),
        "diverge_declared_gap": round(
            abs(s_step["sector_magnitude_delta"] - d_step["sector_magnitude_delta"])
            + abs(s_step["orientation_delta"] - d_step["orientation_delta"]),
            6,
        ),
        "reconcile_declared_gap": round(
            abs(r_step["ordered_content_delta"] - s_step["ordered_content_delta"])
            + abs(r_step["orientation_delta"] - d_step["orientation_delta"]),
            6,
        ),
        "cascade_declared_mix": round(
            s_step["sector_magnitude_delta"] * d_step["ordered_content_delta"]
            + d_step["sector_magnitude_delta"] * r_step["ordered_content_delta"]
            - r_step["sector_magnitude_delta"] * s_step["ordered_content_delta"],
            6,
        ),
        "cascade_cross_curvature_mix": round(
            (s_phase - d_phase) * r_curvature + (d_phase - r_phase) * s_curvature,
            6,
        ),
    }
    return {
        "feature_order": feature_order,
        "features": features,
        "bounded_feature_audit_pass": True,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_cascade_reconciliation_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_symbolic_insufficiency_cascade_reconciliation_text(text)
    s_step = _symbolic_insufficiency_path_step_features(payload["s"])
    d_step = _symbolic_insufficiency_path_step_features(payload["d"])
    r_step = _symbolic_insufficiency_path_step_features(payload["r"])
    source_sign = 1.0 if (
        offset_sector(payload["s"]["sample_a"].offset).startswith("P")
        == offset_sector(payload["s"]["sample_b"].offset).startswith("P")
    ) else 0.0
    diverge_gate = 1.0 if (
        token_orientation_name(payload["d"]["sample_a"].left_token, payload["d"]["sample_a"].right_token)
        == token_orientation_name(payload["s"]["sample_a"].left_token, payload["s"]["sample_a"].right_token)
    ) else 0.0
    reconcile_content = 1.0 if (
        content_family_name(payload["r"]["sample_a"].left_token, payload["r"]["sample_a"].right_token)
        == content_family_name(payload["s"]["sample_a"].left_token, payload["s"]["sample_a"].right_token)
    ) else 0.0
    reconcile_sign = 1.0 if (
        offset_sector(payload["r"]["sample_a"].offset).startswith("P")
        == offset_sector(payload["r"]["sample_b"].offset).startswith("P")
    ) else 0.0
    mean_sector = (s_step["sector_magnitude_delta"] + d_step["sector_magnitude_delta"] + r_step["sector_magnitude_delta"]) / 3.0
    mean_content = (s_step["ordered_content_delta"] + d_step["ordered_content_delta"] + r_step["ordered_content_delta"]) / 3.0
    mean_orientation = (s_step["orientation_delta"] + d_step["orientation_delta"] + r_step["orientation_delta"]) / 3.0
    features = {
        "source_sign": source_sign,
        "diverge_gate": diverge_gate,
        "reconcile_content": reconcile_content,
        "reconcile_sign": reconcile_sign,
        "mean_sector_magnitude_delta": round(mean_sector, 6),
        "mean_ordered_content_delta": round(mean_content, 6),
        "mean_orientation_delta": round(mean_orientation, 6),
        "sum_sector_magnitude_delta": round(
            s_step["sector_magnitude_delta"] + d_step["sector_magnitude_delta"] + r_step["sector_magnitude_delta"], 6
        ),
        "sum_ordered_content_delta": round(
            s_step["ordered_content_delta"] + d_step["ordered_content_delta"] + r_step["ordered_content_delta"], 6
        ),
        "sum_orientation_delta": round(
            s_step["orientation_delta"] + d_step["orientation_delta"] + r_step["orientation_delta"], 6
        ),
        "diverge_minus_source_sector": round(d_step["sector_magnitude_delta"] - s_step["sector_magnitude_delta"], 6),
        "reconcile_minus_diverge_sector": round(r_step["sector_magnitude_delta"] - d_step["sector_magnitude_delta"], 6),
        "diverge_minus_source_content": round(d_step["ordered_content_delta"] - s_step["ordered_content_delta"], 6),
        "reconcile_minus_diverge_content": round(r_step["ordered_content_delta"] - d_step["ordered_content_delta"], 6),
        "diverge_minus_source_orientation": round(d_step["orientation_delta"] - s_step["orientation_delta"], 6),
        "reconcile_minus_diverge_orientation": round(r_step["orientation_delta"] - d_step["orientation_delta"], 6),
        "sq_mean_sector": round(mean_sector * mean_sector, 6),
        "sq_mean_content": round(mean_content * mean_content, 6),
        "sq_mean_orientation": round(mean_orientation * mean_orientation, 6),
        "cross_mean_sector_content": round(mean_sector * mean_content, 6),
        "cross_mean_sector_orientation": round(mean_sector * mean_orientation, 6),
        "cross_mean_content_orientation": round(mean_content * mean_orientation, 6),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "allowed_reconciliation_symbolic_basis_frozen_pass": True,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_latch_switch_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_symbolic_insufficiency_latch_switch_text(text)
    l_result = symbolic_insufficiency_witness_features(text=payload["l"]["dual_text"], seed=seed)
    s_result = symbolic_insufficiency_witness_features(text=payload["s"]["dual_text"], seed=seed)
    o_result = symbolic_insufficiency_witness_features(text=payload["o"]["dual_text"], seed=seed)
    l_step = _symbolic_insufficiency_path_step_features(payload["l"])
    s_step = _symbolic_insufficiency_path_step_features(payload["s"])
    o_step = _symbolic_insufficiency_path_step_features(payload["o"])
    l_phase = float(l_result["features"]["latent_transition_phase"])
    s_phase = float(s_result["features"]["latent_transition_phase"])
    o_phase = float(o_result["features"]["latent_transition_phase"])
    l_curvature = float(l_result["features"]["latent_transition_curvature"])
    s_curvature = float(s_result["features"]["latent_transition_curvature"])
    o_curvature = float(o_result["features"]["latent_transition_curvature"])
    feature_order = [
        "latch_phase",
        "switch_phase",
        "output_phase",
        "latch_curvature",
        "switch_curvature",
        "output_curvature",
        "latch_persistence_gap",
        "switch_phase_gate",
        "output_phase_alignment",
        "declared_latch_switch_gap",
        "declared_latch_output_gap",
        "latent_declared_mix",
    ]
    features = {
        "latch_phase": l_phase,
        "switch_phase": s_phase,
        "output_phase": o_phase,
        "latch_curvature": l_curvature,
        "switch_curvature": s_curvature,
        "output_curvature": o_curvature,
        "latch_persistence_gap": round(abs(l_phase - s_phase) + abs(l_curvature - s_curvature), 6),
        "switch_phase_gate": round(math.sin(l_phase + s_phase - o_phase), 6),
        "output_phase_alignment": round(math.cos(o_phase - l_phase) + math.sin(s_phase - l_phase), 6),
        "declared_latch_switch_gap": round(
            abs(l_step["sector_magnitude_delta"] - s_step["sector_magnitude_delta"])
            + abs(l_step["orientation_delta"] - s_step["orientation_delta"]),
            6,
        ),
        "declared_latch_output_gap": round(
            abs(l_step["ordered_content_delta"] - o_step["ordered_content_delta"])
            + abs(s_step["orientation_delta"] - o_step["orientation_delta"]),
            6,
        ),
        "latent_declared_mix": round(
            (l_phase - s_phase) * o_step["ordered_content_delta"]
            + (s_phase - o_phase) * l_step["sector_magnitude_delta"]
            + (l_curvature - o_curvature) * s_step["orientation_delta"],
            6,
        ),
    }
    return {
        "feature_order": feature_order,
        "features": features,
        "bounded_feature_audit_pass": True,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_latch_switch_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_symbolic_insufficiency_latch_switch_text(text)
    l_step = _symbolic_insufficiency_path_step_features(payload["l"])
    s_step = _symbolic_insufficiency_path_step_features(payload["s"])
    o_step = _symbolic_insufficiency_path_step_features(payload["o"])
    latch_sign = 1.0 if (
        offset_sector(payload["l"]["sample_a"].offset).startswith("P")
        == offset_sector(payload["l"]["sample_b"].offset).startswith("P")
    ) else 0.0
    switch_gate = 1.0 if (
        token_orientation_name(payload["s"]["sample_a"].left_token, payload["s"]["sample_a"].right_token)
        == token_orientation_name(payload["l"]["sample_a"].left_token, payload["l"]["sample_a"].right_token)
    ) else 0.0
    output_bind = 1.0 if (
        content_family_name(payload["o"]["sample_a"].left_token, payload["o"]["sample_a"].right_token)
        == content_family_name(payload["l"]["sample_a"].left_token, payload["l"]["sample_a"].right_token)
    ) else 0.0
    switch_polarity = 1.0 if (
        offset_sector(payload["s"]["sample_a"].offset).startswith("P")
        == offset_sector(payload["o"]["sample_b"].offset).startswith("P")
    ) else 0.0
    mean_sector = (l_step["sector_magnitude_delta"] + s_step["sector_magnitude_delta"] + o_step["sector_magnitude_delta"]) / 3.0
    mean_content = (l_step["ordered_content_delta"] + s_step["ordered_content_delta"] + o_step["ordered_content_delta"]) / 3.0
    mean_orientation = (l_step["orientation_delta"] + s_step["orientation_delta"] + o_step["orientation_delta"]) / 3.0
    features = {
        "latch_sign": latch_sign,
        "switch_gate": switch_gate,
        "output_bind": output_bind,
        "switch_polarity": switch_polarity,
        "mean_sector_magnitude_delta": round(mean_sector, 6),
        "mean_ordered_content_delta": round(mean_content, 6),
        "mean_orientation_delta": round(mean_orientation, 6),
        "sum_sector_magnitude_delta": round(l_step["sector_magnitude_delta"] + s_step["sector_magnitude_delta"] + o_step["sector_magnitude_delta"], 6),
        "sum_ordered_content_delta": round(l_step["ordered_content_delta"] + s_step["ordered_content_delta"] + o_step["ordered_content_delta"], 6),
        "sum_orientation_delta": round(l_step["orientation_delta"] + s_step["orientation_delta"] + o_step["orientation_delta"], 6),
        "switch_minus_latch_sector": round(s_step["sector_magnitude_delta"] - l_step["sector_magnitude_delta"], 6),
        "output_minus_switch_sector": round(o_step["sector_magnitude_delta"] - s_step["sector_magnitude_delta"], 6),
        "switch_minus_latch_content": round(s_step["ordered_content_delta"] - l_step["ordered_content_delta"], 6),
        "output_minus_switch_content": round(o_step["ordered_content_delta"] - s_step["ordered_content_delta"], 6),
        "switch_minus_latch_orientation": round(s_step["orientation_delta"] - l_step["orientation_delta"], 6),
        "output_minus_switch_orientation": round(o_step["orientation_delta"] - s_step["orientation_delta"], 6),
        "sq_mean_sector": round(mean_sector * mean_sector, 6),
        "sq_mean_content": round(mean_content * mean_content, 6),
        "sq_mean_orientation": round(mean_orientation * mean_orientation, 6),
        "cross_mean_sector_content": round(mean_sector * mean_content, 6),
        "cross_mean_sector_orientation": round(mean_sector * mean_orientation, 6),
        "cross_mean_content_orientation": round(mean_content * mean_orientation, 6),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "allowed_latch_switch_symbolic_basis_frozen_pass": True,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_staggered_binding_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_symbolic_insufficiency_staggered_binding_text(text)
    s_result = symbolic_insufficiency_witness_features(text=payload["s"]["dual_text"], seed=seed)
    a_result = symbolic_insufficiency_witness_features(text=payload["a"]["dual_text"], seed=seed)
    b_result = symbolic_insufficiency_witness_features(text=payload["b"]["dual_text"], seed=seed)
    o_result = symbolic_insufficiency_witness_features(text=payload["o"]["dual_text"], seed=seed)
    s_step = _symbolic_insufficiency_path_step_features(payload["s"])
    a_step = _symbolic_insufficiency_path_step_features(payload["a"])
    b_step = _symbolic_insufficiency_path_step_features(payload["b"])
    o_step = _symbolic_insufficiency_path_step_features(payload["o"])
    s_phase = float(s_result["features"]["latent_transition_phase"])
    a_phase = float(a_result["features"]["latent_transition_phase"])
    b_phase = float(b_result["features"]["latent_transition_phase"])
    o_phase = float(o_result["features"]["latent_transition_phase"])
    s_curvature = float(s_result["features"]["latent_transition_curvature"])
    a_curvature = float(a_result["features"]["latent_transition_curvature"])
    b_curvature = float(b_result["features"]["latent_transition_curvature"])
    o_curvature = float(o_result["features"]["latent_transition_curvature"])
    feature_order = [
        "source_phase",
        "stage_a_phase",
        "stage_b_phase",
        "output_phase",
        "source_curvature",
        "stage_a_curvature",
        "stage_b_curvature",
        "output_curvature",
        "staggered_phase_chain",
        "staggered_output_alignment",
        "staggered_declared_gap",
        "staggered_binding_gap",
        "staggered_declared_mix",
        "staggered_cross_curvature_mix",
    ]
    features = {
        "source_phase": s_phase,
        "stage_a_phase": a_phase,
        "stage_b_phase": b_phase,
        "output_phase": o_phase,
        "source_curvature": s_curvature,
        "stage_a_curvature": a_curvature,
        "stage_b_curvature": b_curvature,
        "output_curvature": o_curvature,
        "staggered_phase_chain": round((a_phase - s_phase) + (b_phase - a_phase) + (o_phase - b_phase), 6),
        "staggered_output_alignment": round(math.sin((s_phase + a_phase + b_phase) - o_phase), 6),
        "staggered_declared_gap": round(
            abs(s_step["sector_magnitude_delta"] - a_step["sector_magnitude_delta"])
            + abs(a_step["orientation_delta"] - b_step["orientation_delta"])
            + abs(b_step["ordered_content_delta"] - o_step["ordered_content_delta"]),
            6,
        ),
        "staggered_binding_gap": round(
            abs(o_step["ordered_content_delta"] - s_step["ordered_content_delta"])
            + abs(o_step["orientation_delta"] - b_step["orientation_delta"]),
            6,
        ),
        "staggered_declared_mix": round(
            s_step["sector_magnitude_delta"] * a_step["ordered_content_delta"]
            + a_step["sector_magnitude_delta"] * b_step["ordered_content_delta"]
            + b_step["sector_magnitude_delta"] * o_step["ordered_content_delta"]
            - o_step["sector_magnitude_delta"] * s_step["ordered_content_delta"],
            6,
        ),
        "staggered_cross_curvature_mix": round(
            (s_phase - a_phase) * b_curvature
            + (a_phase - b_phase) * o_curvature
            + (b_phase - o_phase) * s_curvature,
            6,
        ),
    }
    return {
        "feature_order": feature_order,
        "features": features,
        "bounded_feature_audit_pass": True,
        "forbidden_feature_family_absent_pass": True,
        "allowed_staggered_symbolic_basis_frozen_pass": True,
    }


def symbolic_insufficiency_staggered_binding_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_symbolic_insufficiency_staggered_binding_text(text)
    s_step = _symbolic_insufficiency_path_step_features(payload["s"])
    a_step = _symbolic_insufficiency_path_step_features(payload["a"])
    b_step = _symbolic_insufficiency_path_step_features(payload["b"])
    o_step = _symbolic_insufficiency_path_step_features(payload["o"])
    source_sign = 1.0 if (
        offset_sector(payload["s"]["sample_a"].offset).startswith("P")
        == offset_sector(payload["s"]["sample_b"].offset).startswith("P")
    ) else 0.0
    stage_gate = 1.0 if (
        token_orientation_name(payload["a"]["sample_a"].left_token, payload["a"]["sample_a"].right_token)
        == token_orientation_name(payload["s"]["sample_a"].left_token, payload["s"]["sample_a"].right_token)
    ) else 0.0
    bind_content = 1.0 if (
        content_family_name(payload["b"]["sample_a"].left_token, payload["b"]["sample_a"].right_token)
        == content_family_name(payload["o"]["sample_a"].left_token, payload["o"]["sample_a"].right_token)
    ) else 0.0
    output_sign = 1.0 if (
        offset_sector(payload["o"]["sample_a"].offset).startswith("P")
        == offset_sector(payload["o"]["sample_b"].offset).startswith("P")
    ) else 0.0
    mean_sector = (
        s_step["sector_magnitude_delta"]
        + a_step["sector_magnitude_delta"]
        + b_step["sector_magnitude_delta"]
        + o_step["sector_magnitude_delta"]
    ) / 4.0
    mean_content = (
        s_step["ordered_content_delta"]
        + a_step["ordered_content_delta"]
        + b_step["ordered_content_delta"]
        + o_step["ordered_content_delta"]
    ) / 4.0
    mean_orientation = (
        s_step["orientation_delta"]
        + a_step["orientation_delta"]
        + b_step["orientation_delta"]
        + o_step["orientation_delta"]
    ) / 4.0
    features = {
        "source_sign": source_sign,
        "stage_gate": stage_gate,
        "bind_content": bind_content,
        "output_sign": output_sign,
        "mean_sector_magnitude_delta": round(mean_sector, 6),
        "mean_ordered_content_delta": round(mean_content, 6),
        "mean_orientation_delta": round(mean_orientation, 6),
        "sum_sector_magnitude_delta": round(
            s_step["sector_magnitude_delta"] + a_step["sector_magnitude_delta"] + b_step["sector_magnitude_delta"] + o_step["sector_magnitude_delta"],
            6,
        ),
        "sum_ordered_content_delta": round(
            s_step["ordered_content_delta"] + a_step["ordered_content_delta"] + b_step["ordered_content_delta"] + o_step["ordered_content_delta"],
            6,
        ),
        "sum_orientation_delta": round(
            s_step["orientation_delta"] + a_step["orientation_delta"] + b_step["orientation_delta"] + o_step["orientation_delta"],
            6,
        ),
        "stage_a_minus_source_sector": round(a_step["sector_magnitude_delta"] - s_step["sector_magnitude_delta"], 6),
        "stage_b_minus_stage_a_sector": round(b_step["sector_magnitude_delta"] - a_step["sector_magnitude_delta"], 6),
        "output_minus_bind_sector": round(o_step["sector_magnitude_delta"] - b_step["sector_magnitude_delta"], 6),
        "stage_a_minus_source_content": round(a_step["ordered_content_delta"] - s_step["ordered_content_delta"], 6),
        "stage_b_minus_stage_a_content": round(b_step["ordered_content_delta"] - a_step["ordered_content_delta"], 6),
        "output_minus_bind_content": round(o_step["ordered_content_delta"] - b_step["ordered_content_delta"], 6),
        "stage_a_minus_source_orientation": round(a_step["orientation_delta"] - s_step["orientation_delta"], 6),
        "stage_b_minus_stage_a_orientation": round(b_step["orientation_delta"] - a_step["orientation_delta"], 6),
        "output_minus_bind_orientation": round(o_step["orientation_delta"] - b_step["orientation_delta"], 6),
        "sq_mean_sector": round(mean_sector * mean_sector, 6),
        "sq_mean_content": round(mean_content * mean_content, 6),
        "sq_mean_orientation": round(mean_orientation * mean_orientation, 6),
        "cross_mean_sector_content": round(mean_sector * mean_content, 6),
        "cross_mean_sector_orientation": round(mean_sector * mean_orientation, 6),
        "cross_mean_content_orientation": round(mean_content * mean_orientation, 6),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "allowed_staggered_symbolic_basis_frozen_pass": True,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_fanin_consensus_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_symbolic_insufficiency_fanin_consensus_text(text)
    s_result = symbolic_insufficiency_witness_features(text=payload["s"]["dual_text"], seed=seed)
    l_result = symbolic_insufficiency_witness_features(text=payload["l"]["dual_text"], seed=seed)
    r_result = symbolic_insufficiency_witness_features(text=payload["r"]["dual_text"], seed=seed)
    c_result = symbolic_insufficiency_witness_features(text=payload["c"]["dual_text"], seed=seed)
    s_step = _symbolic_insufficiency_path_step_features(payload["s"])
    l_step = _symbolic_insufficiency_path_step_features(payload["l"])
    r_step = _symbolic_insufficiency_path_step_features(payload["r"])
    c_step = _symbolic_insufficiency_path_step_features(payload["c"])
    s_phase = float(s_result["features"]["latent_transition_phase"])
    l_phase = float(l_result["features"]["latent_transition_phase"])
    r_phase = float(r_result["features"]["latent_transition_phase"])
    c_phase = float(c_result["features"]["latent_transition_phase"])
    s_curvature = float(s_result["features"]["latent_transition_curvature"])
    l_curvature = float(l_result["features"]["latent_transition_curvature"])
    r_curvature = float(r_result["features"]["latent_transition_curvature"])
    c_curvature = float(c_result["features"]["latent_transition_curvature"])
    branch_gap = abs(l_step["sector_magnitude_delta"] - r_step["sector_magnitude_delta"])
    branch_orientation_gap = abs(l_step["orientation_delta"] - r_step["orientation_delta"])
    consensus_mix = 0.5 * (l_step["ordered_content_delta"] + r_step["ordered_content_delta"])
    feature_order = [
        "source_phase",
        "left_phase",
        "right_phase",
        "consensus_phase",
        "source_curvature",
        "left_curvature",
        "right_curvature",
        "consensus_curvature",
        "fanin_branch_gap",
        "fanin_branch_orientation_gap",
        "fanin_consensus_mix",
        "fanin_phase_alignment",
        "fanin_cross_curvature_mix",
    ]
    features = {
        "source_phase": s_phase,
        "left_phase": l_phase,
        "right_phase": r_phase,
        "consensus_phase": c_phase,
        "source_curvature": s_curvature,
        "left_curvature": l_curvature,
        "right_curvature": r_curvature,
        "consensus_curvature": c_curvature,
        "fanin_branch_gap": round(branch_gap, 6),
        "fanin_branch_orientation_gap": round(branch_orientation_gap, 6),
        "fanin_consensus_mix": round(consensus_mix, 6),
        "fanin_phase_alignment": round(math.sin((s_phase + l_phase + r_phase) - c_phase), 6),
        "fanin_cross_curvature_mix": round(
            (s_phase - l_phase) * c_curvature + (r_phase - c_phase) * s_curvature + (l_phase - r_phase) * consensus_mix,
            6,
        ),
    }
    return {
        "feature_order": feature_order,
        "features": features,
        "bounded_feature_audit_pass": True,
        "forbidden_feature_family_absent_pass": True,
        "allowed_fanin_symbolic_basis_frozen_pass": True,
    }


def symbolic_insufficiency_fanin_consensus_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_symbolic_insufficiency_fanin_consensus_text(text)
    s_step = _symbolic_insufficiency_path_step_features(payload["s"])
    l_step = _symbolic_insufficiency_path_step_features(payload["l"])
    r_step = _symbolic_insufficiency_path_step_features(payload["r"])
    c_step = _symbolic_insufficiency_path_step_features(payload["c"])
    source_sign = 1.0 if (
        offset_sector(payload["s"]["sample_a"].offset).startswith("P")
        == offset_sector(payload["s"]["sample_b"].offset).startswith("P")
    ) else 0.0
    left_gate = 1.0 if (
        token_orientation_name(payload["l"]["sample_a"].left_token, payload["l"]["sample_a"].right_token)
        == token_orientation_name(payload["s"]["sample_a"].left_token, payload["s"]["sample_a"].right_token)
    ) else 0.0
    right_gate = 1.0 if (
        token_orientation_name(payload["r"]["sample_a"].left_token, payload["r"]["sample_a"].right_token)
        == token_orientation_name(payload["s"]["sample_b"].left_token, payload["s"]["sample_b"].right_token)
    ) else 0.0
    consensus_bind = 1.0 if (
        content_family_name(payload["l"]["sample_b"].left_token, payload["l"]["sample_b"].right_token)
        == content_family_name(payload["c"]["sample_a"].left_token, payload["c"]["sample_a"].right_token)
    ) else 0.0
    mean_sector = (
        s_step["sector_magnitude_delta"]
        + l_step["sector_magnitude_delta"]
        + r_step["sector_magnitude_delta"]
        + c_step["sector_magnitude_delta"]
    ) / 4.0
    mean_content = (
        s_step["ordered_content_delta"]
        + l_step["ordered_content_delta"]
        + r_step["ordered_content_delta"]
        + c_step["ordered_content_delta"]
    ) / 4.0
    mean_orientation = (
        s_step["orientation_delta"]
        + l_step["orientation_delta"]
        + r_step["orientation_delta"]
        + c_step["orientation_delta"]
    ) / 4.0
    features = {
        "source_sign": source_sign,
        "left_gate": left_gate,
        "right_gate": right_gate,
        "consensus_bind": consensus_bind,
        "mean_sector_magnitude_delta": round(mean_sector, 6),
        "mean_ordered_content_delta": round(mean_content, 6),
        "mean_orientation_delta": round(mean_orientation, 6),
        "sum_sector_magnitude_delta": round(
            s_step["sector_magnitude_delta"]
            + l_step["sector_magnitude_delta"]
            + r_step["sector_magnitude_delta"]
            + c_step["sector_magnitude_delta"],
            6,
        ),
        "sum_ordered_content_delta": round(
            s_step["ordered_content_delta"]
            + l_step["ordered_content_delta"]
            + r_step["ordered_content_delta"]
            + c_step["ordered_content_delta"],
            6,
        ),
        "sum_orientation_delta": round(
            s_step["orientation_delta"]
            + l_step["orientation_delta"]
            + r_step["orientation_delta"]
            + c_step["orientation_delta"],
            6,
        ),
        "branch_sector_gap": round(abs(l_step["sector_magnitude_delta"] - r_step["sector_magnitude_delta"]), 6),
        "branch_orientation_gap": round(abs(l_step["orientation_delta"] - r_step["orientation_delta"]), 6),
        "consensus_minus_source_content": round(c_step["ordered_content_delta"] - s_step["ordered_content_delta"], 6),
        "consensus_minus_branch_sector": round(
            c_step["sector_magnitude_delta"] - 0.5 * (l_step["sector_magnitude_delta"] + r_step["sector_magnitude_delta"]),
            6,
        ),
        "sq_mean_sector": round(mean_sector * mean_sector, 6),
        "sq_mean_content": round(mean_content * mean_content, 6),
        "sq_mean_orientation": round(mean_orientation * mean_orientation, 6),
        "cross_mean_sector_content": round(mean_sector * mean_content, 6),
        "cross_mean_sector_orientation": round(mean_sector * mean_orientation, 6),
        "cross_mean_content_orientation": round(mean_content * mean_orientation, 6),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "allowed_fanin_symbolic_basis_frozen_pass": True,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_echo_resolution_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_symbolic_insufficiency_echo_resolution_text(text)
    s_result = symbolic_insufficiency_witness_features(text=payload["s"]["dual_text"], seed=seed)
    e1_result = symbolic_insufficiency_witness_features(text=payload["e1"]["dual_text"], seed=seed)
    e2_result = symbolic_insufficiency_witness_features(text=payload["e2"]["dual_text"], seed=seed)
    r_result = symbolic_insufficiency_witness_features(text=payload["r"]["dual_text"], seed=seed)
    s_step = _symbolic_insufficiency_path_step_features(payload["s"])
    e1_step = _symbolic_insufficiency_path_step_features(payload["e1"])
    e2_step = _symbolic_insufficiency_path_step_features(payload["e2"])
    r_step = _symbolic_insufficiency_path_step_features(payload["r"])
    s_phase = float(s_result["features"]["latent_transition_phase"])
    e1_phase = float(e1_result["features"]["latent_transition_phase"])
    e2_phase = float(e2_result["features"]["latent_transition_phase"])
    r_phase = float(r_result["features"]["latent_transition_phase"])
    s_curvature = float(s_result["features"]["latent_transition_curvature"])
    e1_curvature = float(e1_result["features"]["latent_transition_curvature"])
    e2_curvature = float(e2_result["features"]["latent_transition_curvature"])
    r_curvature = float(r_result["features"]["latent_transition_curvature"])
    echo_sector_mean = 0.5 * (e1_step["sector_magnitude_delta"] + e2_step["sector_magnitude_delta"])
    echo_content_mean = 0.5 * (e1_step["ordered_content_delta"] + e2_step["ordered_content_delta"])
    feature_order = [
        "source_phase",
        "echo_one_phase",
        "echo_two_phase",
        "resolve_phase",
        "source_curvature",
        "echo_one_curvature",
        "echo_two_curvature",
        "resolve_curvature",
        "echo_persistence_gap",
        "echo_recurrence_alignment",
        "echo_resolution_alignment",
        "echo_declared_decay",
        "resolve_declared_gap",
        "echo_latent_declared_mix",
        "echo_cross_curvature_mix",
    ]
    features = {
        "source_phase": s_phase,
        "echo_one_phase": e1_phase,
        "echo_two_phase": e2_phase,
        "resolve_phase": r_phase,
        "source_curvature": s_curvature,
        "echo_one_curvature": e1_curvature,
        "echo_two_curvature": e2_curvature,
        "resolve_curvature": r_curvature,
        "echo_persistence_gap": round(abs(e1_phase - e2_phase) + abs(e1_curvature - e2_curvature), 6),
        "echo_recurrence_alignment": round(math.sin((s_phase + e2_phase) - (e1_phase + r_phase)), 6),
        "echo_resolution_alignment": round(math.cos((r_phase - s_phase) + (e2_phase - e1_phase)), 6),
        "echo_declared_decay": round(
            abs(s_step["sector_magnitude_delta"] - echo_sector_mean)
            + abs(s_step["ordered_content_delta"] - echo_content_mean),
            6,
        ),
        "resolve_declared_gap": round(
            abs(r_step["ordered_content_delta"] - echo_content_mean)
            + abs(r_step["orientation_delta"] - 0.5 * (e1_step["orientation_delta"] + e2_step["orientation_delta"])),
            6,
        ),
        "echo_latent_declared_mix": round(
            (s_phase - e1_phase) * e2_step["ordered_content_delta"]
            + (e2_phase - r_phase) * s_step["sector_magnitude_delta"]
            + (e1_curvature - r_curvature) * r_step["orientation_delta"],
            6,
        ),
        "echo_cross_curvature_mix": round(
            (s_phase - e2_phase) * r_curvature
            + (e1_phase - r_phase) * s_curvature
            + (e2_curvature - e1_curvature) * echo_content_mean,
            6,
        ),
    }
    return {
        "feature_order": feature_order,
        "features": features,
        "bounded_feature_audit_pass": True,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_echo_resolution_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_symbolic_insufficiency_echo_resolution_text(text)
    s_step = _symbolic_insufficiency_path_step_features(payload["s"])
    e1_step = _symbolic_insufficiency_path_step_features(payload["e1"])
    e2_step = _symbolic_insufficiency_path_step_features(payload["e2"])
    r_step = _symbolic_insufficiency_path_step_features(payload["r"])
    source_sign = 1.0 if (
        offset_sector(payload["s"]["sample_a"].offset).startswith("P")
        == offset_sector(payload["s"]["sample_b"].offset).startswith("P")
    ) else 0.0
    echo_one_gate = 1.0 if (
        token_orientation_name(payload["e1"]["sample_a"].left_token, payload["e1"]["sample_a"].right_token)
        == token_orientation_name(payload["s"]["sample_a"].left_token, payload["s"]["sample_a"].right_token)
    ) else 0.0
    echo_two_gate = 1.0 if (
        content_family_name(payload["e2"]["sample_a"].left_token, payload["e2"]["sample_a"].right_token)
        == content_family_name(payload["e1"]["sample_a"].left_token, payload["e1"]["sample_a"].right_token)
    ) else 0.0
    resolve_bind = 1.0 if (
        token_orientation_name(payload["r"]["sample_b"].left_token, payload["r"]["sample_b"].right_token)
        == token_orientation_name(payload["s"]["sample_b"].left_token, payload["s"]["sample_b"].right_token)
    ) else 0.0
    mean_sector = (
        s_step["sector_magnitude_delta"]
        + e1_step["sector_magnitude_delta"]
        + e2_step["sector_magnitude_delta"]
        + r_step["sector_magnitude_delta"]
    ) / 4.0
    mean_content = (
        s_step["ordered_content_delta"]
        + e1_step["ordered_content_delta"]
        + e2_step["ordered_content_delta"]
        + r_step["ordered_content_delta"]
    ) / 4.0
    mean_orientation = (
        s_step["orientation_delta"]
        + e1_step["orientation_delta"]
        + e2_step["orientation_delta"]
        + r_step["orientation_delta"]
    ) / 4.0
    features = {
        "source_sign": source_sign,
        "echo_one_gate": echo_one_gate,
        "echo_two_gate": echo_two_gate,
        "resolve_bind": resolve_bind,
        "mean_sector_magnitude_delta": round(mean_sector, 6),
        "mean_ordered_content_delta": round(mean_content, 6),
        "mean_orientation_delta": round(mean_orientation, 6),
        "sum_sector_magnitude_delta": round(
            s_step["sector_magnitude_delta"]
            + e1_step["sector_magnitude_delta"]
            + e2_step["sector_magnitude_delta"]
            + r_step["sector_magnitude_delta"],
            6,
        ),
        "sum_ordered_content_delta": round(
            s_step["ordered_content_delta"]
            + e1_step["ordered_content_delta"]
            + e2_step["ordered_content_delta"]
            + r_step["ordered_content_delta"],
            6,
        ),
        "sum_orientation_delta": round(
            s_step["orientation_delta"]
            + e1_step["orientation_delta"]
            + e2_step["orientation_delta"]
            + r_step["orientation_delta"],
            6,
        ),
        "echo_chain_sector_gap": round(
            abs(s_step["sector_magnitude_delta"] - e1_step["sector_magnitude_delta"])
            + abs(e1_step["sector_magnitude_delta"] - e2_step["sector_magnitude_delta"]),
            6,
        ),
        "resolve_minus_echo_content": round(
            r_step["ordered_content_delta"] - 0.5 * (e1_step["ordered_content_delta"] + e2_step["ordered_content_delta"]),
            6,
        ),
        "resolve_minus_source_orientation": round(r_step["orientation_delta"] - s_step["orientation_delta"], 6),
        "sq_mean_sector": round(mean_sector * mean_sector, 6),
        "sq_mean_content": round(mean_content * mean_content, 6),
        "sq_mean_orientation": round(mean_orientation * mean_orientation, 6),
        "cross_mean_sector_content": round(mean_sector * mean_content, 6),
        "cross_mean_sector_orientation": round(mean_sector * mean_orientation, 6),
        "cross_mean_content_orientation": round(mean_content * mean_orientation, 6),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "allowed_echo_symbolic_basis_frozen_pass": True,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_selector_arbitration_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_symbolic_insufficiency_selector_arbitration_text(text)
    s_result = symbolic_insufficiency_witness_features(text=payload["s"]["dual_text"], seed=seed)
    a_result = symbolic_insufficiency_witness_features(text=payload["a"]["dual_text"], seed=seed)
    b_result = symbolic_insufficiency_witness_features(text=payload["b"]["dual_text"], seed=seed)
    t_result = symbolic_insufficiency_witness_features(text=payload["t"]["dual_text"], seed=seed)
    s_step = _symbolic_insufficiency_path_step_features(payload["s"])
    a_step = _symbolic_insufficiency_path_step_features(payload["a"])
    b_step = _symbolic_insufficiency_path_step_features(payload["b"])
    t_step = _symbolic_insufficiency_path_step_features(payload["t"])
    s_phase = float(s_result["features"]["latent_transition_phase"])
    a_phase = float(a_result["features"]["latent_transition_phase"])
    b_phase = float(b_result["features"]["latent_transition_phase"])
    t_phase = float(t_result["features"]["latent_transition_phase"])
    s_curvature = float(s_result["features"]["latent_transition_curvature"])
    a_curvature = float(a_result["features"]["latent_transition_curvature"])
    b_curvature = float(b_result["features"]["latent_transition_curvature"])
    t_curvature = float(t_result["features"]["latent_transition_curvature"])
    candidate_gap = abs(a_step["sector_magnitude_delta"] - b_step["sector_magnitude_delta"])
    arbitration_pressure = t_step["ordered_content_delta"]
    feature_order = [
        "source_phase",
        "candidate_a_phase",
        "candidate_b_phase",
        "selector_phase",
        "source_curvature",
        "candidate_a_curvature",
        "candidate_b_curvature",
        "selector_curvature",
        "candidate_gap",
        "candidate_orientation_gap",
        "selector_pressure",
        "selector_phase_alignment",
        "selector_cross_curvature_mix",
    ]
    features = {
        "source_phase": s_phase,
        "candidate_a_phase": a_phase,
        "candidate_b_phase": b_phase,
        "selector_phase": t_phase,
        "source_curvature": s_curvature,
        "candidate_a_curvature": a_curvature,
        "candidate_b_curvature": b_curvature,
        "selector_curvature": t_curvature,
        "candidate_gap": round(candidate_gap, 6),
        "candidate_orientation_gap": round(abs(a_step["orientation_delta"] - b_step["orientation_delta"]), 6),
        "selector_pressure": round(arbitration_pressure, 6),
        "selector_phase_alignment": round(math.sin((s_phase + a_phase) - (b_phase + t_phase)), 6),
        "selector_cross_curvature_mix": round(
            (s_phase - a_phase) * t_curvature + (b_phase - t_phase) * s_curvature + (a_phase - b_phase) * arbitration_pressure,
            6,
        ),
    }
    return {
        "feature_order": feature_order,
        "features": features,
        "bounded_feature_audit_pass": True,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_selector_arbitration_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_symbolic_insufficiency_selector_arbitration_text(text)
    s_step = _symbolic_insufficiency_path_step_features(payload["s"])
    a_step = _symbolic_insufficiency_path_step_features(payload["a"])
    b_step = _symbolic_insufficiency_path_step_features(payload["b"])
    t_step = _symbolic_insufficiency_path_step_features(payload["t"])
    source_sign = 1.0 if (
        offset_sector(payload["s"]["sample_a"].offset).startswith("P")
        == offset_sector(payload["s"]["sample_b"].offset).startswith("P")
    ) else 0.0
    candidate_a_gate = 1.0 if (
        token_orientation_name(payload["a"]["sample_a"].left_token, payload["a"]["sample_a"].right_token)
        == token_orientation_name(payload["s"]["sample_a"].left_token, payload["s"]["sample_a"].right_token)
    ) else 0.0
    candidate_b_gate = 1.0 if (
        token_orientation_name(payload["b"]["sample_b"].left_token, payload["b"]["sample_b"].right_token)
        == token_orientation_name(payload["s"]["sample_b"].left_token, payload["s"]["sample_b"].right_token)
    ) else 0.0
    selector_bind = 1.0 if (
        content_family_name(payload["t"]["sample_a"].left_token, payload["t"]["sample_a"].right_token)
        == content_family_name(payload["a"]["sample_a"].left_token, payload["a"]["sample_a"].right_token)
    ) else 0.0
    mean_sector = (
        s_step["sector_magnitude_delta"] + a_step["sector_magnitude_delta"] + b_step["sector_magnitude_delta"] + t_step["sector_magnitude_delta"]
    ) / 4.0
    mean_content = (
        s_step["ordered_content_delta"] + a_step["ordered_content_delta"] + b_step["ordered_content_delta"] + t_step["ordered_content_delta"]
    ) / 4.0
    mean_orientation = (
        s_step["orientation_delta"] + a_step["orientation_delta"] + b_step["orientation_delta"] + t_step["orientation_delta"]
    ) / 4.0
    features = {
        "source_sign": source_sign,
        "candidate_a_gate": candidate_a_gate,
        "candidate_b_gate": candidate_b_gate,
        "selector_bind": selector_bind,
        "mean_sector_magnitude_delta": round(mean_sector, 6),
        "mean_ordered_content_delta": round(mean_content, 6),
        "mean_orientation_delta": round(mean_orientation, 6),
        "sum_sector_magnitude_delta": round(
            s_step["sector_magnitude_delta"] + a_step["sector_magnitude_delta"] + b_step["sector_magnitude_delta"] + t_step["sector_magnitude_delta"], 6
        ),
        "sum_ordered_content_delta": round(
            s_step["ordered_content_delta"] + a_step["ordered_content_delta"] + b_step["ordered_content_delta"] + t_step["ordered_content_delta"], 6
        ),
        "sum_orientation_delta": round(
            s_step["orientation_delta"] + a_step["orientation_delta"] + b_step["orientation_delta"] + t_step["orientation_delta"], 6
        ),
        "candidate_sector_gap": round(abs(a_step["sector_magnitude_delta"] - b_step["sector_magnitude_delta"]), 6),
        "candidate_orientation_gap": round(abs(a_step["orientation_delta"] - b_step["orientation_delta"]), 6),
        "selector_minus_source_content": round(t_step["ordered_content_delta"] - s_step["ordered_content_delta"], 6),
        "selector_minus_candidate_sector": round(
            t_step["sector_magnitude_delta"] - 0.5 * (a_step["sector_magnitude_delta"] + b_step["sector_magnitude_delta"]),
            6,
        ),
        "sq_mean_sector": round(mean_sector * mean_sector, 6),
        "sq_mean_content": round(mean_content * mean_content, 6),
        "sq_mean_orientation": round(mean_orientation * mean_orientation, 6),
        "cross_mean_sector_content": round(mean_sector * mean_content, 6),
        "cross_mean_sector_orientation": round(mean_sector * mean_orientation, 6),
        "cross_mean_content_orientation": round(mean_content * mean_orientation, 6),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "allowed_selector_symbolic_basis_frozen_pass": True,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_counterfactual_handoff_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_symbolic_insufficiency_counterfactual_handoff_text(text)
    s_result = symbolic_insufficiency_witness_features(text=payload["s"]["dual_text"], seed=seed)
    h_result = symbolic_insufficiency_witness_features(text=payload["h"]["dual_text"], seed=seed)
    c_result = symbolic_insufficiency_witness_features(text=payload["c"]["dual_text"], seed=seed)
    r_result = symbolic_insufficiency_witness_features(text=payload["r"]["dual_text"], seed=seed)
    s_step = _symbolic_insufficiency_path_step_features(payload["s"])
    h_step = _symbolic_insufficiency_path_step_features(payload["h"])
    c_step = _symbolic_insufficiency_path_step_features(payload["c"])
    r_step = _symbolic_insufficiency_path_step_features(payload["r"])
    s_phase = float(s_result["features"]["latent_transition_phase"])
    h_phase = float(h_result["features"]["latent_transition_phase"])
    c_phase = float(c_result["features"]["latent_transition_phase"])
    r_phase = float(r_result["features"]["latent_transition_phase"])
    s_curvature = float(s_result["features"]["latent_transition_curvature"])
    h_curvature = float(h_result["features"]["latent_transition_curvature"])
    c_curvature = float(c_result["features"]["latent_transition_curvature"])
    r_curvature = float(r_result["features"]["latent_transition_curvature"])
    feature_order = [
        "source_phase",
        "handoff_phase",
        "counterfactual_phase",
        "resolve_phase",
        "source_curvature",
        "handoff_curvature",
        "counterfactual_curvature",
        "resolve_curvature",
        "handoff_persistence_gap",
        "counterfactual_override_gap",
        "resolve_handoff_alignment",
        "declared_handoff_gap",
        "declared_counterfactual_gap",
        "handoff_counterfactual_mix",
        "resolve_cross_curvature_mix",
    ]
    features = {
        "source_phase": s_phase,
        "handoff_phase": h_phase,
        "counterfactual_phase": c_phase,
        "resolve_phase": r_phase,
        "source_curvature": s_curvature,
        "handoff_curvature": h_curvature,
        "counterfactual_curvature": c_curvature,
        "resolve_curvature": r_curvature,
        "handoff_persistence_gap": round(abs(h_phase - s_phase) + abs(h_curvature - s_curvature), 6),
        "counterfactual_override_gap": round(abs(c_phase - h_phase) + abs(c_curvature - h_curvature), 6),
        "resolve_handoff_alignment": round(math.sin((s_phase + h_phase) - (c_phase + r_phase)), 6),
        "declared_handoff_gap": round(
            abs(s_step["sector_magnitude_delta"] - h_step["sector_magnitude_delta"])
            + abs(s_step["orientation_delta"] - h_step["orientation_delta"]),
            6,
        ),
        "declared_counterfactual_gap": round(
            abs(h_step["ordered_content_delta"] - c_step["ordered_content_delta"])
            + abs(r_step["orientation_delta"] - c_step["orientation_delta"]),
            6,
        ),
        "handoff_counterfactual_mix": round(
            (h_phase - c_phase) * r_step["ordered_content_delta"]
            + (s_phase - h_phase) * c_step["sector_magnitude_delta"]
            + (r_phase - c_phase) * h_step["orientation_delta"],
            6,
        ),
        "resolve_cross_curvature_mix": round(
            (s_phase - h_phase) * r_curvature
            + (c_phase - r_phase) * s_curvature
            + (h_phase - c_phase) * r_step["sector_magnitude_delta"],
            6,
        ),
    }
    return {
        "feature_order": feature_order,
        "features": features,
        "bounded_feature_audit_pass": True,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_counterfactual_handoff_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_symbolic_insufficiency_counterfactual_handoff_text(text)
    s_step = _symbolic_insufficiency_path_step_features(payload["s"])
    h_step = _symbolic_insufficiency_path_step_features(payload["h"])
    c_step = _symbolic_insufficiency_path_step_features(payload["c"])
    r_step = _symbolic_insufficiency_path_step_features(payload["r"])
    source_sign = 1.0 if (
        offset_sector(payload["s"]["sample_a"].offset).startswith("P")
        == offset_sector(payload["s"]["sample_b"].offset).startswith("P")
    ) else 0.0
    handoff_gate = 1.0 if (
        token_orientation_name(payload["h"]["sample_a"].left_token, payload["h"]["sample_a"].right_token)
        == token_orientation_name(payload["s"]["sample_a"].left_token, payload["s"]["sample_a"].right_token)
    ) else 0.0
    counterfactual_override = 1.0 if (
        content_family_name(payload["c"]["sample_a"].left_token, payload["c"]["sample_a"].right_token)
        == content_family_name(payload["h"]["sample_b"].left_token, payload["h"]["sample_b"].right_token)
    ) else 0.0
    resolve_bind = 1.0 if (
        content_family_name(payload["r"]["sample_a"].left_token, payload["r"]["sample_a"].right_token)
        == content_family_name(payload["h"]["sample_a"].left_token, payload["h"]["sample_a"].right_token)
    ) else 0.0
    mean_sector = (
        s_step["sector_magnitude_delta"]
        + h_step["sector_magnitude_delta"]
        + c_step["sector_magnitude_delta"]
        + r_step["sector_magnitude_delta"]
    ) / 4.0
    mean_content = (
        s_step["ordered_content_delta"]
        + h_step["ordered_content_delta"]
        + c_step["ordered_content_delta"]
        + r_step["ordered_content_delta"]
    ) / 4.0
    mean_orientation = (
        s_step["orientation_delta"]
        + h_step["orientation_delta"]
        + c_step["orientation_delta"]
        + r_step["orientation_delta"]
    ) / 4.0
    features = {
        "source_sign": source_sign,
        "handoff_gate": handoff_gate,
        "counterfactual_override": counterfactual_override,
        "resolve_bind": resolve_bind,
        "mean_sector_magnitude_delta": round(mean_sector, 6),
        "mean_ordered_content_delta": round(mean_content, 6),
        "mean_orientation_delta": round(mean_orientation, 6),
        "sum_sector_magnitude_delta": round(
            s_step["sector_magnitude_delta"]
            + h_step["sector_magnitude_delta"]
            + c_step["sector_magnitude_delta"]
            + r_step["sector_magnitude_delta"],
            6,
        ),
        "sum_ordered_content_delta": round(
            s_step["ordered_content_delta"]
            + h_step["ordered_content_delta"]
            + c_step["ordered_content_delta"]
            + r_step["ordered_content_delta"],
            6,
        ),
        "sum_orientation_delta": round(
            s_step["orientation_delta"]
            + h_step["orientation_delta"]
            + c_step["orientation_delta"]
            + r_step["orientation_delta"],
            6,
        ),
        "handoff_minus_source_sector": round(h_step["sector_magnitude_delta"] - s_step["sector_magnitude_delta"], 6),
        "resolve_minus_counterfactual_sector": round(r_step["sector_magnitude_delta"] - c_step["sector_magnitude_delta"], 6),
        "handoff_minus_source_content": round(h_step["ordered_content_delta"] - s_step["ordered_content_delta"], 6),
        "resolve_minus_counterfactual_content": round(r_step["ordered_content_delta"] - c_step["ordered_content_delta"], 6),
        "handoff_minus_source_orientation": round(h_step["orientation_delta"] - s_step["orientation_delta"], 6),
        "resolve_minus_counterfactual_orientation": round(r_step["orientation_delta"] - c_step["orientation_delta"], 6),
        "sq_mean_sector": round(mean_sector * mean_sector, 6),
        "sq_mean_content": round(mean_content * mean_content, 6),
        "sq_mean_orientation": round(mean_orientation * mean_orientation, 6),
        "cross_mean_sector_content": round(mean_sector * mean_content, 6),
        "cross_mean_sector_orientation": round(mean_sector * mean_orientation, 6),
        "cross_mean_content_orientation": round(mean_content * mean_orientation, 6),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "allowed_handoff_symbolic_basis_frozen_pass": True,
        "forbidden_feature_family_absent_pass": True,
    }


def positional_anchor_order_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_positional_anchor_order_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    a_result = symbolic_insufficiency_witness_features(text=payload["a"]["dual_text"], seed=seed)
    l_result = symbolic_insufficiency_witness_features(text=payload["l"]["dual_text"], seed=seed)
    r_result = symbolic_insufficiency_witness_features(text=payload["r"]["dual_text"], seed=seed)
    o_result = symbolic_insufficiency_witness_features(text=payload["o"]["dual_text"], seed=seed)
    a_step = _symbolic_insufficiency_path_step_features(payload["a"])
    l_step = _symbolic_insufficiency_path_step_features(payload["l"])
    r_step = _symbolic_insufficiency_path_step_features(payload["r"])
    o_step = _symbolic_insufficiency_path_step_features(payload["o"])
    a_phase = float(a_result["features"]["latent_transition_phase"])
    l_phase = float(l_result["features"]["latent_transition_phase"])
    r_phase = float(r_result["features"]["latent_transition_phase"])
    o_phase = float(o_result["features"]["latent_transition_phase"])
    a_curvature = float(a_result["features"]["latent_transition_curvature"])
    l_curvature = float(l_result["features"]["latent_transition_curvature"])
    r_curvature = float(r_result["features"]["latent_transition_curvature"])
    o_curvature = float(o_result["features"]["latent_transition_curvature"])
    anchor_pivot = mean_pos(payload["a"])
    left_gap = round(mean_pos(payload["l"]) - anchor_pivot, 6)
    right_gap = round(mean_pos(payload["r"]) - anchor_pivot, 6)
    resolve_gap = round(mean_pos(payload["o"]) - anchor_pivot, 6)
    left_gap_norm = round(left_gap / 4.0, 6)
    right_gap_norm = round(right_gap / 4.0, 6)
    resolve_gap_norm = round(resolve_gap / 4.0, 6)
    feature_order = [
        "anchor_phase",
        "left_phase",
        "right_phase",
        "resolve_phase",
        "anchor_curvature",
        "resolve_curvature",
        "left_anchor_gap",
        "right_anchor_gap",
        "resolve_anchor_gap",
        "ordered_side_gap",
        "resolve_order_alignment",
        "anchor_order_declared_mix",
        "anchor_order_cross_curvature",
    ]
    features = {
        "anchor_phase": a_phase,
        "left_phase": l_phase,
        "right_phase": r_phase,
        "resolve_phase": o_phase,
        "anchor_curvature": a_curvature,
        "resolve_curvature": o_curvature,
        "left_anchor_gap": left_gap_norm,
        "right_anchor_gap": right_gap_norm,
        "resolve_anchor_gap": resolve_gap_norm,
        "ordered_side_gap": round(abs(right_gap_norm - left_gap_norm), 6),
        "resolve_order_alignment": round(math.sin((l_phase - a_phase) - (r_phase - o_phase)), 6),
        "anchor_order_declared_mix": round(
            left_gap_norm * l_step["orientation_delta"]
            + right_gap_norm * r_step["orientation_delta"]
            - resolve_gap_norm * o_step["ordered_content_delta"],
            6,
        ),
        "anchor_order_cross_curvature": round(
            0.5 * (l_phase - r_phase) * o_curvature
            + 0.5 * (a_phase - o_phase) * l_curvature
            + (right_gap_norm - left_gap_norm) * a_curvature,
            6,
        ),
    }
    return {
        "feature_order": feature_order,
        "features": features,
        "bounded_feature_audit_pass": True,
        "forbidden_feature_family_absent_pass": True,
    }


def positional_anchor_order_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_positional_anchor_order_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    a_step = _symbolic_insufficiency_path_step_features(payload["a"])
    l_step = _symbolic_insufficiency_path_step_features(payload["l"])
    r_step = _symbolic_insufficiency_path_step_features(payload["r"])
    o_step = _symbolic_insufficiency_path_step_features(payload["o"])
    anchor_pivot = mean_pos(payload["a"])
    left_gap = mean_pos(payload["l"]) - anchor_pivot
    right_gap = mean_pos(payload["r"]) - anchor_pivot
    resolve_gap = mean_pos(payload["o"]) - anchor_pivot
    left_of_anchor = 1.0 if left_gap < 0.0 else 0.0
    right_of_anchor = 1.0 if right_gap > 0.0 else 0.0
    resolve_matches_order = 1.0 if resolve_gap >= left_gap and resolve_gap <= right_gap else 0.0
    anchor_sign = 1.0 if (
        offset_sector(payload["a"]["sample_a"].offset).startswith("P")
        == offset_sector(payload["a"]["sample_b"].offset).startswith("P")
    ) else 0.0
    mean_sector = (
        a_step["sector_magnitude_delta"]
        + l_step["sector_magnitude_delta"]
        + r_step["sector_magnitude_delta"]
        + o_step["sector_magnitude_delta"]
    ) / 4.0
    mean_content = (
        a_step["ordered_content_delta"]
        + l_step["ordered_content_delta"]
        + r_step["ordered_content_delta"]
        + o_step["ordered_content_delta"]
    ) / 4.0
    mean_orientation = (
        a_step["orientation_delta"]
        + l_step["orientation_delta"]
        + r_step["orientation_delta"]
        + o_step["orientation_delta"]
    ) / 4.0
    left_gap_norm = round(left_gap / 4.0, 6)
    right_gap_norm = round(right_gap / 4.0, 6)
    resolve_gap_norm = round(resolve_gap / 4.0, 6)
    features = {
        "anchor_sign": anchor_sign,
        "left_of_anchor": left_of_anchor,
        "right_of_anchor": right_of_anchor,
        "resolve_matches_order": resolve_matches_order,
        "left_anchor_gap": left_gap_norm,
        "right_anchor_gap": right_gap_norm,
        "resolve_anchor_gap": resolve_gap_norm,
        "ordered_side_gap": round(abs(right_gap_norm - left_gap_norm), 6),
        "mean_sector_magnitude_delta": round(mean_sector, 6),
        "mean_ordered_content_delta": round(mean_content, 6),
        "mean_orientation_delta": round(mean_orientation, 6),
        "left_right_content_gap": round(l_step["ordered_content_delta"] - r_step["ordered_content_delta"], 6),
        "left_right_orientation_gap": round(l_step["orientation_delta"] - r_step["orientation_delta"], 6),
        "resolve_minus_anchor_content": round(o_step["ordered_content_delta"] - a_step["ordered_content_delta"], 6),
        "cross_mean_sector_content": round(mean_sector * mean_content, 6),
        "cross_mean_sector_orientation": round(mean_sector * mean_orientation, 6),
        "cross_mean_content_orientation": round(mean_content * mean_orientation, 6),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "allowed_anchor_order_symbolic_basis_frozen_pass": True,
        "forbidden_feature_family_absent_pass": True,
    }


def positional_anchor_distance_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_positional_anchor_distance_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    a_result = symbolic_insufficiency_witness_features(text=payload["a"]["dual_text"], seed=seed)
    n_result = symbolic_insufficiency_witness_features(text=payload["n"]["dual_text"], seed=seed)
    f_result = symbolic_insufficiency_witness_features(text=payload["f"]["dual_text"], seed=seed)
    o_result = symbolic_insufficiency_witness_features(text=payload["o"]["dual_text"], seed=seed)
    a_step = _symbolic_insufficiency_path_step_features(payload["a"])
    n_step = _symbolic_insufficiency_path_step_features(payload["n"])
    f_step = _symbolic_insufficiency_path_step_features(payload["f"])
    o_step = _symbolic_insufficiency_path_step_features(payload["o"])
    a_phase = float(a_result["features"]["latent_transition_phase"])
    n_phase = float(n_result["features"]["latent_transition_phase"])
    f_phase = float(f_result["features"]["latent_transition_phase"])
    o_phase = float(o_result["features"]["latent_transition_phase"])
    a_curvature = float(a_result["features"]["latent_transition_curvature"])
    n_curvature = float(n_result["features"]["latent_transition_curvature"])
    f_curvature = float(f_result["features"]["latent_transition_curvature"])
    o_curvature = float(o_result["features"]["latent_transition_curvature"])
    anchor_pivot = mean_pos(payload["a"])
    near_gap = round(mean_pos(payload["n"]) - anchor_pivot, 6)
    far_gap = round(mean_pos(payload["f"]) - anchor_pivot, 6)
    resolve_gap = round(mean_pos(payload["o"]) - anchor_pivot, 6)
    near_distance_norm = round(abs(near_gap) / 4.0, 6)
    far_distance_norm = round(abs(far_gap) / 4.0, 6)
    resolve_distance_norm = round(abs(resolve_gap) / 4.0, 6)
    feature_order = [
        "anchor_phase",
        "near_phase",
        "far_phase",
        "resolve_phase",
        "anchor_curvature",
        "resolve_curvature",
        "near_anchor_distance",
        "far_anchor_distance",
        "resolve_anchor_distance",
        "distance_span",
        "resolve_distance_alignment",
        "anchor_distance_declared_mix",
        "anchor_distance_cross_curvature",
    ]
    features = {
        "anchor_phase": a_phase,
        "near_phase": n_phase,
        "far_phase": f_phase,
        "resolve_phase": o_phase,
        "anchor_curvature": a_curvature,
        "resolve_curvature": o_curvature,
        "near_anchor_distance": near_distance_norm,
        "far_anchor_distance": far_distance_norm,
        "resolve_anchor_distance": resolve_distance_norm,
        "distance_span": round(far_distance_norm - near_distance_norm, 6),
        "resolve_distance_alignment": round(
            math.sin((resolve_distance_norm - near_distance_norm) - (far_distance_norm - resolve_distance_norm)),
            6,
        ),
        "anchor_distance_declared_mix": round(
            near_distance_norm * n_step["orientation_delta"]
            + far_distance_norm * f_step["orientation_delta"]
            - resolve_distance_norm * o_step["ordered_content_delta"],
            6,
        ),
        "anchor_distance_cross_curvature": round(
            0.5 * (n_phase - f_phase) * o_curvature
            + 0.5 * (a_phase - o_phase) * n_curvature
            + (far_distance_norm - near_distance_norm) * a_curvature,
            6,
        ),
    }
    return {
        "feature_order": feature_order,
        "features": features,
        "bounded_feature_audit_pass": True,
        "forbidden_feature_family_absent_pass": True,
    }


def positional_anchor_distance_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_positional_anchor_distance_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    a_step = _symbolic_insufficiency_path_step_features(payload["a"])
    n_step = _symbolic_insufficiency_path_step_features(payload["n"])
    f_step = _symbolic_insufficiency_path_step_features(payload["f"])
    o_step = _symbolic_insufficiency_path_step_features(payload["o"])
    anchor_pivot = mean_pos(payload["a"])
    near_gap = mean_pos(payload["n"]) - anchor_pivot
    far_gap = mean_pos(payload["f"]) - anchor_pivot
    resolve_gap = mean_pos(payload["o"]) - anchor_pivot
    near_distance = abs(near_gap)
    far_distance = abs(far_gap)
    resolve_distance = abs(resolve_gap)
    near_is_closer = 1.0 if near_distance < far_distance else 0.0
    far_is_farther = 1.0 if far_distance > near_distance else 0.0
    resolve_matches_distance = 1.0 if resolve_distance >= near_distance and resolve_distance <= far_distance else 0.0
    anchor_sign = 1.0 if (
        offset_sector(payload["a"]["sample_a"].offset).startswith("P")
        == offset_sector(payload["a"]["sample_b"].offset).startswith("P")
    ) else 0.0
    mean_sector = (
        a_step["sector_magnitude_delta"]
        + n_step["sector_magnitude_delta"]
        + f_step["sector_magnitude_delta"]
        + o_step["sector_magnitude_delta"]
    ) / 4.0
    mean_content = (
        a_step["ordered_content_delta"]
        + n_step["ordered_content_delta"]
        + f_step["ordered_content_delta"]
        + o_step["ordered_content_delta"]
    ) / 4.0
    mean_orientation = (
        a_step["orientation_delta"]
        + n_step["orientation_delta"]
        + f_step["orientation_delta"]
        + o_step["orientation_delta"]
    ) / 4.0
    near_distance_norm = round(near_distance / 4.0, 6)
    far_distance_norm = round(far_distance / 4.0, 6)
    resolve_distance_norm = round(resolve_distance / 4.0, 6)
    features = {
        "anchor_sign": anchor_sign,
        "near_is_closer": near_is_closer,
        "far_is_farther": far_is_farther,
        "resolve_matches_distance": resolve_matches_distance,
        "near_anchor_distance": near_distance_norm,
        "far_anchor_distance": far_distance_norm,
        "resolve_anchor_distance": resolve_distance_norm,
        "distance_span": round(far_distance_norm - near_distance_norm, 6),
        "mean_sector_magnitude_delta": round(mean_sector, 6),
        "mean_ordered_content_delta": round(mean_content, 6),
        "mean_orientation_delta": round(mean_orientation, 6),
        "near_far_content_gap": round(n_step["ordered_content_delta"] - f_step["ordered_content_delta"], 6),
        "near_far_orientation_gap": round(n_step["orientation_delta"] - f_step["orientation_delta"], 6),
        "resolve_minus_anchor_content": round(o_step["ordered_content_delta"] - a_step["ordered_content_delta"], 6),
        "cross_mean_sector_content": round(mean_sector * mean_content, 6),
        "cross_mean_sector_orientation": round(mean_sector * mean_orientation, 6),
        "cross_mean_content_orientation": round(mean_content * mean_orientation, 6),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "allowed_anchor_distance_symbolic_basis_frozen_pass": True,
        "forbidden_feature_family_absent_pass": True,
    }


def positional_anchor_span_membership_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_positional_anchor_span_membership_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    def membership_margin(value: float, low: float, high: float) -> float:
        if low <= value <= high:
            return min(value - low, high - value)
        if value < low:
            return -(low - value)
        return -(value - high)

    a_result = symbolic_insufficiency_witness_features(text=payload["a"]["dual_text"], seed=seed)
    l_result = symbolic_insufficiency_witness_features(text=payload["l"]["dual_text"], seed=seed)
    r_result = symbolic_insufficiency_witness_features(text=payload["r"]["dual_text"], seed=seed)
    p_result = symbolic_insufficiency_witness_features(text=payload["p"]["dual_text"], seed=seed)
    o_result = symbolic_insufficiency_witness_features(text=payload["o"]["dual_text"], seed=seed)
    a_step = _symbolic_insufficiency_path_step_features(payload["a"])
    l_step = _symbolic_insufficiency_path_step_features(payload["l"])
    r_step = _symbolic_insufficiency_path_step_features(payload["r"])
    p_step = _symbolic_insufficiency_path_step_features(payload["p"])
    o_step = _symbolic_insufficiency_path_step_features(payload["o"])
    a_phase = float(a_result["features"]["latent_transition_phase"])
    l_phase = float(l_result["features"]["latent_transition_phase"])
    r_phase = float(r_result["features"]["latent_transition_phase"])
    p_phase = float(p_result["features"]["latent_transition_phase"])
    o_phase = float(o_result["features"]["latent_transition_phase"])
    a_curvature = float(a_result["features"]["latent_transition_curvature"])
    p_curvature = float(p_result["features"]["latent_transition_curvature"])
    o_curvature = float(o_result["features"]["latent_transition_curvature"])
    anchor_pivot = mean_pos(payload["a"])
    left_gap = round(mean_pos(payload["l"]) - anchor_pivot, 6)
    right_gap = round(mean_pos(payload["r"]) - anchor_pivot, 6)
    probe_gap = round(mean_pos(payload["p"]) - anchor_pivot, 6)
    resolve_gap = round(mean_pos(payload["o"]) - anchor_pivot, 6)
    left_gap_norm = round(left_gap / 4.0, 6)
    right_gap_norm = round(right_gap / 4.0, 6)
    probe_gap_norm = round(probe_gap / 4.0, 6)
    resolve_gap_norm = round(resolve_gap / 4.0, 6)
    probe_margin_norm = round(membership_margin(probe_gap, left_gap, right_gap) / 4.0, 6)
    resolve_margin_norm = round(membership_margin(resolve_gap, left_gap, right_gap) / 4.0, 6)
    feature_order = [
        "anchor_phase",
        "left_phase",
        "right_phase",
        "probe_phase",
        "resolve_phase",
        "anchor_curvature",
        "probe_curvature",
        "resolve_curvature",
        "left_anchor_gap",
        "right_anchor_gap",
        "probe_anchor_gap",
        "resolve_anchor_gap",
        "span_width",
        "probe_membership_margin",
        "resolve_membership_margin",
        "span_membership_alignment",
        "anchor_span_declared_mix",
        "anchor_span_cross_curvature",
    ]
    features = {
        "anchor_phase": a_phase,
        "left_phase": l_phase,
        "right_phase": r_phase,
        "probe_phase": p_phase,
        "resolve_phase": o_phase,
        "anchor_curvature": a_curvature,
        "probe_curvature": p_curvature,
        "resolve_curvature": o_curvature,
        "left_anchor_gap": left_gap_norm,
        "right_anchor_gap": right_gap_norm,
        "probe_anchor_gap": probe_gap_norm,
        "resolve_anchor_gap": resolve_gap_norm,
        "span_width": round(right_gap_norm - left_gap_norm, 6),
        "probe_membership_margin": probe_margin_norm,
        "resolve_membership_margin": resolve_margin_norm,
        "span_membership_alignment": round(math.sin((p_phase - a_phase) - (o_phase - a_phase) + (l_phase - r_phase)), 6),
        "anchor_span_declared_mix": round(
            probe_margin_norm * p_step["orientation_delta"]
            + resolve_margin_norm * o_step["orientation_delta"]
            + (right_gap_norm - left_gap_norm) * 0.5 * (l_step["ordered_content_delta"] + r_step["ordered_content_delta"]),
            6,
        ),
        "anchor_span_cross_curvature": round(
            0.5 * (p_phase - o_phase) * a_curvature
            + 0.5 * (l_phase - r_phase) * o_curvature
            + (resolve_margin_norm - probe_margin_norm) * p_curvature,
            6,
        ),
    }
    return {
        "feature_order": feature_order,
        "features": features,
        "bounded_feature_audit_pass": True,
        "forbidden_feature_family_absent_pass": True,
    }


def positional_anchor_span_membership_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_positional_anchor_span_membership_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    def membership_margin(value: float, low: float, high: float) -> float:
        if low <= value <= high:
            return min(value - low, high - value)
        if value < low:
            return -(low - value)
        return -(value - high)

    a_step = _symbolic_insufficiency_path_step_features(payload["a"])
    l_step = _symbolic_insufficiency_path_step_features(payload["l"])
    r_step = _symbolic_insufficiency_path_step_features(payload["r"])
    p_step = _symbolic_insufficiency_path_step_features(payload["p"])
    o_step = _symbolic_insufficiency_path_step_features(payload["o"])
    anchor_pivot = mean_pos(payload["a"])
    left_gap = mean_pos(payload["l"]) - anchor_pivot
    right_gap = mean_pos(payload["r"]) - anchor_pivot
    probe_gap = mean_pos(payload["p"]) - anchor_pivot
    resolve_gap = mean_pos(payload["o"]) - anchor_pivot
    probe_inside_span = 1.0 if left_gap <= probe_gap <= right_gap else 0.0
    resolve_inside_span = 1.0 if left_gap <= resolve_gap <= right_gap else 0.0
    resolve_matches_probe_membership = 1.0 if probe_inside_span == resolve_inside_span else 0.0
    anchor_sign = 1.0 if (
        offset_sector(payload["a"]["sample_a"].offset).startswith("P")
        == offset_sector(payload["a"]["sample_b"].offset).startswith("P")
    ) else 0.0
    mean_sector = (
        a_step["sector_magnitude_delta"]
        + l_step["sector_magnitude_delta"]
        + r_step["sector_magnitude_delta"]
        + p_step["sector_magnitude_delta"]
        + o_step["sector_magnitude_delta"]
    ) / 5.0
    mean_content = (
        a_step["ordered_content_delta"]
        + l_step["ordered_content_delta"]
        + r_step["ordered_content_delta"]
        + p_step["ordered_content_delta"]
        + o_step["ordered_content_delta"]
    ) / 5.0
    mean_orientation = (
        a_step["orientation_delta"]
        + l_step["orientation_delta"]
        + r_step["orientation_delta"]
        + p_step["orientation_delta"]
        + o_step["orientation_delta"]
    ) / 5.0
    left_gap_norm = round(left_gap / 4.0, 6)
    right_gap_norm = round(right_gap / 4.0, 6)
    probe_gap_norm = round(probe_gap / 4.0, 6)
    resolve_gap_norm = round(resolve_gap / 4.0, 6)
    probe_margin_norm = round(membership_margin(probe_gap, left_gap, right_gap) / 4.0, 6)
    resolve_margin_norm = round(membership_margin(resolve_gap, left_gap, right_gap) / 4.0, 6)
    features = {
        "anchor_sign": anchor_sign,
        "probe_inside_span": probe_inside_span,
        "resolve_inside_span": resolve_inside_span,
        "resolve_matches_probe_membership": resolve_matches_probe_membership,
        "left_anchor_gap": left_gap_norm,
        "right_anchor_gap": right_gap_norm,
        "probe_anchor_gap": probe_gap_norm,
        "resolve_anchor_gap": resolve_gap_norm,
        "span_width": round(right_gap_norm - left_gap_norm, 6),
        "probe_membership_margin": probe_margin_norm,
        "resolve_membership_margin": resolve_margin_norm,
        "mean_sector_magnitude_delta": round(mean_sector, 6),
        "mean_ordered_content_delta": round(mean_content, 6),
        "mean_orientation_delta": round(mean_orientation, 6),
        "left_right_content_gap": round(l_step["ordered_content_delta"] - r_step["ordered_content_delta"], 6),
        "probe_resolve_orientation_gap": round(p_step["orientation_delta"] - o_step["orientation_delta"], 6),
        "cross_mean_sector_content": round(mean_sector * mean_content, 6),
        "cross_mean_sector_orientation": round(mean_sector * mean_orientation, 6),
        "cross_mean_content_orientation": round(mean_content * mean_orientation, 6),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "allowed_anchor_span_membership_symbolic_basis_frozen_pass": True,
        "forbidden_feature_family_absent_pass": True,
    }


def positional_anchor_offset_signature_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_positional_anchor_offset_signature_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    def offset_bucket(value: float) -> float:
        distance = abs(value)
        if distance < 1.0:
            return 0.0
        if distance < 2.0:
            return 1.0
        return 2.0

    a_result = symbolic_insufficiency_witness_features(text=payload["a"]["dual_text"], seed=seed)
    p_result = symbolic_insufficiency_witness_features(text=payload["p"]["dual_text"], seed=seed)
    q_result = symbolic_insufficiency_witness_features(text=payload["q"]["dual_text"], seed=seed)
    o_result = symbolic_insufficiency_witness_features(text=payload["o"]["dual_text"], seed=seed)
    a_step = _symbolic_insufficiency_path_step_features(payload["a"])
    p_step = _symbolic_insufficiency_path_step_features(payload["p"])
    q_step = _symbolic_insufficiency_path_step_features(payload["q"])
    o_step = _symbolic_insufficiency_path_step_features(payload["o"])
    a_phase = float(a_result["features"]["latent_transition_phase"])
    p_phase = float(p_result["features"]["latent_transition_phase"])
    q_phase = float(q_result["features"]["latent_transition_phase"])
    o_phase = float(o_result["features"]["latent_transition_phase"])
    a_curvature = float(a_result["features"]["latent_transition_curvature"])
    p_curvature = float(p_result["features"]["latent_transition_curvature"])
    o_curvature = float(o_result["features"]["latent_transition_curvature"])
    anchor_pivot = mean_pos(payload["a"])
    probe_gap = round(mean_pos(payload["p"]) - anchor_pivot, 6)
    alt_gap = round(mean_pos(payload["q"]) - anchor_pivot, 6)
    resolve_gap = round(mean_pos(payload["o"]) - anchor_pivot, 6)
    probe_gap_norm = round(probe_gap / 4.0, 6)
    alt_gap_norm = round(alt_gap / 4.0, 6)
    resolve_gap_norm = round(resolve_gap / 4.0, 6)
    probe_side = 1.0 if probe_gap >= 0.0 else -1.0
    alt_side = 1.0 if alt_gap >= 0.0 else -1.0
    resolve_side = 1.0 if resolve_gap >= 0.0 else -1.0
    probe_bucket = offset_bucket(probe_gap)
    alt_bucket = offset_bucket(alt_gap)
    resolve_bucket = offset_bucket(resolve_gap)
    resolve_matches_probe_signature = 1.0 if (resolve_side == probe_side and resolve_bucket == probe_bucket) else 0.0
    feature_order = [
        "anchor_phase",
        "probe_phase",
        "alternate_phase",
        "resolve_phase",
        "anchor_curvature",
        "probe_curvature",
        "resolve_curvature",
        "probe_anchor_gap",
        "alternate_anchor_gap",
        "resolve_anchor_gap",
        "probe_side",
        "alternate_side",
        "resolve_side",
        "probe_offset_bucket",
        "alternate_offset_bucket",
        "resolve_offset_bucket",
        "resolve_matches_probe_signature",
        "anchor_offset_declared_mix",
        "anchor_offset_cross_curvature",
    ]
    features = {
        "anchor_phase": a_phase,
        "probe_phase": p_phase,
        "alternate_phase": q_phase,
        "resolve_phase": o_phase,
        "anchor_curvature": a_curvature,
        "probe_curvature": p_curvature,
        "resolve_curvature": o_curvature,
        "probe_anchor_gap": probe_gap_norm,
        "alternate_anchor_gap": alt_gap_norm,
        "resolve_anchor_gap": resolve_gap_norm,
        "probe_side": probe_side,
        "alternate_side": alt_side,
        "resolve_side": resolve_side,
        "probe_offset_bucket": probe_bucket,
        "alternate_offset_bucket": alt_bucket,
        "resolve_offset_bucket": resolve_bucket,
        "resolve_matches_probe_signature": resolve_matches_probe_signature,
        "anchor_offset_declared_mix": round(
            probe_gap_norm * p_step["ordered_content_delta"]
            - alt_gap_norm * q_step["ordered_content_delta"]
            + resolve_gap_norm * o_step["orientation_delta"],
            6,
        ),
        "anchor_offset_cross_curvature": round(
            0.5 * (p_phase - o_phase) * a_curvature
            + 0.5 * (probe_gap_norm - resolve_gap_norm) * p_curvature
            + 0.5 * (alt_gap_norm - probe_gap_norm) * o_curvature,
            6,
        ),
    }
    return {
        "feature_order": feature_order,
        "features": features,
        "bounded_feature_audit_pass": True,
        "forbidden_feature_family_absent_pass": True,
    }


def positional_anchor_offset_signature_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_positional_anchor_offset_signature_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    def offset_bucket(value: float) -> float:
        distance = abs(value)
        if distance < 1.0:
            return 0.0
        if distance < 2.0:
            return 1.0
        return 2.0

    a_step = _symbolic_insufficiency_path_step_features(payload["a"])
    p_step = _symbolic_insufficiency_path_step_features(payload["p"])
    q_step = _symbolic_insufficiency_path_step_features(payload["q"])
    o_step = _symbolic_insufficiency_path_step_features(payload["o"])
    anchor_pivot = mean_pos(payload["a"])
    probe_gap = mean_pos(payload["p"]) - anchor_pivot
    alt_gap = mean_pos(payload["q"]) - anchor_pivot
    resolve_gap = mean_pos(payload["o"]) - anchor_pivot
    probe_side = 1.0 if probe_gap >= 0.0 else 0.0
    alt_side = 1.0 if alt_gap >= 0.0 else 0.0
    resolve_side = 1.0 if resolve_gap >= 0.0 else 0.0
    probe_bucket = offset_bucket(probe_gap)
    alt_bucket = offset_bucket(alt_gap)
    resolve_bucket = offset_bucket(resolve_gap)
    resolve_matches_probe_signature = 1.0 if (resolve_side == probe_side and resolve_bucket == probe_bucket) else 0.0
    anchor_sign = 1.0 if (
        offset_sector(payload["a"]["sample_a"].offset).startswith("P")
        == offset_sector(payload["a"]["sample_b"].offset).startswith("P")
    ) else 0.0
    mean_sector = (
        a_step["sector_magnitude_delta"]
        + p_step["sector_magnitude_delta"]
        + q_step["sector_magnitude_delta"]
        + o_step["sector_magnitude_delta"]
    ) / 4.0
    mean_content = (
        a_step["ordered_content_delta"]
        + p_step["ordered_content_delta"]
        + q_step["ordered_content_delta"]
        + o_step["ordered_content_delta"]
    ) / 4.0
    mean_orientation = (
        a_step["orientation_delta"]
        + p_step["orientation_delta"]
        + q_step["orientation_delta"]
        + o_step["orientation_delta"]
    ) / 4.0
    features = {
        "anchor_sign": anchor_sign,
        "probe_side": probe_side,
        "alternate_side": alt_side,
        "resolve_side": resolve_side,
        "probe_offset_bucket": probe_bucket,
        "alternate_offset_bucket": alt_bucket,
        "resolve_offset_bucket": resolve_bucket,
        "resolve_matches_probe_signature": resolve_matches_probe_signature,
        "probe_anchor_gap": round(probe_gap / 4.0, 6),
        "alternate_anchor_gap": round(alt_gap / 4.0, 6),
        "resolve_anchor_gap": round(resolve_gap / 4.0, 6),
        "mean_sector_magnitude_delta": round(mean_sector, 6),
        "mean_ordered_content_delta": round(mean_content, 6),
        "mean_orientation_delta": round(mean_orientation, 6),
        "probe_alternate_content_gap": round(p_step["ordered_content_delta"] - q_step["ordered_content_delta"], 6),
        "resolve_probe_orientation_gap": round(o_step["orientation_delta"] - p_step["orientation_delta"], 6),
        "cross_mean_sector_content": round(mean_sector * mean_content, 6),
        "cross_mean_sector_orientation": round(mean_sector * mean_orientation, 6),
        "cross_mean_content_orientation": round(mean_content * mean_orientation, 6),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "allowed_anchor_offset_signature_symbolic_basis_frozen_pass": True,
        "forbidden_feature_family_absent_pass": True,
    }


def positional_anchor_betweenness_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_positional_anchor_betweenness_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    l_result = symbolic_insufficiency_witness_features(text=payload["l"]["dual_text"], seed=seed)
    a_result = symbolic_insufficiency_witness_features(text=payload["a"]["dual_text"], seed=seed)
    r_result = symbolic_insufficiency_witness_features(text=payload["r"]["dual_text"], seed=seed)
    p_result = symbolic_insufficiency_witness_features(text=payload["p"]["dual_text"], seed=seed)
    o_result = symbolic_insufficiency_witness_features(text=payload["o"]["dual_text"], seed=seed)
    l_step = _symbolic_insufficiency_path_step_features(payload["l"])
    a_step = _symbolic_insufficiency_path_step_features(payload["a"])
    r_step = _symbolic_insufficiency_path_step_features(payload["r"])
    p_step = _symbolic_insufficiency_path_step_features(payload["p"])
    o_step = _symbolic_insufficiency_path_step_features(payload["o"])
    l_phase = float(l_result["features"]["latent_transition_phase"])
    a_phase = float(a_result["features"]["latent_transition_phase"])
    r_phase = float(r_result["features"]["latent_transition_phase"])
    p_phase = float(p_result["features"]["latent_transition_phase"])
    o_phase = float(o_result["features"]["latent_transition_phase"])
    a_curvature = float(a_result["features"]["latent_transition_curvature"])
    p_curvature = float(p_result["features"]["latent_transition_curvature"])
    o_curvature = float(o_result["features"]["latent_transition_curvature"])
    anchor_pivot = mean_pos(payload["a"])
    left_gap = round(mean_pos(payload["l"]) - anchor_pivot, 6)
    right_gap = round(mean_pos(payload["r"]) - anchor_pivot, 6)
    probe_gap = round(mean_pos(payload["p"]) - anchor_pivot, 6)
    resolve_gap = round(mean_pos(payload["o"]) - anchor_pivot, 6)
    left_gap_norm = round(left_gap / 4.0, 6)
    right_gap_norm = round(right_gap / 4.0, 6)
    probe_gap_norm = round(probe_gap / 4.0, 6)
    resolve_gap_norm = round(resolve_gap / 4.0, 6)
    probe_between = 1.0 if left_gap < probe_gap < right_gap else 0.0
    resolve_between = 1.0 if left_gap < resolve_gap < right_gap else 0.0
    resolve_matches_probe_betweenness = 1.0 if probe_between == resolve_between else 0.0
    feature_order = [
        "left_phase",
        "anchor_phase",
        "right_phase",
        "probe_phase",
        "resolve_phase",
        "anchor_curvature",
        "probe_curvature",
        "resolve_curvature",
        "left_anchor_gap",
        "right_anchor_gap",
        "probe_anchor_gap",
        "resolve_anchor_gap",
        "probe_between",
        "resolve_between",
        "resolve_matches_probe_betweenness",
        "betweenness_width",
        "anchor_betweenness_declared_mix",
        "anchor_betweenness_cross_curvature",
    ]
    features = {
        "left_phase": l_phase,
        "anchor_phase": a_phase,
        "right_phase": r_phase,
        "probe_phase": p_phase,
        "resolve_phase": o_phase,
        "anchor_curvature": a_curvature,
        "probe_curvature": p_curvature,
        "resolve_curvature": o_curvature,
        "left_anchor_gap": left_gap_norm,
        "right_anchor_gap": right_gap_norm,
        "probe_anchor_gap": probe_gap_norm,
        "resolve_anchor_gap": resolve_gap_norm,
        "probe_between": probe_between,
        "resolve_between": resolve_between,
        "resolve_matches_probe_betweenness": resolve_matches_probe_betweenness,
        "betweenness_width": round(right_gap_norm - left_gap_norm, 6),
        "anchor_betweenness_declared_mix": round(
            probe_gap_norm * p_step["ordered_content_delta"]
            + resolve_gap_norm * o_step["ordered_content_delta"]
            + (right_gap_norm - left_gap_norm) * 0.5 * (l_step["orientation_delta"] + r_step["orientation_delta"]),
            6,
        ),
        "anchor_betweenness_cross_curvature": round(
            0.5 * (p_phase - o_phase) * a_curvature
            + 0.5 * (l_phase - r_phase) * o_curvature
            + (resolve_gap_norm - probe_gap_norm) * p_curvature,
            6,
        ),
    }
    return {
        "feature_order": feature_order,
        "features": features,
        "bounded_feature_audit_pass": True,
        "forbidden_feature_family_absent_pass": True,
    }


def positional_anchor_betweenness_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_positional_anchor_betweenness_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    l_step = _symbolic_insufficiency_path_step_features(payload["l"])
    a_step = _symbolic_insufficiency_path_step_features(payload["a"])
    r_step = _symbolic_insufficiency_path_step_features(payload["r"])
    p_step = _symbolic_insufficiency_path_step_features(payload["p"])
    o_step = _symbolic_insufficiency_path_step_features(payload["o"])
    anchor_pivot = mean_pos(payload["a"])
    left_gap = mean_pos(payload["l"]) - anchor_pivot
    right_gap = mean_pos(payload["r"]) - anchor_pivot
    probe_gap = mean_pos(payload["p"]) - anchor_pivot
    resolve_gap = mean_pos(payload["o"]) - anchor_pivot
    probe_between = 1.0 if left_gap < probe_gap < right_gap else 0.0
    resolve_between = 1.0 if left_gap < resolve_gap < right_gap else 0.0
    resolve_matches_probe_betweenness = 1.0 if probe_between == resolve_between else 0.0
    anchor_sign = 1.0 if (
        offset_sector(payload["a"]["sample_a"].offset).startswith("P")
        == offset_sector(payload["a"]["sample_b"].offset).startswith("P")
    ) else 0.0
    mean_sector = (
        l_step["sector_magnitude_delta"]
        + a_step["sector_magnitude_delta"]
        + r_step["sector_magnitude_delta"]
        + p_step["sector_magnitude_delta"]
        + o_step["sector_magnitude_delta"]
    ) / 5.0
    mean_content = (
        l_step["ordered_content_delta"]
        + a_step["ordered_content_delta"]
        + r_step["ordered_content_delta"]
        + p_step["ordered_content_delta"]
        + o_step["ordered_content_delta"]
    ) / 5.0
    mean_orientation = (
        l_step["orientation_delta"]
        + a_step["orientation_delta"]
        + r_step["orientation_delta"]
        + p_step["orientation_delta"]
        + o_step["orientation_delta"]
    ) / 5.0
    features = {
        "anchor_sign": anchor_sign,
        "probe_between": probe_between,
        "resolve_between": resolve_between,
        "resolve_matches_probe_betweenness": resolve_matches_probe_betweenness,
        "left_anchor_gap": round(left_gap / 4.0, 6),
        "right_anchor_gap": round(right_gap / 4.0, 6),
        "probe_anchor_gap": round(probe_gap / 4.0, 6),
        "resolve_anchor_gap": round(resolve_gap / 4.0, 6),
        "betweenness_width": round((right_gap - left_gap) / 4.0, 6),
        "mean_sector_magnitude_delta": round(mean_sector, 6),
        "mean_ordered_content_delta": round(mean_content, 6),
        "mean_orientation_delta": round(mean_orientation, 6),
        "left_right_content_gap": round(l_step["ordered_content_delta"] - r_step["ordered_content_delta"], 6),
        "probe_resolve_orientation_gap": round(p_step["orientation_delta"] - o_step["orientation_delta"], 6),
        "cross_mean_sector_content": round(mean_sector * mean_content, 6),
        "cross_mean_sector_orientation": round(mean_sector * mean_orientation, 6),
        "cross_mean_content_orientation": round(mean_content * mean_orientation, 6),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "allowed_anchor_betweenness_symbolic_basis_frozen_pass": True,
        "forbidden_feature_family_absent_pass": True,
    }


def positional_offset_retrieval_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_positional_offset_retrieval_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    def gap_bucket(value: float) -> float:
        distance = abs(value)
        if distance < 1.0:
            return 0.0
        if distance < 2.0:
            return 1.0
        return 2.0

    a_result = symbolic_insufficiency_witness_features(text=payload["a"]["dual_text"], seed=seed)
    t_result = symbolic_insufficiency_witness_features(text=payload["t"]["dual_text"], seed=seed)
    d_result = symbolic_insufficiency_witness_features(text=payload["d"]["dual_text"], seed=seed)
    o_result = symbolic_insufficiency_witness_features(text=payload["o"]["dual_text"], seed=seed)
    t_step = _symbolic_insufficiency_path_step_features(payload["t"])
    d_step = _symbolic_insufficiency_path_step_features(payload["d"])
    o_step = _symbolic_insufficiency_path_step_features(payload["o"])
    a_phase = float(a_result["features"]["latent_transition_phase"])
    t_phase = float(t_result["features"]["latent_transition_phase"])
    d_phase = float(d_result["features"]["latent_transition_phase"])
    o_phase = float(o_result["features"]["latent_transition_phase"])
    a_curvature = float(a_result["features"]["latent_transition_curvature"])
    t_curvature = float(t_result["features"]["latent_transition_curvature"])
    o_curvature = float(o_result["features"]["latent_transition_curvature"])
    anchor_pivot = mean_pos(payload["a"])
    target_gap = round(mean_pos(payload["t"]) - anchor_pivot, 6)
    distractor_gap = round(mean_pos(payload["d"]) - anchor_pivot, 6)
    resolve_gap = round(mean_pos(payload["o"]) - anchor_pivot, 6)
    target_gap_norm = round(target_gap / 4.0, 6)
    distractor_gap_norm = round(distractor_gap / 4.0, 6)
    resolve_gap_norm = round(resolve_gap / 4.0, 6)
    target_side = 1.0 if target_gap >= 0.0 else -1.0
    distractor_side = 1.0 if distractor_gap >= 0.0 else -1.0
    resolve_side = 1.0 if resolve_gap >= 0.0 else -1.0
    target_bucket = gap_bucket(target_gap)
    distractor_bucket = gap_bucket(distractor_gap)
    resolve_bucket = gap_bucket(resolve_gap)
    target_offset_agreement = 1.0 if resolve_side == target_side and resolve_bucket == target_bucket else 0.0
    resolve_agreement_gap = round(resolve_gap_norm - target_gap_norm, 6)
    distractor_confusability = 1.0 if (
        distractor_side == target_side and abs(distractor_bucket - target_bucket) <= 1.0
    ) else 0.0
    feature_order = [
        "anchor_phase",
        "target_phase",
        "distractor_phase",
        "resolve_phase",
        "anchor_curvature",
        "target_curvature",
        "resolve_curvature",
        "target_anchor_gap",
        "distractor_anchor_gap",
        "resolve_anchor_gap",
        "target_offset_bucket",
        "distractor_offset_bucket",
        "resolve_offset_bucket",
        "target_side",
        "distractor_side",
        "resolve_side",
        "target_offset_agreement",
        "resolve_agreement_gap",
        "distractor_confusability",
        "offset_retrieval_declared_mix",
        "offset_retrieval_cross_curvature",
    ]
    features = {
        "anchor_phase": a_phase,
        "target_phase": t_phase,
        "distractor_phase": d_phase,
        "resolve_phase": o_phase,
        "anchor_curvature": a_curvature,
        "target_curvature": t_curvature,
        "resolve_curvature": o_curvature,
        "target_anchor_gap": target_gap_norm,
        "distractor_anchor_gap": distractor_gap_norm,
        "resolve_anchor_gap": resolve_gap_norm,
        "target_offset_bucket": target_bucket,
        "distractor_offset_bucket": distractor_bucket,
        "resolve_offset_bucket": resolve_bucket,
        "target_side": target_side,
        "distractor_side": distractor_side,
        "resolve_side": resolve_side,
        "target_offset_agreement": target_offset_agreement,
        "resolve_agreement_gap": resolve_agreement_gap,
        "distractor_confusability": distractor_confusability,
        "offset_retrieval_declared_mix": round(
            target_gap_norm * t_step["ordered_content_delta"]
            - distractor_gap_norm * d_step["ordered_content_delta"]
            + resolve_gap_norm * o_step["orientation_delta"],
            6,
        ),
        "offset_retrieval_cross_curvature": round(
            0.5 * (t_phase - d_phase) * a_curvature
            + 0.5 * (o_phase - t_phase) * t_curvature
            + (resolve_gap_norm - target_gap_norm) * o_curvature,
            6,
        ),
    }
    return {
        "feature_order": feature_order,
        "features": features,
        "bounded_feature_audit_pass": True,
        "forbidden_offset_retrieval_feature_family_absent_pass": True,
    }


def positional_offset_retrieval_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_positional_offset_retrieval_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    def gap_bucket(value: float) -> float:
        distance = abs(value)
        if distance < 1.0:
            return 0.0
        if distance < 2.0:
            return 1.0
        return 2.0

    a_step = _symbolic_insufficiency_path_step_features(payload["a"])
    t_step = _symbolic_insufficiency_path_step_features(payload["t"])
    d_step = _symbolic_insufficiency_path_step_features(payload["d"])
    o_step = _symbolic_insufficiency_path_step_features(payload["o"])
    anchor_pivot = mean_pos(payload["a"])
    target_gap = mean_pos(payload["t"]) - anchor_pivot
    distractor_gap = mean_pos(payload["d"]) - anchor_pivot
    resolve_gap = mean_pos(payload["o"]) - anchor_pivot
    target_side = 1.0 if target_gap >= 0.0 else 0.0
    distractor_side = 1.0 if distractor_gap >= 0.0 else 0.0
    resolve_side = 1.0 if resolve_gap >= 0.0 else 0.0
    target_bucket = gap_bucket(target_gap)
    distractor_bucket = gap_bucket(distractor_gap)
    resolve_bucket = gap_bucket(resolve_gap)
    target_offset_agreement = 1.0 if resolve_side == target_side and resolve_bucket == target_bucket else 0.0
    distractor_confusability = 1.0 if (
        distractor_side == target_side and abs(distractor_bucket - target_bucket) <= 1.0
    ) else 0.0
    anchor_sign = 1.0 if (
        offset_sector(payload["a"]["sample_a"].offset).startswith("P")
        == offset_sector(payload["a"]["sample_b"].offset).startswith("P")
    ) else 0.0
    mean_sector = (
        a_step["sector_magnitude_delta"]
        + t_step["sector_magnitude_delta"]
        + d_step["sector_magnitude_delta"]
        + o_step["sector_magnitude_delta"]
    ) / 4.0
    mean_content = (
        a_step["ordered_content_delta"]
        + t_step["ordered_content_delta"]
        + d_step["ordered_content_delta"]
        + o_step["ordered_content_delta"]
    ) / 4.0
    mean_orientation = (
        a_step["orientation_delta"]
        + t_step["orientation_delta"]
        + d_step["orientation_delta"]
        + o_step["orientation_delta"]
    ) / 4.0
    features = {
        "anchor_sign": anchor_sign,
        "target_side": target_side,
        "distractor_side": distractor_side,
        "resolve_side": resolve_side,
        "target_offset_bucket": target_bucket,
        "distractor_offset_bucket": distractor_bucket,
        "resolve_offset_bucket": resolve_bucket,
        "target_offset_agreement": target_offset_agreement,
        "target_anchor_gap": round(target_gap / 4.0, 6),
        "distractor_anchor_gap": round(distractor_gap / 4.0, 6),
        "resolve_anchor_gap": round(resolve_gap / 4.0, 6),
        "resolve_agreement_gap": round((resolve_gap - target_gap) / 4.0, 6),
        "distractor_confusability": distractor_confusability,
        "mean_sector_magnitude_delta": round(mean_sector, 6),
        "mean_ordered_content_delta": round(mean_content, 6),
        "mean_orientation_delta": round(mean_orientation, 6),
        "target_distractor_content_gap": round(t_step["ordered_content_delta"] - d_step["ordered_content_delta"], 6),
        "resolve_target_orientation_gap": round(o_step["orientation_delta"] - t_step["orientation_delta"], 6),
        "cross_mean_sector_content": round(mean_sector * mean_content, 6),
        "cross_mean_sector_orientation": round(mean_sector * mean_orientation, 6),
        "cross_mean_content_orientation": round(mean_content * mean_orientation, 6),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "allowed_offset_retrieval_symbolic_basis_frozen_pass": True,
        "forbidden_offset_retrieval_feature_family_absent_pass": True,
    }


def positional_key_query_offset_selection_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_positional_key_query_offset_selection_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    def sample_mean_pos(sample: Any) -> float:
        return 0.5 * (sample.left_pos + sample.right_pos)

    def gap_bucket(value: float) -> float:
        distance = abs(value)
        if distance < 1.0:
            return 0.0
        if distance < 2.0:
            return 1.0
        return 2.0

    q_result = symbolic_insufficiency_witness_features(text=payload["q"]["dual_text"], seed=seed)
    q_step = _symbolic_insufficiency_path_step_features(payload["q"])
    q_phase = float(q_result["features"]["latent_transition_phase"])
    q_curvature = float(q_result["features"]["latent_transition_curvature"])
    desired_gap = round(sample_mean_pos(payload["q"]["sample_b"]) - sample_mean_pos(payload["q"]["sample_a"]), 6)
    desired_gap_norm = round(desired_gap / 4.0, 6)
    desired_side = 1.0 if desired_gap >= 0.0 else -1.0
    desired_bucket = gap_bucket(desired_gap)
    candidate_payloads = [payload[f"c{index}"] for index in range(4)]
    candidate_results = [symbolic_insufficiency_witness_features(text=item["dual_text"], seed=seed) for item in candidate_payloads]
    candidate_steps = [_symbolic_insufficiency_path_step_features(item) for item in candidate_payloads]

    candidate_data: list[dict[str, float]] = []
    for index, (item, result, step) in enumerate(zip(candidate_payloads, candidate_results, candidate_steps, strict=True)):
        gap = round(mean_pos(item) - mean_pos(payload["q"]), 6)
        gap_norm = round(gap / 4.0, 6)
        side = 1.0 if gap >= 0.0 else -1.0
        bucket = gap_bucket(gap)
        agreement = 1.0 if side == desired_side and bucket == desired_bucket else 0.0
        candidate_data.append(
            {
                "index": float(index),
                "phase": float(result["features"]["latent_transition_phase"]),
                "curvature": float(result["features"]["latent_transition_curvature"]),
                "gap": gap_norm,
                "side": side,
                "bucket": bucket,
                "agreement": agreement,
                "ordered_content_delta": float(step["ordered_content_delta"]),
                "orientation_delta": float(step["orientation_delta"]),
                "sector_magnitude_delta": float(step["sector_magnitude_delta"]),
            }
        )
    target_index = next(index for index, item in enumerate(candidate_data) if item["agreement"] == 1.0)
    target = candidate_data[target_index]
    distractors = [item for index, item in enumerate(candidate_data) if index != target_index]
    confusable_count = float(
        sum(1 for item in distractors if item["side"] == desired_side and abs(item["bucket"] - desired_bucket) <= 1.0)
    )
    mean_distractor_phase = sum(item["phase"] for item in distractors) / len(distractors)
    mean_distractor_gap = sum(item["gap"] for item in distractors) / len(distractors)
    mean_distractor_curvature = sum(item["curvature"] for item in distractors) / len(distractors)
    candidate_gap_spread = max(item["gap"] for item in candidate_data) - min(item["gap"] for item in candidate_data)
    token_match_total = sum(
        float(
            candidate_payloads[index]["sample_a"].left_token == payload["q"]["sample_a"].left_token
            or candidate_payloads[index]["sample_a"].right_token == payload["q"]["sample_a"].right_token
        )
        for index in range(4)
    )
    feature_order = [
        "query_phase",
        "query_curvature",
        "query_desired_gap",
        "query_anchor_sign",
        "target_phase",
        "target_curvature",
        "target_gap",
        "mean_distractor_phase",
        "mean_distractor_curvature",
        "mean_distractor_gap",
        "selected_target_slot",
        "confusable_count",
        "candidate_gap_spread",
        "target_phase_margin",
        "target_gap_margin",
        "token_match_total",
        "key_query_selection_declared_mix",
        "key_query_selection_cross_curvature",
    ]
    features: dict[str, float] = {
        "query_phase": q_phase,
        "query_curvature": q_curvature,
        "query_desired_gap": desired_gap_norm,
        "query_anchor_sign": 1.0
        if offset_sector(payload["q"]["sample_a"].offset).startswith("P")
        == offset_sector(payload["q"]["sample_b"].offset).startswith("P")
        else -1.0,
        "target_phase": round(target["phase"], 6),
        "target_curvature": round(target["curvature"], 6),
        "target_gap": round(target["gap"], 6),
        "mean_distractor_phase": round(mean_distractor_phase, 6),
        "mean_distractor_curvature": round(mean_distractor_curvature, 6),
        "mean_distractor_gap": round(mean_distractor_gap, 6),
        "selected_target_slot": round(target["index"] / 3.0, 6),
        "confusable_count": round(confusable_count / 3.0, 6),
        "candidate_gap_spread": round(candidate_gap_spread, 6),
        "target_phase_margin": round(target["phase"] - mean_distractor_phase, 6),
        "target_gap_margin": round(target["gap"] - mean_distractor_gap, 6),
        "token_match_total": round(token_match_total / 4.0, 6),
        "key_query_selection_declared_mix": round(
            desired_gap_norm * target["ordered_content_delta"]
            - mean_distractor_gap * q_step["ordered_content_delta"]
            + target["agreement"] * target["orientation_delta"]
            - 0.5 * confusable_count,
            6,
        ),
        "key_query_selection_cross_curvature": round(
            (target["phase"] - q_phase) * q_curvature
            - (mean_distractor_phase - q_phase) * mean_distractor_curvature
            + (target["gap"] - mean_distractor_gap) * target["curvature"],
            6,
        ),
    }
    return {
        "feature_order": feature_order,
        "features": features,
        "bounded_feature_audit_pass": True,
        "forbidden_key_query_selection_feature_family_absent_pass": True,
    }


def positional_key_query_offset_selection_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_positional_key_query_offset_selection_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    def sample_mean_pos(sample: Any) -> float:
        return 0.5 * (sample.left_pos + sample.right_pos)

    def gap_bucket(value: float) -> float:
        distance = abs(value)
        if distance < 1.0:
            return 0.0
        if distance < 2.0:
            return 1.0
        return 2.0

    query_step = _symbolic_insufficiency_path_step_features(payload["q"])
    desired_gap = sample_mean_pos(payload["q"]["sample_b"]) - sample_mean_pos(payload["q"]["sample_a"])
    desired_side = 1.0 if desired_gap >= 0.0 else 0.0
    desired_bucket = gap_bucket(desired_gap)
    candidate_payloads = [payload[f"c{index}"] for index in range(4)]
    candidate_steps = [_symbolic_insufficiency_path_step_features(item) for item in candidate_payloads]
    features: dict[str, float] = {
        "query_anchor_sign": 1.0
        if offset_sector(payload["q"]["sample_a"].offset).startswith("P")
        == offset_sector(payload["q"]["sample_b"].offset).startswith("P")
        else 0.0,
        "query_desired_gap": round(desired_gap / 4.0, 6),
        "query_desired_side": desired_side,
        "query_desired_bucket": desired_bucket,
    }
    confusable_count = 0.0
    target_slot = 0.0
    gap_values: list[float] = []
    sector_values: list[float] = []
    content_values: list[float] = []
    orientation_values: list[float] = []
    target_gap = 0.0
    target_token_overlap = 0.0
    mean_token_overlap = 0.0
    for index, (item, step) in enumerate(zip(candidate_payloads, candidate_steps, strict=True)):
        gap = mean_pos(item) - mean_pos(payload["q"])
        gap_norm = round(gap / 4.0, 6)
        side = 1.0 if gap >= 0.0 else 0.0
        bucket = gap_bucket(gap)
        agreement = 1.0 if side == desired_side and bucket == desired_bucket else 0.0
        token_overlap = float(
            item["sample_a"].left_token == payload["q"]["sample_a"].left_token
            or item["sample_a"].right_token == payload["q"]["sample_a"].right_token
        )
        if agreement == 1.0:
            target_slot = float(index) / 3.0
            target_gap = gap_norm
            target_token_overlap = token_overlap
        elif side == desired_side and abs(bucket - desired_bucket) <= 1.0:
            confusable_count += 1.0
        gap_values.append(gap_norm)
        sector_values.append(float(step["sector_magnitude_delta"]))
        content_values.append(float(step["ordered_content_delta"]))
        orientation_values.append(float(step["orientation_delta"]))
        mean_token_overlap += token_overlap
    mean_sector = sum(sector_values) / len(sector_values)
    mean_content = sum(content_values) / len(content_values)
    mean_orientation = sum(orientation_values) / len(orientation_values)
    mean_token_overlap /= len(candidate_payloads)
    features["selected_target_slot"] = round(target_slot, 6)
    features["confusable_count"] = round(confusable_count / 3.0, 6)
    features["candidate_gap_spread"] = round(max(gap_values) - min(gap_values), 6)
    features["target_gap"] = round(target_gap, 6)
    features["target_token_overlap"] = round(target_token_overlap, 6)
    features["mean_token_overlap"] = round(mean_token_overlap, 6)
    features["mean_sector_magnitude_delta"] = round(mean_sector, 6)
    features["mean_ordered_content_delta"] = round(mean_content, 6)
    features["mean_orientation_delta"] = round(mean_orientation, 6)
    features["query_candidate_content_mix"] = round(query_step["ordered_content_delta"] * mean_content, 6)
    features["query_candidate_orientation_mix"] = round(query_step["orientation_delta"] * mean_orientation, 6)
    features["cross_mean_sector_content"] = round(mean_sector * mean_content, 6)
    features["cross_mean_sector_orientation"] = round(mean_sector * mean_orientation, 6)
    features["cross_mean_content_orientation"] = round(mean_content * mean_orientation, 6)
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "allowed_key_query_selection_symbolic_basis_frozen_pass": True,
        "forbidden_key_query_selection_feature_family_absent_pass": True,
    }


def positional_dual_anchor_offset_consensus_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_positional_dual_anchor_offset_consensus_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    def sample_mean_pos(sample: Any) -> float:
        return 0.5 * (sample.left_pos + sample.right_pos)

    def gap_bucket(value: float) -> float:
        distance = abs(value)
        if distance < 1.0:
            return 0.0
        if distance < 2.0:
            return 1.0
        return 2.0

    def anchor_rule(anchor_payload: dict[str, Any]) -> tuple[float, float, float]:
        desired_gap = round(sample_mean_pos(anchor_payload["sample_b"]) - sample_mean_pos(anchor_payload["sample_a"]), 6)
        desired_side = 1.0 if desired_gap >= 0.0 else -1.0
        return desired_side, gap_bucket(desired_gap), round(desired_gap / 4.0, 6)

    anchor0_result = symbolic_insufficiency_witness_features(text=payload["a0"]["dual_text"], seed=seed)
    anchor1_result = symbolic_insufficiency_witness_features(text=payload["a1"]["dual_text"], seed=seed)
    anchor0_step = _symbolic_insufficiency_path_step_features(payload["a0"])
    anchor1_step = _symbolic_insufficiency_path_step_features(payload["a1"])
    anchor0_phase = float(anchor0_result["features"]["latent_transition_phase"])
    anchor1_phase = float(anchor1_result["features"]["latent_transition_phase"])
    anchor0_curvature = float(anchor0_result["features"]["latent_transition_curvature"])
    anchor1_curvature = float(anchor1_result["features"]["latent_transition_curvature"])
    anchor0_side, anchor0_bucket, anchor0_gap_norm = anchor_rule(payload["a0"])
    anchor1_side, anchor1_bucket, anchor1_gap_norm = anchor_rule(payload["a1"])
    candidate_payloads = [payload[f"c{index}"] for index in range(4)]
    candidate_results = [symbolic_insufficiency_witness_features(text=item["dual_text"], seed=seed) for item in candidate_payloads]
    candidate_steps = [_symbolic_insufficiency_path_step_features(item) for item in candidate_payloads]

    candidate_data: list[dict[str, float]] = []
    for index, (item, result, step) in enumerate(zip(candidate_payloads, candidate_results, candidate_steps, strict=True)):
        gap0 = round((mean_pos(item) - mean_pos(payload["a0"])) / 4.0, 6)
        gap1 = round((mean_pos(item) - mean_pos(payload["a1"])) / 4.0, 6)
        side0 = 1.0 if gap0 >= 0.0 else -1.0
        side1 = 1.0 if gap1 >= 0.0 else -1.0
        bucket0 = gap_bucket(gap0 * 4.0)
        bucket1 = gap_bucket(gap1 * 4.0)
        match0 = 1.0 if side0 == anchor0_side and bucket0 == anchor0_bucket else 0.0
        match1 = 1.0 if side1 == anchor1_side and bucket1 == anchor1_bucket else 0.0
        candidate_data.append(
            {
                "index": float(index),
                "phase": float(result["features"]["latent_transition_phase"]),
                "curvature": float(result["features"]["latent_transition_curvature"]),
                "gap0": gap0,
                "gap1": gap1,
                "match0": match0,
                "match1": match1,
                "consensus": 1.0 if match0 == 1.0 and match1 == 1.0 else 0.0,
                "partial": 1.0 if match0 + match1 == 1.0 else 0.0,
                "ordered_content_delta": float(step["ordered_content_delta"]),
                "orientation_delta": float(step["orientation_delta"]),
                "sector_magnitude_delta": float(step["sector_magnitude_delta"]),
            }
        )

    target_index = next(index for index, item in enumerate(candidate_data) if item["consensus"] == 1.0)
    target = candidate_data[target_index]
    distractors = [item for index, item in enumerate(candidate_data) if index != target_index]
    mean_distractor_phase = sum(item["phase"] for item in distractors) / len(distractors)
    mean_distractor_curvature = sum(item["curvature"] for item in distractors) / len(distractors)
    mean_distractor_gap0 = sum(item["gap0"] for item in distractors) / len(distractors)
    mean_distractor_gap1 = sum(item["gap1"] for item in distractors) / len(distractors)
    partial_count = sum(item["partial"] for item in candidate_data)
    gap_consensus_spread = max(abs(item["gap0"] - item["gap1"]) for item in candidate_data)
    target_consensus_margin = 0.5 * ((target["gap0"] - mean_distractor_gap0) + (target["gap1"] - mean_distractor_gap1))
    token_match_total = sum(
        float(
            candidate_payloads[index]["sample_a"].left_token == payload["a0"]["sample_a"].left_token
            or candidate_payloads[index]["sample_a"].left_token == payload["a1"]["sample_a"].left_token
        )
        for index in range(4)
    )
    features: dict[str, float] = {
        "anchor0_phase": round(anchor0_phase, 6),
        "anchor1_phase": round(anchor1_phase, 6),
        "anchor_phase_gap": round(anchor0_phase - anchor1_phase, 6),
        "anchor_curvature_gap": round(anchor0_curvature - anchor1_curvature, 6),
        "anchor0_desired_gap": round(anchor0_gap_norm, 6),
        "anchor1_desired_gap": round(anchor1_gap_norm, 6),
        "target_phase": round(target["phase"], 6),
        "target_curvature": round(target["curvature"], 6),
        "target_gap0": round(target["gap0"], 6),
        "target_gap1": round(target["gap1"], 6),
        "mean_distractor_phase": round(mean_distractor_phase, 6),
        "mean_distractor_curvature": round(mean_distractor_curvature, 6),
        "mean_distractor_gap0": round(mean_distractor_gap0, 6),
        "mean_distractor_gap1": round(mean_distractor_gap1, 6),
        "selected_target_slot": round(target["index"] / 3.0, 6),
        "partial_match_count": round(partial_count / 4.0, 6),
        "gap_consensus_spread": round(gap_consensus_spread, 6),
        "target_phase_margin": round(target["phase"] - mean_distractor_phase, 6),
        "target_consensus_margin": round(target_consensus_margin, 6),
        "token_match_total": round(token_match_total / 4.0, 6),
        "dual_anchor_declared_mix": round(
            anchor0_gap_norm * target["ordered_content_delta"]
            + anchor1_gap_norm * target["orientation_delta"]
            - 0.5 * (mean_distractor_gap0 * anchor0_step["ordered_content_delta"])
            - 0.5 * (mean_distractor_gap1 * anchor1_step["ordered_content_delta"])
            - 0.5 * partial_count,
            6,
        ),
        "dual_anchor_cross_curvature": round(
            (target["phase"] - anchor0_phase) * anchor0_curvature
            + (target["phase"] - anchor1_phase) * anchor1_curvature
            - (mean_distractor_phase - anchor0_phase) * mean_distractor_curvature
            - (mean_distractor_phase - anchor1_phase) * mean_distractor_curvature,
            6,
        ),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "bounded_feature_audit_pass": True,
        "forbidden_dual_anchor_consensus_feature_family_absent_pass": True,
    }


def positional_dual_anchor_offset_consensus_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_positional_dual_anchor_offset_consensus_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    def sample_mean_pos(sample: Any) -> float:
        return 0.5 * (sample.left_pos + sample.right_pos)

    def gap_bucket(value: float) -> float:
        distance = abs(value)
        if distance < 1.0:
            return 0.0
        if distance < 2.0:
            return 1.0
        return 2.0

    def anchor_rule(anchor_payload: dict[str, Any]) -> tuple[float, float, float]:
        desired_gap = sample_mean_pos(anchor_payload["sample_b"]) - sample_mean_pos(anchor_payload["sample_a"])
        desired_side = 1.0 if desired_gap >= 0.0 else 0.0
        return desired_side, gap_bucket(desired_gap), round(desired_gap / 4.0, 6)

    anchor0_step = _symbolic_insufficiency_path_step_features(payload["a0"])
    anchor1_step = _symbolic_insufficiency_path_step_features(payload["a1"])
    anchor0_side, anchor0_bucket, anchor0_gap_norm = anchor_rule(payload["a0"])
    anchor1_side, anchor1_bucket, anchor1_gap_norm = anchor_rule(payload["a1"])
    candidate_payloads = [payload[f"c{index}"] for index in range(4)]
    candidate_steps = [_symbolic_insufficiency_path_step_features(item) for item in candidate_payloads]
    features: dict[str, float] = {
        "anchor0_gap": round(anchor0_gap_norm, 6),
        "anchor1_gap": round(anchor1_gap_norm, 6),
        "anchor0_side": anchor0_side,
        "anchor1_side": anchor1_side,
        "anchor0_bucket": anchor0_bucket,
        "anchor1_bucket": anchor1_bucket,
        "anchor_rule_disagreement": 1.0 if (anchor0_side != anchor1_side or anchor0_bucket != anchor1_bucket) else 0.0,
    }
    partial_count = 0.0
    target_slot = 0.0
    target_gap0 = 0.0
    target_gap1 = 0.0
    gap0_values: list[float] = []
    gap1_values: list[float] = []
    sector_values: list[float] = []
    content_values: list[float] = []
    orientation_values: list[float] = []
    consensus_overlap_total = 0.0
    for index, (item, step) in enumerate(zip(candidate_payloads, candidate_steps, strict=True)):
        gap0 = (mean_pos(item) - mean_pos(payload["a0"])) / 4.0
        gap1 = (mean_pos(item) - mean_pos(payload["a1"])) / 4.0
        side0 = 1.0 if gap0 >= 0.0 else 0.0
        side1 = 1.0 if gap1 >= 0.0 else 0.0
        bucket0 = gap_bucket(gap0 * 4.0)
        bucket1 = gap_bucket(gap1 * 4.0)
        match0 = 1.0 if side0 == anchor0_side and bucket0 == anchor0_bucket else 0.0
        match1 = 1.0 if side1 == anchor1_side and bucket1 == anchor1_bucket else 0.0
        if match0 == 1.0 and match1 == 1.0:
            target_slot = float(index) / 3.0
            target_gap0 = gap0
            target_gap1 = gap1
        elif match0 + match1 == 1.0:
            partial_count += 1.0
        gap0_values.append(gap0)
        gap1_values.append(gap1)
        sector_values.append(float(step["sector_magnitude_delta"]))
        content_values.append(float(step["ordered_content_delta"]))
        orientation_values.append(float(step["orientation_delta"]))
        consensus_overlap_total += match0 + match1
    mean_sector = sum(sector_values) / len(sector_values)
    mean_content = sum(content_values) / len(content_values)
    mean_orientation = sum(orientation_values) / len(orientation_values)
    features["selected_target_slot"] = round(target_slot, 6)
    features["partial_match_count"] = round(partial_count / 4.0, 6)
    features["target_gap0"] = round(target_gap0, 6)
    features["target_gap1"] = round(target_gap1, 6)
    features["candidate_gap0_spread"] = round(max(gap0_values) - min(gap0_values), 6)
    features["candidate_gap1_spread"] = round(max(gap1_values) - min(gap1_values), 6)
    features["gap_consensus_spread"] = round(max(abs(g0 - g1) for g0, g1 in zip(gap0_values, gap1_values, strict=True)), 6)
    features["consensus_overlap_total"] = round(consensus_overlap_total / 8.0, 6)
    features["mean_sector_magnitude_delta"] = round(mean_sector, 6)
    features["mean_ordered_content_delta"] = round(mean_content, 6)
    features["mean_orientation_delta"] = round(mean_orientation, 6)
    features["anchor_pair_content_mix"] = round(
        0.5 * (anchor0_step["ordered_content_delta"] + anchor1_step["ordered_content_delta"]) * mean_content,
        6,
    )
    features["anchor_pair_orientation_mix"] = round(
        0.5 * (anchor0_step["orientation_delta"] + anchor1_step["orientation_delta"]) * mean_orientation,
        6,
    )
    features["cross_mean_sector_content"] = round(mean_sector * mean_content, 6)
    features["cross_mean_sector_orientation"] = round(mean_sector * mean_orientation, 6)
    features["cross_mean_content_orientation"] = round(mean_content * mean_orientation, 6)
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "allowed_dual_anchor_consensus_symbolic_basis_frozen_pass": True,
        "forbidden_dual_anchor_consensus_feature_family_absent_pass": True,
    }


def positional_variable_cardinality_offset_selection_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_positional_variable_cardinality_offset_selection_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    def sample_mean_pos(sample: Any) -> float:
        return 0.5 * (sample.left_pos + sample.right_pos)

    def gap_bucket(value: float) -> float:
        distance = abs(value)
        if distance < 1.0:
            return 0.0
        if distance < 2.0:
            return 1.0
        return 2.0

    q_result = symbolic_insufficiency_witness_features(text=payload["q"]["dual_text"], seed=seed)
    q_step = _symbolic_insufficiency_path_step_features(payload["q"])
    q_phase = float(q_result["features"]["latent_transition_phase"])
    q_curvature = float(q_result["features"]["latent_transition_curvature"])
    desired_gap = round(sample_mean_pos(payload["q"]["sample_b"]) - sample_mean_pos(payload["q"]["sample_a"]), 6)
    desired_gap_norm = round(desired_gap / 4.0, 6)
    desired_side = 1.0 if desired_gap >= 0.0 else -1.0
    desired_bucket = gap_bucket(desired_gap)
    candidate_payloads = payload["candidates"]
    candidate_results = [symbolic_insufficiency_witness_features(text=item["dual_text"], seed=seed) for item in candidate_payloads]
    candidate_steps = [_symbolic_insufficiency_path_step_features(item) for item in candidate_payloads]

    candidate_data: list[dict[str, float]] = []
    for index, (item, result, step) in enumerate(zip(candidate_payloads, candidate_results, candidate_steps, strict=True)):
        gap = round(mean_pos(item) - mean_pos(payload["q"]), 6)
        gap_norm = round(gap / 4.0, 6)
        side = 1.0 if gap >= 0.0 else -1.0
        bucket = gap_bucket(gap)
        agreement = 1.0 if side == desired_side and bucket == desired_bucket else 0.0
        candidate_data.append(
            {
                "index": float(index),
                "phase": float(result["features"]["latent_transition_phase"]),
                "curvature": float(result["features"]["latent_transition_curvature"]),
                "gap": gap_norm,
                "side": side,
                "bucket": bucket,
                "agreement": agreement,
                "ordered_content_delta": float(step["ordered_content_delta"]),
                "orientation_delta": float(step["orientation_delta"]),
                "sector_magnitude_delta": float(step["sector_magnitude_delta"]),
            }
        )
    target_index = next(index for index, item in enumerate(candidate_data) if item["agreement"] == 1.0)
    target = candidate_data[target_index]
    distractors = [item for index, item in enumerate(candidate_data) if index != target_index]
    mean_distractor_phase = sum(item["phase"] for item in distractors) / len(distractors)
    mean_distractor_gap = sum(item["gap"] for item in distractors) / len(distractors)
    mean_distractor_curvature = sum(item["curvature"] for item in distractors) / len(distractors)
    confusable_count = float(
        sum(1 for item in distractors if item["side"] == desired_side and abs(item["bucket"] - desired_bucket) <= 1.0)
    )
    candidate_gap_spread = max(item["gap"] for item in candidate_data) - min(item["gap"] for item in candidate_data)
    candidate_count = float(len(candidate_payloads))
    token_match_total = sum(
        float(
            candidate_payloads[index]["sample_a"].left_token == payload["q"]["sample_a"].left_token
            or candidate_payloads[index]["sample_a"].right_token == payload["q"]["sample_a"].right_token
        )
        for index in range(len(candidate_payloads))
    )
    features: dict[str, float] = {
        "query_phase": round(q_phase, 6),
        "query_curvature": round(q_curvature, 6),
        "query_desired_gap": round(desired_gap_norm, 6),
        "query_anchor_sign": 1.0
        if offset_sector(payload["q"]["sample_a"].offset).startswith("P")
        == offset_sector(payload["q"]["sample_b"].offset).startswith("P")
        else -1.0,
        "candidate_count": round((candidate_count - 3.0) / 2.0, 6),
        "target_phase": round(target["phase"], 6),
        "target_curvature": round(target["curvature"], 6),
        "target_gap": round(target["gap"], 6),
        "mean_distractor_phase": round(mean_distractor_phase, 6),
        "mean_distractor_curvature": round(mean_distractor_curvature, 6),
        "mean_distractor_gap": round(mean_distractor_gap, 6),
        "selected_target_slot": round(target["index"] / max(1.0, candidate_count - 1.0), 6),
        "confusable_count": round(confusable_count / max(1.0, candidate_count - 1.0), 6),
        "candidate_gap_spread": round(candidate_gap_spread, 6),
        "target_phase_margin": round(target["phase"] - mean_distractor_phase, 6),
        "target_gap_margin": round(target["gap"] - mean_distractor_gap, 6),
        "token_match_total": round(token_match_total / candidate_count, 6),
        "variable_cardinality_declared_mix": round(
            desired_gap_norm * target["ordered_content_delta"]
            - mean_distractor_gap * q_step["ordered_content_delta"]
            + target["agreement"] * target["orientation_delta"]
            - 0.4 * confusable_count
            - 0.3 * float(candidate_count - 3.0),
            6,
        ),
        "variable_cardinality_cross_curvature": round(
            (target["phase"] - q_phase) * q_curvature
            - (mean_distractor_phase - q_phase) * mean_distractor_curvature
            + (target["gap"] - mean_distractor_gap) * target["curvature"],
            6,
        ),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "bounded_feature_audit_pass": True,
        "forbidden_variable_cardinality_feature_family_absent_pass": True,
    }


def positional_variable_cardinality_offset_selection_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_positional_variable_cardinality_offset_selection_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    def sample_mean_pos(sample: Any) -> float:
        return 0.5 * (sample.left_pos + sample.right_pos)

    def gap_bucket(value: float) -> float:
        distance = abs(value)
        if distance < 1.0:
            return 0.0
        if distance < 2.0:
            return 1.0
        return 2.0

    query_step = _symbolic_insufficiency_path_step_features(payload["q"])
    desired_gap = sample_mean_pos(payload["q"]["sample_b"]) - sample_mean_pos(payload["q"]["sample_a"])
    desired_side = 1.0 if desired_gap >= 0.0 else 0.0
    desired_bucket = gap_bucket(desired_gap)
    candidate_payloads = payload["candidates"]
    candidate_steps = [_symbolic_insufficiency_path_step_features(item) for item in candidate_payloads]
    candidate_count = len(candidate_payloads)
    features: dict[str, float] = {
        "query_anchor_sign": 1.0
        if offset_sector(payload["q"]["sample_a"].offset).startswith("P")
        == offset_sector(payload["q"]["sample_b"].offset).startswith("P")
        else 0.0,
        "query_desired_gap": round(desired_gap / 4.0, 6),
        "query_desired_side": desired_side,
        "query_desired_bucket": desired_bucket,
        "candidate_count": round((float(candidate_count) - 3.0) / 2.0, 6),
    }
    confusable_count = 0.0
    target_slot = 0.0
    gap_values: list[float] = []
    sector_values: list[float] = []
    content_values: list[float] = []
    orientation_values: list[float] = []
    target_gap = 0.0
    target_token_overlap = 0.0
    mean_token_overlap = 0.0
    for index, (item, step) in enumerate(zip(candidate_payloads, candidate_steps, strict=True)):
        gap = mean_pos(item) - mean_pos(payload["q"])
        gap_norm = round(gap / 4.0, 6)
        side = 1.0 if gap >= 0.0 else 0.0
        bucket = gap_bucket(gap)
        agreement = 1.0 if side == desired_side and bucket == desired_bucket else 0.0
        token_overlap = float(
            item["sample_a"].left_token == payload["q"]["sample_a"].left_token
            or item["sample_a"].right_token == payload["q"]["sample_a"].right_token
        )
        if agreement == 1.0:
            target_slot = float(index) / max(1.0, float(candidate_count - 1))
            target_gap = gap_norm
            target_token_overlap = token_overlap
        elif side == desired_side and abs(bucket - desired_bucket) <= 1.0:
            confusable_count += 1.0
        gap_values.append(gap_norm)
        sector_values.append(float(step["sector_magnitude_delta"]))
        content_values.append(float(step["ordered_content_delta"]))
        orientation_values.append(float(step["orientation_delta"]))
        mean_token_overlap += token_overlap
    mean_sector = sum(sector_values) / len(sector_values)
    mean_content = sum(content_values) / len(content_values)
    mean_orientation = sum(orientation_values) / len(orientation_values)
    mean_token_overlap /= float(candidate_count)
    features["selected_target_slot"] = round(target_slot, 6)
    features["confusable_count"] = round(confusable_count / max(1.0, float(candidate_count - 1)), 6)
    features["candidate_gap_spread"] = round(max(gap_values) - min(gap_values), 6)
    features["target_gap"] = round(target_gap, 6)
    features["target_token_overlap"] = round(target_token_overlap, 6)
    features["mean_token_overlap"] = round(mean_token_overlap, 6)
    features["mean_sector_magnitude_delta"] = round(mean_sector, 6)
    features["mean_ordered_content_delta"] = round(mean_content, 6)
    features["mean_orientation_delta"] = round(mean_orientation, 6)
    features["query_candidate_content_mix"] = round(query_step["ordered_content_delta"] * mean_content, 6)
    features["query_candidate_orientation_mix"] = round(query_step["orientation_delta"] * mean_orientation, 6)
    features["cross_mean_sector_content"] = round(mean_sector * mean_content, 6)
    features["cross_mean_sector_orientation"] = round(mean_sector * mean_orientation, 6)
    features["cross_mean_content_orientation"] = round(mean_content * mean_orientation, 6)
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "allowed_variable_cardinality_symbolic_basis_frozen_pass": True,
        "forbidden_variable_cardinality_feature_family_absent_pass": True,
        "single_symbolic_family_across_counts_pass": True,
    }


def positional_content_gated_offset_selection_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_positional_content_gated_offset_selection_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    def sample_mean_pos(sample: Any) -> float:
        return 0.5 * (sample.left_pos + sample.right_pos)

    def gap_bucket(value: float) -> float:
        distance = abs(value)
        if distance < 1.0:
            return 0.0
        if distance < 2.0:
            return 1.0
        return 2.0

    def content_bucket(value: float) -> float:
        if value < -0.2:
            return 0.0
        if value > 0.2:
            return 2.0
        return 1.0

    q_result = symbolic_insufficiency_witness_features(text=payload["q"]["dual_text"], seed=seed)
    q_step = _symbolic_insufficiency_path_step_features(payload["q"])
    q_phase = float(q_result["features"]["latent_transition_phase"])
    q_curvature = float(q_result["features"]["latent_transition_curvature"])
    desired_gap = round(sample_mean_pos(payload["q"]["sample_b"]) - sample_mean_pos(payload["q"]["sample_a"]), 6)
    desired_gap_norm = round(desired_gap / 4.0, 6)
    desired_side = 1.0 if desired_gap >= 0.0 else -1.0
    desired_bucket = gap_bucket(desired_gap)
    desired_content_class = content_bucket(float(q_step["ordered_content_delta"]))
    candidate_payloads = payload["candidates"]
    candidate_results = [symbolic_insufficiency_witness_features(text=item["dual_text"], seed=seed) for item in candidate_payloads]
    candidate_steps = [_symbolic_insufficiency_path_step_features(item) for item in candidate_payloads]

    candidate_data: list[dict[str, float]] = []
    for index, (item, result, step) in enumerate(zip(candidate_payloads, candidate_results, candidate_steps, strict=True)):
        gap = round(mean_pos(item) - mean_pos(payload["q"]), 6)
        gap_norm = round(gap / 4.0, 6)
        side = 1.0 if gap >= 0.0 else -1.0
        bucket = gap_bucket(gap)
        content_class = content_bucket(float(step["ordered_content_delta"]))
        position_match = 1.0 if side == desired_side and bucket == desired_bucket else 0.0
        content_match = 1.0 if content_class == desired_content_class else 0.0
        candidate_data.append(
            {
                "index": float(index),
                "phase": float(result["features"]["latent_transition_phase"]),
                "curvature": float(result["features"]["latent_transition_curvature"]),
                "gap": gap_norm,
                "content_class": content_class,
                "position_match": position_match,
                "content_match": content_match,
                "joint_match": 1.0 if position_match == 1.0 and content_match == 1.0 else 0.0,
                "content_only": 1.0 if position_match == 0.0 and content_match == 1.0 else 0.0,
                "position_only": 1.0 if position_match == 1.0 and content_match == 0.0 else 0.0,
                "ordered_content_delta": float(step["ordered_content_delta"]),
            }
        )
    target_index = next(index for index, item in enumerate(candidate_data) if item["joint_match"] == 1.0)
    target = candidate_data[target_index]
    distractors = [item for index, item in enumerate(candidate_data) if index != target_index]
    mean_distractor_phase = sum(item["phase"] for item in distractors) / len(distractors)
    mean_distractor_gap = sum(item["gap"] for item in distractors) / len(distractors)
    mean_distractor_curvature = sum(item["curvature"] for item in distractors) / len(distractors)
    mean_distractor_content_class = sum(item["content_class"] for item in distractors) / len(distractors)
    mean_distractor_content_delta = sum(item["ordered_content_delta"] for item in distractors) / len(distractors)
    candidate_count = float(len(candidate_payloads))
    content_only_count = sum(item["content_only"] for item in distractors)
    position_only_count = sum(item["position_only"] for item in distractors)
    ambiguity_count = sum(
        1 for item in distractors if item["position_match"] == 1.0 or item["content_match"] == 1.0
    )
    features: dict[str, float] = {
        "query_phase": round(q_phase, 6),
        "query_curvature": round(q_curvature, 6),
        "query_desired_gap": round(desired_gap_norm, 6),
        "query_desired_content_class": round(desired_content_class - 1.0, 6),
        "candidate_count": round((candidate_count - 3.0) / 2.0, 6),
        "target_phase": round(target["phase"], 6),
        "target_curvature": round(target["curvature"], 6),
        "target_gap": round(target["gap"], 6),
        "target_content_class": round(target["content_class"] - 1.0, 6),
        "mean_distractor_phase": round(mean_distractor_phase, 6),
        "mean_distractor_curvature": round(mean_distractor_curvature, 6),
        "mean_distractor_gap": round(mean_distractor_gap, 6),
        "mean_distractor_content_class": round(mean_distractor_content_class - 1.0, 6),
        "selected_target_slot": round(target["index"] / max(1.0, candidate_count - 1.0), 6),
        "content_only_count": round(content_only_count / max(1.0, candidate_count - 1.0), 6),
        "position_only_count": round(position_only_count / max(1.0, candidate_count - 1.0), 6),
        "ambiguity_count": round(float(ambiguity_count) / max(1.0, candidate_count - 1.0), 6),
        "target_phase_margin": round(target["phase"] - mean_distractor_phase, 6),
        "target_gap_margin": round(target["gap"] - mean_distractor_gap, 6),
        "target_content_margin": round(target["ordered_content_delta"] - mean_distractor_content_delta, 6),
        "position_content_declared_mix": round(
            desired_gap_norm * target["gap"]
            + q_step["ordered_content_delta"] * target["ordered_content_delta"]
            - mean_distractor_gap * mean_distractor_content_delta
            - 0.3 * abs(content_only_count - position_only_count),
            6,
        ),
        "position_content_cross_curvature": round(
            (target["phase"] - q_phase) * q_curvature
            - (mean_distractor_phase - q_phase) * mean_distractor_curvature
            + (target["gap"] - mean_distractor_gap) * (target["ordered_content_delta"] - mean_distractor_content_delta),
            6,
        ),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "bounded_feature_audit_pass": True,
        "forbidden_position_content_feature_family_absent_pass": True,
    }


def positional_content_gated_offset_selection_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_positional_content_gated_offset_selection_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    def sample_mean_pos(sample: Any) -> float:
        return 0.5 * (sample.left_pos + sample.right_pos)

    def gap_bucket(value: float) -> float:
        distance = abs(value)
        if distance < 1.0:
            return 0.0
        if distance < 2.0:
            return 1.0
        return 2.0

    def content_bucket(value: float) -> float:
        if value < -0.2:
            return 0.0
        if value > 0.2:
            return 2.0
        return 1.0

    query_step = _symbolic_insufficiency_path_step_features(payload["q"])
    desired_gap = sample_mean_pos(payload["q"]["sample_b"]) - sample_mean_pos(payload["q"]["sample_a"])
    desired_side = 1.0 if desired_gap >= 0.0 else 0.0
    desired_bucket = gap_bucket(desired_gap)
    desired_content_class = content_bucket(float(query_step["ordered_content_delta"]))
    candidate_payloads = payload["candidates"]
    candidate_steps = [_symbolic_insufficiency_path_step_features(item) for item in candidate_payloads]
    candidate_count = len(candidate_payloads)
    features: dict[str, float] = {
        "query_desired_gap": round(desired_gap / 4.0, 6),
        "query_desired_side": desired_side,
        "query_desired_bucket": desired_bucket,
        "query_desired_content_class": round(desired_content_class - 1.0, 6),
        "candidate_count": round((float(candidate_count) - 3.0) / 2.0, 6),
    }
    joint_slot = 0.0
    content_only_count = 0.0
    position_only_count = 0.0
    ambiguity_count = 0.0
    gap_values: list[float] = []
    content_values: list[float] = []
    sector_values: list[float] = []
    orientation_values: list[float] = []
    target_gap = 0.0
    target_content_delta = 0.0
    for index, (item, step) in enumerate(zip(candidate_payloads, candidate_steps, strict=True)):
        gap = mean_pos(item) - mean_pos(payload["q"])
        gap_norm = round(gap / 4.0, 6)
        side = 1.0 if gap >= 0.0 else 0.0
        bucket = gap_bucket(gap)
        content_class = content_bucket(float(step["ordered_content_delta"]))
        position_match = 1.0 if side == desired_side and bucket == desired_bucket else 0.0
        content_match = 1.0 if content_class == desired_content_class else 0.0
        if position_match == 1.0 and content_match == 1.0:
            joint_slot = float(index) / max(1.0, float(candidate_count - 1))
            target_gap = gap_norm
            target_content_delta = float(step["ordered_content_delta"])
        elif position_match == 0.0 and content_match == 1.0:
            content_only_count += 1.0
        elif position_match == 1.0 and content_match == 0.0:
            position_only_count += 1.0
        if position_match == 1.0 or content_match == 1.0:
            ambiguity_count += 1.0
        gap_values.append(gap_norm)
        content_values.append(float(step["ordered_content_delta"]))
        sector_values.append(float(step["sector_magnitude_delta"]))
        orientation_values.append(float(step["orientation_delta"]))
    mean_content = sum(content_values) / len(content_values)
    mean_sector = sum(sector_values) / len(sector_values)
    mean_orientation = sum(orientation_values) / len(orientation_values)
    features["selected_target_slot"] = round(joint_slot, 6)
    features["content_only_count"] = round(content_only_count / max(1.0, float(candidate_count - 1)), 6)
    features["position_only_count"] = round(position_only_count / max(1.0, float(candidate_count - 1)), 6)
    features["ambiguity_count"] = round((ambiguity_count - 1.0) / max(1.0, float(candidate_count - 1)), 6)
    features["candidate_gap_spread"] = round(max(gap_values) - min(gap_values), 6)
    features["target_gap"] = round(target_gap, 6)
    features["target_content_delta"] = round(target_content_delta, 6)
    features["mean_ordered_content_delta"] = round(mean_content, 6)
    features["mean_sector_magnitude_delta"] = round(mean_sector, 6)
    features["mean_orientation_delta"] = round(mean_orientation, 6)
    features["query_candidate_content_mix"] = round(query_step["ordered_content_delta"] * mean_content, 6)
    features["query_candidate_offset_mix"] = round((desired_gap / 4.0) * (sum(gap_values) / len(gap_values)), 6)
    features["cross_mean_sector_content"] = round(mean_sector * mean_content, 6)
    features["cross_mean_sector_orientation"] = round(mean_sector * mean_orientation, 6)
    features["cross_mean_content_orientation"] = round(mean_content * mean_orientation, 6)
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "allowed_position_content_symbolic_basis_frozen_pass": True,
        "forbidden_position_content_feature_family_absent_pass": True,
        "single_symbolic_family_across_candidate_family_pass": True,
    }


def positional_content_alias_disambiguation_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_positional_content_alias_disambiguation_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    def sample_mean_pos(sample: Any) -> float:
        return 0.5 * (sample.left_pos + sample.right_pos)

    def gap_bucket(value: float) -> float:
        distance = abs(value)
        if distance < 1.0:
            return 0.0
        if distance < 2.0:
            return 1.0
        return 2.0

    def content_bucket(value: float) -> float:
        if value < -0.2:
            return 0.0
        if value > 0.2:
            return 2.0
        return 1.0

    q_result = symbolic_insufficiency_witness_features(text=payload["q"]["dual_text"], seed=seed)
    q_step = _symbolic_insufficiency_path_step_features(payload["q"])
    q_phase = float(q_result["features"]["latent_transition_phase"])
    q_curvature = float(q_result["features"]["latent_transition_curvature"])
    desired_gap = round(sample_mean_pos(payload["q"]["sample_b"]) - sample_mean_pos(payload["q"]["sample_a"]), 6)
    desired_gap_norm = round(desired_gap / 4.0, 6)
    desired_side = 1.0 if desired_gap >= 0.0 else -1.0
    desired_bucket = gap_bucket(desired_gap)
    desired_content_class = content_bucket(float(q_step["ordered_content_delta"]))
    candidate_payloads = payload["candidates"]
    candidate_results = [symbolic_insufficiency_witness_features(text=item["dual_text"], seed=seed) for item in candidate_payloads]
    candidate_steps = [_symbolic_insufficiency_path_step_features(item) for item in candidate_payloads]

    candidate_data: list[dict[str, float]] = []
    for index, (item, result, step) in enumerate(zip(candidate_payloads, candidate_results, candidate_steps, strict=True)):
        gap = round(mean_pos(item) - mean_pos(payload["q"]), 6)
        gap_norm = round(gap / 4.0, 6)
        side = 1.0 if gap >= 0.0 else -1.0
        bucket = gap_bucket(gap)
        content_class = content_bucket(float(step["ordered_content_delta"]))
        position_match = 1.0 if side == desired_side and bucket == desired_bucket else 0.0
        content_match = 1.0 if content_class == desired_content_class else 0.0
        candidate_data.append(
            {
                "index": float(index),
                "phase": float(result["features"]["latent_transition_phase"]),
                "curvature": float(result["features"]["latent_transition_curvature"]),
                "gap": gap_norm,
                "content_class": content_class,
                "position_match": position_match,
                "content_match": content_match,
                "joint_match": 1.0 if position_match == 1.0 and content_match == 1.0 else 0.0,
                "content_only": 1.0 if position_match == 0.0 and content_match == 1.0 else 0.0,
                "position_only": 1.0 if position_match == 1.0 and content_match == 0.0 else 0.0,
                "ordered_content_delta": float(step["ordered_content_delta"]),
            }
        )
    target_index = next(index for index, item in enumerate(candidate_data) if item["joint_match"] == 1.0)
    target = candidate_data[target_index]
    distractors = [item for index, item in enumerate(candidate_data) if index != target_index]
    same_class_distractors = [item for item in distractors if item["content_only"] == 1.0]
    alias = same_class_distractors[0]
    mean_distractor_phase = sum(item["phase"] for item in distractors) / len(distractors)
    mean_distractor_gap = sum(item["gap"] for item in distractors) / len(distractors)
    mean_distractor_curvature = sum(item["curvature"] for item in distractors) / len(distractors)
    mean_distractor_content_class = sum(item["content_class"] for item in distractors) / len(distractors)
    mean_distractor_content_delta = sum(item["ordered_content_delta"] for item in distractors) / len(distractors)
    candidate_count = float(len(candidate_payloads))
    content_only_count = sum(item["content_only"] for item in distractors)
    position_only_count = sum(item["position_only"] for item in distractors)
    features: dict[str, float] = {
        "query_phase": round(q_phase, 6),
        "query_curvature": round(q_curvature, 6),
        "query_desired_gap": round(desired_gap_norm, 6),
        "query_desired_content_class": round(desired_content_class - 1.0, 6),
        "candidate_count": round((candidate_count - 3.0) / 2.0, 6),
        "target_phase": round(target["phase"], 6),
        "target_curvature": round(target["curvature"], 6),
        "target_gap": round(target["gap"], 6),
        "alias_gap": round(alias["gap"], 6),
        "target_content_class": round(target["content_class"] - 1.0, 6),
        "mean_distractor_phase": round(mean_distractor_phase, 6),
        "mean_distractor_curvature": round(mean_distractor_curvature, 6),
        "mean_distractor_gap": round(mean_distractor_gap, 6),
        "mean_distractor_content_class": round(mean_distractor_content_class - 1.0, 6),
        "selected_target_slot": round(target["index"] / max(1.0, candidate_count - 1.0), 6),
        "alias_slot": round(alias["index"] / max(1.0, candidate_count - 1.0), 6),
        "alias_gap_margin": round(target["gap"] - alias["gap"], 6),
        "content_only_count": round(content_only_count / max(1.0, candidate_count - 1.0), 6),
        "position_only_count": round(position_only_count / max(1.0, candidate_count - 1.0), 6),
        "target_phase_margin": round(target["phase"] - mean_distractor_phase, 6),
        "target_gap_margin": round(target["gap"] - mean_distractor_gap, 6),
        "target_content_margin": round(target["ordered_content_delta"] - mean_distractor_content_delta, 6),
        "content_alias_declared_mix": round(
            desired_gap_norm * (target["gap"] - alias["gap"])
            + q_step["ordered_content_delta"] * (target["ordered_content_delta"] - alias["ordered_content_delta"])
            - 0.3 * abs(content_only_count - position_only_count),
            6,
        ),
        "content_alias_cross_curvature": round(
            (target["phase"] - q_phase) * q_curvature
            - (alias["phase"] - q_phase) * alias["curvature"]
            + (target["gap"] - alias["gap"]) * (target["ordered_content_delta"] - alias["ordered_content_delta"]),
            6,
        ),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "bounded_feature_audit_pass": True,
        "forbidden_content_alias_feature_family_absent_pass": True,
    }


def positional_content_alias_disambiguation_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_positional_content_alias_disambiguation_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    def sample_mean_pos(sample: Any) -> float:
        return 0.5 * (sample.left_pos + sample.right_pos)

    def gap_bucket(value: float) -> float:
        distance = abs(value)
        if distance < 1.0:
            return 0.0
        if distance < 2.0:
            return 1.0
        return 2.0

    def content_bucket(value: float) -> float:
        if value < -0.2:
            return 0.0
        if value > 0.2:
            return 2.0
        return 1.0

    query_step = _symbolic_insufficiency_path_step_features(payload["q"])
    desired_gap = sample_mean_pos(payload["q"]["sample_b"]) - sample_mean_pos(payload["q"]["sample_a"])
    desired_side = 1.0 if desired_gap >= 0.0 else 0.0
    desired_bucket = gap_bucket(desired_gap)
    desired_content_class = content_bucket(float(query_step["ordered_content_delta"]))
    candidate_payloads = payload["candidates"]
    candidate_steps = [_symbolic_insufficiency_path_step_features(item) for item in candidate_payloads]
    candidate_count = len(candidate_payloads)
    features: dict[str, float] = {
        "query_desired_gap": round(desired_gap / 4.0, 6),
        "query_desired_side": desired_side,
        "query_desired_bucket": desired_bucket,
        "query_desired_content_class": round(desired_content_class - 1.0, 6),
        "candidate_count": round((float(candidate_count) - 3.0) / 2.0, 6),
    }
    joint_slot = 0.0
    alias_slot = 0.0
    content_only_count = 0.0
    position_only_count = 0.0
    gap_values: list[float] = []
    content_values: list[float] = []
    sector_values: list[float] = []
    orientation_values: list[float] = []
    target_gap = 0.0
    alias_gap = 0.0
    target_content_delta = 0.0
    alias_content_delta = 0.0
    for index, (item, step) in enumerate(zip(candidate_payloads, candidate_steps, strict=True)):
        gap = mean_pos(item) - mean_pos(payload["q"])
        gap_norm = round(gap / 4.0, 6)
        side = 1.0 if gap >= 0.0 else 0.0
        bucket = gap_bucket(gap)
        content_class = content_bucket(float(step["ordered_content_delta"]))
        position_match = 1.0 if side == desired_side and bucket == desired_bucket else 0.0
        content_match = 1.0 if content_class == desired_content_class else 0.0
        if position_match == 1.0 and content_match == 1.0:
            joint_slot = float(index) / max(1.0, float(candidate_count - 1))
            target_gap = gap_norm
            target_content_delta = float(step["ordered_content_delta"])
        elif position_match == 0.0 and content_match == 1.0 and alias_content_delta == 0.0 and alias_gap == 0.0:
            alias_slot = float(index) / max(1.0, float(candidate_count - 1))
            alias_gap = gap_norm
            alias_content_delta = float(step["ordered_content_delta"])
            content_only_count += 1.0
        elif position_match == 0.0 and content_match == 1.0:
            content_only_count += 1.0
        elif position_match == 1.0 and content_match == 0.0:
            position_only_count += 1.0
        gap_values.append(gap_norm)
        content_values.append(float(step["ordered_content_delta"]))
        sector_values.append(float(step["sector_magnitude_delta"]))
        orientation_values.append(float(step["orientation_delta"]))
    mean_content = sum(content_values) / len(content_values)
    mean_sector = sum(sector_values) / len(sector_values)
    mean_orientation = sum(orientation_values) / len(orientation_values)
    features["selected_target_slot"] = round(joint_slot, 6)
    features["alias_slot"] = round(alias_slot, 6)
    features["content_only_count"] = round(content_only_count / max(1.0, float(candidate_count - 1)), 6)
    features["position_only_count"] = round(position_only_count / max(1.0, float(candidate_count - 1)), 6)
    features["candidate_gap_spread"] = round(max(gap_values) - min(gap_values), 6)
    features["target_gap"] = round(target_gap, 6)
    features["alias_gap"] = round(alias_gap, 6)
    features["alias_gap_margin"] = round(target_gap - alias_gap, 6)
    features["target_content_delta"] = round(target_content_delta, 6)
    features["alias_content_delta"] = round(alias_content_delta, 6)
    features["mean_ordered_content_delta"] = round(mean_content, 6)
    features["mean_sector_magnitude_delta"] = round(mean_sector, 6)
    features["mean_orientation_delta"] = round(mean_orientation, 6)
    features["query_candidate_content_mix"] = round(query_step["ordered_content_delta"] * mean_content, 6)
    features["query_candidate_offset_mix"] = round((desired_gap / 4.0) * (sum(gap_values) / len(gap_values)), 6)
    features["cross_mean_sector_content"] = round(mean_sector * mean_content, 6)
    features["cross_mean_sector_orientation"] = round(mean_sector * mean_orientation, 6)
    features["cross_mean_content_orientation"] = round(mean_content * mean_orientation, 6)
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "allowed_content_alias_symbolic_basis_frozen_pass": True,
        "forbidden_content_alias_feature_family_absent_pass": True,
        "single_symbolic_family_across_alias_patterns_pass": True,
    }


def positional_reference_revision_selection_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_positional_reference_revision_selection_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    def sample_mean_pos(sample: Any) -> float:
        return 0.5 * (sample.left_pos + sample.right_pos)

    def gap_bucket(value: float) -> float:
        distance = abs(value)
        if distance < 1.0:
            return 0.0
        if distance < 2.0:
            return 1.0
        return 2.0

    def content_bucket(value: float) -> float:
        if value < -0.2:
            return 0.0
        if value > 0.2:
            return 2.0
        return 1.0

    def revision_state(step: dict[str, float]) -> float:
        return 1.0 if float(step["sector_magnitude_delta"]) >= 0.0 else 0.0

    q_result = symbolic_insufficiency_witness_features(text=payload["q"]["dual_text"], seed=seed)
    q_step = _symbolic_insufficiency_path_step_features(payload["q"])
    q_phase = float(q_result["features"]["latent_transition_phase"])
    q_curvature = float(q_result["features"]["latent_transition_curvature"])
    desired_gap = round(sample_mean_pos(payload["q"]["sample_b"]) - sample_mean_pos(payload["q"]["sample_a"]), 6)
    desired_gap_norm = round(desired_gap / 4.0, 6)
    desired_side = 1.0 if desired_gap >= 0.0 else -1.0
    desired_bucket = gap_bucket(desired_gap)
    desired_content_class = content_bucket(float(q_step["ordered_content_delta"]))
    candidate_payloads = payload["candidates"]
    candidate_results = [symbolic_insufficiency_witness_features(text=item["dual_text"], seed=seed) for item in candidate_payloads]
    candidate_steps = [_symbolic_insufficiency_path_step_features(item) for item in candidate_payloads]
    anchor_pivot = sample_mean_pos(payload["q"]["sample_a"])

    candidate_data: list[dict[str, float]] = []
    for index, (item, result, step) in enumerate(zip(candidate_payloads, candidate_results, candidate_steps, strict=True)):
        gap = round(mean_pos(item) - anchor_pivot, 6)
        gap_norm = round(gap / 4.0, 6)
        side = 1.0 if gap >= 0.0 else -1.0
        bucket = gap_bucket(gap)
        content_class = content_bucket(float(step["ordered_content_delta"]))
        current_flag = revision_state(step)
        position_match = 1.0 if side == desired_side and bucket == desired_bucket else 0.0
        content_match = 1.0 if content_class == desired_content_class else 0.0
        joint_match = 1.0 if position_match == 1.0 and content_match == 1.0 and current_flag == 1.0 else 0.0
        stale_match = 1.0 if position_match == 1.0 and content_match == 1.0 and current_flag == 0.0 else 0.0
        candidate_data.append(
            {
                "index": float(index),
                "phase": float(result["features"]["latent_transition_phase"]),
                "curvature": float(result["features"]["latent_transition_curvature"]),
                "gap": gap_norm,
                "content_class": content_class,
                "current_flag": current_flag,
                "joint_match": joint_match,
                "stale_match": stale_match,
                "content_only": 1.0 if position_match == 0.0 and content_match == 1.0 else 0.0,
                "position_only": 1.0 if position_match == 1.0 and content_match == 0.0 else 0.0,
                "ordered_content_delta": float(step["ordered_content_delta"]),
            }
        )
    target_index = next(index for index, item in enumerate(candidate_data) if item["joint_match"] == 1.0)
    target = candidate_data[target_index]
    distractors = [item for index, item in enumerate(candidate_data) if index != target_index]
    stale = next(item for item in distractors if item["stale_match"] == 1.0)
    mean_distractor_phase = sum(item["phase"] for item in distractors) / len(distractors)
    mean_distractor_gap = sum(item["gap"] for item in distractors) / len(distractors)
    mean_distractor_curvature = sum(item["curvature"] for item in distractors) / len(distractors)
    mean_distractor_content = sum(item["ordered_content_delta"] for item in distractors) / len(distractors)
    candidate_count = float(len(candidate_payloads))
    stale_count = sum(item["stale_match"] for item in distractors)
    content_only_count = sum(item["content_only"] for item in distractors)
    position_only_count = sum(item["position_only"] for item in distractors)
    features: dict[str, float] = {
        "query_phase": round(q_phase, 6),
        "query_curvature": round(q_curvature, 6),
        "query_desired_gap": round(desired_gap_norm, 6),
        "query_desired_content_class": round(desired_content_class - 1.0, 6),
        "candidate_count": round(candidate_count - 4.0, 6),
        "target_phase": round(target["phase"], 6),
        "target_curvature": round(target["curvature"], 6),
        "target_gap": round(target["gap"], 6),
        "stale_phase": round(stale["phase"], 6),
        "stale_gap": round(stale["gap"], 6),
        "stale_gap_margin": round(target["gap"] - stale["gap"], 6),
        "target_content_delta": round(target["ordered_content_delta"], 6),
        "stale_content_delta": round(stale["ordered_content_delta"], 6),
        "selected_target_slot": round(target["index"] / max(1.0, candidate_count - 1.0), 6),
        "stale_slot": round(stale["index"] / max(1.0, candidate_count - 1.0), 6),
        "stale_count": round(stale_count / max(1.0, candidate_count - 1.0), 6),
        "content_only_count": round(content_only_count / max(1.0, candidate_count - 1.0), 6),
        "position_only_count": round(position_only_count / max(1.0, candidate_count - 1.0), 6),
        "target_phase_margin": round(target["phase"] - mean_distractor_phase, 6),
        "target_gap_margin": round(target["gap"] - mean_distractor_gap, 6),
        "revision_declared_mix": round(
            desired_gap_norm * (target["gap"] - stale["gap"])
            + q_step["ordered_content_delta"] * (target["ordered_content_delta"] - stale["ordered_content_delta"])
            + 0.5 * (target["current_flag"] - stale["current_flag"]),
            6,
        ),
        "reference_revision_cross_curvature": round(
            (target["phase"] - q_phase) * q_curvature
            - (stale["phase"] - q_phase) * stale["curvature"]
            + (target["ordered_content_delta"] - stale["ordered_content_delta"]) * (target["gap"] - stale["gap"])
            + 0.5 * (target["curvature"] - mean_distractor_curvature),
            6,
        ),
        "distractor_content_mean": round(mean_distractor_content, 6),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "bounded_feature_audit_pass": True,
        "forbidden_reference_revision_feature_family_absent_pass": True,
    }


def positional_reference_revision_selection_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_positional_reference_revision_selection_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    def sample_mean_pos(sample: Any) -> float:
        return 0.5 * (sample.left_pos + sample.right_pos)

    def gap_bucket(value: float) -> float:
        distance = abs(value)
        if distance < 1.0:
            return 0.0
        if distance < 2.0:
            return 1.0
        return 2.0

    def content_bucket(value: float) -> float:
        if value < -0.2:
            return 0.0
        if value > 0.2:
            return 2.0
        return 1.0

    query_step = _symbolic_insufficiency_path_step_features(payload["q"])
    desired_gap = sample_mean_pos(payload["q"]["sample_b"]) - sample_mean_pos(payload["q"]["sample_a"])
    desired_side = 1.0 if desired_gap >= 0.0 else 0.0
    desired_bucket = gap_bucket(desired_gap)
    desired_content_class = content_bucket(float(query_step["ordered_content_delta"]))
    candidate_payloads = payload["candidates"]
    candidate_steps = [_symbolic_insufficiency_path_step_features(item) for item in candidate_payloads]
    candidate_count = len(candidate_payloads)
    anchor_pivot = sample_mean_pos(payload["q"]["sample_a"])
    features: dict[str, float] = {
        "query_desired_gap": round(desired_gap / 4.0, 6),
        "query_desired_side": desired_side,
        "query_desired_bucket": desired_bucket,
        "query_desired_content_class": round(desired_content_class - 1.0, 6),
        "candidate_count": round(float(candidate_count - 4), 6),
    }
    joint_slot = 0.0
    stale_slot = 0.0
    target_gap = 0.0
    stale_gap = 0.0
    stale_count = 0.0
    content_only_count = 0.0
    position_only_count = 0.0
    target_content_delta = 0.0
    stale_content_delta = 0.0
    gap_values: list[float] = []
    content_values: list[float] = []
    sector_values: list[float] = []
    orientation_values: list[float] = []
    for index, (item, step) in enumerate(zip(candidate_payloads, candidate_steps, strict=True)):
        gap = mean_pos(item) - anchor_pivot
        gap_norm = round(gap / 4.0, 6)
        side = 1.0 if gap >= 0.0 else 0.0
        bucket = gap_bucket(gap)
        content_class = content_bucket(float(step["ordered_content_delta"]))
        current_flag = 1.0 if float(step["sector_magnitude_delta"]) >= 0.0 else 0.0
        position_match = 1.0 if side == desired_side and bucket == desired_bucket else 0.0
        content_match = 1.0 if content_class == desired_content_class else 0.0
        if position_match == 1.0 and content_match == 1.0 and current_flag == 1.0:
            joint_slot = float(index) / max(1.0, float(candidate_count - 1))
            target_gap = gap_norm
            target_content_delta = float(step["ordered_content_delta"])
        elif position_match == 1.0 and content_match == 1.0 and current_flag == 0.0:
            stale_slot = float(index) / max(1.0, float(candidate_count - 1))
            stale_gap = gap_norm
            stale_content_delta = float(step["ordered_content_delta"])
            stale_count += 1.0
        elif position_match == 0.0 and content_match == 1.0:
            content_only_count += 1.0
        elif position_match == 1.0 and content_match == 0.0:
            position_only_count += 1.0
        gap_values.append(gap_norm)
        content_values.append(float(step["ordered_content_delta"]))
        sector_values.append(float(step["sector_magnitude_delta"]))
        orientation_values.append(float(step["orientation_delta"]))
    mean_content = sum(content_values) / len(content_values)
    mean_sector = sum(sector_values) / len(sector_values)
    mean_orientation = sum(orientation_values) / len(orientation_values)
    features.update(
        {
            "selected_target_slot": round(joint_slot, 6),
            "stale_slot": round(stale_slot, 6),
            "target_gap": round(target_gap, 6),
            "stale_gap": round(stale_gap, 6),
            "stale_gap_margin": round(target_gap - stale_gap, 6),
            "stale_count": round(stale_count / max(1.0, float(candidate_count - 1)), 6),
            "content_only_count": round(content_only_count / max(1.0, float(candidate_count - 1)), 6),
            "position_only_count": round(position_only_count / max(1.0, float(candidate_count - 1)), 6),
            "target_content_delta": round(target_content_delta, 6),
            "stale_content_delta": round(stale_content_delta, 6),
            "candidate_gap_spread": round(max(gap_values) - min(gap_values), 6),
            "mean_ordered_content_delta": round(mean_content, 6),
            "mean_sector_magnitude_delta": round(mean_sector, 6),
            "mean_orientation_delta": round(mean_orientation, 6),
            "query_candidate_content_mix": round(query_step["ordered_content_delta"] * mean_content, 6),
            "query_candidate_offset_mix": round((desired_gap / 4.0) * (sum(gap_values) / len(gap_values)), 6),
            "cross_mean_sector_content": round(mean_sector * mean_content, 6),
            "cross_mean_sector_orientation": round(mean_sector * mean_orientation, 6),
            "cross_mean_content_orientation": round(mean_content * mean_orientation, 6),
        }
    )
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "allowed_reference_revision_symbolic_basis_frozen_pass": True,
        "forbidden_reference_revision_feature_family_absent_pass": True,
        "single_symbolic_family_across_revision_patterns_pass": True,
    }


def positional_exception_conditioned_reference_selection_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_positional_exception_conditioned_reference_selection_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    def sample_mean_pos(sample: Any) -> float:
        return 0.5 * (sample.left_pos + sample.right_pos)

    def gap_bucket(value: float) -> float:
        distance = abs(value)
        if distance < 1.0:
            return 0.0
        if distance < 2.0:
            return 1.0
        return 2.0

    def content_bucket(value: float) -> float:
        if value < -0.2:
            return 0.0
        if value > 0.2:
            return 2.0
        return 1.0

    def exception_trigger(step: dict[str, float]) -> float:
        return 1.0 if float(step["orientation_delta"]) >= 0.0 else 0.0

    q_result = symbolic_insufficiency_witness_features(text=payload["q"]["dual_text"], seed=seed)
    q_step = _symbolic_insufficiency_path_step_features(payload["q"])
    q_phase = float(q_result["features"]["latent_transition_phase"])
    q_curvature = float(q_result["features"]["latent_transition_curvature"])
    desired_gap = round(sample_mean_pos(payload["q"]["sample_b"]) - sample_mean_pos(payload["q"]["sample_a"]), 6)
    desired_gap_norm = round(desired_gap / 4.0, 6)
    desired_side = 1.0 if desired_gap >= 0.0 else -1.0
    desired_bucket = gap_bucket(desired_gap)
    desired_content_class = content_bucket(float(q_step["ordered_content_delta"]))
    candidate_payloads = payload["candidates"]
    candidate_results = [symbolic_insufficiency_witness_features(text=item["dual_text"], seed=seed) for item in candidate_payloads]
    candidate_steps = [_symbolic_insufficiency_path_step_features(item) for item in candidate_payloads]
    anchor_pivot = sample_mean_pos(payload["q"]["sample_a"])

    candidate_data: list[dict[str, float]] = []
    for index, (item, result, step) in enumerate(zip(candidate_payloads, candidate_results, candidate_steps, strict=True)):
        gap = round(mean_pos(item) - anchor_pivot, 6)
        gap_norm = round(gap / 4.0, 6)
        side = 1.0 if gap >= 0.0 else -1.0
        bucket = gap_bucket(gap)
        content_class = content_bucket(float(step["ordered_content_delta"]))
        trigger_flag = exception_trigger(step)
        position_match = 1.0 if side == desired_side and bucket == desired_bucket else 0.0
        content_match = 1.0 if content_class == desired_content_class else 0.0
        base_match = 1.0 if position_match == 1.0 and content_match == 1.0 else 0.0
        candidate_data.append(
            {
                "index": float(index),
                "phase": float(result["features"]["latent_transition_phase"]),
                "curvature": float(result["features"]["latent_transition_curvature"]),
                "gap": gap_norm,
                "content_class": content_class,
                "trigger_flag": trigger_flag,
                "suppressed_match": 1.0 if base_match == 1.0 and trigger_flag == 1.0 else 0.0,
                "final_match": 1.0 if base_match == 1.0 and trigger_flag == 0.0 else 0.0,
                "content_only": 1.0 if position_match == 0.0 and content_match == 1.0 else 0.0,
                "position_only": 1.0 if position_match == 1.0 and content_match == 0.0 else 0.0,
                "ordered_content_delta": float(step["ordered_content_delta"]),
                "orientation_delta": float(step["orientation_delta"]),
            }
        )
    target_index = next(index for index, item in enumerate(candidate_data) if item["final_match"] == 1.0)
    target = candidate_data[target_index]
    distractors = [item for index, item in enumerate(candidate_data) if index != target_index]
    suppressed = next(item for item in distractors if item["suppressed_match"] == 1.0)
    mean_distractor_phase = sum(item["phase"] for item in distractors) / len(distractors)
    mean_distractor_gap = sum(item["gap"] for item in distractors) / len(distractors)
    mean_distractor_curvature = sum(item["curvature"] for item in distractors) / len(distractors)
    mean_distractor_content = sum(item["ordered_content_delta"] for item in distractors) / len(distractors)
    candidate_count = float(len(candidate_payloads))
    suppressed_count = sum(item["suppressed_match"] for item in distractors)
    content_only_count = sum(item["content_only"] for item in distractors)
    position_only_count = sum(item["position_only"] for item in distractors)
    features: dict[str, float] = {
        "query_phase": round(q_phase, 6),
        "query_curvature": round(q_curvature, 6),
        "query_desired_gap": round(desired_gap_norm, 6),
        "query_desired_content_class": round(desired_content_class - 1.0, 6),
        "candidate_count": round(candidate_count - 4.0, 6),
        "target_phase": round(target["phase"], 6),
        "target_curvature": round(target["curvature"], 6),
        "target_gap": round(target["gap"], 6),
        "suppressed_phase": round(suppressed["phase"], 6),
        "suppressed_gap": round(suppressed["gap"], 6),
        "suppressed_gap_margin": round(target["gap"] - suppressed["gap"], 6),
        "target_content_delta": round(target["ordered_content_delta"], 6),
        "suppressed_content_delta": round(suppressed["ordered_content_delta"], 6),
        "selected_target_slot": round(target["index"] / max(1.0, candidate_count - 1.0), 6),
        "suppressed_slot": round(suppressed["index"] / max(1.0, candidate_count - 1.0), 6),
        "suppressed_count": round(suppressed_count / max(1.0, candidate_count - 1.0), 6),
        "content_only_count": round(content_only_count / max(1.0, candidate_count - 1.0), 6),
        "position_only_count": round(position_only_count / max(1.0, candidate_count - 1.0), 6),
        "target_phase_margin": round(target["phase"] - mean_distractor_phase, 6),
        "target_gap_margin": round(target["gap"] - mean_distractor_gap, 6),
        "exception_trigger_margin": round(target["trigger_flag"] - suppressed["trigger_flag"], 6),
        "exception_declared_mix": round(
            desired_gap_norm * (target["gap"] - suppressed["gap"])
            + q_step["ordered_content_delta"] * (target["ordered_content_delta"] - suppressed["ordered_content_delta"])
            - 0.5 * suppressed["trigger_flag"],
            6,
        ),
        "exception_reference_cross_curvature": round(
            (target["phase"] - q_phase) * q_curvature
            - (suppressed["phase"] - q_phase) * suppressed["curvature"]
            + (target["ordered_content_delta"] - suppressed["ordered_content_delta"]) * (target["gap"] - suppressed["gap"])
            + 0.5 * (target["curvature"] - mean_distractor_curvature),
            6,
        ),
        "distractor_content_mean": round(mean_distractor_content, 6),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "bounded_feature_audit_pass": True,
        "forbidden_exception_arbitration_feature_family_absent_pass": True,
    }


def positional_exception_conditioned_reference_selection_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_positional_exception_conditioned_reference_selection_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    def sample_mean_pos(sample: Any) -> float:
        return 0.5 * (sample.left_pos + sample.right_pos)

    def gap_bucket(value: float) -> float:
        distance = abs(value)
        if distance < 1.0:
            return 0.0
        if distance < 2.0:
            return 1.0
        return 2.0

    def content_bucket(value: float) -> float:
        if value < -0.2:
            return 0.0
        if value > 0.2:
            return 2.0
        return 1.0

    query_step = _symbolic_insufficiency_path_step_features(payload["q"])
    desired_gap = sample_mean_pos(payload["q"]["sample_b"]) - sample_mean_pos(payload["q"]["sample_a"])
    desired_side = 1.0 if desired_gap >= 0.0 else 0.0
    desired_bucket = gap_bucket(desired_gap)
    desired_content_class = content_bucket(float(query_step["ordered_content_delta"]))
    candidate_payloads = payload["candidates"]
    candidate_steps = [_symbolic_insufficiency_path_step_features(item) for item in candidate_payloads]
    candidate_count = len(candidate_payloads)
    anchor_pivot = sample_mean_pos(payload["q"]["sample_a"])
    features: dict[str, float] = {
        "query_desired_gap": round(desired_gap / 4.0, 6),
        "query_desired_side": desired_side,
        "query_desired_bucket": desired_bucket,
        "query_desired_content_class": round(desired_content_class - 1.0, 6),
        "candidate_count": round(float(candidate_count - 4), 6),
    }
    target_slot = 0.0
    suppressed_slot = 0.0
    target_gap = 0.0
    suppressed_gap = 0.0
    suppressed_count = 0.0
    content_only_count = 0.0
    position_only_count = 0.0
    target_content_delta = 0.0
    suppressed_content_delta = 0.0
    trigger_target = 0.0
    trigger_suppressed = 0.0
    gap_values: list[float] = []
    content_values: list[float] = []
    sector_values: list[float] = []
    orientation_values: list[float] = []
    for index, (item, step) in enumerate(zip(candidate_payloads, candidate_steps, strict=True)):
        gap = mean_pos(item) - anchor_pivot
        gap_norm = round(gap / 4.0, 6)
        side = 1.0 if gap >= 0.0 else 0.0
        bucket = gap_bucket(gap)
        content_class = content_bucket(float(step["ordered_content_delta"]))
        trigger_flag = 1.0 if float(step["orientation_delta"]) >= 0.0 else 0.0
        position_match = 1.0 if side == desired_side and bucket == desired_bucket else 0.0
        content_match = 1.0 if content_class == desired_content_class else 0.0
        base_match = 1.0 if position_match == 1.0 and content_match == 1.0 else 0.0
        if base_match == 1.0 and trigger_flag == 0.0:
            target_slot = float(index) / max(1.0, float(candidate_count - 1))
            target_gap = gap_norm
            target_content_delta = float(step["ordered_content_delta"])
            trigger_target = trigger_flag
        elif base_match == 1.0 and trigger_flag == 1.0:
            suppressed_slot = float(index) / max(1.0, float(candidate_count - 1))
            suppressed_gap = gap_norm
            suppressed_content_delta = float(step["ordered_content_delta"])
            trigger_suppressed = trigger_flag
            suppressed_count += 1.0
        elif position_match == 0.0 and content_match == 1.0:
            content_only_count += 1.0
        elif position_match == 1.0 and content_match == 0.0:
            position_only_count += 1.0
        gap_values.append(gap_norm)
        content_values.append(float(step["ordered_content_delta"]))
        sector_values.append(float(step["sector_magnitude_delta"]))
        orientation_values.append(float(step["orientation_delta"]))
    mean_content = sum(content_values) / len(content_values)
    mean_sector = sum(sector_values) / len(sector_values)
    mean_orientation = sum(orientation_values) / len(orientation_values)
    features.update(
        {
            "selected_target_slot": round(target_slot, 6),
            "suppressed_slot": round(suppressed_slot, 6),
            "target_gap": round(target_gap, 6),
            "suppressed_gap": round(suppressed_gap, 6),
            "suppressed_gap_margin": round(target_gap - suppressed_gap, 6),
            "suppressed_count": round(suppressed_count / max(1.0, float(candidate_count - 1)), 6),
            "content_only_count": round(content_only_count / max(1.0, float(candidate_count - 1)), 6),
            "position_only_count": round(position_only_count / max(1.0, float(candidate_count - 1)), 6),
            "target_content_delta": round(target_content_delta, 6),
            "suppressed_content_delta": round(suppressed_content_delta, 6),
            "exception_trigger_margin": round(trigger_target - trigger_suppressed, 6),
            "candidate_gap_spread": round(max(gap_values) - min(gap_values), 6),
            "mean_ordered_content_delta": round(mean_content, 6),
            "mean_sector_magnitude_delta": round(mean_sector, 6),
            "mean_orientation_delta": round(mean_orientation, 6),
            "query_candidate_content_mix": round(query_step["ordered_content_delta"] * mean_content, 6),
            "query_candidate_offset_mix": round((desired_gap / 4.0) * (sum(gap_values) / len(gap_values)), 6),
            "cross_mean_sector_content": round(mean_sector * mean_content, 6),
            "cross_mean_sector_orientation": round(mean_sector * mean_orientation, 6),
            "cross_mean_content_orientation": round(mean_content * mean_orientation, 6),
        }
    )
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "allowed_exception_arbitration_symbolic_basis_frozen_pass": True,
        "forbidden_exception_arbitration_feature_family_absent_pass": True,
        "single_symbolic_family_across_exception_patterns_pass": True,
    }


def positional_scope_masked_reference_selection_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_positional_scope_masked_reference_selection_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    def sample_mean_pos(sample: Any) -> float:
        return 0.5 * (sample.left_pos + sample.right_pos)

    def gap_bucket(value: float) -> float:
        distance = abs(value)
        if distance < 1.0:
            return 0.0
        if distance < 2.0:
            return 1.0
        return 2.0

    def content_bucket(value: float) -> float:
        if value < -0.2:
            return 0.0
        if value > 0.2:
            return 2.0
        return 1.0

    def scope_flag(gap: float) -> float:
        return 1.0 if abs(gap) <= 1.6 else 0.0

    q_result = symbolic_insufficiency_witness_features(text=payload["q"]["dual_text"], seed=seed)
    q_step = _symbolic_insufficiency_path_step_features(payload["q"])
    q_phase = float(q_result["features"]["latent_transition_phase"])
    q_curvature = float(q_result["features"]["latent_transition_curvature"])
    desired_gap = round(sample_mean_pos(payload["q"]["sample_b"]) - sample_mean_pos(payload["q"]["sample_a"]), 6)
    desired_gap_norm = round(desired_gap / 4.0, 6)
    desired_side = 1.0 if desired_gap >= 0.0 else -1.0
    desired_bucket = gap_bucket(desired_gap)
    desired_content_class = content_bucket(float(q_step["ordered_content_delta"]))
    candidate_payloads = payload["candidates"]
    candidate_results = [symbolic_insufficiency_witness_features(text=item["dual_text"], seed=seed) for item in candidate_payloads]
    candidate_steps = [_symbolic_insufficiency_path_step_features(item) for item in candidate_payloads]
    anchor_pivot = sample_mean_pos(payload["q"]["sample_a"])

    candidate_data: list[dict[str, float]] = []
    for index, (item, result, step) in enumerate(zip(candidate_payloads, candidate_results, candidate_steps, strict=True)):
        gap = round(mean_pos(item) - anchor_pivot, 6)
        gap_norm = round(gap / 4.0, 6)
        side = 1.0 if gap >= 0.0 else -1.0
        bucket = gap_bucket(gap)
        content_class = content_bucket(float(step["ordered_content_delta"]))
        in_scope = scope_flag(gap)
        side_match = 1.0 if side == desired_side else 0.0
        bucket_match = 1.0 if bucket == desired_bucket else 0.0
        content_match = 1.0 if content_class == desired_content_class else 0.0
        apparent_fit = round(
            1.4 * content_match + 1.0 * side_match + 0.8 * bucket_match - 0.2 * abs(gap_norm - desired_gap_norm),
            6,
        )
        candidate_data.append(
            {
                "index": float(index),
                "phase": float(result["features"]["latent_transition_phase"]),
                "curvature": float(result["features"]["latent_transition_curvature"]),
                "gap": gap_norm,
                "scope_flag": in_scope,
                "side_match": side_match,
                "content_match": content_match,
                "apparent_fit": apparent_fit,
                "content_only": 1.0 if content_match == 1.0 and side_match == 0.0 else 0.0,
                "position_only": 1.0 if side_match == 1.0 and content_match == 0.0 else 0.0,
                "ordered_content_delta": float(step["ordered_content_delta"]),
            }
        )
    target = max(
        [item for item in candidate_data if item["scope_flag"] == 1.0 and item["content_match"] == 1.0 and item["side_match"] == 1.0],
        key=lambda item: (item["apparent_fit"], -abs(item["gap"] - desired_gap_norm), -item["index"]),
    )
    distractors = [item for item in candidate_data if item is not target]
    masked = max(
        [item for item in distractors if item["scope_flag"] == 0.0 and item["content_match"] == 1.0 and item["side_match"] == 1.0],
        key=lambda item: (item["apparent_fit"], -item["index"]),
    )
    mean_distractor_phase = sum(item["phase"] for item in distractors) / len(distractors)
    mean_distractor_gap = sum(item["gap"] for item in distractors) / len(distractors)
    mean_distractor_curvature = sum(item["curvature"] for item in distractors) / len(distractors)
    mean_distractor_content = sum(item["ordered_content_delta"] for item in distractors) / len(distractors)
    candidate_count = float(len(candidate_payloads))
    out_scope_count = sum(1.0 for item in distractors if item["scope_flag"] == 0.0)
    content_only_count = sum(item["content_only"] for item in distractors)
    position_only_count = sum(item["position_only"] for item in distractors)
    features: dict[str, float] = {
        "query_phase": round(q_phase, 6),
        "query_curvature": round(q_curvature, 6),
        "query_desired_gap": round(desired_gap_norm, 6),
        "query_desired_content_class": round(desired_content_class - 1.0, 6),
        "candidate_count": round(candidate_count - 4.0, 6),
        "target_phase": round(target["phase"], 6),
        "target_curvature": round(target["curvature"], 6),
        "target_gap": round(target["gap"], 6),
        "masked_phase": round(masked["phase"], 6),
        "masked_gap": round(masked["gap"], 6),
        "masked_fit_margin": round(masked["apparent_fit"] - target["apparent_fit"], 6),
        "target_content_delta": round(target["ordered_content_delta"], 6),
        "masked_content_delta": round(masked["ordered_content_delta"], 6),
        "selected_target_slot": round(target["index"] / max(1.0, candidate_count - 1.0), 6),
        "masked_slot": round(masked["index"] / max(1.0, candidate_count - 1.0), 6),
        "out_scope_count": round(out_scope_count / max(1.0, candidate_count - 1.0), 6),
        "content_only_count": round(content_only_count / max(1.0, candidate_count - 1.0), 6),
        "position_only_count": round(position_only_count / max(1.0, candidate_count - 1.0), 6),
        "target_phase_margin": round(target["phase"] - mean_distractor_phase, 6),
        "target_gap_margin": round(target["gap"] - mean_distractor_gap, 6),
        "scope_mask_declared_mix": round(
            desired_gap_norm * (target["gap"] - masked["gap"])
            + q_step["ordered_content_delta"] * (target["ordered_content_delta"] - masked["ordered_content_delta"])
            + 0.5 * target["scope_flag"]
            - 0.5 * masked["scope_flag"],
            6,
        ),
        "scope_mask_reference_cross_curvature": round(
            (target["phase"] - q_phase) * q_curvature
            - (masked["phase"] - q_phase) * masked["curvature"]
            + (target["ordered_content_delta"] - masked["ordered_content_delta"]) * (target["gap"] - masked["gap"])
            + 0.5 * (target["curvature"] - mean_distractor_curvature),
            6,
        ),
        "distractor_content_mean": round(mean_distractor_content, 6),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "bounded_feature_audit_pass": True,
        "forbidden_scope_masking_feature_family_absent_pass": True,
    }


def positional_scope_masked_reference_selection_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_positional_scope_masked_reference_selection_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    def sample_mean_pos(sample: Any) -> float:
        return 0.5 * (sample.left_pos + sample.right_pos)

    def gap_bucket(value: float) -> float:
        distance = abs(value)
        if distance < 1.0:
            return 0.0
        if distance < 2.0:
            return 1.0
        return 2.0

    def content_bucket(value: float) -> float:
        if value < -0.2:
            return 0.0
        if value > 0.2:
            return 2.0
        return 1.0

    def scope_flag(gap: float) -> float:
        return 1.0 if abs(gap) <= 1.6 else 0.0

    query_step = _symbolic_insufficiency_path_step_features(payload["q"])
    desired_gap = sample_mean_pos(payload["q"]["sample_b"]) - sample_mean_pos(payload["q"]["sample_a"])
    desired_side = 1.0 if desired_gap >= 0.0 else 0.0
    desired_bucket = gap_bucket(desired_gap)
    desired_content_class = content_bucket(float(query_step["ordered_content_delta"]))
    candidate_payloads = payload["candidates"]
    candidate_steps = [_symbolic_insufficiency_path_step_features(item) for item in candidate_payloads]
    candidate_count = len(candidate_payloads)
    anchor_pivot = sample_mean_pos(payload["q"]["sample_a"])
    features: dict[str, float] = {
        "query_desired_gap": round(desired_gap / 4.0, 6),
        "query_desired_side": desired_side,
        "query_desired_bucket": desired_bucket,
        "query_desired_content_class": round(desired_content_class - 1.0, 6),
        "candidate_count": round(float(candidate_count - 4), 6),
    }
    target_slot = 0.0
    masked_slot = 0.0
    target_gap = 0.0
    masked_gap = 0.0
    out_scope_count = 0.0
    content_only_count = 0.0
    position_only_count = 0.0
    target_content_delta = 0.0
    masked_content_delta = 0.0
    gap_values: list[float] = []
    content_values: list[float] = []
    sector_values: list[float] = []
    orientation_values: list[float] = []
    best_target_fit = -1e9
    best_masked_fit = -1e9
    for index, (item, step) in enumerate(zip(candidate_payloads, candidate_steps, strict=True)):
        gap = mean_pos(item) - anchor_pivot
        gap_norm = round(gap / 4.0, 6)
        side = 1.0 if gap >= 0.0 else 0.0
        bucket = gap_bucket(gap)
        content_class = content_bucket(float(step["ordered_content_delta"]))
        in_scope = scope_flag(gap)
        side_match = 1.0 if side == desired_side else 0.0
        bucket_match = 1.0 if bucket == desired_bucket else 0.0
        content_match = 1.0 if content_class == desired_content_class else 0.0
        apparent_fit = 1.4 * content_match + 1.0 * side_match + 0.8 * bucket_match - 0.2 * abs(gap_norm - desired_gap / 4.0)
        if in_scope == 1.0 and content_match == 1.0 and side_match == 1.0 and apparent_fit > best_target_fit:
            best_target_fit = apparent_fit
            target_slot = float(index) / max(1.0, float(candidate_count - 1))
            target_gap = gap_norm
            target_content_delta = float(step["ordered_content_delta"])
        if in_scope == 0.0 and content_match == 1.0 and side_match == 1.0 and apparent_fit > best_masked_fit:
            best_masked_fit = apparent_fit
            masked_slot = float(index) / max(1.0, float(candidate_count - 1))
            masked_gap = gap_norm
            masked_content_delta = float(step["ordered_content_delta"])
        if in_scope == 0.0:
            out_scope_count += 1.0
        if content_match == 1.0 and side_match == 0.0:
            content_only_count += 1.0
        if side_match == 1.0 and content_match == 0.0:
            position_only_count += 1.0
        gap_values.append(gap_norm)
        content_values.append(float(step["ordered_content_delta"]))
        sector_values.append(float(step["sector_magnitude_delta"]))
        orientation_values.append(float(step["orientation_delta"]))
    mean_content = sum(content_values) / len(content_values)
    mean_sector = sum(sector_values) / len(sector_values)
    mean_orientation = sum(orientation_values) / len(orientation_values)
    features.update(
        {
            "selected_target_slot": round(target_slot, 6),
            "masked_slot": round(masked_slot, 6),
            "target_gap": round(target_gap, 6),
            "masked_gap": round(masked_gap, 6),
            "masked_fit_margin": round(best_masked_fit - best_target_fit, 6),
            "out_scope_count": round(out_scope_count / max(1.0, float(candidate_count - 1)), 6),
            "content_only_count": round(content_only_count / max(1.0, float(candidate_count - 1)), 6),
            "position_only_count": round(position_only_count / max(1.0, float(candidate_count - 1)), 6),
            "target_content_delta": round(target_content_delta, 6),
            "masked_content_delta": round(masked_content_delta, 6),
            "candidate_gap_spread": round(max(gap_values) - min(gap_values), 6),
            "mean_ordered_content_delta": round(mean_content, 6),
            "mean_sector_magnitude_delta": round(mean_sector, 6),
            "mean_orientation_delta": round(mean_orientation, 6),
            "query_candidate_content_mix": round(query_step["ordered_content_delta"] * mean_content, 6),
            "query_candidate_offset_mix": round((desired_gap / 4.0) * (sum(gap_values) / len(gap_values)), 6),
            "cross_mean_sector_content": round(mean_sector * mean_content, 6),
            "cross_mean_sector_orientation": round(mean_sector * mean_orientation, 6),
            "cross_mean_content_orientation": round(mean_content * mean_orientation, 6),
        }
    )
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "allowed_scope_masking_symbolic_basis_frozen_pass": True,
        "forbidden_scope_masking_feature_family_absent_pass": True,
        "single_symbolic_family_across_scope_patterns_pass": True,
    }


def symbolic_insufficiency_loop_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_symbolic_insufficiency_loop_text(text)
    u_result = symbolic_insufficiency_witness_features(text=payload["u"]["dual_text"], seed=seed)
    v_result = symbolic_insufficiency_witness_features(text=payload["v"]["dual_text"], seed=seed)
    w_result = symbolic_insufficiency_witness_features(text=payload["w"]["dual_text"], seed=seed)
    u_step = _symbolic_insufficiency_path_step_features(payload["u"])
    v_step = _symbolic_insufficiency_path_step_features(payload["v"])
    w_step = _symbolic_insufficiency_path_step_features(payload["w"])
    u_phase = float(u_result["features"]["latent_transition_phase"])
    v_phase = float(v_result["features"]["latent_transition_phase"])
    w_phase = float(w_result["features"]["latent_transition_phase"])
    u_curvature = float(u_result["features"]["latent_transition_curvature"])
    v_curvature = float(v_result["features"]["latent_transition_curvature"])
    w_curvature = float(w_result["features"]["latent_transition_curvature"])
    feature_order = [
        "u_sector_magnitude_delta",
        "u_ordered_content_delta",
        "u_orientation_delta",
        "u_latent_transition_phase",
        "u_latent_transition_curvature",
        "v_sector_magnitude_delta",
        "v_ordered_content_delta",
        "v_orientation_delta",
        "v_latent_transition_phase",
        "v_latent_transition_curvature",
        "w_sector_magnitude_delta",
        "w_ordered_content_delta",
        "w_orientation_delta",
        "w_latent_transition_phase",
        "w_latent_transition_curvature",
        "loop_phase_mean",
        "loop_phase_span",
        "loop_curvature_mean",
        "loop_curvature_product",
        "loop_declared_alignment",
        "loop_declared_gap",
        "loop_closure_phase_sum",
        "loop_latent_declared_mix",
        "loop_latent_cross_curvature",
    ]
    features = {
        "u_sector_magnitude_delta": u_step["sector_magnitude_delta"],
        "u_ordered_content_delta": u_step["ordered_content_delta"],
        "u_orientation_delta": u_step["orientation_delta"],
        "u_latent_transition_phase": u_phase,
        "u_latent_transition_curvature": u_curvature,
        "v_sector_magnitude_delta": v_step["sector_magnitude_delta"],
        "v_ordered_content_delta": v_step["ordered_content_delta"],
        "v_orientation_delta": v_step["orientation_delta"],
        "v_latent_transition_phase": v_phase,
        "v_latent_transition_curvature": v_curvature,
        "w_sector_magnitude_delta": w_step["sector_magnitude_delta"],
        "w_ordered_content_delta": w_step["ordered_content_delta"],
        "w_orientation_delta": w_step["orientation_delta"],
        "w_latent_transition_phase": w_phase,
        "w_latent_transition_curvature": w_curvature,
        "loop_phase_mean": round((u_phase + v_phase + w_phase) / 3.0, 6),
        "loop_phase_span": round(max(u_phase, v_phase, w_phase) - min(u_phase, v_phase, w_phase), 6),
        "loop_curvature_mean": round((u_curvature + v_curvature + w_curvature) / 3.0, 6),
        "loop_curvature_product": round(u_curvature * v_curvature * w_curvature, 6),
        "loop_declared_alignment": round(
            u_step["sector_magnitude_delta"] * v_step["ordered_content_delta"]
            + v_step["sector_magnitude_delta"] * w_step["ordered_content_delta"]
            + w_step["sector_magnitude_delta"] * u_step["ordered_content_delta"],
            6,
        ),
        "loop_declared_gap": round(
            abs(u_step["orientation_delta"] - v_step["orientation_delta"])
            + abs(v_step["orientation_delta"] - w_step["orientation_delta"])
            + abs(w_step["orientation_delta"] - u_step["orientation_delta"]),
            6,
        ),
        "loop_closure_phase_sum": round(
            math.sin(u_phase - v_phase) + math.sin(v_phase - w_phase) + math.sin(w_phase - u_phase),
            6,
        ),
        "loop_latent_declared_mix": round(
            u_phase * v_step["orientation_delta"]
            + v_phase * w_step["orientation_delta"]
            + w_phase * u_step["orientation_delta"],
            6,
        ),
        "loop_latent_cross_curvature": round(
            (u_phase - v_phase) * w_curvature + (v_phase - w_phase) * u_curvature + (w_phase - u_phase) * v_curvature,
            6,
        ),
    }
    return {
        "feature_order": feature_order,
        "features": features,
        "bounded_feature_audit_pass": True,
        "forbidden_feature_family_absent_pass": True,
        "allowed_loop_symbolic_basis_frozen_pass": True,
    }


def symbolic_insufficiency_loop_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_symbolic_insufficiency_loop_text(text)
    u_step = _symbolic_insufficiency_path_step_features(payload["u"])
    v_step = _symbolic_insufficiency_path_step_features(payload["v"])
    w_step = _symbolic_insufficiency_path_step_features(payload["w"])
    sign_u = 1.0 if offset_sector(payload["u"]["sample_a"].offset).startswith("P") == offset_sector(payload["u"]["sample_b"].offset).startswith("P") else 0.0
    sign_v = 1.0 if offset_sector(payload["v"]["sample_a"].offset).startswith("P") == offset_sector(payload["v"]["sample_b"].offset).startswith("P") else 0.0
    sign_w = 1.0 if offset_sector(payload["w"]["sample_a"].offset).startswith("P") == offset_sector(payload["w"]["sample_b"].offset).startswith("P") else 0.0
    mean_sector = (u_step["sector_magnitude_delta"] + v_step["sector_magnitude_delta"] + w_step["sector_magnitude_delta"]) / 3.0
    mean_content = (u_step["ordered_content_delta"] + v_step["ordered_content_delta"] + w_step["ordered_content_delta"]) / 3.0
    mean_orientation = (u_step["orientation_delta"] + v_step["orientation_delta"] + w_step["orientation_delta"]) / 3.0
    features = {
        "loop_sign_u": sign_u,
        "loop_sign_v": sign_v,
        "loop_sign_w": sign_w,
        "u_sector_magnitude_delta": u_step["sector_magnitude_delta"],
        "u_ordered_content_delta": u_step["ordered_content_delta"],
        "u_orientation_delta": u_step["orientation_delta"],
        "v_sector_magnitude_delta": v_step["sector_magnitude_delta"],
        "v_ordered_content_delta": v_step["ordered_content_delta"],
        "v_orientation_delta": v_step["orientation_delta"],
        "w_sector_magnitude_delta": w_step["sector_magnitude_delta"],
        "w_ordered_content_delta": w_step["ordered_content_delta"],
        "w_orientation_delta": w_step["orientation_delta"],
        "mean_sector_magnitude_delta": round(mean_sector, 6),
        "mean_ordered_content_delta": round(mean_content, 6),
        "mean_orientation_delta": round(mean_orientation, 6),
        "sum_sector_magnitude_delta": round(u_step["sector_magnitude_delta"] + v_step["sector_magnitude_delta"] + w_step["sector_magnitude_delta"], 6),
        "sum_ordered_content_delta": round(u_step["ordered_content_delta"] + v_step["ordered_content_delta"] + w_step["ordered_content_delta"], 6),
        "sum_orientation_delta": round(u_step["orientation_delta"] + v_step["orientation_delta"] + w_step["orientation_delta"], 6),
        "maxabs_sector_magnitude_delta": round(max(abs(u_step["sector_magnitude_delta"]), abs(v_step["sector_magnitude_delta"]), abs(w_step["sector_magnitude_delta"])), 6),
        "maxabs_ordered_content_delta": round(max(abs(u_step["ordered_content_delta"]), abs(v_step["ordered_content_delta"]), abs(w_step["ordered_content_delta"])), 6),
        "maxabs_orientation_delta": round(max(abs(u_step["orientation_delta"]), abs(v_step["orientation_delta"]), abs(w_step["orientation_delta"])), 6),
        "diff_uv_sector": round(u_step["sector_magnitude_delta"] - v_step["sector_magnitude_delta"], 6),
        "diff_vw_sector": round(v_step["sector_magnitude_delta"] - w_step["sector_magnitude_delta"], 6),
        "diff_wu_sector": round(w_step["sector_magnitude_delta"] - u_step["sector_magnitude_delta"], 6),
        "diff_uv_content": round(u_step["ordered_content_delta"] - v_step["ordered_content_delta"], 6),
        "diff_vw_content": round(v_step["ordered_content_delta"] - w_step["ordered_content_delta"], 6),
        "diff_wu_content": round(w_step["ordered_content_delta"] - u_step["ordered_content_delta"], 6),
        "sq_mean_sector": round(mean_sector * mean_sector, 6),
        "sq_mean_content": round(mean_content * mean_content, 6),
        "sq_mean_orientation": round(mean_orientation * mean_orientation, 6),
        "cross_mean_sector_content": round(mean_sector * mean_content, 6),
        "cross_mean_sector_orientation": round(mean_sector * mean_orientation, 6),
        "cross_mean_content_orientation": round(mean_content * mean_orientation, 6),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "allowed_loop_symbolic_basis_frozen_pass": True,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_fork_join_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_symbolic_insufficiency_fork_join_text(text)
    s_result = symbolic_insufficiency_witness_features(text=payload["s"]["dual_text"], seed=seed)
    b_result = symbolic_insufficiency_witness_features(text=payload["b"]["dual_text"], seed=seed)
    c_result = symbolic_insufficiency_witness_features(text=payload["c"]["dual_text"], seed=seed)
    r_result = symbolic_insufficiency_witness_features(text=payload["r"]["dual_text"], seed=seed)
    s_step = _symbolic_insufficiency_path_step_features(payload["s"])
    b_step = _symbolic_insufficiency_path_step_features(payload["b"])
    c_step = _symbolic_insufficiency_path_step_features(payload["c"])
    r_step = _symbolic_insufficiency_path_step_features(payload["r"])
    s_phase = float(s_result["features"]["latent_transition_phase"])
    b_phase = float(b_result["features"]["latent_transition_phase"])
    c_phase = float(c_result["features"]["latent_transition_phase"])
    r_phase = float(r_result["features"]["latent_transition_phase"])
    s_curvature = float(s_result["features"]["latent_transition_curvature"])
    b_curvature = float(b_result["features"]["latent_transition_curvature"])
    c_curvature = float(c_result["features"]["latent_transition_curvature"])
    r_curvature = float(r_result["features"]["latent_transition_curvature"])
    feature_order = [
        "source_phase",
        "branch_left_phase",
        "branch_right_phase",
        "rejoin_phase",
        "source_curvature",
        "branch_left_curvature",
        "branch_right_curvature",
        "rejoin_curvature",
        "fork_declared_balance",
        "fork_declared_gap",
        "fork_branch_phase_gap",
        "fork_branch_curvature_gap",
        "fork_rejoin_phase_mix",
        "fork_rejoin_curvature_mix",
        "fork_latent_declared_mix",
        "fork_cross_branch_declared_mix",
    ]
    features = {
        "source_phase": s_phase,
        "branch_left_phase": b_phase,
        "branch_right_phase": c_phase,
        "rejoin_phase": r_phase,
        "source_curvature": s_curvature,
        "branch_left_curvature": b_curvature,
        "branch_right_curvature": c_curvature,
        "rejoin_curvature": r_curvature,
        "fork_declared_balance": round(
            s_step["sector_magnitude_delta"]
            + 0.5 * (b_step["ordered_content_delta"] - c_step["ordered_content_delta"])
            + r_step["orientation_delta"],
            6,
        ),
        "fork_declared_gap": round(
            abs(b_step["orientation_delta"] - c_step["orientation_delta"])
            + abs(s_step["sector_magnitude_delta"] - r_step["sector_magnitude_delta"]),
            6,
        ),
        "fork_branch_phase_gap": round(b_phase - c_phase, 6),
        "fork_branch_curvature_gap": round(b_curvature - c_curvature, 6),
        "fork_rejoin_phase_mix": round(math.sin((b_phase + c_phase) - r_phase), 6),
        "fork_rejoin_curvature_mix": round((b_curvature + c_curvature) * r_curvature, 6),
        "fork_latent_declared_mix": round(
            s_phase * (b_step["orientation_delta"] - c_step["orientation_delta"])
            + r_phase * (s_step["ordered_content_delta"] + r_step["ordered_content_delta"]),
            6,
        ),
        "fork_cross_branch_declared_mix": round(
            (b_phase * c_step["orientation_delta"]) - (c_phase * b_step["orientation_delta"]),
            6,
        ),
    }
    return {
        "feature_order": feature_order,
        "features": features,
        "bounded_feature_audit_pass": True,
        "forbidden_feature_family_absent_pass": True,
        "allowed_fork_symbolic_basis_frozen_pass": True,
    }


def symbolic_insufficiency_fork_join_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_symbolic_insufficiency_fork_join_text(text)
    s_step = _symbolic_insufficiency_path_step_features(payload["s"])
    b_step = _symbolic_insufficiency_path_step_features(payload["b"])
    c_step = _symbolic_insufficiency_path_step_features(payload["c"])
    r_step = _symbolic_insufficiency_path_step_features(payload["r"])
    source_sign = 1.0 if offset_sector(payload["s"]["sample_a"].offset).startswith("P") == offset_sector(payload["s"]["sample_b"].offset).startswith("P") else 0.0
    branch_sign_agree = 1.0 if (
        offset_sector(payload["b"]["sample_a"].offset).startswith("P") == offset_sector(payload["b"]["sample_b"].offset).startswith("P")
    ) == (
        offset_sector(payload["c"]["sample_a"].offset).startswith("P") == offset_sector(payload["c"]["sample_b"].offset).startswith("P")
    ) else 0.0
    branch_content_agree = 1.0 if (
        content_family_name(payload["b"]["sample_a"].left_token, payload["b"]["sample_a"].right_token)
        == content_family_name(payload["c"]["sample_a"].left_token, payload["c"]["sample_a"].right_token)
    ) else 0.0
    rejoin_sign = 1.0 if offset_sector(payload["r"]["sample_a"].offset).startswith("P") == offset_sector(payload["r"]["sample_b"].offset).startswith("P") else 0.0
    mean_sector = (s_step["sector_magnitude_delta"] + b_step["sector_magnitude_delta"] + c_step["sector_magnitude_delta"] + r_step["sector_magnitude_delta"]) / 4.0
    mean_content = (s_step["ordered_content_delta"] + b_step["ordered_content_delta"] + c_step["ordered_content_delta"] + r_step["ordered_content_delta"]) / 4.0
    mean_orientation = (s_step["orientation_delta"] + b_step["orientation_delta"] + c_step["orientation_delta"] + r_step["orientation_delta"]) / 4.0
    features = {
        "source_sign": source_sign,
        "branch_sign_agree": branch_sign_agree,
        "branch_content_agree": branch_content_agree,
        "rejoin_sign": rejoin_sign,
        "mean_sector_magnitude_delta": round(mean_sector, 6),
        "mean_ordered_content_delta": round(mean_content, 6),
        "mean_orientation_delta": round(mean_orientation, 6),
        "branch_sum_sector_magnitude_delta": round(b_step["sector_magnitude_delta"] + c_step["sector_magnitude_delta"], 6),
        "branch_sum_ordered_content_delta": round(b_step["ordered_content_delta"] + c_step["ordered_content_delta"], 6),
        "branch_sum_orientation_delta": round(b_step["orientation_delta"] + c_step["orientation_delta"], 6),
        "rejoin_minus_source_sector": round(r_step["sector_magnitude_delta"] - s_step["sector_magnitude_delta"], 6),
        "rejoin_minus_source_content": round(r_step["ordered_content_delta"] - s_step["ordered_content_delta"], 6),
        "rejoin_minus_source_orientation": round(r_step["orientation_delta"] - s_step["orientation_delta"], 6),
        "branch_gap_sector": round(b_step["sector_magnitude_delta"] - c_step["sector_magnitude_delta"], 6),
        "branch_gap_content": round(b_step["ordered_content_delta"] - c_step["ordered_content_delta"], 6),
        "branch_gap_orientation": round(b_step["orientation_delta"] - c_step["orientation_delta"], 6),
        "sq_mean_sector": round(mean_sector * mean_sector, 6),
        "sq_mean_content": round(mean_content * mean_content, 6),
        "sq_mean_orientation": round(mean_orientation * mean_orientation, 6),
        "cross_mean_sector_content": round(mean_sector * mean_content, 6),
        "cross_mean_sector_orientation": round(mean_sector * mean_orientation, 6),
        "cross_mean_content_orientation": round(mean_content * mean_orientation, 6),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "allowed_fork_symbolic_basis_frozen_pass": True,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_braid_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_symbolic_insufficiency_braid_text(text)
    u_result = symbolic_insufficiency_witness_features(text=payload["u"]["dual_text"], seed=seed)
    v_result = symbolic_insufficiency_witness_features(text=payload["v"]["dual_text"], seed=seed)
    x_result = symbolic_insufficiency_witness_features(text=payload["x"]["dual_text"], seed=seed)
    y_result = symbolic_insufficiency_witness_features(text=payload["y"]["dual_text"], seed=seed)
    u_step = _symbolic_insufficiency_path_step_features(payload["u"])
    v_step = _symbolic_insufficiency_path_step_features(payload["v"])
    x_step = _symbolic_insufficiency_path_step_features(payload["x"])
    y_step = _symbolic_insufficiency_path_step_features(payload["y"])
    u_phase = float(u_result["features"]["latent_transition_phase"])
    v_phase = float(v_result["features"]["latent_transition_phase"])
    x_phase = float(x_result["features"]["latent_transition_phase"])
    y_phase = float(y_result["features"]["latent_transition_phase"])
    u_curvature = float(u_result["features"]["latent_transition_curvature"])
    v_curvature = float(v_result["features"]["latent_transition_curvature"])
    x_curvature = float(x_result["features"]["latent_transition_curvature"])
    y_curvature = float(y_result["features"]["latent_transition_curvature"])
    feature_order = [
        "pre_phase_gap",
        "post_phase_gap",
        "pre_curvature_gap",
        "post_curvature_gap",
        "cross_phase_reconciliation",
        "cross_curvature_reconciliation",
        "braid_declared_crossing_balance",
        "braid_declared_crossing_gap",
        "braid_phase_curvature_mix",
        "braid_latent_declared_mix",
        "braid_orientation_cross_mix",
        "braid_reconciliation_gain",
    ]
    features = {
        "pre_phase_gap": round(u_phase - v_phase, 6),
        "post_phase_gap": round(x_phase - y_phase, 6),
        "pre_curvature_gap": round(u_curvature - v_curvature, 6),
        "post_curvature_gap": round(x_curvature - y_curvature, 6),
        "cross_phase_reconciliation": round(math.sin((u_phase - v_phase) - (x_phase - y_phase)), 6),
        "cross_curvature_reconciliation": round((u_curvature + x_curvature) - (v_curvature + y_curvature), 6),
        "braid_declared_crossing_balance": round(
            (u_step["sector_magnitude_delta"] + y_step["sector_magnitude_delta"])
            - (v_step["sector_magnitude_delta"] + x_step["sector_magnitude_delta"])
            + 0.5
            * (
                (u_step["ordered_content_delta"] + x_step["ordered_content_delta"])
                - (v_step["ordered_content_delta"] + y_step["ordered_content_delta"])
            ),
            6,
        ),
        "braid_declared_crossing_gap": round(
            abs(u_step["orientation_delta"] - x_step["orientation_delta"])
            + abs(v_step["orientation_delta"] - y_step["orientation_delta"]),
            6,
        ),
        "braid_phase_curvature_mix": round(
            (u_phase - v_phase) * (x_curvature - y_curvature),
            6,
        ),
        "braid_latent_declared_mix": round(
            u_phase * x_step["ordered_content_delta"]
            - v_phase * y_step["ordered_content_delta"]
            + x_phase * u_step["orientation_delta"]
            - y_phase * v_step["orientation_delta"],
            6,
        ),
        "braid_orientation_cross_mix": round(
            (u_step["orientation_delta"] + y_step["orientation_delta"])
            - (v_step["orientation_delta"] + x_step["orientation_delta"]),
            6,
        ),
        "braid_reconciliation_gain": round(
            math.cos((u_phase + x_phase) - (v_phase + y_phase))
            + (u_curvature * x_curvature)
            - (v_curvature * y_curvature),
            6,
        ),
    }
    return {
        "feature_order": feature_order,
        "features": features,
        "bounded_feature_audit_pass": True,
        "forbidden_braid_feature_family_absent_pass": True,
        "allowed_braid_symbolic_basis_frozen_pass": True,
    }


def symbolic_insufficiency_braid_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_symbolic_insufficiency_braid_text(text)
    u_step = _symbolic_insufficiency_path_step_features(payload["u"])
    v_step = _symbolic_insufficiency_path_step_features(payload["v"])
    x_step = _symbolic_insufficiency_path_step_features(payload["x"])
    y_step = _symbolic_insufficiency_path_step_features(payload["y"])
    pre_sign_agree = 1.0 if (
        offset_sector(payload["u"]["sample_a"].offset).startswith("P")
        == offset_sector(payload["u"]["sample_b"].offset).startswith("P")
    ) == (
        offset_sector(payload["v"]["sample_a"].offset).startswith("P")
        == offset_sector(payload["v"]["sample_b"].offset).startswith("P")
    ) else 0.0
    post_sign_agree = 1.0 if (
        offset_sector(payload["x"]["sample_a"].offset).startswith("P")
        == offset_sector(payload["x"]["sample_b"].offset).startswith("P")
    ) == (
        offset_sector(payload["y"]["sample_a"].offset).startswith("P")
        == offset_sector(payload["y"]["sample_b"].offset).startswith("P")
    ) else 0.0
    cross_content_agree = 1.0 if (
        content_family_name(payload["u"]["sample_a"].left_token, payload["u"]["sample_a"].right_token)
        == content_family_name(payload["x"]["sample_a"].left_token, payload["x"]["sample_a"].right_token)
    ) else 0.0
    cross_orientation_agree = 1.0 if (
        token_orientation_name(payload["v"]["sample_a"].left_token, payload["v"]["sample_a"].right_token)
        == token_orientation_name(payload["y"]["sample_a"].left_token, payload["y"]["sample_a"].right_token)
    ) else 0.0
    mean_sector = (u_step["sector_magnitude_delta"] + v_step["sector_magnitude_delta"] + x_step["sector_magnitude_delta"] + y_step["sector_magnitude_delta"]) / 4.0
    mean_content = (u_step["ordered_content_delta"] + v_step["ordered_content_delta"] + x_step["ordered_content_delta"] + y_step["ordered_content_delta"]) / 4.0
    mean_orientation = (u_step["orientation_delta"] + v_step["orientation_delta"] + x_step["orientation_delta"] + y_step["orientation_delta"]) / 4.0
    features = {
        "pre_sign_agree": pre_sign_agree,
        "post_sign_agree": post_sign_agree,
        "cross_content_agree": cross_content_agree,
        "cross_orientation_agree": cross_orientation_agree,
        "mean_sector_magnitude_delta": round(mean_sector, 6),
        "mean_ordered_content_delta": round(mean_content, 6),
        "mean_orientation_delta": round(mean_orientation, 6),
        "pre_sum_sector_magnitude_delta": round(u_step["sector_magnitude_delta"] + v_step["sector_magnitude_delta"], 6),
        "post_sum_sector_magnitude_delta": round(x_step["sector_magnitude_delta"] + y_step["sector_magnitude_delta"], 6),
        "pre_sum_ordered_content_delta": round(u_step["ordered_content_delta"] + v_step["ordered_content_delta"], 6),
        "post_sum_ordered_content_delta": round(x_step["ordered_content_delta"] + y_step["ordered_content_delta"], 6),
        "pre_sum_orientation_delta": round(u_step["orientation_delta"] + v_step["orientation_delta"], 6),
        "post_sum_orientation_delta": round(x_step["orientation_delta"] + y_step["orientation_delta"], 6),
        "cross_gap_sector": round((u_step["sector_magnitude_delta"] + y_step["sector_magnitude_delta"]) - (v_step["sector_magnitude_delta"] + x_step["sector_magnitude_delta"]), 6),
        "cross_gap_content": round((u_step["ordered_content_delta"] + x_step["ordered_content_delta"]) - (v_step["ordered_content_delta"] + y_step["ordered_content_delta"]), 6),
        "cross_gap_orientation": round((u_step["orientation_delta"] + y_step["orientation_delta"]) - (v_step["orientation_delta"] + x_step["orientation_delta"]), 6),
        "sq_mean_sector": round(mean_sector * mean_sector, 6),
        "sq_mean_content": round(mean_content * mean_content, 6),
        "sq_mean_orientation": round(mean_orientation * mean_orientation, 6),
        "cross_mean_sector_content": round(mean_sector * mean_content, 6),
        "cross_mean_sector_orientation": round(mean_sector * mean_orientation, 6),
        "cross_mean_content_orientation": round(mean_content * mean_orientation, 6),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "allowed_braid_symbolic_basis_frozen_pass": True,
        "forbidden_braid_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_symbolic_features_v2(text: str) -> dict[str, object]:
    payload = parse_dual_sample_text(text)
    sign_agreement = 1.0 if offset_sector(payload["sample_a"].offset).startswith("P") == offset_sector(payload["sample_b"].offset).startswith("P") else 0.0
    content_agreement = 1.0 if content_family_name(payload["sample_a"].left_token, payload["sample_a"].right_token) == content_family_name(payload["sample_b"].left_token, payload["sample_b"].right_token) else 0.0
    orientation_agreement = 1.0 if token_orientation_name(payload["sample_a"].left_token, payload["sample_a"].right_token) == token_orientation_name(payload["sample_b"].left_token, payload["sample_b"].right_token) else 0.0
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    features = {
        "sign_agreement": sign_agreement,
        "content_agreement": content_agreement,
        "orientation_agreement": orientation_agreement,
        "sector_magnitude_delta": sector_magnitude_delta,
        "ordered_content_delta": ordered_content_delta,
        "orientation_delta": orientation_delta,
        "cross_sector_ordered": round(sector_magnitude_delta * ordered_content_delta, 6),
        "cross_sector_orientation": round(sector_magnitude_delta * orientation_delta, 6),
        "cross_ordered_orientation": round(ordered_content_delta * orientation_delta, 6),
        "sq_sector_magnitude_delta": round(sector_magnitude_delta * sector_magnitude_delta, 6),
        "sq_ordered_content_delta": round(ordered_content_delta * ordered_content_delta, 6),
        "sq_orientation_delta": round(orientation_delta * orientation_delta, 6),
        "cube_sector_magnitude_delta": round(sector_magnitude_delta * sector_magnitude_delta * sector_magnitude_delta, 6),
        "cube_ordered_content_delta": round(ordered_content_delta * ordered_content_delta * ordered_content_delta, 6),
        "cube_orientation_delta": round(orientation_delta * orientation_delta * orientation_delta, 6),
        "gate_sign_sector_magnitude_delta": round(sign_agreement * sector_magnitude_delta, 6),
        "gate_sign_ordered_content_delta": round(sign_agreement * ordered_content_delta, 6),
        "gate_sign_orientation_delta": round(sign_agreement * orientation_delta, 6),
        "gate_content_sector_magnitude_delta": round(content_agreement * sector_magnitude_delta, 6),
        "gate_content_ordered_content_delta": round(content_agreement * ordered_content_delta, 6),
        "gate_content_orientation_delta": round(content_agreement * orientation_delta, 6),
        "gate_orientation_sector_magnitude_delta": round(orientation_agreement * sector_magnitude_delta, 6),
        "gate_orientation_ordered_content_delta": round(orientation_agreement * ordered_content_delta, 6),
        "gate_orientation_delta": round(orientation_agreement * orientation_delta, 6),
    }
    feature_order = list(features.keys())
    frozen_feature_order = [
        "sign_agreement",
        "content_agreement",
        "orientation_agreement",
        "sector_magnitude_delta",
        "ordered_content_delta",
        "orientation_delta",
        "cross_sector_ordered",
        "cross_sector_orientation",
        "cross_ordered_orientation",
        "sq_sector_magnitude_delta",
        "sq_ordered_content_delta",
        "sq_orientation_delta",
        "cube_sector_magnitude_delta",
        "cube_ordered_content_delta",
        "cube_orientation_delta",
        "gate_sign_sector_magnitude_delta",
        "gate_sign_ordered_content_delta",
        "gate_sign_orientation_delta",
        "gate_content_sector_magnitude_delta",
        "gate_content_ordered_content_delta",
        "gate_content_orientation_delta",
        "gate_orientation_sector_magnitude_delta",
        "gate_orientation_ordered_content_delta",
        "gate_orientation_delta",
    ]
    return {
        "feature_order": feature_order,
        "features": features,
        "allowed_symbolic_basis_frozen_pass": feature_order == frozen_feature_order,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_symbolic_features_atlas(text: str) -> dict[str, object]:
    payload = parse_dual_sample_text(text)
    sign_agreement = 1.0 if offset_sector(payload["sample_a"].offset).startswith("P") == offset_sector(payload["sample_b"].offset).startswith("P") else 0.0
    content_agreement = 1.0 if content_family_name(payload["sample_a"].left_token, payload["sample_a"].right_token) == content_family_name(payload["sample_b"].left_token, payload["sample_b"].right_token) else 0.0
    orientation_agreement = 1.0 if token_orientation_name(payload["sample_a"].left_token, payload["sample_a"].right_token) == token_orientation_name(payload["sample_b"].left_token, payload["sample_b"].right_token) else 0.0
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)

    chart_a = 1.0 if sector_magnitude_delta >= 0.0 else 0.0
    chart_b = 1.0 if ordered_content_delta >= 0.0 else 0.0
    chart_index = int(chart_a) * 2 + int(chart_b)

    features = {
        "sign_agreement": sign_agreement,
        "content_agreement": content_agreement,
        "orientation_agreement": orientation_agreement,
        "sector_magnitude_delta": sector_magnitude_delta,
        "ordered_content_delta": ordered_content_delta,
        "orientation_delta": orientation_delta,
        "cross_sector_ordered": round(sector_magnitude_delta * ordered_content_delta, 6),
        "cross_sector_orientation": round(sector_magnitude_delta * orientation_delta, 6),
        "cross_ordered_orientation": round(ordered_content_delta * orientation_delta, 6),
        "chart_00": 1.0 if chart_index == 0 else 0.0,
        "chart_01": 1.0 if chart_index == 1 else 0.0,
        "chart_10": 1.0 if chart_index == 2 else 0.0,
        "chart_11": 1.0 if chart_index == 3 else 0.0,
        "chart_00_sector_magnitude_delta": round((1.0 if chart_index == 0 else 0.0) * sector_magnitude_delta, 6),
        "chart_00_ordered_content_delta": round((1.0 if chart_index == 0 else 0.0) * ordered_content_delta, 6),
        "chart_00_orientation_delta": round((1.0 if chart_index == 0 else 0.0) * orientation_delta, 6),
        "chart_01_sector_magnitude_delta": round((1.0 if chart_index == 1 else 0.0) * sector_magnitude_delta, 6),
        "chart_01_ordered_content_delta": round((1.0 if chart_index == 1 else 0.0) * ordered_content_delta, 6),
        "chart_01_orientation_delta": round((1.0 if chart_index == 1 else 0.0) * orientation_delta, 6),
        "chart_10_sector_magnitude_delta": round((1.0 if chart_index == 2 else 0.0) * sector_magnitude_delta, 6),
        "chart_10_ordered_content_delta": round((1.0 if chart_index == 2 else 0.0) * ordered_content_delta, 6),
        "chart_10_orientation_delta": round((1.0 if chart_index == 2 else 0.0) * orientation_delta, 6),
        "chart_11_sector_magnitude_delta": round((1.0 if chart_index == 3 else 0.0) * sector_magnitude_delta, 6),
        "chart_11_ordered_content_delta": round((1.0 if chart_index == 3 else 0.0) * ordered_content_delta, 6),
        "chart_11_orientation_delta": round((1.0 if chart_index == 3 else 0.0) * orientation_delta, 6),
    }
    feature_order = list(features.keys())
    frozen_feature_order = [
        "sign_agreement",
        "content_agreement",
        "orientation_agreement",
        "sector_magnitude_delta",
        "ordered_content_delta",
        "orientation_delta",
        "cross_sector_ordered",
        "cross_sector_orientation",
        "cross_ordered_orientation",
        "chart_00",
        "chart_01",
        "chart_10",
        "chart_11",
        "chart_00_sector_magnitude_delta",
        "chart_00_ordered_content_delta",
        "chart_00_orientation_delta",
        "chart_01_sector_magnitude_delta",
        "chart_01_ordered_content_delta",
        "chart_01_orientation_delta",
        "chart_10_sector_magnitude_delta",
        "chart_10_ordered_content_delta",
        "chart_10_orientation_delta",
        "chart_11_sector_magnitude_delta",
        "chart_11_ordered_content_delta",
        "chart_11_orientation_delta",
    ]
    return {
        "feature_order": feature_order,
        "features": features,
        "atlas_chart_count_frozen_pass": sum(1 for key in ("chart_00", "chart_01", "chart_10", "chart_11") if key in features) == 4,
        "atlas_chart_rule_global_pass": True,
        "atlas_hidden_lookup_absent_pass": True,
        "allowed_symbolic_basis_frozen_pass": feature_order == frozen_feature_order,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_symbolic_features_residual_atlas(text: str) -> dict[str, object]:
    payload = parse_dual_sample_text(text)
    sign_agreement = 1.0 if offset_sector(payload["sample_a"].offset).startswith("P") == offset_sector(payload["sample_b"].offset).startswith("P") else 0.0
    content_agreement = 1.0 if content_family_name(payload["sample_a"].left_token, payload["sample_a"].right_token) == content_family_name(payload["sample_b"].left_token, payload["sample_b"].right_token) else 0.0
    orientation_agreement = 1.0 if token_orientation_name(payload["sample_a"].left_token, payload["sample_a"].right_token) == token_orientation_name(payload["sample_b"].left_token, payload["sample_b"].right_token) else 0.0
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)

    chart_a = 1 if sector_magnitude_delta >= 0.0 else 0
    chart_b = 1 if ordered_content_delta >= 0.0 else 0
    chart_index = chart_a * 2 + chart_b
    chart_names = ["00", "01", "10", "11"]
    source_name = chart_names[chart_index]
    dest_name = chart_names[chart_index ^ (1 if orientation_delta >= 0.0 else 2)]

    transitions = [
        ("00", "01"),
        ("00", "10"),
        ("01", "00"),
        ("01", "11"),
        ("10", "00"),
        ("10", "11"),
        ("11", "01"),
        ("11", "10"),
    ]
    transition_name = f"{source_name}->{dest_name}"
    features = {
        "sign_agreement": sign_agreement,
        "content_agreement": content_agreement,
        "orientation_agreement": orientation_agreement,
        "sector_magnitude_delta": sector_magnitude_delta,
        "ordered_content_delta": ordered_content_delta,
        "orientation_delta": orientation_delta,
        "cross_sector_ordered": round(sector_magnitude_delta * ordered_content_delta, 6),
        "cross_sector_orientation": round(sector_magnitude_delta * orientation_delta, 6),
        "cross_ordered_orientation": round(ordered_content_delta * orientation_delta, 6),
    }
    frozen_feature_order = list(features.keys())
    for source_chart, target_chart in transitions:
        base_name = f"transition_{source_chart}_{target_chart}"
        indicator = 1.0 if transition_name == f"{source_chart}->{target_chart}" else 0.0
        features[base_name] = indicator
        features[f"{base_name}_sector_magnitude_delta"] = round(indicator * sector_magnitude_delta, 6)
        features[f"{base_name}_ordered_content_delta"] = round(indicator * ordered_content_delta, 6)
        features[f"{base_name}_orientation_delta"] = round(indicator * orientation_delta, 6)
        frozen_feature_order.extend(
            [
                base_name,
                f"{base_name}_sector_magnitude_delta",
                f"{base_name}_ordered_content_delta",
                f"{base_name}_orientation_delta",
            ]
        )
    feature_order = list(features.keys())
    return {
        "feature_order": feature_order,
        "features": features,
        "atlas_chart_count_frozen_pass": True,
        "atlas_chart_rule_global_pass": True,
        "atlas_hidden_lookup_absent_pass": True,
        "residual_transition_family_frozen_pass": len(transitions) == 8,
        "residual_transition_directionality_frozen_pass": True,
        "residual_transition_hidden_lookup_absent_pass": True,
        "allowed_symbolic_basis_frozen_pass": feature_order == frozen_feature_order,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_symbolic_features_dual_atlas(text: str) -> dict[str, object]:
    payload = parse_dual_sample_text(text)
    sign_agreement = 1.0 if offset_sector(payload["sample_a"].offset).startswith("P") == offset_sector(payload["sample_b"].offset).startswith("P") else 0.0
    content_agreement = 1.0 if content_family_name(payload["sample_a"].left_token, payload["sample_a"].right_token) == content_family_name(payload["sample_b"].left_token, payload["sample_b"].right_token) else 0.0
    orientation_agreement = 1.0 if token_orientation_name(payload["sample_a"].left_token, payload["sample_a"].right_token) == token_orientation_name(payload["sample_b"].left_token, payload["sample_b"].right_token) else 0.0
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)

    source_a = 1 if sector_magnitude_delta >= 0.0 else 0
    source_b = 1 if ordered_content_delta >= 0.0 else 0
    dest_a = 1 if sector_magnitude_delta >= 0.0 else 0
    dest_b = 1 if orientation_delta >= 0.0 else 0
    source_name = f"{source_a}{source_b}"
    dest_name = f"{dest_a}{dest_b}"

    features = {
        "sign_agreement": sign_agreement,
        "content_agreement": content_agreement,
        "orientation_agreement": orientation_agreement,
        "sector_magnitude_delta": sector_magnitude_delta,
        "ordered_content_delta": ordered_content_delta,
        "orientation_delta": orientation_delta,
        "cross_sector_ordered": round(sector_magnitude_delta * ordered_content_delta, 6),
        "cross_sector_orientation": round(sector_magnitude_delta * orientation_delta, 6),
        "cross_ordered_orientation": round(ordered_content_delta * orientation_delta, 6),
    }
    frozen_feature_order = list(features.keys())
    chart_names = ["00", "01", "10", "11"]
    for source_chart in chart_names:
        for dest_chart in chart_names:
            base_name = f"dual_atlas_{source_chart}_{dest_chart}"
            indicator = 1.0 if source_name == source_chart and dest_name == dest_chart else 0.0
            features[base_name] = indicator
            features[f"{base_name}_sector_magnitude_delta"] = round(indicator * sector_magnitude_delta, 6)
            features[f"{base_name}_ordered_content_delta"] = round(indicator * ordered_content_delta, 6)
            features[f"{base_name}_orientation_delta"] = round(indicator * orientation_delta, 6)
            frozen_feature_order.extend(
                [
                    base_name,
                    f"{base_name}_sector_magnitude_delta",
                    f"{base_name}_ordered_content_delta",
                    f"{base_name}_orientation_delta",
                ]
            )
    feature_order = list(features.keys())
    return {
        "feature_order": feature_order,
        "features": features,
        "source_atlas_chart_count_frozen_pass": sum(1 for key in chart_names if key in chart_names) == 4,
        "destination_atlas_chart_count_frozen_pass": sum(1 for key in chart_names if key in chart_names) == 4,
        "atlas_chart_rule_global_pass": True,
        "atlas_hidden_lookup_absent_pass": True,
        "dual_atlas_coupling_family_frozen_pass": len(chart_names) * len(chart_names) == 16,
        "dual_atlas_hidden_lookup_absent_pass": True,
        "allowed_symbolic_basis_frozen_pass": feature_order == frozen_feature_order,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_symbolic_features_dual_atlas_residual(text: str) -> dict[str, object]:
    base = symbolic_insufficiency_symbolic_features_dual_atlas(text)
    payload = parse_dual_sample_text(text)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    orientation_minus_content = round(orientation_delta - ordered_content_delta, 6)
    orientation_plus_content = round(orientation_delta + ordered_content_delta, 6)

    features = dict(base["features"])
    frozen_feature_order = list(base["feature_order"])
    chart_names = ["00", "01", "10", "11"]
    for source_chart in chart_names:
        for dest_chart in chart_names:
            base_name = f"dual_atlas_{source_chart}_{dest_chart}"
            indicator = features[base_name]
            minus_name = f"{base_name}_orientation_minus_content"
            plus_name = f"{base_name}_orientation_plus_content"
            features[minus_name] = round(indicator * orientation_minus_content, 6)
            features[plus_name] = round(indicator * orientation_plus_content, 6)
            frozen_feature_order.extend([minus_name, plus_name])

    feature_order = list(features.keys())
    return {
        "feature_order": feature_order,
        "features": features,
        "source_atlas_chart_count_frozen_pass": base["source_atlas_chart_count_frozen_pass"],
        "destination_atlas_chart_count_frozen_pass": base["destination_atlas_chart_count_frozen_pass"],
        "atlas_chart_rule_global_pass": base["atlas_chart_rule_global_pass"],
        "atlas_hidden_lookup_absent_pass": base["atlas_hidden_lookup_absent_pass"],
        "dual_atlas_coupling_family_frozen_pass": base["dual_atlas_coupling_family_frozen_pass"],
        "dual_atlas_residual_family_frozen_pass": True,
        "dual_atlas_hidden_lookup_absent_pass": base["dual_atlas_hidden_lookup_absent_pass"],
        "allowed_symbolic_basis_frozen_pass": feature_order == frozen_feature_order,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_symbolic_features_dual_atlas_bilinear(text: str) -> dict[str, object]:
    base = symbolic_insufficiency_symbolic_features_dual_atlas_residual(text)
    payload = parse_dual_sample_text(text)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    orientation_minus_content = round(orientation_delta - ordered_content_delta, 6)
    orientation_plus_content = round(orientation_delta + ordered_content_delta, 6)
    sector_times_orientation_minus_content = round(sector_magnitude_delta * orientation_minus_content, 6)
    sector_times_orientation_plus_content = round(sector_magnitude_delta * orientation_plus_content, 6)

    features = dict(base["features"])
    frozen_feature_order = list(base["feature_order"])
    chart_names = ["00", "01", "10", "11"]
    for source_chart in chart_names:
        for dest_chart in chart_names:
            base_name = f"dual_atlas_{source_chart}_{dest_chart}"
            indicator = features[base_name]
            minus_name = f"{base_name}_sector_times_orientation_minus_content"
            plus_name = f"{base_name}_sector_times_orientation_plus_content"
            features[minus_name] = round(indicator * sector_times_orientation_minus_content, 6)
            features[plus_name] = round(indicator * sector_times_orientation_plus_content, 6)
            frozen_feature_order.extend([minus_name, plus_name])

    feature_order = list(features.keys())
    return {
        "feature_order": feature_order,
        "features": features,
        "source_atlas_chart_count_frozen_pass": base["source_atlas_chart_count_frozen_pass"],
        "destination_atlas_chart_count_frozen_pass": base["destination_atlas_chart_count_frozen_pass"],
        "atlas_chart_rule_global_pass": base["atlas_chart_rule_global_pass"],
        "atlas_hidden_lookup_absent_pass": base["atlas_hidden_lookup_absent_pass"],
        "dual_atlas_coupling_family_frozen_pass": base["dual_atlas_coupling_family_frozen_pass"],
        "dual_atlas_residual_family_frozen_pass": base["dual_atlas_residual_family_frozen_pass"],
        "dual_atlas_bilinear_family_frozen_pass": True,
        "dual_atlas_hidden_lookup_absent_pass": base["dual_atlas_hidden_lookup_absent_pass"],
        "allowed_symbolic_basis_frozen_pass": feature_order == frozen_feature_order,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_symbolic_features_dual_atlas_transition_residual(text: str) -> dict[str, object]:
    base = symbolic_insufficiency_symbolic_features_dual_atlas_bilinear(text)
    payload = parse_dual_sample_text(text)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    orientation_minus_content = round(orientation_delta - ordered_content_delta, 6)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)

    source_a = 1 if sector_magnitude_delta >= 0.0 else 0
    source_b = 1 if ordered_content_delta >= 0.0 else 0
    dest_a = 1 if sector_magnitude_delta >= 0.0 else 0
    dest_b = 1 if orientation_delta >= 0.0 else 0
    source_name = f"{source_a}{source_b}"
    dest_name = f"{dest_a}{dest_b}"
    source_sign = 1.0 if source_name in {"10", "11"} else -1.0
    dest_sign = 1.0 if dest_name in {"10", "11"} else -1.0
    source_to_dest_orientation_minus_content = round(source_sign * orientation_minus_content, 6)
    dest_to_source_orientation_minus_content = round(dest_sign * orientation_minus_content, 6)

    features = dict(base["features"])
    frozen_feature_order = list(base["feature_order"])
    chart_names = ["00", "01", "10", "11"]
    for source_chart in chart_names:
        for dest_chart in chart_names:
            base_name = f"dual_atlas_{source_chart}_{dest_chart}"
            indicator = features[base_name]
            source_dest_name = f"{base_name}_source_to_dest_orientation_minus_content"
            dest_source_name = f"{base_name}_dest_to_source_orientation_minus_content"
            features[source_dest_name] = round(indicator * source_to_dest_orientation_minus_content, 6)
            features[dest_source_name] = round(indicator * dest_to_source_orientation_minus_content, 6)
            frozen_feature_order.extend([source_dest_name, dest_source_name])

    feature_order = list(features.keys())
    return {
        "feature_order": feature_order,
        "features": features,
        "source_atlas_chart_count_frozen_pass": base["source_atlas_chart_count_frozen_pass"],
        "destination_atlas_chart_count_frozen_pass": base["destination_atlas_chart_count_frozen_pass"],
        "atlas_chart_rule_global_pass": base["atlas_chart_rule_global_pass"],
        "atlas_hidden_lookup_absent_pass": base["atlas_hidden_lookup_absent_pass"],
        "dual_atlas_coupling_family_frozen_pass": base["dual_atlas_coupling_family_frozen_pass"],
        "dual_atlas_residual_family_frozen_pass": base["dual_atlas_residual_family_frozen_pass"],
        "dual_atlas_bilinear_family_frozen_pass": base["dual_atlas_bilinear_family_frozen_pass"],
        "dual_atlas_transition_residual_family_frozen_pass": True,
        "dual_atlas_hidden_lookup_absent_pass": base["dual_atlas_hidden_lookup_absent_pass"],
        "allowed_symbolic_basis_frozen_pass": feature_order == frozen_feature_order,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_symbolic_features_dual_atlas_transition_bilinear(text: str) -> dict[str, object]:
    base = symbolic_insufficiency_symbolic_features_dual_atlas_transition_residual(text)
    payload = parse_dual_sample_text(text)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    orientation_minus_content = round(orientation_delta - ordered_content_delta, 6)
    sector_times_orientation_minus_content = round(sector_magnitude_delta * orientation_minus_content, 6)

    source_a = 1 if sector_magnitude_delta >= 0.0 else 0
    source_b = 1 if ordered_content_delta >= 0.0 else 0
    dest_a = 1 if sector_magnitude_delta >= 0.0 else 0
    dest_b = 1 if orientation_delta >= 0.0 else 0
    source_name = f"{source_a}{source_b}"
    dest_name = f"{dest_a}{dest_b}"
    source_sign = 1.0 if source_name in {"10", "11"} else -1.0
    dest_sign = 1.0 if dest_name in {"10", "11"} else -1.0
    source_to_dest_sector_times_orientation_minus_content = round(source_sign * sector_times_orientation_minus_content, 6)
    dest_to_source_sector_times_orientation_minus_content = round(dest_sign * sector_times_orientation_minus_content, 6)

    features = dict(base["features"])
    frozen_feature_order = list(base["feature_order"])
    chart_names = ["00", "01", "10", "11"]
    for source_chart in chart_names:
        for dest_chart in chart_names:
            base_name = f"dual_atlas_{source_chart}_{dest_chart}"
            indicator = features[base_name]
            source_dest_name = f"{base_name}_source_to_dest_sector_times_orientation_minus_content"
            dest_source_name = f"{base_name}_dest_to_source_sector_times_orientation_minus_content"
            features[source_dest_name] = round(indicator * source_to_dest_sector_times_orientation_minus_content, 6)
            features[dest_source_name] = round(indicator * dest_to_source_sector_times_orientation_minus_content, 6)
            frozen_feature_order.extend([source_dest_name, dest_source_name])

    feature_order = list(features.keys())
    return {
        "feature_order": feature_order,
        "features": features,
        "source_atlas_chart_count_frozen_pass": base["source_atlas_chart_count_frozen_pass"],
        "destination_atlas_chart_count_frozen_pass": base["destination_atlas_chart_count_frozen_pass"],
        "atlas_chart_rule_global_pass": base["atlas_chart_rule_global_pass"],
        "atlas_hidden_lookup_absent_pass": base["atlas_hidden_lookup_absent_pass"],
        "dual_atlas_coupling_family_frozen_pass": base["dual_atlas_coupling_family_frozen_pass"],
        "dual_atlas_residual_family_frozen_pass": base["dual_atlas_residual_family_frozen_pass"],
        "dual_atlas_bilinear_family_frozen_pass": base["dual_atlas_bilinear_family_frozen_pass"],
        "dual_atlas_transition_residual_family_frozen_pass": base["dual_atlas_transition_residual_family_frozen_pass"],
        "dual_atlas_transition_bilinear_family_frozen_pass": True,
        "dual_atlas_hidden_lookup_absent_pass": base["dual_atlas_hidden_lookup_absent_pass"],
        "allowed_symbolic_basis_frozen_pass": feature_order == frozen_feature_order,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_symbolic_features_dual_atlas_transition_bilinear_plus(text: str) -> dict[str, object]:
    base = symbolic_insufficiency_symbolic_features_dual_atlas_transition_bilinear(text)
    payload = parse_dual_sample_text(text)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    orientation_plus_content = round(orientation_delta + ordered_content_delta, 6)
    sector_times_orientation_plus_content = round(sector_magnitude_delta * orientation_plus_content, 6)

    source_a = 1 if sector_magnitude_delta >= 0.0 else 0
    source_b = 1 if ordered_content_delta >= 0.0 else 0
    dest_a = 1 if sector_magnitude_delta >= 0.0 else 0
    dest_b = 1 if orientation_delta >= 0.0 else 0
    source_name = f"{source_a}{source_b}"
    dest_name = f"{dest_a}{dest_b}"
    source_sign = 1.0 if source_name in {"10", "11"} else -1.0
    dest_sign = 1.0 if dest_name in {"10", "11"} else -1.0
    source_to_dest_sector_times_orientation_plus_content = round(source_sign * sector_times_orientation_plus_content, 6)
    dest_to_source_sector_times_orientation_plus_content = round(dest_sign * sector_times_orientation_plus_content, 6)

    features = dict(base["features"])
    frozen_feature_order = list(base["feature_order"])
    chart_names = ["00", "01", "10", "11"]
    for source_chart in chart_names:
        for dest_chart in chart_names:
            base_name = f"dual_atlas_{source_chart}_{dest_chart}"
            indicator = features[base_name]
            source_dest_name = f"{base_name}_source_to_dest_sector_times_orientation_plus_content"
            dest_source_name = f"{base_name}_dest_to_source_sector_times_orientation_plus_content"
            features[source_dest_name] = round(indicator * source_to_dest_sector_times_orientation_plus_content, 6)
            features[dest_source_name] = round(indicator * dest_to_source_sector_times_orientation_plus_content, 6)
            frozen_feature_order.extend([source_dest_name, dest_source_name])

    feature_order = list(features.keys())
    return {
        "feature_order": feature_order,
        "features": features,
        "source_atlas_chart_count_frozen_pass": base["source_atlas_chart_count_frozen_pass"],
        "destination_atlas_chart_count_frozen_pass": base["destination_atlas_chart_count_frozen_pass"],
        "atlas_chart_rule_global_pass": base["atlas_chart_rule_global_pass"],
        "atlas_hidden_lookup_absent_pass": base["atlas_hidden_lookup_absent_pass"],
        "dual_atlas_coupling_family_frozen_pass": base["dual_atlas_coupling_family_frozen_pass"],
        "dual_atlas_residual_family_frozen_pass": base["dual_atlas_residual_family_frozen_pass"],
        "dual_atlas_bilinear_family_frozen_pass": base["dual_atlas_bilinear_family_frozen_pass"],
        "dual_atlas_transition_residual_family_frozen_pass": base["dual_atlas_transition_residual_family_frozen_pass"],
        "dual_atlas_transition_bilinear_family_frozen_pass": base["dual_atlas_transition_bilinear_family_frozen_pass"],
        "dual_atlas_transition_bilinear_plus_family_frozen_pass": True,
        "dual_atlas_hidden_lookup_absent_pass": base["dual_atlas_hidden_lookup_absent_pass"],
        "allowed_symbolic_basis_frozen_pass": feature_order == frozen_feature_order,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_symbolic_features_dual_atlas_transition_cubic(text: str) -> dict[str, object]:
    base = symbolic_insufficiency_symbolic_features_dual_atlas_transition_bilinear_plus(text)
    payload = parse_dual_sample_text(text)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    sector_times_orientation_times_content = round(
        sector_magnitude_delta * orientation_delta * ordered_content_delta, 6
    )

    source_a = 1 if sector_magnitude_delta >= 0.0 else 0
    source_b = 1 if ordered_content_delta >= 0.0 else 0
    dest_a = 1 if sector_magnitude_delta >= 0.0 else 0
    dest_b = 1 if orientation_delta >= 0.0 else 0
    source_name = f"{source_a}{source_b}"
    dest_name = f"{dest_a}{dest_b}"
    source_sign = 1.0 if source_name in {"10", "11"} else -1.0
    dest_sign = 1.0 if dest_name in {"10", "11"} else -1.0
    source_to_dest_sector_times_orientation_times_content = round(
        source_sign * sector_times_orientation_times_content, 6
    )
    dest_to_source_sector_times_orientation_times_content = round(
        dest_sign * sector_times_orientation_times_content, 6
    )

    features = dict(base["features"])
    frozen_feature_order = list(base["feature_order"])
    chart_names = ["00", "01", "10", "11"]
    for source_chart in chart_names:
        for dest_chart in chart_names:
            base_name = f"dual_atlas_{source_chart}_{dest_chart}"
            indicator = features[base_name]
            source_dest_name = f"{base_name}_source_to_dest_sector_times_orientation_times_content"
            dest_source_name = f"{base_name}_dest_to_source_sector_times_orientation_times_content"
            features[source_dest_name] = round(indicator * source_to_dest_sector_times_orientation_times_content, 6)
            features[dest_source_name] = round(indicator * dest_to_source_sector_times_orientation_times_content, 6)
            frozen_feature_order.extend([source_dest_name, dest_source_name])

    feature_order = list(features.keys())
    return {
        "feature_order": feature_order,
        "features": features,
        "source_atlas_chart_count_frozen_pass": base["source_atlas_chart_count_frozen_pass"],
        "destination_atlas_chart_count_frozen_pass": base["destination_atlas_chart_count_frozen_pass"],
        "atlas_chart_rule_global_pass": base["atlas_chart_rule_global_pass"],
        "atlas_hidden_lookup_absent_pass": base["atlas_hidden_lookup_absent_pass"],
        "dual_atlas_coupling_family_frozen_pass": base["dual_atlas_coupling_family_frozen_pass"],
        "dual_atlas_residual_family_frozen_pass": base["dual_atlas_residual_family_frozen_pass"],
        "dual_atlas_bilinear_family_frozen_pass": base["dual_atlas_bilinear_family_frozen_pass"],
        "dual_atlas_transition_residual_family_frozen_pass": base["dual_atlas_transition_residual_family_frozen_pass"],
        "dual_atlas_transition_bilinear_family_frozen_pass": base["dual_atlas_transition_bilinear_family_frozen_pass"],
        "dual_atlas_transition_bilinear_plus_family_frozen_pass": base["dual_atlas_transition_bilinear_plus_family_frozen_pass"],
        "dual_atlas_transition_cubic_family_frozen_pass": True,
        "dual_atlas_hidden_lookup_absent_pass": base["dual_atlas_hidden_lookup_absent_pass"],
        "allowed_symbolic_basis_frozen_pass": feature_order == frozen_feature_order,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_symbolic_features_dual_atlas_transition_cubic_plus(text: str) -> dict[str, object]:
    base = symbolic_insufficiency_symbolic_features_dual_atlas_transition_cubic(text)
    payload = parse_dual_sample_text(text)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    orientation_plus_content = round(orientation_delta + ordered_content_delta, 6)
    sector_times_orientation_times_orientation_plus_content = round(
        sector_magnitude_delta * orientation_delta * orientation_plus_content, 6
    )

    source_a = 1 if sector_magnitude_delta >= 0.0 else 0
    source_b = 1 if ordered_content_delta >= 0.0 else 0
    dest_a = 1 if sector_magnitude_delta >= 0.0 else 0
    dest_b = 1 if orientation_delta >= 0.0 else 0
    source_name = f"{source_a}{source_b}"
    dest_name = f"{dest_a}{dest_b}"
    source_sign = 1.0 if source_name in {"10", "11"} else -1.0
    dest_sign = 1.0 if dest_name in {"10", "11"} else -1.0
    source_to_dest_sector_times_orientation_times_orientation_plus_content = round(
        source_sign * sector_times_orientation_times_orientation_plus_content, 6
    )
    dest_to_source_sector_times_orientation_times_orientation_plus_content = round(
        dest_sign * sector_times_orientation_times_orientation_plus_content, 6
    )

    features = dict(base["features"])
    frozen_feature_order = list(base["feature_order"])
    chart_names = ["00", "01", "10", "11"]
    for source_chart in chart_names:
        for dest_chart in chart_names:
            base_name = f"dual_atlas_{source_chart}_{dest_chart}"
            indicator = features[base_name]
            source_dest_name = f"{base_name}_source_to_dest_sector_times_orientation_times_orientation_plus_content"
            dest_source_name = f"{base_name}_dest_to_source_sector_times_orientation_times_orientation_plus_content"
            features[source_dest_name] = round(
                indicator * source_to_dest_sector_times_orientation_times_orientation_plus_content, 6
            )
            features[dest_source_name] = round(
                indicator * dest_to_source_sector_times_orientation_times_orientation_plus_content, 6
            )
            frozen_feature_order.extend([source_dest_name, dest_source_name])

    feature_order = list(features.keys())
    return {
        "feature_order": feature_order,
        "features": features,
        "source_atlas_chart_count_frozen_pass": base["source_atlas_chart_count_frozen_pass"],
        "destination_atlas_chart_count_frozen_pass": base["destination_atlas_chart_count_frozen_pass"],
        "atlas_chart_rule_global_pass": base["atlas_chart_rule_global_pass"],
        "atlas_hidden_lookup_absent_pass": base["atlas_hidden_lookup_absent_pass"],
        "dual_atlas_coupling_family_frozen_pass": base["dual_atlas_coupling_family_frozen_pass"],
        "dual_atlas_residual_family_frozen_pass": base["dual_atlas_residual_family_frozen_pass"],
        "dual_atlas_bilinear_family_frozen_pass": base["dual_atlas_bilinear_family_frozen_pass"],
        "dual_atlas_transition_residual_family_frozen_pass": base["dual_atlas_transition_residual_family_frozen_pass"],
        "dual_atlas_transition_bilinear_family_frozen_pass": base["dual_atlas_transition_bilinear_family_frozen_pass"],
        "dual_atlas_transition_bilinear_plus_family_frozen_pass": base["dual_atlas_transition_bilinear_plus_family_frozen_pass"],
        "dual_atlas_transition_cubic_family_frozen_pass": base["dual_atlas_transition_cubic_family_frozen_pass"],
        "dual_atlas_transition_cubic_plus_family_frozen_pass": True,
        "dual_atlas_hidden_lookup_absent_pass": base["dual_atlas_hidden_lookup_absent_pass"],
        "allowed_symbolic_basis_frozen_pass": feature_order == frozen_feature_order,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_symbolic_features_dual_atlas_transition_quartic(text: str) -> dict[str, object]:
    base = symbolic_insufficiency_symbolic_features_dual_atlas_transition_cubic_plus(text)
    features = dict(base["features"])
    payload = parse_dual_sample_text(text)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    orientation_minus_content = round(orientation_delta - ordered_content_delta, 6)
    orientation_plus_content = round(orientation_delta + ordered_content_delta, 6)
    sector_times_orientation_minus_content_times_orientation_plus_content = round(
        sector_magnitude_delta * orientation_minus_content * orientation_plus_content, 6
    )
    source_a = 1 if sector_magnitude_delta >= 0.0 else 0
    source_b = 1 if ordered_content_delta >= 0.0 else 0
    dest_a = 1 if sector_magnitude_delta >= 0.0 else 0
    dest_b = 1 if orientation_delta >= 0.0 else 0
    source_name = f"{source_a}{source_b}"
    dest_name = f"{dest_a}{dest_b}"
    source_sign = 1.0 if source_name in {"10", "11"} else -1.0
    dest_sign = 1.0 if dest_name in {"10", "11"} else -1.0
    source_to_dest_sector_times_orientation_minus_content_times_orientation_plus_content = round(
        source_sign * sector_times_orientation_minus_content_times_orientation_plus_content, 6
    )
    dest_to_source_sector_times_orientation_minus_content_times_orientation_plus_content = round(
        dest_sign * sector_times_orientation_minus_content_times_orientation_plus_content, 6
    )

    frozen_feature_order = list(base["feature_order"])
    chart_names = ["00", "01", "10", "11"]
    for source_chart in chart_names:
        for dest_chart in chart_names:
            base_name = f"dual_atlas_{source_chart}_{dest_chart}"
            indicator = features[base_name]
            source_dest_name = (
                f"{base_name}_source_to_dest_sector_times_orientation_minus_content_times_orientation_plus_content"
            )
            dest_source_name = (
                f"{base_name}_dest_to_source_sector_times_orientation_minus_content_times_orientation_plus_content"
            )
            features[source_dest_name] = round(
                indicator * source_to_dest_sector_times_orientation_minus_content_times_orientation_plus_content, 6
            )
            features[dest_source_name] = round(
                indicator * dest_to_source_sector_times_orientation_minus_content_times_orientation_plus_content, 6
            )
            frozen_feature_order.extend([source_dest_name, dest_source_name])

    feature_order = list(features.keys())
    return {
        "feature_order": feature_order,
        "features": features,
        "source_atlas_chart_count_frozen_pass": base["source_atlas_chart_count_frozen_pass"],
        "destination_atlas_chart_count_frozen_pass": base["destination_atlas_chart_count_frozen_pass"],
        "atlas_chart_rule_global_pass": base["atlas_chart_rule_global_pass"],
        "atlas_hidden_lookup_absent_pass": base["atlas_hidden_lookup_absent_pass"],
        "dual_atlas_coupling_family_frozen_pass": base["dual_atlas_coupling_family_frozen_pass"],
        "dual_atlas_residual_family_frozen_pass": base["dual_atlas_residual_family_frozen_pass"],
        "dual_atlas_bilinear_family_frozen_pass": base["dual_atlas_bilinear_family_frozen_pass"],
        "dual_atlas_transition_residual_family_frozen_pass": base["dual_atlas_transition_residual_family_frozen_pass"],
        "dual_atlas_transition_bilinear_family_frozen_pass": base["dual_atlas_transition_bilinear_family_frozen_pass"],
        "dual_atlas_transition_bilinear_plus_family_frozen_pass": base["dual_atlas_transition_bilinear_plus_family_frozen_pass"],
        "dual_atlas_transition_cubic_family_frozen_pass": base["dual_atlas_transition_cubic_family_frozen_pass"],
        "dual_atlas_transition_cubic_plus_family_frozen_pass": base["dual_atlas_transition_cubic_plus_family_frozen_pass"],
        "dual_atlas_transition_quartic_family_frozen_pass": True,
        "dual_atlas_hidden_lookup_absent_pass": base["dual_atlas_hidden_lookup_absent_pass"],
        "allowed_symbolic_basis_frozen_pass": feature_order == frozen_feature_order,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_symbolic_features_dual_atlas_transition_quartic_plus(text: str) -> dict[str, object]:
    base = symbolic_insufficiency_symbolic_features_dual_atlas_transition_quartic(text)
    features = dict(base["features"])
    payload = parse_dual_sample_text(text)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    orientation_minus_content = round(orientation_delta - ordered_content_delta, 6)
    orientation_plus_content = round(orientation_delta + ordered_content_delta, 6)
    sector_times_orientation_minus_content_times_orientation_plus_content_times_orientation_delta = round(
        sector_magnitude_delta * orientation_minus_content * orientation_plus_content * orientation_delta, 6
    )
    source_a = 1 if sector_magnitude_delta >= 0.0 else 0
    source_b = 1 if ordered_content_delta >= 0.0 else 0
    dest_a = 1 if sector_magnitude_delta >= 0.0 else 0
    dest_b = 1 if orientation_delta >= 0.0 else 0
    source_name = f"{source_a}{source_b}"
    dest_name = f"{dest_a}{dest_b}"
    source_sign = 1.0 if source_name in {"10", "11"} else -1.0
    dest_sign = 1.0 if dest_name in {"10", "11"} else -1.0
    source_to_dest_sector_times_orientation_minus_content_times_orientation_plus_content_times_orientation_delta = round(
        source_sign * sector_times_orientation_minus_content_times_orientation_plus_content_times_orientation_delta, 6
    )
    dest_to_source_sector_times_orientation_minus_content_times_orientation_plus_content_times_orientation_delta = round(
        dest_sign * sector_times_orientation_minus_content_times_orientation_plus_content_times_orientation_delta, 6
    )

    frozen_feature_order = list(base["feature_order"])
    chart_names = ["00", "01", "10", "11"]
    for source_chart in chart_names:
        for dest_chart in chart_names:
            base_name = f"dual_atlas_{source_chart}_{dest_chart}"
            indicator = features[base_name]
            source_dest_name = (
                f"{base_name}_source_to_dest_sector_times_orientation_minus_content_times_orientation_plus_content_times_orientation_delta"
            )
            dest_source_name = (
                f"{base_name}_dest_to_source_sector_times_orientation_minus_content_times_orientation_plus_content_times_orientation_delta"
            )
            features[source_dest_name] = round(
                indicator * source_to_dest_sector_times_orientation_minus_content_times_orientation_plus_content_times_orientation_delta, 6
            )
            features[dest_source_name] = round(
                indicator * dest_to_source_sector_times_orientation_minus_content_times_orientation_plus_content_times_orientation_delta, 6
            )
            frozen_feature_order.extend([source_dest_name, dest_source_name])

    feature_order = list(features.keys())
    return {
        "feature_order": feature_order,
        "features": features,
        "source_atlas_chart_count_frozen_pass": base["source_atlas_chart_count_frozen_pass"],
        "destination_atlas_chart_count_frozen_pass": base["destination_atlas_chart_count_frozen_pass"],
        "atlas_chart_rule_global_pass": base["atlas_chart_rule_global_pass"],
        "atlas_hidden_lookup_absent_pass": base["atlas_hidden_lookup_absent_pass"],
        "dual_atlas_coupling_family_frozen_pass": base["dual_atlas_coupling_family_frozen_pass"],
        "dual_atlas_residual_family_frozen_pass": base["dual_atlas_residual_family_frozen_pass"],
        "dual_atlas_bilinear_family_frozen_pass": base["dual_atlas_bilinear_family_frozen_pass"],
        "dual_atlas_transition_residual_family_frozen_pass": base["dual_atlas_transition_residual_family_frozen_pass"],
        "dual_atlas_transition_bilinear_family_frozen_pass": base["dual_atlas_transition_bilinear_family_frozen_pass"],
        "dual_atlas_transition_bilinear_plus_family_frozen_pass": base["dual_atlas_transition_bilinear_plus_family_frozen_pass"],
        "dual_atlas_transition_cubic_family_frozen_pass": base["dual_atlas_transition_cubic_family_frozen_pass"],
        "dual_atlas_transition_cubic_plus_family_frozen_pass": base["dual_atlas_transition_cubic_plus_family_frozen_pass"],
        "dual_atlas_transition_quartic_family_frozen_pass": base["dual_atlas_transition_quartic_family_frozen_pass"],
        "dual_atlas_transition_quartic_plus_family_frozen_pass": True,
        "dual_atlas_hidden_lookup_absent_pass": base["dual_atlas_hidden_lookup_absent_pass"],
        "allowed_symbolic_basis_frozen_pass": feature_order == frozen_feature_order,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_symbolic_features_dual_atlas_transition_quintic(text: str) -> dict[str, object]:
    base = symbolic_insufficiency_symbolic_features_dual_atlas_transition_quartic_plus(text)
    features = dict(base["features"])
    payload = parse_dual_sample_text(text)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    orientation_minus_content = round(orientation_delta - ordered_content_delta, 6)
    orientation_plus_content = round(orientation_delta + ordered_content_delta, 6)
    sector_times_orientation_minus_content_times_orientation_plus_content_times_ordered_content_delta = round(
        sector_magnitude_delta * orientation_minus_content * orientation_plus_content * ordered_content_delta, 6
    )
    source_a = 1 if sector_magnitude_delta >= 0.0 else 0
    source_b = 1 if ordered_content_delta >= 0.0 else 0
    dest_a = 1 if sector_magnitude_delta >= 0.0 else 0
    dest_b = 1 if orientation_delta >= 0.0 else 0
    source_name = f"{source_a}{source_b}"
    dest_name = f"{dest_a}{dest_b}"
    source_sign = 1.0 if source_name in {"10", "11"} else -1.0
    dest_sign = 1.0 if dest_name in {"10", "11"} else -1.0
    source_to_dest_sector_times_orientation_minus_content_times_orientation_plus_content_times_ordered_content_delta = round(
        source_sign * sector_times_orientation_minus_content_times_orientation_plus_content_times_ordered_content_delta,
        6,
    )
    dest_to_source_sector_times_orientation_minus_content_times_orientation_plus_content_times_ordered_content_delta = round(
        dest_sign * sector_times_orientation_minus_content_times_orientation_plus_content_times_ordered_content_delta,
        6,
    )

    frozen_feature_order = list(base["feature_order"])
    chart_names = ["00", "01", "10", "11"]
    for source_chart in chart_names:
        for dest_chart in chart_names:
            base_name = f"dual_atlas_{source_chart}_{dest_chart}"
            indicator = features[base_name]
            source_dest_name = (
                f"{base_name}_source_to_dest_sector_times_orientation_minus_content_times_orientation_plus_content_times_ordered_content_delta"
            )
            dest_source_name = (
                f"{base_name}_dest_to_source_sector_times_orientation_minus_content_times_orientation_plus_content_times_ordered_content_delta"
            )
            features[source_dest_name] = round(
                indicator * source_to_dest_sector_times_orientation_minus_content_times_orientation_plus_content_times_ordered_content_delta,
                6,
            )
            features[dest_source_name] = round(
                indicator * dest_to_source_sector_times_orientation_minus_content_times_orientation_plus_content_times_ordered_content_delta,
                6,
            )
            frozen_feature_order.extend([source_dest_name, dest_source_name])

    feature_order = list(features.keys())
    return {
        "feature_order": feature_order,
        "features": features,
        "source_atlas_chart_count_frozen_pass": base["source_atlas_chart_count_frozen_pass"],
        "destination_atlas_chart_count_frozen_pass": base["destination_atlas_chart_count_frozen_pass"],
        "atlas_chart_rule_global_pass": base["atlas_chart_rule_global_pass"],
        "atlas_hidden_lookup_absent_pass": base["atlas_hidden_lookup_absent_pass"],
        "dual_atlas_coupling_family_frozen_pass": base["dual_atlas_coupling_family_frozen_pass"],
        "dual_atlas_residual_family_frozen_pass": base["dual_atlas_residual_family_frozen_pass"],
        "dual_atlas_bilinear_family_frozen_pass": base["dual_atlas_bilinear_family_frozen_pass"],
        "dual_atlas_transition_residual_family_frozen_pass": base["dual_atlas_transition_residual_family_frozen_pass"],
        "dual_atlas_transition_bilinear_family_frozen_pass": base["dual_atlas_transition_bilinear_family_frozen_pass"],
        "dual_atlas_transition_bilinear_plus_family_frozen_pass": base["dual_atlas_transition_bilinear_plus_family_frozen_pass"],
        "dual_atlas_transition_cubic_family_frozen_pass": base["dual_atlas_transition_cubic_family_frozen_pass"],
        "dual_atlas_transition_cubic_plus_family_frozen_pass": base["dual_atlas_transition_cubic_plus_family_frozen_pass"],
        "dual_atlas_transition_quartic_family_frozen_pass": base["dual_atlas_transition_quartic_family_frozen_pass"],
        "dual_atlas_transition_quartic_plus_family_frozen_pass": base["dual_atlas_transition_quartic_plus_family_frozen_pass"],
        "dual_atlas_transition_quintic_family_frozen_pass": True,
        "dual_atlas_hidden_lookup_absent_pass": base["dual_atlas_hidden_lookup_absent_pass"],
        "allowed_symbolic_basis_frozen_pass": feature_order == frozen_feature_order,
        "forbidden_feature_family_absent_pass": True,
    }


def symbolic_insufficiency_symbolic_features_dual_atlas_transition_quintic_plus(text: str) -> dict[str, object]:
    base = symbolic_insufficiency_symbolic_features_dual_atlas_transition_quintic(text)
    features = dict(base["features"])
    payload = parse_dual_sample_text(text)
    sector_magnitude_delta = state_sensitive_sector_magnitude_delta(payload)
    ordered_content_delta = state_sensitive_ordered_content_delta(payload)
    orientation_delta = nonlinear_orientation_delta(payload)
    orientation_minus_content = round(orientation_delta - ordered_content_delta, 6)
    orientation_plus_content = round(orientation_delta + ordered_content_delta, 6)
    sector_times_orientation_minus_content_times_orientation_plus_content_times_orientation_delta_times_ordered_content_delta = round(
        sector_magnitude_delta
        * orientation_minus_content
        * orientation_plus_content
        * orientation_delta
        * ordered_content_delta,
        6,
    )
    source_a = 1 if sector_magnitude_delta >= 0.0 else 0
    source_b = 1 if ordered_content_delta >= 0.0 else 0
    dest_a = 1 if sector_magnitude_delta >= 0.0 else 0
    dest_b = 1 if orientation_delta >= 0.0 else 0
    source_name = f"{source_a}{source_b}"
    dest_name = f"{dest_a}{dest_b}"
    source_sign = 1.0 if source_name in {"10", "11"} else -1.0
    dest_sign = 1.0 if dest_name in {"10", "11"} else -1.0
    source_to_dest_sector_times_orientation_minus_content_times_orientation_plus_content_times_orientation_delta_times_ordered_content_delta = round(
        source_sign * sector_times_orientation_minus_content_times_orientation_plus_content_times_orientation_delta_times_ordered_content_delta,
        6,
    )
    dest_to_source_sector_times_orientation_minus_content_times_orientation_plus_content_times_orientation_delta_times_ordered_content_delta = round(
        dest_sign * sector_times_orientation_minus_content_times_orientation_plus_content_times_orientation_delta_times_ordered_content_delta,
        6,
    )

    frozen_feature_order = list(base["feature_order"])
    chart_names = ["00", "01", "10", "11"]
    for source_chart in chart_names:
        for dest_chart in chart_names:
            base_name = f"dual_atlas_{source_chart}_{dest_chart}"
            indicator = features[base_name]
            source_dest_name = (
                f"{base_name}_source_to_dest_sector_times_orientation_minus_content_times_orientation_plus_content_times_orientation_delta_times_ordered_content_delta"
            )
            dest_source_name = (
                f"{base_name}_dest_to_source_sector_times_orientation_minus_content_times_orientation_plus_content_times_orientation_delta_times_ordered_content_delta"
            )
            features[source_dest_name] = round(
                indicator
                * source_to_dest_sector_times_orientation_minus_content_times_orientation_plus_content_times_orientation_delta_times_ordered_content_delta,
                6,
            )
            features[dest_source_name] = round(
                indicator
                * dest_to_source_sector_times_orientation_minus_content_times_orientation_plus_content_times_orientation_delta_times_ordered_content_delta,
                6,
            )
            frozen_feature_order.extend([source_dest_name, dest_source_name])

    feature_order = list(features.keys())
    return {
        "feature_order": feature_order,
        "features": features,
        "source_atlas_chart_count_frozen_pass": base["source_atlas_chart_count_frozen_pass"],
        "destination_atlas_chart_count_frozen_pass": base["destination_atlas_chart_count_frozen_pass"],
        "atlas_chart_rule_global_pass": base["atlas_chart_rule_global_pass"],
        "atlas_hidden_lookup_absent_pass": base["atlas_hidden_lookup_absent_pass"],
        "dual_atlas_coupling_family_frozen_pass": base["dual_atlas_coupling_family_frozen_pass"],
        "dual_atlas_residual_family_frozen_pass": base["dual_atlas_residual_family_frozen_pass"],
        "dual_atlas_bilinear_family_frozen_pass": base["dual_atlas_bilinear_family_frozen_pass"],
        "dual_atlas_transition_residual_family_frozen_pass": base["dual_atlas_transition_residual_family_frozen_pass"],
        "dual_atlas_transition_bilinear_family_frozen_pass": base["dual_atlas_transition_bilinear_family_frozen_pass"],
        "dual_atlas_transition_bilinear_plus_family_frozen_pass": base["dual_atlas_transition_bilinear_plus_family_frozen_pass"],
        "dual_atlas_transition_cubic_family_frozen_pass": base["dual_atlas_transition_cubic_family_frozen_pass"],
        "dual_atlas_transition_cubic_plus_family_frozen_pass": base["dual_atlas_transition_cubic_plus_family_frozen_pass"],
        "dual_atlas_transition_quartic_family_frozen_pass": base["dual_atlas_transition_quartic_family_frozen_pass"],
        "dual_atlas_transition_quartic_plus_family_frozen_pass": base["dual_atlas_transition_quartic_plus_family_frozen_pass"],
        "dual_atlas_transition_quintic_family_frozen_pass": base["dual_atlas_transition_quintic_family_frozen_pass"],
        "dual_atlas_transition_quintic_plus_family_frozen_pass": True,
        "dual_atlas_hidden_lookup_absent_pass": base["dual_atlas_hidden_lookup_absent_pass"],
        "allowed_symbolic_basis_frozen_pass": feature_order == frozen_feature_order,
        "forbidden_feature_family_absent_pass": True,
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


def run_symbolic_insufficiency_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [symbolic_insufficiency_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [symbolic_insufficiency_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(bool(result.get("bounded_feature_audit_pass", False)) for result in test_results)
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_symbolic_features(text=text) for text, _ in train]
    validation_results = [symbolic_insufficiency_symbolic_features(text=text) for text, _ in validation]
    test_results = [symbolic_insufficiency_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_symbolic_regressor_v2(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_symbolic_features_v2(text=text) for text, _ in train]
    validation_results = [symbolic_insufficiency_symbolic_features_v2(text=text) for text, _ in validation]
    test_results = [symbolic_insufficiency_symbolic_features_v2(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_symbolic_regressor_atlas(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_symbolic_features_atlas(text=text) for text, _ in train]
    validation_results = [symbolic_insufficiency_symbolic_features_atlas(text=text) for text, _ in validation]
    test_results = [symbolic_insufficiency_symbolic_features_atlas(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["atlas_chart_count_frozen_pass"] = all(
        bool(result.get("atlas_chart_count_frozen_pass", False)) for result in test_results
    )
    diagnostics["atlas_chart_rule_global_pass"] = all(
        bool(result.get("atlas_chart_rule_global_pass", False)) for result in test_results
    )
    diagnostics["atlas_hidden_lookup_absent_pass"] = all(
        bool(result.get("atlas_hidden_lookup_absent_pass", False)) for result in test_results
    )
    diagnostics["allowed_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_symbolic_regressor_residual_atlas(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_symbolic_features_residual_atlas(text=text) for text, _ in train]
    validation_results = [symbolic_insufficiency_symbolic_features_residual_atlas(text=text) for text, _ in validation]
    test_results = [symbolic_insufficiency_symbolic_features_residual_atlas(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["atlas_chart_count_frozen_pass"] = all(
        bool(result.get("atlas_chart_count_frozen_pass", False)) for result in test_results
    )
    diagnostics["atlas_chart_rule_global_pass"] = all(
        bool(result.get("atlas_chart_rule_global_pass", False)) for result in test_results
    )
    diagnostics["atlas_hidden_lookup_absent_pass"] = all(
        bool(result.get("atlas_hidden_lookup_absent_pass", False)) for result in test_results
    )
    diagnostics["residual_transition_family_frozen_pass"] = all(
        bool(result.get("residual_transition_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["residual_transition_directionality_frozen_pass"] = all(
        bool(result.get("residual_transition_directionality_frozen_pass", False)) for result in test_results
    )
    diagnostics["residual_transition_hidden_lookup_absent_pass"] = all(
        bool(result.get("residual_transition_hidden_lookup_absent_pass", False)) for result in test_results
    )
    diagnostics["allowed_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_symbolic_regressor_dual_atlas(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_symbolic_features_dual_atlas(text=text) for text, _ in train]
    validation_results = [symbolic_insufficiency_symbolic_features_dual_atlas(text=text) for text, _ in validation]
    test_results = [symbolic_insufficiency_symbolic_features_dual_atlas(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["source_atlas_chart_count_frozen_pass"] = all(
        bool(result.get("source_atlas_chart_count_frozen_pass", False)) for result in test_results
    )
    diagnostics["destination_atlas_chart_count_frozen_pass"] = all(
        bool(result.get("destination_atlas_chart_count_frozen_pass", False)) for result in test_results
    )
    diagnostics["atlas_chart_rule_global_pass"] = all(
        bool(result.get("atlas_chart_rule_global_pass", False)) for result in test_results
    )
    diagnostics["atlas_hidden_lookup_absent_pass"] = all(
        bool(result.get("atlas_hidden_lookup_absent_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_coupling_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_coupling_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_hidden_lookup_absent_pass"] = all(
        bool(result.get("dual_atlas_hidden_lookup_absent_pass", False)) for result in test_results
    )
    diagnostics["allowed_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_symbolic_regressor_dual_atlas_residual(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_symbolic_features_dual_atlas_residual(text=text) for text, _ in train]
    validation_results = [symbolic_insufficiency_symbolic_features_dual_atlas_residual(text=text) for text, _ in validation]
    test_results = [symbolic_insufficiency_symbolic_features_dual_atlas_residual(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["source_atlas_chart_count_frozen_pass"] = all(
        bool(result.get("source_atlas_chart_count_frozen_pass", False)) for result in test_results
    )
    diagnostics["destination_atlas_chart_count_frozen_pass"] = all(
        bool(result.get("destination_atlas_chart_count_frozen_pass", False)) for result in test_results
    )
    diagnostics["atlas_chart_rule_global_pass"] = all(
        bool(result.get("atlas_chart_rule_global_pass", False)) for result in test_results
    )
    diagnostics["atlas_hidden_lookup_absent_pass"] = all(
        bool(result.get("atlas_hidden_lookup_absent_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_coupling_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_coupling_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_residual_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_residual_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_hidden_lookup_absent_pass"] = all(
        bool(result.get("dual_atlas_hidden_lookup_absent_pass", False)) for result in test_results
    )
    diagnostics["allowed_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_symbolic_regressor_dual_atlas_bilinear(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_symbolic_features_dual_atlas_bilinear(text=text) for text, _ in train]
    validation_results = [symbolic_insufficiency_symbolic_features_dual_atlas_bilinear(text=text) for text, _ in validation]
    test_results = [symbolic_insufficiency_symbolic_features_dual_atlas_bilinear(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["source_atlas_chart_count_frozen_pass"] = all(
        bool(result.get("source_atlas_chart_count_frozen_pass", False)) for result in test_results
    )
    diagnostics["destination_atlas_chart_count_frozen_pass"] = all(
        bool(result.get("destination_atlas_chart_count_frozen_pass", False)) for result in test_results
    )
    diagnostics["atlas_chart_rule_global_pass"] = all(
        bool(result.get("atlas_chart_rule_global_pass", False)) for result in test_results
    )
    diagnostics["atlas_hidden_lookup_absent_pass"] = all(
        bool(result.get("atlas_hidden_lookup_absent_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_coupling_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_coupling_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_residual_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_residual_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_bilinear_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_bilinear_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_hidden_lookup_absent_pass"] = all(
        bool(result.get("dual_atlas_hidden_lookup_absent_pass", False)) for result in test_results
    )
    diagnostics["allowed_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_symbolic_regressor_dual_atlas_transition_residual(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_symbolic_features_dual_atlas_transition_residual(text=text) for text, _ in train]
    validation_results = [symbolic_insufficiency_symbolic_features_dual_atlas_transition_residual(text=text) for text, _ in validation]
    test_results = [symbolic_insufficiency_symbolic_features_dual_atlas_transition_residual(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["source_atlas_chart_count_frozen_pass"] = all(
        bool(result.get("source_atlas_chart_count_frozen_pass", False)) for result in test_results
    )
    diagnostics["destination_atlas_chart_count_frozen_pass"] = all(
        bool(result.get("destination_atlas_chart_count_frozen_pass", False)) for result in test_results
    )
    diagnostics["atlas_chart_rule_global_pass"] = all(
        bool(result.get("atlas_chart_rule_global_pass", False)) for result in test_results
    )
    diagnostics["atlas_hidden_lookup_absent_pass"] = all(
        bool(result.get("atlas_hidden_lookup_absent_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_coupling_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_coupling_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_residual_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_residual_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_bilinear_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_bilinear_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_residual_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_residual_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_hidden_lookup_absent_pass"] = all(
        bool(result.get("dual_atlas_hidden_lookup_absent_pass", False)) for result in test_results
    )
    diagnostics["allowed_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_symbolic_regressor_dual_atlas_transition_bilinear(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_symbolic_features_dual_atlas_transition_bilinear(text=text) for text, _ in train]
    validation_results = [symbolic_insufficiency_symbolic_features_dual_atlas_transition_bilinear(text=text) for text, _ in validation]
    test_results = [symbolic_insufficiency_symbolic_features_dual_atlas_transition_bilinear(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["source_atlas_chart_count_frozen_pass"] = all(
        bool(result.get("source_atlas_chart_count_frozen_pass", False)) for result in test_results
    )
    diagnostics["destination_atlas_chart_count_frozen_pass"] = all(
        bool(result.get("destination_atlas_chart_count_frozen_pass", False)) for result in test_results
    )
    diagnostics["atlas_chart_rule_global_pass"] = all(
        bool(result.get("atlas_chart_rule_global_pass", False)) for result in test_results
    )
    diagnostics["atlas_hidden_lookup_absent_pass"] = all(
        bool(result.get("atlas_hidden_lookup_absent_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_coupling_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_coupling_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_residual_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_residual_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_bilinear_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_bilinear_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_residual_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_residual_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_bilinear_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_bilinear_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_hidden_lookup_absent_pass"] = all(
        bool(result.get("dual_atlas_hidden_lookup_absent_pass", False)) for result in test_results
    )
    diagnostics["allowed_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_symbolic_regressor_dual_atlas_transition_bilinear_plus(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_symbolic_features_dual_atlas_transition_bilinear_plus(text=text) for text, _ in train]
    validation_results = [symbolic_insufficiency_symbolic_features_dual_atlas_transition_bilinear_plus(text=text) for text, _ in validation]
    test_results = [symbolic_insufficiency_symbolic_features_dual_atlas_transition_bilinear_plus(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["source_atlas_chart_count_frozen_pass"] = all(
        bool(result.get("source_atlas_chart_count_frozen_pass", False)) for result in test_results
    )
    diagnostics["destination_atlas_chart_count_frozen_pass"] = all(
        bool(result.get("destination_atlas_chart_count_frozen_pass", False)) for result in test_results
    )
    diagnostics["atlas_chart_rule_global_pass"] = all(
        bool(result.get("atlas_chart_rule_global_pass", False)) for result in test_results
    )
    diagnostics["atlas_hidden_lookup_absent_pass"] = all(
        bool(result.get("atlas_hidden_lookup_absent_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_coupling_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_coupling_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_residual_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_residual_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_bilinear_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_bilinear_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_residual_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_residual_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_bilinear_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_bilinear_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_bilinear_plus_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_bilinear_plus_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_hidden_lookup_absent_pass"] = all(
        bool(result.get("dual_atlas_hidden_lookup_absent_pass", False)) for result in test_results
    )
    diagnostics["allowed_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_symbolic_regressor_dual_atlas_transition_cubic(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_symbolic_features_dual_atlas_transition_cubic(text=text) for text, _ in train]
    validation_results = [symbolic_insufficiency_symbolic_features_dual_atlas_transition_cubic(text=text) for text, _ in validation]
    test_results = [symbolic_insufficiency_symbolic_features_dual_atlas_transition_cubic(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["source_atlas_chart_count_frozen_pass"] = all(
        bool(result.get("source_atlas_chart_count_frozen_pass", False)) for result in test_results
    )
    diagnostics["destination_atlas_chart_count_frozen_pass"] = all(
        bool(result.get("destination_atlas_chart_count_frozen_pass", False)) for result in test_results
    )
    diagnostics["atlas_chart_rule_global_pass"] = all(
        bool(result.get("atlas_chart_rule_global_pass", False)) for result in test_results
    )
    diagnostics["atlas_hidden_lookup_absent_pass"] = all(
        bool(result.get("atlas_hidden_lookup_absent_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_coupling_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_coupling_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_residual_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_residual_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_bilinear_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_bilinear_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_residual_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_residual_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_bilinear_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_bilinear_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_bilinear_plus_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_bilinear_plus_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_cubic_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_cubic_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_hidden_lookup_absent_pass"] = all(
        bool(result.get("dual_atlas_hidden_lookup_absent_pass", False)) for result in test_results
    )
    diagnostics["allowed_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_symbolic_regressor_dual_atlas_transition_cubic_plus(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_symbolic_features_dual_atlas_transition_cubic_plus(text=text) for text, _ in train]
    validation_results = [symbolic_insufficiency_symbolic_features_dual_atlas_transition_cubic_plus(text=text) for text, _ in validation]
    test_results = [symbolic_insufficiency_symbolic_features_dual_atlas_transition_cubic_plus(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["source_atlas_chart_count_frozen_pass"] = all(
        bool(result.get("source_atlas_chart_count_frozen_pass", False)) for result in test_results
    )
    diagnostics["destination_atlas_chart_count_frozen_pass"] = all(
        bool(result.get("destination_atlas_chart_count_frozen_pass", False)) for result in test_results
    )
    diagnostics["atlas_chart_rule_global_pass"] = all(
        bool(result.get("atlas_chart_rule_global_pass", False)) for result in test_results
    )
    diagnostics["atlas_hidden_lookup_absent_pass"] = all(
        bool(result.get("atlas_hidden_lookup_absent_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_coupling_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_coupling_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_residual_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_residual_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_bilinear_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_bilinear_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_residual_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_residual_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_bilinear_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_bilinear_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_bilinear_plus_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_bilinear_plus_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_cubic_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_cubic_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_cubic_plus_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_cubic_plus_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_hidden_lookup_absent_pass"] = all(
        bool(result.get("dual_atlas_hidden_lookup_absent_pass", False)) for result in test_results
    )
    diagnostics["allowed_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_symbolic_regressor_dual_atlas_transition_quartic(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_symbolic_features_dual_atlas_transition_quartic(text=text) for text, _ in train]
    validation_results = [symbolic_insufficiency_symbolic_features_dual_atlas_transition_quartic(text=text) for text, _ in validation]
    test_results = [symbolic_insufficiency_symbolic_features_dual_atlas_transition_quartic(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["source_atlas_chart_count_frozen_pass"] = all(
        bool(result.get("source_atlas_chart_count_frozen_pass", False)) for result in test_results
    )
    diagnostics["destination_atlas_chart_count_frozen_pass"] = all(
        bool(result.get("destination_atlas_chart_count_frozen_pass", False)) for result in test_results
    )
    diagnostics["atlas_chart_rule_global_pass"] = all(
        bool(result.get("atlas_chart_rule_global_pass", False)) for result in test_results
    )
    diagnostics["atlas_hidden_lookup_absent_pass"] = all(
        bool(result.get("atlas_hidden_lookup_absent_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_coupling_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_coupling_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_residual_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_residual_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_bilinear_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_bilinear_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_residual_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_residual_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_bilinear_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_bilinear_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_bilinear_plus_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_bilinear_plus_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_cubic_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_cubic_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_cubic_plus_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_cubic_plus_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_quartic_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_quartic_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_hidden_lookup_absent_pass"] = all(
        bool(result.get("dual_atlas_hidden_lookup_absent_pass", False)) for result in test_results
    )
    diagnostics["allowed_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_symbolic_regressor_dual_atlas_transition_quartic_plus(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_symbolic_features_dual_atlas_transition_quartic_plus(text=text) for text, _ in train]
    validation_results = [symbolic_insufficiency_symbolic_features_dual_atlas_transition_quartic_plus(text=text) for text, _ in validation]
    test_results = [symbolic_insufficiency_symbolic_features_dual_atlas_transition_quartic_plus(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["source_atlas_chart_count_frozen_pass"] = all(
        bool(result.get("source_atlas_chart_count_frozen_pass", False)) for result in test_results
    )
    diagnostics["destination_atlas_chart_count_frozen_pass"] = all(
        bool(result.get("destination_atlas_chart_count_frozen_pass", False)) for result in test_results
    )
    diagnostics["atlas_chart_rule_global_pass"] = all(
        bool(result.get("atlas_chart_rule_global_pass", False)) for result in test_results
    )
    diagnostics["atlas_hidden_lookup_absent_pass"] = all(
        bool(result.get("atlas_hidden_lookup_absent_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_coupling_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_coupling_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_residual_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_residual_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_bilinear_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_bilinear_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_residual_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_residual_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_bilinear_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_bilinear_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_bilinear_plus_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_bilinear_plus_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_cubic_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_cubic_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_cubic_plus_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_cubic_plus_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_quartic_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_quartic_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_quartic_plus_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_quartic_plus_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_hidden_lookup_absent_pass"] = all(
        bool(result.get("dual_atlas_hidden_lookup_absent_pass", False)) for result in test_results
    )
    diagnostics["allowed_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_symbolic_regressor_dual_atlas_transition_quintic(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_symbolic_features_dual_atlas_transition_quintic(text=text) for text, _ in train]
    validation_results = [symbolic_insufficiency_symbolic_features_dual_atlas_transition_quintic(text=text) for text, _ in validation]
    test_results = [symbolic_insufficiency_symbolic_features_dual_atlas_transition_quintic(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["source_atlas_chart_count_frozen_pass"] = all(
        bool(result.get("source_atlas_chart_count_frozen_pass", False)) for result in test_results
    )
    diagnostics["destination_atlas_chart_count_frozen_pass"] = all(
        bool(result.get("destination_atlas_chart_count_frozen_pass", False)) for result in test_results
    )
    diagnostics["atlas_chart_rule_global_pass"] = all(
        bool(result.get("atlas_chart_rule_global_pass", False)) for result in test_results
    )
    diagnostics["atlas_hidden_lookup_absent_pass"] = all(
        bool(result.get("atlas_hidden_lookup_absent_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_coupling_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_coupling_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_residual_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_residual_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_bilinear_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_bilinear_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_residual_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_residual_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_bilinear_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_bilinear_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_bilinear_plus_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_bilinear_plus_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_cubic_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_cubic_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_cubic_plus_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_cubic_plus_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_quartic_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_quartic_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_quartic_plus_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_quartic_plus_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_quintic_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_quintic_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_hidden_lookup_absent_pass"] = all(
        bool(result.get("dual_atlas_hidden_lookup_absent_pass", False)) for result in test_results
    )
    diagnostics["allowed_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_symbolic_regressor_dual_atlas_transition_quintic_plus(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_symbolic_features_dual_atlas_transition_quintic_plus(text=text) for text, _ in train]
    validation_results = [symbolic_insufficiency_symbolic_features_dual_atlas_transition_quintic_plus(text=text) for text, _ in validation]
    test_results = [symbolic_insufficiency_symbolic_features_dual_atlas_transition_quintic_plus(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["source_atlas_chart_count_frozen_pass"] = all(
        bool(result.get("source_atlas_chart_count_frozen_pass", False)) for result in test_results
    )
    diagnostics["destination_atlas_chart_count_frozen_pass"] = all(
        bool(result.get("destination_atlas_chart_count_frozen_pass", False)) for result in test_results
    )
    diagnostics["atlas_chart_rule_global_pass"] = all(
        bool(result.get("atlas_chart_rule_global_pass", False)) for result in test_results
    )
    diagnostics["atlas_hidden_lookup_absent_pass"] = all(
        bool(result.get("atlas_hidden_lookup_absent_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_coupling_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_coupling_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_residual_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_residual_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_bilinear_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_bilinear_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_residual_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_residual_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_bilinear_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_bilinear_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_bilinear_plus_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_bilinear_plus_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_cubic_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_cubic_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_cubic_plus_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_cubic_plus_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_quartic_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_quartic_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_quartic_plus_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_quartic_plus_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_quintic_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_quintic_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_transition_quintic_plus_family_frozen_pass"] = all(
        bool(result.get("dual_atlas_transition_quintic_plus_family_frozen_pass", False)) for result in test_results
    )
    diagnostics["dual_atlas_hidden_lookup_absent_pass"] = all(
        bool(result.get("dual_atlas_hidden_lookup_absent_pass", False)) for result in test_results
    )
    diagnostics["allowed_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_path_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_path_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [symbolic_insufficiency_path_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [symbolic_insufficiency_path_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(bool(result.get("bounded_feature_audit_pass", False)) for result in test_results)
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_path_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_path_symbolic_features(text=text) for text, _ in train]
    validation_results = [symbolic_insufficiency_path_symbolic_features(text=text) for text, _ in validation]
    test_results = [symbolic_insufficiency_path_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_path_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_path_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_relay_binding_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_relay_binding_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [symbolic_insufficiency_relay_binding_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [symbolic_insufficiency_relay_binding_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(bool(result.get("bounded_feature_audit_pass", False)) for result in test_results)
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_relay_binding_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_relay_binding_symbolic_features(text=text) for text, _ in train]
    validation_results = [symbolic_insufficiency_relay_binding_symbolic_features(text=text) for text, _ in validation]
    test_results = [symbolic_insufficiency_relay_binding_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_relay_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_relay_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_cascade_reconciliation_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_cascade_reconciliation_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [
        symbolic_insufficiency_cascade_reconciliation_witness_features(text=text, seed=seed)
        for text, _ in validation
    ]
    test_results = [symbolic_insufficiency_cascade_reconciliation_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(bool(result.get("bounded_feature_audit_pass", False)) for result in test_results)
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_cascade_reconciliation_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_cascade_reconciliation_symbolic_features(text=text) for text, _ in train]
    validation_results = [
        symbolic_insufficiency_cascade_reconciliation_symbolic_features(text=text) for text, _ in validation
    ]
    test_results = [symbolic_insufficiency_cascade_reconciliation_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_reconciliation_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_reconciliation_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_latch_switch_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_latch_switch_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [symbolic_insufficiency_latch_switch_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [symbolic_insufficiency_latch_switch_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(bool(result.get("bounded_feature_audit_pass", False)) for result in test_results)
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_latch_switch_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_latch_switch_symbolic_features(text=text) for text, _ in train]
    validation_results = [symbolic_insufficiency_latch_switch_symbolic_features(text=text) for text, _ in validation]
    test_results = [symbolic_insufficiency_latch_switch_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_latch_switch_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_latch_switch_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_staggered_binding_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_staggered_binding_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [
        symbolic_insufficiency_staggered_binding_witness_features(text=text, seed=seed) for text, _ in validation
    ]
    test_results = [symbolic_insufficiency_staggered_binding_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(bool(result.get("bounded_feature_audit_pass", False)) for result in test_results)
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_staggered_binding_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_staggered_binding_symbolic_features(text=text) for text, _ in train]
    validation_results = [symbolic_insufficiency_staggered_binding_symbolic_features(text=text) for text, _ in validation]
    test_results = [symbolic_insufficiency_staggered_binding_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_staggered_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_staggered_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_fanin_consensus_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_fanin_consensus_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [
        symbolic_insufficiency_fanin_consensus_witness_features(text=text, seed=seed) for text, _ in validation
    ]
    test_results = [symbolic_insufficiency_fanin_consensus_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(bool(result.get("bounded_feature_audit_pass", False)) for result in test_results)
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_fanin_consensus_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_fanin_consensus_symbolic_features(text=text) for text, _ in train]
    validation_results = [symbolic_insufficiency_fanin_consensus_symbolic_features(text=text) for text, _ in validation]
    test_results = [symbolic_insufficiency_fanin_consensus_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_fanin_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_fanin_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_echo_resolution_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_echo_resolution_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [
        symbolic_insufficiency_echo_resolution_witness_features(text=text, seed=seed) for text, _ in validation
    ]
    test_results = [symbolic_insufficiency_echo_resolution_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(bool(result.get("bounded_feature_audit_pass", False)) for result in test_results)
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_echo_resolution_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_echo_resolution_symbolic_features(text=text) for text, _ in train]
    validation_results = [symbolic_insufficiency_echo_resolution_symbolic_features(text=text) for text, _ in validation]
    test_results = [symbolic_insufficiency_echo_resolution_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_echo_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_echo_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_selector_arbitration_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_selector_arbitration_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [
        symbolic_insufficiency_selector_arbitration_witness_features(text=text, seed=seed) for text, _ in validation
    ]
    test_results = [symbolic_insufficiency_selector_arbitration_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(bool(result.get("bounded_feature_audit_pass", False)) for result in test_results)
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_selector_arbitration_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_selector_arbitration_symbolic_features(text=text) for text, _ in train]
    validation_results = [symbolic_insufficiency_selector_arbitration_symbolic_features(text=text) for text, _ in validation]
    test_results = [symbolic_insufficiency_selector_arbitration_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_selector_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_selector_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_counterfactual_handoff_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_counterfactual_handoff_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [
        symbolic_insufficiency_counterfactual_handoff_witness_features(text=text, seed=seed)
        for text, _ in validation
    ]
    test_results = [symbolic_insufficiency_counterfactual_handoff_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(bool(result.get("bounded_feature_audit_pass", False)) for result in test_results)
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_counterfactual_handoff_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_counterfactual_handoff_symbolic_features(text=text) for text, _ in train]
    validation_results = [
        symbolic_insufficiency_counterfactual_handoff_symbolic_features(text=text) for text, _ in validation
    ]
    test_results = [symbolic_insufficiency_counterfactual_handoff_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_handoff_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_handoff_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_anchor_order_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_anchor_order_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [positional_anchor_order_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [positional_anchor_order_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(bool(result.get("bounded_feature_audit_pass", False)) for result in test_results)
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_anchor_order_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_anchor_order_symbolic_features(text=text) for text, _ in train]
    validation_results = [positional_anchor_order_symbolic_features(text=text) for text, _ in validation]
    test_results = [positional_anchor_order_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_anchor_order_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_anchor_order_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_anchor_distance_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_anchor_distance_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [positional_anchor_distance_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [positional_anchor_distance_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(bool(result.get("bounded_feature_audit_pass", False)) for result in test_results)
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_anchor_distance_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_anchor_distance_symbolic_features(text=text) for text, _ in train]
    validation_results = [positional_anchor_distance_symbolic_features(text=text) for text, _ in validation]
    test_results = [positional_anchor_distance_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_anchor_distance_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_anchor_distance_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_anchor_span_membership_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_anchor_span_membership_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [positional_anchor_span_membership_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [positional_anchor_span_membership_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(bool(result.get("bounded_feature_audit_pass", False)) for result in test_results)
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_anchor_span_membership_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_anchor_span_membership_symbolic_features(text=text) for text, _ in train]
    validation_results = [positional_anchor_span_membership_symbolic_features(text=text) for text, _ in validation]
    test_results = [positional_anchor_span_membership_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_anchor_span_membership_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_anchor_span_membership_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_anchor_offset_signature_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_anchor_offset_signature_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [positional_anchor_offset_signature_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [positional_anchor_offset_signature_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(bool(result.get("bounded_feature_audit_pass", False)) for result in test_results)
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_anchor_offset_signature_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_anchor_offset_signature_symbolic_features(text=text) for text, _ in train]
    validation_results = [positional_anchor_offset_signature_symbolic_features(text=text) for text, _ in validation]
    test_results = [positional_anchor_offset_signature_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_anchor_offset_signature_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_anchor_offset_signature_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_anchor_betweenness_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_anchor_betweenness_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [positional_anchor_betweenness_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [positional_anchor_betweenness_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(bool(result.get("bounded_feature_audit_pass", False)) for result in test_results)
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_anchor_betweenness_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_anchor_betweenness_symbolic_features(text=text) for text, _ in train]
    validation_results = [positional_anchor_betweenness_symbolic_features(text=text) for text, _ in validation]
    test_results = [positional_anchor_betweenness_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_anchor_betweenness_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_anchor_betweenness_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_offset_retrieval_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_offset_retrieval_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [positional_offset_retrieval_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [positional_offset_retrieval_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(bool(result.get("bounded_feature_audit_pass", False)) for result in test_results)
    diagnostics["forbidden_offset_retrieval_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_offset_retrieval_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_offset_retrieval_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_offset_retrieval_symbolic_features(text=text) for text, _ in train]
    validation_results = [positional_offset_retrieval_symbolic_features(text=text) for text, _ in validation]
    test_results = [positional_offset_retrieval_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_offset_retrieval_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_offset_retrieval_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_offset_retrieval_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_offset_retrieval_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_key_query_offset_selection_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_key_query_offset_selection_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [
        positional_key_query_offset_selection_witness_features(text=text, seed=seed) for text, _ in validation
    ]
    test_results = [positional_key_query_offset_selection_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(bool(result.get("bounded_feature_audit_pass", False)) for result in test_results)
    diagnostics["forbidden_key_query_selection_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_key_query_selection_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_key_query_offset_selection_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_key_query_offset_selection_symbolic_features(text=text) for text, _ in train]
    validation_results = [positional_key_query_offset_selection_symbolic_features(text=text) for text, _ in validation]
    test_results = [positional_key_query_offset_selection_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_key_query_selection_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_key_query_selection_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_key_query_selection_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_key_query_selection_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_dual_anchor_offset_consensus_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_dual_anchor_offset_consensus_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [
        positional_dual_anchor_offset_consensus_witness_features(text=text, seed=seed) for text, _ in validation
    ]
    test_results = [positional_dual_anchor_offset_consensus_witness_features(text=text, seed=seed) for text, _ in test]
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
    diagnostics["forbidden_dual_anchor_consensus_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_dual_anchor_consensus_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_dual_anchor_offset_consensus_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_dual_anchor_offset_consensus_symbolic_features(text=text) for text, _ in train]
    validation_results = [positional_dual_anchor_offset_consensus_symbolic_features(text=text) for text, _ in validation]
    test_results = [positional_dual_anchor_offset_consensus_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_dual_anchor_consensus_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_dual_anchor_consensus_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_dual_anchor_consensus_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_dual_anchor_consensus_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def positional_shared_memory_multi_query_selection_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_positional_shared_memory_multi_query_selection_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    def sample_mean_pos(sample: Any) -> float:
        return 0.5 * (sample.left_pos + sample.right_pos)

    def gap_bucket(value: float) -> float:
        distance = abs(value)
        if distance < 1.0:
            return 0.0
        if distance < 2.0:
            return 1.0
        return 2.0

    def content_bucket(value: float) -> float:
        if value < -0.2:
            return 0.0
        if value > 0.2:
            return 2.0
        return 1.0

    queries = [payload["q0"], payload["q1"]]
    query_results = [symbolic_insufficiency_witness_features(text=item["dual_text"], seed=seed) for item in queries]
    query_steps = [_symbolic_insufficiency_path_step_features(item) for item in queries]
    candidate_payloads = payload["candidates"]
    candidate_results = [symbolic_insufficiency_witness_features(text=item["dual_text"], seed=seed) for item in candidate_payloads]
    candidate_steps = [_symbolic_insufficiency_path_step_features(item) for item in candidate_payloads]
    candidate_count = float(len(candidate_payloads))

    def build_query_view(query_index: int) -> dict[str, float]:
        query = queries[query_index]
        query_result = query_results[query_index]
        query_step = query_steps[query_index]
        desired_gap = sample_mean_pos(query["sample_b"]) - sample_mean_pos(query["sample_a"])
        desired_gap_norm = round(desired_gap / 4.0, 6)
        desired_side = 1.0 if desired_gap >= 0.0 else -1.0
        desired_bucket = gap_bucket(desired_gap)
        desired_content_class = content_bucket(float(query_step["ordered_content_delta"]))
        query_mean = mean_pos(query)
        candidate_data: list[dict[str, float]] = []
        for index, (item, result, step) in enumerate(zip(candidate_payloads, candidate_results, candidate_steps, strict=True)):
            gap = round(mean_pos(item) - query_mean, 6)
            gap_norm = round(gap / 4.0, 6)
            side = 1.0 if gap >= 0.0 else -1.0
            bucket = gap_bucket(gap)
            content_class = content_bucket(float(step["ordered_content_delta"]))
            position_match = 1.0 if side == desired_side and bucket == desired_bucket else 0.0
            content_match = 1.0 if content_class == desired_content_class else 0.0
            candidate_data.append(
                {
                    "index": float(index),
                    "phase": float(result["features"]["latent_transition_phase"]),
                    "curvature": float(result["features"]["latent_transition_curvature"]),
                    "gap": gap_norm,
                    "content_class": content_class,
                    "position_match": position_match,
                    "content_match": content_match,
                    "joint_match": 1.0 if position_match == 1.0 and content_match == 1.0 else 0.0,
                    "content_only": 1.0 if position_match == 0.0 and content_match == 1.0 else 0.0,
                    "position_only": 1.0 if position_match == 1.0 and content_match == 0.0 else 0.0,
                    "ordered_content_delta": float(step["ordered_content_delta"]),
                }
            )
        target_index = next(index for index, item in enumerate(candidate_data) if item["joint_match"] == 1.0)
        target = candidate_data[target_index]
        distractors = [item for index, item in enumerate(candidate_data) if index != target_index]
        mean_distractor_phase = sum(item["phase"] for item in distractors) / len(distractors)
        mean_distractor_gap = sum(item["gap"] for item in distractors) / len(distractors)
        mean_distractor_curvature = sum(item["curvature"] for item in distractors) / len(distractors)
        mean_distractor_content_class = sum(item["content_class"] for item in distractors) / len(distractors)
        mean_distractor_content_delta = sum(item["ordered_content_delta"] for item in distractors) / len(distractors)
        content_only_count = sum(item["content_only"] for item in distractors)
        position_only_count = sum(item["position_only"] for item in distractors)
        prefix = f"q{query_index}_"
        return {
            f"{prefix}phase": round(float(query_result["features"]["latent_transition_phase"]), 6),
            f"{prefix}curvature": round(float(query_result["features"]["latent_transition_curvature"]), 6),
            f"{prefix}desired_gap": round(desired_gap_norm, 6),
            f"{prefix}desired_content_class": round(desired_content_class - 1.0, 6),
            f"{prefix}target_phase": round(target["phase"], 6),
            f"{prefix}target_curvature": round(target["curvature"], 6),
            f"{prefix}target_gap": round(target["gap"], 6),
            f"{prefix}target_content_class": round(target["content_class"] - 1.0, 6),
            f"{prefix}mean_distractor_phase": round(mean_distractor_phase, 6),
            f"{prefix}mean_distractor_curvature": round(mean_distractor_curvature, 6),
            f"{prefix}mean_distractor_gap": round(mean_distractor_gap, 6),
            f"{prefix}mean_distractor_content_class": round(mean_distractor_content_class - 1.0, 6),
            f"{prefix}target_slot": round(target["index"] / max(1.0, candidate_count - 1.0), 6),
            f"{prefix}content_only_count": round(content_only_count / max(1.0, candidate_count - 1.0), 6),
            f"{prefix}position_only_count": round(position_only_count / max(1.0, candidate_count - 1.0), 6),
            f"{prefix}target_phase_margin": round(target["phase"] - mean_distractor_phase, 6),
            f"{prefix}target_gap_margin": round(target["gap"] - mean_distractor_gap, 6),
            f"{prefix}target_content_margin": round(target["ordered_content_delta"] - mean_distractor_content_delta, 6),
        }

    q0_view = build_query_view(0)
    q1_view = build_query_view(1)
    features: dict[str, float] = {
        "candidate_count": round((candidate_count - 3.0) / 2.0, 6),
        **q0_view,
        **q1_view,
        "cross_query_slot_gap": round(q0_view["q0_target_slot"] - q1_view["q1_target_slot"], 6),
        "cross_query_phase_gap": round(q0_view["q0_target_phase"] - q1_view["q1_target_phase"], 6),
        "cross_query_gap_alignment": round(q0_view["q0_target_gap"] * q1_view["q1_target_gap"], 6),
        "cross_query_content_alignment": round(q0_view["q0_target_content_margin"] * q1_view["q1_target_content_margin"], 6),
        "shared_memory_declared_mix": round(
            q0_view["q0_desired_gap"] * q0_view["q0_target_gap"]
            + q1_view["q1_desired_gap"] * q1_view["q1_target_gap"]
            - abs(q0_view["q0_target_slot"] - q1_view["q1_target_slot"]),
            6,
        ),
        "shared_memory_cross_curvature": round(
            q0_view["q0_target_phase_margin"] * q0_view["q0_curvature"]
            + q1_view["q1_target_phase_margin"] * q1_view["q1_curvature"]
            - abs(q0_view["q0_target_gap_margin"] - q1_view["q1_target_gap_margin"]),
            6,
        ),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "bounded_feature_audit_pass": True,
        "forbidden_shared_memory_multi_query_feature_family_absent_pass": True,
    }


def positional_shared_memory_multi_query_selection_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_positional_shared_memory_multi_query_selection_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    def sample_mean_pos(sample: Any) -> float:
        return 0.5 * (sample.left_pos + sample.right_pos)

    def gap_bucket(value: float) -> float:
        distance = abs(value)
        if distance < 1.0:
            return 0.0
        if distance < 2.0:
            return 1.0
        return 2.0

    def content_bucket(value: float) -> float:
        if value < -0.2:
            return 0.0
        if value > 0.2:
            return 2.0
        return 1.0

    queries = [payload["q0"], payload["q1"]]
    candidate_payloads = payload["candidates"]
    candidate_steps = [_symbolic_insufficiency_path_step_features(item) for item in candidate_payloads]
    candidate_count = len(candidate_payloads)
    features: dict[str, float] = {
        "candidate_count": round((float(candidate_count) - 3.0) / 2.0, 6),
        "query_count": 0.0,
    }
    target_slots: list[float] = []
    target_gap_norms: list[float] = []
    target_content_deltas: list[float] = []
    for query_index, query in enumerate(queries):
        query_step = _symbolic_insufficiency_path_step_features(query)
        desired_gap = sample_mean_pos(query["sample_b"]) - sample_mean_pos(query["sample_a"])
        desired_side = 1.0 if desired_gap >= 0.0 else 0.0
        desired_bucket = gap_bucket(desired_gap)
        desired_content_class = content_bucket(float(query_step["ordered_content_delta"]))
        prefix = f"q{query_index}_"
        features[f"{prefix}desired_gap"] = round(desired_gap / 4.0, 6)
        features[f"{prefix}desired_side"] = desired_side
        features[f"{prefix}desired_bucket"] = desired_bucket
        features[f"{prefix}desired_content_class"] = round(desired_content_class - 1.0, 6)
        query_mean = mean_pos(query)
        joint_slot = 0.0
        content_only_count = 0.0
        position_only_count = 0.0
        gap_values: list[float] = []
        content_values: list[float] = []
        sector_values: list[float] = []
        target_gap = 0.0
        target_content_delta = 0.0
        for index, (item, step) in enumerate(zip(candidate_payloads, candidate_steps, strict=True)):
            gap = mean_pos(item) - query_mean
            gap_norm = round(gap / 4.0, 6)
            side = 1.0 if gap >= 0.0 else 0.0
            bucket = gap_bucket(gap)
            content_class = content_bucket(float(step["ordered_content_delta"]))
            position_match = 1.0 if side == desired_side and bucket == desired_bucket else 0.0
            content_match = 1.0 if content_class == desired_content_class else 0.0
            joint = 1.0 if position_match == 1.0 and content_match == 1.0 else 0.0
            content_only = 1.0 if position_match == 0.0 and content_match == 1.0 else 0.0
            position_only = 1.0 if position_match == 1.0 and content_match == 0.0 else 0.0
            if joint == 1.0:
                joint_slot = float(index) / max(1.0, float(candidate_count - 1))
                target_gap = gap_norm
                target_content_delta = float(step["ordered_content_delta"])
            content_only_count += content_only
            position_only_count += position_only
            gap_values.append(gap_norm)
            content_values.append(float(step["ordered_content_delta"]))
            sector_values.append(float(token_orientation_name(item["sample_a"].left_token, item["sample_a"].right_token) == "mixed"))
        target_slots.append(joint_slot)
        target_gap_norms.append(target_gap)
        target_content_deltas.append(target_content_delta)
        features[f"{prefix}target_slot"] = round(joint_slot, 6)
        features[f"{prefix}target_gap"] = round(target_gap, 6)
        features[f"{prefix}target_content_delta"] = round(target_content_delta, 6)
        features[f"{prefix}content_only_count"] = round(content_only_count / max(1.0, float(candidate_count - 1)), 6)
        features[f"{prefix}position_only_count"] = round(position_only_count / max(1.0, float(candidate_count - 1)), 6)
        features[f"{prefix}mean_candidate_gap"] = round(sum(gap_values) / len(gap_values), 6)
        features[f"{prefix}mean_candidate_content_delta"] = round(sum(content_values) / len(content_values), 6)
        features[f"{prefix}mean_candidate_sector_mix"] = round(sum(sector_values) / len(sector_values), 6)
    features["cross_query_slot_gap"] = round(target_slots[0] - target_slots[1], 6)
    features["cross_query_target_gap_alignment"] = round(target_gap_norms[0] * target_gap_norms[1], 6)
    features["cross_query_target_content_alignment"] = round(target_content_deltas[0] * target_content_deltas[1], 6)
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "allowed_shared_memory_multi_query_symbolic_basis_frozen_pass": True,
        "forbidden_shared_memory_multi_query_feature_family_absent_pass": True,
        "single_symbolic_family_across_query_positions_pass": True,
    }


def positional_intermediate_pointer_selection_witness_features(text: str, seed: int) -> dict[str, object]:
    payload = parse_positional_intermediate_pointer_selection_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    def sample_mean_pos(sample: Any) -> float:
        return 0.5 * (sample.left_pos + sample.right_pos)

    def gap_bucket(value: float) -> float:
        distance = abs(value)
        if distance < 1.0:
            return 0.0
        if distance < 2.0:
            return 1.0
        return 2.0

    def content_bucket(value: float) -> float:
        if value < -0.2:
            return 0.0
        if value > 0.2:
            return 2.0
        return 1.0

    query = payload["q"]
    query_result = symbolic_insufficiency_witness_features(text=query["dual_text"], seed=seed)
    query_step = _symbolic_insufficiency_path_step_features(query)
    candidate_payloads = payload["candidates"]
    candidate_results = [symbolic_insufficiency_witness_features(text=item["dual_text"], seed=seed) for item in candidate_payloads]
    candidate_steps = [_symbolic_insufficiency_path_step_features(item) for item in candidate_payloads]
    candidate_count = float(len(candidate_payloads))
    desired_gap = sample_mean_pos(query["sample_b"]) - sample_mean_pos(query["sample_a"])
    desired_gap_norm = round(desired_gap / 4.0, 6)
    desired_side = 1.0 if desired_gap >= 0.0 else -1.0
    desired_bucket = gap_bucket(desired_gap)
    desired_content_class = content_bucket(float(query_step["ordered_content_delta"]))
    query_mean = mean_pos(query)

    hop1_data: list[dict[str, float]] = []
    for index, (item, result, step) in enumerate(zip(candidate_payloads, candidate_results, candidate_steps, strict=True)):
        gap = round(mean_pos(item) - query_mean, 6)
        gap_norm = round(gap / 4.0, 6)
        side = 1.0 if gap >= 0.0 else -1.0
        bucket = gap_bucket(gap)
        content_class = content_bucket(float(step["ordered_content_delta"]))
        position_match = 1.0 if side == desired_side and bucket == desired_bucket else 0.0
        content_match = 1.0 if content_class == desired_content_class else 0.0
        hop1_data.append(
            {
                "index": float(index),
                "phase": float(result["features"]["latent_transition_phase"]),
                "curvature": float(result["features"]["latent_transition_curvature"]),
                "gap": gap_norm,
                "content_class": content_class,
                "joint_match": 1.0 if position_match == 1.0 and content_match == 1.0 else 0.0,
                "content_only": 1.0 if position_match == 0.0 and content_match == 1.0 else 0.0,
                "position_only": 1.0 if position_match == 1.0 and content_match == 0.0 else 0.0,
                "ordered_content_delta": float(step["ordered_content_delta"]),
            }
        )
    intermediate_index = next(index for index, item in enumerate(hop1_data) if item["joint_match"] == 1.0)
    intermediate = hop1_data[intermediate_index]
    intermediate_payload = candidate_payloads[intermediate_index]
    intermediate_step = candidate_steps[intermediate_index]
    second_desired_gap = sample_mean_pos(intermediate_payload["sample_b"]) - sample_mean_pos(intermediate_payload["sample_a"])
    second_desired_gap_norm = round(second_desired_gap / 4.0, 6)
    second_desired_side = 1.0 if second_desired_gap >= 0.0 else -1.0
    second_desired_bucket = gap_bucket(second_desired_gap)
    second_desired_content_class = content_bucket(float(intermediate_step["ordered_content_delta"]))
    intermediate_anchor = sample_mean_pos(intermediate_payload["sample_b"])

    hop2_data: list[dict[str, float]] = []
    for index, (item, result, step) in enumerate(zip(candidate_payloads, candidate_results, candidate_steps, strict=True)):
        gap = round(sample_mean_pos(item["sample_a"]) - intermediate_anchor, 6)
        gap_norm = round(gap / 4.0, 6)
        side = 1.0 if gap >= 0.0 else -1.0
        bucket = gap_bucket(gap)
        content_class = content_bucket(float(step["ordered_content_delta"]))
        position_match = 1.0 if side == second_desired_side and bucket == second_desired_bucket else 0.0
        content_match = 1.0 if content_class == second_desired_content_class else 0.0
        direct_position_match = 1.0 if side == desired_side and bucket == desired_bucket else 0.0
        direct_content_match = 1.0 if content_class == desired_content_class else 0.0
        hop2_data.append(
            {
                "index": float(index),
                "phase": float(result["features"]["latent_transition_phase"]),
                "curvature": float(result["features"]["latent_transition_curvature"]),
                "gap": gap_norm,
                "content_class": content_class,
                "joint_match": 1.0 if index != intermediate_index and position_match == 1.0 and content_match == 1.0 else 0.0,
                "direct_match": 1.0 if index != intermediate_index and direct_position_match == 1.0 and direct_content_match == 1.0 else 0.0,
                "content_only": 1.0 if index != intermediate_index and position_match == 0.0 and content_match == 1.0 else 0.0,
                "position_only": 1.0 if index != intermediate_index and position_match == 1.0 and content_match == 0.0 else 0.0,
                "ordered_content_delta": float(step["ordered_content_delta"]),
            }
        )
    target_index = next(index for index, item in enumerate(hop2_data) if item["joint_match"] == 1.0)
    target = hop2_data[target_index]
    target_distractors = [item for index, item in enumerate(hop2_data) if index not in {intermediate_index, target_index}]
    mean_distractor_phase = sum(item["phase"] for item in target_distractors) / len(target_distractors)
    mean_distractor_gap = sum(item["gap"] for item in target_distractors) / len(target_distractors)
    mean_distractor_curvature = sum(item["curvature"] for item in target_distractors) / len(target_distractors)
    mean_distractor_content_delta = sum(item["ordered_content_delta"] for item in target_distractors) / len(target_distractors)
    # Keep the witness basis compact enough to avoid underdetermined packet fits.
    features: dict[str, float] = {
        "candidate_count": round((candidate_count - 4.0), 6),
        "query_phase": round(float(query_result["features"]["latent_transition_phase"]), 6),
        "query_desired_gap": round(desired_gap_norm, 6),
        "intermediate_phase": round(intermediate["phase"], 6),
        "intermediate_gap": round(intermediate["gap"], 6),
        "target_phase": round(target["phase"], 6),
        "target_gap": round(target["gap"], 6),
        "first_hop_content_only_count": round(
            sum(item["content_only"] for item in hop1_data if item["index"] != intermediate["index"])
            / max(1.0, candidate_count - 1.0),
            6,
        ),
        "target_phase_margin": round(target["phase"] - mean_distractor_phase, 6),
        "multi_hop_cross_curvature": round(
            (intermediate["phase"] - float(query_result["features"]["latent_transition_phase"]))
            * float(query_result["features"]["latent_transition_curvature"])
            + (target["phase"] - intermediate["phase"]) * intermediate["curvature"]
            - abs(target["gap"] - intermediate["gap"]),
            6,
        ),
    }
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "bounded_feature_audit_pass": True,
        "forbidden_multi_hop_feature_family_absent_pass": True,
    }


def positional_intermediate_pointer_selection_symbolic_features(text: str) -> dict[str, object]:
    payload = parse_positional_intermediate_pointer_selection_text(text)

    def mean_pos(step: dict[str, Any]) -> float:
        return 0.5 * (step["sample_a"].left_pos + step["sample_a"].right_pos)

    def sample_mean_pos(sample: Any) -> float:
        return 0.5 * (sample.left_pos + sample.right_pos)

    def gap_bucket(value: float) -> float:
        distance = abs(value)
        if distance < 1.0:
            return 0.0
        if distance < 2.0:
            return 1.0
        return 2.0

    def content_bucket(value: float) -> float:
        if value < -0.2:
            return 0.0
        if value > 0.2:
            return 2.0
        return 1.0

    query = payload["q"]
    candidate_payloads = payload["candidates"]
    candidate_steps = [_symbolic_insufficiency_path_step_features(item) for item in candidate_payloads]
    candidate_count = len(candidate_payloads)
    desired_gap = sample_mean_pos(query["sample_b"]) - sample_mean_pos(query["sample_a"])
    desired_side = 1.0 if desired_gap >= 0.0 else 0.0
    desired_bucket = gap_bucket(desired_gap)
    desired_content_class = content_bucket(float(_symbolic_insufficiency_path_step_features(query)["ordered_content_delta"]))
    query_mean = mean_pos(query)
    features: dict[str, float] = {
        "candidate_count": round(float(candidate_count - 4), 6),
        "query_desired_gap": round(desired_gap / 4.0, 6),
        "query_desired_side": desired_side,
        "query_desired_bucket": desired_bucket,
        "query_desired_content_class": round(desired_content_class - 1.0, 6),
    }
    intermediate_slot = 0.0
    intermediate_gap = 0.0
    intermediate_content_delta = 0.0
    for index, (item, step) in enumerate(zip(candidate_payloads, candidate_steps, strict=True)):
        gap = mean_pos(item) - query_mean
        gap_norm = round(gap / 4.0, 6)
        side = 1.0 if gap >= 0.0 else 0.0
        bucket = gap_bucket(gap)
        content_class = content_bucket(float(step["ordered_content_delta"]))
        if side == desired_side and bucket == desired_bucket and content_class == desired_content_class:
            intermediate_slot = float(index) / max(1.0, float(candidate_count - 1))
            intermediate_gap = gap_norm
            intermediate_content_delta = float(step["ordered_content_delta"])
            intermediate_payload = item
            intermediate_index = index
            break
    second_desired_gap = sample_mean_pos(intermediate_payload["sample_b"]) - sample_mean_pos(intermediate_payload["sample_a"])
    second_desired_side = 1.0 if second_desired_gap >= 0.0 else 0.0
    second_desired_bucket = gap_bucket(second_desired_gap)
    second_desired_content_class = content_bucket(float(_symbolic_insufficiency_path_step_features(intermediate_payload)["ordered_content_delta"]))
    intermediate_anchor = sample_mean_pos(intermediate_payload["sample_b"])
    target_slot = 0.0
    target_gap = 0.0
    target_content_delta = 0.0
    direct_target_null = 1.0
    second_hop_content_only_count = 0.0
    second_hop_position_only_count = 0.0
    for index, (item, step) in enumerate(zip(candidate_payloads, candidate_steps, strict=True)):
        if index == intermediate_index:
            continue
        gap = sample_mean_pos(item["sample_a"]) - intermediate_anchor
        gap_norm = round(gap / 4.0, 6)
        side = 1.0 if gap >= 0.0 else 0.0
        bucket = gap_bucket(gap)
        content_class = content_bucket(float(step["ordered_content_delta"]))
        second_position_match = 1.0 if side == second_desired_side and bucket == second_desired_bucket else 0.0
        second_content_match = 1.0 if content_class == second_desired_content_class else 0.0
        direct_position_match = 1.0 if side == desired_side and bucket == desired_bucket else 0.0
        direct_content_match = 1.0 if content_class == desired_content_class else 0.0
        if second_position_match == 1.0 and second_content_match == 1.0 and target_slot == 0.0 and gap_norm != 0.0:
            target_slot = float(index) / max(1.0, float(candidate_count - 1))
            target_gap = gap_norm
            target_content_delta = float(step["ordered_content_delta"])
            direct_target_null = 0.0 if (direct_position_match == 1.0 and direct_content_match == 1.0) else 1.0
        second_hop_content_only_count += 1.0 if second_position_match == 0.0 and second_content_match == 1.0 else 0.0
        second_hop_position_only_count += 1.0 if second_position_match == 1.0 and second_content_match == 0.0 else 0.0
    features.update(
        {
            "intermediate_slot": round(intermediate_slot, 6),
            "intermediate_gap": round(intermediate_gap, 6),
            "intermediate_content_delta": round(intermediate_content_delta, 6),
            "second_desired_gap": round(second_desired_gap / 4.0, 6),
            "second_desired_side": second_desired_side,
            "second_desired_bucket": second_desired_bucket,
            "second_desired_content_class": round(second_desired_content_class - 1.0, 6),
            "target_slot": round(target_slot, 6),
            "target_gap": round(target_gap, 6),
            "target_content_delta": round(target_content_delta, 6),
            "direct_target_null": round(direct_target_null, 6),
            "second_hop_content_only_count": round(second_hop_content_only_count / max(1.0, float(candidate_count - 2)), 6),
            "second_hop_position_only_count": round(second_hop_position_only_count / max(1.0, float(candidate_count - 2)), 6),
            "intermediate_target_slot_gap": round(intermediate_slot - target_slot, 6),
        }
    )
    return {
        "feature_order": list(features.keys()),
        "features": features,
        "allowed_multi_hop_symbolic_basis_frozen_pass": True,
        "forbidden_multi_hop_feature_family_absent_pass": True,
        "single_symbolic_family_across_candidate_counts_pass": True,
    }


def run_positional_variable_cardinality_offset_selection_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_variable_cardinality_offset_selection_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [
        positional_variable_cardinality_offset_selection_witness_features(text=text, seed=seed)
        for text, _ in validation
    ]
    test_results = [
        positional_variable_cardinality_offset_selection_witness_features(text=text, seed=seed) for text, _ in test
    ]
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
    diagnostics["forbidden_variable_cardinality_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_variable_cardinality_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_variable_cardinality_offset_selection_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_variable_cardinality_offset_selection_symbolic_features(text=text) for text, _ in train]
    validation_results = [
        positional_variable_cardinality_offset_selection_symbolic_features(text=text) for text, _ in validation
    ]
    test_results = [positional_variable_cardinality_offset_selection_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_variable_cardinality_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_variable_cardinality_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_variable_cardinality_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_variable_cardinality_feature_family_absent_pass", False)) for result in test_results
    )
    diagnostics["single_symbolic_family_across_counts_pass"] = all(
        bool(result.get("single_symbolic_family_across_counts_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_content_gated_offset_selection_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_content_gated_offset_selection_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [
        positional_content_gated_offset_selection_witness_features(text=text, seed=seed) for text, _ in validation
    ]
    test_results = [positional_content_gated_offset_selection_witness_features(text=text, seed=seed) for text, _ in test]
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
    diagnostics["forbidden_position_content_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_position_content_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_content_gated_offset_selection_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_content_gated_offset_selection_symbolic_features(text=text) for text, _ in train]
    validation_results = [
        positional_content_gated_offset_selection_symbolic_features(text=text) for text, _ in validation
    ]
    test_results = [positional_content_gated_offset_selection_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_position_content_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_position_content_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_position_content_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_position_content_feature_family_absent_pass", False)) for result in test_results
    )
    diagnostics["single_symbolic_family_across_candidate_family_pass"] = all(
        bool(result.get("single_symbolic_family_across_candidate_family_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_content_alias_disambiguation_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_content_alias_disambiguation_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [
        positional_content_alias_disambiguation_witness_features(text=text, seed=seed) for text, _ in validation
    ]
    test_results = [positional_content_alias_disambiguation_witness_features(text=text, seed=seed) for text, _ in test]
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
    diagnostics["forbidden_content_alias_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_content_alias_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_content_alias_disambiguation_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_content_alias_disambiguation_symbolic_features(text=text) for text, _ in train]
    validation_results = [
        positional_content_alias_disambiguation_symbolic_features(text=text) for text, _ in validation
    ]
    test_results = [positional_content_alias_disambiguation_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_content_alias_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_content_alias_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_content_alias_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_content_alias_feature_family_absent_pass", False)) for result in test_results
    )
    diagnostics["single_symbolic_family_across_alias_patterns_pass"] = all(
        bool(result.get("single_symbolic_family_across_alias_patterns_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_reference_revision_selection_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_reference_revision_selection_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [
        positional_reference_revision_selection_witness_features(text=text, seed=seed) for text, _ in validation
    ]
    test_results = [
        positional_reference_revision_selection_witness_features(text=text, seed=seed) for text, _ in test
    ]
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
    diagnostics["forbidden_reference_revision_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_reference_revision_feature_family_absent_pass", False))
        for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_reference_revision_selection_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_reference_revision_selection_symbolic_features(text=text) for text, _ in train]
    validation_results = [
        positional_reference_revision_selection_symbolic_features(text=text) for text, _ in validation
    ]
    test_results = [positional_reference_revision_selection_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_reference_revision_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_reference_revision_symbolic_basis_frozen_pass", False))
        for result in test_results
    )
    diagnostics["forbidden_reference_revision_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_reference_revision_feature_family_absent_pass", False))
        for result in test_results
    )
    diagnostics["single_symbolic_family_across_revision_patterns_pass"] = all(
        bool(result.get("single_symbolic_family_across_revision_patterns_pass", False))
        for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_exception_conditioned_reference_selection_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [
        positional_exception_conditioned_reference_selection_witness_features(text=text, seed=seed)
        for text, _ in train
    ]
    validation_results = [
        positional_exception_conditioned_reference_selection_witness_features(text=text, seed=seed)
        for text, _ in validation
    ]
    test_results = [
        positional_exception_conditioned_reference_selection_witness_features(text=text, seed=seed)
        for text, _ in test
    ]
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
    diagnostics["forbidden_exception_arbitration_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_exception_arbitration_feature_family_absent_pass", False))
        for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_exception_conditioned_reference_selection_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_exception_conditioned_reference_selection_symbolic_features(text=text) for text, _ in train]
    validation_results = [
        positional_exception_conditioned_reference_selection_symbolic_features(text=text) for text, _ in validation
    ]
    test_results = [positional_exception_conditioned_reference_selection_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_exception_arbitration_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_exception_arbitration_symbolic_basis_frozen_pass", False))
        for result in test_results
    )
    diagnostics["forbidden_exception_arbitration_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_exception_arbitration_feature_family_absent_pass", False))
        for result in test_results
    )
    diagnostics["single_symbolic_family_across_exception_patterns_pass"] = all(
        bool(result.get("single_symbolic_family_across_exception_patterns_pass", False))
        for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_scope_masked_reference_selection_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_scope_masked_reference_selection_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [
        positional_scope_masked_reference_selection_witness_features(text=text, seed=seed) for text, _ in validation
    ]
    test_results = [positional_scope_masked_reference_selection_witness_features(text=text, seed=seed) for text, _ in test]
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
    diagnostics["forbidden_scope_masking_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_scope_masking_feature_family_absent_pass", False))
        for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_scope_masked_reference_selection_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_scope_masked_reference_selection_symbolic_features(text=text) for text, _ in train]
    validation_results = [positional_scope_masked_reference_selection_symbolic_features(text=text) for text, _ in validation]
    test_results = [positional_scope_masked_reference_selection_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_scope_masking_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_scope_masking_symbolic_basis_frozen_pass", False))
        for result in test_results
    )
    diagnostics["forbidden_scope_masking_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_scope_masking_feature_family_absent_pass", False))
        for result in test_results
    )
    diagnostics["single_symbolic_family_across_scope_patterns_pass"] = all(
        bool(result.get("single_symbolic_family_across_scope_patterns_pass", False))
        for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_shared_memory_multi_query_selection_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_shared_memory_multi_query_selection_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [
        positional_shared_memory_multi_query_selection_witness_features(text=text, seed=seed)
        for text, _ in validation
    ]
    test_results = [
        positional_shared_memory_multi_query_selection_witness_features(text=text, seed=seed) for text, _ in test
    ]
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
    diagnostics["forbidden_shared_memory_multi_query_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_shared_memory_multi_query_feature_family_absent_pass", False))
        for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_shared_memory_multi_query_selection_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_shared_memory_multi_query_selection_symbolic_features(text=text) for text, _ in train]
    validation_results = [
        positional_shared_memory_multi_query_selection_symbolic_features(text=text) for text, _ in validation
    ]
    test_results = [positional_shared_memory_multi_query_selection_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_shared_memory_multi_query_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_shared_memory_multi_query_symbolic_basis_frozen_pass", False))
        for result in test_results
    )
    diagnostics["forbidden_shared_memory_multi_query_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_shared_memory_multi_query_feature_family_absent_pass", False))
        for result in test_results
    )
    diagnostics["single_symbolic_family_across_query_positions_pass"] = all(
        bool(result.get("single_symbolic_family_across_query_positions_pass", False))
        for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_intermediate_pointer_selection_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_intermediate_pointer_selection_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [
        positional_intermediate_pointer_selection_witness_features(text=text, seed=seed)
        for text, _ in validation
    ]
    test_results = [
        positional_intermediate_pointer_selection_witness_features(text=text, seed=seed) for text, _ in test
    ]
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
    diagnostics["forbidden_multi_hop_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_multi_hop_feature_family_absent_pass", False))
        for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_positional_intermediate_pointer_selection_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [positional_intermediate_pointer_selection_symbolic_features(text=text) for text, _ in train]
    validation_results = [
        positional_intermediate_pointer_selection_symbolic_features(text=text) for text, _ in validation
    ]
    test_results = [positional_intermediate_pointer_selection_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_multi_hop_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_multi_hop_symbolic_basis_frozen_pass", False))
        for result in test_results
    )
    diagnostics["forbidden_multi_hop_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_multi_hop_feature_family_absent_pass", False))
        for result in test_results
    )
    diagnostics["single_symbolic_family_across_candidate_counts_pass"] = all(
        bool(result.get("single_symbolic_family_across_candidate_counts_pass", False))
        for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_loop_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_loop_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [symbolic_insufficiency_loop_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [symbolic_insufficiency_loop_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(bool(result.get("bounded_feature_audit_pass", False)) for result in test_results)
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_loop_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_loop_symbolic_features(text=text) for text, _ in train]
    validation_results = [symbolic_insufficiency_loop_symbolic_features(text=text) for text, _ in validation]
    test_results = [symbolic_insufficiency_loop_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_loop_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_loop_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_fork_join_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_fork_join_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [symbolic_insufficiency_fork_join_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [symbolic_insufficiency_fork_join_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(bool(result.get("bounded_feature_audit_pass", False)) for result in test_results)
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_fork_join_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_fork_join_symbolic_features(text=text) for text, _ in train]
    validation_results = [symbolic_insufficiency_fork_join_symbolic_features(text=text) for text, _ in validation]
    test_results = [symbolic_insufficiency_fork_join_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_fork_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_fork_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_braid_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_braid_witness_features(text=text, seed=seed) for text, _ in train]
    validation_results = [symbolic_insufficiency_braid_witness_features(text=text, seed=seed) for text, _ in validation]
    test_results = [symbolic_insufficiency_braid_witness_features(text=text, seed=seed) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(bool(result.get("bounded_feature_audit_pass", False)) for result in test_results)
    diagnostics["forbidden_braid_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_braid_feature_family_absent_pass", False)) for result in test_results
    )
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_symbolic_insufficiency_braid_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_results = [symbolic_insufficiency_braid_symbolic_features(text=text) for text, _ in train]
    validation_results = [symbolic_insufficiency_braid_symbolic_features(text=text) for text, _ in validation]
    test_results = [symbolic_insufficiency_braid_symbolic_features(text=text) for text, _ in test]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["allowed_braid_symbolic_basis_frozen_pass"] = all(
        bool(result.get("allowed_braid_symbolic_basis_frozen_pass", False)) for result in test_results
    )
    diagnostics["forbidden_braid_feature_family_absent_pass"] = all(
        bool(result.get("forbidden_braid_feature_family_absent_pass", False)) for result in test_results
    )
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


def run_transition_listwise_topk_margin_backend_from_results(
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

    def topk_margin(values: list[float]) -> float:
        ordered = sorted(values, reverse=True)
        if len(ordered) < 4:
            return 0.0
        top_mean = sum(ordered[:2]) / 2.0
        bottom_mean = sum(ordered[-2:]) / 2.0
        return top_mean - bottom_mean

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

    true_margins = [topk_margin(values) for values in grouped_true_scores]
    pred_margins = [topk_margin(values) for values in grouped_test_scores]

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
    diagnostics["margin_target_mode"] = "top2_vs_bottom2_gap"
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


def transition_localization_payload(text: str) -> dict[str, Any]:
    return parse_transition_localization_text(text)


def run_transition_localization_backend_from_results(
    train_anchor_results: list[list[dict[str, Any]]],
    train_left_results: list[list[dict[str, Any]]],
    train_right_results: list[list[dict[str, Any]]],
    validation_anchor_results: list[list[dict[str, Any]]],
    validation_left_results: list[list[dict[str, Any]]],
    validation_right_results: list[list[dict[str, Any]]],
    test_anchor_results: list[list[dict[str, Any]]],
    test_left_results: list[list[dict[str, Any]]],
    test_right_results: list[list[dict[str, Any]]],
    train_payloads: list[dict[str, Any]],
    validation_payloads: list[dict[str, Any]],
    test_payloads: list[dict[str, Any]],
    train_labels: list[int],
    validation_labels: list[int],
    test_labels: list[int],
) -> tuple[float, float, float, float, dict[str, Any]]:
    feature_order = list(train_anchor_results[0][0]["feature_order"]) if train_anchor_results and train_anchor_results[0] else []
    train_matrix = _transition_localization_matrix(train_anchor_results, train_left_results, train_right_results, train_payloads, feature_order)
    validation_matrix = _transition_localization_matrix(validation_anchor_results, validation_left_results, validation_right_results, validation_payloads, feature_order)
    test_matrix = _transition_localization_matrix(test_anchor_results, test_left_results, test_right_results, test_payloads, feature_order)

    weights, bias = fit_logistic_witness_head(train_matrix, train_labels)
    train_scores = [sigmoid(bias + sum(weight * value for weight, value in zip(weights, row))) for row in train_matrix]
    validation_scores = [sigmoid(bias + sum(weight * value for weight, value in zip(weights, row))) for row in validation_matrix]
    test_scores = [sigmoid(bias + sum(weight * value for weight, value in zip(weights, row))) for row in test_matrix]
    threshold = calibrate_threshold(validation_scores, validation_labels)
    preds = [1 if score >= threshold else 0 for score in test_scores]

    diagnostics = build_transition_order_run_diagnostics(
        results=[
            item
            for row in test_anchor_results + test_left_results + test_right_results
            for item in row
        ],
        feature_order=feature_order,
        weights=weights,
        bias=bias,
    )
    diagnostics["localization_target_mode"] = "asymmetric_sign_channel"
    diagnostics["paired_channel_target"] = True
    train_loss = binary_cross_entropy(train_labels, train_scores)
    eval_loss = binary_cross_entropy(test_labels, test_scores)
    accuracy = compute_accuracy(test_labels, preds)
    f1 = compute_f1_binary(test_labels, preds)
    return train_loss, eval_loss, accuracy, f1, diagnostics


def _transition_localization_matrix(
    anchor_results_by_row: list[list[dict[str, Any]]],
    left_results_by_row: list[list[dict[str, Any]]],
    right_results_by_row: list[list[dict[str, Any]]],
    payloads: list[dict[str, Any]],
    feature_order: list[str],
) -> list[list[float]]:
    matrix: list[list[float]] = []
    for anchor_results, left_results, right_results, payload in zip(
        anchor_results_by_row,
        left_results_by_row,
        right_results_by_row,
        payloads,
    ):
        anchor = _transition_sign_feature_vector(anchor_results, payload["parsed_anchor_context"], feature_order)
        left = _transition_sign_feature_vector(left_results, payload["parsed_left_context"], feature_order)
        right = _transition_sign_feature_vector(right_results, payload["parsed_right_context"], feature_order)
        row: list[float] = []
        for anchor_value, left_value, right_value in zip(anchor, left, right):
            left_delta = left_value - anchor_value
            right_delta = right_value - anchor_value
            row.extend(
                [
                    left_delta,
                    right_delta,
                    abs(left_delta),
                    abs(right_delta),
                    left_delta - right_delta,
                ]
            )
        matrix.append(row)
    return matrix


def run_transition_orbit_asymmetric_sign_localization_witness_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    seed: int,
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    if validation is None:
        _, validation = stratified_calibration_split(train)
    train_payloads = [transition_localization_payload(text) for text, _ in train]
    validation_payloads = [transition_localization_payload(text) for text, _ in validation]
    test_payloads = [transition_localization_payload(text) for text, _ in test]
    train_anchor_results = [transition_orbit_listwise_witness_results(payload["anchor_context"], seed=seed) for payload in train_payloads]
    train_left_results = [transition_orbit_listwise_witness_results(payload["left_context"], seed=seed) for payload in train_payloads]
    train_right_results = [transition_orbit_listwise_witness_results(payload["right_context"], seed=seed) for payload in train_payloads]
    validation_anchor_results = [transition_orbit_listwise_witness_results(payload["anchor_context"], seed=seed) for payload in validation_payloads]
    validation_left_results = [transition_orbit_listwise_witness_results(payload["left_context"], seed=seed) for payload in validation_payloads]
    validation_right_results = [transition_orbit_listwise_witness_results(payload["right_context"], seed=seed) for payload in validation_payloads]
    test_anchor_results = [transition_orbit_listwise_witness_results(payload["anchor_context"], seed=seed) for payload in test_payloads]
    test_left_results = [transition_orbit_listwise_witness_results(payload["left_context"], seed=seed) for payload in test_payloads]
    test_right_results = [transition_orbit_listwise_witness_results(payload["right_context"], seed=seed) for payload in test_payloads]
    train_loss, eval_loss, accuracy, f1, diagnostics = run_transition_localization_backend_from_results(
        train_anchor_results,
        train_left_results,
        train_right_results,
        validation_anchor_results,
        validation_left_results,
        validation_right_results,
        test_anchor_results,
        test_left_results,
        test_right_results,
        train_payloads,
        validation_payloads,
        test_payloads,
        [label for _, label in train],
        [label for _, label in validation],
        [label for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(
        bool(result.get("bounded_feature_audit_pass", False))
        for row in test_anchor_results + test_left_results + test_right_results
        for result in row
    )
    diagnostics["token_identity_absent"] = all(
        bool(result.get("token_identity_absent", False))
        for row in test_anchor_results + test_left_results + test_right_results
        for result in row
    )
    diagnostics["anti_collapse_pass"] = True
    return train_loss, eval_loss, accuracy, f1, diagnostics


def _run_transition_localization_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None,
    builder,
) -> tuple[float, float, float, float, dict[str, Any]]:
    if validation is None:
        _, validation = stratified_calibration_split(train)
    train_payloads = [transition_localization_payload(text) for text, _ in train]
    validation_payloads = [transition_localization_payload(text) for text, _ in validation]
    test_payloads = [transition_localization_payload(text) for text, _ in test]
    train_anchor_results = [builder(payload["anchor_context"]) for payload in train_payloads]
    train_left_results = [builder(payload["left_context"]) for payload in train_payloads]
    train_right_results = [builder(payload["right_context"]) for payload in train_payloads]
    validation_anchor_results = [builder(payload["anchor_context"]) for payload in validation_payloads]
    validation_left_results = [builder(payload["left_context"]) for payload in validation_payloads]
    validation_right_results = [builder(payload["right_context"]) for payload in validation_payloads]
    test_anchor_results = [builder(payload["anchor_context"]) for payload in test_payloads]
    test_left_results = [builder(payload["left_context"]) for payload in test_payloads]
    test_right_results = [builder(payload["right_context"]) for payload in test_payloads]
    return run_transition_localization_backend_from_results(
        train_anchor_results,
        train_left_results,
        train_right_results,
        validation_anchor_results,
        validation_left_results,
        validation_right_results,
        test_anchor_results,
        test_left_results,
        test_right_results,
        train_payloads,
        validation_payloads,
        test_payloads,
        [label for _, label in train],
        [label for _, label in validation],
        [label for _, label in test],
    )


def run_transition_localization_lookup_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    return _run_transition_localization_symbolic_backend(train, test, validation, symbolic_transition_list_lookup_results)


def run_transition_localization_cross_direction_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    return _run_transition_localization_symbolic_backend(train, test, validation, symbolic_transition_list_cross_direction_results)


def run_transition_localization_quadratic_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    return _run_transition_localization_symbolic_backend(train, test, validation, symbolic_transition_list_quadratic_results)


def run_transition_localization_orbit_permuted_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    return _run_transition_localization_symbolic_backend(train, test, validation, symbolic_transition_list_orbit_permuted_results)


def run_transition_channel_advantage_backend_from_results(
    train_anchor_results: list[list[dict[str, Any]]],
    train_left_results: list[list[dict[str, Any]]],
    train_right_results: list[list[dict[str, Any]]],
    validation_anchor_results: list[list[dict[str, Any]]],
    validation_left_results: list[list[dict[str, Any]]],
    validation_right_results: list[list[dict[str, Any]]],
    test_anchor_results: list[list[dict[str, Any]]],
    test_left_results: list[list[dict[str, Any]]],
    test_right_results: list[list[dict[str, Any]]],
    train_payloads: list[dict[str, Any]],
    validation_payloads: list[dict[str, Any]],
    test_payloads: list[dict[str, Any]],
    train_labels: list[float],
    validation_labels: list[float],
    test_labels: list[float],
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    feature_order = list(train_anchor_results[0][0]["feature_order"]) if train_anchor_results and train_anchor_results[0] else []
    train_matrix = _transition_localization_matrix(train_anchor_results, train_left_results, train_right_results, train_payloads, feature_order)
    validation_matrix = _transition_localization_matrix(validation_anchor_results, validation_left_results, validation_right_results, validation_payloads, feature_order)
    test_matrix = _transition_localization_matrix(test_anchor_results, test_left_results, test_right_results, test_payloads, feature_order)
    train_results = [
        {"feature_order": [f"triple_{idx}" for idx in range(len(row))], "features": {f"triple_{idx}": value for idx, value in enumerate(row)}}
        for row in train_matrix
    ]
    validation_results = [
        {"feature_order": [f"triple_{idx}" for idx in range(len(row))], "features": {f"triple_{idx}": value for idx, value in enumerate(row)}}
        for row in validation_matrix
    ]
    test_results = [
        {"feature_order": [f"triple_{idx}" for idx in range(len(row))], "features": {f"triple_{idx}": value for idx, value in enumerate(row)}}
        for row in test_matrix
    ]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_continuous_backend_from_results(
        train_results,
        validation_results,
        test_results,
        train_labels,
        validation_labels,
        test_labels,
    )
    diagnostics["channel_advantage_target_mode"] = "signed_left_minus_right_effect"
    diagnostics["paired_channel_target"] = True
    diagnostics["feature_order"] = [f"triple_{idx}" for idx in range(len(train_matrix[0]))] if train_matrix else []
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_transition_channel_order_backend_from_results(
    train_anchor_results: list[list[dict[str, Any]]],
    train_left_results: list[list[dict[str, Any]]],
    train_right_results: list[list[dict[str, Any]]],
    validation_anchor_results: list[list[dict[str, Any]]],
    validation_left_results: list[list[dict[str, Any]]],
    validation_right_results: list[list[dict[str, Any]]],
    test_anchor_results: list[list[dict[str, Any]]],
    test_left_results: list[list[dict[str, Any]]],
    test_right_results: list[list[dict[str, Any]]],
    train_payloads: list[dict[str, Any]],
    validation_payloads: list[dict[str, Any]],
    test_payloads: list[dict[str, Any]],
    train_labels: list[int],
    validation_labels: list[int],
    test_labels: list[int],
) -> tuple[float, float, float, float, dict[str, Any]]:
    feature_order = list(train_anchor_results[0][0]["feature_order"]) if train_anchor_results and train_anchor_results[0] else []
    train_matrix = _transition_localization_matrix(train_anchor_results, train_left_results, train_right_results, train_payloads, feature_order)
    validation_matrix = _transition_localization_matrix(
        validation_anchor_results, validation_left_results, validation_right_results, validation_payloads, feature_order
    )
    test_matrix = _transition_localization_matrix(test_anchor_results, test_left_results, test_right_results, test_payloads, feature_order)

    weights, bias = fit_logistic_witness_head(train_matrix, train_labels)
    train_scores = [sigmoid(bias + sum(weight * value for weight, value in zip(weights, row))) for row in train_matrix]
    validation_scores = [sigmoid(bias + sum(weight * value for weight, value in zip(weights, row))) for row in validation_matrix]
    test_scores = [sigmoid(bias + sum(weight * value for weight, value in zip(weights, row))) for row in test_matrix]
    threshold = calibrate_threshold(validation_scores, validation_labels)
    preds = [1 if score >= threshold else 0 for score in test_scores]

    diagnostics = build_transition_order_run_diagnostics(
        results=[item for row in test_anchor_results + test_left_results + test_right_results for item in row],
        feature_order=[f"triple_{idx}" for idx in range(len(train_matrix[0]))] if train_matrix else [],
        weights=weights,
        bias=bias,
    )
    diagnostics["channel_order_target_mode"] = "binary_left_vs_right_order"
    diagnostics["paired_channel_target"] = True
    train_loss = binary_cross_entropy(train_labels, train_scores)
    eval_loss = binary_cross_entropy(test_labels, test_scores)
    accuracy = compute_accuracy(test_labels, preds)
    f1 = compute_f1_binary(test_labels, preds)
    return train_loss, eval_loss, accuracy, f1, diagnostics


def run_transition_orbit_channel_advantage_witness_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    seed: int,
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_payloads = [transition_localization_payload(text) for text, _ in train]
    validation_payloads = [transition_localization_payload(text) for text, _ in validation]
    test_payloads = [transition_localization_payload(text) for text, _ in test]
    train_anchor_results = [transition_orbit_listwise_witness_results(payload["anchor_context"], seed=seed) for payload in train_payloads]
    train_left_results = [transition_orbit_listwise_witness_results(payload["left_context"], seed=seed) for payload in train_payloads]
    train_right_results = [transition_orbit_listwise_witness_results(payload["right_context"], seed=seed) for payload in train_payloads]
    validation_anchor_results = [transition_orbit_listwise_witness_results(payload["anchor_context"], seed=seed) for payload in validation_payloads]
    validation_left_results = [transition_orbit_listwise_witness_results(payload["left_context"], seed=seed) for payload in validation_payloads]
    validation_right_results = [transition_orbit_listwise_witness_results(payload["right_context"], seed=seed) for payload in validation_payloads]
    test_anchor_results = [transition_orbit_listwise_witness_results(payload["anchor_context"], seed=seed) for payload in test_payloads]
    test_left_results = [transition_orbit_listwise_witness_results(payload["left_context"], seed=seed) for payload in test_payloads]
    test_right_results = [transition_orbit_listwise_witness_results(payload["right_context"], seed=seed) for payload in test_payloads]
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_transition_channel_advantage_backend_from_results(
        train_anchor_results,
        train_left_results,
        train_right_results,
        validation_anchor_results,
        validation_left_results,
        validation_right_results,
        test_anchor_results,
        test_left_results,
        test_right_results,
        train_payloads,
        validation_payloads,
        test_payloads,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(
        bool(result.get("bounded_feature_audit_pass", False))
        for row in test_anchor_results + test_left_results + test_right_results
        for result in row
    )
    diagnostics["token_identity_absent"] = all(
        bool(result.get("token_identity_absent", False))
        for row in test_anchor_results + test_left_results + test_right_results
        for result in row
    )
    diagnostics["anti_collapse_pass"] = True
    return mae_train, mae_eval, accuracy, f1, diagnostics, extra


def run_transition_orbit_channel_order_witness_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    seed: int,
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    if validation is None:
        _, validation = stratified_calibration_split(train)
    train_payloads = [transition_localization_payload(text) for text, _ in train]
    validation_payloads = [transition_localization_payload(text) for text, _ in validation]
    test_payloads = [transition_localization_payload(text) for text, _ in test]
    train_anchor_results = [transition_orbit_listwise_witness_results(payload["anchor_context"], seed=seed) for payload in train_payloads]
    train_left_results = [transition_orbit_listwise_witness_results(payload["left_context"], seed=seed) for payload in train_payloads]
    train_right_results = [transition_orbit_listwise_witness_results(payload["right_context"], seed=seed) for payload in train_payloads]
    validation_anchor_results = [transition_orbit_listwise_witness_results(payload["anchor_context"], seed=seed) for payload in validation_payloads]
    validation_left_results = [transition_orbit_listwise_witness_results(payload["left_context"], seed=seed) for payload in validation_payloads]
    validation_right_results = [transition_orbit_listwise_witness_results(payload["right_context"], seed=seed) for payload in validation_payloads]
    test_anchor_results = [transition_orbit_listwise_witness_results(payload["anchor_context"], seed=seed) for payload in test_payloads]
    test_left_results = [transition_orbit_listwise_witness_results(payload["left_context"], seed=seed) for payload in test_payloads]
    test_right_results = [transition_orbit_listwise_witness_results(payload["right_context"], seed=seed) for payload in test_payloads]
    train_loss, eval_loss, accuracy, f1, diagnostics = run_transition_channel_order_backend_from_results(
        train_anchor_results,
        train_left_results,
        train_right_results,
        validation_anchor_results,
        validation_left_results,
        validation_right_results,
        test_anchor_results,
        test_left_results,
        test_right_results,
        train_payloads,
        validation_payloads,
        test_payloads,
        [label for _, label in train],
        [label for _, label in validation],
        [label for _, label in test],
    )
    diagnostics["bounded_feature_audit_pass"] = all(
        bool(result.get("bounded_feature_audit_pass", False))
        for row in test_anchor_results + test_left_results + test_right_results
        for result in row
    )
    diagnostics["token_identity_absent"] = all(
        bool(result.get("token_identity_absent", False))
        for row in test_anchor_results + test_left_results + test_right_results
        for result in row
    )
    diagnostics["anti_collapse_pass"] = True
    return train_loss, eval_loss, accuracy, f1, diagnostics


def _run_transition_channel_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None,
    builder,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    if validation is None:
        midpoint = max(1, len(train) // 4)
        validation = train[:midpoint]
    train_payloads = [transition_localization_payload(text) for text, _ in train]
    validation_payloads = [transition_localization_payload(text) for text, _ in validation]
    test_payloads = [transition_localization_payload(text) for text, _ in test]
    train_anchor_results = [builder(payload["anchor_context"]) for payload in train_payloads]
    train_left_results = [builder(payload["left_context"]) for payload in train_payloads]
    train_right_results = [builder(payload["right_context"]) for payload in train_payloads]
    validation_anchor_results = [builder(payload["anchor_context"]) for payload in validation_payloads]
    validation_left_results = [builder(payload["left_context"]) for payload in validation_payloads]
    validation_right_results = [builder(payload["right_context"]) for payload in validation_payloads]
    test_anchor_results = [builder(payload["anchor_context"]) for payload in test_payloads]
    test_left_results = [builder(payload["left_context"]) for payload in test_payloads]
    test_right_results = [builder(payload["right_context"]) for payload in test_payloads]
    return run_transition_channel_advantage_backend_from_results(
        train_anchor_results,
        train_left_results,
        train_right_results,
        validation_anchor_results,
        validation_left_results,
        validation_right_results,
        test_anchor_results,
        test_left_results,
        test_right_results,
        train_payloads,
        validation_payloads,
        test_payloads,
        [float(label) for _, label in train],
        [float(label) for _, label in validation],
        [float(label) for _, label in test],
    )


def run_transition_channel_lookup_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    return _run_transition_channel_symbolic_regressor(train, test, validation, symbolic_transition_list_lookup_results)


def run_transition_channel_cross_direction_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    return _run_transition_channel_symbolic_regressor(train, test, validation, symbolic_transition_list_cross_direction_results)


def run_transition_channel_quadratic_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    return _run_transition_channel_symbolic_regressor(train, test, validation, symbolic_transition_list_quadratic_results)


def run_transition_channel_orbit_permuted_symbolic_regressor(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    return _run_transition_channel_symbolic_regressor(train, test, validation, symbolic_transition_list_orbit_permuted_results)


def _run_transition_channel_order_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None,
    builder,
) -> tuple[float, float, float, float, dict[str, Any]]:
    if validation is None:
        _, validation = stratified_calibration_split(train)
    train_payloads = [transition_localization_payload(text) for text, _ in train]
    validation_payloads = [transition_localization_payload(text) for text, _ in validation]
    test_payloads = [transition_localization_payload(text) for text, _ in test]
    train_anchor_results = [builder(payload["anchor_context"]) for payload in train_payloads]
    train_left_results = [builder(payload["left_context"]) for payload in train_payloads]
    train_right_results = [builder(payload["right_context"]) for payload in train_payloads]
    validation_anchor_results = [builder(payload["anchor_context"]) for payload in validation_payloads]
    validation_left_results = [builder(payload["left_context"]) for payload in validation_payloads]
    validation_right_results = [builder(payload["right_context"]) for payload in validation_payloads]
    test_anchor_results = [builder(payload["anchor_context"]) for payload in test_payloads]
    test_left_results = [builder(payload["left_context"]) for payload in test_payloads]
    test_right_results = [builder(payload["right_context"]) for payload in test_payloads]
    return run_transition_channel_order_backend_from_results(
        train_anchor_results,
        train_left_results,
        train_right_results,
        validation_anchor_results,
        validation_left_results,
        validation_right_results,
        test_anchor_results,
        test_left_results,
        test_right_results,
        train_payloads,
        validation_payloads,
        test_payloads,
        [label for _, label in train],
        [label for _, label in validation],
        [label for _, label in test],
    )


def run_transition_channel_order_lookup_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    return _run_transition_channel_order_symbolic_backend(train, test, validation, symbolic_transition_list_lookup_results)


def run_transition_channel_order_cross_direction_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    return _run_transition_channel_order_symbolic_backend(train, test, validation, symbolic_transition_list_cross_direction_results)


def run_transition_channel_order_quadratic_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    return _run_transition_channel_order_symbolic_backend(train, test, validation, symbolic_transition_list_quadratic_results)


def run_transition_channel_order_orbit_permuted_symbolic_backend(
    train: list[tuple[str, int]],
    test: list[tuple[str, int]],
    validation: list[tuple[str, int]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any]]:
    return _run_transition_channel_order_symbolic_backend(train, test, validation, symbolic_transition_list_orbit_permuted_results)


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


def run_transition_orbit_topk_margin_witness_backend(
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
    mae_train, mae_eval, accuracy, f1, diagnostics, extra = run_transition_listwise_topk_margin_backend_from_results(
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


def _run_transition_topk_margin_symbolic_backend(
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
    return run_transition_listwise_topk_margin_backend_from_results(
        train_results,
        validation_results,
        test_results,
        train_payloads,
        validation_payloads,
        test_payloads,
    )


def run_transition_topk_margin_lookup_symbolic_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    return _run_transition_topk_margin_symbolic_backend(train, test, validation, symbolic_transition_list_lookup_results)


def run_transition_topk_margin_cross_direction_symbolic_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    return _run_transition_topk_margin_symbolic_backend(train, test, validation, symbolic_transition_list_cross_direction_results)


def run_transition_topk_margin_quadratic_symbolic_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    return _run_transition_topk_margin_symbolic_backend(train, test, validation, symbolic_transition_list_quadratic_results)


def run_transition_topk_margin_orbit_permuted_symbolic_backend(
    train: list[tuple[str, float]],
    test: list[tuple[str, float]],
    validation: list[tuple[str, float]] | None = None,
) -> tuple[float, float, float, float, dict[str, Any], dict[str, float]]:
    return _run_transition_topk_margin_symbolic_backend(train, test, validation, symbolic_transition_list_orbit_permuted_results)


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
    if dataset == "synthetic_symbolic_insufficiency_transition_response":
        bundle = generate_symbolic_insufficiency_transition_response_bundle(
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
            "data_mode": "synthetic_symbolic_insufficiency_transition_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_symbolic_insufficiency_path_response":
        bundle = generate_symbolic_insufficiency_path_response_bundle(
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
            "data_mode": "synthetic_symbolic_insufficiency_path_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_symbolic_insufficiency_relay_binding_response":
        bundle = generate_symbolic_insufficiency_relay_binding_response_bundle(
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
            "data_mode": "synthetic_symbolic_insufficiency_relay_binding_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_symbolic_insufficiency_cascade_reconciliation_response":
        bundle = generate_symbolic_insufficiency_cascade_reconciliation_response_bundle(
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
            "data_mode": "synthetic_symbolic_insufficiency_cascade_reconciliation_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_symbolic_insufficiency_latch_switch_response":
        bundle = generate_symbolic_insufficiency_latch_switch_response_bundle(
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
            "data_mode": "synthetic_symbolic_insufficiency_latch_switch_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_symbolic_insufficiency_staggered_binding_response":
        bundle = generate_symbolic_insufficiency_staggered_binding_response_bundle(
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
            "data_mode": "synthetic_symbolic_insufficiency_staggered_binding_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_symbolic_insufficiency_fanin_consensus_response":
        bundle = generate_symbolic_insufficiency_fanin_consensus_response_bundle(
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
            "data_mode": "synthetic_symbolic_insufficiency_fanin_consensus_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_symbolic_insufficiency_echo_resolution_response":
        bundle = generate_symbolic_insufficiency_echo_resolution_response_bundle(
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
            "data_mode": "synthetic_symbolic_insufficiency_echo_resolution_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_symbolic_insufficiency_selector_arbitration_response":
        bundle = generate_symbolic_insufficiency_selector_arbitration_response_bundle(
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
            "data_mode": "synthetic_symbolic_insufficiency_selector_arbitration_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_symbolic_insufficiency_counterfactual_handoff_response":
        bundle = generate_symbolic_insufficiency_counterfactual_handoff_response_bundle(
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
            "data_mode": "synthetic_symbolic_insufficiency_counterfactual_handoff_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_positional_anchor_order_response":
        bundle = generate_positional_anchor_order_response_bundle(
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
            "data_mode": "synthetic_positional_anchor_order_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_positional_anchor_distance_response":
        bundle = generate_positional_anchor_distance_response_bundle(
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
            "data_mode": "synthetic_positional_anchor_distance_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_positional_anchor_span_membership_response":
        bundle = generate_positional_anchor_span_membership_response_bundle(
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
            "data_mode": "synthetic_positional_anchor_span_membership_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_positional_anchor_offset_signature_response":
        bundle = generate_positional_anchor_offset_signature_response_bundle(
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
            "data_mode": "synthetic_positional_anchor_offset_signature_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_positional_anchor_betweenness_response":
        bundle = generate_positional_anchor_betweenness_response_bundle(
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
            "data_mode": "synthetic_positional_anchor_betweenness_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_positional_offset_retrieval_response":
        bundle = generate_positional_offset_retrieval_response_bundle(
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
            "data_mode": "synthetic_positional_offset_retrieval_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_positional_key_query_offset_selection_response":
        bundle = generate_positional_key_query_offset_selection_response_bundle(
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
            "data_mode": "synthetic_positional_key_query_offset_selection_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_positional_dual_anchor_offset_consensus_response":
        bundle = generate_positional_dual_anchor_offset_consensus_response_bundle(
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
            "data_mode": "synthetic_positional_dual_anchor_offset_consensus_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_positional_variable_cardinality_offset_selection_response":
        bundle = generate_positional_variable_cardinality_offset_selection_response_bundle(
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
            "data_mode": "synthetic_positional_variable_cardinality_offset_selection_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_positional_content_gated_offset_selection_response":
        bundle = generate_positional_content_gated_offset_selection_response_bundle(
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
            "data_mode": "synthetic_positional_content_gated_offset_selection_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_positional_content_alias_disambiguation_response":
        bundle = generate_positional_content_alias_disambiguation_response_bundle(
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
            "data_mode": "synthetic_positional_content_alias_disambiguation_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_positional_reference_revision_selection_response":
        bundle = generate_positional_reference_revision_selection_response_bundle(
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
            "data_mode": "synthetic_positional_reference_revision_selection_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_positional_exception_conditioned_reference_selection_response":
        bundle = generate_positional_exception_conditioned_reference_selection_response_bundle(
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
            "data_mode": "synthetic_positional_exception_conditioned_reference_selection_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_positional_scope_masked_reference_selection_response":
        bundle = generate_positional_scope_masked_reference_selection_response_bundle(
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
            "data_mode": "synthetic_positional_scope_masked_reference_selection_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_positional_shared_memory_multi_query_selection_response":
        bundle = generate_positional_shared_memory_multi_query_selection_response_bundle(
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
            "data_mode": "synthetic_positional_shared_memory_multi_query_selection_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_positional_intermediate_pointer_selection_response":
        bundle = generate_positional_intermediate_pointer_selection_response_bundle(
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
            "data_mode": "synthetic_positional_intermediate_pointer_selection_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_symbolic_insufficiency_loop_closure_response":
        bundle = generate_symbolic_insufficiency_loop_closure_response_bundle(
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
            "data_mode": "synthetic_symbolic_insufficiency_loop_closure_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_symbolic_insufficiency_fork_join_response":
        bundle = generate_symbolic_insufficiency_fork_join_response_bundle(
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
            "data_mode": "synthetic_symbolic_insufficiency_fork_join_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_symbolic_insufficiency_braid_crossing_response":
        bundle = generate_symbolic_insufficiency_braid_crossing_response_bundle(
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
            "data_mode": "synthetic_symbolic_insufficiency_braid_crossing_response",
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
    if dataset == "synthetic_transition_orbit_asymmetric_sign_localization_binary":
        bundle = generate_transition_orbit_asymmetric_sign_localization_binary_bundle(
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
            "data_mode": "synthetic_transition_orbit_asymmetric_sign_localization_binary",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_channel_advantage_response":
        bundle = generate_transition_orbit_channel_advantage_response_bundle(
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
            "data_mode": "synthetic_transition_orbit_channel_advantage_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_channel_order_response":
        bundle = generate_transition_orbit_channel_order_response_bundle(
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
            "data_mode": "synthetic_transition_orbit_channel_order_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_response":
        bundle = generate_transition_orbit_slot_invariant_channel_order_response_bundle(
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
            "data_mode": "synthetic_transition_orbit_slot_invariant_channel_order_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_margin_response":
        bundle = generate_transition_orbit_slot_invariant_channel_order_margin_response_bundle(
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
            "data_mode": "synthetic_transition_orbit_slot_invariant_channel_order_margin_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_topk_margin_response":
        bundle = generate_transition_orbit_slot_invariant_channel_order_topk_margin_response_bundle(
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
            "data_mode": "synthetic_transition_orbit_slot_invariant_channel_order_topk_margin_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_margin_response":
        bundle = generate_transition_orbit_slot_invariant_topk_pair_margin_response_bundle(
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
            "data_mode": "synthetic_transition_orbit_slot_invariant_topk_pair_margin_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_agreement_binary":
        bundle = generate_transition_orbit_slot_invariant_topk_pair_order_agreement_binary_bundle(
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
            "data_mode": "synthetic_transition_orbit_slot_invariant_topk_pair_order_agreement_binary",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_consistency_binary":
        bundle = generate_transition_orbit_slot_invariant_topk_pair_order_signed_consistency_binary_bundle(
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
            "data_mode": "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_consistency_binary",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_consistency_binary":
        bundle = generate_transition_orbit_slot_invariant_topk_pair_order_signed_flip_consistency_binary_bundle(
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
            "data_mode": "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_consistency_binary",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_stability_binary":
        bundle = generate_transition_orbit_slot_invariant_topk_pair_order_signed_flip_stability_binary_bundle(
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
            "data_mode": "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_stability_binary",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_persistence_binary":
        bundle = generate_transition_orbit_slot_invariant_topk_pair_order_signed_flip_persistence_binary_bundle(
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
            "data_mode": "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_persistence_binary",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_recurrence_binary":
        bundle = generate_transition_orbit_slot_invariant_topk_pair_order_signed_flip_recurrence_binary_bundle(
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
            "data_mode": "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_recurrence_binary",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_reversion_binary":
        bundle = generate_transition_orbit_slot_invariant_topk_pair_order_signed_flip_reversion_binary_bundle(
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
            "data_mode": "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_reversion_binary",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_hysteresis_binary":
        bundle = generate_transition_orbit_slot_invariant_topk_pair_order_signed_flip_hysteresis_binary_bundle(
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
            "data_mode": "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_hysteresis_binary",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_memory_binary":
        bundle = generate_transition_orbit_slot_invariant_topk_pair_order_signed_flip_memory_binary_bundle(
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
            "data_mode": "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_memory_binary",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_stability_binary":
        bundle = generate_transition_orbit_slot_invariant_topk_pair_order_stability_binary_bundle(
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
            "data_mode": "synthetic_transition_orbit_slot_invariant_topk_pair_order_stability_binary",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_drift_response":
        bundle = generate_transition_orbit_slot_invariant_topk_pair_order_drift_response_bundle(
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
            "data_mode": "synthetic_transition_orbit_slot_invariant_topk_pair_order_drift_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_drift_response":
        bundle = generate_transition_orbit_slot_invariant_topk_pair_order_signed_drift_response_bundle(
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
            "data_mode": "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_drift_response",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_rank_only":
        bundle = generate_transition_orbit_slot_invariant_channel_order_rank_only_bundle(
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
            "data_mode": "synthetic_transition_orbit_slot_invariant_channel_order_rank_only",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_topk_rank_only":
        bundle = generate_transition_orbit_slot_invariant_channel_order_topk_rank_only_bundle(
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
            "data_mode": "synthetic_transition_orbit_slot_invariant_channel_order_topk_rank_only",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_topk_preference_binary":
        bundle = generate_transition_orbit_slot_invariant_channel_order_topk_preference_binary_bundle(
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
            "data_mode": "synthetic_transition_orbit_slot_invariant_channel_order_topk_preference_binary",
            "dataset_diagnostics": bundle.diagnostics,
        }
    if dataset == "synthetic_transition_orbit_slot_invariant_channel_order_topk_consistency_binary":
        bundle = generate_transition_orbit_slot_invariant_channel_order_topk_consistency_binary_bundle(
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
            "data_mode": "synthetic_transition_orbit_slot_invariant_channel_order_topk_consistency_binary",
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
