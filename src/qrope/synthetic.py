from __future__ import annotations

import json
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
    label: int
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


def generate_signed_offset_binary_bundle(seed: int) -> SyntheticDatasetBundle:
    return generate_sector_bundle(seed=seed, dataset_name="synthetic_offset_binary", label_mode="offset_sign")


def generate_sector_parity_binary_bundle(seed: int) -> SyntheticDatasetBundle:
    return generate_sector_bundle(seed=seed, dataset_name="synthetic_sector_parity_binary", label_mode="sector_parity")


def generate_sector_bundle(seed: int, dataset_name: str, label_mode: str) -> SyntheticDatasetBundle:
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
        train.extend(bucket[:TRAIN_COUNT_PER_BUCKET])
        validation.extend(bucket[TRAIN_COUNT_PER_BUCKET : TRAIN_COUNT_PER_BUCKET + VALIDATION_COUNT_PER_BUCKET])
        test.extend(bucket[TRAIN_COUNT_PER_BUCKET + VALIDATION_COUNT_PER_BUCKET : required])

    train_rows = [(sample.text, sample.label) for sample in sorted(train, key=sample_sort_key)]
    validation_rows = [(sample.text, sample.label) for sample in sorted(validation, key=sample_sort_key)]
    test_rows = [(sample.text, sample.label) for sample in sorted(test, key=sample_sort_key)]

    diagnostics = build_bundle_diagnostics(
        dataset_name=dataset_name,
        seed=seed,
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


def render_sample_text(left_token: str, right_token: str, left_pos: int, right_pos: int, offset: int) -> str:
    return f"lt:{left_token} rt:{right_token} lp:{left_pos} rp:{right_pos} off:{offset:+d}"


def sample_sort_key(sample: SyntheticSample) -> tuple[Any, ...]:
    return (
        sample.label,
        sample.offset_abs,
        sample.left_token,
        sample.right_token,
        sample.left_pos,
        sample.right_pos,
    )


def build_bundle_diagnostics(
    dataset_name: str,
    seed: int,
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
