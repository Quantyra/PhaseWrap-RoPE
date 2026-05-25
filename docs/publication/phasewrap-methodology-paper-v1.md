# On the Difficulty of Isolating Positional Contributions in Retrieval Benchmarks

Status: `METHODOLOGY_PAPER_DRAFT_V1`

Date: `2026-05-25`

Repository: `PhaseWrap-RoPE`

## Abstract

This paper reports a negative result from the PhaseWrap research program: fixed-period phase-wrap positional scoring did not become a supported RoPE replacement under the audited retrieval gates in this repository. The useful contribution is methodological. Across a long sequence of controlled retrieval diagnostics, assistance mechanisms such as content-key redesigns, query-support recovery, support-routed selectors, structural copy experts, and auxiliary heads repeatedly repaired retrieval without isolating the positional mechanism under test. In several cases, the same repairs solved the benchmark for `no_position` controls.

The central conclusion is that retrieval benchmarks can overstate positional-encoding evidence when the repair path contains method-nonspecific support recovery, routing, copy, or auxiliary mechanisms. A positional-method claim should therefore require strong controls: `no_position`, sinusoidal, ALiBI-like, RoPE-like, direct classical periodic features, failed-run retention, confidence intervals, probability/calibration metrics, and explicit claim cards.

PhaseWrap remains useful here as a worked example because it is compact enough to audit completely. Stage 11 shows that the fixed `8/12` score has least common period `24`, only `10` distinct residue scores, mirror aliases, and exact Fourier support `[1, 2, 3, 5]`. This makes the score interpretable and reproducible, but also explains why it is structurally limited as a unique long-context address. Stage 216-218 hardware evidence is included only as a bounded two-qubit readout-audit example; it is not transformer evidence and does not reverse the negative retrieval conclusion.

## Claim

Assistance pipelines can repair retrieval tasks without isolating the positional mechanism under test.

This claim is supported by the Stage 67-96 arc. It is the essential publication target for the current repository.

## Non-Claims

This paper does not claim:

- PhaseWrap replaces RoPE.
- PhaseWrap improves production transformers.
- PhaseWrap proves quantum advantage.
- PhaseWrap has broad cross-backend hardware robustness.
- Support-routed recovery is PhaseWrap-specific.
- Two-qubit hardware readout is transformer-scale model evidence.
- Patent status is scientific evidence.

## Background

PhaseWrap maps relative-position comparisons into two wrapped residual margins, one at period `8` and one at period `12`, and multiplies the two margins into a scalar score:

```text
SQR = m8 * m12
```

The score is classical and exactly CPU-computable. The quantum hardware path in this repository is a readout/audit lane for frozen two-qubit packets, not a computational requirement.

Early positive-looking signals motivated increasingly strict tests. The later evidence shows that the original replacement framing should be closed. The program now has a stronger and more defensible output: an audited negative-results package showing where positional-method claims can be confounded by benchmark assistance mechanisms.

## Methods

The repository used staged audits rather than a single monolithic benchmark. Each stage wrote machine-readable artifacts under `logs/automated_stage_gates/`, and the public reviewer path preserves:

- stage documentation;
- raw metrics and summaries;
- failed-run records where applicable;
- no-position, sinusoidal, ALiBI-like, RoPE-like, and PhaseWrap-derived comparisons;
- claim boundaries and excluded claims;
- verifier scripts that recompute reported summaries from committed artifacts.

The methodology paper focuses on Stages 67-96 because that is where the strongest benchmark-design lesson appears. Earlier stages provide context, especially Stage 5, Stage 11, Stage 12, Stage 216-218, and Stage 219.

## Evidence Summary

| Stage | Question | Result | Methodology lesson |
| --- | --- | --- | --- |
| Stage 5 | Can direct classical baselines recover the original synthetic label? | `lookup_mod24` and `classical_m8_m12_product` recover the label exactly. | A benchmark generated from the exposed periodic feature cannot support a broad positional-encoding claim. |
| Stage 11 | What is the exact structure of the fixed score? | Least common period `24`, `10` distinct residue values, Fourier support `[1, 2, 3, 5]`. | The score is compact and auditable but heavily aliased. |
| Stage 12 | Does fixed PhaseWrap solve non-phase-cued retrieval? | RoPE-like and sinusoidal baselines solve; fixed PhaseWrap is weak. | Non-phase-cued retrieval prevents the original tautology from carrying the claim. |
| Stage 67 | Is visible content-key retrieval solvable by the harness? | All tested methods solve, including `no_position`. | The model path can retrieve, but content-key success is not positional-method evidence. |
| Stage 74/75 | Can query support be recovered from visible cues? | Support recovery repairs phase-cued retrieval for multiple methods, including `no_position`. | Support recovery can solve the row family without isolating the positional mechanism. |
| Stage 80 | Does hard support routing repair phase-cued retrieval? | Every tested method reaches phase-cued top-1 `1.000000`, including `no_position`. | The hard routing rule does the decisive work; the repair is method-nonspecific. |
| Stage 81 | Does soft support routing preserve the repair? | Every tested method again solves phase-cued retrieval, including `no_position`. | Softened support probabilities still route enough mass without proving positional specificity. |
| Stage 82 | Can a learned routing head replace the hard selector? | Support accuracy remains `1.000000`, but phase-cued top-1 drops to `0.333333`. | Recovering support is not the same as learning support-to-token binding. |
| Stage 93 | What is the toy decoder lane boundary? | Structural routes solve; free learned pointer-generators do not solve full original retrieval. | Structural solvability should not be mistaken for learned positional-method promotion. |
| Stage 94 | Is the promotion gate ready? | `PROMOTION_GATE_NOT_READY_STRONGEST_CLAIM_BOUNDED`. | The missing proof is a free learned PhaseWrap-led original retrieval solve. |
| Stage 96 | What is the claim card? | `CLAIM_CARD_BOUND_STRONGEST_HONEST_CLAIM`. | The public claim must preserve positives, failures, exclusions, intervals, and next gate together. |
| Stage 219 | Do adapters reach RoPE rank parity? | Top-1/MRR parity in bounded bridges, with probability/calibration degradation. | Ranking parity is not substitution adequacy. |

## Main Result

The Stage 67-96 arc shows that retrieval repair is not sufficient evidence for positional-method contribution.

The key pattern is repeated:

- Stage 67 shows the harness can solve visible content-key retrieval, but `no_position` solves too.
- Stage 74/75 show query-support recovery can repair phase-cued retrieval, but the repair is not PhaseWrap-specific.
- Stage 80/81 show hard and soft support-routed token selection can solve phase-cued retrieval for every tested method, including `no_position`.
- Stage 82 shows that when the decisive routing rule must be learned rather than supplied, support recovery alone is insufficient.
- Stage 93/94/96 package the boundary: the structural row family is solvable, but the free learned PhaseWrap-led promotion gate remains unmet.

The resulting methodology warning is direct: a benchmark that adds support routing, copy experts, auxiliary support heads, or content-key redesigns must include method-nonspecific controls before calling the repair positional-encoding evidence.

## Stage 219 Ranking-Parity Boundary

Stage 219 is included because it is the easiest place to overread the results.

The primary Stage 30 bridge reports:

| Metric | PhaseWrap-derived adapter vs RoPE |
| --- | ---: |
| top-1 degradation | `0.000000` |
| MRR degradation | `0.000000` |
| mean target-probability degradation | `0.179917` |
| expected-calibration-error degradation | `0.185967` |

The secondary Stage 32 bridge reports:

| Metric | PhaseWrap-derived adapter vs RoPE |
| --- | ---: |
| top-1 degradation | `0.000000` |
| MRR degradation | `0.000000` |
| mean target-probability degradation | `0.232716` |
| expected-calibration-error degradation | `0.238330` |

This supports ranking parity in bounded bridge settings, not substitution adequacy. Any paper, README, or release note that summarizes Stage 219 must put the probability and calibration degradation in the same sentence as the rank result.

## Appendix A: Score Theory

Stage 11 explains why PhaseWrap is a good audit object but a weak unique address.

For the default period pair `(8, 12)`:

- least common period is `24`;
- the score is invariant under joint translations of the two offsets;
- the score is invariant to shifting either offset by `24`;
- the score is symmetric under sign reversal of the offset difference;
- there are `10` distinct score values on the mod-24 residue table;
- Fourier support is exactly `[1, 2, 3, 5]`.

Alias growth is structural:

| Context length | Unique score count | Mean alias class size | Max alias class size |
| ---: | ---: | ---: | ---: |
| 24 | 10 | 2.400000 | 6 |
| 48 | 10 | 4.800000 | 12 |
| 96 | 10 | 9.600000 | 24 |
| 192 | 10 | 19.200000 | 48 |
| 384 | 10 | 38.400000 | 96 |
| 768 | 10 | 76.800000 | 192 |
| 1024 | 10 | 102.400000 | 257 |

This appendix should remain in the methodology paper unless a separate score-theory note becomes worth the extra writing overhead.

## Appendix B: Bounded Hardware-Audit Evidence

The hardware results are real but should remain secondary.

Stages 216-218 report `FULL_REPLACEMENT_HARDWARE_POSITIVE_PHASEWRAP_ADVANTAGE`: PhaseWrap has lower normalized noise-sensitivity delta than the best matched positional baseline and matched null control in all four full IBM Fez 4096-shot seed/template comparison groups, after Stage 217 validates `q1q0` known-state calibration.

| Source lane | Circuit template | PhaseWrap delta | Best positional delta | Matched null delta |
| --- | --- | ---: | ---: | ---: |
| `ibm_cx_seed314_rows16_shots4096` | CX parity | `0.056686` | `0.073770` | `0.079248` |
| `ibm_cx_seed577_rows16_shots4096` | CX parity | `0.058017` | `0.082664` | `0.072316` |
| `ibm_product_seed314_rows16_shots4096` | Product state | `0.027709` | `0.038480` | `0.039844` |
| `ibm_product_seed577_rows16_shots4096` | Product state | `0.037817` | `0.039628` | `0.042044` |

This is useful for evidence hygiene: frozen packets, raw counts, provider metadata, known-state calibration, and offline metric interpretation are preserved. It is not a transformer result, not RoPE replacement evidence, and not quantum advantage.

## Recommended Benchmark Rules

Future positional-encoding retrieval benchmarks should:

- include `no_position`, sinusoidal, ALiBI-like, RoPE-like, and direct classical periodic-feature controls;
- separate support recovery from support-to-token binding;
- report target probability and calibration metrics beside rank metrics;
- retain failed runs and confidence intervals;
- avoid target definitions that are exactly recoverable from the proposed feature;
- publish claim cards that pair each positive statement with exclusions and failure modes;
- treat structural copy/routing experts as upper bounds unless a free learned model internalizes the mechanism.

## Conclusion

The PhaseWrap replacement line should remain closed. The publishable result is not that fixed-period PhaseWrap beats RoPE. The publishable result is that the project documents, with reproducible artifacts, how assistance pipelines can make retrieval benchmarks look solved without proving that the tested positional mechanism is responsible.

The next useful work is paper preparation and repo hygiene, not another PhaseWrap-positive diagnostic stage.
