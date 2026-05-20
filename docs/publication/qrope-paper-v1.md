# PhaseWrap-RoPE: A Bounded Phase-Wrap Positional Scoring Rule with Reproducible Two-Qubit Hardware Readout

Manuscript status: `repository-paper-v2-draft`

Public claim posture: `bounded, reproducible, evidence-disciplined`

Archive DOI: `10.5281/zenodo.20306787`

USPTO record note: the repository reports an Electronic Acknowledgement Receipt dated `2026-05-18` listing application `64/068,121` and Patent Center number `76347440`. Public materials should continue to describe this as an acknowledgement-receipt record until the final Filing Receipt is received and checked.

License context: repository software released under `AGPL-3.0-only`.

## Abstract

PhaseWrap-RoPE is a bounded positional-scoring method based on wrapped phase residuals. Given two integer relative offsets, the method computes residuals in two fixed modular bases, converts those residuals into signed cosine margins, and combines the margins through a cross-band product score denoted `SQR` in the repository artifacts. This paper describes the scoring rule, the deterministic packet protocol used to audit it, and small two-qubit hardware readouts that recompute the frozen score from raw measurement counts.

The contribution is not a claim of quantum advantage, production transformer improvement, or general cross-backend robustness. Instead, the paper contributes a reproducibility-first evidence lane: frozen packets, fixed shot counts, raw counts, backend metadata, offline recomputation, explicit verifier scripts, and conservative claim boundaries. The current evidence includes a canonical IBM Fez product-state packet, a completed IBM Fez CX packet, Amazon Braket/Rigetti product-state replication evidence, provider-aware Amazon Braket CX recomputations, and classical downstream baselines that identify both the strengths and the limits of the synthetic tasks.

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
4. Classical and toy downstream baselines. The repository reports that the original synthetic scoring target is exactly recoverable by simple exposed-feature baselines, then separates that limitation from later toy downstream attention experiments.

The main scientific value is therefore the evidence discipline and the clarity of the scoring rule. The main scientific limitation is that the strongest claims remain packet-specific and toy-task-specific.

## 2. Claim Boundary and Evidence Tiers

PhaseWrap-RoPE is related to RoPE-style phase behavior, but the present release does not test a full transformer-scale architecture. Its evidence should be interpreted by tier:

| Tier | Evidence class | Supported interpretation | Unsupported interpretation |
| --- | --- | --- | --- |
| Formula | Closed scoring rule over integer offsets | `SQR = m8 * m12` is well specified and reproducible | Learned positional representation or broad model improvement |
| Stage 4 hardware | Two-qubit product-state and CX readout packets | Recorded hardware can preserve the frozen score/control ordering under specific packet/backend/date/calibration contexts | Quantum advantage, entanglement advantage, or general backend robustness |
| Stage 5 baselines | Synthetic attention-scoring baseline closure | The original synthetic target is recoverable by mod-24 and direct product-feature baselines | Evidence that the scoring task is nontrivial or production-relevant |
| Stage 6 downstream toy task | Content-plus-position toy attention benchmark | PhaseWrap-RoPE improves score calibration on one fixed non-tautological toy packet | Production transformer superiority |
| Stage 7 toy transformer ablation | Four-layer attention-only synthetic length-extrapolation packet | PhaseWrap-RoPE is worth testing in broader transformer-adjacent settings | Full transformer-scale validation |

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

Stage 6 mixes token/content compatibility with phase-wrap positional signal. The resulting target is not exactly recovered by mod-24 lookup or direct `m8`/`m12`/`m8*m12` features alone. On the fixed packet, `phasewrap_rope_attention` has the lowest MAE against RoPE, ALiBI, sinusoidal, no-position, mod-24 lookup, and classical phase-feature baselines. This is bounded toy downstream evidence only.

The repository also includes a deterministic Stage 7 toy transformer ablation:

```bash
python scripts/run_stage7_toy_transformer_ablation.py
```

Stage 7 tests a four-layer attention-only toy transformer ablation on one synthetic length-extrapolation retrieval packet. The reported result supports continued investigation in transformer-adjacent settings, but it remains a toy result. It does not establish production transformer superiority.

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

Deferred IBM comparison rows are not promoted to machine-verifiable public evidence until their real packet, raw-count, job-ID, backend-metadata, and verifier-output files are present in the repository. For IonQ, any future evidence should be recorded as a new dated Amazon Braket/IonQ run when a Braket IonQ device is available, and then added as a new active sweep record.

## 8. Reproducibility Artifacts

The repository prioritizes evidence files over narrative-only claims. The minimum review path is:

- inspect `docs/research/q-rope-phase-wrap-qrope-algorithm-v1.md`;
- inspect `docs/research/q-rope-stage4-real-hardware-validation-result-v1.md`;
- inspect `docs/evidence/review-packets/qrope-automated-terminal-v1/qrope-terminal-human-review-packet-v1.md`;
- inspect `docs/publication/manuscript-to-provisional-support-audit-v1.md`;
- run or inspect `scripts/verify_stage4_hardware_packet.py`;
- run or inspect `scripts/verify_stage4_hardware_sweep.py`;
- run or inspect `scripts/run_stage5_attention_baselines.py`;
- run or inspect `scripts/run_stage6_downstream_attention.py`;
- run or inspect `scripts/run_stage7_toy_transformer_ablation.py`;
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
- Stage 6 and Stage 7 are toy downstream experiments, not production transformer evaluations.
- The paper does not compare against production language-model baselines.
- The current hardware sweep is not a statistically broad backend survey.
- Provider result-key conventions can change the interpretation of recorded bitstrings, so manifest-declared decoding rules must be audited carefully.
- IonQ is not part of the active hardware evidence in this release because the current Amazon Braket path was unavailable or not run.
- The paper does not establish quantum advantage.

These limitations are not footnotes; they define the scientific scope of the release.

## 10. Discussion

The current evidence package is most valuable as a reproducibility-first method record. It shows that the PhaseWrap-RoPE score can be defined with a compact formula, frozen into small evidence packets, read out through two-qubit witness circuits, and recomputed offline from committed artifacts. This is a narrower but stronger posture than a broad performance claim: a reviewer can inspect the exact packet, backend, date, raw-count, and verifier path used for each reported result.

The Stage 4 hardware evidence is encouraging because the witness/control ordering is preserved across the active recorded IBM Fez and Amazon Braket artifacts under the manifest-declared verifier. The result remains context-specific. Backend calibration windows, provider result-key conventions, transpilation choices, shot budgets, queue conditions, and packet composition can all change future outcomes. The paper therefore treats the hardware runs as bounded validation records rather than as evidence of general cross-backend robustness.

The Stage 5, Stage 6, and Stage 7 classical experiments clarify the downstream interpretation. Stage 5 showed that the original synthetic attention-scoring target is exactly recoverable by simple exposed-feature baselines, which prevents overreading that result. Stage 6 made the target less tautological by mixing content and positional signal, where PhaseWrap-RoPE gave the best score calibration on one fixed packet. Stage 7 then moved one step closer to a transformer-like setting by swapping the PhaseWrap positional term into a four-layer attention-only toy stack, where it improved target ranking on a synthetic length-extrapolation retrieval packet. These experiments support continued downstream study; they do not establish production transformer superiority or full transformer-scale validation.

The CX witness should also be read pragmatically. It was selected because it is the smallest entangling extension of the product-state witness: preserve the two `RY` margin encodings, add one `CX(q0 -> q1)`, and read a target-qubit parity/product signal while retaining the same packet discipline. It is useful for checking whether the phase-wrap cross-band signal survives an entangling readout path, not for claiming entanglement advantage.

## 11. Recommended Next Experiments

The next scientific step is not broader rhetoric about the current hardware records. It is controlled expansion with new evidence:

| Priority | Work item | Evidence required before promotion |
| --- | --- | --- |
| 1 | Multi-seed downstream benchmark suite | Repeat Stage 6 and Stage 7 style tasks across seeds, lengths, distractor regimes, and task variants; promote only if results remain stable against lookup, exposed-feature, RoPE, ALiBI, sinusoidal, and no-position baselines. |
| 2 | Less phase-aligned toy transformer tasks | Add retrieval and classification tasks where the target is not constructed directly from the mod-8/mod-12 relation, so the benchmark tests useful inductive bias rather than formula recovery. |
| 3 | Confidence intervals for existing hardware metrics | Add bootstrap or other interval estimates for witness/control MAE and rank correlations using the committed raw-count artifacts. |
| 4 | Independent hardware replication | Add new packet/date/backend records with raw counts, backend metadata, verifier output, and confidence or bootstrap intervals for MAE/rank correlations. |
| 5 | Provider-aware verifier hardening | Preserve manifest-declared decoding, provider metadata, and blocked/unavailable-target records separately from completed evidence. |
| 6 | Larger or error-aware witnesses | Explore larger witness families or mitigation analysis only when the packet generator, controls, costs, and verifier can preserve the current artifact discipline. |
| 7 | DOI/preprint release packaging | Publish a tagged archive with DOI metadata and unchanged bounded claim language before further experiments alter the repository state. |

The highest-impact research gap is downstream relevance. The current release shows that the phase-wrap witness/control ordering is machine-verifiable in recorded small-circuit hardware contexts, that the Stage 5 synthetic attention-scoring label is recoverable by simple exposed-feature baselines, that Stage 6 improves score calibration on one non-tautological toy downstream packet, and that Stage 7 improves target ranking in a four-layer toy length-extrapolation ablation. Harder multi-seed downstream tasks are therefore the preferred next experiment.

Broader hardware expansion is useful but secondary. IonQ should be added only through a dated Amazon Braket/IonQ record when a device is available. Quandela, AQT, or larger-qubit witnesses should be added only when credentials, provider cost, and artifact capture support the same manifest/verifier discipline as Stage 4.

## 12. Conclusion

PhaseWrap-RoPE provides a compact phase-wrap positional scoring rule and a reproducibility-first evidence path for auditing that rule through deterministic packets, classical baselines, and bounded small-circuit hardware readouts. The current evidence supports a narrow method-and-artifact claim: the score is well specified, the packet machinery is auditable, selected hardware records preserve the witness/control ordering, and toy downstream results justify continued study.

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
- `logs/automated_stage_gates/stage4_hardware_packet/frozen_packet.json`
- `logs/automated_stage_gates/stage4_hardware_packet/execution.json`
- `logs/automated_stage_gates/stage4_hardware_packet/evaluation.json`
- `logs/automated_stage_gates/stage4_hardware_packet/offline_verification.json`
- `logs/automated_stage_gates/stage4_hardware_sweep/manifest.json`
- `logs/automated_stage_gates/stage5_attention_baselines/manifest.json`
- `logs/automated_stage_gates/stage6_downstream_attention/manifest.json`
- `logs/automated_stage_gates/stage7_toy_transformer_ablation/manifest.json`
- `docs/research/q-rope-phase-wrap-qrope-algorithm-v1.md`
- `docs/research/q-rope-stage4-real-hardware-validation-result-v1.md`
- `docs/research/q-rope-stage4-hardware-comparison-v1.md`
- `docs/research/q-rope-stage7-toy-transformer-ablation-v1.md`
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
