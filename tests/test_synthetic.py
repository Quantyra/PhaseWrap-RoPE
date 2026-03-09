from qrope.synthetic import (
    generate_dual_sector_agreement_binary_bundle,
    generate_sector_parity_binary_bundle,
    generate_signed_offset_binary_bundle,
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
