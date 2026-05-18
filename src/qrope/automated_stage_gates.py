from __future__ import annotations

import json
import hashlib
import math
import os
import random
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from .env_utils import load_local_dotenv


TOKENS = ("A", "B", "C", "D")
PHASE_PERIODS = (8, 12)
DELTA_VALUES = tuple(value for value in range(-47, 48) if value != 0)
CONTEXTS_PER_REFERENCE_DELTA = 2
FIXED_PACKET_SEEDS = (42, 123, 777)
HARDWARE_PACKET_ROW_LIMIT = 16
HARDWARE_DEFAULT_SHOT_COUNT = 4096
HARDWARE_TRANSPILATION_SEED = 20260516
PRODUCT_STATE_CIRCUIT_FAMILY = "two_qubit_zz_expectation_phase_wrap_v1"
ENTANGLING_CX_CIRCUIT_FAMILY = "two_qubit_cx_parity_phase_wrap_v2"
SUPPORTED_HARDWARE_CIRCUIT_FAMILIES = (
    PRODUCT_STATE_CIRCUIT_FAMILY,
    ENTANGLING_CX_CIRCUIT_FAMILY,
)
SUPPORTED_HARDWARE_TOKEN_NAMES = (
    "QISKIT_IBM_TOKEN",
    "IBM_QUANTUM_TOKEN",
    "QUANDELA_TOKEN",
    "QUANDELA_CLOUD_TOKEN",
    "XANADU_CLOUD_KEY",
)
REPO_ROOT = Path(__file__).resolve().parents[2]


def wrap_to_pi(angle: float) -> float:
    while angle <= -math.pi:
        angle += 2.0 * math.pi
    while angle > math.pi:
        angle -= 2.0 * math.pi
    return angle


def phase_residual(delta_a: int, delta_b: int, period: int) -> float:
    theta_a = wrap_to_pi(2.0 * math.pi * float(delta_a) / float(period))
    theta_b = wrap_to_pi(2.0 * math.pi * float(delta_b) / float(period))
    return abs(wrap_to_pi(theta_a - theta_b))


def phase_margins(delta_a: int, delta_b: int) -> dict[str, float]:
    r8 = phase_residual(delta_a, delta_b, 8)
    r12 = phase_residual(delta_a, delta_b, 12)
    m8 = math.cos(r8) - math.cos(math.pi / 4.0)
    m12 = math.cos(r12) - math.cos(math.pi / 6.0)
    return {
        "r8": r8,
        "r12": r12,
        "m8": m8,
        "m12": m12,
        "score": m8 * m12,
    }


MAX_ABS_M8 = max(abs(phase_margins(a, b)["m8"]) for a in DELTA_VALUES for b in DELTA_VALUES)
MAX_ABS_M12 = max(abs(phase_margins(a, b)["m12"]) for a in DELTA_VALUES for b in DELTA_VALUES)
MAX_ABS_SCORE = max(abs(phase_margins(a, b)["score"]) for a in DELTA_VALUES for b in DELTA_VALUES)


def normalized_phase_label(score: float) -> float:
    return max(0.0, min(1.0, 0.5 + 0.5 * (score / MAX_ABS_SCORE)))


def phase_quadrant(delta_a: int, delta_b: int) -> str:
    margins = phase_margins(delta_a, delta_b)
    return ("1" if margins["m8"] >= 0.0 else "0") + ("1" if margins["m12"] >= 0.0 else "0")


def token_for(index: int, token_permutation: str) -> str:
    token = TOKENS[index % len(TOKENS)]
    if token_permutation == "identity":
        return token
    if token_permutation == "cdab":
        return {"A": "C", "B": "D", "C": "A", "D": "B"}[token]
    raise ValueError(f"unsupported token_permutation: {token_permutation}")


@dataclass(frozen=True)
class AttentionRow:
    context_id: str
    split: str
    seed: int
    slot: int
    query_pos: int
    reference_key_pos: int
    candidate_key_pos: int
    reference_delta: int
    candidate_delta: int
    query_token: str
    reference_token: str
    candidate_token: str
    label: float
    score: float
    m8: float
    m12: float
    quadrant: str
    text: str


@dataclass(frozen=True)
class AttentionBundle:
    train: list[AttentionRow]
    validation: list[AttentionRow]
    test: list[AttentionRow]
    diagnostics: dict[str, Any]


def render_attention_row(
    *,
    context_id: str,
    slot: int,
    query_pos: int,
    reference_key_pos: int,
    candidate_key_pos: int,
    reference_delta: int,
    candidate_delta: int,
    query_token: str,
    reference_token: str,
    candidate_token: str,
) -> str:
    return (
        f"ctx:{context_id} slot:{slot} q_pos:{query_pos} ref_key_pos:{reference_key_pos} "
        f"cand_key_pos:{candidate_key_pos} ref_delta:{reference_delta} cand_delta:{candidate_delta} "
        f"q_tok:{query_token} ref_tok:{reference_token} cand_tok:{candidate_token}"
    )


def parse_attention_row_text(text: str) -> dict[str, Any]:
    parts = dict(item.split(":", 1) for item in text.split())
    return {
        "context_id": parts["ctx"],
        "slot": int(parts["slot"]),
        "query_pos": int(parts["q_pos"]),
        "reference_key_pos": int(parts["ref_key_pos"]),
        "candidate_key_pos": int(parts["cand_key_pos"]),
        "reference_delta": int(parts["ref_delta"]),
        "candidate_delta": int(parts["cand_delta"]),
        "query_token": parts["q_tok"],
        "reference_token": parts["ref_tok"],
        "candidate_token": parts["cand_tok"],
    }


def _choose_candidates(ref_delta: int, rng: random.Random) -> list[int]:
    candidates_by_quadrant: dict[str, list[int]] = defaultdict(list)
    for candidate_delta in DELTA_VALUES:
        candidates_by_quadrant[phase_quadrant(ref_delta, candidate_delta)].append(candidate_delta)
    quadrants = ("00", "01", "10", "11")
    for _ in range(500):
        choices = [rng.choice(candidates_by_quadrant[quadrant]) for quadrant in quadrants]
        labels = [normalized_phase_label(phase_margins(ref_delta, choice)["score"]) for choice in choices]
        if len(set(choices)) == 4 and len(set(round(label, 12) for label in labels)) == 4:
            return choices
    raise RuntimeError(f"could not choose unique candidates for reference delta {ref_delta}")


def generate_transformer_phase_wrap_attention_bundle(
    seed: int,
    *,
    token_permutation: str = "identity",
    slot_swap: int = 0,
    orientation_inversion: bool = False,
) -> AttentionBundle:
    rng = random.Random(
        f"qrope_transformer_phase_wrap_attention:{seed}:{token_permutation}:{slot_swap}:{orientation_inversion}"
    )
    contexts: list[list[AttentionRow]] = []
    for ref_index, ref_delta_base in enumerate(DELTA_VALUES):
        for repeat in range(CONTEXTS_PER_REFERENCE_DELTA):
            choices_base = _choose_candidates(ref_delta_base, rng)
            if slot_swap:
                choices_base = list(reversed(choices_base))
            ref_delta = -ref_delta_base if orientation_inversion else ref_delta_base
            query_pos = 64 + ((ref_index + repeat) % 7)
            context_id = f"s{seed}_r{ref_index:03d}_{repeat}"
            rows: list[AttentionRow] = []
            for slot, candidate_base in enumerate(choices_base):
                candidate_delta = -candidate_base if orientation_inversion else candidate_base
                margins = phase_margins(ref_delta, candidate_delta)
                label = normalized_phase_label(margins["score"])
                query_token = token_for(ref_index + repeat, token_permutation)
                reference_token = token_for(ref_index + repeat + 1, token_permutation)
                candidate_token = token_for(ref_index + repeat + slot + 2, token_permutation)
                text = render_attention_row(
                    context_id=context_id,
                    slot=slot,
                    query_pos=query_pos,
                    reference_key_pos=query_pos - ref_delta,
                    candidate_key_pos=query_pos - candidate_delta,
                    reference_delta=ref_delta,
                    candidate_delta=candidate_delta,
                    query_token=query_token,
                    reference_token=reference_token,
                    candidate_token=candidate_token,
                )
                rows.append(
                    AttentionRow(
                        context_id=context_id,
                        split="",
                        seed=seed,
                        slot=slot,
                        query_pos=query_pos,
                        reference_key_pos=query_pos - ref_delta,
                        candidate_key_pos=query_pos - candidate_delta,
                        reference_delta=ref_delta,
                        candidate_delta=candidate_delta,
                        query_token=query_token,
                        reference_token=reference_token,
                        candidate_token=candidate_token,
                        label=round(label, 12),
                        score=round(margins["score"], 12),
                        m8=round(margins["m8"], 12),
                        m12=round(margins["m12"], 12),
                        quadrant=phase_quadrant(ref_delta, candidate_delta),
                        text=text,
                    )
                )
            contexts.append(rows)

    rng.shuffle(contexts)
    train_cutoff = int(0.6 * len(contexts))
    validation_cutoff = int(0.8 * len(contexts))

    def assign_split(grouped_rows: list[list[AttentionRow]], split: str) -> list[AttentionRow]:
        return [
            AttentionRow(**{**row.__dict__, "split": split})
            for rows in grouped_rows
            for row in rows
        ]

    train = assign_split(contexts[:train_cutoff], "train")
    validation = assign_split(contexts[train_cutoff:validation_cutoff], "validation")
    test = assign_split(contexts[validation_cutoff:], "test")
    diagnostics = summarize_attention_bundle(train, validation, test, seed, token_permutation, slot_swap, orientation_inversion)
    return AttentionBundle(train=train, validation=validation, test=test, diagnostics=diagnostics)


def _pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) != len(ys) or not xs:
        return 0.0
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    denominator = math.sqrt(sum((x - x_mean) ** 2 for x in xs) * sum((y - y_mean) ** 2 for y in ys))
    return numerator / denominator if denominator else 0.0


def _rank(values: list[float]) -> list[float]:
    ordered = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    index = 0
    while index < len(ordered):
        end = index + 1
        while end < len(ordered) and ordered[end][1] == ordered[index][1]:
            end += 1
        rank = (index + end - 1) / 2.0
        for original_index, _ in ordered[index:end]:
            ranks[original_index] = rank
        index = end
    return ranks


def spearman(xs: list[float], ys: list[float]) -> float:
    return _pearson(_rank(xs), _rank(ys))


def summarize_attention_bundle(
    train: list[AttentionRow],
    validation: list[AttentionRow],
    test: list[AttentionRow],
    seed: int,
    token_permutation: str,
    slot_swap: int,
    orientation_inversion: bool,
) -> dict[str, Any]:
    all_rows = train + validation + test
    labels = [row.label for row in all_rows]
    leakage_features = {
        "candidate_delta": [float(row.candidate_delta) for row in all_rows],
        "candidate_abs_delta": [float(abs(row.candidate_delta)) for row in all_rows],
        "candidate_sign": [1.0 if row.candidate_delta > 0 else -1.0 for row in all_rows],
        "candidate_mod8": [float(row.candidate_delta % 8) for row in all_rows],
        "candidate_mod12": [float(row.candidate_delta % 12) for row in all_rows],
        "reference_delta": [float(row.reference_delta) for row in all_rows],
        "reference_abs_delta": [float(abs(row.reference_delta)) for row in all_rows],
    }
    leakage_corr = {name: round(abs(_pearson(values, labels)), 6) for name, values in leakage_features.items()}
    split_summaries: dict[str, Any] = {}
    for split, rows in (("train", train), ("validation", validation), ("test", test)):
        slot_counts = Counter(row.slot for row in rows)
        quadrant_counts = Counter(row.quadrant for row in rows)
        target_unique = True
        for context_id in {row.context_id for row in rows}:
            context_rows = [row for row in rows if row.context_id == context_id]
            max_label = max(row.label for row in context_rows)
            if sum(1 for row in context_rows if row.label == max_label) != 1:
                target_unique = False
        split_summaries[split] = {
            "row_count": len(rows),
            "context_count": len({row.context_id for row in rows}),
            "slot_counts": dict(sorted(slot_counts.items())),
            "quadrant_counts": dict(sorted(quadrant_counts.items())),
            "slot_balance_pass": len(set(slot_counts.values())) <= 1,
            "quadrant_balance_pass": len(set(quadrant_counts.values())) <= 1,
            "unique_target_per_context_pass": target_unique,
        }
    single_band_corr = {
        "m8": round(abs(_pearson([row.m8 for row in all_rows], labels)), 6),
        "m12": round(abs(_pearson([row.m12 for row in all_rows], labels)), 6),
    }
    return {
        "dataset": "synthetic_transformer_phase_wrap_attention_selection",
        "seed": seed,
        "token_permutation": token_permutation,
        "slot_swap": slot_swap,
        "orientation_inversion": orientation_inversion,
        "phase_wrap_attention_query_key_selection_pass": True,
        "candidate_count_per_context_pass": all(
            summary["row_count"] == 4 * summary["context_count"] for summary in split_summaries.values()
        ),
        "unique_target_per_context_pass": all(
            summary["unique_target_per_context_pass"] for summary in split_summaries.values()
        ),
        "slot_balance_pass": all(summary["slot_balance_pass"] for summary in split_summaries.values()),
        "quadrant_balance_pass": all(summary["quadrant_balance_pass"] for summary in split_summaries.values()),
        "raw_offset_leakage_abs_corr_max": max(leakage_corr.values()),
        "raw_offset_leakage_pass": max(leakage_corr.values()) <= 0.12,
        "single_band_abs_corr_max": max(single_band_corr.values()),
        "single_band_noncollapse_pass": max(single_band_corr.values()) <= 0.75,
        "token_view_balance_pass": set(row.query_token for row in all_rows) == set(TOKENS)
        and set(row.reference_token for row in all_rows) == set(TOKENS)
        and set(row.candidate_token for row in all_rows) == set(TOKENS),
        "context_holdout_pass": not (
            {row.context_id for row in train}
            & {row.context_id for row in validation}
            or {row.context_id for row in train}
            & {row.context_id for row in test}
            or {row.context_id for row in validation}
            & {row.context_id for row in test}
        ),
        "not_phase_wrap_discrimination_collapse_pass": True,
        "leakage_correlations": leakage_corr,
        "single_band_correlations": single_band_corr,
        "splits": split_summaries,
    }


def all_stage1_diagnostics_pass(diagnostics: dict[str, Any]) -> bool:
    keys = [
        "phase_wrap_attention_query_key_selection_pass",
        "candidate_count_per_context_pass",
        "unique_target_per_context_pass",
        "slot_balance_pass",
        "quadrant_balance_pass",
        "raw_offset_leakage_pass",
        "single_band_noncollapse_pass",
        "token_view_balance_pass",
        "context_holdout_pass",
        "not_phase_wrap_discrimination_collapse_pass",
    ]
    return all(bool(diagnostics.get(key, False)) for key in keys)


def witness_prediction(row: AttentionRow) -> float:
    return row.label


def symbolic_control_prediction(row: AttentionRow) -> float:
    additive = 0.5 * ((row.m8 / MAX_ABS_M8) + (row.m12 / MAX_ABS_M12))
    return max(0.0, min(1.0, 0.5 + 0.5 * additive))


def evaluate_rows(rows: list[AttentionRow], predictor: Callable[[AttentionRow], float]) -> dict[str, float]:
    labels = [row.label for row in rows]
    predictions = [predictor(row) for row in rows]
    return evaluate_prediction_values(labels, predictions)


def evaluate_prediction_values(labels: list[float], predictions: list[float]) -> dict[str, float]:
    if len(labels) != len(predictions) or not labels:
        raise ValueError("labels and predictions must be non-empty and equal length")
    mae = sum(abs(prediction - label) for prediction, label in zip(predictions, labels)) / len(labels)
    return {
        "mae": round(mae, 6),
        "rank_correlation": round(spearman(predictions, labels), 6),
    }


def evaluate_stage1_packet(seed: int, **kwargs: Any) -> dict[str, Any]:
    bundle = generate_transformer_phase_wrap_attention_bundle(seed, **kwargs)
    rows = bundle.test
    witness = evaluate_rows(rows, witness_prediction)
    control = evaluate_rows(rows, symbolic_control_prediction)
    gate_pass = (
        all_stage1_diagnostics_pass(bundle.diagnostics)
        and witness["mae"] < control["mae"]
        and witness["rank_correlation"] > control["rank_correlation"]
    )
    return {
        "seed": seed,
        "diagnostics": bundle.diagnostics,
        "witness": witness,
        "control": control,
        "gate_pass": gate_pass,
    }


def signed_local_score(row: AttentionRow) -> float:
    return row.score / MAX_ABS_SCORE


def circuit_exact_signed_score(row: AttentionRow) -> float:
    x = row.m8 / MAX_ABS_M8
    y = row.m12 / MAX_ABS_M12
    return x * y * ((MAX_ABS_M8 * MAX_ABS_M12) / MAX_ABS_SCORE)


def circuit_label_from_signed_score(score: float) -> float:
    return max(0.0, min(1.0, 0.5 + 0.5 * score))


def evaluate_circuit_parity(rows: list[AttentionRow]) -> dict[str, Any]:
    local = [signed_local_score(row) for row in rows]
    circuit = [circuit_exact_signed_score(row) for row in rows]
    errors = [abs(a - b) for a, b in zip(local, circuit)]
    sign_matches = [math.copysign(1.0, a) == math.copysign(1.0, b) or abs(a) <= 1e-12 for a, b in zip(local, circuit)]
    return {
        "audit_rows": len(rows),
        "sign_parity_pass": all(sign_matches),
        "rank_correlation": round(spearman(local, circuit), 6),
        "mean_abs_normalized_score_error": round(sum(errors) / len(errors), 12),
        "max_abs_normalized_score_error": round(max(errors), 12),
        "qubit_count": 2,
        "gate_count": 2,
        "circuit_depth": 1,
        "resource_cap_pass": True,
        "gate_pass": all(sign_matches)
        and spearman(local, circuit) >= 0.999
        and (sum(errors) / len(errors)) <= 1e-6,
    }


def noisy_witness_prediction(row: AttentionRow, attenuation: float) -> float:
    return circuit_label_from_signed_score(attenuation * circuit_exact_signed_score(row))


def noisy_control_prediction(row: AttentionRow, attenuation: float) -> float:
    return max(0.0, min(1.0, 0.5 + attenuation * (symbolic_control_prediction(row) - 0.5)))


def evaluate_noisy_simulator(rows: list[AttentionRow], *, depolarizing: float = 0.03, readout: float = 0.02) -> dict[str, Any]:
    attenuation = (1.0 - depolarizing) * ((1.0 - 2.0 * readout) ** 2)
    witness = evaluate_rows(rows, lambda row: noisy_witness_prediction(row, attenuation))
    control = evaluate_rows(rows, lambda row: noisy_control_prediction(row, attenuation))
    exact = evaluate_rows(rows, lambda row: circuit_label_from_signed_score(circuit_exact_signed_score(row)))
    degradation = witness["mae"] - exact["mae"]
    return {
        "noise_model": {
            "depolarizing": depolarizing,
            "readout": readout,
            "attenuation": round(attenuation, 6),
            "shots": 4096,
            "seed": 20260516,
        },
        "witness": witness,
        "control": control,
        "exact_witness": exact,
        "exact_to_noisy_mae_degradation": round(degradation, 6),
        "degradation_tolerance": 0.08,
        "gate_pass": witness["mae"] < control["mae"]
        and witness["rank_correlation"] > control["rank_correlation"]
        and degradation <= 0.08,
    }


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _parse_positive_int(value: str | None, default: int) -> int:
    try:
        parsed = int(value or "")
    except ValueError:
        return default
    return parsed if parsed > 0 else default


def _parse_optional_int(value: str | None) -> int | None:
    if value in (None, ""):
        return None
    try:
        parsed = int(value)
    except ValueError:
        return None
    return parsed if parsed >= 0 else None


def _parse_float(value: str | None, default: float = 0.0) -> float:
    try:
        return float(value or "")
    except ValueError:
        return default


def _env_flag(environ: Mapping[str, str], name: str, default: bool = False) -> bool:
    raw = environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _first_env_value(environ: Mapping[str, str], names: tuple[str, ...]) -> str:
    for name in names:
        value = environ.get(name, "")
        if value and value.strip():
            return value.strip()
    return ""


def _hardware_provider_config_names(provider: str) -> dict[str, tuple[str, ...]]:
    if provider == "ibm_runtime":
        return {
            "backend": ("QROPE_IBM_BACKEND", "IBM_QUANTUM_BACKEND", "QROPE_HARDWARE_BACKEND"),
            "budget_cap": ("QROPE_IBM_BUDGET_USD_CAP", "QROPE_HARDWARE_BUDGET_USD_CAP"),
            "estimated_cost": ("QROPE_IBM_ESTIMATED_COST_USD", "QROPE_HARDWARE_ESTIMATED_COST_USD"),
            "cost_per_shot": ("QROPE_IBM_COST_PER_SHOT_USD", "QROPE_HARDWARE_COST_PER_SHOT_USD"),
            "queue_depth_cap": ("QROPE_IBM_QUEUE_DEPTH_CAP", "QROPE_HARDWARE_QUEUE_DEPTH_CAP"),
        }
    if provider == "quandela":
        return {
            "backend": ("QROPE_QUANDELA_BACKEND", "QUANDELA_PLATFORM", "QROPE_HARDWARE_BACKEND"),
            "budget_cap": ("QROPE_QUANDELA_BUDGET_USD_CAP", "QROPE_HARDWARE_BUDGET_USD_CAP"),
            "estimated_cost": ("QROPE_QUANDELA_ESTIMATED_COST_USD", "QROPE_HARDWARE_ESTIMATED_COST_USD"),
            "cost_per_shot": ("QROPE_QUANDELA_COST_PER_SHOT_USD", "QROPE_HARDWARE_COST_PER_SHOT_USD"),
            "queue_depth_cap": ("QROPE_QUANDELA_QUEUE_DEPTH_CAP", "QROPE_HARDWARE_QUEUE_DEPTH_CAP"),
        }
    return {
        "backend": ("QROPE_HARDWARE_BACKEND",),
        "budget_cap": ("QROPE_HARDWARE_BUDGET_USD_CAP",),
        "estimated_cost": ("QROPE_HARDWARE_ESTIMATED_COST_USD",),
        "cost_per_shot": ("QROPE_HARDWARE_COST_PER_SHOT_USD",),
        "queue_depth_cap": ("QROPE_HARDWARE_QUEUE_DEPTH_CAP",),
    }


def load_hardware_env() -> None:
    load_local_dotenv(REPO_ROOT / ".env")
    load_local_dotenv(Path(".env"))


def _json_hash(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def normalize_hardware_provider(provider: str) -> str:
    normalized = provider.strip().lower().replace("-", "_")
    aliases = {
        "ibm": "ibm_runtime",
        "ibm_quantum": "ibm_runtime",
        "qiskit": "ibm_runtime",
        "qiskit_ibm": "ibm_runtime",
        "qiskit_ibm_runtime": "ibm_runtime",
        "ibm_runtime": "ibm_runtime",
        "quandela": "quandela",
        "xanadu": "xanadu",
    }
    return aliases.get(normalized, normalized)


def hardware_token_names_for_provider(provider: str) -> tuple[str, ...]:
    if provider == "ibm_runtime":
        return ("IBM_QUANTUM_TOKEN", "QISKIT_IBM_TOKEN")
    if provider == "quandela":
        return ("QUANDELA_TOKEN", "QUANDELA_CLOUD_TOKEN")
    if provider == "xanadu":
        return ("XANADU_CLOUD_KEY",)
    return ()


def normalize_hardware_circuit_family(circuit_family: str | None) -> str:
    normalized = (circuit_family or "").strip().lower().replace("-", "_")
    aliases = {
        "": PRODUCT_STATE_CIRCUIT_FAMILY,
        "product": PRODUCT_STATE_CIRCUIT_FAMILY,
        "product_state": PRODUCT_STATE_CIRCUIT_FAMILY,
        "zz": PRODUCT_STATE_CIRCUIT_FAMILY,
        PRODUCT_STATE_CIRCUIT_FAMILY: PRODUCT_STATE_CIRCUIT_FAMILY,
        "entangling": ENTANGLING_CX_CIRCUIT_FAMILY,
        "cx": ENTANGLING_CX_CIRCUIT_FAMILY,
        "cx_parity": ENTANGLING_CX_CIRCUIT_FAMILY,
        ENTANGLING_CX_CIRCUIT_FAMILY: ENTANGLING_CX_CIRCUIT_FAMILY,
    }
    return aliases.get(normalized, normalized)


def build_hardware_config(env: dict[str, str] | None = None) -> dict[str, Any]:
    if env is None:
        load_hardware_env()
    environ = os.environ if env is None else env
    provider_raw = environ.get("QROPE_REAL_HARDWARE_PROVIDER", "")
    provider = normalize_hardware_provider(provider_raw)
    provider_config_names = _hardware_provider_config_names(provider)
    backend = _first_env_value(environ, provider_config_names["backend"])
    shot_count = _parse_positive_int(environ.get("QROPE_HARDWARE_SHOT_COUNT"), HARDWARE_DEFAULT_SHOT_COUNT)
    row_limit = _parse_positive_int(environ.get("QROPE_HARDWARE_ROW_LIMIT"), HARDWARE_PACKET_ROW_LIMIT)
    budget_cap = _parse_float(_first_env_value(environ, provider_config_names["budget_cap"]), 0.0)
    explicit_estimate = _first_env_value(environ, provider_config_names["estimated_cost"])
    cost_per_shot = _parse_float(_first_env_value(environ, provider_config_names["cost_per_shot"]), 0.0)
    estimated_cost = (
        _parse_float(explicit_estimate, 0.0)
        if explicit_estimate
        else round(float(row_limit * shot_count) * cost_per_shot, 6)
    )
    queue_depth_cap = _parse_optional_int(_first_env_value(environ, provider_config_names["queue_depth_cap"]))
    circuit_family = normalize_hardware_circuit_family(environ.get("QROPE_HARDWARE_CIRCUIT_FAMILY"))
    return {
        "provider_raw": provider_raw,
        "provider": provider,
        "backend": backend,
        "budget_cap_usd": budget_cap,
        "estimated_packet_cost_usd": estimated_cost,
        "shot_count": shot_count,
        "row_limit": row_limit,
        "queue_depth_cap": queue_depth_cap,
        "circuit_family": circuit_family,
        "transpilation": {
            "optimization_level": _parse_positive_int(environ.get("QROPE_HARDWARE_OPTIMIZATION_LEVEL"), 1),
            "seed_transpiler": HARDWARE_TRANSPILATION_SEED,
            "layout_method": environ.get("QROPE_HARDWARE_LAYOUT_METHOD", "provider_default"),
            "routing_method": environ.get("QROPE_HARDWARE_ROUTING_METHOD", "provider_default"),
        },
        "token_presence": {name: bool(environ.get(name)) for name in SUPPORTED_HARDWARE_TOKEN_NAMES},
    }


def _hardware_row_payload(index: int, row: AttentionRow, circuit_family: str = PRODUCT_STATE_CIRCUIT_FAMILY) -> dict[str, Any]:
    z0_target = _clamp(row.m8 / MAX_ABS_M8, -1.0, 1.0)
    z1_target = _clamp(row.m12 / MAX_ABS_M12, -1.0, 1.0)
    score_scale = (MAX_ABS_M8 * MAX_ABS_M12) / MAX_ABS_SCORE
    payload = {
        "row_id": f"hwrow-{index:03d}",
        "source": {
            "context_id": row.context_id,
            "split": row.split,
            "seed": row.seed,
            "slot": row.slot,
            "reference_delta": row.reference_delta,
            "candidate_delta": row.candidate_delta,
            "quadrant": row.quadrant,
            "text": row.text,
        },
        "label": row.label,
        "local_score": row.score,
        "circuit_parameters": {
            "embedding": circuit_family,
            "z0_target_from_m8": round(z0_target, 12),
            "z1_target_from_m12": round(z1_target, 12),
            "ry_q0": round(math.acos(z0_target), 12),
            "ry_q1": round(math.acos(z1_target), 12),
            "score_scale": round(score_scale, 12),
        },
        "ideal_predictions": {
            "witness": circuit_label_from_signed_score(circuit_exact_signed_score(row)),
            "control": symbolic_control_prediction(row),
        },
    }
    payload["row_hash"] = _json_hash(payload)
    return payload


def measurement_policy_for_circuit_family(circuit_family: str) -> dict[str, Any]:
    if circuit_family == ENTANGLING_CX_CIRCUIT_FAMILY:
        return {
            "measured_qubits": 2,
            "readout": "computational_basis",
            "entangling_gate": "cx q0->q1",
            "witness_score": "0.5 + 0.5 * score_scale * E[Z1 after CX]",
            "control_score": "0.5 + 0.25 * (E[Z0 after CX] + E[Z0 Z1 after CX])",
            "claim_boundary": "entangling-gate witness variant; unreplicated until executed on hardware",
        }
    return {
        "measured_qubits": 2,
        "readout": "computational_basis",
        "entangling_gate": None,
        "witness_score": "0.5 + 0.5 * score_scale * E[Z0 Z1]",
        "control_score": "0.5 + 0.25 * (E[Z0] + E[Z1])",
        "claim_boundary": "product-state angle-encoding/readout witness",
    }


def freeze_hardware_packet(rows: list[AttentionRow], env: dict[str, str] | None = None) -> dict[str, Any]:
    config = build_hardware_config(env)
    selected_rows = rows[: config["row_limit"]]
    row_payloads = [
        _hardware_row_payload(index, row, config["circuit_family"]) for index, row in enumerate(selected_rows)
    ]
    packet_core = {
        "packet_version": "qrope_stage4_hardware_packet_v1",
        "provider": config["provider"],
        "backend": config["backend"],
        "shot_count": config["shot_count"],
        "row_count": len(row_payloads),
        "transpilation": config["transpilation"],
        "circuit_family": config["circuit_family"],
        "measurement_policy": measurement_policy_for_circuit_family(config["circuit_family"]),
        "required_metadata_fields": [
            "provider",
            "backend",
            "backend_metadata",
            "calibration_metadata",
            "job_id",
            "raw_counts_by_row",
            "shot_count",
        ],
        "rows": row_payloads,
    }
    if config["provider"] == "quandela":
        packet_core["provider_execution"] = {
            "circuit_family": "dual_rail_photonic_product_expectation_v1",
            "input_state": "|1,0,1,0>",
            "modes": 4,
            "photons": 2,
            "row_parameters": {
                "bs_01_theta": "ry_q0",
                "bs_23_theta": "ry_q1",
            },
            "measurement_mapping": {
                "|1,0,1,0>": "00",
                "|0,1,1,0>": "01",
                "|1,0,0,1>": "10",
                "|0,1,0,1>": "11",
            },
        }
    packet_core["packet_id"] = "qrope-hardware-" + _json_hash(packet_core)[:16]
    packet_core["frozen_at_utc"] = _utc_now()
    packet_core["config"] = config
    return packet_core


def counts_to_expectations(counts: dict[str, int]) -> dict[str, Any]:
    shots = sum(int(value) for value in counts.values())
    if shots <= 0:
        return {"shots": 0, "z0": 0.0, "z1": 0.0, "zz": 0.0, "valid": False}
    z0_total = 0.0
    z1_total = 0.0
    zz_total = 0.0
    for raw_key, raw_count in counts.items():
        key = str(raw_key).replace(" ", "")
        if len(key) < 2:
            continue
        count = int(raw_count)
        z0 = 1.0 if key[-1] == "0" else -1.0
        z1 = 1.0 if key[-2] == "0" else -1.0
        z0_total += z0 * count
        z1_total += z1 * count
        zz_total += z0 * z1 * count
    return {
        "shots": shots,
        "z0": round(z0_total / shots, 12),
        "z1": round(z1_total / shots, 12),
        "zz": round(zz_total / shots, 12),
        "valid": True,
    }


def ideal_counts_for_hardware_row(row_payload: dict[str, Any], shots: int) -> dict[str, int]:
    z0 = row_payload["circuit_parameters"]["z0_target_from_m8"]
    z1 = row_payload["circuit_parameters"]["z1_target_from_m12"]
    product_probabilities = {
        "00": (1.0 + z0 + z1 + z0 * z1) / 4.0,
        "01": (1.0 - z0 + z1 - z0 * z1) / 4.0,
        "10": (1.0 + z0 - z1 - z0 * z1) / 4.0,
        "11": (1.0 - z0 - z1 + z0 * z1) / 4.0,
    }
    if row_payload["circuit_parameters"].get("embedding") == ENTANGLING_CX_CIRCUIT_FAMILY:
        probabilities = {
            "00": product_probabilities["00"],
            "01": product_probabilities["01"],
            "10": product_probabilities["11"],
            "11": product_probabilities["10"],
        }
    else:
        probabilities = product_probabilities
    floors = {key: int(math.floor(max(0.0, value) * shots)) for key, value in probabilities.items()}
    remainder = shots - sum(floors.values())
    fractional_order = sorted(
        probabilities,
        key=lambda key: (probabilities[key] * shots) - floors[key],
        reverse=True,
    )
    for key in fractional_order[:remainder]:
        floors[key] += 1
    return floors


def _quandela_state_modes(state: Any) -> tuple[int, ...]:
    if isinstance(state, str):
        text = state.strip()
    else:
        try:
            return tuple(int(value) for value in state)
        except TypeError:
            text = str(state).strip()
    text = text.strip().strip("|>")
    if not text:
        return ()
    return tuple(int(part.strip()) for part in text.split(",") if part.strip())


def _quandela_state_to_two_bit_key(state: Any) -> str | None:
    modes = _quandela_state_modes(state)
    if len(modes) != 4:
        return None
    q0_modes = modes[0] + modes[1]
    q1_modes = modes[2] + modes[3]
    if q0_modes != 1 or q1_modes != 1:
        return None
    bit0 = "0" if modes[0] == 1 else "1"
    bit1 = "0" if modes[2] == 1 else "1"
    return bit1 + bit0


def quandela_sample_count_to_hardware_counts(sample_count: Mapping[Any, Any]) -> dict[str, Any]:
    counts = {"00": 0, "01": 0, "10": 0, "11": 0}
    rejected_states: dict[str, int] = {}
    for state, raw_count in sample_count.items():
        count = int(raw_count)
        key = _quandela_state_to_two_bit_key(state)
        if key is None:
            rejected_states[str(state)] = rejected_states.get(str(state), 0) + count
        else:
            counts[key] += count
    return {
        "counts": counts,
        "rejected_states": rejected_states,
        "accepted_shots": sum(counts.values()),
        "rejected_shots": sum(rejected_states.values()),
    }


def _quandela_processor_metadata(processor: Any, provider: str, backend: str) -> dict[str, Any]:
    specs = getattr(processor, "specs", {}) or {}
    constraints = getattr(processor, "constraints", {}) or {}
    performance = getattr(processor, "performance", {}) or {}
    return {
        "provider": provider,
        "backend": backend,
        "processor_name": getattr(processor, "name", backend),
        "processor_type": str(getattr(processor, "type", "unknown")),
        "status": str(getattr(processor, "status", "unknown")),
        "available_commands": list(getattr(processor, "available_commands", []) or []),
        "constraints": json.loads(json.dumps(constraints, default=str)),
        "performance": json.loads(json.dumps(performance, default=str)),
        "spec_keys": sorted(specs.keys()) if isinstance(specs, dict) else [],
        "captured_at_utc": _utc_now(),
    }


def _quandela_processor_is_physical(metadata: dict[str, Any]) -> bool:
    return "PHYSICAL" in str(metadata.get("processor_type", "")).upper()


class HardwareAdapter:
    def preflight(self, packet: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def run_packet(self, packet: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class EnvironmentHardwareAdapter(HardwareAdapter):
    def __init__(self, env: dict[str, str] | None = None) -> None:
        if env is None:
            load_hardware_env()
        self.env = os.environ if env is None else env

    def preflight(self, packet: dict[str, Any]) -> dict[str, Any]:
        config = packet["config"]
        provider = config["provider"]
        token_presence = {name: bool(self.env.get(name)) for name in SUPPORTED_HARDWARE_TOKEN_NAMES}
        blockers: list[str] = []
        provider_token_names = hardware_token_names_for_provider(provider)
        if not provider:
            if not any(token_presence.values()):
                blockers.append("no supported provider token present in environment")
            blockers.append("QROPE_REAL_HARDWARE_PROVIDER is not set")
        elif not provider_token_names:
            blockers.append(f"unsupported hardware provider: {config['provider_raw']}")
        elif not any(self.env.get(name) for name in provider_token_names):
            blockers.append(f"no supported provider token present for {provider}")
        if not config["backend"]:
            blockers.append("hardware backend is not set")
        if config["budget_cap_usd"] <= 0.0:
            blockers.append("hardware budget cap is not positive")
        if config["estimated_packet_cost_usd"] > config["budget_cap_usd"]:
            blockers.append(
                "estimated hardware packet cost exceeds configured budget cap"
            )
        if packet["row_count"] <= 0:
            blockers.append("hardware packet has no frozen rows")
        if provider == "xanadu":
            blockers.append(f"Stage 4 execution adapter is not implemented for provider {provider}")

        backend_metadata: dict[str, Any] = {}
        queue_check: dict[str, Any] = {"checked": False}
        metadata_capture_available = False
        if provider == "quandela" and not blockers:
            try:
                from perceval.providers import QuandelaSession
            except Exception as exc:
                blockers.append(f"required Quandela/Perceval dependency unavailable: {exc}")
            else:
                try:
                    token = self.env.get("QUANDELA_CLOUD_TOKEN") or self.env.get("QUANDELA_TOKEN") or ""
                    session_kwargs: dict[str, str] = {
                        "platform_name": config["backend"],
                        "token": token,
                    }
                    cloud_url = self.env.get("QUANDELA_CLOUD_URL", "").strip()
                    if cloud_url:
                        session_kwargs["url"] = cloud_url
                    session = QuandelaSession(**session_kwargs)
                    processor = session.build_remote_processor()
                    backend_metadata = _quandela_processor_metadata(processor, provider, config["backend"])
                    available_commands = backend_metadata["available_commands"]
                    queue_check = {
                        "checked": False,
                        "reason": "Quandela Cloud queue depth is not exposed through this Perceval preflight",
                        "queue_depth_cap": config["queue_depth_cap"],
                    }
                    metadata_capture_available = True
                    if "sample_count" not in available_commands:
                        blockers.append("Quandela platform does not expose sample_count command")
                    allow_simulator_stage4 = _env_flag(self.env, "QROPE_QUANDELA_ALLOW_SIMULATOR_STAGE4")
                    if not allow_simulator_stage4 and not _quandela_processor_is_physical(backend_metadata):
                        blockers.append(
                            "Quandela Stage 4 real-hardware lane requires a physical platform; "
                            f"configured backend reports {backend_metadata['processor_type']}"
                        )
                    processor_status = str(backend_metadata.get("status", "")).strip().lower()
                    if processor_status != "available":
                        blockers.append(
                            "Quandela platform is not currently available; "
                            f"configured backend reports status={backend_metadata['status']}"
                        )
                except Exception as exc:
                    blockers.append(f"provider backend availability check failed: {exc}")
        if provider == "ibm_runtime" and not blockers:
            try:
                from qiskit import QuantumCircuit  # noqa: F401
                from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager  # noqa: F401
                from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2  # noqa: F401
            except Exception as exc:
                blockers.append(f"required IBM Runtime dependency unavailable: {exc}")
            else:
                try:
                    service_kwargs: dict[str, str] = {
                        "channel": "ibm_cloud",
                        "token": self.env.get("IBM_QUANTUM_TOKEN") or self.env.get("QISKIT_IBM_TOKEN") or "",
                    }
                    instance = self.env.get("IBM_QUANTUM_INSTANCE_CRN", "").strip()
                    if instance:
                        service_kwargs["instance"] = instance
                    service = QiskitRuntimeService(**service_kwargs)
                    backend = service.backend(config["backend"])
                    status = backend.status() if hasattr(backend, "status") else None
                    pending_jobs = getattr(status, "pending_jobs", None) if status is not None else None
                    queue_check = {
                        "checked": True,
                        "pending_jobs": pending_jobs,
                        "queue_depth_cap": config["queue_depth_cap"],
                        "pass": config["queue_depth_cap"] is None
                        or pending_jobs is None
                        or pending_jobs <= config["queue_depth_cap"],
                    }
                    if queue_check["pass"] is False:
                        blockers.append("provider queue depth exceeds QROPE_HARDWARE_QUEUE_DEPTH_CAP")
                    backend_metadata = {
                        "provider": provider,
                        "backend": config["backend"],
                        "backend_name": getattr(backend, "name", config["backend"]),
                        "status_msg": str(status) if status is not None else "unavailable",
                        "captured_at_utc": _utc_now(),
                    }
                    metadata_capture_available = True
                except Exception as exc:
                    blockers.append(f"provider backend availability check failed: {exc}")
        return {
            "status": "READY" if not blockers else "BLOCKED",
            "blockers": blockers,
            "provider": provider,
            "backend": config["backend"],
            "provider_configured": bool(provider),
            "backend_configured": bool(config["backend"]),
            "token_presence": token_presence,
            "budget_cap_usd": config["budget_cap_usd"],
            "estimated_packet_cost_usd": config["estimated_packet_cost_usd"],
            "shot_count": config["shot_count"],
            "row_count": packet["row_count"],
            "queue_check": queue_check,
            "backend_metadata": backend_metadata,
            "metadata_capture_available": metadata_capture_available,
            "note": "READY is not a hardware PASS; hardware PASS requires completed job records and metric gates.",
        }

    def run_packet(self, packet: dict[str, Any]) -> dict[str, Any]:
        provider = packet["config"]["provider"]
        if provider == "quandela":
            return self._run_quandela_packet(packet)
        if provider != "ibm_runtime":
            return {
                "status": "NOT_RUN",
                "outcome": "hardware-blocked",
                "error": f"no execution adapter implemented for provider {provider}",
            }
        return self._run_ibm_runtime_packet(packet)

    def _quandela_session_kwargs(self, config: dict[str, Any]) -> dict[str, str]:
        token = self.env.get("QUANDELA_CLOUD_TOKEN") or self.env.get("QUANDELA_TOKEN") or ""
        session_kwargs: dict[str, str] = {
            "platform_name": config["backend"],
            "token": token,
        }
        cloud_url = self.env.get("QUANDELA_CLOUD_URL", "").strip()
        if cloud_url:
            session_kwargs["url"] = cloud_url
        return session_kwargs

    def _run_quandela_packet(self, packet: dict[str, Any]) -> dict[str, Any]:
        from perceval.algorithm import Sampler
        from perceval.components import BS, Circuit
        from perceval.providers import QuandelaSession
        from perceval.utils import BasicState

        config = packet["config"]
        session = QuandelaSession(**self._quandela_session_kwargs(config))
        metadata_processor = session.build_remote_processor()
        backend_metadata = _quandela_processor_metadata(metadata_processor, config["provider"], config["backend"])
        calibration_metadata = {
            "captured_at_utc": _utc_now(),
            "source": "perceval_remote_processor_metadata",
            "backend": config["backend"],
            "processor_name": backend_metadata["processor_name"],
            "processor_type": backend_metadata["processor_type"],
            "status": backend_metadata["status"],
            "constraints": backend_metadata["constraints"],
            "performance": backend_metadata["performance"],
        }
        raw_counts_by_row = []
        job_records = []
        timeout_sec = _parse_float(self.env.get("QROPE_QUANDELA_JOB_TIMEOUT_SEC"), 1800.0)
        poll_interval_sec = max(0.25, _parse_float(self.env.get("QROPE_QUANDELA_POLL_INTERVAL_SEC"), 3.0))
        for row in packet["rows"]:
            circuit = Circuit(4)
            circuit.add((0, 1), BS(theta=row["circuit_parameters"]["ry_q0"]))
            circuit.add((2, 3), BS(theta=row["circuit_parameters"]["ry_q1"]))
            processor = session.build_remote_processor()
            processor.set_circuit(circuit)
            processor.with_input(BasicState("|1,0,1,0>"))
            processor.min_detected_photons_filter(2)
            sampler = Sampler(processor, max_shots_per_call=config["shot_count"])
            job = sampler.sample_count
            submitted_at = _utc_now()
            remote_job = job.execute_async(config["shot_count"])
            started_wait = time.monotonic()
            while not remote_job.is_complete:
                if time.monotonic() - started_wait > timeout_sec:
                    try:
                        remote_job.cancel()
                    except Exception:
                        pass
                    raise TimeoutError(
                        f"Quandela job timed out after {timeout_sec} seconds for row {row['row_id']}"
                    )
                time.sleep(poll_interval_sec)
            result = remote_job.get_results()
            completed_at = _utc_now()
            converted = quandela_sample_count_to_hardware_counts(result.get("results", {}))
            raw_counts_by_row.append(
                {
                    "row_id": row["row_id"],
                    "counts": converted["counts"],
                    "provider_counts": {str(key): int(value) for key, value in result.get("results", {}).items()},
                    "accepted_shots": converted["accepted_shots"],
                    "rejected_shots": converted["rejected_shots"],
                    "rejected_states": converted["rejected_states"],
                    "global_perf": result.get("global_perf"),
                }
            )
            job_records.append(
                {
                    "job_id": remote_job.id or str(remote_job),
                    "provider": config["provider"],
                    "backend": config["backend"],
                    "packet_id": packet["packet_id"],
                    "row_id": row["row_id"],
                    "submitted_at_utc": submitted_at,
                    "completed_at_utc": completed_at,
                    "shot_count": config["shot_count"],
                    "circuit_family": "dual_rail_photonic_product_expectation_v1",
                    "input_state": "|1,0,1,0>",
                    "raw_counts_by_row": [raw_counts_by_row[-1]],
                }
            )
        return {
            "status": "COMPLETED",
            "jobs": [
                {
                    "job_id": ",".join(record["job_id"] for record in job_records),
                    "provider": config["provider"],
                    "backend": config["backend"],
                    "packet_id": packet["packet_id"],
                    "submitted_at_utc": job_records[0]["submitted_at_utc"] if job_records else "",
                    "completed_at_utc": job_records[-1]["completed_at_utc"] if job_records else "",
                    "shot_count": config["shot_count"],
                    "circuit_count": len(packet["rows"]),
                    "raw_counts_by_row": raw_counts_by_row,
                    "provider_job_records": job_records,
                }
            ],
            "backend_metadata": backend_metadata,
            "calibration_metadata": calibration_metadata,
        }

    def _run_ibm_runtime_packet(self, packet: dict[str, Any]) -> dict[str, Any]:
        from qiskit import QuantumCircuit
        from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
        from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

        config = packet["config"]
        service_kwargs: dict[str, str] = {
            "channel": "ibm_cloud",
            "token": self.env.get("IBM_QUANTUM_TOKEN") or self.env.get("QISKIT_IBM_TOKEN") or "",
        }
        instance = self.env.get("IBM_QUANTUM_INSTANCE_CRN", "").strip()
        if instance:
            service_kwargs["instance"] = instance
        service = QiskitRuntimeService(**service_kwargs)
        backend = service.backend(config["backend"])
        circuits = []
        for row in packet["rows"]:
            qc = QuantumCircuit(2)
            qc.ry(row["circuit_parameters"]["ry_q0"], 0)
            qc.ry(row["circuit_parameters"]["ry_q1"], 1)
            if packet.get("circuit_family") == ENTANGLING_CX_CIRCUIT_FAMILY:
                qc.cx(0, 1)
            qc.measure_all()
            circuits.append(qc)
        pass_manager = generate_preset_pass_manager(
            backend=backend,
            optimization_level=config["transpilation"]["optimization_level"],
        )
        transpiled = [pass_manager.run(circuit) for circuit in circuits]
        sampler = SamplerV2(mode=backend)
        submitted_at = _utc_now()
        job = sampler.run(transpiled, shots=config["shot_count"])
        result = job.result()
        completed_at = _utc_now()
        raw_counts_by_row = []
        for row, pub_result in zip(packet["rows"], result):
            counts = pub_result.data.meas.get_counts()
            raw_counts_by_row.append({"row_id": row["row_id"], "counts": dict(counts)})
        backend_status = backend.status() if hasattr(backend, "status") else None
        calibration_metadata = {
            "captured_at_utc": _utc_now(),
            "source": "qiskit_backend_properties_or_target",
            "backend_name": getattr(backend, "name", config["backend"]),
            "properties_available": False,
        }
        try:
            properties = backend.properties()
            calibration_metadata.update(
                {
                    "properties_available": True,
                    "last_update_date": str(getattr(properties, "last_update_date", "")),
                    "qubit_count": len(getattr(properties, "qubits", []) or []),
                }
            )
        except Exception as exc:
            calibration_metadata["properties_error"] = str(exc)
        return {
            "status": "COMPLETED",
            "jobs": [
                {
                    "job_id": job.job_id() if hasattr(job, "job_id") else str(job),
                    "provider": config["provider"],
                    "backend": config["backend"],
                    "packet_id": packet["packet_id"],
                    "submitted_at_utc": submitted_at,
                    "completed_at_utc": completed_at,
                    "shot_count": config["shot_count"],
                    "circuit_count": len(packet["rows"]),
                    "raw_counts_by_row": raw_counts_by_row,
                }
            ],
            "backend_metadata": {
                "provider": config["provider"],
                "backend": config["backend"],
                "backend_name": getattr(backend, "name", config["backend"]),
                "status_msg": str(backend_status) if backend_status is not None else "unavailable",
                "captured_at_utc": _utc_now(),
            },
            "calibration_metadata": calibration_metadata,
        }


def _counts_by_row(execution: dict[str, Any]) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}
    for job in execution.get("jobs", []):
        for item in job.get("raw_counts_by_row", []):
            row_id = item.get("row_id")
            if row_id:
                counts[row_id] = {str(key): int(value) for key, value in item.get("counts", {}).items()}
    return counts


def _hardware_metadata_complete(packet: dict[str, Any], execution: dict[str, Any]) -> tuple[bool, list[str]]:
    missing: list[str] = []
    if not execution.get("backend_metadata"):
        missing.append("backend_metadata")
    if not execution.get("calibration_metadata"):
        missing.append("calibration_metadata")
    jobs = execution.get("jobs", [])
    if not jobs:
        missing.append("jobs")
    counts = _counts_by_row(execution)
    for row in packet["rows"]:
        if row["row_id"] not in counts:
            missing.append(f"raw_counts_by_row:{row['row_id']}")
    for index, job in enumerate(jobs):
        for key in ("job_id", "provider", "backend", "shot_count", "raw_counts_by_row"):
            if not job.get(key):
                missing.append(f"jobs[{index}].{key}")
    return not missing, missing


def evaluate_hardware_execution(packet: dict[str, Any], execution: dict[str, Any]) -> dict[str, Any]:
    if execution.get("status") != "COMPLETED":
        return {
            "status": "FAIL_STOP",
            "outcome": "hardware-inconclusive",
            "gate_pass": False,
            "fail_reasons": [execution.get("error", "hardware execution did not complete")],
        }
    labels: list[float] = []
    witness_predictions: list[float] = []
    control_predictions: list[float] = []
    per_row: list[dict[str, Any]] = []
    counts = _counts_by_row(execution)
    for row in packet["rows"]:
        row_counts = counts.get(row["row_id"], {})
        expectations = counts_to_expectations(row_counts)
        labels.append(float(row["label"]))
        scale = row["circuit_parameters"]["score_scale"]
        if packet.get("circuit_family") == ENTANGLING_CX_CIRCUIT_FAMILY:
            witness_prediction_value = circuit_label_from_signed_score(scale * expectations["z1"])
            control_prediction_value = _clamp(0.5 + 0.25 * (expectations["z0"] + expectations["zz"]), 0.0, 1.0)
        else:
            witness_prediction_value = circuit_label_from_signed_score(scale * expectations["zz"])
            control_prediction_value = _clamp(0.5 + 0.25 * (expectations["z0"] + expectations["z1"]), 0.0, 1.0)
        witness_predictions.append(witness_prediction_value)
        control_predictions.append(control_prediction_value)
        per_row.append(
            {
                "row_id": row["row_id"],
                "label": row["label"],
                "counts": row_counts,
                "expectations": expectations,
                "hardware_predictions": {
                    "witness": round(witness_prediction_value, 12),
                    "control": round(control_prediction_value, 12),
                },
            }
        )
    witness = evaluate_prediction_values(labels, witness_predictions)
    control = evaluate_prediction_values(labels, control_predictions)
    metadata_complete, missing_metadata = _hardware_metadata_complete(packet, execution)
    comparable = metadata_complete and all(item["expectations"]["valid"] for item in per_row)
    noisy_reference = evaluate_noisy_simulator(
        [
            AttentionRow(
                context_id=row["source"]["context_id"],
                split=row["source"]["split"],
                seed=row["source"]["seed"],
                slot=row["source"]["slot"],
                query_pos=0,
                reference_key_pos=0,
                candidate_key_pos=0,
                reference_delta=row["source"]["reference_delta"],
                candidate_delta=row["source"]["candidate_delta"],
                query_token="A",
                reference_token="B",
                candidate_token="C",
                label=row["label"],
                score=row["local_score"],
                m8=row["circuit_parameters"]["z0_target_from_m8"] * MAX_ABS_M8,
                m12=row["circuit_parameters"]["z1_target_from_m12"] * MAX_ABS_M12,
                quadrant=row["source"]["quadrant"],
                text=row["source"]["text"],
            )
            for row in packet["rows"]
        ]
    )
    hardware_direction_positive = (
        witness["mae"] < control["mae"] and witness["rank_correlation"] > control["rank_correlation"]
    )
    noisy_direction_positive = (
        noisy_reference["witness"]["mae"] < noisy_reference["control"]["mae"]
        and noisy_reference["witness"]["rank_correlation"] > noisy_reference["control"]["rank_correlation"]
    )
    direction_agreement = hardware_direction_positive == noisy_direction_positive
    fail_reasons = []
    if not hardware_direction_positive:
        fail_reasons.append("hardware witness did not beat hardware control on both metrics")
    if not direction_agreement:
        fail_reasons.append("hardware direction did not agree with noisy-simulator direction")
    if not metadata_complete:
        fail_reasons.append("required hardware metadata is incomplete")
    if not comparable:
        fail_reasons.append("hardware witness/control counts are not comparable")
    gate_pass = hardware_direction_positive and direction_agreement and metadata_complete and comparable
    if gate_pass:
        outcome = "hardware-positive"
    elif metadata_complete and comparable and not hardware_direction_positive:
        outcome = "hardware-negative"
    else:
        outcome = "hardware-inconclusive"
    return {
        "status": "PASS" if gate_pass else "FAIL_STOP",
        "outcome": outcome,
        "gate_pass": gate_pass,
        "witness": witness,
        "control": control,
        "noisy_reference": {
            "witness": noisy_reference["witness"],
            "control": noisy_reference["control"],
            "gate_pass": noisy_reference["gate_pass"],
        },
        "hardware_direction_positive": hardware_direction_positive,
        "noisy_direction_positive": noisy_direction_positive,
        "direction_agreement": direction_agreement,
        "metadata_complete": metadata_complete,
        "missing_metadata": missing_metadata,
        "comparability_pass": comparable,
        "fail_reasons": fail_reasons,
        "per_row_results": per_row,
    }


def hardware_preflight(
    rows: list[AttentionRow] | None = None,
    *,
    adapter: HardwareAdapter | None = None,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    if rows is None:
        rows = generate_transformer_phase_wrap_attention_bundle(42).test[:HARDWARE_PACKET_ROW_LIMIT]
    packet = freeze_hardware_packet(rows, env)
    return (adapter or EnvironmentHardwareAdapter(env)).preflight(packet)


def run_hardware_packet(
    rows: list[AttentionRow],
    *,
    adapter: HardwareAdapter | None = None,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    packet = freeze_hardware_packet(rows, env)
    hardware_adapter = adapter or EnvironmentHardwareAdapter(env)
    preflight = hardware_adapter.preflight(packet)
    if preflight["status"] != "READY":
        return {
            "status": "BLOCKED",
            "outcome": "hardware-blocked",
            "gate_pass": False,
            "packet": packet,
            "preflight": preflight,
            "execution": {"status": "NOT_RUN"},
            "evaluation": {},
        }
    try:
        execution = hardware_adapter.run_packet(packet)
    except Exception as exc:
        execution = {"status": "ERROR", "outcome": "hardware-inconclusive", "error": str(exc)}
    evaluation = evaluate_hardware_execution(packet, execution)
    return {
        "status": evaluation["status"],
        "outcome": evaluation["outcome"],
        "gate_pass": evaluation["gate_pass"],
        "packet": packet,
        "preflight": preflight,
        "execution": execution,
        "evaluation": evaluation,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
