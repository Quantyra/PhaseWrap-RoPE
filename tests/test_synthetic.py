from qrope.synthetic import (
    content_family_name,
    generate_chart_transition_token_invariant_response_bundle,
    generate_chart_transition_orbit_response_bundle,
    generate_transition_orbit_rank_band_response_bundle,
    generate_dual_continuous_coupled_response_bundle,
    generate_dual_latent_phase_manifold_residual_response_bundle,
    generate_dual_local_atlas_manifold_response_bundle,
    generate_dual_chart_transition_manifold_response_bundle,
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
