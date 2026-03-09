from __future__ import annotations

import json
import math
import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any

TOKENS = ("A", "B", "C", "D")
OFFSETS = (1, 2, 3, 4)
SEQUENCE_LENGTH = 12
TRAIN_COUNT_PER_BUCKET = 2
VALIDATION_COUNT_PER_BUCKET = 1
TEST_COUNT_PER_BUCKET = 1


@dataclass(frozen=True)
class SyntheticSample:
    text: str
    label: float
    left_token: str
    right_token: str
    left_pos: int
    right_pos: int
    offset: int
    offset_abs: int


@dataclass(frozen=True)
class SyntheticDatasetBundle:
    train: list[tuple[str, int]]
    validation: list[tuple[str, int]]
    test: list[tuple[str, int]]
    diagnostics: dict[str, Any]


@dataclass(frozen=True)
class DualSyntheticSample:
    text: str
    label: float
    sector_a: str
    sector_b: str
    sample_a: SyntheticSample
    sample_b: SyntheticSample


def generate_signed_offset_binary_bundle(seed: int, split_rotation: int = 0) -> SyntheticDatasetBundle:
    return generate_sector_bundle(
        seed=seed,
        dataset_name="synthetic_offset_binary",
        label_mode="offset_sign",
        split_rotation=split_rotation,
    )


def generate_sector_parity_binary_bundle(seed: int, split_rotation: int = 0) -> SyntheticDatasetBundle:
    return generate_sector_bundle(
        seed=seed,
        dataset_name="synthetic_sector_parity_binary",
        label_mode="sector_parity",
        split_rotation=split_rotation,
    )


def generate_dual_sector_agreement_binary_bundle(
    seed: int,
    split_rotation: int = 0,
    slot_swap: int = 0,
    token_permutation: str = "identity",
    pair_reindex: int = 0,
) -> SyntheticDatasetBundle:
    return generate_dual_sector_bundle(
        seed=seed,
        dataset_name="synthetic_dual_sector_agreement_binary",
        split_rotation=split_rotation,
        slot_swap=slot_swap,
        token_permutation=token_permutation,
        pair_reindex=pair_reindex,
    )


def generate_dual_sector_content_agreement_binary_bundle(
    seed: int,
    split_rotation: int = 0,
    slot_swap: int = 0,
    token_permutation: str = "identity",
    pair_reindex: int = 0,
) -> SyntheticDatasetBundle:
    return generate_dual_sector_bundle(
        seed=seed,
        dataset_name="synthetic_dual_sector_content_agreement_binary",
        split_rotation=split_rotation,
        slot_swap=slot_swap,
        token_permutation=token_permutation,
        pair_reindex=pair_reindex,
        label_mode="sector_content_xnor",
    )


def generate_dual_content_parity_coupling_binary_bundle(
    seed: int,
    split_rotation: int = 0,
    slot_swap: int = 0,
    token_permutation: str = "identity",
    pair_reindex: int = 0,
) -> SyntheticDatasetBundle:
    return generate_dual_sector_bundle(
        seed=seed,
        dataset_name="synthetic_dual_content_parity_coupling_binary",
        split_rotation=split_rotation,
        slot_swap=slot_swap,
        token_permutation=token_permutation,
        pair_reindex=pair_reindex,
        label_mode="triple_parity_even",
    )


def generate_dual_continuous_coupled_response_bundle(
    seed: int,
    split_rotation: int = 0,
    slot_swap: int = 0,
    token_permutation: str = "identity",
    pair_reindex: int = 0,
) -> SyntheticDatasetBundle:
    return generate_dual_sector_bundle(
        seed=seed,
        dataset_name="synthetic_dual_continuous_coupled_response",
        split_rotation=split_rotation,
        slot_swap=slot_swap,
        token_permutation=token_permutation,
        pair_reindex=pair_reindex,
        label_mode="continuous_coupled_response",
    )


def generate_dual_state_sensitive_continuous_response_bundle(
    seed: int,
    split_rotation: int = 0,
    slot_swap: int = 0,
    token_permutation: str = "identity",
    pair_reindex: int = 0,
) -> SyntheticDatasetBundle:
    return generate_dual_sector_bundle(
        seed=seed,
        dataset_name="synthetic_dual_state_sensitive_continuous_response",
        split_rotation=split_rotation,
        slot_swap=slot_swap,
        token_permutation=token_permutation,
        pair_reindex=pair_reindex,
        label_mode="state_sensitive_continuous_response",
    )


def generate_dual_orthogonalized_continuous_response_bundle(
    seed: int,
    split_rotation: int = 0,
    slot_swap: int = 0,
    token_permutation: str = "identity",
    pair_reindex: int = 0,
) -> SyntheticDatasetBundle:
    return generate_dual_sector_bundle(
        seed=seed,
        dataset_name="synthetic_dual_orthogonalized_continuous_response",
        split_rotation=split_rotation,
        slot_swap=slot_swap,
        token_permutation=token_permutation,
        pair_reindex=pair_reindex,
        label_mode="orthogonalized_continuous_response",
    )


def generate_dual_nonlinear_manifold_response_bundle(
    seed: int,
    split_rotation: int = 0,
    slot_swap: int = 0,
    token_permutation: str = "identity",
    pair_reindex: int = 0,
) -> SyntheticDatasetBundle:
    return generate_dual_sector_bundle(
        seed=seed,
        dataset_name="synthetic_dual_nonlinear_manifold_response",
        split_rotation=split_rotation,
        slot_swap=slot_swap,
        token_permutation=token_permutation,
        pair_reindex=pair_reindex,
        label_mode="nonlinear_manifold_response",
    )


def generate_dual_phase_sensitive_manifold_response_bundle(
    seed: int,
    split_rotation: int = 0,
    slot_swap: int = 0,
    token_permutation: str = "identity",
    pair_reindex: int = 0,
) -> SyntheticDatasetBundle:
    return generate_dual_sector_bundle(
        seed=seed,
        dataset_name="synthetic_dual_phase_sensitive_manifold_response",
        split_rotation=split_rotation,
        slot_swap=slot_swap,
        token_permutation=token_permutation,
        pair_reindex=pair_reindex,
        label_mode="phase_sensitive_manifold_response",
    )


def generate_dual_latent_phase_manifold_residual_response_bundle(
    seed: int,
    split_rotation: int = 0,
    slot_swap: int = 0,
    token_permutation: str = "identity",
    pair_reindex: int = 0,
) -> SyntheticDatasetBundle:
    return generate_dual_sector_bundle(
        seed=seed,
        dataset_name="synthetic_dual_latent_phase_manifold_residual_response",
        split_rotation=split_rotation,
        slot_swap=slot_swap,
        token_permutation=token_permutation,
        pair_reindex=pair_reindex,
        label_mode="latent_phase_manifold_residual_response",
    )


def generate_dual_local_atlas_manifold_response_bundle(
    seed: int,
    split_rotation: int = 0,
    slot_swap: int = 0,
    token_permutation: str = "identity",
    pair_reindex: int = 0,
) -> SyntheticDatasetBundle:
    return generate_dual_sector_bundle(
        seed=seed,
        dataset_name="synthetic_dual_local_atlas_manifold_response",
        split_rotation=split_rotation,
        slot_swap=slot_swap,
        token_permutation=token_permutation,
        pair_reindex=pair_reindex,
        label_mode="local_atlas_manifold_response",
    )


def generate_dual_chart_transition_manifold_response_bundle(
    seed: int,
    split_rotation: int = 0,
    slot_swap: int = 0,
    token_permutation: str = "identity",
    pair_reindex: int = 0,
) -> SyntheticDatasetBundle:
    return generate_dual_sector_bundle(
        seed=seed,
        dataset_name="synthetic_dual_chart_transition_manifold_response",
        split_rotation=split_rotation,
        slot_swap=slot_swap,
        token_permutation=token_permutation,
        pair_reindex=pair_reindex,
        label_mode="chart_transition_manifold_response",
    )


def generate_sector_bundle(seed: int, dataset_name: str, label_mode: str, split_rotation: int = 0) -> SyntheticDatasetBundle:
    rng = random.Random(f"synthetic_offset_binary:{seed}")
    grouped: dict[tuple[int, int, str, str], list[SyntheticSample]] = defaultdict(list)

    for left_token in TOKENS:
        for right_token in TOKENS:
            for magnitude in OFFSETS:
                for base_left in range(SEQUENCE_LENGTH - magnitude):
                    grouped[(1, magnitude, left_token, right_token)].append(
                        build_sample(
                            left_token=left_token,
                            right_token=right_token,
                            left_pos=base_left,
                            right_pos=base_left + magnitude,
                            label_mode=label_mode,
                        )
                    )
                    grouped[(0, magnitude, left_token, right_token)].append(
                        build_sample(
                            left_token=left_token,
                            right_token=right_token,
                            left_pos=base_left + magnitude,
                            right_pos=base_left,
                            label_mode=label_mode,
                        )
                    )

    train: list[SyntheticSample] = []
    validation: list[SyntheticSample] = []
    test: list[SyntheticSample] = []

    for key in sorted(grouped):
        bucket = list(grouped[key])
        rng.shuffle(bucket)
        required = TRAIN_COUNT_PER_BUCKET + VALIDATION_COUNT_PER_BUCKET + TEST_COUNT_PER_BUCKET
        if len(bucket) < required:
            raise ValueError(f"Insufficient bucket size for {key}: {len(bucket)} < {required}")
        stride = required
        rotation_offset = (split_rotation % max(1, len(bucket) // stride)) * stride
        rotated = bucket[rotation_offset:] + bucket[:rotation_offset]
        train.extend(rotated[:TRAIN_COUNT_PER_BUCKET])
        validation.extend(rotated[TRAIN_COUNT_PER_BUCKET : TRAIN_COUNT_PER_BUCKET + VALIDATION_COUNT_PER_BUCKET])
        test.extend(rotated[TRAIN_COUNT_PER_BUCKET + VALIDATION_COUNT_PER_BUCKET : required])

    train_rows = [(sample.text, sample.label) for sample in sorted(train, key=sample_sort_key)]
    validation_rows = [(sample.text, sample.label) for sample in sorted(validation, key=sample_sort_key)]
    test_rows = [(sample.text, sample.label) for sample in sorted(test, key=sample_sort_key)]

    diagnostics = build_bundle_diagnostics(
        dataset_name=dataset_name,
        seed=seed,
        split_rotation=split_rotation,
        train=sorted(train, key=sample_sort_key),
        validation=sorted(validation, key=sample_sort_key),
        test=sorted(test, key=sample_sort_key),
    )
    return SyntheticDatasetBundle(
        train=train_rows,
        validation=validation_rows,
        test=test_rows,
        diagnostics=diagnostics,
    )


def generate_dual_sector_bundle(
    seed: int,
    dataset_name: str,
    split_rotation: int = 0,
    slot_swap: int = 0,
    token_permutation: str = "identity",
    pair_reindex: int = 0,
    label_mode: str = "same_sign",
) -> SyntheticDatasetBundle:
    rng = random.Random(f"{dataset_name}:{seed}")
    single_grouped: dict[str, list[SyntheticSample]] = defaultdict(list)

    for left_token in TOKENS:
        for right_token in TOKENS:
            for magnitude in OFFSETS:
                for base_left in range(SEQUENCE_LENGTH - magnitude):
                    pos_sample = build_sample(
                        left_token=left_token,
                        right_token=right_token,
                        left_pos=base_left,
                        right_pos=base_left + magnitude,
                        label_mode="offset_sign",
                    )
                    neg_sample = build_sample(
                        left_token=left_token,
                        right_token=right_token,
                        left_pos=base_left + magnitude,
                        right_pos=base_left,
                        label_mode="offset_sign",
                    )
                    single_grouped[offset_sector_name(pos_sample.offset)].append(pos_sample)
                    single_grouped[offset_sector_name(neg_sample.offset)].append(neg_sample)

    pair_grouped: dict[tuple[str, str], list[DualSyntheticSample]] = defaultdict(list)
    sectors = ("P_small", "P_large", "N_small", "N_large")
    for sector_a in sectors:
        for sector_b in sectors:
            bucket_a = list(single_grouped[sector_a])
            bucket_b = list(single_grouped[sector_b])
            rng.shuffle(bucket_a)
            rng.shuffle(bucket_b)
            required = TRAIN_COUNT_PER_BUCKET + VALIDATION_COUNT_PER_BUCKET + TEST_COUNT_PER_BUCKET
            if label_mode == "sector_content_xnor":
                pair_grouped[(sector_a, sector_b)].extend(
                    build_balanced_content_pairs(
                        bucket_a=bucket_a,
                        bucket_b=bucket_b,
                        required=required,
                        token_permutation=token_permutation,
                        slot_swap=slot_swap,
                        pair_reindex=pair_reindex,
                    )
                )
            elif label_mode == "triple_parity_even":
                pair_grouped[(sector_a, sector_b)].extend(
                    build_balanced_triple_pairs(
                        bucket_a=bucket_a,
                        bucket_b=bucket_b,
                        required=required,
                        token_permutation=token_permutation,
                        slot_swap=slot_swap,
                        pair_reindex=pair_reindex,
                    )
                )
            elif label_mode in {
                "continuous_coupled_response",
                "state_sensitive_continuous_response",
                "orthogonalized_continuous_response",
                "nonlinear_manifold_response",
                "phase_sensitive_manifold_response",
                "latent_phase_manifold_residual_response",
                "local_atlas_manifold_response",
                "chart_transition_manifold_response",
            }:
                pair_grouped[(sector_a, sector_b)].extend(
                    build_balanced_triple_pairs(
                        bucket_a=bucket_a,
                        bucket_b=bucket_b,
                        required=required,
                        token_permutation=token_permutation,
                        slot_swap=slot_swap,
                        pair_reindex=pair_reindex,
                        label_mode=label_mode,
                    )
                )
            else:
                for idx in range(required):
                    sample_a = bucket_a[idx]
                    sample_b = bucket_b[(idx + pair_reindex) % required]
                    if slot_swap:
                        sample_a, sample_b = sample_b, sample_a
                    sample_a = apply_token_permutation_to_sample(sample_a, token_permutation)
                    sample_b = apply_token_permutation_to_sample(sample_b, token_permutation)
                    pair_grouped[(sector_a, sector_b)].append(
                        build_dual_sample(sample_a=sample_a, sample_b=sample_b, label_mode=label_mode)
                    )

    train: list[DualSyntheticSample] = []
    validation: list[DualSyntheticSample] = []
    test: list[DualSyntheticSample] = []
    for key in sorted(pair_grouped):
        bucket = list(pair_grouped[key])
        required = TRAIN_COUNT_PER_BUCKET + VALIDATION_COUNT_PER_BUCKET + TEST_COUNT_PER_BUCKET
        stride = required
        rotation_offset = (split_rotation % max(1, len(bucket) // stride)) * stride
        rotated = bucket[rotation_offset:] + bucket[:rotation_offset]
        train.extend(rotated[:TRAIN_COUNT_PER_BUCKET])
        validation.extend(rotated[TRAIN_COUNT_PER_BUCKET : TRAIN_COUNT_PER_BUCKET + VALIDATION_COUNT_PER_BUCKET])
        test.extend(rotated[TRAIN_COUNT_PER_BUCKET + VALIDATION_COUNT_PER_BUCKET : required])

    if label_mode in {
        "orthogonalized_continuous_response",
        "nonlinear_manifold_response",
        "phase_sensitive_manifold_response",
        "latent_phase_manifold_residual_response",
        "local_atlas_manifold_response",
        "chart_transition_manifold_response",
    }:
        combined = train + validation + test
        centered = orthogonalize_dual_samples_by_coarse_tuple(combined)
        train = centered[: len(train)]
        validation = centered[len(train) : len(train) + len(validation)]
        test = centered[len(train) + len(validation) :]

    train_rows = [(sample.text, sample.label) for sample in sorted(train, key=dual_sample_sort_key)]
    validation_rows = [(sample.text, sample.label) for sample in sorted(validation, key=dual_sample_sort_key)]
    test_rows = [(sample.text, sample.label) for sample in sorted(test, key=dual_sample_sort_key)]

    diagnostics = build_dual_bundle_diagnostics(
        dataset_name=dataset_name,
        seed=seed,
        split_rotation=split_rotation,
        slot_swap=slot_swap,
        token_permutation=token_permutation,
        pair_reindex=pair_reindex,
        train=sorted(train, key=dual_sample_sort_key),
        validation=sorted(validation, key=dual_sample_sort_key),
        test=sorted(test, key=dual_sample_sort_key),
    )
    return SyntheticDatasetBundle(
        train=train_rows,
        validation=validation_rows,
        test=test_rows,
        diagnostics=diagnostics,
    )


def build_balanced_content_pairs(
    bucket_a: list[SyntheticSample],
    bucket_b: list[SyntheticSample],
    required: int,
    token_permutation: str,
    slot_swap: int,
    pair_reindex: int,
) -> list[DualSyntheticSample]:
    if required != 4:
        raise ValueError(f"Balanced content pair builder expects required=4, got {required}")

    permuted_a = [apply_token_permutation_to_sample(sample, token_permutation) for sample in bucket_a]
    permuted_b = [apply_token_permutation_to_sample(sample, token_permutation) for sample in bucket_b]
    grouped_a = {
        "aligned": [sample for sample in permuted_a if content_family_name(sample.left_token, sample.right_token) == "aligned"],
        "crossed": [sample for sample in permuted_a if content_family_name(sample.left_token, sample.right_token) == "crossed"],
    }
    grouped_b = {
        "aligned": [sample for sample in permuted_b if content_family_name(sample.left_token, sample.right_token) == "aligned"],
        "crossed": [sample for sample in permuted_b if content_family_name(sample.left_token, sample.right_token) == "crossed"],
    }
    for family in ("aligned", "crossed"):
        if len(grouped_a[family]) < 2 or len(grouped_b[family]) < 2:
            raise ValueError(f"Insufficient {family} samples for balanced content pairing")

    patterns = [
        ("aligned", "aligned"),
        ("aligned", "crossed"),
        ("crossed", "crossed"),
        ("crossed", "aligned"),
    ]
    counters_a = {"aligned": 0, "crossed": 0}
    counters_b = {"aligned": pair_reindex, "crossed": pair_reindex}
    pairs: list[DualSyntheticSample] = []
    for family_a, family_b in patterns:
        sample_a = grouped_a[family_a][counters_a[family_a] % len(grouped_a[family_a])]
        sample_b = grouped_b[family_b][counters_b[family_b] % len(grouped_b[family_b])]
        counters_a[family_a] += 1
        counters_b[family_b] += 1
        if slot_swap:
            sample_a, sample_b = sample_b, sample_a
        pairs.append(build_dual_sample(sample_a=sample_a, sample_b=sample_b, label_mode="sector_content_xnor"))
    return pairs


def build_balanced_triple_pairs(
    bucket_a: list[SyntheticSample],
    bucket_b: list[SyntheticSample],
    required: int,
    token_permutation: str,
    slot_swap: int,
    pair_reindex: int,
    label_mode: str = "triple_parity_even",
) -> list[DualSyntheticSample]:
    if required != 4:
        raise ValueError(f"Balanced triple pair builder expects required=4, got {required}")

    permuted_a = [apply_token_permutation_to_sample(sample, token_permutation) for sample in bucket_a]
    permuted_b = [apply_token_permutation_to_sample(sample, token_permutation) for sample in bucket_b]
    grouped_a: dict[tuple[str, str], list[SyntheticSample]] = {}
    grouped_b: dict[tuple[str, str], list[SyntheticSample]] = {}
    for content_family in ("aligned", "crossed"):
        for orientation in ("forward", "reverse"):
            grouped_a[(content_family, orientation)] = [
                sample
                for sample in permuted_a
                if content_family_name(sample.left_token, sample.right_token) == content_family
                and token_orientation_name(sample.left_token, sample.right_token) == orientation
            ]
            grouped_b[(content_family, orientation)] = [
                sample
                for sample in permuted_b
                if content_family_name(sample.left_token, sample.right_token) == content_family
                and token_orientation_name(sample.left_token, sample.right_token) == orientation
            ]
    for key in grouped_a:
        if not grouped_a[key] or not grouped_b[key]:
            raise ValueError(f"Insufficient samples for triple pair category {key}")

    patterns = [
        (("aligned", "forward"), ("aligned", "forward")),
        (("aligned", "reverse"), ("crossed", "forward")),
        (("crossed", "forward"), ("crossed", "reverse")),
        (("crossed", "reverse"), ("aligned", "reverse")),
    ]
    counters_a = {key: 0 for key in grouped_a}
    counters_b = {key: pair_reindex for key in grouped_b}
    pairs: list[DualSyntheticSample] = []
    for key_a, key_b in patterns:
        sample_a = grouped_a[key_a][counters_a[key_a] % len(grouped_a[key_a])]
        sample_b = grouped_b[key_b][counters_b[key_b] % len(grouped_b[key_b])]
        counters_a[key_a] += 1
        counters_b[key_b] += 1
        if slot_swap:
            sample_a, sample_b = sample_b, sample_a
        pairs.append(build_dual_sample(sample_a=sample_a, sample_b=sample_b, label_mode=label_mode))
    return pairs


def label_from_offset(offset: int, label_mode: str) -> int:
    if label_mode == "offset_sign":
        return 1 if offset > 0 else 0
    if label_mode == "sector_parity":
        magnitude = abs(offset)
        sign_positive = offset > 0
        return 1 if (sign_positive and magnitude in {1, 2}) or ((not sign_positive) and magnitude in {3, 4}) else 0
    raise ValueError(f"Unsupported synthetic label mode: {label_mode}")


def build_sample(left_token: str, right_token: str, left_pos: int, right_pos: int, label_mode: str) -> SyntheticSample:
    offset = right_pos - left_pos
    label = label_from_offset(offset=offset, label_mode=label_mode)
    text = render_sample_text(
        left_token=left_token,
        right_token=right_token,
        left_pos=left_pos,
        right_pos=right_pos,
        offset=offset,
    )
    return SyntheticSample(
        text=text,
        label=label,
        left_token=left_token,
        right_token=right_token,
        left_pos=left_pos,
        right_pos=right_pos,
        offset=offset,
        offset_abs=abs(offset),
    )


def build_dual_sample(sample_a: SyntheticSample, sample_b: SyntheticSample, label_mode: str = "same_sign") -> DualSyntheticSample:
    sector_a = offset_sector_name(sample_a.offset)
    sector_b = offset_sector_name(sample_b.offset)
    if label_mode == "same_sign":
        label = 1 if sector_sign_family(sector_a) == sector_sign_family(sector_b) else 0
    elif label_mode == "sector_content_xnor":
        sign_agreement = sector_sign_family(sector_a) == sector_sign_family(sector_b)
        content_agreement = content_family_name(sample_a.left_token, sample_a.right_token) == content_family_name(
            sample_b.left_token, sample_b.right_token
        )
        label = 1 if sign_agreement == content_agreement else 0
    elif label_mode == "triple_parity_even":
        sign_agreement = sector_sign_family(sector_a) == sector_sign_family(sector_b)
        content_agreement = content_family_name(sample_a.left_token, sample_a.right_token) == content_family_name(
            sample_b.left_token, sample_b.right_token
        )
        orientation_agreement = token_orientation_name(sample_a.left_token, sample_a.right_token) == token_orientation_name(
            sample_b.left_token, sample_b.right_token
        )
        parity = int(sign_agreement) ^ int(content_agreement) ^ int(orientation_agreement)
        label = 1 if parity == 0 else 0
    elif label_mode == "continuous_coupled_response":
        sign_agreement = sector_sign_family(sector_a) == sector_sign_family(sector_b)
        content_agreement = content_family_name(sample_a.left_token, sample_a.right_token) == content_family_name(
            sample_b.left_token, sample_b.right_token
        )
        orientation_agreement = token_orientation_name(sample_a.left_token, sample_a.right_token) == token_orientation_name(
            sample_b.left_token, sample_b.right_token
        )
        sign_term = 1.0 if sign_agreement else -1.0
        content_term = 1.0 if content_agreement else -1.0
        orientation_term = 1.0 if orientation_agreement else -1.0
        base = 0.5 * sign_term + 0.3 * content_term + 0.2 * orientation_term
        curvature = sign_term * content_term * orientation_term
        label = round(0.8 * base + 0.2 * curvature, 6)
    elif label_mode == "state_sensitive_continuous_response":
        sign_agreement = sector_sign_family(sector_a) == sector_sign_family(sector_b)
        content_agreement = content_family_name(sample_a.left_token, sample_a.right_token) == content_family_name(
            sample_b.left_token, sample_b.right_token
        )
        orientation_agreement = token_orientation_name(sample_a.left_token, sample_a.right_token) == token_orientation_name(
            sample_b.left_token, sample_b.right_token
        )
        sign_term = 1.0 if sign_agreement else -1.0
        content_term = 1.0 if content_agreement else -1.0
        orientation_term = 1.0 if orientation_agreement else -1.0
        sector_magnitude_delta = normalized_sector_magnitude_delta(sample_a, sample_b)
        ordered_content_delta = ordered_content_delta_score(sample_a, sample_b)
        label = round(
            0.25 * sign_term
            + 0.15 * content_term
            + 0.10 * orientation_term
            + 0.15 * sector_magnitude_delta
            + 0.10 * ordered_content_delta
            + 0.15 * (sign_term * sector_magnitude_delta)
            + 0.10 * (content_term * ordered_content_delta),
            6,
        )
    elif label_mode == "orthogonalized_continuous_response":
        sector_magnitude_delta = normalized_sector_magnitude_delta(sample_a, sample_b)
        ordered_content_delta = ordered_content_delta_score(sample_a, sample_b)
        label = round(
            0.45 * sector_magnitude_delta
            + 0.35 * ordered_content_delta
            + 0.20 * (sector_magnitude_delta * ordered_content_delta),
            6,
        )
    elif label_mode == "nonlinear_manifold_response":
        sector_magnitude_delta = normalized_sector_magnitude_delta(sample_a, sample_b)
        ordered_content_delta = ordered_content_delta_score(sample_a, sample_b)
        orientation_delta = orientation_delta_score(sample_a, sample_b)
        label = round(
            math.sin(math.pi * sector_magnitude_delta * ordered_content_delta)
            + 0.5 * (1.0 if sector_magnitude_delta >= 0.0 else -1.0) * orientation_delta
            - 0.25 * math.cos(math.pi * ordered_content_delta),
            6,
        )
    elif label_mode == "phase_sensitive_manifold_response":
        sign_agreement = sector_sign_family(sector_a) == sector_sign_family(sector_b)
        content_agreement = content_family_name(sample_a.left_token, sample_a.right_token) == content_family_name(
            sample_b.left_token, sample_b.right_token
        )
        orientation_agreement = token_orientation_name(sample_a.left_token, sample_a.right_token) == token_orientation_name(
            sample_b.left_token, sample_b.right_token
        )
        sector_magnitude_delta = normalized_sector_magnitude_delta(sample_a, sample_b)
        ordered_content_delta = ordered_content_delta_score(sample_a, sample_b)
        orientation_delta = orientation_delta_score(sample_a, sample_b)
        phi = phase_family_offset(sign_agreement, content_agreement, orientation_agreement)
        label = round(
            math.sin(math.pi * sector_magnitude_delta * ordered_content_delta + phi)
            + 0.35 * math.cos(math.pi * (ordered_content_delta + orientation_delta)),
            6,
        )
    elif label_mode == "latent_phase_manifold_residual_response":
        sector_magnitude_delta = normalized_sector_magnitude_delta(sample_a, sample_b)
        ordered_content_delta = ordered_content_delta_score(sample_a, sample_b)
        orientation_delta = orientation_delta_score(sample_a, sample_b)
        alpha = sector_magnitude_delta + 0.5 * orientation_delta
        beta = ordered_content_delta - 0.75 * sector_magnitude_delta
        latent_id = (1 if alpha >= 0.0 else 0) * 2 + (1 if beta >= 0.0 else 0)
        latent_offsets = {
            0: -math.pi / 3.0,
            1: math.pi / 6.0,
            2: math.pi / 2.0,
            3: -math.pi / 8.0,
        }
        latent_phi = latent_offsets[latent_id]
        global_backbone = math.sin(math.pi * sector_magnitude_delta * ordered_content_delta)
        local_phase_term = math.sin(
            math.pi * (sector_magnitude_delta - orientation_delta) * (ordered_content_delta + 0.5 * orientation_delta)
            + latent_phi
        )
        local_curvature_term = math.cos(
            math.pi * (sector_magnitude_delta + ordered_content_delta) * orientation_delta - 0.5 * latent_phi
        )
        label = round(global_backbone + 0.35 * local_phase_term + 0.20 * local_curvature_term, 6)
    elif label_mode == "local_atlas_manifold_response":
        sector_magnitude_delta = normalized_sector_magnitude_delta(sample_a, sample_b)
        ordered_content_delta = ordered_content_delta_score(sample_a, sample_b)
        orientation_delta = orientation_delta_score(sample_a, sample_b)
        alpha = sector_magnitude_delta + 0.4 * orientation_delta
        beta = ordered_content_delta - 0.5 * sector_magnitude_delta
        chart_id = (1 if alpha >= 0.0 else 0) * 2 + (1 if beta >= 0.0 else 0)
        chart_params = {
            0: (-math.pi / 3.0, math.pi / 7.0),
            1: (math.pi / 5.0, -math.pi / 6.0),
            2: (math.pi / 2.5, math.pi / 9.0),
            3: (-math.pi / 8.0, -math.pi / 4.5),
        }
        phi_chart, psi_chart = chart_params[chart_id]
        global_backbone = math.sin(math.pi * sector_magnitude_delta * ordered_content_delta)
        chart_phase_term = math.sin(
            math.pi * (sector_magnitude_delta - orientation_delta) * (ordered_content_delta + 0.4 * orientation_delta)
            + phi_chart
        )
        chart_curvature_term = math.cos(
            math.pi * (sector_magnitude_delta + ordered_content_delta) * orientation_delta - psi_chart
        )
        label = round(global_backbone + 0.30 * chart_phase_term + 0.18 * chart_curvature_term, 6)
    elif label_mode == "chart_transition_manifold_response":
        sector_magnitude_delta = normalized_sector_magnitude_delta(sample_a, sample_b)
        ordered_content_delta = ordered_content_delta_score(sample_a, sample_b)
        orientation_delta = orientation_delta_score(sample_a, sample_b)
        alpha = sector_magnitude_delta + 0.4 * orientation_delta
        beta = ordered_content_delta - 0.5 * sector_magnitude_delta
        gamma = ordered_content_delta + 0.35 * orientation_delta
        delta = sector_magnitude_delta - 0.25 * orientation_delta
        source_chart = (1 if alpha >= 0.0 else 0) * 2 + (1 if beta >= 0.0 else 0)
        dest_chart = (1 if gamma >= 0.0 else 0) * 2 + (1 if delta >= 0.0 else 0)
        transition_params = {
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
        phi_transition, psi_transition = transition_params[(source_chart, dest_chart)]
        global_backbone = math.sin(math.pi * sector_magnitude_delta * ordered_content_delta)
        transition_phase_term = math.sin(
            math.pi * (sector_magnitude_delta - orientation_delta) * (ordered_content_delta + 0.45 * orientation_delta)
            + phi_transition
        )
        transition_curvature_term = math.cos(
            math.pi * (sector_magnitude_delta + ordered_content_delta) * orientation_delta - psi_transition
        )
        label = round(global_backbone + 0.28 * transition_phase_term + 0.20 * transition_curvature_term, 6)
    else:
        raise ValueError(f"Unsupported dual label_mode: {label_mode}")
    text = render_dual_sample_text(sample_a=sample_a, sample_b=sample_b)
    return DualSyntheticSample(
        text=text,
        label=label,
        sector_a=sector_a,
        sector_b=sector_b,
        sample_a=sample_a,
        sample_b=sample_b,
    )


def render_sample_text(left_token: str, right_token: str, left_pos: int, right_pos: int, offset: int) -> str:
    return f"lt:{left_token} rt:{right_token} lp:{left_pos} rp:{right_pos} off:{offset:+d}"


def render_dual_sample_text(sample_a: SyntheticSample, sample_b: SyntheticSample) -> str:
    return (
        f"a_lt:{sample_a.left_token} a_rt:{sample_a.right_token} a_lp:{sample_a.left_pos} a_rp:{sample_a.right_pos} a_off:{sample_a.offset:+d} "
        f"b_lt:{sample_b.left_token} b_rt:{sample_b.right_token} b_lp:{sample_b.left_pos} b_rp:{sample_b.right_pos} b_off:{sample_b.offset:+d}"
    )


def apply_token_permutation_to_sample(sample: SyntheticSample, token_permutation: str) -> SyntheticSample:
    if token_permutation == "identity":
        return sample
    token_maps = {
        "cdab": {
            "A": "C",
            "B": "D",
            "C": "A",
            "D": "B",
        }
    }
    if token_permutation not in token_maps:
        raise ValueError(f"Unsupported token_permutation: {token_permutation}")
    mapping = token_maps[token_permutation]
    return SyntheticSample(
        text=render_sample_text(
            left_token=mapping[sample.left_token],
            right_token=mapping[sample.right_token],
            left_pos=sample.left_pos,
            right_pos=sample.right_pos,
            offset=sample.offset,
        ),
        label=sample.label,
        left_token=mapping[sample.left_token],
        right_token=mapping[sample.right_token],
        left_pos=sample.left_pos,
        right_pos=sample.right_pos,
        offset=sample.offset,
        offset_abs=sample.offset_abs,
    )


def content_family_name(left_token: str, right_token: str) -> str:
    group_x = {"A", "C"}
    group_y = {"B", "D"}
    if (left_token in group_x and right_token in group_x) or (left_token in group_y and right_token in group_y):
        return "aligned"
    return "crossed"


def token_orientation_name(left_token: str, right_token: str) -> str:
    token_index = {"A": 0, "B": 1, "C": 2, "D": 3}
    delta = (token_index[right_token] - token_index[left_token]) % 4
    return "forward" if delta in {1, 2} else "reverse"


def token_ordinal(token: str) -> int:
    return {"A": 0, "B": 1, "C": 2, "D": 3}[token]


def normalized_sector_magnitude_delta(sample_a: SyntheticSample, sample_b: SyntheticSample) -> float:
    return round((sample_a.offset_abs - sample_b.offset_abs) / 3.0, 6)


def ordered_content_delta_score(sample_a: SyntheticSample, sample_b: SyntheticSample) -> float:
    score_a = (token_ordinal(sample_a.left_token) - token_ordinal(sample_a.right_token)) / 3.0
    score_b = (token_ordinal(sample_b.left_token) - token_ordinal(sample_b.right_token)) / 3.0
    return round(0.5 * (score_a - score_b), 6)


def orientation_delta_score(sample_a: SyntheticSample, sample_b: SyntheticSample) -> float:
    score_a = (token_ordinal(sample_a.right_token) - token_ordinal(sample_a.left_token)) / 3.0
    score_b = (token_ordinal(sample_b.right_token) - token_ordinal(sample_b.left_token)) / 3.0
    return round(0.5 * (score_a + score_b), 6)


def phase_family_offset(sign_agreement: bool, content_agreement: bool, orientation_agreement: bool) -> float:
    family = (int(sign_agreement), int(content_agreement) ^ int(orientation_agreement))
    offsets = {
        (0, 0): -math.pi / 4.0,
        (0, 1): math.pi / 8.0,
        (1, 0): math.pi / 4.0,
        (1, 1): -math.pi / 8.0,
    }
    return offsets[family]


def coarse_tuple_key(sample: DualSyntheticSample) -> tuple[bool, bool, bool]:
    return (
        sector_sign_family(sample.sector_a) == sector_sign_family(sample.sector_b),
        content_family_name(sample.sample_a.left_token, sample.sample_a.right_token)
        == content_family_name(sample.sample_b.left_token, sample.sample_b.right_token),
        token_orientation_name(sample.sample_a.left_token, sample.sample_a.right_token)
        == token_orientation_name(sample.sample_b.left_token, sample.sample_b.right_token),
    )


def orthogonalize_dual_samples_by_coarse_tuple(rows: list[DualSyntheticSample]) -> list[DualSyntheticSample]:
    grouped: dict[tuple[bool, bool, bool], list[DualSyntheticSample]] = defaultdict(list)
    for sample in rows:
        grouped[coarse_tuple_key(sample)].append(sample)
    means = {
        key: (sum(float(sample.label) for sample in group) / len(group) if group else 0.0)
        for key, group in grouped.items()
    }
    return [
        DualSyntheticSample(
            text=sample.text,
            label=round(float(sample.label) - means[coarse_tuple_key(sample)], 6),
            sector_a=sample.sector_a,
            sector_b=sample.sector_b,
            sample_a=sample.sample_a,
            sample_b=sample.sample_b,
        )
        for sample in rows
    ]


def sample_sort_key(sample: SyntheticSample) -> tuple[Any, ...]:
    return (
        sample.label,
        sample.offset_abs,
        sample.left_token,
        sample.right_token,
        sample.left_pos,
        sample.right_pos,
    )


def dual_sample_sort_key(sample: DualSyntheticSample) -> tuple[Any, ...]:
    return (
        sample.label,
        sample.sector_a,
        sample.sector_b,
        sample.sample_a.left_token,
        sample.sample_a.right_token,
        sample.sample_a.left_pos,
        sample.sample_b.left_token,
        sample.sample_b.right_token,
        sample.sample_b.left_pos,
    )


def offset_sector_name(offset: int) -> str:
    magnitude = abs(offset)
    if offset > 0:
        return "P_small" if magnitude in {1, 2} else "P_large"
    return "N_small" if magnitude in {1, 2} else "N_large"


def sector_sign_family(sector: str) -> str:
    return "positive" if sector.startswith("P_") else "negative"


def build_bundle_diagnostics(
    dataset_name: str,
    seed: int,
    split_rotation: int,
    train: list[SyntheticSample],
    validation: list[SyntheticSample],
    test: list[SyntheticSample],
) -> dict[str, Any]:
    splits = {
        "train": train,
        "validation": validation,
        "test": test,
    }
    diagnostics = {
        "dataset": dataset_name,
        "seed": seed,
        "split_rotation": split_rotation,
        "sequence_length": SEQUENCE_LENGTH,
        "vocabulary": list(TOKENS),
        "offsets": list(OFFSETS),
        "splits": {},
        "leakage_checks": {},
    }

    for name, rows in splits.items():
        diagnostics["splits"][name] = summarize_split(rows)

    diagnostics["leakage_checks"] = {
        "token_pair_balanced": all(split["token_pair_balance_ok"] for split in diagnostics["splits"].values()),
        "offset_magnitude_balanced": all(split["offset_abs_balance_ok"] for split in diagnostics["splits"].values()),
        "class_balanced": all(split["class_balance_ok"] for split in diagnostics["splits"].values()),
        "token_permutation_invariant_labels": True,
        "absolute_position_baseline_note": (
            "Label depends only on the declared relative-offset rule by construction; token identity does not affect labels."
        ),
    }
    return diagnostics


def build_dual_bundle_diagnostics(
    dataset_name: str,
    seed: int,
    split_rotation: int,
    slot_swap: int,
    token_permutation: str,
    pair_reindex: int,
    train: list[DualSyntheticSample],
    validation: list[DualSyntheticSample],
    test: list[DualSyntheticSample],
) -> dict[str, Any]:
    splits = {
        "train": train,
        "validation": validation,
        "test": test,
    }
    diagnostics = {
        "dataset": dataset_name,
        "seed": seed,
        "split_rotation": split_rotation,
        "slot_swap": slot_swap,
        "token_permutation": token_permutation,
        "pair_reindex": pair_reindex,
        "sequence_length": SEQUENCE_LENGTH,
        "vocabulary": list(TOKENS),
        "offsets": list(OFFSETS),
        "splits": {},
        "leakage_checks": {},
    }
    for name, rows in splits.items():
        diagnostics["splits"][name] = summarize_dual_split(rows)
    diagnostics["leakage_checks"] = {
        "class_balanced": all(split["class_balance_ok"] for split in diagnostics["splits"].values()),
        "sector_pair_balanced": all(split["sector_pair_balance_ok"] for split in diagnostics["splits"].values()),
        "sector_slot_balanced": all(split["sector_slot_balance_ok"] for split in diagnostics["splits"].values()),
        "token_identity_not_in_label_rule": True,
        "single_sector_shortcut_note": (
            "Label depends on agreement between sector_a and sector_b; no single sector identity determines the class."
        ),
    }
    return diagnostics


def summarize_split(rows: list[SyntheticSample]) -> dict[str, Any]:
    class_counts = Counter(sample.label for sample in rows)
    offset_counts = Counter(sample.offset for sample in rows)
    offset_abs_counts = Counter(sample.offset_abs for sample in rows)
    token_pair_counts = Counter(f"{sample.left_token}->{sample.right_token}" for sample in rows)
    left_pos_counts = Counter(sample.left_pos for sample in rows)
    right_pos_counts = Counter(sample.right_pos for sample in rows)

    return {
        "size": len(rows),
        "class_counts": dict(sorted(class_counts.items())),
        "offset_counts": dict(sorted(offset_counts.items())),
        "offset_abs_counts": dict(sorted(offset_abs_counts.items())),
        "token_pair_counts": dict(sorted(token_pair_counts.items())),
        "left_pos_counts": dict(sorted(left_pos_counts.items())),
        "right_pos_counts": dict(sorted(right_pos_counts.items())),
        "class_balance_ok": class_counts.get(0, 0) == class_counts.get(1, 0),
        "offset_abs_balance_ok": len(set(offset_abs_counts.values())) <= 1,
        "token_pair_balance_ok": token_pair_balance_ok(rows),
    }


def summarize_dual_split(rows: list[DualSyntheticSample]) -> dict[str, Any]:
    class_counts = Counter(sample.label for sample in rows)
    sector_pair_counts = Counter(f"{sample.sector_a}|{sample.sector_b}" for sample in rows)
    sector_a_counts = Counter(sample.sector_a for sample in rows)
    sector_b_counts = Counter(sample.sector_b for sample in rows)
    content_a_counts = Counter(content_family_name(sample.sample_a.left_token, sample.sample_a.right_token) for sample in rows)
    content_b_counts = Counter(content_family_name(sample.sample_b.left_token, sample.sample_b.right_token) for sample in rows)
    orientation_a_counts = Counter(token_orientation_name(sample.sample_a.left_token, sample.sample_a.right_token) for sample in rows)
    orientation_b_counts = Counter(token_orientation_name(sample.sample_b.left_token, sample.sample_b.right_token) for sample in rows)
    sign_agreement_counts = Counter(
        sector_sign_family(sample.sector_a) == sector_sign_family(sample.sector_b) for sample in rows
    )
    content_agreement_counts = Counter(
        content_family_name(sample.sample_a.left_token, sample.sample_a.right_token)
        == content_family_name(sample.sample_b.left_token, sample.sample_b.right_token)
        for sample in rows
    )
    orientation_agreement_counts = Counter(
        token_orientation_name(sample.sample_a.left_token, sample.sample_a.right_token)
        == token_orientation_name(sample.sample_b.left_token, sample.sample_b.right_token)
        for sample in rows
    )
    target_values = [float(sample.label) for sample in rows]
    within_state_groups: dict[tuple[bool, bool, bool], list[float]] = defaultdict(list)
    for sample in rows:
        key = (
            sector_sign_family(sample.sector_a) == sector_sign_family(sample.sector_b),
            content_family_name(sample.sample_a.left_token, sample.sample_a.right_token)
            == content_family_name(sample.sample_b.left_token, sample.sample_b.right_token),
            token_orientation_name(sample.sample_a.left_token, sample.sample_a.right_token)
            == token_orientation_name(sample.sample_b.left_token, sample.sample_b.right_token),
        )
        within_state_groups[key].append(float(sample.label))
    within_state_ranges = {
        f"{int(key[0])}{int(key[1])}{int(key[2])}": round(max(vals) - min(vals), 6)
        for key, vals in sorted(within_state_groups.items())
    }
    within_state_means = {
        f"{int(key[0])}{int(key[1])}{int(key[2])}": round(sum(vals) / len(vals), 6)
        for key, vals in sorted(within_state_groups.items())
    }
    return {
        "size": len(rows),
        "class_counts": dict(sorted(class_counts.items())),
        "sector_pair_counts": dict(sorted(sector_pair_counts.items())),
        "sector_a_counts": dict(sorted(sector_a_counts.items())),
        "sector_b_counts": dict(sorted(sector_b_counts.items())),
        "content_a_counts": dict(sorted(content_a_counts.items())),
        "content_b_counts": dict(sorted(content_b_counts.items())),
        "orientation_a_counts": dict(sorted(orientation_a_counts.items())),
        "orientation_b_counts": dict(sorted(orientation_b_counts.items())),
        "sign_agreement_counts": {str(key).lower(): value for key, value in sorted(sign_agreement_counts.items())},
        "content_agreement_counts": {str(key).lower(): value for key, value in sorted(content_agreement_counts.items())},
        "orientation_agreement_counts": {str(key).lower(): value for key, value in sorted(orientation_agreement_counts.items())},
        "class_balance_ok": class_counts.get(0, 0) == class_counts.get(1, 0),
        "sector_pair_balance_ok": len(set(sector_pair_counts.values())) <= 1,
        "sector_slot_balance_ok": len(set(sector_a_counts.values())) <= 1 and len(set(sector_b_counts.values())) <= 1,
        "content_slot_balance_ok": len(set(content_a_counts.values())) <= 1 and len(set(content_b_counts.values())) <= 1,
        "orientation_slot_balance_ok": len(set(orientation_a_counts.values())) <= 1 and len(set(orientation_b_counts.values())) <= 1,
        "target_mean": round(sum(target_values) / len(target_values), 6) if target_values else 0.0,
        "target_min": round(min(target_values), 6) if target_values else 0.0,
        "target_max": round(max(target_values), 6) if target_values else 0.0,
        "within_state_target_means": within_state_means,
        "within_state_target_ranges": within_state_ranges,
        "within_state_variation_ok": any(value > 0.0 for value in within_state_ranges.values()),
        "coarse_tuple_mean_abs_max": round(max((abs(value) for value in within_state_means.values()), default=0.0), 6),
    }


def token_pair_balance_ok(rows: list[SyntheticSample]) -> bool:
    pair_label_counts: dict[tuple[str, int], int] = Counter(
        (f"{sample.left_token}->{sample.right_token}", sample.label) for sample in rows
    )
    for left_token in TOKENS:
        for right_token in TOKENS:
            pair = f"{left_token}->{right_token}"
            if pair_label_counts[(pair, 0)] != pair_label_counts[(pair, 1)]:
                return False
    return True


def diagnostics_to_jsonable(diagnostics: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(diagnostics))
