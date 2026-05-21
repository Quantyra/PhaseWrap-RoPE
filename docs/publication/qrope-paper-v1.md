# PhaseWrap-RoPE: A Bounded Phase-Wrap Positional Scoring Rule with Reproducible Two-Qubit Hardware Readout

Manuscript status: `repository-paper-v2-draft`

Public claim posture: `bounded, reproducible, evidence-disciplined`

Archive DOI: `10.5281/zenodo.20306786`

USPTO record note: the repository reports an Electronic Acknowledgement Receipt dated `2026-05-18` listing application `64/068,121` and Patent Center number `76347440`. Public materials should continue to describe this as an acknowledgement-receipt record until the final Filing Receipt is received and checked.

License context: repository software released under `AGPL-3.0-only`.

## Abstract

PhaseWrap-RoPE is a bounded positional-scoring method based on wrapped phase residuals. Given two integer relative offsets, the method computes residuals in two fixed modular bases, converts those residuals into signed cosine margins, and combines the margins through a cross-band product score denoted `SQR` in the repository artifacts. This paper describes the scoring rule, the deterministic packet protocol used to audit it, and small two-qubit hardware readouts that recompute the frozen score from raw measurement counts.

The contribution is not a claim of quantum advantage, production transformer improvement, or general cross-backend robustness. Instead, the paper contributes a reproducibility-first evidence lane: frozen packets, fixed shot counts, raw counts, backend metadata, offline recomputation, explicit verifier scripts, and conservative claim boundaries. The current evidence includes a canonical IBM Fez product-state packet, a completed IBM Fez CX packet, Amazon Braket/Rigetti product-state replication evidence, provider-aware Amazon Braket CX recomputations, classical downstream baselines that identify both the strengths and the limits of the synthetic tasks, a local phase-cued Needle-style retrieval benchmark, and a stricter non-phase-cued retrieval benchmark that exposes the current RoPE-replacement gap.

The strongest supported interpretation is that PhaseWrap-RoPE is a compact, auditable phase-wrap scoring rule whose cross-band signal can be preserved in recorded small-circuit hardware readouts and in selected toy downstream attention tasks. The current evidence does not establish a replacement for RoPE, a production language-model result, or a broad hardware generalization claim.

## Keywords

Rotary positional encoding; phase-wrap scoring; positional scoring; deterministic evidence packets; two-qubit readout; reproducible hardware validation; quantum circuit audit.

## 1. Introduction

Transformer models require positional information to distinguish token order in attention. Rotary Position Embedding, or RoPE, introduced a rotation-based way to inject relative-position structure into attention [1,2]. PhaseWrap-RoPE studies a narrower question: can a RoPE-shaped phase-wrap scoring component be stated as a compact rule, frozen into deterministic packets, and audited through both classical baselines and small hardware readouts?

This paper should be read as a method-and-evidence paper, not as a full model paper. It does not train a production transformer, does not replace RoPE in a large language model, and does not claim quantum speedup. The aim is to make a small positional scoring rule reviewable: every reported packet should be traceable to input rows, raw measurement counts or deterministic classical outputs, backend metadata where applicable, and an offline verifier.

This paper documents the first public PhaseWrap-RoPE release under Quantyra. The repository is open source under `AGPL-3.0-only` and references the USPTO submission record summarized in `PATENTS.md` and `docs/publication/patent-status-note-v1.md`. The release is designed to permit external review while preserving the claim boundary established by the manuscript-to-provisional support audit.

The paper makes four contributions:

1. A fixed phase-wrap scoring rule. PhaseWrap-RoPE computes two signed residual margins, one in period 8 and one in period 12, and combines them through a cross-band product score.
2. A deterministic evidence protocol. The repository uses frozen rows, fixed shot counts, explicit packet IDs, raw counts, backend metadata, and offline recomputation rather than narrative-only hardware claims.
3. Bounded two-qubit hardware readouts. Product-state and CX readout paths show that the frozen cross-band score can be recomputed from recorded small-circuit hardware artifacts under stated backend/date/calibration conditions.
4. Classical and toy downstream baselines. The repository reports that the original synthetic scoring target is exactly recoverable by simple exposed-feature baselines, then separates that limitation from later toy downstream attention and Needle-style retrieval experiments.

The main scientific value is therefore the evidence discipline and the clarity of the scoring rule. The main scientific limitation is that the strongest claims remain packet-specific and toy-task-specific.

## 2. Claim Boundary and Evidence Tiers

PhaseWrap-RoPE is related to RoPE-style phase behavior, but the present release does not test a full transformer-scale architecture. Its evidence should be interpreted by tier:

| Tier | Evidence class | Supported interpretation | Unsupported interpretation |
| --- | --- | --- | --- |
| Formula | Closed scoring rule over integer offsets | `SQR = m8 * m12` is well specified and reproducible | Learned positional representation or broad model improvement |
| Stage 4 hardware | Two-qubit product-state and CX readout packets | Recorded hardware can preserve the frozen score/control ordering under specific packet/backend/date/calibration contexts | Quantum advantage, entanglement advantage, or general backend robustness |
| Stage 5 baselines | Synthetic attention-scoring baseline closure | The original synthetic target is recoverable by mod-24 and direct product-feature baselines | Evidence that the scoring task is nontrivial or production-relevant |
| Stage 6 downstream toy task | Content-plus-position oracle phase-feature sanity check | PhaseWrap-RoPE gives the lowest MAE on one fixed toy packet | Production transformer superiority |
| Stage 7 toy transformer ablation | Four-layer attention-only synthetic length-extrapolation packet | PhaseWrap-RoPE has the best argmax retrieval ranking on one fixed packet | Full transformer-scale validation or better calibration |
| Stage 8 Needle-style benchmark | Local phase-cued synthetic retrieval packet | PhaseWrap-RoPE is worth testing in broader RoPE-facing retrieval settings | RULER result, production transformer result, or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 9 trained positional-attention ablation | Synthetic train-short/test-long phase-cued and exact-offset passkey packets with matched optimizer/seeds | `phasewrap_adapter` is strongest on the phase-cued packet; `rope_relative` is strongest on exact-offset passkey | Full language-model benchmark, production transformer result, or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 10 small decoder-only transformer ablation | Autograd-backed one-block decoder-only transformer on phase-cued retrieval, exact-offset passkey, and tiny text-fact QA lanes | The first full-transformer sanity check is near chance, target probabilities are near uniform, and no meaningful PhaseWrap advantage is shown | Production transformer result, full language-model benchmark, or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 11 score theory | Deterministic invariance, aliasing, period-pair, and Fourier-support analysis | The fixed 8/12 score is a mod-24 periodic feature with unavoidable aliases and exact small classical Fourier support | Proof that 8/12 is globally optimal or that the score improves trained transformers |
| Stage 12 RULER-style retrieval | Deterministic passkey, multi-needle, and aggregation-style local retrieval whose targets are not PhaseWrap-selected | RoPE-like and sinusoidal baselines solve this exact-offset packet; fixed 8/12 PhaseWrap-RoPE does not | Claim that PhaseWrap-RoPE is currently a RoPE replacement |
| Stage 13 positional-adapter benchmark | Train-short/test-long adapters on Stage 12 non-phase-cued retrieval rows | PhaseWrap-plus-distance matches RoPE on held-out top-1/MRR, but RoPE has higher target-probability mass | Production transformer result or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 14 attention-readout benchmark | Key-value attention readout derived from Stage 12 rows | PhaseWrap-plus-distance again matches RoPE on held-out top-1/MRR, but RoPE has higher target value probability | Production transformer result or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 15 learned attention-readout benchmark | One-hidden-layer scorer over Stage 14 positional feature families | PhaseWrap-plus-distance leads held-out top-1/MRR, while RoPE has higher target value probability | Production transformer result or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 16 learned attention stability | Five initialization-seed reruns of Stage 15 | PhaseWrap-plus-distance preserves top-1/MRR leadership across the tested seeds; RoPE has higher target value probability | Production transformer result or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 17 small decoder value model | Learned value embeddings and output projection over Stage 14 rows | All tested methods are near chance in the current compact value-output setup | Production transformer result or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 18 value-output capacity probe | Uniform and teacher-forced target attention through the learned value-output path | Teacher forcing does not substantially improve train or test performance, pointing to value-output capacity/optimization as a bottleneck | Production transformer result or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 19 value-output hardening probe | Teacher-forced target attention with full-batch Adam and larger learned value embeddings | Train fit is solved and held-out value-token retrieval improves, showing the value-output path is improvable | Positional-mechanism comparison, production transformer result, or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 20 hardened positional value model | Learned positional attention with the hardened value-output path over Stage 14 rows | `rope_relative` is strongest on held-out value-token retrieval; PhaseWrap-plus-distance trails on this packet | Production transformer result or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 21 hardened positional stability | Five initialization-seed reruns of Stage 20 | `rope_relative` remains strongest by mean held-out top-1/MRR; PhaseWrap-plus-distance remains behind on MRR | Production transformer result or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 22 long-context retrieval | Explicit passkey, multi-needle, and aggregation rules through 4096-token contexts | RoPE-like and sinusoidal fixed scoring solve the packet; fixed PhaseWrap 8/12 is weak | Production transformer result or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 23 long-context adapter | Train-short/test-long adapters on Stage 22 rows | PhaseWrap-plus-distance matches RoPE-like top-1/MRR at 4096, while RoPE-like scoring has higher target probability mass | Production transformer result or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 24 long-context value model | Learned value embeddings/output projection on Stage 22 rows | `rope_relative` is strongest on held-out value retrieval; PhaseWrap-derived adapters trail | Production transformer result or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 25 long-context value stability | Five initialization-seed reruns of Stage 24 | `rope_relative` remains strongest by mean held-out top-1/MRR; PhaseWrap-derived adapters trail | Production transformer result or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 26 compact key-value QA | Explicit content-key retrieval with distractor facts | PhaseWrap-derived adapters match ALiBI-style top-1/MRR on this packet; fixed PhaseWrap scoring remains weak | Production transformer result or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 27 compact key-value transformer bridge | One-hidden-layer attention bridge over Stage 26 candidate features across five model initialization seeds | PhaseWrap-plus-distance ties ALiBI-style top-1/MRR and slightly leads target probability on this compact bridge | Full decoder-only language-model result or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 28 RULER-style attention bridge | One-hidden-layer attention bridge over Stage 12 non-phase-cued retrieval rows across five model initialization seeds | PhaseWrap-plus-distance matches RoPE-like top-1/MRR, while RoPE-like scoring keeps stronger probability and calibration metrics | Full decoder-only language-model result or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 29 period-pair task audit | Stage 11 period-pair grid over local and long-context retrieval rows | Period-pair swaps alone do not solve the fixed-score retrieval gap | Proof of a globally optimal period pair or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 30 matched retrieval bridge | Equal feature-width and parameter-count bridge over Stage 12 non-phase-cued retrieval rows | PhaseWrap-plus-distance matches RoPE-like top-1/MRR under the matched budget, while RoPE-like scoring keeps stronger probability and calibration metrics | Full decoder-only language-model result or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 31 full-context retrieval attention | Learned four-parameter attention over every prefix position on Stage 12 rows | RoPE-like scoring solves the held-out packet; current PhaseWrap variants are weak | Full decoder-only language-model result or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 32 full-context feature bridge | Nonlinear full-prefix feature bridge over Stage 12 rows | PhaseWrap distance/multiscale adapters recover top-1/MRR; RoPE-like scoring keeps stronger probability and calibration metrics | Full decoder-only language-model result or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 33 temperature calibration audit | Validation-selected post-hoc temperature scaling for the Stage 32 bridge | PhaseWrap-derived adapters keep top-1/MRR and improve probability/ECE; RoPE-like scoring remains strongest on calibrated probability/ECE | Full decoder-only language-model result or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 34 small decoder value bridge | Learned attention, learned value embeddings, and output projection over Stage 14 key-value rows | RoPE-like scoring is strongest; current PhaseWrap-derived adapters trail under the value-output bottleneck | Full decoder-only language-model result or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 35 value-bridge bottleneck diagnostic | Teacher-forced target attention over Stage 14 key-value rows | Value output is partly viable but not solved; learned attention/mechanism selection remains a major bottleneck | Full decoder-only language-model result or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 36 copy-value bridge | Learned attention with copy-style value output over Stage 14 key-value rows | PhaseWrap-derived adapters recover top-1/MRR; RoPE-like scoring keeps stronger target probability mass | Full decoder-only language-model result or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 37 copy-value temperature calibration | Validation-selected post-hoc temperature scaling for the Stage 36 bridge | PhaseWrap-derived adapters keep top-1/MRR and sharply improve target probability; RoPE-like scoring remains strongest on calibrated probability/ECE | Full decoder-only language-model result or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 38 hardened decoder value bridge | Larger learned attention/value-output bridge over Stage 14 key-value rows | All methods fit train, but held-out length generalization still favors RoPE-like scoring over the PhaseWrap-derived adapters | Full decoder-only language-model result or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 39 sequence decoder retrieval | All-prefix sequence-style decoder retrieval over Stage 14 rows | Several methods fit train, but all tested methods collapse on held-out length extrapolation | Full decoder-only language-model result or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 40 sequence length curriculum | All-prefix sequence decoder trained on lengths 128/256/512 and tested on 2048 | Curriculum does not repair length extrapolation; PhaseWrap-derived adapters lead weak 2048-token test rows | Full decoder-only language-model result or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 41 pointer/copy sequence | All-prefix sequence decoder with copy-style value output over observed prefix token IDs | Copy output repairs 2048-token ranking for RoPE-like scoring and PhaseWrap multiscale; RoPE-like scoring remains best calibrated | Full decoder-only language-model result or proof that PhaseWrap-RoPE replaces RoPE |
| Stage 42 trainable pointer-generator sequence | All-prefix sequence decoder with learned copy/vocab mixture | Strong ranking mostly survives, but RoPE-like scoring remains best and the learned generator branch is weak | Full decoder-only language-model result or proof that PhaseWrap-RoPE replaces RoPE |

The allowed public claims are:

- PhaseWrap-RoPE defines a phase-wrap positional scoring rule.
- The score is computed from mod-8 and mod-12 signed-margin structure.
- The validation lane uses frozen packets, raw counts, backend metadata, and offline recomputation.
- The Stage 4 evidence record contains bounded hardware-positive results for recorded IBM Fez and Amazon Braket packet contexts, including product-state and provider-aware CX artifacts.
- IonQ is excluded from the active sweep described here because the current Amazon Braket check found the relevant IonQ route unavailable or not run.

The excluded claims are:

- broad quantum advantage;
- production transformer superiority;
- full transformer-scale validation;
- general cross-backend robustness;
- commercial performance improvement in deployed language models.

This boundary follows the manuscript-to-provisional support audit and the conservative patent-status note for the USPTO acknowledgement receipt.

Claims should not be promoted beyond the highest tier supported by committed packet, verifier, and artifact records.

## 3. Method

![PhaseWrap-RoPE phase-wrap method schematic](figures/qrope-method-schematic-v1.svg)

Figure 1. PhaseWrap-RoPE phase-wrap scoring schematic. The figure is conceptual; the normative method is the formula block below.

For integer offsets `delta_a` and `delta_b`, define a period-specific wrapped phase:

```text
wrap_pi(x) = x shifted by integer multiples of 2*pi into the interval (-pi, pi]

theta_P(delta) = wrap_pi(2*pi*delta/P)

r_P(delta_a, delta_b) = abs(wrap_pi(theta_P(delta_a) - theta_P(delta_b)))
```

The two signed margins used in this release are:

```text
r8  = r_8(delta_a, delta_b)
r12 = r_12(delta_a, delta_b)

m8  = cos(r8)  - cos(pi/4)
m12 = cos(r12) - cos(pi/6)
```

The local PhaseWrap-RoPE score is:

```text
SQR = m8 * m12
```

The thresholds are tied to one modular step in each basis. For period 8, one step is `2*pi/8 = pi/4`; for period 12, one step is `2*pi/12 = pi/6`. Subtracting `cos(pi/4)` and `cos(pi/6)` centers each margin at the one-step residual boundary: margins are positive for residuals closer than one modular step, approximately zero at one step, and negative beyond one step.

The period pair `8` and `12` is a fixed first-release design choice rather than a proven optimum. It gives two distinct wrapped residual bases, two different one-step thresholds, and a simple cross-band interaction through the product of signed margins. Other period pairs, learned period schedules, and task-conditioned period selection are intentionally left as future ablation targets.

The repository now includes a deterministic Stage 11 score-theory analysis:

```bash
python scripts/run_stage11_phasewrap_theory.py
```

Stage 11 verifies that the default 8/12 score has least common period `24`, is invariant under joint translation of both offsets, is invariant when either offset is shifted by `24`, and is symmetric under sign reversal of the offset difference. The mod-24 residue table contains `10` distinct score values after mirrored and zero-margin aliases are accounted for. Fourier analysis over the residue table gives positive frequency support `[1, 2, 3, 5]`, so the fixed score is exactly representable as a small classical periodic feature map. This makes the score easier to audit, but it also makes the aliasing limitation explicit.

The implementation normalizes the score for packet labels by clamping:

```text
label = clamp(0.5 + 0.5 * SQR / MAX_ABS_SCORE, 0, 1)
```

where `MAX_ABS_SCORE` is computed over the fixed delta grid used by the packet generator.

### Algorithm 1. Local PhaseWrap-RoPE score

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

## 4. Two-Qubit Readout Families

The product-state witness normalizes the margins into Z targets:

```text
z0 = clamp(m8 / MAX_ABS_M8, -1, 1)
z1 = clamp(m12 / MAX_ABS_M12, -1, 1)
theta_0 = arccos(z0)
theta_1 = arccos(z1)
```

The circuit prepares each qubit with a Y-axis rotation using `theta_0` and `theta_1`, measures computational-basis counts, and estimates `E[Z0]`, `E[Z1]`, and `E[Z0 Z1]`. The Stage 4 packet uses the `two_qubit_zz_expectation_phase_wrap_v1` family.

The original Stage 4 circuit is a product-state angle-encoding/readout witness. It contains no entangling gate. Consequently, the measured `E[Z0 Z1]` term should be understood as a hardware readout of the cross-band product induced by independently encoded margins, not as evidence of entanglement, quantum speedup, or nonclassical interference.

The repository now includes an opt-in entangling CX witness family:

```text
two_qubit_cx_parity_phase_wrap_v2
```

This variant applies `CX(q0 -> q1)` after the two `RY` margin encodings. In the ideal circuit, the target-qubit Z expectation after CX carries the cross-band parity/product signal. The corresponding witness and control scores are:

```text
witness_cx = clamp(0.5 + 0.5 * score_scale * E[Z1 after CX], 0, 1)
control_cx = clamp(0.5 + 0.25 * (E[Z0 after CX] + E[Z0 Z1 after CX]), 0, 1)
```

This variant has a completed IBM Fez hardware-positive artifact in the active public sweep. It also has completed Amazon Braket artifacts on Rigetti Cepheus, IQM Garnet, and IQM Emerald that verify as hardware-positive under manifest-declared `q0q1` Amazon Braket bitstring decoding. The earlier generic `q1q0` decode classified those Braket CX records as negative; the diagnostic remains as audit evidence for that correction. The positive claim remains bounded to recorded packet/backend/date/calibration-specific results and does not establish entanglement advantage, quantum advantage, or cross-backend robustness.

The CX witness should be read pragmatically. It checks whether the same frozen signal survives an entangling readout path; it does not establish entanglement advantage or quantum advantage.

Implementation reference: `src/qrope/automated_stage_gates.py`.

## 5. Classical and Downstream Baselines

The repository also includes a deterministic Stage 5 attention-scoring baseline suite:

```bash
python scripts/run_stage5_attention_baselines.py
```

This suite compares the phase-wrap score against a 24-way lookup on `(reference_delta - candidate_delta) mod 24`, a direct `m8`/`m12`/`m8*m12` feature baseline, a shallow regression tree on exposed deltas, and RoPE-style, sinusoidal, and ALiBI-style scoring rules. On the current synthetic task, the mod-24 lookup and direct product-feature baselines recover the label exactly. This is reported as a baseline closure and limitation: the task validates the current scoring construction, but it does not establish transformer-scale superiority or production language-model improvement.

The repository further includes a deterministic Stage 6 toy downstream attention benchmark:

```bash
python scripts/run_stage6_downstream_attention.py
```

Stage 6 mixes token/content compatibility with phase-wrap positional signal. The resulting target is not exactly recovered by mod-24 lookup or direct `m8`/`m12`/`m8*m12` features alone. Because the PhaseWrap model sees the normalized phase label directly, Stage 6 is best read as an oracle phase-feature sanity check. On the fixed packet, `phasewrap_rope_attention` has the lowest MAE against RoPE, ALiBI, sinusoidal, no-position, mod-24 lookup, and classical phase-feature baselines. This is bounded toy evidence only.

The repository also includes a deterministic Stage 7 toy transformer ablation:

```bash
python scripts/run_stage7_toy_transformer_ablation.py
```

Stage 7 tests a four-layer attention-only toy transformer ablation on one synthetic length-extrapolation retrieval packet. The reported result supports continued investigation in transformer-adjacent settings, but it remains a toy result. The PhaseWrap variant has the best argmax retrieval ranking by top-1 and MRR on the fixed packet; it does not have the best target-probability calibration. It does not establish production transformer superiority.

The repository also includes a deterministic Stage 8 local Needle-style benchmark:

```bash
python scripts/run_stage8_needle_benchmark.py
```

Stage 8 compares PhaseWrap-RoPE against RoPE-like, ALiBI-like, sinusoidal, and no-position scoring rules on a phase-cued synthetic retrieval packet with five seeds, context lengths up to 1024, row-bootstrap intervals, and a period-pair ablation. On this packet, `phasewrap_rope_8_12` has top-1 `1.0` and MRR `1.0`, and the `(8, 12)` period pair is best among the tested pairs. This supports keeping the RoPE-facing replacement research lane open, but it is not a RULER benchmark, a trained language-model benchmark, or a proof that the method replaces RoPE.

The repository also includes the first executable Stage 9 trained positional-attention ablation:

```bash
python scripts/run_stage9_trained_transformer_ablation.py
```

Stage 9 trains matched decoder-style positional attention mechanisms across five seeds, short training contexts, and longer test contexts. The current synthetic packets compare `phasewrap_bias`, `phasewrap_adapter`, `rope_relative`, `alibi`, `sinusoidal`, and `no_position`. On the phase-cued packet, `phasewrap_adapter` has mean test top-1 `0.668750` and mean test MRR `0.745096`, with no failed runs. On the exact-offset passkey packet, whose target is not selected by the PhaseWrap score, `rope_relative` has mean test top-1 `1.000000`, mean test MRR `1.000000`, and lower mean test loss than `phasewrap_adapter`. This is a trained positional-attention result, not a full language-model benchmark.

The repository also includes a Stage 10 small decoder-only transformer ablation:

```bash
python scripts/run_stage10_small_decoder_transformer.py
```

Stage 10 trains a very small one-block decoder-only single-head transformer with token embeddings, query/key/value projections, an output projection, and a positional scale. The tested variants use matched seeds, tasks, model shape, optimizer, and epochs. The task set includes phase-cued retrieval, exact-offset passkey retrieval, and a tiny curated text-fact QA lane. The current result is near chance across the tested lanes, with target probabilities near uniform (`~0.007813`); the regenerated artifact also reports target-probability MAE, top-1 confidence, and expected calibration error. The included capacity probe does not show strong training-set fit. It is therefore reported as a negative or inconclusive first full-transformer sanity check rather than as a PhaseWrap advantage.

The repository also includes a deterministic Stage 12 RULER-style retrieval benchmark:

```bash
python scripts/run_stage12_ruler_retrieval.py
```

Stage 12 uses passkey, multi-needle, and aggregation-style retrieval rows whose targets are selected by explicit task rules and RNG offsets rather than by the PhaseWrap score. On this packet, `sinusoidal` and `rope_relative` have top-1 `1.000000` and MRR `1.000000`; `phasewrap_rope_8_12` has top-1 `0.020833` and MRR `0.156865`. The PhaseWrap oracle target-overlap diagnostic is `0.020833`, confirming that the packet is not phase-cued. This is useful negative evidence: the fixed 8/12 score is not sufficient for exact-offset retrieval, and a stronger PhaseWrap positional mechanism is needed before any RoPE-replacement claim.

The repository also includes a deterministic Stage 13 positional-adapter benchmark:

```bash
python scripts/run_stage13_positional_adapter.py
```

Stage 13 trains lightweight positional adapters on Stage 12 rows with short contexts and evaluates on held-out length-1024 rows. The fixed `phasewrap_score` remains weak with top-1 `0.016667` and MRR `0.080860`. The `phasewrap_residual_adapter` improves to top-1 `0.450000` and MRR `0.673611`. The `phasewrap_distance_adapter` reaches top-1 `1.000000` and MRR `1.000000`, matching `rope_relative` on argmax ranking, while `rope_relative` has higher mean target-probability mass (`0.821549` versus `0.429105`). This supports the next mechanism direction: PhaseWrap-derived features need explicit distance or comparable positional information for exact-offset retrieval.

The repository also includes a deterministic Stage 14 attention-readout benchmark:

```bash
python scripts/run_stage14_attention_readout.py
```

Stage 14 converts the Stage 12 non-phase-cued rows into key-value attention-readout rows. It evaluates whether the positional mechanism recovers target value tokens, not just target positions. The result preserves the Stage 13 pattern: `phasewrap_distance_adapter` reaches top-1 `1.000000` and MRR `1.000000`, matching `rope_relative`; `rope_relative` has higher mean target value probability (`0.824888` versus `0.432405`). This is stronger evidence for a candidate adapter shape, but it is still not a full transformer benchmark.

The repository also includes a deterministic Stage 15 learned attention-readout benchmark:

```bash
python scripts/run_stage15_learned_attention.py
```

Stage 15 trains a one-hidden-layer scorer over each positional feature family on the Stage 14 key-value rows. On the held-out length-1024 rows, `phasewrap_distance_adapter` has top-1 `1.000000`, MRR `1.000000`, and mean target value probability `0.516181`. `rope_relative` has top-1 `0.933333`, MRR `0.966667`, and higher mean target value probability `0.678210`. This is the strongest local ranking evidence so far for the PhaseWrap-plus-distance adapter shape, while still falling short of a full transformer or production-language-model claim.

The repository also includes a deterministic Stage 16 learned attention stability benchmark:

```bash
python scripts/run_stage16_learned_attention_stability.py
```

Stage 16 reruns the Stage 15 learned attention-readout benchmark across five deterministic initialization seeds. `phasewrap_distance_adapter` has mean top-1 `1.000000`, top-1 min-max `1.000000-1.000000`, mean MRR `1.000000`, and mean target value probability `0.522507`. `rope_relative` has mean top-1 `0.983333`, top-1 min-max `0.933333-1.000000`, mean MRR `0.991667`, and higher mean target value probability `0.706780`. This strengthens the local ranking evidence while preserving the calibration caveat.

The repository also includes a deterministic Stage 17 small decoder value-model benchmark:

```bash
python scripts/run_stage17_small_decoder_value_model.py
```

Stage 17 adds learned value embeddings and a learned output projection to the Stage 14 key-value rows. The result is near chance for every tested positional method: `phasewrap_distance_adapter` has top-1 `0.016667`, MRR `0.035684`, and mean target value probability `0.005179`; `rope_relative` has top-1 `0.016667`, MRR `0.035220`, and mean target value probability `0.005179`. This is negative evidence for the current compact decoder-style value-output setup and indicates that optimization/capacity hardening is needed before the adapter can be interpreted inside a stronger transformer.

The repository also includes a deterministic Stage 18 value-output capacity probe:

```bash
python scripts/run_stage18_value_output_capacity.py
```

Stage 18 compares uniform attention with teacher-forced target attention through the same learned value embeddings and output projection used to diagnose Stage 17. On the held-out test rows, `uniform_attention` has top-1 `0.016667`, MRR `0.034671`, and mean target value probability `0.005182`; `teacher_forced_attention` has top-1 `0.016667`, MRR `0.041872`, and mean target value probability `0.005308`. Teacher forcing improves MRR slightly but does not substantially fix train or test performance, so the next transformer-style experiment should harden the learned value-output path before drawing conclusions about positional mechanisms.

The repository also includes a deterministic Stage 19 value-output hardening probe:

```bash
python scripts/run_stage19_value_output_hardening.py
```

Stage 19 keeps attention teacher-forced and changes the value-output path to full-batch Adam with larger learned value embeddings. The best held-out result by top-1/MRR is `adam_embed12`, with train top-1 `1.000000`, train MRR `1.000000`, test top-1 `0.533333`, test MRR `0.552776`, and test mean target value probability `0.480821`. This shows that the Stage 17/18 value-output bottleneck is improvable. It does not compare PhaseWrap against RoPE because positional attention is bypassed.

The repository also includes a deterministic Stage 20 hardened positional value-model benchmark:

```bash
python scripts/run_stage20_hardened_positional_value_model.py
```

Stage 20 reintroduces learned positional attention while keeping the hardened value-output path. All methods fit the training rows, but held-out value-token retrieval favors `rope_relative`: top-1 `0.383333`, MRR `0.429275`, and mean target value probability `0.350653`. `phasewrap_distance_adapter` has top-1 `0.250000`, MRR `0.321470`, and mean target value probability `0.193673`; the fixed `phasewrap_score` has top-1 `0.000000` and MRR `0.032774`. This is negative/mixed evidence for the current PhaseWrap adapter on the non-phase-cued packet, not evidence that PhaseWrap-RoPE replaces RoPE.

The repository also includes a deterministic Stage 21 hardened positional stability benchmark:

```bash
python scripts/run_stage21_hardened_positional_stability.py
```

Stage 21 reruns Stage 20 across five learned-parameter initialization seeds. `rope_relative` remains strongest with mean top-1 `0.376666`, top-1 range `0.350000-0.383333`, mean MRR `0.421212`, and mean target value probability `0.351668`. `phasewrap_distance_adapter` has mean top-1 `0.286667`, top-1 range `0.250000-0.316667`, mean MRR `0.339284`, and mean target value probability `0.205887`. This stabilizes the Stage 20 negative/mixed result for the current non-phase-cued packet.

The repository also includes a deterministic Stage 22 long-context retrieval benchmark:

```bash
python scripts/run_stage22_long_context_retrieval.py
```

Stage 22 extends the Stage 12 explicit passkey, multi-needle, and aggregation retrieval rules to contexts `512`, `1024`, `2048`, and `4096`. On 240 rows, `sinusoidal` and `rope_relative` both have top-1 `1.000000` and MRR `1.000000`. Fixed `phasewrap_rope_8_12` has top-1 `0.012500`, MRR `0.096153`, and mean target probability mass `0.021593`. This strengthens the evidence that the fixed 8/12 score is not sufficient for non-phase-cued exact retrieval.

The repository also includes a deterministic Stage 23 long-context adapter benchmark:

```bash
python scripts/run_stage23_long_context_adapter.py
```

Stage 23 trains positional adapters on the Stage 22 rows with train lengths `512`/`1024`, validation length `2048`, and test length `4096`. On the held-out `4096` rows, `phasewrap_distance_adapter` has top-1 `1.000000`, MRR `1.000000`, and mean target probability mass `0.600201`, matching `rope_relative` on top-1/MRR. `rope_relative` has higher mean target probability mass `0.910440`. This supports the trained adapter direction while preserving the calibration gap.

The repository also includes a deterministic Stage 24 long-context value-model benchmark:

```bash
python scripts/run_stage24_long_context_value_model.py
```

Stage 24 adds learned value embeddings and output projection to the Stage 22 long-context rows. All methods fit the training rows at top-1 `1.000000` and MRR `1.000000`, but held-out `4096` token value retrieval favors `rope_relative` with top-1 `0.350000`, MRR `0.399642`, and mean target value probability `0.362745`. The strongest PhaseWrap-derived method is `phasewrap_residual_adapter`, with top-1 `0.133333`, MRR `0.221899`, and mean target value probability `0.118677`. This is negative/mixed evidence for the current PhaseWrap-derived value-model path.

The repository also includes a deterministic Stage 25 long-context value-model stability benchmark:

```bash
python scripts/run_stage25_long_context_value_stability.py
```

Stage 25 reruns Stage 24 across five learned-parameter initialization seeds. `rope_relative` remains strongest with mean top-1 `0.383333`, mean MRR `0.426498`, and mean target value probability `0.362492`. The strongest PhaseWrap-derived method is `phasewrap_residual_adapter`, with mean top-1 `0.073333`, mean MRR `0.120739`, and mean target value probability `0.055600`. This confirms the Stage 24 held-out ordering across the tested seeds.

The repository also includes a deterministic Stage 26 compact key-value QA retrieval benchmark:

```bash
python scripts/run_stage26_compact_kv_qa.py
```

Stage 26 adds explicit content keys and distractor facts. On held-out `2048` token rows, `alibi`, `phasewrap_residual_adapter`, and `phasewrap_distance_adapter` each have top-1 `0.950000` and MRR `0.975000`; `phasewrap_distance_adapter` has the highest mean target probability among those tied methods at `0.767915`. `rope_relative` has top-1 `0.500000` and MRR `0.716667` on this packet, while the fixed `phasewrap_score` remains weak with top-1 `0.300000` and MRR `0.608333`. This is constructive compact-retrieval evidence, not full transformer evidence.

The repository also includes a deterministic Stage 27 compact key-value transformer-bridge benchmark:

```bash
python scripts/run_stage27_compact_kv_transformer_bridge.py
```

Stage 27 trains a one-hidden-layer attention bridge over the Stage 26 candidate features across five model initialization seeds. On held-out `2048` token rows, `phasewrap_distance_adapter` and `alibi` tie at mean top-1 `0.950000` and mean MRR `0.975000`; `phasewrap_distance_adapter` has slightly higher mean target probability (`0.823006` versus `0.821886`). `phasewrap_residual_adapter` follows with mean top-1 `0.920000` and mean MRR `0.960000`; `rope_relative` has mean top-1 `0.320000` and mean MRR `0.541381`. This is a compact bridge toward the roadmap, not a full decoder-only language-model benchmark.

The repository also includes a deterministic Stage 28 RULER-style attention-bridge benchmark:

```bash
python scripts/run_stage28_ruler_attention_bridge.py
```

Stage 28 trains a one-hidden-layer attention bridge directly on Stage 12 non-phase-cued passkey, multi-needle, and aggregation-style retrieval rows across five model initialization seeds. `phasewrap_distance_adapter` and `rope_relative` both reach mean top-1 `1.000000` and mean MRR `1.000000`; `rope_relative` keeps higher mean target probability (`0.704867` versus `0.518441`) and lower top-1 expected calibration error (`0.297454` versus `0.486407`). This is compact retrieval-bridge evidence, not a full decoder-only language-model benchmark.

The repository also includes a deterministic Stage 29 period-pair task audit:

```bash
python scripts/run_stage29_period_pair_task_audit.py
```

Stage 29 evaluates the Stage 11 period-pair grid on Stage 12 local and Stage 22 long-context retrieval rows. No tested fixed period pair solves the non-phase-cued packets. The best local top-1 is `8/24` at `0.045833`; the default `8/12` local top-1 is `0.020833`. The best long-context top-1 is `9/15` at `0.016667`; default `8/12` long top-1 is `0.012500`. This supports the adapter/transformer direction rather than a claim that another fixed period pair is enough.

The repository also includes a deterministic Stage 30 matched retrieval-bridge benchmark:

```bash
python scripts/run_stage30_matched_retrieval_bridge.py
```

Stage 30 reruns the Stage 28 non-phase-cued retrieval bridge while equalizing feature width, hidden width, learned parameter count, optimizer, epochs, and model initialization count across positional variants. Every method uses feature width `12`, hidden width `10`, and learned parameter count `141`. On held-out Stage 12 rows, `phasewrap_distance_adapter` and `rope_relative` both reach mean top-1 `1.000000` and mean MRR `1.000000`; `rope_relative` keeps higher mean target probability (`0.744078` versus `0.564161`) and lower expected calibration error (`0.260653` versus `0.446620`). This removes one compact-bridge confound from Stage 28, but it remains a retrieval bridge rather than a full decoder-only language-model benchmark.

The repository also includes a deterministic Stage 31 full-context retrieval-attention benchmark:

```bash
python scripts/run_stage31_full_context_retrieval_attention.py
```

Stage 31 trains the same four attention parameters for each positional variant while every prefix position competes. This is harder than the candidate-only Stage 30 bridge. On held-out Stage 12 rows, `rope_relative` reaches mean top-1 `1.000000`, mean MRR `1.000000`, and mean target probability `0.821104`. The current PhaseWrap variants are weak: `phasewrap_bias` has mean top-1 `0.016667`, and `phasewrap_distance_adapter` has mean top-1 `0.000000`. This is negative evidence for the current PhaseWrap variants under a stricter full-prefix retrieval-attention harness.

The repository also includes a deterministic Stage 32 full-context feature-bridge benchmark:

```bash
python scripts/run_stage32_full_context_feature_bridge.py
```

Stage 32 keeps the Stage 31 full-prefix setting but replaces the four-parameter attention rule with a one-hidden-layer feature bridge. Every method uses feature width `12`, hidden width `10`, learned parameter count `141`, and five model seeds. `rope_relative`, `phasewrap_distance_adapter`, and `phasewrap_multiscale_adapter` all reach mean top-1 `1.000000` and mean MRR `1.000000`; `rope_relative` keeps higher mean target probability (`0.713026` versus `0.480310` for multiscale and `0.429075` for distance) and lower expected calibration error. This is constructive mechanism evidence, not a RoPE replacement claim.

## 6. Validation Protocol

![PhaseWrap-RoPE deterministic validation pipeline](figures/qrope-validation-pipeline-v1.svg)

Figure 2. Deterministic validation lane. The verification path is designed to recompute metrics from frozen packet files and execution records.

The validation protocol is designed around reproducibility rather than opportunistic metric selection. A valid evidence packet should include:

- frozen input rows;
- fixed row count;
- fixed shot count for hardware or simulator execution;
- raw measurement counts;
- backend metadata;
- packet identifier;
- offline verifier;
- deterministic pass/fail or bounded status outcome.

For the Stage 4 packet, the verifier entry point is:

```bash
python scripts/verify_stage4_hardware_packet.py
```

For the Stage 4 hardware sweep manifest, the verifier entry point is:

```bash
python scripts/verify_stage4_hardware_sweep.py
```

For the Stage 4 local classical recomputation cost estimate, the entry point is:

```bash
python scripts/estimate_stage4_classical_compute_cost.py
```

For preregistering future Stage 4 replication packet sets without hardware submission, the entry point is:

```bash
python scripts/preregister_stage4_replication_packets.py
```

For preparing provider bitstring calibration specs and checking whether real calibration counts are present, the entry points are:

```bash
python scripts/prepare_stage4_bitstring_calibration_packets.py
python scripts/verify_stage4_bitstring_calibration.py
```

The sweep verifier recomputes metrics only for active completed records whose packet, execution, evaluation, and summary artifacts are present. Deferred or unavailable targets are documented in the manifest but are not treated as required verifier records.

The default verifier inputs are:

- `logs/automated_stage_gates/stage4_hardware_packet/frozen_packet.json`
- `logs/automated_stage_gates/stage4_hardware_packet/execution.json`
- `logs/automated_stage_gates/stage4_hardware_packet/evaluation.json`
- `logs/automated_stage_gates/stage4_hardware_packet/summary.json`

The default single-packet path is the reviewer convenience path. The same IBM Fez 2026-05-17 product-state pass is also preserved as the immutable named run:

- `logs/automated_stage_gates/stage4_hardware_packet_ibm_fez_20260517_pass/frozen_packet.json`
- `logs/automated_stage_gates/stage4_hardware_packet_ibm_fez_20260517_pass/execution.json`
- `logs/automated_stage_gates/stage4_hardware_packet_ibm_fez_20260517_pass/evaluation.json`
- `logs/automated_stage_gates/stage4_hardware_packet_ibm_fez_20260517_pass/summary.json`
- `logs/automated_stage_gates/stage4_hardware_packet_ibm_fez_20260517_pass/offline_verification.json`

The default verifier output is:

- `logs/automated_stage_gates/stage4_hardware_packet/offline_verification.json`

IBM Quantum Runtime primitives provide the execution model used by the hardware lane: Sampler samples circuit output registers, while IBM backend documentation describes dynamic backend properties and calibration metadata that can change over time [3-5].

This verifier supports recomputation, not independent replication. Recomputing the saved packet verifies that the reported metrics follow from the published raw counts and metadata. Replication requires a new execution of the same frozen packet, preferably across additional dates and backends.

## 7. Hardware Validation Records

The active Stage 4 hardware sweep includes six completed records: the original IBM Fez product-state hardware packet, an IBM Fez CX hardware-positive packet, an Amazon Braket/Rigetti product-state hardware-positive replication artifact, and Amazon Braket CX artifacts on Rigetti Cepheus, IQM Garnet, and IQM Emerald. The Braket CX artifacts verify as hardware-positive under the provider-aware sweep verifier, which decodes Amazon Braket result keys as `q0q1`; the earlier generic `q1q0` classification is retained only as diagnostic audit context. Additional IBM machines are deferred from the active sweep. IonQ is not an active sweep record: the current intended route is Amazon Braket, and a read-only Braket check on 2026-05-19 found `Forte-1` and `Forte-Enterprise-1` `OFFLINE` and `Aria-1` `RETIRED`, so no IonQ hardware task was submitted.

The canonical fully enumerated product-state run is the IBM Fez packet:

| Field | Value |
| --- | --- |
| Provider | `ibm_runtime` |
| Backend | `ibm_fez` |
| Job ID | `d84jbq00bvlc73d4krr0` |
| Packet ID | `qrope-hardware-73c61893576297ff` |
| Rows | `16` |
| Shots per row | `4096` |
| Submitted UTC | `2026-05-17T03:28:38Z` |
| Completed UTC | `2026-05-17T03:29:05Z` |
| Calibration metadata captured | yes |
| Backend qubits in captured metadata | `156` |
| Witness MAE | `0.018382` |
| Witness rank correlation | `0.876558` |
| Control MAE | `0.217262` |
| Control rank correlation | `-0.176940` |
| Outcome | `hardware-positive` |

The active sweep records also include:

| Record class | Backend/context | Shots | Status in paper |
| --- | --- | ---: | --- |
| Product-state canonical packet | IBM Fez | 4096 | completed, hardware-positive |
| CX packet | IBM Fez | 4096 | completed, hardware-positive artifact |
| Product-state replication | Amazon Braket/Rigetti | 1000 | completed, machine-verifiable sweep evidence |
| CX provider-aware records | Rigetti Cepheus, IQM Garnet, IQM Emerald | 1000 per row | completed under manifest-declared `q0q1` Braket decoding |
| IonQ via Amazon Braket | Forte/Aria route | not submitted | unavailable/not-run in current check |
| Additional IBM targets | deferred | not promoted | not active public evidence until full artifacts are committed |

The machine-verifiable active sweep table is:

| Backend | Provider | Family | Shots | Rows | Witness MAE | Witness rank corr | Control MAE | Control rank corr | Outcome |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| IBM Fez | `ibm_runtime` | `two_qubit_zz_expectation_phase_wrap_v1` | 4096 | 16 | 0.018382 | 0.876558 | 0.217262 | -0.176940 | `hardware-positive` |
| Rigetti Cepheus-1-108Q | `amazon_braket` | `two_qubit_zz_expectation_phase_wrap_v1` | 1000 | 8 | 0.069901 | 0.786644 | 0.149995 | 0.121232 | `hardware-positive` |
| IBM Fez | `ibm_runtime` | `two_qubit_cx_parity_phase_wrap_v2` | 4096 | 16 | 0.021458 | 0.972455 | 0.212516 | -0.169318 | `hardware-positive` |
| Rigetti Cepheus-1-108Q | `amazon_braket` | `two_qubit_cx_parity_phase_wrap_v2` | 1000 | 8 | 0.061643 | 0.557668 | 0.194370 | -0.060616 | `hardware-positive` |
| IQM Garnet | `amazon_braket` | `two_qubit_cx_parity_phase_wrap_v2` | 1000 | 8 | 0.021719 | 0.981981 | 0.204370 | -0.060616 | `hardware-positive` |
| IQM Emerald | `amazon_braket` | `two_qubit_cx_parity_phase_wrap_v2` | 1000 | 8 | 0.021479 | 0.884995 | 0.210995 | -0.096986 | `hardware-positive` |

The Amazon Braket CX records require provider-aware bitstring handling. Under manifest-declared `q0q1` decoding, the records verify as hardware-positive. The earlier generic `q1q0` classification remains diagnostic audit evidence for why provider-specific result-key conventions matter.

Do not compress the active sweep into a broad cross-backend robustness result. The appropriate claim is narrower: recorded IBM Fez and Amazon Braket artifacts preserve the witness/control ordering under their stated packet, backend, date, shot, decoding, and calibration conditions.

The control condition is the additive single-band readout baseline:

```text
control = clamp(0.5 + 0.25 * (E[Z0] + E[Z1]), 0, 1)
```

The witness condition uses the cross-band product readout:

```text
witness = clamp(0.5 + 0.5 * score_scale * E[Z0 Z1], 0, 1)
```

The completed IBM Fez and Braket/Rigetti product-state records support the Stage 4 packet outcome under the recorded conditions. The completed Braket CX records support bounded provider-aware recomputation for their recorded packet/backend/date/calibration contexts. They do not support a general CX cross-backend claim. Backend calibration, queue conditions, transpilation details, result-key conventions, and packet composition can affect replication results. The result therefore remains scoped to the stated packet, backend, date, calibration window, and metrics.

The Stage 5 attention-scoring baseline artifacts are:

- `logs/automated_stage_gates/stage5_attention_baselines/manifest.json`
- `logs/automated_stage_gates/stage5_attention_baselines/results.json`
- `logs/automated_stage_gates/stage5_attention_baselines/summary.csv`

The Stage 6 toy downstream attention artifacts are:

- `logs/automated_stage_gates/stage6_downstream_attention/manifest.json`
- `logs/automated_stage_gates/stage6_downstream_attention/results.json`
- `logs/automated_stage_gates/stage6_downstream_attention/summary.csv`

The Stage 7 toy transformer ablation artifacts are:

- `logs/automated_stage_gates/stage7_toy_transformer_ablation/manifest.json`
- `logs/automated_stage_gates/stage7_toy_transformer_ablation/results.json`
- `logs/automated_stage_gates/stage7_toy_transformer_ablation/summary.csv`
- `logs/automated_stage_gates/stage7_toy_transformer_ablation/calibration_summary.csv`

The Stage 8 local Needle-style benchmark artifacts are:

- `logs/automated_stage_gates/stage8_needle_benchmark/manifest.json`
- `logs/automated_stage_gates/stage8_needle_benchmark/results.json`
- `logs/automated_stage_gates/stage8_needle_benchmark/summary.csv`
- `logs/automated_stage_gates/stage8_needle_benchmark/period_pair_ablation.csv`

The Stage 9 trained positional-attention artifacts are:

- `logs/automated_stage_gates/stage9_trained_transformer_ablation/manifest.json`
- `logs/automated_stage_gates/stage9_trained_transformer_ablation/results.json`
- `logs/automated_stage_gates/stage9_trained_transformer_ablation/summary.csv`
- `logs/automated_stage_gates/stage9_trained_transformer_ablation/per_seed_results.csv`
- `logs/automated_stage_gates/stage9_trained_transformer_ablation/failed_runs.json`

The Stage 10 small decoder-only transformer artifacts are:

- `logs/automated_stage_gates/stage10_small_decoder_transformer/manifest.json`
- `logs/automated_stage_gates/stage10_small_decoder_transformer/results.json`
- `logs/automated_stage_gates/stage10_small_decoder_transformer/summary.csv`
- `logs/automated_stage_gates/stage10_small_decoder_transformer/per_seed_results.csv`
- `logs/automated_stage_gates/stage10_small_decoder_transformer/failed_runs.json`

The Stage 4 classical recomputation cost artifacts are:

- `logs/automated_stage_gates/stage4_classical_compute_cost/manifest.json`
- `logs/automated_stage_gates/stage4_classical_compute_cost/results.json`
- `logs/automated_stage_gates/stage4_classical_compute_cost/summary.csv`

The Stage 4 preregistered replication packet artifacts are:

- `logs/automated_stage_gates/stage4_preregistered_replication_packets/manifest.json`
- `logs/automated_stage_gates/stage4_preregistered_replication_packets/ibm_product_seed314_rows16_shots4096.json`
- `logs/automated_stage_gates/stage4_preregistered_replication_packets/ibm_cx_seed314_rows16_shots4096.json`
- `logs/automated_stage_gates/stage4_preregistered_replication_packets/braket_product_seed2718_rows8_shots1000.json`
- `logs/automated_stage_gates/stage4_preregistered_replication_packets/braket_cx_seed2718_rows8_shots1000.json`

The Stage 4 bitstring calibration planning artifacts are:

- `logs/automated_stage_gates/stage4_bitstring_calibration/manifest.json`
- `logs/automated_stage_gates/stage4_bitstring_calibration/offline_verification.json`
- `logs/automated_stage_gates/stage4_bitstring_calibration/ibm_runtime_known_state_packet.json`
- `logs/automated_stage_gates/stage4_bitstring_calibration/amazon_braket_known_state_packet.json`

The Stage 11 score-theory artifacts are:

- `logs/automated_stage_gates/stage11_phasewrap_theory/manifest.json`
- `logs/automated_stage_gates/stage11_phasewrap_theory/results.json`
- `logs/automated_stage_gates/stage11_phasewrap_theory/alias_summary.csv`
- `logs/automated_stage_gates/stage11_phasewrap_theory/period_pair_summary.csv`
- `logs/automated_stage_gates/stage11_phasewrap_theory/residue_score_table.csv`

The Stage 12 RULER-style retrieval artifacts are:

- `logs/automated_stage_gates/stage12_ruler_retrieval/manifest.json`
- `logs/automated_stage_gates/stage12_ruler_retrieval/results.json`
- `logs/automated_stage_gates/stage12_ruler_retrieval/summary.csv`
- `logs/automated_stage_gates/stage12_ruler_retrieval/task_summary.csv`
- `logs/automated_stage_gates/stage12_ruler_retrieval/per_example_results.csv`

The Stage 13 positional-adapter artifacts are:

- `logs/automated_stage_gates/stage13_positional_adapter/manifest.json`
- `logs/automated_stage_gates/stage13_positional_adapter/results.json`
- `logs/automated_stage_gates/stage13_positional_adapter/summary.csv`
- `logs/automated_stage_gates/stage13_positional_adapter/task_summary.csv`

The Stage 14 attention-readout artifacts are:

- `logs/automated_stage_gates/stage14_attention_readout/manifest.json`
- `logs/automated_stage_gates/stage14_attention_readout/results.json`
- `logs/automated_stage_gates/stage14_attention_readout/summary.csv`
- `logs/automated_stage_gates/stage14_attention_readout/task_summary.csv`

The Stage 15 learned attention-readout artifacts are:

- `logs/automated_stage_gates/stage15_learned_attention/manifest.json`
- `logs/automated_stage_gates/stage15_learned_attention/results.json`
- `logs/automated_stage_gates/stage15_learned_attention/summary.csv`
- `logs/automated_stage_gates/stage15_learned_attention/task_summary.csv`

The Stage 16 learned attention stability artifacts are:

- `logs/automated_stage_gates/stage16_learned_attention_stability/manifest.json`
- `logs/automated_stage_gates/stage16_learned_attention_stability/results.json`
- `logs/automated_stage_gates/stage16_learned_attention_stability/summary.csv`
- `logs/automated_stage_gates/stage16_learned_attention_stability/per_run_results.csv`

The Stage 17 small decoder value-model artifacts are:

- `logs/automated_stage_gates/stage17_small_decoder_value_model/manifest.json`
- `logs/automated_stage_gates/stage17_small_decoder_value_model/results.json`
- `logs/automated_stage_gates/stage17_small_decoder_value_model/summary.csv`
- `logs/automated_stage_gates/stage17_small_decoder_value_model/task_summary.csv`

The Stage 18 value-output capacity probe artifacts are:

- `logs/automated_stage_gates/stage18_value_output_capacity/manifest.json`
- `logs/automated_stage_gates/stage18_value_output_capacity/results.json`
- `logs/automated_stage_gates/stage18_value_output_capacity/summary.csv`

The Stage 19 value-output hardening probe artifacts are:

- `logs/automated_stage_gates/stage19_value_output_hardening/manifest.json`
- `logs/automated_stage_gates/stage19_value_output_hardening/results.json`
- `logs/automated_stage_gates/stage19_value_output_hardening/summary.csv`

The Stage 20 hardened positional value-model artifacts are:

- `logs/automated_stage_gates/stage20_hardened_positional_value_model/manifest.json`
- `logs/automated_stage_gates/stage20_hardened_positional_value_model/results.json`
- `logs/automated_stage_gates/stage20_hardened_positional_value_model/summary.csv`
- `logs/automated_stage_gates/stage20_hardened_positional_value_model/task_summary.csv`

The Stage 21 hardened positional stability artifacts are:

- `logs/automated_stage_gates/stage21_hardened_positional_stability/manifest.json`
- `logs/automated_stage_gates/stage21_hardened_positional_stability/results.json`
- `logs/automated_stage_gates/stage21_hardened_positional_stability/summary.csv`
- `logs/automated_stage_gates/stage21_hardened_positional_stability/per_run_results.csv`

The Stage 22 long-context retrieval artifacts are:

- `logs/automated_stage_gates/stage22_long_context_retrieval/manifest.json`
- `logs/automated_stage_gates/stage22_long_context_retrieval/results.json`
- `logs/automated_stage_gates/stage22_long_context_retrieval/summary.csv`
- `logs/automated_stage_gates/stage22_long_context_retrieval/task_summary.csv`
- `logs/automated_stage_gates/stage22_long_context_retrieval/length_summary.csv`
- `logs/automated_stage_gates/stage22_long_context_retrieval/per_example_results.csv`

The Stage 23 long-context adapter artifacts are:

- `logs/automated_stage_gates/stage23_long_context_adapter/manifest.json`
- `logs/automated_stage_gates/stage23_long_context_adapter/results.json`
- `logs/automated_stage_gates/stage23_long_context_adapter/summary.csv`
- `logs/automated_stage_gates/stage23_long_context_adapter/task_summary.csv`

The Stage 24 long-context value-model artifacts are:

- `logs/automated_stage_gates/stage24_long_context_value_model/manifest.json`
- `logs/automated_stage_gates/stage24_long_context_value_model/results.json`
- `logs/automated_stage_gates/stage24_long_context_value_model/summary.csv`
- `logs/automated_stage_gates/stage24_long_context_value_model/task_summary.csv`

The Stage 25 long-context value-model stability artifacts are:

- `logs/automated_stage_gates/stage25_long_context_value_stability/manifest.json`
- `logs/automated_stage_gates/stage25_long_context_value_stability/results.json`
- `logs/automated_stage_gates/stage25_long_context_value_stability/summary.csv`
- `logs/automated_stage_gates/stage25_long_context_value_stability/per_run_results.csv`
- `logs/automated_stage_gates/stage25_long_context_value_stability/weak_run_records.json`

The Stage 26 compact key-value QA artifacts are:

- `logs/automated_stage_gates/stage26_compact_kv_qa/manifest.json`
- `logs/automated_stage_gates/stage26_compact_kv_qa/results.json`
- `logs/automated_stage_gates/stage26_compact_kv_qa/summary.csv`
- `logs/automated_stage_gates/stage26_compact_kv_qa/weak_runs.json`

The Stage 27 compact key-value transformer-bridge artifacts are:

- `logs/automated_stage_gates/stage27_compact_kv_transformer_bridge/manifest.json`
- `logs/automated_stage_gates/stage27_compact_kv_transformer_bridge/results.json`
- `logs/automated_stage_gates/stage27_compact_kv_transformer_bridge/summary.csv`
- `logs/automated_stage_gates/stage27_compact_kv_transformer_bridge/per_run_results.csv`
- `logs/automated_stage_gates/stage27_compact_kv_transformer_bridge/weak_runs.json`

The Stage 28 RULER-style attention-bridge artifacts are:

- `logs/automated_stage_gates/stage28_ruler_attention_bridge/manifest.json`
- `logs/automated_stage_gates/stage28_ruler_attention_bridge/results.json`
- `logs/automated_stage_gates/stage28_ruler_attention_bridge/summary.csv`
- `logs/automated_stage_gates/stage28_ruler_attention_bridge/per_run_results.csv`
- `logs/automated_stage_gates/stage28_ruler_attention_bridge/task_summary.csv`
- `logs/automated_stage_gates/stage28_ruler_attention_bridge/weak_runs.json`

The Stage 29 period-pair task-audit artifacts are:

- `logs/automated_stage_gates/stage29_period_pair_task_audit/manifest.json`
- `logs/automated_stage_gates/stage29_period_pair_task_audit/results.json`
- `logs/automated_stage_gates/stage29_period_pair_task_audit/local_summary.csv`
- `logs/automated_stage_gates/stage29_period_pair_task_audit/long_summary.csv`
- `logs/automated_stage_gates/stage29_period_pair_task_audit/task_summary.csv`
- `logs/automated_stage_gates/stage29_period_pair_task_audit/length_summary.csv`

The Stage 30 matched retrieval-bridge artifacts are:

- `logs/automated_stage_gates/stage30_matched_retrieval_bridge/manifest.json`
- `logs/automated_stage_gates/stage30_matched_retrieval_bridge/results.json`
- `logs/automated_stage_gates/stage30_matched_retrieval_bridge/summary.csv`
- `logs/automated_stage_gates/stage30_matched_retrieval_bridge/per_run_results.csv`
- `logs/automated_stage_gates/stage30_matched_retrieval_bridge/task_summary.csv`
- `logs/automated_stage_gates/stage30_matched_retrieval_bridge/weak_runs.json`

The Stage 31 full-context retrieval-attention artifacts are:

- `logs/automated_stage_gates/stage31_full_context_retrieval_attention/manifest.json`
- `logs/automated_stage_gates/stage31_full_context_retrieval_attention/results.json`
- `logs/automated_stage_gates/stage31_full_context_retrieval_attention/summary.csv`
- `logs/automated_stage_gates/stage31_full_context_retrieval_attention/per_run_results.csv`
- `logs/automated_stage_gates/stage31_full_context_retrieval_attention/task_summary.csv`
- `logs/automated_stage_gates/stage31_full_context_retrieval_attention/weak_runs.json`

The Stage 32 full-context feature-bridge artifacts are:

- `logs/automated_stage_gates/stage32_full_context_feature_bridge/manifest.json`
- `logs/automated_stage_gates/stage32_full_context_feature_bridge/results.json`
- `logs/automated_stage_gates/stage32_full_context_feature_bridge/summary.csv`
- `logs/automated_stage_gates/stage32_full_context_feature_bridge/per_run_results.csv`
- `logs/automated_stage_gates/stage32_full_context_feature_bridge/task_summary.csv`
- `logs/automated_stage_gates/stage32_full_context_feature_bridge/weak_runs.json`

Deferred IBM comparison rows are not promoted to machine-verifiable public evidence until their real packet, raw-count, job-ID, backend-metadata, and verifier-output files are present in the repository. For IonQ, any future evidence should be recorded as a new dated Amazon Braket/IonQ run when a Braket IonQ device is available, and then added as a new active sweep record.

## 8. Reproducibility Artifacts

The repository prioritizes evidence files over narrative-only claims. The minimum review path is:

- inspect `docs/research/q-rope-phase-wrap-qrope-algorithm-v1.md`;
- inspect `docs/research/q-rope-stage4-real-hardware-validation-result-v1.md`;
- inspect `docs/evidence/review-packets/qrope-automated-terminal-v1/qrope-terminal-human-review-packet-v1.md`;
- inspect `docs/publication/manuscript-to-provisional-support-audit-v1.md`;
- run or inspect `scripts/verify_stage4_hardware_packet.py`;
- run or inspect `scripts/verify_stage4_hardware_sweep.py`;
- run or inspect `scripts/estimate_stage4_classical_compute_cost.py`;
- run or inspect `scripts/preregister_stage4_replication_packets.py`;
- run or inspect `scripts/run_stage5_attention_baselines.py`;
- run or inspect `scripts/run_stage6_downstream_attention.py`;
- run or inspect `scripts/run_stage7_toy_transformer_ablation.py`;
- run or inspect `scripts/run_stage8_needle_benchmark.py`;
- run or inspect `scripts/run_stage9_trained_transformer_ablation.py`;
- run or inspect `scripts/run_stage10_small_decoder_transformer.py`;
- run or inspect `scripts/run_stage11_phasewrap_theory.py`;
- run or inspect `scripts/run_stage12_ruler_retrieval.py`;
- run or inspect `scripts/run_stage13_positional_adapter.py`;
- run or inspect `scripts/run_stage14_attention_readout.py`;
- run or inspect `scripts/run_stage15_learned_attention.py`;
- run or inspect `scripts/run_stage16_learned_attention_stability.py`;
- run or inspect `scripts/run_stage17_small_decoder_value_model.py`;
- run or inspect `scripts/run_stage18_value_output_capacity.py`;
- run or inspect `scripts/run_stage19_value_output_hardening.py`;
- run or inspect `scripts/run_stage20_hardened_positional_value_model.py`;
- run or inspect `scripts/run_stage21_hardened_positional_stability.py`;
- run or inspect `scripts/run_stage22_long_context_retrieval.py`;
- run or inspect `scripts/run_stage23_long_context_adapter.py`;
- run or inspect `scripts/run_stage24_long_context_value_model.py`;
- run or inspect `scripts/run_stage25_long_context_value_stability.py`;
- run or inspect `scripts/run_stage26_compact_kv_qa.py`;
- run or inspect `scripts/run_stage27_compact_kv_transformer_bridge.py`;
- run or inspect `scripts/run_stage28_ruler_attention_bridge.py`;
- run or inspect `scripts/run_stage29_period_pair_task_audit.py`;
- run or inspect `scripts/run_stage30_matched_retrieval_bridge.py`;
- run or inspect `scripts/run_stage31_full_context_retrieval_attention.py`;
- run or inspect `scripts/run_stage32_full_context_feature_bridge.py`;
- compare the verifier output with `logs/automated_stage_gates/stage4_hardware_packet/offline_verification.json`.
- inspect `logs/automated_stage_gates/stage4_hardware_sweep/manifest.json` and the sweep verifier output.

The intended reproducibility standard is not that every future backend execution match the present numbers. The standard is that the reported numbers are traceable to packet files, execution records, raw counts, and deterministic recomputation.

Repository naming note: public materials use `PhaseWrap-RoPE`; Python imports, script paths, packet IDs, and evidence IDs retain the existing `qrope` stem.

## 9. Limitations and Threats to Validity

The current evidence has several important limitations:

- The Stage 4 evidence is bounded to recorded packet/backend/date/calibration contexts.
- The product-state readout is not an entangling or quantum-advantage result.
- The CX readout is an entangling circuit variant, but it does not establish entanglement advantage.
- The Stage 5 synthetic target is exactly recoverable by simple exposed-feature baselines.
- Stage 6, Stage 7, Stage 8, Stage 9, Stage 10, Stage 12, Stage 13, Stage 14, Stage 15, Stage 16, Stage 17, Stage 18, Stage 19, Stage 20, Stage 21, Stage 22, Stage 23, Stage 24, Stage 25, Stage 26, Stage 27, Stage 28, Stage 29, Stage 30, Stage 31, and Stage 32 are toy downstream, retrieval, compact trained positional-attention, positional-adapter, attention-readout, learned attention-readout, stability, value-output capacity/hardening, compact QA, compact attention-bridge, period-pair audit, matched retrieval-bridge, full-context retrieval-attention, full-context feature-bridge, or very small transformer experiments, not production transformer evaluations.
- Stage 11 shows the fixed score is periodic and aliasing-limited; it is theory evidence for the score, not downstream model evidence.
- Stage 12 is intentionally non-phase-cued and is negative for the fixed 8/12 PhaseWrap score on exact-offset retrieval; this is evidence of a remaining mechanism gap, not evidence against the narrower score audit.
- The paper does not compare against production language-model baselines.
- The current hardware sweep is not a statistically broad backend survey.
- Provider result-key conventions can change the interpretation of recorded bitstrings, so manifest-declared decoding rules must be audited carefully.
- IonQ is not part of the active hardware evidence in this release because the current Amazon Braket path was unavailable or not run.
- The paper does not establish quantum advantage.

These limitations are not footnotes; they define the scientific scope of the release.

## 10. Discussion

The current evidence package is most valuable as a reproducibility-first method record. It shows that the PhaseWrap-RoPE score can be defined with a compact formula, frozen into small evidence packets, read out through two-qubit witness circuits, and recomputed offline from committed artifacts. This is a narrower but stronger posture than a broad performance claim: a reviewer can inspect the exact packet, backend, date, raw-count, and verifier path used for each reported result.

The Stage 4 hardware evidence is encouraging because the witness/control ordering is preserved across the active recorded IBM Fez and Amazon Braket artifacts under the manifest-declared verifier. The result remains context-specific. Backend calibration windows, provider result-key conventions, transpilation choices, shot budgets, queue conditions, and packet composition can all change future outcomes. The paper therefore treats the hardware runs as bounded validation records rather than as evidence of general cross-backend robustness.

The Stage 4 classical recomputation cost estimate makes the hardware witness interpretation more concrete. Across the six active hardware records, the committed artifacts contain `163072` recorded hardware shots, while local recomputation of the saved raw-count metrics is estimated at `4096` static arithmetic-scale operations with zero incremental local verifier cost. This is a reproducibility-cost statement only; it does not reconstruct provider billing, predict queue time, or support a quantum advantage or disadvantage claim.

The preregistered Stage 4 replication packets add a process guardrail for future hardware work. They freeze four future row sets before execution: IBM-style product-state and CX lanes with seed `314`, 16 rows, and 4096 shots, plus Amazon Braket-style product-state and CX lanes with seed `2718`, 8 rows, and 1000 shots. These packet files are not hardware evidence; they only make future reruns harder to tune after observing provider behavior.

The bitstring calibration packet specs add a second process guardrail. They predeclare known-state `|00>`, `|01>`, `|10>`, and `|11>` checks for IBM-style `q1q0` and Amazon Braket-style `q0q1` conventions. The current verifier output is intentionally `missing-evidence`; real calibration counts are still required before any broader provider-level decoding claim is made.

The Stage 5 through Stage 42 classical experiments clarify the downstream interpretation. Stage 5 showed that the original synthetic attention-scoring target is exactly recoverable by simple exposed-feature baselines, which prevents overreading that result. Stage 6 made the target less tautological by mixing content and positional signal, but it remains an oracle phase-feature sanity check because the PhaseWrap model sees the normalized phase label directly. Stage 7 then moved one step closer to a transformer-like setting by swapping the PhaseWrap positional term into a four-layer attention-only toy stack, where it had the best argmax retrieval ranking on a synthetic length-extrapolation packet while calibration remained mixed. Stage 8 added a local Needle-style retrieval packet with multiple seeds, bootstrap intervals, and a period-pair ablation. Stage 9 adds a trained decoder-style positional attention ablation where `phasewrap_adapter` is strongest on the phase-cued train-short/test-long packet, while `rope_relative` is strongest on the exact-offset passkey packet. Stage 10 adds a first full small-transformer sanity check and is near chance across the tested lanes. Stage 12 then tests local passkey, multi-needle, and aggregation-style retrieval without PhaseWrap-selected targets; RoPE-like and sinusoidal baselines solve the packet, while the fixed 8/12 PhaseWrap score does not. Stage 13 shows that PhaseWrap residual features plus explicit distance can recover argmax ranking on that local packet, but RoPE remains better calibrated by target-probability mass. Stage 14 preserves that pattern after converting targets into key-value attention readout. Stage 15 adds a learned attention scorer and gives the strongest local ranking result so far for PhaseWrap-plus-distance, while RoPE remains better on probability mass. Stage 16 shows that this ranking result is stable across the tested learned-scorer initialization seeds. Stage 17 shows that adding learned value embeddings and an output projection makes all methods near chance in the current compact setup. Stage 18 then teacher-forces target attention and still finds weak value-output performance under the compact optimizer. Stage 19 changes optimizer and capacity, fits train, and improves held-out value-token retrieval under teacher-forced attention. Stage 20 reintroduces learned positional attention and finds that RoPE-like scoring is strongest on the held-out packet. Stage 21 shows the Stage 20 ordering is stable across five initialization seeds. Stage 22 extends explicit retrieval through 4096-token contexts and is strongly negative for the fixed 8/12 score. Stage 23 then trains adapters on those long-context rows and recovers PhaseWrap-plus-distance argmax ranking, while RoPE remains stronger by target probability mass. Stage 24 adds learned value embeddings and output projection to the long-context rows; RoPE-like scoring is strongest on held-out value retrieval and the PhaseWrap-derived adapters trail. Stage 25 confirms that Stage 24 ordering across five initialization seeds. Stage 26 adds an explicit content-key QA retrieval packet where PhaseWrap-derived adapters match ALiBI-style top-1/MRR, while fixed PhaseWrap scoring remains weak. Stage 27 trains a compact attention bridge on those rows and preserves the PhaseWrap-plus-distance/ALiBI top-1 and MRR tie across five model initialization seeds, with PhaseWrap-plus-distance slightly ahead on target probability. Stage 28 trains a compact attention bridge directly on non-phase-cued RULER-style retrieval rows; PhaseWrap-plus-distance matches RoPE-like top-1/MRR, while RoPE-like scoring keeps stronger probability and calibration metrics. Stage 29 shows that period-pair swaps alone do not solve the fixed-score retrieval gap on local or long-context retrieval rows. Stage 30 then equalizes the Stage 28 bridge feature width and learned parameter count; PhaseWrap-plus-distance still matches RoPE-like top-1/MRR, while RoPE-like scoring remains stronger on target probability and calibration. Stage 31 makes every prefix position compete and is negative for the current PhaseWrap variants. Stage 32 adds a nonlinear full-context bridge and recovers PhaseWrap argmax retrieval, while RoPE-like scoring remains stronger on probability and calibration. Stage 33 then applies validation-selected post-hoc temperature scaling to the Stage 32 bridge: PhaseWrap-derived adapters keep perfect argmax retrieval and improve probability/ECE, but RoPE-like scoring still has the strongest calibrated target probability and ECE. Stage 34 moves the richer retrieval signal into a compact decoder-style value bridge with learned value embeddings and output projection; `rope_relative` is strongest, and the current PhaseWrap-derived adapters trail under this value-output bottleneck. Stage 35 teacher-forces target attention on the same value-output path and reaches only about `0.50-0.53` top-1, so value output is partly viable but not solved. Stage 36 then replaces the learned value-token classifier with copy-style value output; PhaseWrap distance and multiscale adapters recover perfect top-1/MRR, while RoPE-like scoring keeps higher target probability mass. Stage 37 applies validation-selected temperature calibration to that copy-value bridge; PhaseWrap-derived target probability improves sharply, but RoPE-like scoring remains strongest on calibrated probability/ECE. Stage 38 hardens the learned decoder-style value bridge; all methods fit train, but held-out length generalization still favors RoPE-like scoring. Stage 39 makes every prefix token compete in a compact sequence decoder and shows severe held-out length failure for every tested positional method. Stage 40 adds a broader train-length curriculum; it does not repair held-out `1024`/`2048` generalization, though PhaseWrap-derived adapters lead the weak `2048` test rows. Stage 41 then replaces learned value-token output with a pointer/copy head and repairs `2048` ranking for `rope_relative` and `phasewrap_multiscale_adapter`, while `rope_relative` remains strongest on target probability and calibration. Stage 42 makes that copy-aware output trainable with a pointer-generator mixture; strong ranking mostly survives, but RoPE-like scoring remains best and the learned generator branch contributes little target mass. These experiments support continued RoPE-facing downstream study, but they also make the current replacement gap explicit.

Stage 11 adds theory evidence for the score itself. It shows that the 8/12 rule is exactly periodic over mod 24, has only 10 distinct residue scores because of mirrored and zero-margin aliases, and is exactly expressible as a small classical Fourier feature map. This helps explain why the score can be compact and auditable while still requiring stronger mechanisms or auxiliary information for long-context transformer use.

The CX witness should also be read pragmatically. It was selected because it is the smallest entangling extension of the product-state witness: preserve the two `RY` margin encodings, add one `CX(q0 -> q1)`, and read a target-qubit parity/product signal while retaining the same packet discipline. It is useful for checking whether the phase-wrap cross-band signal survives an entangling readout path, not for claiming entanglement advantage.

## 11. Recommended Next Experiments

The next scientific step is not broader rhetoric about the current hardware records. It is controlled expansion with new evidence:

| Priority | Work item | Evidence required before promotion |
| --- | --- | --- |
| 1 | Stronger Stage 10 trained transformer ablation | Extend the current very small autograd-backed transformer to a stronger small decoder-only implementation and harder tasks. Compare RoPE, ALiBI, sinusoidal, no-position, and PhaseWrap positional variants under matched parameter counts, optimizer settings, training tokens, seeds, and hyperparameter budget. |
| 2 | Stronger standard retrieval tasks | Stage 26 adds an explicit content-key QA retrieval packet, Stage 27 trains a compact attention bridge on that packet, Stage 28 trains a compact attention bridge on non-phase-cued RULER-style retrieval rows, Stage 29 shows period-pair swaps alone do not solve the fixed-score retrieval gap, Stage 30 equalizes the compact bridge feature/parameter budget, Stage 31 shows the current simple PhaseWrap variants fail a harder full-prefix retrieval-attention stress test, Stage 32 shows a richer feature bridge can recover argmax retrieval, Stage 33 shows post-hoc calibration improves but does not erase the probability/ECE gap, Stage 34 shows the current adapters trail RoPE-like scoring once learned value-token output is required, Stage 35 shows teacher-forced value output is only partly solved, Stage 36 shows copy-style value output restores PhaseWrap top-1/MRR, Stage 37 shows scalar calibration sharply improves PhaseWrap-derived probability without closing the RoPE-like calibrated probability/ECE lead, Stage 38 shows hardened learned value-output training fits train but still generalizes best with RoPE-like scoring, Stage 39 shows the current all-prefix compact sequence decoder fails held-out length extrapolation for all tested positional methods, Stage 40 shows adding train length 512 does not repair that failure, Stage 41 shows pointer/copy output repairs sequence ranking, and Stage 42 shows learned copy/vocab mixing preserves much of that repair. Next, harden the trainable generator/copy gate or move the mechanism into a stronger decoder benchmark. |
| 3 | Comparable PhaseWrap mechanism | Stage 13 through Stage 42 now test adapters, period-pair alternatives, a matched feature-budget bridge, full-context retrieval attention, a nonlinear full-context feature bridge, post-hoc calibration, a compact learned value-output bridge, a teacher-forced value-output diagnostic, a copy-style value bridge, copy-value calibration, a hardened learned decoder value bridge, an all-prefix sequence decoder diagnostic, a sequence length-curriculum repair attempt, a pointer/copy sequence diagnostic, and a trainable pointer-generator. The behavior remains mixed: PhaseWrap ranking can recover under copy-aware output, but RoPE-like scoring remains stronger on probability/calibration and learned generator target mass remains weak. |
| 4 | Hardware witness hardening | Treat hardware as an auditable witness for a classical phase score. The sweep verifier now includes deterministic row-bootstrap and shot-resampling intervals from committed artifacts, Stage 4 includes a deterministic local classical recomputation cost estimate, future replication row sets are preregistered, and provider bitstring calibration specs/verifier contract are present. Remaining hardening requires real provider calibration execution plus independent reruns across dates and queue conditions. |
| 5 | Theory-to-task connection | Stage 11 now formalizes invariances, unavoidable aliases, period-pair tradeoffs, context-length behavior, and exact periodic-feature support. Next, connect those facts to task distributions and mechanism designs where the score should help or hurt. |
| 6 | Larger or error-aware witnesses | Explore larger witness families or mitigation analysis only when the packet generator, controls, costs, and verifier can preserve the current artifact discipline. |

The full promotion gate is maintained in `docs/research/q-rope-next-transformer-benchmark-roadmap-v1.md`. The key requirement is a real small decoder-only transformer ablation where the intended variable is the positional mechanism: RoPE, ALiBI, sinusoidal, no-position, and PhaseWrap variants should be trained under matched parameter counts, optimizer settings, training tokens, seeds, and hyperparameter budget. The benchmark should include train-short/test-long extrapolation, at least five seeds, failed-run artifacts, confidence intervals, and at least one task whose answer is not constructed from the PhaseWrap score.

The highest-impact research gap remains downstream relevance. The current release shows that the phase-wrap witness/control ordering is machine-verifiable in recorded small-circuit hardware contexts, that the Stage 5 synthetic attention-scoring label is recoverable by simple exposed-feature baselines, that Stage 6 is a useful oracle phase-feature sanity check, that Stage 7 improves argmax retrieval ranking in a four-layer toy length-extrapolation ablation, that Stage 8 wins a local phase-cued packet with a release-local period-pair ablation, and that Stage 9 produces a first trained positional-attention result with a mixed outcome across task lanes. Stage 10 adds a first full small-transformer sanity check, including a tiny text-fact QA lane, but its near-chance result means a stronger small decoder-only transformer ablation on harder tasks remains the next milestone for any stronger RoPE-replacement claim. Stage 11 clarifies that the fixed score is a mod-24 periodic feature with aliases, Stage 12 confirms that exact-offset retrieval can favor RoPE-like or sinusoidal positional behavior over the fixed score, Stages 13-16 identify PhaseWrap-plus-distance as a candidate adapter shape, Stages 17-19 harden the learned value-output path, Stages 20-21 show that the current hardened positional comparison still favors RoPE-like scoring on non-phase-cued held-out rows, Stage 22 shows the fixed score remains weak on longer explicit retrieval contexts, Stage 23 shows the trained PhaseWrap-plus-distance adapter can recover argmax retrieval but not the RoPE probability-mass advantage, Stage 24 shows the current learned long-context value-output path favors RoPE-like scoring, Stage 25 confirms that ordering across the tested initialization seeds, Stage 26 gives a constructive compact content-key QA result for PhaseWrap-derived adapters, Stage 27 preserves that result in a compact attention bridge across five model initialization seeds, Stage 28 adds a compact non-phase-cued RULER-style attention bridge where PhaseWrap-plus-distance matches RoPE-like top-1/MRR but not target probability, Stage 29 shows changing fixed period pairs does not by itself close the retrieval gap, Stage 30 removes the unequal-feature-width confound from the compact bridge while preserving the same probability/calibration caveat, Stage 31 shows that the current PhaseWrap variants do not survive a stricter full-prefix retrieval-attention stress test, Stage 32 shows a richer PhaseWrap feature bridge can recover full-prefix argmax retrieval while still trailing RoPE-like probability/calibration, and Stage 33 shows scalar temperature calibration improves the bridge but does not remove the RoPE-like probability/ECE lead.

Stages 34-42 extend that diagnosis into decoder-style value output and all-prefix sequence retrieval. The current learned value-output paths favor RoPE-like scoring, the unassisted all-prefix sequence decoder fails length extrapolation for every tested positional method, Stage 41 repairs ranking with deterministic copy output, and Stage 42 preserves much of that repair with a trainable pointer-generator while keeping a RoPE-like probability/calibration lead. The next downstream milestone is generator/copy-gate hardening or a stronger matched decoder-only transformer, not a broader claim based on the copy diagnostics alone.

Broader hardware expansion is useful but secondary to the transformer ablation. The hardware track should be framed as an auditable hardware witness for a classical phase score, not as quantum-enhanced attention. IonQ should be added only through a dated Amazon Braket/IonQ record when a device is available. Quandela, AQT, or larger-qubit witnesses should be added only when credentials, provider cost, and artifact capture support the same manifest/verifier discipline as Stage 4.

For presentation clarity, public materials should keep three concepts separate:

- the mathematical score: a classical modular phase feature;
- the transformer hypothesis: unproven until trained-model ablations show value under matched controls;
- the hardware witness: a small-circuit readout audit, not evidence of model advantage.

## 12. Conclusion

PhaseWrap-RoPE provides a compact phase-wrap positional scoring rule and a reproducibility-first evidence path for auditing that rule through deterministic packets, classical baselines, bounded small-circuit hardware readouts, local retrieval benchmarks, compact trained positional-attention ablations, and a deterministic score-theory analysis. The current evidence supports a narrow method-and-artifact claim: the score is well specified, the packet machinery is auditable, selected hardware records preserve the witness/control ordering, the 8/12 score's periodic structure is explicit, and mixed downstream evidence identifies both phase-cued promise and exact-offset limitations.

The current evidence does not support production transformer superiority, general cross-backend robustness, or quantum advantage. The next scientific step is controlled expansion: multi-seed downstream tasks, less phase-aligned targets, confidence intervals, and independently replicated hardware records.

## 13. Legal and Repository Notice

PhaseWrap-RoPE is associated with a USPTO provisional submission received `2026-05-18`. The Electronic Acknowledgement Receipt lists application `64/068,121` and Patent Center number `76347440`; final Filing Receipt review is pending, and the bounded hardware comparison status is documented separately in `docs/research/q-rope-stage4-hardware-comparison-v1.md`.

USPTO MPEP 503 currently lists provisional application series codes as `60/` through `63/` [6]. Because the acknowledgement receipt lists `64/068,121`, public materials should describe that number as the acknowledgement-receipt application number until the final Filing Receipt is received and checked.

The repository software is released under `AGPL-3.0-only`. The patent/IP-status notice does not convert the repository into a broad patent grant beyond the applicable open-source license and contributor grants for covered software. Commercial patent licensing, non-AGPL use, assignments, and sublicensing should be handled separately with Quantyra/CYINT IP.

## Repository evidence references

- `src/qrope/automated_stage_gates.py`
- `scripts/verify_stage4_hardware_packet.py`
- `scripts/verify_stage4_hardware_sweep.py`
- `scripts/run_stage5_attention_baselines.py`
- `scripts/run_stage6_downstream_attention.py`
- `scripts/run_stage7_toy_transformer_ablation.py`
- `scripts/run_stage8_needle_benchmark.py`
- `scripts/run_stage9_trained_transformer_ablation.py`
- `scripts/run_stage10_small_decoder_transformer.py`
- `scripts/run_stage33_temperature_calibration.py`
- `scripts/run_stage34_small_decoder_value_bridge.py`
- `scripts/run_stage35_value_bridge_bottleneck_diagnostic.py`
- `scripts/run_stage36_copy_value_bridge.py`
- `scripts/run_stage37_copy_value_temperature_calibration.py`
- `scripts/run_stage38_hardened_decoder_value_bridge.py`
- `scripts/run_stage39_sequence_decoder_retrieval.py`
- `scripts/run_stage40_sequence_length_curriculum.py`
- `scripts/run_stage41_pointer_copy_sequence.py`
- `scripts/run_stage42_trainable_pointer_generator_sequence.py`
- `logs/automated_stage_gates/stage4_hardware_packet/frozen_packet.json`
- `logs/automated_stage_gates/stage4_hardware_packet/execution.json`
- `logs/automated_stage_gates/stage4_hardware_packet/evaluation.json`
- `logs/automated_stage_gates/stage4_hardware_packet/offline_verification.json`
- `logs/automated_stage_gates/stage4_hardware_sweep/manifest.json`
- `logs/automated_stage_gates/stage5_attention_baselines/manifest.json`
- `logs/automated_stage_gates/stage6_downstream_attention/manifest.json`
- `logs/automated_stage_gates/stage7_toy_transformer_ablation/manifest.json`
- `logs/automated_stage_gates/stage8_needle_benchmark/manifest.json`
- `logs/automated_stage_gates/stage9_trained_transformer_ablation/manifest.json`
- `logs/automated_stage_gates/stage10_small_decoder_transformer/manifest.json`
- `logs/automated_stage_gates/stage33_temperature_calibration/manifest.json`
- `logs/automated_stage_gates/stage34_small_decoder_value_bridge/manifest.json`
- `logs/automated_stage_gates/stage35_value_bridge_bottleneck_diagnostic/manifest.json`
- `logs/automated_stage_gates/stage36_copy_value_bridge/manifest.json`
- `logs/automated_stage_gates/stage37_copy_value_temperature_calibration/manifest.json`
- `logs/automated_stage_gates/stage38_hardened_decoder_value_bridge/manifest.json`
- `logs/automated_stage_gates/stage39_sequence_decoder_retrieval/manifest.json`
- `logs/automated_stage_gates/stage40_sequence_length_curriculum/manifest.json`
- `logs/automated_stage_gates/stage41_pointer_copy_sequence/manifest.json`
- `logs/automated_stage_gates/stage42_trainable_pointer_generator_sequence/manifest.json`
- `docs/research/q-rope-phase-wrap-qrope-algorithm-v1.md`
- `docs/research/q-rope-stage4-real-hardware-validation-result-v1.md`
- `docs/research/q-rope-stage4-hardware-comparison-v1.md`
- `docs/research/q-rope-stage7-toy-transformer-ablation-v1.md`
- `docs/research/q-rope-stage8-needle-benchmark-v1.md`
- `docs/research/q-rope-stage9-trained-transformer-ablation-plan-v1.md`
- `docs/research/q-rope-stage33-temperature-calibration-v1.md`
- `docs/research/q-rope-stage34-small-decoder-value-bridge-v1.md`
- `docs/research/q-rope-stage35-value-bridge-bottleneck-diagnostic-v1.md`
- `docs/research/q-rope-stage36-copy-value-bridge-v1.md`
- `docs/research/q-rope-stage37-copy-value-temperature-calibration-v1.md`
- `docs/research/q-rope-stage38-hardened-decoder-value-bridge-v1.md`
- `docs/research/q-rope-stage39-sequence-decoder-retrieval-v1.md`
- `docs/research/q-rope-stage40-sequence-length-curriculum-v1.md`
- `docs/research/q-rope-stage41-pointer-copy-sequence-v1.md`
- `docs/research/q-rope-stage42-trainable-pointer-generator-sequence-v1.md`
- `docs/evidence/review-packets/qrope-automated-terminal-v1/qrope-terminal-human-review-packet-v1.md`
- `docs/publication/manuscript-to-provisional-support-audit-v1.md`
- `docs/publication/figures/qrope-method-schematic-v1.svg`
- `docs/publication/figures/qrope-validation-pipeline-v1.svg`
- `docs/publication/figures/qrope-stage4-comparison-v1.svg`
- `PATENTS.md`
- `README.md`

## References

[1] Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Lukasz Kaiser, and Illia Polosukhin. "Attention Is All You Need." arXiv:1706.03762, 2017. https://arxiv.org/abs/1706.03762

[2] Jianlin Su, Yu Lu, Shengfeng Pan, Ahmed Murtadha, Bo Wen, and Yunfeng Liu. "RoFormer: Enhanced Transformer with Rotary Position Embedding." arXiv:2104.09864, 2021. https://arxiv.org/abs/2104.09864

[3] IBM Quantum Documentation. "Introduction to primitives." Accessed 2026-05-18. https://quantum.cloud.ibm.com/docs/en/guides/qiskit-runtime-primitives

[4] IBM Quantum Documentation. "SamplerV2." Accessed 2026-05-18. https://quantum.cloud.ibm.com/docs/en/api/qiskit-ibm-runtime/0.25/sampler-v2

[5] IBM Quantum Documentation. "View backend details." Accessed 2026-05-18. https://quantum.cloud.ibm.com/docs/en/guides/qpu-information

[6] USPTO Manual of Patent Examining Procedure. "503 Application Number and Filing Receipt." Accessed 2026-05-18. https://www.uspto.gov/web/offices/pac/mpep/s503.html
