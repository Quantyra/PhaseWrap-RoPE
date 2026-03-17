import importlib.util

from qrope.run import (
    RELATIONAL_WITNESS_FEATURE_GROUPS,
    RELATIONAL_WITNESS_SCHEMA_VIEWS,
    build_relational_witness_feature_mask,
    calibrate_threshold,
    collect_quandela_scores,
    compute_balanced_accuracy,
    compute_macro_f1_binary,
    estimate_hardware_costs,
    limit_remote_samples,
    load_dataset_samples,
    parse_dual_synthetic_pair_text,
    run_real_experiment,
    symbolic_dual_content_interaction_features,
    symbolic_dual_cross_interaction_features,
    symbolic_dual_interaction_features,
    symbolic_dual_sector_features,
    symbolic_triple_parity_features,
    symbolic_triple_orientation_features,
    symbolic_triple_two_family_features,
    symbolic_relational_features,
    stratified_calibration_split,
)


def test_real_experiment_returns_non_placeholder_metrics() -> None:
    metrics = run_real_experiment(dataset="yelp", seed=42, backend="sim_local", variant="V0")
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0
    assert metrics["train_loss_final"] > 0.0
    assert metrics["eval_loss"] > 0.0
    assert metrics["data_mode"] in {"synthetic_fallback", "local_jsonl"}


def test_hardware_cost_estimate_positive() -> None:
    gate_count, depth = estimate_hardware_costs(qubits=8, layers=2, variant="V3")
    assert gate_count > 0
    assert depth > 0


def test_v4_hardware_cost_matches_v3_structure() -> None:
    gate_count_v3, depth_v3 = estimate_hardware_costs(qubits=8, layers=2, variant="V3")
    gate_count_v4, depth_v4 = estimate_hardware_costs(qubits=8, layers=2, variant="V4")
    assert gate_count_v4 == gate_count_v3
    assert depth_v4 == depth_v3


def test_v4b_hardware_cost_matches_v3_structure() -> None:
    gate_count_v3, depth_v3 = estimate_hardware_costs(qubits=8, layers=2, variant="V3")
    gate_count_v4b, depth_v4b = estimate_hardware_costs(qubits=8, layers=2, variant="V4b")
    assert gate_count_v4b == gate_count_v3
    assert depth_v4b == depth_v3


def test_local_dataset_loader_path() -> None:
    rows, mode = load_dataset_samples(dataset="yelp", seed=42)
    assert len(rows) >= 20
    assert mode == "local_jsonl"


def test_local_amazon_dataset_loader_path() -> None:
    rows, mode = load_dataset_samples(dataset="amazon", seed=42)
    assert len(rows) >= 20
    assert mode == "local_jsonl"


def test_quantum_backend_path_runs() -> None:
    metrics = run_real_experiment(dataset="yelp", seed=42, backend="sim_quantum_statevector", variant="V3")
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0
    assert metrics["train_loss_final"] > 0.0
    assert metrics["eval_loss"] > 0.0


def test_v4_quantum_backend_path_runs() -> None:
    metrics = run_real_experiment(dataset="yelp", seed=42, backend="sim_quantum_statevector", variant="V4")
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0
    assert metrics["train_loss_final"] > 0.0
    assert metrics["eval_loss"] > 0.0


def test_v4b_quantum_backend_path_runs() -> None:
    metrics = run_real_experiment(dataset="yelp", seed=42, backend="sim_quantum_statevector", variant="V4b")
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0
    assert metrics["train_loss_final"] > 0.0
    assert metrics["eval_loss"] > 0.0


def test_quantum_backend_repeated_runs_are_stable_for_same_inputs() -> None:
    metrics_a = run_real_experiment(dataset="yelp", seed=42, backend="sim_quantum_statevector", variant="V3")
    metrics_b = run_real_experiment(dataset="yelp", seed=42, backend="sim_quantum_statevector", variant="V3")
    assert metrics_a["accuracy"] == metrics_b["accuracy"]
    assert metrics_a["f1"] == metrics_b["f1"]
    assert metrics_a["train_loss_final"] == metrics_b["train_loss_final"]
    assert metrics_a["eval_loss"] == metrics_b["eval_loss"]


def test_qiskit_aer_backend_path_runs_if_available() -> None:
    if not importlib.util.find_spec("qiskit_aer"):
        return
    metrics = run_real_experiment(dataset="yelp", seed=42, backend="sim_qiskit_aer", variant="V3")
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0


def test_limit_remote_samples_balances_classes() -> None:
    rows, _ = load_dataset_samples(dataset="yelp", seed=42)
    subset = limit_remote_samples(rows, max_samples=12)
    assert len(subset) == 12
    assert sum(1 for _, label in subset if label == 1) == 6
    assert sum(1 for _, label in subset if label == 0) == 6


def test_collect_quandela_scores_skips_runtime_errors(monkeypatch) -> None:
    calls = iter([0.3, RuntimeError("blocked"), 0.7])

    def fake_score(*args, **kwargs):
        value = next(calls)
        if isinstance(value, Exception):
            raise value
        return value

    monkeypatch.setattr("qrope.run.quandela_remote_score", fake_score)
    labels, scores, skipped = collect_quandela_scores(
        rows=[("a", 1), ("b", 0), ("c", 1)],
        seed=42,
        variant="V3",
        platform_name="sim:slos",
    )
    assert labels == [1, 1]
    assert scores == [0.3, 0.7]
    assert skipped == 1


def test_stratified_calibration_split_keeps_both_classes() -> None:
    rows = [(f"neg-{idx}", 0) for idx in range(8)] + [(f"pos-{idx}", 1) for idx in range(8)]
    subtrain, validation = stratified_calibration_split(rows)
    assert len(subtrain) + len(validation) == len(rows)
    assert sum(1 for _, label in validation if label == 0) >= 1
    assert sum(1 for _, label in validation if label == 1) >= 1
    assert sum(1 for _, label in subtrain if label == 0) >= 1
    assert sum(1 for _, label in subtrain if label == 1) >= 1


def test_calibrate_threshold_prefers_validation_rule_with_low_drift() -> None:
    scores = [0.15, 0.30, 0.45, 0.60, 0.72, 0.84]
    labels = [0, 0, 0, 1, 1, 1]
    threshold = calibrate_threshold(scores, labels)
    preds = [1 if score >= threshold else 0 for score in scores]
    assert 0.45 <= threshold <= 0.60
    assert compute_macro_f1_binary(labels, preds) >= 0.8
    assert compute_balanced_accuracy(labels, preds) >= 0.8


def test_v4_quantum_backend_uses_stable_robust_calibration() -> None:
    metrics_a = run_real_experiment(dataset="imdb", seed=123, backend="sim_quantum_statevector", variant="V4")
    metrics_b = run_real_experiment(dataset="imdb", seed=123, backend="sim_quantum_statevector", variant="V4")
    assert metrics_a["accuracy"] == metrics_b["accuracy"]
    assert metrics_a["f1"] == metrics_b["f1"]
    assert metrics_a["train_loss_final"] == metrics_b["train_loss_final"]
    assert metrics_a["eval_loss"] == metrics_b["eval_loss"]


def test_quantum_backend_supports_q2_readout() -> None:
    metrics = run_real_experiment(
        dataset="yelp",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V3",
        local_readout="q2",
    )
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0
    assert metrics["data_mode"].endswith("readout_q2+mix_mix_v0")


def test_quantum_backend_supports_parity_readout() -> None:
    metrics = run_real_experiment(
        dataset="yelp",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V3",
        local_readout="parity",
    )
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0
    assert metrics["data_mode"].endswith("readout_parity+mix_mix_v0")


def test_quantum_backend_supports_mixing_preset() -> None:
    metrics = run_real_experiment(
        dataset="yelp",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V3",
        local_readout="parity",
        local_mixing_preset="mix_v1",
    )
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0
    assert metrics["data_mode"].endswith("readout_parity+mix_mix_v1")


def test_quantum_backend_supports_interference_tail_preset() -> None:
    metrics = run_real_experiment(
        dataset="yelp",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V3",
        local_readout="parity",
        local_mixing_preset="mix_it1",
    )
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0
    assert metrics["data_mode"].endswith("readout_parity+mix_mix_it1")


def test_synthetic_offset_binary_loader_path() -> None:
    rows, mode = load_dataset_samples(dataset="synthetic_offset_binary", seed=42)
    assert len(rows) == 512
    assert mode == "synthetic_offset_binary"


def test_synthetic_sector_parity_binary_loader_path() -> None:
    rows, mode = load_dataset_samples(dataset="synthetic_sector_parity_binary", seed=42)
    assert len(rows) == 512
    assert mode == "synthetic_sector_parity_binary"


def test_synthetic_chart_transition_token_invariant_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_chart_transition_token_invariant_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_chart_transition_invariant",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_chart_transition_token_invariant_response+readout_relational_witness_chart_transition_invariant+head_linear"
    )
    assert diagnostics["latent_target_invariance_pass"] is True
    assert diagnostics["latent_target_max_abs_delta"] == 0.0
    assert diagnostics["latent_render_pair_count"] > 0
    assert diagnostics["token_view_balance_pass"] is True


def test_chart_transition_invariant_control_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_chart_transition_token_invariant_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_additive_regressor",
    )
    assert metrics["data_mode"].startswith(
        "synthetic_chart_transition_token_invariant_response+readout_symbolic_transition_additive_regressor+head_linear"
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["token_identity_absent"] is True
    assert diagnostics["transition_family_only"] is True


def test_synthetic_chart_transition_orbit_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_chart_transition_orbit_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_chart_transition_orbit_response+readout_relational_witness_transition_orbit+head_linear"
    )
    assert diagnostics["orbit_target_invariance_pass"] is True
    assert diagnostics["orbit_target_max_abs_delta"] == 0.0
    assert diagnostics["orbit_canonical_balance_pass"] is True


def test_symbolic_insufficiency_witness_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_transition_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_symbolic_insufficiency",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith("synthetic_symbolic_insufficiency_transition_response")
    assert diagnostics["coarse_state_null_pass"] is True
    assert diagnostics["within_state_variation_pass"] is True
    assert diagnostics["latent_path_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True


def test_symbolic_insufficiency_symbolic_control_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_transition_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_symbolic_insufficiency_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_symbolic_control_v2_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_transition_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_symbolic_insufficiency_regressor_v2",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_symbolic_control_atlas_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_transition_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_symbolic_insufficiency_regressor_atlas",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["atlas_chart_count_frozen_pass"] is True
    assert diagnostics["atlas_chart_rule_global_pass"] is True
    assert diagnostics["atlas_hidden_lookup_absent_pass"] is True
    assert diagnostics["allowed_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_symbolic_control_residual_atlas_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_transition_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_symbolic_insufficiency_regressor_residual_atlas",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["atlas_chart_count_frozen_pass"] is True
    assert diagnostics["atlas_chart_rule_global_pass"] is True
    assert diagnostics["atlas_hidden_lookup_absent_pass"] is True
    assert diagnostics["residual_transition_family_frozen_pass"] is True
    assert diagnostics["residual_transition_directionality_frozen_pass"] is True
    assert diagnostics["residual_transition_hidden_lookup_absent_pass"] is True
    assert diagnostics["allowed_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_symbolic_control_dual_atlas_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_transition_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["source_atlas_chart_count_frozen_pass"] is True
    assert diagnostics["destination_atlas_chart_count_frozen_pass"] is True
    assert diagnostics["atlas_chart_rule_global_pass"] is True
    assert diagnostics["atlas_hidden_lookup_absent_pass"] is True
    assert diagnostics["dual_atlas_coupling_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_hidden_lookup_absent_pass"] is True
    assert diagnostics["allowed_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_symbolic_control_dual_atlas_residual_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_transition_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_residual",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["source_atlas_chart_count_frozen_pass"] is True
    assert diagnostics["destination_atlas_chart_count_frozen_pass"] is True
    assert diagnostics["atlas_chart_rule_global_pass"] is True
    assert diagnostics["atlas_hidden_lookup_absent_pass"] is True
    assert diagnostics["dual_atlas_coupling_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_residual_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_hidden_lookup_absent_pass"] is True
    assert diagnostics["allowed_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_symbolic_control_dual_atlas_bilinear_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_transition_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_bilinear",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["source_atlas_chart_count_frozen_pass"] is True
    assert diagnostics["destination_atlas_chart_count_frozen_pass"] is True
    assert diagnostics["atlas_chart_rule_global_pass"] is True
    assert diagnostics["atlas_hidden_lookup_absent_pass"] is True
    assert diagnostics["dual_atlas_coupling_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_residual_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_bilinear_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_hidden_lookup_absent_pass"] is True
    assert diagnostics["allowed_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_symbolic_control_dual_atlas_transition_residual_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_transition_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_residual",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["source_atlas_chart_count_frozen_pass"] is True
    assert diagnostics["destination_atlas_chart_count_frozen_pass"] is True
    assert diagnostics["atlas_chart_rule_global_pass"] is True
    assert diagnostics["atlas_hidden_lookup_absent_pass"] is True
    assert diagnostics["dual_atlas_coupling_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_residual_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_bilinear_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_residual_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_hidden_lookup_absent_pass"] is True
    assert diagnostics["allowed_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_symbolic_control_dual_atlas_transition_bilinear_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_transition_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_bilinear",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["source_atlas_chart_count_frozen_pass"] is True
    assert diagnostics["destination_atlas_chart_count_frozen_pass"] is True
    assert diagnostics["atlas_chart_rule_global_pass"] is True
    assert diagnostics["atlas_hidden_lookup_absent_pass"] is True
    assert diagnostics["dual_atlas_coupling_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_residual_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_bilinear_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_residual_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_bilinear_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_hidden_lookup_absent_pass"] is True
    assert diagnostics["allowed_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_symbolic_control_dual_atlas_transition_bilinear_plus_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_transition_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_bilinear_plus",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["source_atlas_chart_count_frozen_pass"] is True
    assert diagnostics["destination_atlas_chart_count_frozen_pass"] is True
    assert diagnostics["atlas_chart_rule_global_pass"] is True
    assert diagnostics["atlas_hidden_lookup_absent_pass"] is True
    assert diagnostics["dual_atlas_coupling_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_residual_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_bilinear_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_residual_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_bilinear_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_bilinear_plus_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_hidden_lookup_absent_pass"] is True
    assert diagnostics["allowed_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_symbolic_control_dual_atlas_transition_cubic_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_transition_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_cubic",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["source_atlas_chart_count_frozen_pass"] is True
    assert diagnostics["destination_atlas_chart_count_frozen_pass"] is True
    assert diagnostics["atlas_chart_rule_global_pass"] is True
    assert diagnostics["atlas_hidden_lookup_absent_pass"] is True
    assert diagnostics["dual_atlas_coupling_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_residual_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_bilinear_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_residual_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_bilinear_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_bilinear_plus_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_cubic_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_hidden_lookup_absent_pass"] is True
    assert diagnostics["allowed_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_symbolic_control_dual_atlas_transition_cubic_plus_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_transition_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_cubic_plus",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["source_atlas_chart_count_frozen_pass"] is True
    assert diagnostics["destination_atlas_chart_count_frozen_pass"] is True
    assert diagnostics["atlas_chart_rule_global_pass"] is True
    assert diagnostics["atlas_hidden_lookup_absent_pass"] is True
    assert diagnostics["dual_atlas_coupling_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_residual_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_bilinear_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_residual_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_bilinear_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_bilinear_plus_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_cubic_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_cubic_plus_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_hidden_lookup_absent_pass"] is True
    assert diagnostics["allowed_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_symbolic_control_dual_atlas_transition_quartic_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_transition_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_quartic",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["source_atlas_chart_count_frozen_pass"] is True
    assert diagnostics["destination_atlas_chart_count_frozen_pass"] is True
    assert diagnostics["atlas_chart_rule_global_pass"] is True
    assert diagnostics["atlas_hidden_lookup_absent_pass"] is True
    assert diagnostics["dual_atlas_coupling_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_residual_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_bilinear_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_residual_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_bilinear_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_bilinear_plus_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_cubic_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_cubic_plus_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_quartic_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_hidden_lookup_absent_pass"] is True
    assert diagnostics["allowed_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_symbolic_control_dual_atlas_transition_quartic_plus_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_transition_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_quartic_plus",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["source_atlas_chart_count_frozen_pass"] is True
    assert diagnostics["destination_atlas_chart_count_frozen_pass"] is True
    assert diagnostics["atlas_chart_rule_global_pass"] is True
    assert diagnostics["atlas_hidden_lookup_absent_pass"] is True
    assert diagnostics["dual_atlas_coupling_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_residual_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_bilinear_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_residual_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_bilinear_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_bilinear_plus_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_cubic_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_cubic_plus_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_quartic_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_quartic_plus_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_hidden_lookup_absent_pass"] is True
    assert diagnostics["allowed_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_symbolic_control_dual_atlas_transition_quintic_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_transition_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_quintic",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["source_atlas_chart_count_frozen_pass"] is True
    assert diagnostics["destination_atlas_chart_count_frozen_pass"] is True
    assert diagnostics["atlas_chart_rule_global_pass"] is True
    assert diagnostics["atlas_hidden_lookup_absent_pass"] is True
    assert diagnostics["dual_atlas_coupling_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_residual_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_bilinear_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_residual_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_bilinear_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_bilinear_plus_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_cubic_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_cubic_plus_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_quartic_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_quartic_plus_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_quintic_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_hidden_lookup_absent_pass"] is True
    assert diagnostics["allowed_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_symbolic_control_dual_atlas_transition_quintic_plus_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_transition_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_quintic_plus",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["source_atlas_chart_count_frozen_pass"] is True
    assert diagnostics["destination_atlas_chart_count_frozen_pass"] is True
    assert diagnostics["atlas_chart_rule_global_pass"] is True
    assert diagnostics["atlas_hidden_lookup_absent_pass"] is True
    assert diagnostics["dual_atlas_coupling_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_residual_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_bilinear_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_residual_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_bilinear_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_bilinear_plus_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_cubic_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_cubic_plus_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_quartic_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_quartic_plus_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_quintic_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_transition_quintic_plus_family_frozen_pass"] is True
    assert diagnostics["dual_atlas_hidden_lookup_absent_pass"] is True
    assert diagnostics["allowed_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_path_witness_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_path_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_symbolic_insufficiency_path",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_symbolic_insufficiency_path_response+readout_relational_witness_symbolic_insufficiency_path+head_linear"
    )
    assert diagnostics["coarse_path_state_null_pass"] is True
    assert diagnostics["within_path_state_variation_pass"] is True
    assert diagnostics["latent_path_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["path_length_balance_pass"] is True
    run_diagnostics = metrics["run_diagnostics"]
    assert run_diagnostics["bounded_feature_audit_pass"] is True
    assert run_diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_path_symbolic_control_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_path_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_symbolic_insufficiency_path_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_path_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_relay_witness_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_relay_binding_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_symbolic_insufficiency_relay_binding",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_symbolic_insufficiency_relay_binding_response+readout_relational_witness_symbolic_insufficiency_relay_binding+head_linear"
    )
    assert diagnostics["coarse_relay_state_null_pass"] is True
    assert diagnostics["within_relay_state_variation_pass"] is True
    assert diagnostics["latent_relay_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["relay_length_balance_pass"] is True
    assert diagnostics["binding_target_nontrivial_pass"] is True
    run_diagnostics = metrics["run_diagnostics"]
    assert run_diagnostics["bounded_feature_audit_pass"] is True
    assert run_diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_relay_symbolic_control_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_relay_binding_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_symbolic_insufficiency_relay_binding_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_relay_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_cascade_reconciliation_witness_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_cascade_reconciliation_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_symbolic_insufficiency_cascade_reconciliation",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_symbolic_insufficiency_cascade_reconciliation_response+readout_relational_witness_symbolic_insufficiency_cascade_reconciliation+head_linear"
    )
    assert diagnostics["coarse_reconciliation_state_null_pass"] is True
    assert diagnostics["within_reconciliation_state_variation_pass"] is True
    assert diagnostics["latent_reconciliation_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["reconciliation_length_balance_pass"] is True
    assert diagnostics["reconciliation_target_nontrivial_pass"] is True
    run_diagnostics = metrics["run_diagnostics"]
    assert run_diagnostics["bounded_feature_audit_pass"] is True
    assert run_diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_cascade_reconciliation_symbolic_control_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_cascade_reconciliation_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_symbolic_insufficiency_cascade_reconciliation_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_reconciliation_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_latch_switch_witness_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_latch_switch_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_symbolic_insufficiency_latch_switch",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_symbolic_insufficiency_latch_switch_response+readout_relational_witness_symbolic_insufficiency_latch_switch+head_linear"
    )
    assert diagnostics["coarse_latch_switch_state_null_pass"] is True
    assert diagnostics["within_latch_switch_state_variation_pass"] is True
    assert diagnostics["latent_latch_switch_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["latch_switch_target_nontrivial_pass"] is True
    run_diagnostics = metrics["run_diagnostics"]
    assert run_diagnostics["bounded_feature_audit_pass"] is True
    assert run_diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_latch_switch_symbolic_control_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_latch_switch_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_symbolic_insufficiency_latch_switch_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_latch_switch_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_staggered_binding_witness_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_staggered_binding_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_symbolic_insufficiency_staggered_binding",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_symbolic_insufficiency_staggered_binding_response+readout_relational_witness_symbolic_insufficiency_staggered_binding+head_linear"
    )
    assert diagnostics["coarse_staggered_state_null_pass"] is True
    assert diagnostics["within_staggered_state_variation_pass"] is True
    assert diagnostics["latent_staggered_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["staggered_length_balance_pass"] is True
    assert diagnostics["binding_target_nontrivial_pass"] is True
    run_diagnostics = metrics["run_diagnostics"]
    assert run_diagnostics["bounded_feature_audit_pass"] is True
    assert run_diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_staggered_binding_symbolic_control_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_staggered_binding_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_symbolic_insufficiency_staggered_binding_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_staggered_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_fanin_consensus_witness_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_fanin_consensus_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_symbolic_insufficiency_fanin_consensus",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_symbolic_insufficiency_fanin_consensus_response+readout_relational_witness_symbolic_insufficiency_fanin_consensus+head_linear"
    )
    assert diagnostics["coarse_fanin_state_null_pass"] is True
    assert diagnostics["within_fanin_state_variation_pass"] is True
    assert diagnostics["latent_fanin_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["fanin_width_balance_pass"] is True
    assert diagnostics["consensus_target_nontrivial_pass"] is True
    run_diagnostics = metrics["run_diagnostics"]
    assert run_diagnostics["bounded_feature_audit_pass"] is True
    assert run_diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_fanin_consensus_symbolic_control_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_fanin_consensus_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_symbolic_insufficiency_fanin_consensus_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_fanin_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_echo_resolution_witness_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_echo_resolution_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_symbolic_insufficiency_echo_resolution",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_symbolic_insufficiency_echo_resolution_response+readout_relational_witness_symbolic_insufficiency_echo_resolution+head_linear"
    )
    assert diagnostics["coarse_echo_state_null_pass"] is True
    assert diagnostics["within_echo_state_variation_pass"] is True
    assert diagnostics["latent_echo_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["echo_length_balance_pass"] is True
    assert diagnostics["resolution_target_nontrivial_pass"] is True
    run_diagnostics = metrics["run_diagnostics"]
    assert run_diagnostics["bounded_feature_audit_pass"] is True
    assert run_diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_echo_resolution_symbolic_control_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_echo_resolution_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_symbolic_insufficiency_echo_resolution_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_echo_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_selector_arbitration_witness_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_selector_arbitration_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_symbolic_insufficiency_selector_arbitration",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_symbolic_insufficiency_selector_arbitration_response+readout_relational_witness_symbolic_insufficiency_selector_arbitration+head_linear"
    )
    assert diagnostics["coarse_selector_state_null_pass"] is True
    assert diagnostics["within_selector_state_variation_pass"] is True
    assert diagnostics["latent_selector_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["selector_length_balance_pass"] is True
    assert diagnostics["selector_target_nontrivial_pass"] is True
    run_diagnostics = metrics["run_diagnostics"]
    assert run_diagnostics["bounded_feature_audit_pass"] is True
    assert run_diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_selector_arbitration_symbolic_control_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_selector_arbitration_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_symbolic_insufficiency_selector_arbitration_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_selector_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_counterfactual_handoff_witness_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_counterfactual_handoff_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_symbolic_insufficiency_counterfactual_handoff",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_symbolic_insufficiency_counterfactual_handoff_response+readout_relational_witness_symbolic_insufficiency_counterfactual_handoff+head_linear"
    )
    assert diagnostics["coarse_handoff_state_null_pass"] is True
    assert diagnostics["within_handoff_state_variation_pass"] is True
    assert diagnostics["latent_handoff_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["handoff_length_balance_pass"] is True
    assert diagnostics["handoff_target_nontrivial_pass"] is True
    run_diagnostics = metrics["run_diagnostics"]
    assert run_diagnostics["bounded_feature_audit_pass"] is True
    assert run_diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_counterfactual_handoff_symbolic_control_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_counterfactual_handoff_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_symbolic_insufficiency_counterfactual_handoff_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_handoff_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_positional_anchor_order_witness_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_anchor_order_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_positional_anchor_order",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_positional_anchor_order_response+readout_relational_witness_positional_anchor_order+head_linear"
    )
    assert diagnostics["coarse_anchor_order_state_null_pass"] is True
    assert diagnostics["within_anchor_order_state_variation_pass"] is True
    assert diagnostics["latent_anchor_order_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["anchor_order_length_balance_pass"] is True
    assert diagnostics["anchor_order_target_nontrivial_pass"] is True
    run_diagnostics = metrics["run_diagnostics"]
    assert run_diagnostics["bounded_feature_audit_pass"] is True
    assert run_diagnostics["forbidden_feature_family_absent_pass"] is True


def test_positional_anchor_order_symbolic_control_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_anchor_order_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_positional_anchor_order_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_anchor_order_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_positional_anchor_distance_witness_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_anchor_distance_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_positional_anchor_distance",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_positional_anchor_distance_response+readout_relational_witness_positional_anchor_distance+head_linear"
    )
    assert diagnostics["coarse_anchor_distance_state_null_pass"] is True
    assert diagnostics["within_anchor_distance_state_variation_pass"] is True
    assert diagnostics["latent_anchor_distance_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["anchor_distance_length_balance_pass"] is True
    assert diagnostics["anchor_distance_target_nontrivial_pass"] is True
    run_diagnostics = metrics["run_diagnostics"]
    assert run_diagnostics["bounded_feature_audit_pass"] is True
    assert run_diagnostics["forbidden_feature_family_absent_pass"] is True


def test_positional_anchor_distance_symbolic_control_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_anchor_distance_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_positional_anchor_distance_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_anchor_distance_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_positional_anchor_span_membership_witness_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_anchor_span_membership_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_positional_anchor_span_membership",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_positional_anchor_span_membership_response+readout_relational_witness_positional_anchor_span_membership+head_linear"
    )
    assert diagnostics["coarse_anchor_span_membership_state_null_pass"] is True
    assert diagnostics["within_anchor_span_membership_state_variation_pass"] is True
    assert diagnostics["latent_anchor_span_membership_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["anchor_span_membership_length_balance_pass"] is True
    assert diagnostics["anchor_span_membership_target_nontrivial_pass"] is True
    run_diagnostics = metrics["run_diagnostics"]
    assert run_diagnostics["bounded_feature_audit_pass"] is True
    assert run_diagnostics["forbidden_feature_family_absent_pass"] is True


def test_positional_anchor_span_membership_symbolic_control_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_anchor_span_membership_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_positional_anchor_span_membership_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_anchor_span_membership_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_positional_anchor_offset_signature_witness_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_anchor_offset_signature_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_positional_anchor_offset_signature",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_positional_anchor_offset_signature_response+readout_relational_witness_positional_anchor_offset_signature+head_linear"
    )
    assert diagnostics["coarse_anchor_offset_signature_state_null_pass"] is True
    assert diagnostics["within_anchor_offset_signature_state_variation_pass"] is True
    assert diagnostics["latent_anchor_offset_signature_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["anchor_offset_signature_length_balance_pass"] is True
    assert diagnostics["anchor_offset_signature_target_nontrivial_pass"] is True
    run_diagnostics = metrics["run_diagnostics"]
    assert run_diagnostics["bounded_feature_audit_pass"] is True
    assert run_diagnostics["forbidden_feature_family_absent_pass"] is True


def test_positional_anchor_offset_signature_symbolic_control_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_anchor_offset_signature_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_positional_anchor_offset_signature_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_anchor_offset_signature_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_positional_anchor_betweenness_witness_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_anchor_betweenness_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_positional_anchor_betweenness",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_positional_anchor_betweenness_response+readout_relational_witness_positional_anchor_betweenness+head_linear"
    )
    assert diagnostics["coarse_anchor_betweenness_state_null_pass"] is True
    assert diagnostics["within_anchor_betweenness_state_variation_pass"] is True
    assert diagnostics["latent_anchor_betweenness_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["anchor_betweenness_length_balance_pass"] is True
    assert diagnostics["anchor_betweenness_target_nontrivial_pass"] is True
    run_diagnostics = metrics["run_diagnostics"]
    assert run_diagnostics["bounded_feature_audit_pass"] is True
    assert run_diagnostics["forbidden_feature_family_absent_pass"] is True


def test_positional_anchor_betweenness_symbolic_control_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_anchor_betweenness_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_positional_anchor_betweenness_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_anchor_betweenness_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_positional_offset_retrieval_witness_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_offset_retrieval_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_positional_offset_retrieval",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_positional_offset_retrieval_response+readout_relational_witness_positional_offset_retrieval+head_linear"
    )
    assert diagnostics["coarse_offset_retrieval_state_null_pass"] is True
    assert diagnostics["within_offset_retrieval_state_variation_pass"] is True
    assert diagnostics["latent_offset_retrieval_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["offset_retrieval_length_balance_pass"] is True
    assert diagnostics["offset_retrieval_target_nontrivial_pass"] is True
    assert diagnostics["distractor_competition_nontrivial_pass"] is True
    run_diagnostics = metrics["run_diagnostics"]
    assert run_diagnostics["bounded_feature_audit_pass"] is True
    assert run_diagnostics["forbidden_offset_retrieval_feature_family_absent_pass"] is True


def test_positional_offset_retrieval_symbolic_control_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_offset_retrieval_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_positional_offset_retrieval_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_offset_retrieval_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_offset_retrieval_feature_family_absent_pass"] is True


def test_positional_key_query_offset_selection_witness_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_key_query_offset_selection_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_positional_key_query_offset_selection",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_positional_key_query_offset_selection_response+readout_relational_witness_positional_key_query_offset_selection+head_linear"
    )
    assert diagnostics["coarse_key_query_selection_state_null_pass"] is True
    assert diagnostics["within_key_query_selection_state_variation_pass"] is True
    assert diagnostics["candidate_set_nontrivial_pass"] is True
    assert diagnostics["target_selection_nontrivial_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["bounded_candidate_count_pass"] is True
    run_diagnostics = metrics["run_diagnostics"]
    assert run_diagnostics["bounded_feature_audit_pass"] is True
    assert run_diagnostics["forbidden_key_query_selection_feature_family_absent_pass"] is True


def test_positional_key_query_offset_selection_symbolic_control_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_key_query_offset_selection_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_positional_key_query_offset_selection_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_key_query_selection_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_key_query_selection_feature_family_absent_pass"] is True


def test_positional_dual_anchor_offset_consensus_witness_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_dual_anchor_offset_consensus_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_positional_dual_anchor_offset_consensus",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_positional_dual_anchor_offset_consensus_response+readout_relational_witness_positional_dual_anchor_offset_consensus+head_linear"
    )
    assert diagnostics["coarse_dual_anchor_consensus_state_null_pass"] is True
    assert diagnostics["within_dual_anchor_consensus_state_variation_pass"] is True
    assert diagnostics["candidate_set_nontrivial_pass"] is True
    assert diagnostics["dual_anchor_target_nontrivial_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["bounded_candidate_count_pass"] is True
    assert diagnostics["dual_anchor_noncollapse_pass"] is True
    run_diagnostics = metrics["run_diagnostics"]
    assert run_diagnostics["bounded_feature_audit_pass"] is True
    assert run_diagnostics["forbidden_dual_anchor_consensus_feature_family_absent_pass"] is True


def test_positional_dual_anchor_offset_consensus_symbolic_control_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_dual_anchor_offset_consensus_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_positional_dual_anchor_offset_consensus_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_dual_anchor_consensus_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_dual_anchor_consensus_feature_family_absent_pass"] is True


def test_positional_variable_cardinality_offset_selection_witness_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_variable_cardinality_offset_selection_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_positional_variable_cardinality_offset_selection",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_positional_variable_cardinality_offset_selection_response+readout_relational_witness_positional_variable_cardinality_offset_selection+head_linear"
    )
    assert diagnostics["coarse_variable_cardinality_state_null_pass"] is True
    assert diagnostics["within_variable_cardinality_state_variation_pass"] is True
    assert diagnostics["candidate_count_range_nontrivial_pass"] is True
    assert diagnostics["variable_cardinality_target_nontrivial_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["bounded_candidate_count_pass"] is True
    assert diagnostics["distractor_insertion_nontrivial_pass"] is True
    assert diagnostics["cross_count_target_stability_pass"] is True
    run_diagnostics = metrics["run_diagnostics"]
    assert run_diagnostics["bounded_feature_audit_pass"] is True
    assert run_diagnostics["forbidden_variable_cardinality_feature_family_absent_pass"] is True


def test_positional_variable_cardinality_offset_selection_symbolic_control_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_variable_cardinality_offset_selection_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_positional_variable_cardinality_offset_selection_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_variable_cardinality_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_variable_cardinality_feature_family_absent_pass"] is True
    assert diagnostics["single_symbolic_family_across_counts_pass"] is True


def test_positional_content_gated_offset_selection_witness_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_content_gated_offset_selection_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_positional_content_gated_offset_selection",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_positional_content_gated_offset_selection_response+readout_relational_witness_positional_content_gated_offset_selection+head_linear"
    )
    assert diagnostics["coarse_position_content_state_null_pass"] is True
    assert diagnostics["within_position_content_state_variation_pass"] is True
    assert diagnostics["content_only_null_pass"] is True
    assert diagnostics["position_only_null_pass"] is True
    assert diagnostics["joint_target_nontrivial_pass"] is True
    assert diagnostics["candidate_set_nontrivial_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["bounded_content_class_pass"] is True
    assert diagnostics["bounded_candidate_count_pass"] is True
    assert diagnostics["joint_noncollapse_pass"] is True
    run_diagnostics = metrics["run_diagnostics"]
    assert run_diagnostics["bounded_feature_audit_pass"] is True
    assert run_diagnostics["forbidden_position_content_feature_family_absent_pass"] is True


def test_positional_content_gated_offset_selection_symbolic_control_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_content_gated_offset_selection_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_positional_content_gated_offset_selection_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_position_content_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_position_content_feature_family_absent_pass"] is True
    assert diagnostics["single_symbolic_family_across_candidate_family_pass"] is True


def test_positional_content_alias_disambiguation_witness_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_content_alias_disambiguation_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_positional_content_alias_disambiguation",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_positional_content_alias_disambiguation_response+readout_relational_witness_positional_content_alias_disambiguation+head_linear"
    )
    assert diagnostics["coarse_content_alias_state_null_pass"] is True
    assert diagnostics["within_content_alias_state_variation_pass"] is True
    assert diagnostics["alias_pressure_nontrivial_pass"] is True
    assert diagnostics["content_only_null_pass"] is True
    assert diagnostics["position_only_null_pass"] is True
    assert diagnostics["joint_target_nontrivial_pass"] is True
    assert diagnostics["candidate_set_nontrivial_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["bounded_content_class_pass"] is True
    assert diagnostics["bounded_candidate_count_pass"] is True
    assert diagnostics["alias_slot_rotation_pass"] is True
    assert diagnostics["joint_noncollapse_pass"] is True
    run_diagnostics = metrics["run_diagnostics"]
    assert run_diagnostics["bounded_feature_audit_pass"] is True
    assert run_diagnostics["forbidden_content_alias_feature_family_absent_pass"] is True


def test_positional_content_alias_disambiguation_symbolic_control_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_content_alias_disambiguation_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_positional_content_alias_disambiguation_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_content_alias_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_content_alias_feature_family_absent_pass"] is True
    assert diagnostics["single_symbolic_family_across_alias_patterns_pass"] is True


def test_positional_reference_revision_selection_witness_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_reference_revision_selection_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_positional_reference_revision_selection",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_positional_reference_revision_selection_response+readout_relational_witness_positional_reference_revision_selection+head_linear"
    )
    assert diagnostics["coarse_reference_revision_state_null_pass"] is True
    assert diagnostics["within_reference_revision_state_variation_pass"] is True
    assert diagnostics["stale_current_competition_nontrivial_pass"] is True
    assert diagnostics["stale_only_null_pass"] is True
    assert diagnostics["current_only_null_pass"] is True
    assert diagnostics["revision_target_nontrivial_pass"] is True
    assert diagnostics["candidate_set_nontrivial_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["bounded_candidate_count_pass"] is True
    assert diagnostics["revision_noncollapse_pass"] is True
    run_diagnostics = metrics["run_diagnostics"]
    assert run_diagnostics["bounded_feature_audit_pass"] is True
    assert run_diagnostics["forbidden_reference_revision_feature_family_absent_pass"] is True


def test_positional_reference_revision_selection_symbolic_control_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_reference_revision_selection_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_positional_reference_revision_selection_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_reference_revision_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_reference_revision_feature_family_absent_pass"] is True
    assert diagnostics["single_symbolic_family_across_revision_patterns_pass"] is True


def test_positional_exception_conditioned_reference_selection_witness_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_exception_conditioned_reference_selection_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_positional_exception_conditioned_reference_selection",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_positional_exception_conditioned_reference_selection_response+readout_relational_witness_positional_exception_conditioned_reference_selection+head_linear"
    )
    assert diagnostics["coarse_exception_arbitration_state_null_pass"] is True
    assert diagnostics["within_exception_arbitration_state_variation_pass"] is True
    assert diagnostics["base_rule_nontrivial_pass"] is True
    assert diagnostics["exception_trigger_nontrivial_pass"] is True
    assert diagnostics["base_only_null_pass"] is True
    assert diagnostics["exception_only_null_pass"] is True
    assert diagnostics["final_target_nontrivial_pass"] is True
    assert diagnostics["candidate_set_nontrivial_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["bounded_candidate_count_pass"] is True
    assert diagnostics["exception_noncollapse_pass"] is True
    run_diagnostics = metrics["run_diagnostics"]
    assert run_diagnostics["bounded_feature_audit_pass"] is True
    assert run_diagnostics["forbidden_exception_arbitration_feature_family_absent_pass"] is True


def test_positional_exception_conditioned_reference_selection_symbolic_control_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_exception_conditioned_reference_selection_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_positional_exception_conditioned_reference_selection_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_exception_arbitration_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_exception_arbitration_feature_family_absent_pass"] is True
    assert diagnostics["single_symbolic_family_across_exception_patterns_pass"] is True


def test_positional_shared_memory_multi_query_selection_witness_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_shared_memory_multi_query_selection_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_positional_shared_memory_multi_query_selection",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_positional_shared_memory_multi_query_selection_response+readout_relational_witness_positional_shared_memory_multi_query_selection+head_linear"
    )
    assert diagnostics["coarse_shared_memory_state_null_pass"] is True
    assert diagnostics["within_shared_memory_state_variation_pass"] is True
    assert diagnostics["query_pair_nontrivial_pass"] is True
    assert diagnostics["query_one_only_null_pass"] is True
    assert diagnostics["query_two_only_null_pass"] is True
    assert diagnostics["joint_query_target_nontrivial_pass"] is True
    assert diagnostics["shared_candidate_set_nontrivial_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["bounded_candidate_count_pass"] is True
    assert diagnostics["bounded_query_count_pass"] is True
    assert diagnostics["cross_query_noncollapse_pass"] is True
    assert diagnostics["shared_memory_reuse_pass"] is True
    run_diagnostics = metrics["run_diagnostics"]
    assert run_diagnostics["bounded_feature_audit_pass"] is True
    assert run_diagnostics["forbidden_shared_memory_multi_query_feature_family_absent_pass"] is True


def test_positional_shared_memory_multi_query_selection_symbolic_control_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_shared_memory_multi_query_selection_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_positional_shared_memory_multi_query_selection_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_shared_memory_multi_query_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_shared_memory_multi_query_feature_family_absent_pass"] is True
    assert diagnostics["single_symbolic_family_across_query_positions_pass"] is True


def test_positional_intermediate_pointer_selection_witness_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_intermediate_pointer_selection_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_positional_intermediate_pointer_selection",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_positional_intermediate_pointer_selection_response+readout_relational_witness_positional_intermediate_pointer_selection+head_linear"
    )
    assert diagnostics["coarse_multi_hop_state_null_pass"] is True
    assert diagnostics["within_multi_hop_state_variation_pass"] is True
    assert diagnostics["first_hop_nontrivial_pass"] is True
    assert diagnostics["second_hop_nontrivial_pass"] is True
    assert diagnostics["direct_target_null_pass"] is True
    assert diagnostics["intermediate_criticality_pass"] is True
    assert diagnostics["candidate_set_nontrivial_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["bounded_candidate_count_pass"] is True
    assert diagnostics["multi_hop_noncollapse_pass"] is True
    run_diagnostics = metrics["run_diagnostics"]
    assert run_diagnostics["bounded_feature_audit_pass"] is True
    assert run_diagnostics["forbidden_multi_hop_feature_family_absent_pass"] is True


def test_positional_intermediate_pointer_selection_symbolic_control_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_positional_intermediate_pointer_selection_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_positional_intermediate_pointer_selection_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_multi_hop_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_multi_hop_feature_family_absent_pass"] is True
    assert diagnostics["single_symbolic_family_across_candidate_counts_pass"] is True


def test_symbolic_insufficiency_loop_witness_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_loop_closure_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_symbolic_insufficiency_loop",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_symbolic_insufficiency_loop_closure_response+readout_relational_witness_symbolic_insufficiency_loop+head_linear"
    )
    assert diagnostics["coarse_loop_state_null_pass"] is True
    assert diagnostics["within_loop_state_variation_pass"] is True
    assert diagnostics["latent_loop_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["loop_length_balance_pass"] is True
    assert diagnostics["closure_target_nontrivial_pass"] is True
    run_diagnostics = metrics["run_diagnostics"]
    assert run_diagnostics["bounded_feature_audit_pass"] is True
    assert run_diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_loop_symbolic_control_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_loop_closure_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_symbolic_insufficiency_loop_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_loop_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_fork_join_witness_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_fork_join_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_symbolic_insufficiency_fork_join",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_symbolic_insufficiency_fork_join_response+readout_relational_witness_symbolic_insufficiency_fork_join+head_linear"
    )
    assert diagnostics["coarse_fork_state_null_pass"] is True
    assert diagnostics["within_fork_state_variation_pass"] is True
    assert diagnostics["latent_fork_diversity_pass"] is True
    assert diagnostics["branch_balance_pass"] is True
    assert diagnostics["rejoin_target_nontrivial_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    run_diagnostics = metrics["run_diagnostics"]
    assert run_diagnostics["bounded_feature_audit_pass"] is True
    assert run_diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_fork_join_symbolic_control_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_fork_join_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_symbolic_insufficiency_fork_join_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_fork_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_braid_witness_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_braid_crossing_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_symbolic_insufficiency_braid",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_symbolic_insufficiency_braid_crossing_response+readout_relational_witness_symbolic_insufficiency_braid+head_linear"
    )
    assert diagnostics["coarse_braid_state_null_pass"] is True
    assert diagnostics["within_braid_state_variation_pass"] is True
    assert diagnostics["latent_braid_diversity_pass"] is True
    assert diagnostics["crossing_target_nontrivial_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["channel_balance_pass"] is True
    run_diagnostics = metrics["run_diagnostics"]
    assert run_diagnostics["bounded_feature_audit_pass"] is True
    assert run_diagnostics["forbidden_braid_feature_family_absent_pass"] is True


def test_symbolic_insufficiency_braid_symbolic_control_freezes_basis() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_symbolic_insufficiency_braid_crossing_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_symbolic_insufficiency_braid_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["allowed_braid_symbolic_basis_frozen_pass"] is True
    assert diagnostics["forbidden_braid_feature_family_absent_pass"] is True


def test_transition_orbit_additive_control_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_chart_transition_orbit_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_orbit_additive_regressor",
    )
    assert metrics["data_mode"].startswith(
        "synthetic_chart_transition_orbit_response+readout_symbolic_transition_orbit_additive_regressor+head_linear"
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["token_identity_absent"] is True
    assert diagnostics["orbit_canonical_only"] is True


def test_transition_orbit_permuted_control_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_chart_transition_orbit_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_orbit_permuted_regressor",
    )
    assert metrics["data_mode"].startswith(
        "synthetic_chart_transition_orbit_response+readout_symbolic_transition_orbit_permuted_regressor+head_linear"
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["token_identity_absent"] is True
    assert diagnostics["orbit_canonical_only"] is True
    assert diagnostics["transition_table_permuted"] is True


def test_transition_orbit_rank_band_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_rank_band_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_rank",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_transition_orbit_rank_band_response+readout_relational_witness_transition_orbit_rank+head_linear"
    )
    assert diagnostics["coarse_rank_lookup_near_null_pass"] is True
    assert diagnostics["within_state_rank_band_count_min"] >= 3
    assert diagnostics["rank_band_balance_pass"] is True


def test_transition_orbit_rank_lookup_control_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_rank_band_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_orbit_rank_lookup",
    )
    assert metrics["data_mode"].startswith(
        "synthetic_transition_orbit_rank_band_response+readout_symbolic_transition_orbit_rank_lookup+head_linear"
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["token_identity_absent"] is True
    assert diagnostics["coarse_state_only"] is True


def test_transition_orbit_pairwise_order_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_pairwise_order_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_order",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_transition_orbit_pairwise_order_binary+readout_relational_witness_transition_orbit_order+head_linear"
    )
    assert diagnostics["coarse_order_lookup_near_null_pass"] is True
    assert diagnostics["within_state_pair_count_min"] >= 2
    assert diagnostics["pair_label_balance_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True


def test_transition_orbit_pairwise_order_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_pairwise_order_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_order_lookup",
    )
    assert metrics["data_mode"].startswith(
        "synthetic_transition_orbit_pairwise_order_binary+readout_symbolic_transition_order_lookup+head_linear"
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["token_identity_absent"] is True
    assert diagnostics["coarse_state_only"] is True


def test_transition_orbit_listwise_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_listwise_ranking",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_listwise",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_transition_orbit_listwise_ranking+readout_relational_witness_transition_orbit_listwise+head_linear"
    )
    assert diagnostics["coarse_list_lookup_near_null_pass"] is True
    assert diagnostics["within_state_list_count_min"] >= 2
    assert diagnostics["rank_position_balance_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True


def test_transition_orbit_listwise_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_listwise_ranking",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_list_lookup",
    )
    assert metrics["data_mode"].startswith(
        "synthetic_transition_orbit_listwise_ranking+readout_symbolic_transition_list_lookup+head_linear"
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["coarse_state_only"] is True


def test_transition_orbit_order_margin_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_order_margin_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_order_margin",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_transition_orbit_order_margin_response+readout_relational_witness_transition_orbit_order_margin+head_linear"
    )
    assert diagnostics["coarse_margin_lookup_near_null_pass"] is True
    assert diagnostics["within_state_margin_variation_pass"] is True
    assert diagnostics["top1_only_shortcut_absent"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert metrics["run_diagnostics"]["margin_target_mode"] == "top2_gap"


def test_transition_orbit_order_margin_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_order_margin_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_margin_lookup",
    )
    assert metrics["data_mode"].startswith(
        "synthetic_transition_orbit_order_margin_response+readout_symbolic_transition_margin_lookup+head_linear"
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["margin_target_mode"] == "top2_gap"
    assert diagnostics["coarse_state_only"] is True


def test_transition_orbit_signed_margin_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_signed_margin_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_signed_margin",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_transition_orbit_signed_margin_response+readout_relational_witness_transition_orbit_signed_margin+head_linear"
    )
    assert diagnostics["coarse_signed_margin_lookup_near_null_pass"] is True
    assert diagnostics["within_state_signed_margin_variation_pass"] is True
    assert diagnostics["signed_margin_balance_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert metrics["run_diagnostics"]["margin_target_mode"] == "signed_top2_gap"


def test_transition_orbit_signed_margin_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_signed_margin_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_signed_margin_lookup",
    )
    assert metrics["data_mode"].startswith(
        "synthetic_transition_orbit_signed_margin_response+readout_symbolic_transition_signed_margin_lookup+head_linear"
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["margin_target_mode"] == "signed_top2_gap"
    assert diagnostics["coarse_state_only"] is True


def test_transition_orbit_sign_only_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_sign_only_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_sign_only",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_transition_orbit_sign_only_binary+readout_relational_witness_transition_orbit_sign_only+head_linear"
    )
    assert diagnostics["coarse_sign_lookup_near_null_pass"] is True
    assert diagnostics["within_state_sign_variation_pass"] is True
    assert diagnostics["sign_label_balance_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert metrics["run_diagnostics"]["sign_target_mode"] == "top2_direction_only"


def test_transition_orbit_sign_only_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_sign_only_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_sign_lookup",
    )
    assert metrics["data_mode"].startswith(
        "synthetic_transition_orbit_sign_only_binary+readout_symbolic_transition_sign_lookup+head_linear"
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["sign_target_mode"] == "top2_direction_only"
    assert diagnostics["coarse_state_only"] is True


def test_transition_orbit_sign_consistency_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_sign_consistency_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_sign_consistency",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_transition_orbit_sign_consistency_binary+readout_relational_witness_transition_orbit_sign_consistency+head_linear"
    )
    assert diagnostics["coarse_consistency_lookup_near_null_pass"] is True
    assert diagnostics["within_state_consistency_variation_pass"] is True
    assert diagnostics["paired_context_diversity_pass"] is True
    assert diagnostics["consistency_label_balance_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert metrics["run_diagnostics"]["consistency_target_mode"] == "paired_sign_agreement"


def test_transition_orbit_sign_consistency_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_sign_consistency_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_consistency_lookup",
    )
    assert metrics["data_mode"].startswith(
        "synthetic_transition_orbit_sign_consistency_binary+readout_symbolic_transition_consistency_lookup+head_linear"
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["consistency_target_mode"] == "paired_sign_agreement"
    assert diagnostics["coarse_state_only"] is True


def test_transition_orbit_sign_flip_contrast_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_sign_flip_contrast_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_sign_flip_contrast",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_transition_orbit_sign_flip_contrast_binary+readout_relational_witness_transition_orbit_sign_flip_contrast+head_linear"
    )
    assert diagnostics["coarse_flip_lookup_near_null_pass"] is True
    assert diagnostics["within_state_flip_variation_pass"] is True
    assert diagnostics["paired_context_diversity_pass"] is True
    assert diagnostics["flip_label_balance_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert metrics["run_diagnostics"]["consistency_target_mode"] == "paired_sign_flip_hold"


def test_transition_orbit_sign_flip_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_sign_flip_contrast_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_flip_lookup",
    )
    assert metrics["data_mode"].startswith(
        "synthetic_transition_orbit_sign_flip_contrast_binary+readout_symbolic_transition_flip_lookup+head_linear"
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["consistency_target_mode"] == "paired_sign_flip_hold"
    assert diagnostics["coarse_state_only"] is True


def test_transition_orbit_asymmetric_sign_localization_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_asymmetric_sign_localization_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_asymmetric_sign_localization",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_transition_orbit_asymmetric_sign_localization_binary+readout_relational_witness_transition_orbit_asymmetric_sign_localization+head_linear"
    )
    assert diagnostics["coarse_localization_lookup_near_null_pass"] is True
    assert diagnostics["within_state_localization_variation_pass"] is True
    assert diagnostics["paired_channel_diversity_pass"] is True
    assert diagnostics["localization_label_balance_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert metrics["run_diagnostics"]["localization_target_mode"] == "asymmetric_sign_channel"


def test_transition_orbit_asymmetric_sign_localization_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_asymmetric_sign_localization_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_localization_lookup",
    )
    assert metrics["data_mode"].startswith(
        "synthetic_transition_orbit_asymmetric_sign_localization_binary+readout_symbolic_transition_localization_lookup+head_linear"
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["localization_target_mode"] == "asymmetric_sign_channel"
    assert diagnostics["coarse_state_only"] is True


def test_transition_orbit_channel_advantage_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_channel_advantage_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_channel_advantage",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_transition_orbit_channel_advantage_response+readout_relational_witness_transition_orbit_channel_advantage+head_linear"
    )
    assert diagnostics["coarse_channel_advantage_lookup_near_null_pass"] is True
    assert diagnostics["within_state_channel_advantage_variation_pass"] is True
    assert diagnostics["paired_channel_diversity_pass"] is True
    assert diagnostics["channel_advantage_balance_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert metrics["run_diagnostics"]["channel_advantage_target_mode"] == "signed_left_minus_right_effect"
    assert metrics["extra_metrics"]["mae"] >= 0.0


def test_transition_orbit_channel_advantage_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_channel_advantage_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_channel_lookup_regressor",
    )
    assert metrics["data_mode"].startswith(
        "synthetic_transition_orbit_channel_advantage_response+readout_symbolic_transition_channel_lookup_regressor+head_linear"
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["extra_metrics"]["mae"] >= 0.0
    assert diagnostics["channel_advantage_target_mode"] == "signed_left_minus_right_effect"


def test_transition_orbit_channel_order_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_channel_order_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_channel_order",
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert metrics["data_mode"].startswith(
        "synthetic_transition_orbit_channel_order_response+readout_relational_witness_transition_orbit_channel_order+head_linear"
    )
    assert diagnostics["coarse_channel_order_lookup_near_null_pass"] is True
    assert diagnostics["within_state_channel_order_variation_pass"] is True
    assert diagnostics["paired_channel_diversity_pass"] is True
    assert diagnostics["channel_order_balance_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert metrics["run_diagnostics"]["channel_order_target_mode"] == "binary_left_vs_right_order"
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0


def test_transition_orbit_channel_order_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_channel_order_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_channel_order_lookup",
    )
    assert metrics["data_mode"].startswith(
        "synthetic_transition_orbit_channel_order_response+readout_symbolic_transition_channel_order_lookup+head_linear"
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["channel_order_target_mode"] == "binary_left_vs_right_order"


def test_transition_orbit_slot_invariant_channel_order_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_channel_order_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_channel_order_invariant",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_channel_order_response+readout_relational_witness_transition_orbit_channel_order_invariant+head_linear"
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0
    assert diagnostics["slot_view_balance_pass"] is True
    assert metrics["run_diagnostics"]["channel_order_target_mode"] == "binary_left_vs_right_order"


def test_transition_orbit_slot_invariant_channel_order_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_channel_order_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_channel_order_invariant_lookup",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_channel_order_response+readout_symbolic_transition_channel_order_invariant_lookup+head_linear"
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["channel_order_target_mode"] == "binary_left_vs_right_order"


def test_transition_orbit_slot_invariant_channel_order_margin_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_channel_order_margin_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_channel_order_margin_invariant",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_channel_order_margin_response+readout_relational_witness_transition_orbit_channel_order_margin_invariant+head_linear"
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_margin_lookup_near_null_pass"] is True


def test_transition_orbit_slot_invariant_channel_order_margin_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_channel_order_margin_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_channel_order_margin_invariant_lookup",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_channel_order_margin_response+readout_symbolic_transition_channel_order_margin_invariant_lookup+head_linear"
    )
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0


def test_transition_orbit_slot_invariant_channel_order_topk_margin_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_channel_order_topk_margin_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_channel_order_topk_margin_invariant",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_channel_order_topk_margin_response+readout_relational_witness_transition_orbit_channel_order_topk_margin_invariant+head_linear"
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_margin_lookup_near_null_pass"] is True


def test_transition_orbit_slot_invariant_channel_order_topk_margin_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_channel_order_topk_margin_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_channel_order_topk_margin_invariant_lookup",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_channel_order_topk_margin_response+readout_symbolic_transition_channel_order_topk_margin_invariant_lookup+head_linear"
    )
    assert "mae" in metrics["extra_metrics"]
    assert "rank_correlation" in metrics["extra_metrics"]


def test_transition_orbit_slot_invariant_channel_order_rank_only_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_channel_order_rank_only",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_channel_order_rank_only_invariant",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_channel_order_rank_only+readout_relational_witness_transition_orbit_channel_order_rank_only_invariant+head_linear"
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_rank_lookup_near_null_pass"] is True


def test_transition_orbit_slot_invariant_channel_order_rank_only_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_channel_order_rank_only",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_channel_order_rank_only_invariant_lookup",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_channel_order_rank_only+readout_symbolic_transition_channel_order_rank_only_invariant_lookup+head_linear"
    )
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0


def test_transition_orbit_slot_invariant_channel_order_topk_consistency_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_channel_order_topk_consistency_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_channel_order_topk_consistency_invariant",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_channel_order_topk_consistency_binary+readout_relational_witness_transition_orbit_channel_order_topk_consistency_invariant+head_linear"
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_lookup_near_null_pass"] is True


def test_transition_orbit_slot_invariant_channel_order_topk_consistency_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_channel_order_topk_consistency_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_channel_order_topk_consistency_invariant_lookup",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_channel_order_topk_consistency_binary+readout_symbolic_transition_channel_order_topk_consistency_invariant_lookup+head_linear"
    )
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0


def test_transition_orbit_slot_invariant_channel_order_topk_rank_only_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_channel_order_topk_rank_only",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_channel_order_topk_rank_only_invariant",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_channel_order_topk_rank_only+readout_relational_witness_transition_orbit_channel_order_topk_rank_only_invariant+head_linear"
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_rank_lookup_near_null_pass"] is True


def test_transition_orbit_slot_invariant_channel_order_topk_rank_only_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_channel_order_topk_rank_only",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_channel_order_topk_rank_only_invariant_lookup",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_channel_order_topk_rank_only+readout_symbolic_transition_channel_order_topk_rank_only_invariant_lookup+head_linear"
    )
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0


def test_transition_orbit_slot_invariant_channel_order_topk_preference_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_channel_order_topk_preference_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_channel_order_topk_preference_invariant",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_channel_order_topk_preference_binary+readout_relational_witness_transition_orbit_channel_order_topk_preference_invariant+head_linear"
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_preference_lookup_near_null_pass"] is True


def test_transition_orbit_slot_invariant_channel_order_topk_preference_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_channel_order_topk_preference_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_channel_order_topk_preference_invariant_lookup",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_channel_order_topk_preference_binary+readout_symbolic_transition_channel_order_topk_preference_invariant_lookup+head_linear"
    )
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0


def test_transition_orbit_slot_invariant_topk_pair_margin_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_topk_pair_margin_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_topk_pair_margin_invariant",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_topk_pair_margin_response+readout_relational_witness_transition_orbit_topk_pair_margin_invariant+head_linear"
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_pair_margin_lookup_near_null_pass"] is True


def test_transition_orbit_slot_invariant_topk_pair_margin_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_topk_pair_margin_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_topk_pair_margin_invariant_lookup",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_topk_pair_margin_response+readout_symbolic_transition_topk_pair_margin_invariant_lookup+head_linear"
    )
    assert "mae" in metrics["extra_metrics"]
    assert "rank_correlation" in metrics["extra_metrics"]


def test_transition_orbit_slot_invariant_topk_pair_order_agreement_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_topk_pair_order_agreement_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_topk_pair_order_agreement_invariant",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_topk_pair_order_agreement_binary+readout_relational_witness_transition_orbit_topk_pair_order_agreement_invariant+head_linear"
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_pair_order_lookup_near_null_pass"] is True


def test_transition_orbit_slot_invariant_topk_pair_order_agreement_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_topk_pair_order_agreement_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_topk_pair_order_agreement_invariant_lookup",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_topk_pair_order_agreement_binary+readout_symbolic_transition_topk_pair_order_agreement_invariant_lookup+head_linear"
    )
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0


def test_transition_orbit_slot_invariant_topk_pair_order_signed_consistency_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_consistency_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_topk_pair_order_signed_consistency_invariant",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_consistency_binary+readout_relational_witness_transition_orbit_topk_pair_order_signed_consistency_invariant+head_linear"
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0.0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_pair_signed_consistency_lookup_near_null_pass"] is True
    assert diagnostics["within_state_topk_pair_signed_consistency_variation_pass"] is True
    assert diagnostics["paired_context_diversity_pass"] is True
    assert diagnostics["signed_consistency_label_balance_pass"] is True
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0


def test_transition_orbit_slot_invariant_topk_pair_order_signed_consistency_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_consistency_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_topk_pair_order_signed_consistency_invariant_lookup",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_consistency_binary+readout_symbolic_transition_topk_pair_order_signed_consistency_invariant_lookup+head_linear"
    )
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0


def test_transition_orbit_slot_invariant_topk_pair_order_signed_flip_consistency_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_consistency_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_consistency_invariant",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_consistency_binary+readout_relational_witness_transition_orbit_topk_pair_order_signed_flip_consistency_invariant+head_linear"
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0.0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_pair_signed_flip_lookup_near_null_pass"] is True
    assert diagnostics["within_state_topk_pair_signed_flip_variation_pass"] is True
    assert diagnostics["paired_context_diversity_pass"] is True
    assert diagnostics["signed_flip_label_balance_pass"] is True
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0


def test_transition_orbit_slot_invariant_topk_pair_order_signed_flip_consistency_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_consistency_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_topk_pair_order_signed_flip_consistency_invariant_lookup",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_consistency_binary+readout_symbolic_transition_topk_pair_order_signed_flip_consistency_invariant_lookup+head_linear"
    )
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0


def test_transition_orbit_slot_invariant_topk_pair_order_signed_flip_stability_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_stability_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_stability_invariant",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_stability_binary+readout_relational_witness_transition_orbit_topk_pair_order_signed_flip_stability_invariant+head_linear"
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0.0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_pair_signed_flip_stability_lookup_near_null_pass"] is True
    assert diagnostics["within_state_topk_pair_signed_flip_stability_variation_pass"] is True
    assert diagnostics["paired_context_diversity_pass"] is True
    assert diagnostics["signed_flip_stability_label_balance_pass"] is True
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0


def test_transition_orbit_slot_invariant_topk_pair_order_signed_flip_stability_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_stability_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_topk_pair_order_signed_flip_stability_invariant_lookup",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_stability_binary+readout_symbolic_transition_topk_pair_order_signed_flip_stability_invariant_lookup+head_linear"
    )
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0


def test_transition_orbit_slot_invariant_topk_pair_order_signed_flip_persistence_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_persistence_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_persistence_invariant",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_persistence_binary+readout_relational_witness_transition_orbit_topk_pair_order_signed_flip_persistence_invariant+head_linear"
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0.0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_pair_signed_flip_persistence_lookup_near_null_pass"] is True
    assert diagnostics["within_state_topk_pair_signed_flip_persistence_variation_pass"] is True
    assert diagnostics["paired_context_diversity_pass"] is True
    assert diagnostics["signed_flip_persistence_label_balance_pass"] is True
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0


def test_transition_orbit_slot_invariant_topk_pair_order_signed_flip_persistence_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_persistence_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_topk_pair_order_signed_flip_persistence_invariant_lookup",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_persistence_binary+readout_symbolic_transition_topk_pair_order_signed_flip_persistence_invariant_lookup+head_linear"
    )
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0


def test_transition_orbit_slot_invariant_topk_pair_order_signed_flip_recurrence_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_recurrence_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_recurrence_invariant",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_recurrence_binary+readout_relational_witness_transition_orbit_topk_pair_order_signed_flip_recurrence_invariant+head_linear"
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0.0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_pair_signed_flip_recurrence_lookup_near_null_pass"] is True
    assert diagnostics["within_state_topk_pair_signed_flip_recurrence_variation_pass"] is True
    assert diagnostics["paired_context_diversity_pass"] is True
    assert diagnostics["signed_flip_recurrence_label_balance_pass"] is True
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0


def test_transition_orbit_slot_invariant_topk_pair_order_signed_flip_recurrence_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_recurrence_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_topk_pair_order_signed_flip_recurrence_invariant_lookup",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_recurrence_binary+readout_symbolic_transition_topk_pair_order_signed_flip_recurrence_invariant_lookup+head_linear"
    )
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0


def test_transition_orbit_slot_invariant_topk_pair_order_signed_flip_reversion_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_reversion_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_reversion_invariant",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_reversion_binary+readout_relational_witness_transition_orbit_topk_pair_order_signed_flip_reversion_invariant+head_linear"
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0.0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_pair_signed_flip_reversion_lookup_near_null_pass"] is True
    assert diagnostics["within_state_topk_pair_signed_flip_reversion_variation_pass"] is True
    assert diagnostics["paired_context_diversity_pass"] is True
    assert diagnostics["signed_flip_reversion_label_balance_pass"] is True
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0


def test_transition_orbit_slot_invariant_topk_pair_order_signed_flip_reversion_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_reversion_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_topk_pair_order_signed_flip_reversion_invariant_lookup",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_reversion_binary+readout_symbolic_transition_topk_pair_order_signed_flip_reversion_invariant_lookup+head_linear"
    )
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0


def test_transition_orbit_slot_invariant_topk_pair_order_signed_flip_hysteresis_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_hysteresis_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_hysteresis_invariant",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_hysteresis_binary+readout_relational_witness_transition_orbit_topk_pair_order_signed_flip_hysteresis_invariant+head_linear"
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0.0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_pair_signed_flip_hysteresis_lookup_near_null_pass"] is True
    assert diagnostics["within_state_topk_pair_signed_flip_hysteresis_variation_pass"] is True
    assert diagnostics["paired_context_diversity_pass"] is True
    assert diagnostics["signed_flip_hysteresis_label_balance_pass"] is True
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0


def test_transition_orbit_slot_invariant_topk_pair_order_signed_flip_hysteresis_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_hysteresis_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_topk_pair_order_signed_flip_hysteresis_invariant_lookup",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_hysteresis_binary+readout_symbolic_transition_topk_pair_order_signed_flip_hysteresis_invariant_lookup+head_linear"
    )
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0


def test_transition_orbit_slot_invariant_topk_pair_order_signed_flip_memory_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_memory_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_topk_pair_order_signed_flip_memory_invariant",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_memory_binary+readout_relational_witness_transition_orbit_topk_pair_order_signed_flip_memory_invariant+head_linear"
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0.0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_pair_signed_flip_memory_lookup_near_null_pass"] is True
    assert diagnostics["within_state_topk_pair_signed_flip_memory_variation_pass"] is True
    assert diagnostics["paired_context_diversity_pass"] is True
    assert diagnostics["signed_flip_memory_label_balance_pass"] is True
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0


def test_transition_orbit_slot_invariant_topk_pair_order_signed_flip_memory_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_memory_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_topk_pair_order_signed_flip_memory_invariant_lookup",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_memory_binary+readout_symbolic_transition_topk_pair_order_signed_flip_memory_invariant_lookup+head_linear"
    )
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0


def test_transition_orbit_slot_invariant_topk_pair_order_stability_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_topk_pair_order_stability_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_topk_pair_order_stability_invariant",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_topk_pair_order_stability_binary+readout_relational_witness_transition_orbit_topk_pair_order_stability_invariant+head_linear"
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_pair_stability_lookup_near_null_pass"] is True


def test_transition_orbit_slot_invariant_topk_pair_order_stability_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_topk_pair_order_stability_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_topk_pair_order_stability_invariant_lookup",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_topk_pair_order_stability_binary+readout_symbolic_transition_topk_pair_order_stability_invariant_lookup+head_linear"
    )
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0


def test_transition_orbit_slot_invariant_topk_pair_order_drift_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_topk_pair_order_drift_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_topk_pair_order_drift_invariant",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_topk_pair_order_drift_response+readout_relational_witness_transition_orbit_topk_pair_order_drift_invariant+head_linear"
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_pair_drift_lookup_near_null_pass"] is True


def test_transition_orbit_slot_invariant_topk_pair_order_drift_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_topk_pair_order_drift_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_topk_pair_order_drift_invariant_lookup",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_topk_pair_order_drift_response+readout_symbolic_transition_topk_pair_order_drift_invariant_lookup+head_linear"
    )
    assert "mae" in metrics["extra_metrics"]
    assert "rank_correlation" in metrics["extra_metrics"]


def test_transition_orbit_slot_invariant_topk_pair_order_signed_drift_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_drift_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_transition_orbit_topk_pair_order_signed_drift_invariant",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_drift_response+readout_relational_witness_transition_orbit_topk_pair_order_signed_drift_invariant+head_linear"
    )
    diagnostics = metrics["dataset_diagnostics"]
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0.0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_pair_signed_drift_lookup_near_null_pass"] is True
    assert diagnostics["within_state_topk_pair_signed_drift_variation_pass"] is True


def test_transition_orbit_slot_invariant_topk_pair_order_signed_drift_lookup_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_drift_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_topk_pair_order_signed_drift_invariant_lookup",
    )
    assert (
        metrics["data_mode"]
        == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_drift_response+readout_symbolic_transition_topk_pair_order_signed_drift_invariant_lookup+head_linear"
    )
    assert "mae" in metrics["extra_metrics"]
    assert "rank_correlation" in metrics["extra_metrics"]


def test_synthetic_offset_binary_quantum_backend_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_offset_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V3",
        local_readout="parity",
    )
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0
    assert metrics["data_mode"].endswith("readout_parity+mix_mix_v0")
    assert metrics["dataset_diagnostics"]["dataset"] == "synthetic_offset_binary"


def test_vnew_explicit_interference_runs_on_synthetic_packet() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_offset_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_new_explicit_interference",
        local_readout="parity",
    )
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0
    assert metrics["data_mode"].endswith("readout_parity_contrast+mix_interference")
    assert "score_by_offset" in metrics["run_diagnostics"]
    assert "positive_minus_negative_offset_gap" in metrics["run_diagnostics"]
    assert "overall_score_mean" in metrics["run_diagnostics"]


def test_pairstate_relational_runs_on_synthetic_packet() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_offset_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_pairstate_relational",
        local_readout="parity",
    )
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0
    assert metrics["data_mode"].endswith("readout_sector_contrast+repr_pairstate+control_aligned")
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["sector_resolution_pre_aggregation"] is True
    assert set(diagnostics["sector_responses"].keys()) == {"P_small", "P_large", "N_small", "N_large"}
    assert "signed_contrast_mean" in diagnostics
    assert "magnitude_balance_mean" in diagnostics


def test_pairstate_sector_permuted_control_is_recorded() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_offset_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_pairstate_relational",
        pairstate_control_mode="sector_permuted",
    )
    assert metrics["data_mode"].endswith("readout_sector_contrast+repr_pairstate+control_sector_permuted")
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["control_mode"] == "sector_permuted"
    assert diagnostics["aggregation_buckets"] == {
        "positive": ["P_small", "N_large"],
        "negative": ["N_small", "P_large"],
    }


def test_future_sector_contrast_pairstate_runs_on_sector_parity_packet() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_sector_parity_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_sector_contrast_pairstate",
        pairstate_control_mode="sector_parity",
    )
    assert metrics["data_mode"].endswith("readout_sector_contrast+repr_pairstate+control_sector_parity")
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["control_mode"] == "sector_parity"
    assert "score_by_sector" in diagnostics
    assert "task_contrast_mean" in diagnostics
    assert diagnostics["anti_collapse_pass"] is True


def test_future_relational_witness_runs_on_sector_parity_packet() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_sector_parity_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness",
    )
    assert metrics["data_mode"].endswith("readout_relational_witness+head_logreg+featuremode_full")
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["feature_order"] == [
        "mu_P_small",
        "mu_P_large",
        "mu_N_small",
        "mu_N_large",
        "delta_sign_small",
        "delta_sign_large",
        "delta_mag_pos",
        "delta_mag_neg",
        "delta_task",
    ]
    assert "coefficients" in diagnostics
    assert "intercept" in diagnostics
    assert diagnostics["witness_feature_mode"] == "full"
    assert diagnostics["witness_ablation_group"] == "full"
    assert diagnostics["ablated_features"] == []
    assert diagnostics["anti_collapse_pass"] is True
    assert diagnostics["forbidden_inputs_absent"] is True


def test_sector_parity_split_rotation_flows_through_runner() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_sector_parity_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness",
        synthetic_split_rotation=1,
    )
    assert metrics["dataset_diagnostics"]["split_rotation"] == 1


def test_relational_witness_feature_mask_ablates_expected_group() -> None:
    feature_order = [
        "mu_P_small",
        "mu_P_large",
        "mu_N_small",
        "mu_N_large",
        "delta_sign_small",
        "delta_sign_large",
        "delta_mag_pos",
        "delta_mag_neg",
        "delta_task",
    ]
    mask, diagnostics = build_relational_witness_feature_mask(feature_order, "group_D_task_contrast")
    assert mask == [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0]
    assert diagnostics["ablated_features"] == ["delta_task"]
    assert diagnostics["feature_group_state"]["group_D_task_contrast"]["ablated"] is True
    assert diagnostics["feature_group_state"]["group_A_sector_means"]["ablated"] is False
    assert set(diagnostics["feature_group_state"].keys()) == set(RELATIONAL_WITNESS_FEATURE_GROUPS.keys())


def test_future_relational_witness_supports_group_ablation_run() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_sector_parity_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness",
        witness_feature_mode="group_D_task_contrast",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["witness_feature_mode"] == "group_D_task_contrast"
    assert diagnostics["witness_ablation_group"] == "group_D_task_contrast"
    assert diagnostics["ablated_features"] == ["delta_task"]
    assert diagnostics["feature_group_state"]["group_D_task_contrast"]["ablated"] is True
    assert metrics["data_mode"].endswith("readout_relational_witness+head_logreg+featuremode_group_D_task_contrast")


def test_relational_witness_feature_mask_supports_schema_views() -> None:
    feature_order = [
        "mu_P_small",
        "mu_P_large",
        "mu_N_small",
        "mu_N_large",
        "delta_sign_small",
        "delta_sign_large",
        "delta_mag_pos",
        "delta_mag_neg",
        "delta_task",
    ]
    mask, diagnostics = build_relational_witness_feature_mask(feature_order, "contrasts_only")
    assert mask == [0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0]
    assert diagnostics["witness_feature_mode"] == "contrasts_only"
    assert diagnostics["retained_features"] == RELATIONAL_WITNESS_SCHEMA_VIEWS["contrasts_only"]
    assert diagnostics["ablated_features"] == ["mu_P_small", "mu_P_large", "mu_N_small", "mu_N_large", "delta_task"]


def test_future_relational_witness_supports_schema_view_run() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_sector_parity_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness",
        witness_feature_mode="means_only",
    )
    diagnostics = metrics["run_diagnostics"]
    assert diagnostics["witness_feature_mode"] == "means_only"
    assert diagnostics["retained_features"] == RELATIONAL_WITNESS_SCHEMA_VIEWS["means_only"]
    assert "delta_task" in diagnostics["ablated_features"]
    assert metrics["data_mode"].endswith("readout_relational_witness+head_logreg+featuremode_means_only")


def test_symbolic_relational_features_are_one_hot() -> None:
    result = symbolic_relational_features("lt:A rt:C lp:2 rp:5 off:+3")
    assert result["feature_order"] == ["sec_P_small", "sec_P_large", "sec_N_small", "sec_N_large"]
    assert result["features"] == {
        "sec_P_small": 0.0,
        "sec_P_large": 1.0,
        "sec_N_small": 0.0,
        "sec_N_large": 0.0,
    }
    assert result["forbidden_inputs_absent"] is True


def test_symbolic_relational_control_runs_on_sector_parity_packet() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_sector_parity_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_relational",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_symbolic_relational+head_logreg")
    assert diagnostics["feature_order"] == ["sec_P_small", "sec_P_large", "sec_N_small", "sec_N_large"]
    assert "coefficients" in diagnostics
    assert diagnostics["forbidden_inputs_absent"] is True


def test_parse_dual_synthetic_pair_text_extracts_sectors() -> None:
    payload = parse_dual_synthetic_pair_text(
        "a_lt:A a_rt:B a_lp:1 a_rp:3 a_off:+2 b_lt:C b_rt:D b_lp:7 b_rp:4 b_off:-3"
    )
    assert payload["sector_a"] == "P_small"
    assert payload["sector_b"] == "N_large"
    assert payload["content_family_a"] == "crossed"
    assert payload["content_family_b"] == "crossed"
    assert payload["orientation_a"] == "forward"
    assert payload["orientation_b"] == "forward"
    assert payload["sign_agreement"] is False
    assert payload["content_agreement"] is True
    assert payload["orientation_agreement"] is True


def test_symbolic_dual_sector_features_use_two_one_hot_blocks() -> None:
    result = symbolic_dual_sector_features(
        "a_lt:A a_rt:B a_lp:1 a_rp:3 a_off:+2 b_lt:C b_rt:D b_lp:7 b_rp:4 b_off:-3"
    )
    assert result["feature_order"] == [
        "secA_P_small",
        "secA_P_large",
        "secA_N_small",
        "secA_N_large",
        "secB_P_small",
        "secB_P_large",
        "secB_N_small",
        "secB_N_large",
    ]
    assert result["features"]["secA_P_small"] == 1.0
    assert result["features"]["secB_N_large"] == 1.0
    assert sum(result["features"].values()) == 2.0


def test_symbolic_dual_interaction_features_use_single_pair_one_hot() -> None:
    result = symbolic_dual_interaction_features(
        "a_lt:A a_rt:B a_lp:1 a_rp:3 a_off:+2 b_lt:C b_rt:D b_lp:7 b_rp:4 b_off:-3"
    )
    assert result["feature_order"][0] == "pair_P_small__P_small"
    assert result["features"]["pair_P_small__N_large"] == 1.0
    assert sum(result["features"].values()) == 1.0


def test_symbolic_dual_content_interaction_features_use_content_pair_one_hot() -> None:
    result = symbolic_dual_content_interaction_features(
        "a_lt:A a_rt:C a_lp:1 a_rp:3 a_off:+2 b_lt:B b_rt:D b_lp:7 b_rp:4 b_off:-3"
    )
    assert result["feature_order"] == [
        "content_aligned__aligned",
        "content_aligned__crossed",
        "content_crossed__aligned",
        "content_crossed__crossed",
    ]
    assert result["features"]["content_aligned__aligned"] == 1.0
    assert sum(result["features"].values()) == 1.0


def test_symbolic_dual_cross_interaction_features_use_agreement_one_hot() -> None:
    result = symbolic_dual_cross_interaction_features(
        "a_lt:A a_rt:C a_lp:1 a_rp:3 a_off:+2 b_lt:B b_rt:D b_lp:7 b_rp:4 b_off:-3"
    )
    assert result["feature_order"] == [
        "cross_same__same",
        "cross_same__diff",
        "cross_diff__same",
        "cross_diff__diff",
    ]
    assert result["features"]["cross_diff__same"] == 1.0
    assert sum(result["features"].values()) == 1.0


def test_symbolic_triple_orientation_features_use_orientation_pair_one_hot() -> None:
    result = symbolic_triple_orientation_features(
        "a_lt:A a_rt:C a_lp:1 a_rp:3 a_off:+2 b_lt:B b_rt:A b_lp:7 b_rp:4 b_off:-3"
    )
    assert result["feature_order"] == [
        "orientation_forward__forward",
        "orientation_forward__reverse",
        "orientation_reverse__forward",
        "orientation_reverse__reverse",
    ]
    assert result["features"]["orientation_forward__reverse"] == 1.0
    assert sum(result["features"].values()) == 1.0


def test_symbolic_triple_two_family_features_use_three_pairwise_blocks() -> None:
    result = symbolic_triple_two_family_features(
        "a_lt:A a_rt:C a_lp:1 a_rp:3 a_off:+2 b_lt:B b_rt:A b_lp:7 b_rp:4 b_off:-3"
    )
    assert "sc_same__same" in result["feature_order"]
    assert "so_same__diff" in result["feature_order"]
    assert "co_same__diff" in result["feature_order"]
    assert sum(result["features"].values()) == 3.0


def test_symbolic_triple_parity_features_use_single_parity_feature() -> None:
    result = symbolic_triple_parity_features(
        "a_lt:A a_rt:C a_lp:1 a_rp:3 a_off:+2 b_lt:B b_rt:A b_lp:7 b_rp:4 b_off:-3"
    )
    assert result["feature_order"] == ["triple_even_parity"]
    assert result["features"]["triple_even_parity"] in {0.0, 1.0}


def test_dual_sector_agreement_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_sector_agreement_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_dual_sector",
    )
    assert metrics["data_mode"].endswith("readout_symbolic_dual_sector+head_logreg")
    assert metrics["dataset_diagnostics"]["dataset"] == "synthetic_dual_sector_agreement_binary"


def test_dual_sector_agreement_slot_swap_flows_through_runner() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_sector_agreement_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_dual_sector",
        synthetic_slot_swap=1,
    )
    assert metrics["dataset_diagnostics"]["slot_swap"] == 1


def test_dual_sector_agreement_token_permutation_flows_through_runner() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_sector_agreement_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_dual_sector",
        synthetic_token_permutation="cdab",
    )
    assert metrics["dataset_diagnostics"]["token_permutation"] == "cdab"


def test_dual_sector_agreement_pair_reindex_flows_through_runner() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_sector_agreement_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_dual_sector",
        synthetic_pair_reindex=1,
    )
    assert metrics["dataset_diagnostics"]["pair_reindex"] == 1


def test_dual_witness_runs_on_dual_sector_agreement_packet() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_sector_agreement_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_dual",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_relational_witness_dual+head_logreg")
    assert diagnostics["bounded_feature_audit_pass"] is True
    assert diagnostics["forbidden_inputs_absent"] is True


def test_dual_symbolic_interaction_control_runs_on_dual_sector_agreement_packet() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_sector_agreement_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_dual_interaction",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_symbolic_dual_interaction+head_logreg")
    assert "pair_P_small__P_small" in diagnostics["feature_order"]
    assert diagnostics["forbidden_inputs_absent"] is True


def test_dual_sector_content_agreement_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_sector_content_agreement_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_dual_content",
    )
    assert metrics["data_mode"].endswith("readout_relational_witness_dual_content+head_logreg")
    assert metrics["dataset_diagnostics"]["dataset"] == "synthetic_dual_sector_content_agreement_binary"
    assert metrics["run_diagnostics"]["bounded_feature_audit_pass"] is True
    assert metrics["run_diagnostics"]["forbidden_inputs_absent"] is True


def test_dual_symbolic_sector_interaction_runs_on_content_agreement_packet() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_sector_content_agreement_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_dual_sector_interaction",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_symbolic_dual_sector_interaction+head_logreg")
    assert "pair_P_small__P_small" in diagnostics["feature_order"]
    assert diagnostics["forbidden_inputs_absent"] is True


def test_dual_symbolic_content_interaction_runs_on_content_agreement_packet() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_sector_content_agreement_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_dual_content_interaction",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_symbolic_dual_content_interaction+head_logreg")
    assert "content_aligned__aligned" in diagnostics["feature_order"]
    assert diagnostics["forbidden_inputs_absent"] is True


def test_dual_symbolic_cross_interaction_runs_on_content_agreement_packet() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_sector_content_agreement_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_dual_cross_interaction",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_symbolic_dual_cross_interaction+head_logreg")
    assert "cross_same__same" in diagnostics["feature_order"]
    assert diagnostics["forbidden_inputs_absent"] is True


def test_triple_family_loader_path() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_content_parity_coupling_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_triple",
    )
    assert metrics["data_mode"].endswith("readout_relational_witness_triple+head_logreg")
    assert metrics["dataset_diagnostics"]["dataset"] == "synthetic_dual_content_parity_coupling_binary"
    assert metrics["run_diagnostics"]["bounded_feature_audit_pass"] is True
    assert metrics["run_diagnostics"]["forbidden_inputs_absent"] is True


def test_triple_symbolic_orientation_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_content_parity_coupling_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_orientation_only",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_symbolic_orientation_only+head_logreg")
    assert "orientation_forward__forward" in diagnostics["feature_order"]
    assert diagnostics["forbidden_inputs_absent"] is True


def test_triple_symbolic_two_family_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_content_parity_coupling_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_two_family_bounded",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_symbolic_two_family_bounded+head_logreg")
    assert "sc_same__same" in diagnostics["feature_order"]
    assert diagnostics["forbidden_inputs_absent"] is True


def test_triple_symbolic_three_family_parity_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_content_parity_coupling_binary",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_three_family_parity",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_symbolic_three_family_parity+head_logreg")
    assert diagnostics["feature_order"] == ["triple_even_parity"]
    assert diagnostics["forbidden_inputs_absent"] is True


def test_continuous_dataset_loader_path() -> None:
    rows, mode = load_dataset_samples(dataset="synthetic_dual_continuous_coupled_response", seed=42)
    assert len(rows) == 64
    assert mode == "synthetic_dual_continuous_coupled_response"


def test_continuous_relational_witness_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_continuous_coupled_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_continuous",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_relational_witness_continuous+head_linear")
    assert metrics["extra_metrics"]["mae"] >= 0.0
    assert "response_linear_hint" in diagnostics["feature_order"]
    assert diagnostics["bounded_feature_audit_pass"] is True
    assert diagnostics["forbidden_inputs_absent"] is True


def test_continuous_symbolic_single_family_regressor_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_continuous_coupled_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_single_family_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_symbolic_single_family_regressor+head_linear")
    assert diagnostics["feature_order"] == ["sign_agreement", "content_agreement", "orientation_agreement"]
    assert diagnostics["forbidden_inputs_absent"] is True


def test_continuous_symbolic_two_family_regressor_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_continuous_coupled_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_two_family_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_symbolic_two_family_regressor+head_linear")
    assert "sc_same__same" in diagnostics["feature_order"]
    assert diagnostics["forbidden_inputs_absent"] is True


def test_continuous_symbolic_boolean_state_lookup_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_continuous_coupled_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_boolean_state_lookup",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_symbolic_boolean_state_lookup+head_linear")
    assert "state_same__same__same" in diagnostics["feature_order"]
    assert diagnostics["forbidden_inputs_absent"] is True


def test_state_sensitive_continuous_loader_path() -> None:
    rows, mode = load_dataset_samples(dataset="synthetic_dual_state_sensitive_continuous_response", seed=42)
    assert len(rows) == 64
    assert mode == "synthetic_dual_state_sensitive_continuous_response"


def test_state_sensitive_continuous_witness_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_state_sensitive_continuous_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_state_sensitive",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_relational_witness_state_sensitive+head_linear")
    assert metrics["extra_metrics"]["mae"] >= 0.0
    assert "sign_mag_coupling" in diagnostics["feature_order"]
    assert diagnostics["bounded_feature_audit_pass"] is True
    assert diagnostics["anti_collapse_pass"] is True


def test_state_sensitive_symbolic_coarse_lookup_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_state_sensitive_continuous_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_coarse_lookup_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_symbolic_coarse_lookup_regressor+head_linear")
    assert diagnostics["feature_order"] == ["sign_agreement", "content_agreement", "orientation_agreement"]


def test_state_sensitive_symbolic_analog_only_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_state_sensitive_continuous_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_analog_only_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_symbolic_analog_only_regressor+head_linear")
    assert diagnostics["feature_order"] == ["sector_magnitude_delta", "ordered_content_delta"]


def test_state_sensitive_symbolic_full_declared_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_state_sensitive_continuous_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_full_declared_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_symbolic_full_declared_regressor+head_linear")
    assert "ordered_content_delta" in diagnostics["feature_order"]
    assert "sector_magnitude_delta" in diagnostics["feature_order"]


def test_orthogonalized_continuous_loader_path() -> None:
    rows, mode = load_dataset_samples(dataset="synthetic_dual_orthogonalized_continuous_response", seed=42)
    assert len(rows) == 64
    assert mode == "synthetic_dual_orthogonalized_continuous_response"


def test_orthogonalized_continuous_witness_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_orthogonalized_continuous_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_orthogonalized",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_relational_witness_orthogonalized+head_linear")
    assert metrics["extra_metrics"]["mae"] >= 0.0
    assert "analog_residual_hint" in diagnostics["feature_order"]
    assert diagnostics["bounded_feature_audit_pass"] is True
    assert diagnostics["anti_collapse_pass"] is True


def test_orthogonalized_full_declared_residual_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_orthogonalized_continuous_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_full_declared_residual_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_symbolic_full_declared_residual_regressor+head_linear")
    assert "ordered_content_delta" in diagnostics["feature_order"]
    assert "sector_magnitude_delta" in diagnostics["feature_order"]


def test_nonlinear_manifold_loader_path() -> None:
    rows, mode = load_dataset_samples(dataset="synthetic_dual_nonlinear_manifold_response", seed=42)
    assert len(rows) == 64
    assert mode == "synthetic_dual_nonlinear_manifold_response"


def test_nonlinear_manifold_witness_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_nonlinear_manifold_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_nonlinear",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_relational_witness_nonlinear+head_linear")
    assert metrics["extra_metrics"]["mae"] >= 0.0
    assert "nonlinear_manifold_hint" in diagnostics["feature_order"]
    assert diagnostics["bounded_feature_audit_pass"] is True
    assert diagnostics["anti_collapse_pass"] is True


def test_nonlinear_manifold_additive_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_nonlinear_manifold_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_full_declared_additive_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_symbolic_full_declared_additive_regressor+head_linear")
    assert "orientation_delta" in diagnostics["feature_order"]
    assert "ordered_content_delta" in diagnostics["feature_order"]
    assert "sector_magnitude_delta" in diagnostics["feature_order"]


def test_nonlinear_manifold_symbolic_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_nonlinear_manifold_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_nonlinear_manifold_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_symbolic_nonlinear_manifold_regressor+head_linear")
    assert diagnostics["feature_order"] == ["sin_uv", "signed_orientation", "cos_v"]


def test_phase_sensitive_manifold_loader_path() -> None:
    rows, mode = load_dataset_samples(dataset="synthetic_dual_phase_sensitive_manifold_response", seed=42)
    assert len(rows) == 64
    assert mode == "synthetic_dual_phase_sensitive_manifold_response"


def test_phase_sensitive_manifold_witness_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_phase_sensitive_manifold_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_phase_sensitive",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_relational_witness_phase_sensitive+head_linear")
    assert metrics["extra_metrics"]["mae"] >= 0.0
    assert "phase_sensitive_hint" in diagnostics["feature_order"]
    assert diagnostics["bounded_feature_audit_pass"] is True
    assert diagnostics["anti_collapse_pass"] is True


def test_phase_sensitive_phase_insensitive_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_phase_sensitive_manifold_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_phase_insensitive_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_symbolic_phase_insensitive_regressor+head_linear")
    assert diagnostics["feature_order"] == ["sin_uv", "cos_v_plus_w"]
    assert diagnostics["phase_offset_absent"] is True


def test_latent_phase_manifold_loader_path() -> None:
    rows, mode = load_dataset_samples(dataset="synthetic_dual_latent_phase_manifold_residual_response", seed=42)
    assert len(rows) == 64
    assert mode == "synthetic_dual_latent_phase_manifold_residual_response"


def test_latent_phase_manifold_witness_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_latent_phase_manifold_residual_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_latent_phase",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_relational_witness_latent_phase+head_linear")
    assert metrics["extra_metrics"]["mae"] >= 0.0
    assert "latent_phase_hint" in diagnostics["feature_order"]
    assert diagnostics["bounded_feature_audit_pass"] is True
    assert diagnostics["anti_collapse_pass"] is True


def test_latent_phase_global_phase_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_latent_phase_manifold_residual_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_global_phase_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_symbolic_global_phase_regressor+head_linear")
    assert diagnostics["feature_order"] == ["global_phase_backbone", "global_phase_curvature"]
    assert diagnostics["latent_neighborhood_absent"] is True
    assert diagnostics["global_phase_only"] is True


def test_local_atlas_manifold_loader_path() -> None:
    rows, mode = load_dataset_samples(dataset="synthetic_dual_local_atlas_manifold_response", seed=42)
    assert len(rows) == 64
    assert mode == "synthetic_dual_local_atlas_manifold_response"


def test_local_atlas_manifold_witness_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_local_atlas_manifold_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_local_atlas",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_relational_witness_local_atlas+head_linear")
    assert metrics["extra_metrics"]["mae"] >= 0.0
    assert "local_atlas_hint" in diagnostics["feature_order"]
    assert diagnostics["bounded_feature_audit_pass"] is True
    assert diagnostics["anti_collapse_pass"] is True


def test_local_atlas_single_chart_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_local_atlas_manifold_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_single_chart_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_symbolic_single_chart_regressor+head_linear")
    assert diagnostics["feature_order"] == [
        "single_chart_backbone",
        "single_chart_phase",
        "single_chart_curvature",
    ]
    assert diagnostics["chart_id_absent"] is True
    assert diagnostics["single_chart_only"] is True


def test_chart_transition_manifold_loader_path() -> None:
    rows, mode = load_dataset_samples(dataset="synthetic_dual_chart_transition_manifold_response", seed=42)
    assert len(rows) == 64
    assert mode == "synthetic_dual_chart_transition_manifold_response"


def test_chart_transition_manifold_witness_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_chart_transition_manifold_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_future_relational_witness_chart_transition",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_relational_witness_chart_transition+head_linear")
    assert metrics["extra_metrics"]["mae"] >= 0.0
    assert "chart_transition_hint" in diagnostics["feature_order"]
    assert diagnostics["bounded_feature_audit_pass"] is True
    assert diagnostics["anti_collapse_pass"] is True


def test_chart_transition_additive_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_chart_transition_manifold_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_additive_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_symbolic_transition_additive_regressor+head_linear")
    assert diagnostics["feature_order"] == [
        "transition_backbone",
        "transition_phase",
        "transition_curvature",
    ]
    assert diagnostics["chart_id_absent"] is True
    assert diagnostics["transition_family_only"] is True


def test_chart_transition_unordered_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_chart_transition_manifold_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_unordered_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_symbolic_transition_unordered_regressor+head_linear")
    assert diagnostics["feature_order"] == [
        "transition_backbone",
        "transition_phase_unordered",
        "transition_curvature_unordered",
    ]
    assert diagnostics["chart_id_absent"] is True
    assert diagnostics["transition_family_only"] is True
    assert diagnostics["ordered_transition_absent"] is True


def test_chart_transition_permuted_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_chart_transition_manifold_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_permuted_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_symbolic_transition_permuted_regressor+head_linear")
    assert diagnostics["feature_order"] == [
        "transition_backbone",
        "transition_phase_permuted",
        "transition_curvature_permuted",
    ]
    assert diagnostics["chart_id_absent"] is True
    assert diagnostics["transition_family_only"] is True
    assert diagnostics["transition_table_permuted"] is True


def test_chart_transition_reversed_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_chart_transition_manifold_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_reversed_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_symbolic_transition_reversed_regressor+head_linear")
    assert diagnostics["feature_order"] == [
        "transition_backbone",
        "transition_phase_reversed",
        "transition_curvature_reversed",
    ]
    assert diagnostics["chart_id_absent"] is True
    assert diagnostics["transition_family_only"] is True
    assert diagnostics["transition_direction_reversed"] is True


def test_chart_transition_bidirectional_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_chart_transition_manifold_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_bidirectional_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_symbolic_transition_bidirectional_regressor+head_linear")
    assert diagnostics["feature_order"] == [
        "transition_backbone",
        "transition_phase_forward",
        "transition_curvature_forward",
        "transition_phase_reversed",
        "transition_curvature_reversed",
    ]
    assert diagnostics["chart_id_absent"] is True
    assert diagnostics["transition_family_only"] is True
    assert diagnostics["transition_direction_bidirectional"] is True


def test_chart_transition_cross_direction_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_chart_transition_manifold_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_cross_direction_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_symbolic_transition_cross_direction_regressor+head_linear")
    assert diagnostics["feature_order"] == [
        "transition_backbone",
        "transition_phase_forward",
        "transition_curvature_forward",
        "transition_phase_reversed",
        "transition_curvature_reversed",
        "transition_phase_cross",
        "transition_curvature_cross",
    ]
    assert diagnostics["chart_id_absent"] is True
    assert diagnostics["transition_family_only"] is True
    assert diagnostics["transition_cross_direction_only"] is True


def test_chart_transition_quadratic_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_chart_transition_manifold_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_quadratic_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_symbolic_transition_quadratic_regressor+head_linear")
    assert diagnostics["feature_order"] == [
        "transition_backbone",
        "transition_phase_forward",
        "transition_curvature_forward",
        "transition_phase_reversed",
        "transition_curvature_reversed",
        "transition_backbone_sq",
        "transition_phase_forward_sq",
        "transition_curvature_forward_sq",
        "transition_phase_reversed_sq",
        "transition_curvature_reversed_sq",
        "transition_phase_cross",
        "transition_curvature_cross",
        "transition_backbone_phase_forward",
        "transition_backbone_phase_reversed",
    ]
    assert diagnostics["chart_id_absent"] is True
    assert diagnostics["transition_family_only"] is True
    assert diagnostics["transition_quadratic_only"] is True


def test_chart_transition_cubic_control_runs() -> None:
    metrics = run_real_experiment(
        dataset="synthetic_dual_chart_transition_manifold_response",
        seed=42,
        backend="sim_quantum_statevector",
        variant="V_control_symbolic_transition_cubic_regressor",
    )
    diagnostics = metrics["run_diagnostics"]
    assert metrics["data_mode"].endswith("readout_symbolic_transition_cubic_regressor+head_linear")
    assert diagnostics["feature_order"] == [
        "transition_backbone",
        "transition_phase_forward",
        "transition_curvature_forward",
        "transition_phase_reversed",
        "transition_curvature_reversed",
        "transition_backbone_sq",
        "transition_phase_forward_sq",
        "transition_curvature_forward_sq",
        "transition_phase_reversed_sq",
        "transition_curvature_reversed_sq",
        "transition_phase_cross",
        "transition_curvature_cross",
        "transition_backbone_phase_forward",
        "transition_backbone_phase_reversed",
        "transition_phase_forward_cube",
        "transition_phase_reversed_cube",
        "transition_curvature_forward_cube",
        "transition_curvature_reversed_cube",
        "transition_phase_cross_backbone",
        "transition_curvature_cross_backbone",
    ]
    assert diagnostics["chart_id_absent"] is True
    assert diagnostics["transition_family_only"] is True
    assert diagnostics["transition_cubic_only"] is True
