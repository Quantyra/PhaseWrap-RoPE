# QRoPE: Phase-Wrap Positional Scoring with Bounded Hardware Validation

Manuscript status: `repository-paper-v1`  
Publication posture: `patent-pending, bounded, reproducible, evidence-disciplined`  
Patent: U.S. provisional patent application `64/068,121`  
License context: repository software released under `AGPL-3.0-only`

## Abstract

Quantum Rotary Positional Encoding (QRoPE) is a phase-wrap positional-scoring method for studying modular residual structure in positional encodings. The method computes wrapped residuals in two modular bases, converts those residuals into signed cosine margins, and combines the margins through an SQR score. This repository paper describes the QRoPE method, the deterministic validation protocol used to evaluate it, and a bounded Stage 4 real-hardware result for one frozen packet executed on IBM Quantum hardware.

The reported result should be interpreted narrowly. It supports the recorded packet-, backend-, date-, and calibration-specific validation outcome; it does not establish broad quantum advantage, transformer-scale superiority, general cross-backend robustness, or production language-model improvement. The main contribution is a reproducible review path: fixed input packets, fixed shot counts, raw measurement counts, backend metadata, offline recomputation, and explicit claim boundaries.

## Keywords

Quantum positional encoding; rotary positional encoding; phase-wrap scoring; quantum circuit validation; deterministic evidence packets; reproducible hardware validation.

## 1. Introduction

Transformer positional encodings provide sequence-order information to attention models. The Transformer architecture established the baseline context for modern attention-based sequence modeling [1], and Rotary Position Embedding (RoPE) introduced a rotation-based mechanism for incorporating positional information into self-attention while supporting relative-position behavior [2].

QRoPE investigates a narrower question: can a phase-wrap positional-scoring component be specified, frozen, and validated through deterministic software artifacts and a small-circuit hardware witness? This release does not claim to replace RoPE in production transformers and does not report transformer-scale training or evaluation.

This paper documents the first public QRoPE release under Quantyra. The repository is open source under `AGPL-3.0-only` and includes patent and licensing notices in `PATENTS.md`. The release is structured for external review while preserving the claim boundaries stated in this paper and the repository patent notice.

The contributions are:

- a phase-wrap QRoPE scoring method based on mod-8 and mod-12 signed margins;
- a deterministic validation protocol built from frozen packets, fixed rows, fixed shot counts, raw counts, backend metadata, and offline recomputation; and
- a Stage 4 real-hardware validation result for one recorded packet/backend/date/calibration context.

## 2. Related work and claim boundary

QRoPE is motivated by positional encoding and RoPE-style relative phase behavior, but the present result is not a drop-in transformer positional-embedding result. The relationship to RoPE is conceptual: QRoPE uses wrapped phase residuals and cross-band interactions, while this release evaluates a small deterministic validation pathway rather than a complete language-model architecture.

The supported public claims are:

- QRoPE defines a phase-wrap positional-scoring method.
- The SQR score is computed from mod-8 and mod-12 signed-margin structure.
- The validation protocol uses frozen packets, raw counts, backend metadata, and offline recomputation.
- The Stage 4 evidence record reports a hardware-positive result for the recorded packet/backend/date/calibration context.

The following claims are outside the scope of the present evidence:

- broad quantum advantage;
- production transformer superiority;
- full transformer-scale validation;
- general cross-backend robustness; and
- commercial performance improvement in deployed language models.

These boundaries follow the repository patent notice and the evidence scope stated in this paper.

## 3. Method

![QRoPE phase-wrap method schematic](figures/qrope-method-schematic-v1.svg)

**Figure 1.** QRoPE phase-wrap scoring schematic. The figure is conceptual; the formula block below is the normative method definition.

For integer offsets `delta_a` and `delta_b`, define the period-specific wrapped phase as:

```text
wrap_pi(x) = x shifted by integer multiples of 2*pi into the interval (-pi, pi]

theta_P(delta) = wrap_pi(2*pi*delta/P)

r_P(delta_a, delta_b) = abs(wrap_pi(theta_P(delta_a) - theta_P(delta_b)))
```

The release uses two signed margins:

```text
r8  = r_8(delta_a, delta_b)
r12 = r_12(delta_a, delta_b)

m8  = cos(r8)  - cos(pi/4)
m12 = cos(r12) - cos(pi/6)
```

The local QRoPE score is:

```text
SQR = m8 * m12
```

The thresholds correspond to one modular step in each basis. For period 8, one step is `2*pi/8 = pi/4`; for period 12, one step is `2*pi/12 = pi/6`. Subtracting `cos(pi/4)` and `cos(pi/6)` centers each margin at its one-step residual boundary. Margins are positive when residuals are closer than one modular step, approximately zero at one step, and negative beyond one step.

For packet labels, the implementation normalizes the score by clamping:

```text
label = clamp(0.5 + 0.5 * SQR / MAX_ABS_SCORE, 0, 1)
```

where `MAX_ABS_SCORE` is computed over the fixed delta grid used by the packet generator.

### Algorithm 1. Local QRoPE score

```text
Input: integer offsets delta_a, delta_b
Output: signed score SQR and normalized label

for P in {8, 12}:
    theta_a[P] = wrap_pi(2*pi*delta_a/P)
    theta_b[P] = wrap_pi(2*pi*delta_b/P)
    r[P] = abs(wrap_pi(theta_a[P] - theta_b[P]))

m8 = cos(r[8]) - cos(pi/4)
m12 = cos(r[12]) - cos(pi/6)
SQR = m8 * m12
label = clamp(0.5 + 0.5*SQR/MAX_ABS_SCORE, 0, 1)
```

The two-qubit witness normalizes the margins into Z targets:

```text
z0 = clamp(m8 / MAX_ABS_M8, -1, 1)
z1 = clamp(m12 / MAX_ABS_M12, -1, 1)
theta_0 = arccos(z0)
theta_1 = arccos(z1)
```

The circuit prepares each qubit with a Y-axis rotation using `theta_0` and `theta_1`, measures computational-basis counts, and estimates `E[Z0]`, `E[Z1]`, and `E[Z0 Z1]`. The Stage 4 packet uses the `two_qubit_zz_expectation_phase_wrap_v1` circuit family.

The current Stage 4 circuit is a product-state angle-encoding/readout witness. It contains no entangling gate. Therefore, the measured `E[Z0 Z1]` term should be interpreted as a hardware readout of the cross-band product induced by independently encoded margins, not as evidence of entanglement, quantum speedup, or nonclassical interference.

![QRoPE product-state witness circuit](figures/qrope-product-state-circuit-v1.png)

**Figure 2.** Product-state witness circuit for the published Stage 4 hardware packet. The parameters shown in the rendered diagram are taken from the first frozen packet row.

The repository also includes an opt-in entangling CX witness family:

```text
two_qubit_cx_parity_phase_wrap_v2
```

This variant applies `CX(q0 -> q1)` after the two `RY` margin encodings. In the ideal circuit, the target-qubit Z expectation after CX carries the cross-band parity/product signal. The corresponding witness and control scores are:

```text
witness_cx = clamp(0.5 + 0.5 * score_scale * E[Z1 after CX], 0, 1)
control_cx = clamp(0.5 + 0.25 * (E[Z0 after CX] + E[Z0 Z1 after CX]), 0, 1)
```

This CX variant is implemented and unit-tested for follow-up hardware execution, but it is not part of the current hardware evidence. It should be included in the evidence record only after an authorized hardware run publishes raw counts, metadata, and verifier output.

![QRoPE entangling CX witness circuit](figures/qrope-cx-witness-circuit-v1.png)

**Figure 3.** Entangling CX witness variant implemented for follow-up hardware execution. This circuit is not part of the current published hardware evidence.

Implementation reference: `src/qrope/automated_stage_gates.py`.

## 4. Validation protocol

![QRoPE deterministic validation pipeline](figures/qrope-validation-pipeline-v1.svg)

**Figure 4.** Deterministic validation pathway. The verification path recomputes metrics from frozen packet files and execution records.

The validation protocol is designed for reproducibility rather than opportunistic metric selection. A valid evidence packet should include:

- frozen input rows;
- a fixed row count;
- a fixed shot count for hardware or simulator execution;
- raw measurement counts;
- backend metadata;
- a packet identifier;
- an offline verifier; and
- a deterministic pass/fail or bounded status outcome.

For the Stage 4 packet, the verifier entry point is:

```bash
python scripts/verify_stage4_hardware_packet.py
```

The default verifier inputs are:

- `logs/automated_stage_gates/stage4_hardware_packet/frozen_packet.json`
- `logs/automated_stage_gates/stage4_hardware_packet/execution.json`
- `logs/automated_stage_gates/stage4_hardware_packet/evaluation.json`
- `logs/automated_stage_gates/stage4_hardware_packet/summary.json`

The default verifier output is:

- `logs/automated_stage_gates/stage4_hardware_packet/offline_verification.json`

IBM Quantum Runtime primitives provide the execution model used by the hardware validation pathway. In this context, Sampler samples circuit output registers, and IBM backend documentation describes dynamic backend properties and calibration metadata that can change over time [3-5].

The verifier supports recomputation, not independent replication. Recomputing the saved packet verifies that the reported metrics follow from the published raw counts and metadata. Replication requires a new execution of the same frozen packet family, preferably across additional dates and backends. Current replication status is recorded in `docs/publication/replication-ledger-v1.md`.

## 5. Hardware validation result

![QRoPE Stage 4 row-level predictions](figures/qrope-stage4-predictions-v1.png)

**Figure 5.** Stage 4 row-level labels, witness predictions, control predictions, and absolute errors. Source data: `logs/automated_stage_gates/stage4_hardware_packet/evaluation.json`.

![QRoPE Stage 4 witness versus control metrics](figures/qrope-stage4-metrics-v1.png)

**Figure 6.** Stage 4 witness versus control summary metrics. Source data: `logs/automated_stage_gates/stage4_hardware_packet/evaluation.json`.

![QRoPE replication lane status](figures/qrope-replication-status-v1.png)

**Figure 7.** Replication lane status. Source data: `logs/automated_stage_gates/replication_lanes/replication-ledger.json`.

The Stage 4 evidence record reports one real-hardware validation run with the following recorded conditions and metrics:

- provider: `ibm_runtime`;
- backend: `ibm_fez`;
- job id: `d84jbq00bvlc73d4krr0`;
- submitted at: `2026-05-17T03:28:38Z`;
- completed at: `2026-05-17T03:29:05Z`;
- calibration metadata captured at: `2026-05-17T03:29:05Z`;
- calibration last update: `2026-05-16 20:02:17-07:00`;
- backend qubit count in captured metadata: `156`;
- packet id: `qrope-hardware-73c61893576297ff`;
- rows: `16`;
- shots per row: `4096`;
- witness MAE: `0.018382`;
- witness rank correlation: `0.876558`;
- control MAE: `0.217262`;
- control rank correlation: `-0.176940`; and
- outcome: `hardware-positive`.

The control condition is the additive single-band readout baseline:

```text
control = clamp(0.5 + 0.25 * (E[Z0] + E[Z1]), 0, 1)
```

The witness condition uses the cross-band product readout:

```text
witness = clamp(0.5 + 0.5 * score_scale * E[Z0 Z1], 0, 1)
```

The captured execution supports the Stage 4 packet outcome under the recorded conditions. Backend calibration, queue conditions, transpilation details, and packet composition may affect replication. The result is therefore limited to the stated packet, backend, date, calibration window, and metrics.

## 6. Reproducibility artifacts

The repository prioritizes evidence files over narrative-only claims. The minimum review path is:

- inspect `docs/research/q-rope-phase-wrap-qrope-algorithm-v1.md`;
- inspect `docs/research/q-rope-stage4-real-hardware-validation-result-v1.md`;
- run or inspect `scripts/verify_stage4_hardware_packet.py`; and
- compare the verifier output with `logs/automated_stage_gates/stage4_hardware_packet/offline_verification.json`.

The intended reproducibility standard is not that every future backend execution match the present numbers. The standard is that the reported numbers remain traceable to packet files, execution records, raw counts, and deterministic recomputation.

## 7. Patent and open-source notice

QRoPE is patent pending under U.S. provisional patent application `64/068,121`.

Copyright 2026 Quantyra contributors. The repository software is released under `AGPL-3.0-only`. Commercial patent licensing, non-AGPL use, assignments, and sublicensing should be handled separately with Quantyra/CYINT IP.

## 8. Limitations

The present result has important limitations:

- The Stage 4 evidence is limited to one recorded packet/backend/date/calibration context.
- The paper does not report transformer-scale training or evaluation.
- The paper does not report completed cross-backend replication; the replication ledger records those lanes as blocked or unexecuted pending authorized hardware runs.
- The paper does not compare against production language-model baselines.
- The paper does not establish quantum advantage.

These limitations define the scientific scope of the current release.

## 9. Conclusion

QRoPE provides an open-source research pathway for phase-wrap positional scoring and bounded small-circuit validation. The current evidence supports publication as a narrowly framed method and evidence paper. The next scientific step is credentialed replication and controlled expansion: executing the entangling-gate witness variant, evaluating additional packets and backends, comparing simulator and hardware behavior, and pursuing broader transformer-adjacent experiments only when supported by new evidence.

## Repository evidence references

- `src/qrope/automated_stage_gates.py`
- `scripts/verify_stage4_hardware_packet.py`
- `logs/automated_stage_gates/stage4_hardware_packet/frozen_packet.json`
- `logs/automated_stage_gates/stage4_hardware_packet/execution.json`
- `logs/automated_stage_gates/stage4_hardware_packet/evaluation.json`
- `logs/automated_stage_gates/stage4_hardware_packet/offline_verification.json`
- `docs/research/q-rope-phase-wrap-qrope-algorithm-v1.md`
- `docs/research/q-rope-stage4-real-hardware-validation-result-v1.md`
- `docs/publication/figures/qrope-method-schematic-v1.svg`
- `docs/publication/figures/qrope-product-state-circuit-v1.png`
- `docs/publication/figures/qrope-cx-witness-circuit-v1.png`
- `docs/publication/figures/qrope-validation-pipeline-v1.svg`
- `docs/publication/figures/qrope-stage4-predictions-v1.png`
- `docs/publication/figures/qrope-stage4-metrics-v1.png`
- `docs/publication/figures/qrope-replication-status-v1.png`
- `docs/publication/replication-ledger-v1.md`
- `logs/automated_stage_gates/replication_lanes/replication-ledger.json`
- `PATENTS.md`
- `README.md`

## References

[1] Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Lukasz Kaiser, and Illia Polosukhin. "Attention Is All You Need." arXiv:1706.03762, 2017. https://arxiv.org/abs/1706.03762

[2] Jianlin Su, Yu Lu, Shengfeng Pan, Ahmed Murtadha, Bo Wen, and Yunfeng Liu. "RoFormer: Enhanced Transformer with Rotary Position Embedding." arXiv:2104.09864, 2021. https://arxiv.org/abs/2104.09864

[3] IBM Quantum Documentation. "Introduction to primitives." Accessed 2026-05-18. https://quantum.cloud.ibm.com/docs/en/guides/qiskit-runtime-primitives

[4] IBM Quantum Documentation. "SamplerV2." Accessed 2026-05-18. https://quantum.cloud.ibm.com/docs/en/api/qiskit-ibm-runtime/0.25/sampler-v2

[5] IBM Quantum Documentation. "View backend details." Accessed 2026-05-18. https://quantum.cloud.ibm.com/docs/en/guides/qpu-information


