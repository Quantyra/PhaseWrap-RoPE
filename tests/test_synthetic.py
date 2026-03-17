from qrope.synthetic import (
    content_family_name,
    generate_chart_transition_token_invariant_response_bundle,
    generate_chart_transition_orbit_response_bundle,
    generate_transition_orbit_listwise_ranking_bundle,
    generate_transition_orbit_order_margin_response_bundle,
    generate_transition_orbit_sign_only_binary_bundle,
    generate_transition_orbit_sign_consistency_binary_bundle,
    generate_transition_orbit_sign_flip_contrast_binary_bundle,
    generate_transition_orbit_asymmetric_sign_localization_binary_bundle,
    generate_transition_orbit_channel_advantage_response_bundle,
    generate_transition_orbit_channel_order_response_bundle,
    generate_transition_orbit_slot_invariant_channel_order_response_bundle,
    generate_transition_orbit_slot_invariant_channel_order_margin_response_bundle,
    generate_transition_orbit_slot_invariant_channel_order_rank_only_bundle,
    generate_transition_orbit_slot_invariant_channel_order_topk_rank_only_bundle,
    generate_transition_orbit_slot_invariant_channel_order_topk_preference_binary_bundle,
    generate_transition_orbit_slot_invariant_channel_order_topk_margin_response_bundle,
    generate_transition_orbit_slot_invariant_topk_pair_margin_response_bundle,
    generate_transition_orbit_slot_invariant_topk_pair_order_agreement_binary_bundle,
    generate_transition_orbit_slot_invariant_topk_pair_order_signed_consistency_binary_bundle,
    generate_transition_orbit_slot_invariant_topk_pair_order_signed_flip_consistency_binary_bundle,
    generate_transition_orbit_slot_invariant_topk_pair_order_signed_flip_stability_binary_bundle,
    generate_transition_orbit_slot_invariant_topk_pair_order_signed_flip_persistence_binary_bundle,
    generate_transition_orbit_slot_invariant_topk_pair_order_signed_flip_recurrence_binary_bundle,
    generate_transition_orbit_slot_invariant_topk_pair_order_signed_flip_reversion_binary_bundle,
    generate_transition_orbit_slot_invariant_topk_pair_order_signed_flip_hysteresis_binary_bundle,
    generate_transition_orbit_slot_invariant_topk_pair_order_signed_flip_memory_binary_bundle,
    generate_transition_orbit_slot_invariant_topk_pair_order_signed_drift_response_bundle,
    generate_transition_orbit_slot_invariant_topk_pair_order_stability_binary_bundle,
    generate_transition_orbit_slot_invariant_topk_pair_order_drift_response_bundle,
    generate_transition_orbit_slot_invariant_channel_order_topk_consistency_binary_bundle,
    generate_transition_orbit_signed_margin_response_bundle,
    generate_transition_orbit_pairwise_order_binary_bundle,
    generate_transition_orbit_rank_band_response_bundle,
    generate_dual_continuous_coupled_response_bundle,
    generate_dual_latent_phase_manifold_residual_response_bundle,
    generate_dual_local_atlas_manifold_response_bundle,
    generate_dual_chart_transition_manifold_response_bundle,
    generate_symbolic_insufficiency_loop_closure_response_bundle,
    generate_symbolic_insufficiency_fork_join_response_bundle,
    generate_symbolic_insufficiency_path_response_bundle,
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
    generate_positional_shared_memory_multi_query_selection_response_bundle,
    generate_positional_intermediate_pointer_selection_response_bundle,
    generate_symbolic_insufficiency_braid_crossing_response_bundle,
    generate_symbolic_insufficiency_transition_response_bundle,
    generate_dual_content_parity_coupling_binary_bundle,
    generate_dual_nonlinear_manifold_response_bundle,
    generate_dual_phase_sensitive_manifold_response_bundle,
    generate_dual_orthogonalized_continuous_response_bundle,
    generate_dual_state_sensitive_continuous_response_bundle,
    generate_dual_sector_agreement_binary_bundle,
    generate_dual_sector_content_agreement_binary_bundle,
    generate_sector_parity_binary_bundle,
    generate_signed_offset_binary_bundle,
    token_orientation_name,
)


def test_signed_offset_bundle_is_deterministic() -> None:
    bundle_a = generate_signed_offset_binary_bundle(seed=42)
    bundle_b = generate_signed_offset_binary_bundle(seed=42)
    assert bundle_a.train == bundle_b.train
    assert bundle_a.validation == bundle_b.validation
    assert bundle_a.test == bundle_b.test
    assert bundle_a.diagnostics == bundle_b.diagnostics


def test_signed_offset_bundle_has_expected_sizes() -> None:
    bundle = generate_signed_offset_binary_bundle(seed=42)
    assert len(bundle.train) == 256
    assert len(bundle.validation) == 128
    assert len(bundle.test) == 128


def test_signed_offset_bundle_is_balanced() -> None:
    bundle = generate_signed_offset_binary_bundle(seed=42)
    for split in ("train", "validation", "test"):
        summary = bundle.diagnostics["splits"][split]
        assert summary["class_balance_ok"] is True
        assert summary["offset_abs_balance_ok"] is True
        assert summary["token_pair_balance_ok"] is True


def test_signed_offset_labels_match_rendered_offsets() -> None:
    bundle = generate_signed_offset_binary_bundle(seed=42)
    rows = bundle.train[:10] + bundle.validation[:10] + bundle.test[:10]
    for text, label in rows:
        offset = int(text.split("off:", 1)[1])
        assert label == (1 if offset > 0 else 0)


def test_sector_parity_bundle_is_deterministic() -> None:
    bundle_a = generate_sector_parity_binary_bundle(seed=42)
    bundle_b = generate_sector_parity_binary_bundle(seed=42)
    assert bundle_a.train == bundle_b.train
    assert bundle_a.validation == bundle_b.validation
    assert bundle_a.test == bundle_b.test
    assert bundle_a.diagnostics == bundle_b.diagnostics


def test_sector_parity_labels_match_crossed_sector_rule() -> None:
    bundle = generate_sector_parity_binary_bundle(seed=42)
    rows = bundle.train[:10] + bundle.validation[:10] + bundle.test[:10]
    for text, label in rows:
        offset = int(text.split("off:", 1)[1])
        magnitude = abs(offset)
        expected = 1 if (offset > 0 and magnitude in {1, 2}) or (offset < 0 and magnitude in {3, 4}) else 0
        assert label == expected


def test_sector_parity_split_rotation_changes_selected_rows() -> None:
    base = generate_sector_parity_binary_bundle(seed=42, split_rotation=0)
    rotated = generate_sector_parity_binary_bundle(seed=42, split_rotation=1)
    assert base.train != rotated.train
    assert base.validation != rotated.validation
    assert base.test != rotated.test
    assert rotated.diagnostics["split_rotation"] == 1


def test_dual_sector_agreement_bundle_is_deterministic() -> None:
    bundle_a = generate_dual_sector_agreement_binary_bundle(seed=42)
    bundle_b = generate_dual_sector_agreement_binary_bundle(seed=42)
    assert bundle_a.train == bundle_b.train
    assert bundle_a.validation == bundle_b.validation
    assert bundle_a.test == bundle_b.test
    assert bundle_a.diagnostics == bundle_b.diagnostics


def test_dual_sector_agreement_bundle_is_balanced() -> None:
    bundle = generate_dual_sector_agreement_binary_bundle(seed=42)
    for split in ("train", "validation", "test"):
        summary = bundle.diagnostics["splits"][split]
        assert summary["class_balance_ok"] is True
        assert summary["sector_pair_balance_ok"] is True
        assert summary["sector_slot_balance_ok"] is True


def test_dual_sector_agreement_labels_follow_same_sign_rule() -> None:
    bundle = generate_dual_sector_agreement_binary_bundle(seed=42)
    rows = bundle.train[:10] + bundle.validation[:10] + bundle.test[:10]
    for text, label in rows:
        parts = {item.split(":", 1)[0]: item.split(":", 1)[1] for item in text.split()}
        sector_a = ("P" if int(parts["a_off"]) > 0 else "N")
        sector_b = ("P" if int(parts["b_off"]) > 0 else "N")
        assert label == (1 if sector_a == sector_b else 0)


def test_dual_sector_agreement_slot_swap_preserves_labels_and_changes_order() -> None:
    base = generate_dual_sector_agreement_binary_bundle(seed=42, slot_swap=0)
    swapped = generate_dual_sector_agreement_binary_bundle(seed=42, slot_swap=1)
    assert base.train != swapped.train
    assert swapped.diagnostics["slot_swap"] == 1

    def swap_text(text: str) -> str:
        parts = {item.split(":", 1)[0]: item.split(":", 1)[1] for item in text.split()}
        return (
            f"a_lt:{parts['b_lt']} a_rt:{parts['b_rt']} a_lp:{parts['b_lp']} a_rp:{parts['b_rp']} a_off:{parts['b_off']} "
            f"b_lt:{parts['a_lt']} b_rt:{parts['a_rt']} b_lp:{parts['a_lp']} b_rp:{parts['a_rp']} b_off:{parts['a_off']}"
        )

    expected = {(swap_text(text), label) for text, label in base.train}
    observed = set(swapped.train)
    assert observed == expected


def test_dual_sector_agreement_token_permutation_preserves_labels_and_renames_tokens() -> None:
    base = generate_dual_sector_agreement_binary_bundle(seed=42, token_permutation="identity")
    renamed = generate_dual_sector_agreement_binary_bundle(seed=42, token_permutation="cdab")
    assert base.train != renamed.train
    assert renamed.diagnostics["token_permutation"] == "cdab"

    mapping = {"A": "C", "B": "D", "C": "A", "D": "B"}

    def rename_text(text: str) -> str:
        parts = {item.split(":", 1)[0]: item.split(":", 1)[1] for item in text.split()}
        return (
            f"a_lt:{mapping[parts['a_lt']]} a_rt:{mapping[parts['a_rt']]} a_lp:{parts['a_lp']} a_rp:{parts['a_rp']} a_off:{parts['a_off']} "
            f"b_lt:{mapping[parts['b_lt']]} b_rt:{mapping[parts['b_rt']]} b_lp:{parts['b_lp']} b_rp:{parts['b_rp']} b_off:{parts['b_off']}"
        )

    expected = {(rename_text(text), label) for text, label in base.train}
    observed = set(renamed.train)
    assert observed == expected


def test_dual_sector_agreement_pair_reindex_changes_pairing_but_preserves_labels() -> None:
    base = generate_dual_sector_agreement_binary_bundle(seed=42, pair_reindex=0)
    reindexed = generate_dual_sector_agreement_binary_bundle(seed=42, pair_reindex=1)
    assert base.train != reindexed.train
    assert reindexed.diagnostics["pair_reindex"] == 1

    def sector_label_counts(rows: list[tuple[str, int]]) -> dict[tuple[str, str, int], int]:
        counts: dict[tuple[str, str, int], int] = {}
        for text, label in rows:
            parts = {item.split(":", 1)[0]: item.split(":", 1)[1] for item in text.split()}
            sector_a = ("P_small" if 0 < int(parts["a_off"]) <= 2 else
                        "P_large" if int(parts["a_off"]) > 0 else
                        "N_small" if abs(int(parts["a_off"])) <= 2 else "N_large")
            sector_b = ("P_small" if 0 < int(parts["b_off"]) <= 2 else
                        "P_large" if int(parts["b_off"]) > 0 else
                        "N_small" if abs(int(parts["b_off"])) <= 2 else "N_large")
            key = (sector_a, sector_b, label)
            counts[key] = counts.get(key, 0) + 1
        return counts

    assert sector_label_counts(base.train) == sector_label_counts(reindexed.train)


def test_content_family_name_groups_tokens_relationally() -> None:
    assert content_family_name("A", "C") == "aligned"
    assert content_family_name("B", "D") == "aligned"
    assert content_family_name("A", "B") == "crossed"


def test_dual_sector_content_agreement_bundle_is_balanced() -> None:
    bundle = generate_dual_sector_content_agreement_binary_bundle(seed=42)
    for split in ("train", "validation", "test"):
        summary = bundle.diagnostics["splits"][split]
        assert summary["class_balance_ok"] is True
        assert summary["sector_pair_balance_ok"] is True
        assert summary["sector_slot_balance_ok"] is True
        assert summary["content_slot_balance_ok"] is True


def test_dual_sector_content_agreement_labels_follow_xnor_rule() -> None:
    bundle = generate_dual_sector_content_agreement_binary_bundle(seed=42)
    rows = bundle.train[:10] + bundle.validation[:10] + bundle.test[:10]
    positive_sectors = {"P_small", "P_large"}
    for text, label in rows:
        parts = {item.split(":", 1)[0]: item.split(":", 1)[1] for item in text.split()}
        sector_a = ("P_small" if 0 < int(parts["a_off"]) <= 2 else
                    "P_large" if int(parts["a_off"]) > 0 else
                    "N_small" if abs(int(parts["a_off"])) <= 2 else "N_large")
        sector_b = ("P_small" if 0 < int(parts["b_off"]) <= 2 else
                    "P_large" if int(parts["b_off"]) > 0 else
                    "N_small" if abs(int(parts["b_off"])) <= 2 else "N_large")
        sign_agreement = (sector_a in positive_sectors) == (sector_b in positive_sectors)
        content_agreement = content_family_name(parts["a_lt"], parts["a_rt"]) == content_family_name(
            parts["b_lt"], parts["b_rt"]
        )
        assert label == (1 if sign_agreement == content_agreement else 0)


def test_symbolic_insufficiency_path_bundle_enforces_declared_diagnostics() -> None:
    bundle = generate_symbolic_insufficiency_path_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_symbolic_insufficiency_path_response"
    assert diagnostics["coarse_path_state_null_pass"] is True
    assert diagnostics["within_path_state_variation_pass"] is True
    assert diagnostics["latent_path_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["path_length_balance_pass"] is True


def test_symbolic_insufficiency_relay_bundle_enforces_declared_diagnostics() -> None:
    bundle = generate_symbolic_insufficiency_relay_binding_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_symbolic_insufficiency_relay_binding_response"
    assert diagnostics["coarse_relay_state_null_pass"] is True
    assert diagnostics["within_relay_state_variation_pass"] is True
    assert diagnostics["latent_relay_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["relay_length_balance_pass"] is True
    assert diagnostics["binding_target_nontrivial_pass"] is True


def test_symbolic_insufficiency_cascade_reconciliation_bundle_enforces_declared_diagnostics() -> None:
    bundle = generate_symbolic_insufficiency_cascade_reconciliation_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_symbolic_insufficiency_cascade_reconciliation_response"
    assert diagnostics["coarse_reconciliation_state_null_pass"] is True
    assert diagnostics["within_reconciliation_state_variation_pass"] is True
    assert diagnostics["latent_reconciliation_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["reconciliation_length_balance_pass"] is True
    assert diagnostics["reconciliation_target_nontrivial_pass"] is True


def test_symbolic_insufficiency_latch_switch_bundle_enforces_declared_diagnostics() -> None:
    bundle = generate_symbolic_insufficiency_latch_switch_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_symbolic_insufficiency_latch_switch_response"
    assert diagnostics["coarse_latch_switch_state_null_pass"] is True
    assert diagnostics["within_latch_switch_state_variation_pass"] is True
    assert diagnostics["latent_latch_switch_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["latch_switch_target_nontrivial_pass"] is True


def test_symbolic_insufficiency_staggered_binding_bundle_enforces_declared_diagnostics() -> None:
    bundle = generate_symbolic_insufficiency_staggered_binding_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_symbolic_insufficiency_staggered_binding_response"
    assert diagnostics["coarse_staggered_state_null_pass"] is True
    assert diagnostics["within_staggered_state_variation_pass"] is True
    assert diagnostics["latent_staggered_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["staggered_length_balance_pass"] is True
    assert diagnostics["binding_target_nontrivial_pass"] is True


def test_symbolic_insufficiency_fanin_consensus_bundle_enforces_declared_diagnostics() -> None:
    bundle = generate_symbolic_insufficiency_fanin_consensus_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_symbolic_insufficiency_fanin_consensus_response"
    assert diagnostics["coarse_fanin_state_null_pass"] is True
    assert diagnostics["within_fanin_state_variation_pass"] is True
    assert diagnostics["latent_fanin_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["fanin_width_balance_pass"] is True
    assert diagnostics["consensus_target_nontrivial_pass"] is True


def test_symbolic_insufficiency_echo_resolution_bundle_enforces_declared_diagnostics() -> None:
    bundle = generate_symbolic_insufficiency_echo_resolution_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_symbolic_insufficiency_echo_resolution_response"
    assert diagnostics["coarse_echo_state_null_pass"] is True
    assert diagnostics["within_echo_state_variation_pass"] is True
    assert diagnostics["latent_echo_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["echo_length_balance_pass"] is True
    assert diagnostics["resolution_target_nontrivial_pass"] is True


def test_symbolic_insufficiency_selector_arbitration_bundle_enforces_declared_diagnostics() -> None:
    bundle = generate_symbolic_insufficiency_selector_arbitration_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_symbolic_insufficiency_selector_arbitration_response"
    assert diagnostics["coarse_selector_state_null_pass"] is True
    assert diagnostics["within_selector_state_variation_pass"] is True
    assert diagnostics["latent_selector_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["selector_length_balance_pass"] is True
    assert diagnostics["selector_target_nontrivial_pass"] is True


def test_symbolic_insufficiency_counterfactual_handoff_bundle_enforces_declared_diagnostics() -> None:
    bundle = generate_symbolic_insufficiency_counterfactual_handoff_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_symbolic_insufficiency_counterfactual_handoff_response"
    assert diagnostics["coarse_handoff_state_null_pass"] is True
    assert diagnostics["within_handoff_state_variation_pass"] is True
    assert diagnostics["latent_handoff_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["handoff_length_balance_pass"] is True
    assert diagnostics["handoff_target_nontrivial_pass"] is True


def test_positional_anchor_order_bundle_enforces_declared_diagnostics() -> None:
    bundle = generate_positional_anchor_order_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_positional_anchor_order_response"
    assert diagnostics["coarse_anchor_order_state_null_pass"] is True
    assert diagnostics["within_anchor_order_state_variation_pass"] is True
    assert diagnostics["latent_anchor_order_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["anchor_order_length_balance_pass"] is True
    assert diagnostics["anchor_order_target_nontrivial_pass"] is True


def test_positional_anchor_distance_bundle_enforces_declared_diagnostics() -> None:
    bundle = generate_positional_anchor_distance_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_positional_anchor_distance_response"
    assert diagnostics["coarse_anchor_distance_state_null_pass"] is True
    assert diagnostics["within_anchor_distance_state_variation_pass"] is True
    assert diagnostics["latent_anchor_distance_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["anchor_distance_length_balance_pass"] is True
    assert diagnostics["anchor_distance_target_nontrivial_pass"] is True


def test_positional_anchor_span_membership_bundle_enforces_declared_diagnostics() -> None:
    bundle = generate_positional_anchor_span_membership_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_positional_anchor_span_membership_response"
    assert diagnostics["coarse_anchor_span_membership_state_null_pass"] is True
    assert diagnostics["within_anchor_span_membership_state_variation_pass"] is True
    assert diagnostics["latent_anchor_span_membership_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["anchor_span_membership_length_balance_pass"] is True
    assert diagnostics["anchor_span_membership_target_nontrivial_pass"] is True


def test_positional_anchor_offset_signature_bundle_enforces_declared_diagnostics() -> None:
    bundle = generate_positional_anchor_offset_signature_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_positional_anchor_offset_signature_response"
    assert diagnostics["coarse_anchor_offset_signature_state_null_pass"] is True
    assert diagnostics["within_anchor_offset_signature_state_variation_pass"] is True
    assert diagnostics["latent_anchor_offset_signature_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["anchor_offset_signature_length_balance_pass"] is True
    assert diagnostics["anchor_offset_signature_target_nontrivial_pass"] is True


def test_positional_anchor_betweenness_bundle_enforces_declared_diagnostics() -> None:
    bundle = generate_positional_anchor_betweenness_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_positional_anchor_betweenness_response"
    assert diagnostics["coarse_anchor_betweenness_state_null_pass"] is True
    assert diagnostics["within_anchor_betweenness_state_variation_pass"] is True
    assert diagnostics["latent_anchor_betweenness_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["anchor_betweenness_length_balance_pass"] is True
    assert diagnostics["anchor_betweenness_target_nontrivial_pass"] is True


def test_positional_offset_retrieval_bundle_enforces_declared_diagnostics() -> None:
    bundle = generate_positional_offset_retrieval_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_positional_offset_retrieval_response"
    assert diagnostics["coarse_offset_retrieval_state_null_pass"] is True
    assert diagnostics["within_offset_retrieval_state_variation_pass"] is True
    assert diagnostics["latent_offset_retrieval_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["offset_retrieval_length_balance_pass"] is True
    assert diagnostics["offset_retrieval_target_nontrivial_pass"] is True
    assert diagnostics["distractor_competition_nontrivial_pass"] is True


def test_positional_key_query_offset_selection_bundle_enforces_declared_diagnostics() -> None:
    bundle = generate_positional_key_query_offset_selection_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_positional_key_query_offset_selection_response"
    assert diagnostics["coarse_key_query_selection_state_null_pass"] is True
    assert diagnostics["within_key_query_selection_state_variation_pass"] is True
    assert diagnostics["candidate_set_nontrivial_pass"] is True
    assert diagnostics["target_selection_nontrivial_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["bounded_candidate_count_pass"] is True


def test_positional_dual_anchor_offset_consensus_bundle_enforces_declared_diagnostics() -> None:
    bundle = generate_positional_dual_anchor_offset_consensus_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_positional_dual_anchor_offset_consensus_response"
    assert diagnostics["coarse_dual_anchor_consensus_state_null_pass"] is True
    assert diagnostics["within_dual_anchor_consensus_state_variation_pass"] is True
    assert diagnostics["candidate_set_nontrivial_pass"] is True
    assert diagnostics["dual_anchor_target_nontrivial_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["bounded_candidate_count_pass"] is True
    assert diagnostics["dual_anchor_noncollapse_pass"] is True


def test_positional_variable_cardinality_offset_selection_bundle_enforces_declared_diagnostics() -> None:
    bundle = generate_positional_variable_cardinality_offset_selection_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_positional_variable_cardinality_offset_selection_response"
    assert diagnostics["coarse_variable_cardinality_state_null_pass"] is True
    assert diagnostics["within_variable_cardinality_state_variation_pass"] is True
    assert diagnostics["candidate_count_range_nontrivial_pass"] is True
    assert diagnostics["variable_cardinality_target_nontrivial_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["bounded_candidate_count_pass"] is True
    assert diagnostics["distractor_insertion_nontrivial_pass"] is True
    assert diagnostics["cross_count_target_stability_pass"] is True


def test_positional_content_gated_offset_selection_bundle_enforces_declared_diagnostics() -> None:
    bundle = generate_positional_content_gated_offset_selection_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_positional_content_gated_offset_selection_response"
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


def test_positional_content_alias_disambiguation_bundle_enforces_declared_diagnostics() -> None:
    bundle = generate_positional_content_alias_disambiguation_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_positional_content_alias_disambiguation_response"
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


def test_positional_reference_revision_selection_bundle_enforces_declared_diagnostics() -> None:
    bundle = generate_positional_reference_revision_selection_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_positional_reference_revision_selection_response"
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


def test_positional_exception_conditioned_reference_selection_bundle_enforces_declared_diagnostics() -> None:
    bundle = generate_positional_exception_conditioned_reference_selection_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_positional_exception_conditioned_reference_selection_response"
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


def test_positional_shared_memory_multi_query_selection_bundle_enforces_declared_diagnostics() -> None:
    bundle = generate_positional_shared_memory_multi_query_selection_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_positional_shared_memory_multi_query_selection_response"
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


def test_positional_intermediate_pointer_selection_bundle_enforces_declared_diagnostics() -> None:
    bundle = generate_positional_intermediate_pointer_selection_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_positional_intermediate_pointer_selection_response"
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


def test_symbolic_insufficiency_loop_bundle_enforces_declared_diagnostics() -> None:
    bundle = generate_symbolic_insufficiency_loop_closure_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_symbolic_insufficiency_loop_closure_response"
    assert diagnostics["coarse_loop_state_null_pass"] is True
    assert diagnostics["within_loop_state_variation_pass"] is True
    assert diagnostics["latent_loop_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["loop_length_balance_pass"] is True
    assert diagnostics["closure_target_nontrivial_pass"] is True


def test_symbolic_insufficiency_fork_join_bundle_enforces_declared_diagnostics() -> None:
    bundle = generate_symbolic_insufficiency_fork_join_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_symbolic_insufficiency_fork_join_response"
    assert diagnostics["coarse_fork_state_null_pass"] is True
    assert diagnostics["within_fork_state_variation_pass"] is True
    assert diagnostics["latent_fork_diversity_pass"] is True
    assert diagnostics["branch_balance_pass"] is True
    assert diagnostics["rejoin_target_nontrivial_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True


def test_symbolic_insufficiency_braid_bundle_enforces_declared_diagnostics() -> None:
    bundle = generate_symbolic_insufficiency_braid_crossing_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_symbolic_insufficiency_braid_crossing_response"
    assert diagnostics["coarse_braid_state_null_pass"] is True
    assert diagnostics["within_braid_state_variation_pass"] is True
    assert diagnostics["latent_braid_diversity_pass"] is True
    assert diagnostics["crossing_target_nontrivial_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["channel_balance_pass"] is True


def test_token_orientation_name_is_pair_relational() -> None:
    assert token_orientation_name("A", "B") == "forward"
    assert token_orientation_name("A", "C") == "forward"
    assert token_orientation_name("A", "D") == "reverse"
    assert token_orientation_name("C", "A") == "forward"


def test_dual_content_parity_coupling_bundle_is_balanced() -> None:
    bundle = generate_dual_content_parity_coupling_binary_bundle(seed=42)
    for split in ("train", "validation", "test"):
        summary = bundle.diagnostics["splits"][split]
        assert summary["class_balance_ok"] is True
        assert summary["sector_pair_balance_ok"] is True
        assert summary["sector_slot_balance_ok"] is True
        assert summary["content_slot_balance_ok"] is True
        assert summary["orientation_slot_balance_ok"] is True


def test_dual_content_parity_coupling_labels_follow_even_parity_rule() -> None:
    bundle = generate_dual_content_parity_coupling_binary_bundle(seed=42)
    rows = bundle.train[:10] + bundle.validation[:10] + bundle.test[:10]
    positive_sectors = {"P_small", "P_large"}
    for text, label in rows:
        parts = {item.split(":", 1)[0]: item.split(":", 1)[1] for item in text.split()}
        sector_a = ("P_small" if 0 < int(parts["a_off"]) <= 2 else
                    "P_large" if int(parts["a_off"]) > 0 else
                    "N_small" if abs(int(parts["a_off"])) <= 2 else "N_large")
        sector_b = ("P_small" if 0 < int(parts["b_off"]) <= 2 else
                    "P_large" if int(parts["b_off"]) > 0 else
                    "N_small" if abs(int(parts["b_off"])) <= 2 else "N_large")
        sign_agreement = (sector_a in positive_sectors) == (sector_b in positive_sectors)
        content_agreement = content_family_name(parts["a_lt"], parts["a_rt"]) == content_family_name(
            parts["b_lt"], parts["b_rt"]
        )
        orientation_agreement = token_orientation_name(parts["a_lt"], parts["a_rt"]) == token_orientation_name(
            parts["b_lt"], parts["b_rt"]
        )
        parity = int(sign_agreement) ^ int(content_agreement) ^ int(orientation_agreement)
        assert label == (1 if parity == 0 else 0)


def test_symbolic_insufficiency_bundle_enforces_declared_diagnostics() -> None:
    bundle = generate_symbolic_insufficiency_transition_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["coarse_state_null_pass"] is True
    assert diagnostics["within_state_variation_pass"] is True
    assert diagnostics["latent_path_diversity_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True


def test_dual_continuous_coupled_response_bundle_is_balanced() -> None:
    bundle = generate_dual_continuous_coupled_response_bundle(seed=42)
    for split in ("train", "validation", "test"):
        summary = bundle.diagnostics["splits"][split]
        assert summary["sector_pair_balance_ok"] is True
        assert summary["sector_slot_balance_ok"] is True
        assert summary["content_slot_balance_ok"] is True
        assert summary["orientation_slot_balance_ok"] is True
    assert -1.0 <= summary["target_min"] <= summary["target_max"] <= 1.0


def test_chart_transition_token_invariant_bundle_emits_required_latent_diagnostics() -> None:
    bundle = generate_chart_transition_token_invariant_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_chart_transition_token_invariant_response"
    assert diagnostics["latent_target_invariance_pass"] is True
    assert diagnostics["latent_target_max_abs_delta"] == 0.0
    assert diagnostics["latent_render_pair_count"] > 0
    assert diagnostics["token_view_balance_pass"] is True
    assert diagnostics["token_view_counts"]["train"]["identity"] == diagnostics["token_view_counts"]["train"]["cdab"]
    assert diagnostics["token_view_counts"]["validation"]["identity"] == diagnostics["token_view_counts"]["validation"]["cdab"]
    assert diagnostics["token_view_counts"]["test"]["identity"] == diagnostics["token_view_counts"]["test"]["cdab"]


def test_chart_transition_orbit_bundle_emits_required_orbit_diagnostics() -> None:
    bundle = generate_chart_transition_orbit_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_chart_transition_orbit_response"
    assert diagnostics["orbit_target_invariance_pass"] is True
    assert diagnostics["orbit_target_max_abs_delta"] == 0.0
    assert diagnostics["orbit_canonical_balance_pass"] is True


def test_transition_orbit_rank_band_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_rank_band_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_rank_band_response"
    assert diagnostics["coarse_rank_lookup_near_null_pass"] is True
    assert diagnostics["within_state_rank_band_count_min"] >= 3
    assert diagnostics["rank_band_balance_pass"] is True
    assert diagnostics["splits"]["validation"]["target_max"] > diagnostics["splits"]["validation"]["target_min"]
    assert diagnostics["splits"]["test"]["target_max"] > diagnostics["splits"]["test"]["target_min"]


def test_transition_orbit_pairwise_order_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_pairwise_order_binary_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_pairwise_order_binary"
    assert diagnostics["coarse_order_lookup_near_null_pass"] is True
    assert diagnostics["within_state_pair_count_min"] >= 2
    assert diagnostics["pair_label_balance_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True


def test_transition_orbit_listwise_ranking_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_listwise_ranking_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_listwise_ranking"
    assert diagnostics["coarse_list_lookup_near_null_pass"] is True
    assert diagnostics["within_state_list_count_min"] >= 2
    assert diagnostics["rank_position_balance_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True


def test_transition_orbit_order_margin_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_order_margin_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_order_margin_response"
    assert diagnostics["coarse_margin_lookup_near_null_pass"] is True
    assert diagnostics["within_state_margin_variation_pass"] is True
    assert diagnostics["top1_only_shortcut_absent"] is True
    assert diagnostics["token_view_balance_pass"] is True


def test_transition_orbit_signed_margin_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_signed_margin_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_signed_margin_response"
    assert diagnostics["coarse_signed_margin_lookup_near_null_pass"] is True
    assert diagnostics["within_state_signed_margin_variation_pass"] is True
    assert diagnostics["signed_margin_balance_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True


def test_transition_orbit_sign_only_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_sign_only_binary_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_sign_only_binary"
    assert diagnostics["coarse_sign_lookup_near_null_pass"] is True
    assert diagnostics["within_state_sign_variation_pass"] is True
    assert diagnostics["sign_label_balance_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True


def test_transition_orbit_sign_consistency_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_sign_consistency_binary_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_sign_consistency_binary"
    assert diagnostics["coarse_consistency_lookup_near_null_pass"] is True
    assert diagnostics["within_state_consistency_variation_pass"] is True
    assert diagnostics["paired_context_diversity_pass"] is True
    assert diagnostics["consistency_label_balance_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True


def test_transition_orbit_sign_flip_contrast_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_sign_flip_contrast_binary_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_sign_flip_contrast_binary"
    assert diagnostics["coarse_flip_lookup_near_null_pass"] is True
    assert diagnostics["within_state_flip_variation_pass"] is True
    assert diagnostics["paired_context_diversity_pass"] is True
    assert diagnostics["flip_label_balance_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True


def test_transition_orbit_asymmetric_sign_localization_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_asymmetric_sign_localization_binary_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_asymmetric_sign_localization_binary"
    assert diagnostics["coarse_localization_lookup_near_null_pass"] is True
    assert diagnostics["within_state_localization_variation_pass"] is True
    assert diagnostics["paired_channel_diversity_pass"] is True
    assert diagnostics["localization_label_balance_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True


def test_transition_orbit_channel_advantage_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_channel_advantage_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_channel_advantage_response"
    assert diagnostics["coarse_channel_advantage_lookup_near_null_pass"] is True
    assert diagnostics["within_state_channel_advantage_variation_pass"] is True
    assert diagnostics["paired_channel_diversity_pass"] is True
    assert diagnostics["channel_advantage_balance_pass"] is True
    assert diagnostics["token_view_balance_pass"] is True


def test_transition_orbit_channel_order_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_channel_order_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_channel_order_response"
    assert diagnostics["coarse_channel_order_lookup_near_null_pass"] is True
    assert diagnostics["within_state_channel_order_variation_pass"] is True
    assert diagnostics["paired_channel_diversity_pass"] is True
    assert diagnostics["channel_order_balance_pass"] is True


def test_transition_orbit_slot_invariant_channel_order_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_slot_invariant_channel_order_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_slot_invariant_channel_order_response"
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_order_lookup_near_null_pass"] is True


def test_transition_orbit_slot_invariant_channel_order_margin_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_slot_invariant_channel_order_margin_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_slot_invariant_channel_order_margin_response"
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_margin_lookup_near_null_pass"] is True
    assert diagnostics["within_state_margin_variation_pass"] is True


def test_transition_orbit_slot_invariant_channel_order_rank_only_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_slot_invariant_channel_order_rank_only_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_slot_invariant_channel_order_rank_only"
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_rank_lookup_near_null_pass"] is True
    assert diagnostics["within_state_rank_variation_pass"] is True


def test_transition_orbit_slot_invariant_channel_order_topk_consistency_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_slot_invariant_channel_order_topk_consistency_binary_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_slot_invariant_channel_order_topk_consistency_binary"
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_lookup_near_null_pass"] is True
    assert diagnostics["within_state_topk_variation_pass"] is True


def test_transition_orbit_slot_invariant_channel_order_topk_margin_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_slot_invariant_channel_order_topk_margin_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_slot_invariant_channel_order_topk_margin_response"
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_margin_lookup_near_null_pass"] is True
    assert diagnostics["within_state_topk_margin_variation_pass"] is True


def test_transition_orbit_slot_invariant_channel_order_topk_rank_only_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_slot_invariant_channel_order_topk_rank_only_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_slot_invariant_channel_order_topk_rank_only"
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_rank_lookup_near_null_pass"] is True
    assert diagnostics["within_state_topk_rank_variation_pass"] is True


def test_transition_orbit_slot_invariant_channel_order_topk_preference_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_slot_invariant_channel_order_topk_preference_binary_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_slot_invariant_channel_order_topk_preference_binary"
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_preference_lookup_near_null_pass"] is True
    assert diagnostics["within_state_topk_preference_variation_pass"] is True


def test_transition_orbit_slot_invariant_topk_pair_margin_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_slot_invariant_topk_pair_margin_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_slot_invariant_topk_pair_margin_response"
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0.0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_pair_margin_lookup_near_null_pass"] is True
    assert diagnostics["within_state_topk_pair_margin_variation_pass"] is True


def test_transition_orbit_slot_invariant_topk_pair_order_agreement_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_slot_invariant_topk_pair_order_agreement_binary_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_slot_invariant_topk_pair_order_agreement_binary"
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0.0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_pair_order_lookup_near_null_pass"] is True
    assert diagnostics["within_state_topk_pair_order_variation_pass"] is True


def test_transition_orbit_slot_invariant_topk_pair_order_signed_consistency_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_slot_invariant_topk_pair_order_signed_consistency_binary_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_consistency_binary"
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0.0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_pair_signed_consistency_lookup_near_null_pass"] is True
    assert diagnostics["within_state_topk_pair_signed_consistency_variation_pass"] is True
    assert diagnostics["paired_context_diversity_pass"] is True
    assert diagnostics["signed_consistency_label_balance_pass"] is True


def test_transition_orbit_slot_invariant_topk_pair_order_signed_flip_consistency_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_slot_invariant_topk_pair_order_signed_flip_consistency_binary_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_consistency_binary"
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0.0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_pair_signed_flip_lookup_near_null_pass"] is True
    assert diagnostics["within_state_topk_pair_signed_flip_variation_pass"] is True
    assert diagnostics["paired_context_diversity_pass"] is True
    assert diagnostics["signed_flip_label_balance_pass"] is True


def test_transition_orbit_slot_invariant_topk_pair_order_signed_flip_stability_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_slot_invariant_topk_pair_order_signed_flip_stability_binary_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_stability_binary"
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0.0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_pair_signed_flip_stability_lookup_near_null_pass"] is True
    assert diagnostics["within_state_topk_pair_signed_flip_stability_variation_pass"] is True
    assert diagnostics["paired_context_diversity_pass"] is True
    assert diagnostics["signed_flip_stability_label_balance_pass"] is True


def test_transition_orbit_slot_invariant_topk_pair_order_signed_flip_persistence_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_slot_invariant_topk_pair_order_signed_flip_persistence_binary_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_persistence_binary"
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0.0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_pair_signed_flip_persistence_lookup_near_null_pass"] is True
    assert diagnostics["within_state_topk_pair_signed_flip_persistence_variation_pass"] is True
    assert diagnostics["paired_context_diversity_pass"] is True
    assert diagnostics["signed_flip_persistence_label_balance_pass"] is True


def test_transition_orbit_slot_invariant_topk_pair_order_signed_flip_recurrence_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_slot_invariant_topk_pair_order_signed_flip_recurrence_binary_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_recurrence_binary"
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0.0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_pair_signed_flip_recurrence_lookup_near_null_pass"] is True
    assert diagnostics["within_state_topk_pair_signed_flip_recurrence_variation_pass"] is True
    assert diagnostics["paired_context_diversity_pass"] is True
    assert diagnostics["signed_flip_recurrence_label_balance_pass"] is True


def test_transition_orbit_slot_invariant_topk_pair_order_signed_flip_reversion_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_slot_invariant_topk_pair_order_signed_flip_reversion_binary_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_reversion_binary"
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0.0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_pair_signed_flip_reversion_lookup_near_null_pass"] is True
    assert diagnostics["within_state_topk_pair_signed_flip_reversion_variation_pass"] is True
    assert diagnostics["paired_context_diversity_pass"] is True
    assert diagnostics["signed_flip_reversion_label_balance_pass"] is True


def test_transition_orbit_slot_invariant_topk_pair_order_signed_flip_hysteresis_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_slot_invariant_topk_pair_order_signed_flip_hysteresis_binary_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_hysteresis_binary"
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0.0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_pair_signed_flip_hysteresis_lookup_near_null_pass"] is True
    assert diagnostics["within_state_topk_pair_signed_flip_hysteresis_variation_pass"] is True
    assert diagnostics["paired_context_diversity_pass"] is True
    assert diagnostics["signed_flip_hysteresis_label_balance_pass"] is True


def test_transition_orbit_slot_invariant_topk_pair_order_signed_flip_memory_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_slot_invariant_topk_pair_order_signed_flip_memory_binary_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_memory_binary"
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0.0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_pair_signed_flip_memory_lookup_near_null_pass"] is True
    assert diagnostics["within_state_topk_pair_signed_flip_memory_variation_pass"] is True
    assert diagnostics["paired_context_diversity_pass"] is True
    assert diagnostics["signed_flip_memory_label_balance_pass"] is True


def test_transition_orbit_slot_invariant_topk_pair_order_stability_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_slot_invariant_topk_pair_order_stability_binary_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_slot_invariant_topk_pair_order_stability_binary"
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0.0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_pair_stability_lookup_near_null_pass"] is True
    assert diagnostics["within_state_topk_pair_stability_variation_pass"] is True


def test_transition_orbit_slot_invariant_topk_pair_order_drift_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_slot_invariant_topk_pair_order_drift_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_slot_invariant_topk_pair_order_drift_response"
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0.0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_pair_drift_lookup_near_null_pass"] is True
    assert diagnostics["within_state_topk_pair_drift_variation_pass"] is True


def test_transition_orbit_slot_invariant_topk_pair_order_signed_drift_bundle_emits_required_diagnostics() -> None:
    bundle = generate_transition_orbit_slot_invariant_topk_pair_order_signed_drift_response_bundle(seed=42)
    diagnostics = bundle.diagnostics
    assert diagnostics["dataset"] == "synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_drift_response"
    assert diagnostics["latent_slot_invariance_pass"] is True
    assert diagnostics["latent_slot_max_abs_delta"] == 0.0
    assert diagnostics["slot_view_balance_pass"] is True
    assert diagnostics["coarse_slot_topk_pair_signed_drift_lookup_near_null_pass"] is True
    assert diagnostics["within_state_topk_pair_signed_drift_variation_pass"] is True


def test_dual_continuous_coupled_response_labels_follow_rule() -> None:
    bundle = generate_dual_continuous_coupled_response_bundle(seed=42)
    rows = bundle.train[:10] + bundle.validation[:10] + bundle.test[:10]
    positive_sectors = {"P_small", "P_large"}
    for text, label in rows:
        parts = {item.split(":", 1)[0]: item.split(":", 1)[1] for item in text.split()}
        sector_a = ("P_small" if 0 < int(parts["a_off"]) <= 2 else
                    "P_large" if int(parts["a_off"]) > 0 else
                    "N_small" if abs(int(parts["a_off"])) <= 2 else "N_large")
        sector_b = ("P_small" if 0 < int(parts["b_off"]) <= 2 else
                    "P_large" if int(parts["b_off"]) > 0 else
                    "N_small" if abs(int(parts["b_off"])) <= 2 else "N_large")
        sign_term = 1.0 if ((sector_a in positive_sectors) == (sector_b in positive_sectors)) else -1.0
        content_term = 1.0 if content_family_name(parts["a_lt"], parts["a_rt"]) == content_family_name(
            parts["b_lt"], parts["b_rt"]
        ) else -1.0
        orientation_term = 1.0 if token_orientation_name(parts["a_lt"], parts["a_rt"]) == token_orientation_name(
            parts["b_lt"], parts["b_rt"]
        ) else -1.0
        expected = round(0.8 * (0.5 * sign_term + 0.3 * content_term + 0.2 * orientation_term)
                         + 0.2 * (sign_term * content_term * orientation_term), 6)
        assert label == expected


def test_dual_state_sensitive_continuous_response_bundle_preserves_within_state_variation() -> None:
    bundle = generate_dual_state_sensitive_continuous_response_bundle(seed=42)
    for split in ("train", "validation", "test"):
        summary = bundle.diagnostics["splits"][split]
        assert summary["sector_pair_balance_ok"] is True
        assert summary["sector_slot_balance_ok"] is True
        assert summary["content_slot_balance_ok"] is True
        assert summary["orientation_slot_balance_ok"] is True
        assert summary["within_state_variation_ok"] is True


def test_dual_state_sensitive_continuous_response_labels_follow_rule() -> None:
    bundle = generate_dual_state_sensitive_continuous_response_bundle(seed=42)
    rows = bundle.train[:10] + bundle.validation[:10] + bundle.test[:10]
    positive_sectors = {"P_small", "P_large"}
    token_index = {"A": 0, "B": 1, "C": 2, "D": 3}
    for text, label in rows:
        parts = {item.split(":", 1)[0]: item.split(":", 1)[1] for item in text.split()}
        sector_a = ("P_small" if 0 < int(parts["a_off"]) <= 2 else
                    "P_large" if int(parts["a_off"]) > 0 else
                    "N_small" if abs(int(parts["a_off"])) <= 2 else "N_large")
        sector_b = ("P_small" if 0 < int(parts["b_off"]) <= 2 else
                    "P_large" if int(parts["b_off"]) > 0 else
                    "N_small" if abs(int(parts["b_off"])) <= 2 else "N_large")
        sign_term = 1.0 if ((sector_a in positive_sectors) == (sector_b in positive_sectors)) else -1.0
        content_term = 1.0 if content_family_name(parts["a_lt"], parts["a_rt"]) == content_family_name(
            parts["b_lt"], parts["b_rt"]
        ) else -1.0
        orientation_term = 1.0 if token_orientation_name(parts["a_lt"], parts["a_rt"]) == token_orientation_name(
            parts["b_lt"], parts["b_rt"]
        ) else -1.0
        sector_magnitude_delta = round((abs(int(parts["a_off"])) - abs(int(parts["b_off"]))) / 3.0, 6)
        score_a = (token_index[parts["a_lt"]] - token_index[parts["a_rt"]]) / 3.0
        score_b = (token_index[parts["b_lt"]] - token_index[parts["b_rt"]]) / 3.0
        ordered_content_delta = round(0.5 * (score_a - score_b), 6)
        expected = round(
            0.25 * sign_term
            + 0.15 * content_term
            + 0.10 * orientation_term
            + 0.15 * sector_magnitude_delta
            + 0.10 * ordered_content_delta
            + 0.15 * (sign_term * sector_magnitude_delta)
            + 0.10 * (content_term * ordered_content_delta),
            6,
        )
        assert label == expected


def test_dual_orthogonalized_continuous_response_bundle_centers_coarse_tuple_means() -> None:
    bundle = generate_dual_orthogonalized_continuous_response_bundle(seed=42)
    for split in ("train", "validation", "test"):
        summary = bundle.diagnostics["splits"][split]
        assert summary["within_state_variation_ok"] is True
        assert summary["coarse_tuple_mean_abs_max"] <= 1e-6


def test_dual_nonlinear_manifold_response_bundle_centers_coarse_tuple_means() -> None:
    bundle = generate_dual_nonlinear_manifold_response_bundle(seed=42)
    for split in ("train", "validation", "test"):
        summary = bundle.diagnostics["splits"][split]
        assert summary["within_state_variation_ok"] is True
        assert summary["coarse_tuple_mean_abs_max"] <= 1e-6
        assert summary["target_min"] < summary["target_max"]


def test_dual_phase_sensitive_manifold_response_bundle_centers_coarse_tuple_means() -> None:
    bundle = generate_dual_phase_sensitive_manifold_response_bundle(seed=42)
    for split in ("train", "validation", "test"):
        summary = bundle.diagnostics["splits"][split]
        assert summary["within_state_variation_ok"] is True
        assert summary["coarse_tuple_mean_abs_max"] <= 1e-6
        assert summary["target_min"] < summary["target_max"]


def test_dual_latent_phase_manifold_residual_response_bundle_centers_coarse_tuple_means() -> None:
    bundle = generate_dual_latent_phase_manifold_residual_response_bundle(seed=42)
    for split in ("train", "validation", "test"):
        summary = bundle.diagnostics["splits"][split]
        assert summary["within_state_variation_ok"] is True
        assert summary["coarse_tuple_mean_abs_max"] <= 1e-6
        assert summary["target_min"] < summary["target_max"]


def test_dual_local_atlas_manifold_response_bundle_centers_coarse_tuple_means() -> None:
    bundle = generate_dual_local_atlas_manifold_response_bundle(seed=42)
    for split in ("train", "validation", "test"):
        summary = bundle.diagnostics["splits"][split]
        assert summary["within_state_variation_ok"] is True
        assert summary["coarse_tuple_mean_abs_max"] <= 1e-6
        assert summary["target_min"] < summary["target_max"]


def test_dual_chart_transition_manifold_response_bundle_centers_coarse_tuple_means() -> None:
    bundle = generate_dual_chart_transition_manifold_response_bundle(seed=42)
    for split in ("train", "validation", "test"):
        summary = bundle.diagnostics["splits"][split]
        assert summary["within_state_variation_ok"] is True
        assert summary["coarse_tuple_mean_abs_max"] <= 1e-6
        assert summary["target_min"] < summary["target_max"]
