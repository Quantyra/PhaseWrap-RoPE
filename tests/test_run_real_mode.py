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
    run_real_experiment,
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
