# PhaseWrap-RoPE Negative Results Publication Roadmap v1

Status: `NEGATIVE_RESULTS_PUBLICATION_TRACK`

Date: `2026-05-25`

Canonical program decision: [PhaseWrap research program decision](phasewrap-research-program-decision-v1.md).

Essential paper draft: [On the Difficulty of Isolating Positional Contributions in Retrieval Benchmarks](phasewrap-methodology-paper-v1.md).

## Decision

The PhaseWrap-RoPE replacement line is closed as a positive-result research program. The repository should be published as a negative-results and methodology package, not as a RoPE-replacement, transformer-improvement, or quantum-advantage claim.

The central publication value is that the project records where a compact fixed-period positional score fails, how assistance pipelines can mask positional-method specificity, and which reproducibility practices made those conclusions auditable.

## Publication Set

### 1. Essential Paper: Retrieval-Benchmark Methodology

Working title:

`On the Difficulty of Isolating Positional Contributions in Retrieval Benchmarks`

Primary evidence:

- Stage 67: visible content-key retrieval is solvable by all tested methods, including `no_position`.
- Stage 74/75: query-support recovery can solve support prediction without establishing positional-method specificity.
- Stage 80: hard support-routed token selection solves phase-cued retrieval for every tested method, including `no_position`.
- Stage 81: soft support-routed token selection preserves the same method-nonspecific repair.
- Stages 82-92: learned, nonlinear, in-decoder, dual-auxiliary, teacher-distilled, curriculum, and support-binding routes do not establish a free learned PhaseWrap-specific retrieval mechanism.
- Stage 94: the promotion gate remains failed because the free learned PhaseWrap-led original-retrieval solve is missing.
- Stage 95/96: confidence intervals and claim-card packaging preserve the bounded conclusion.

Main claim:

Assistance pipelines can repair retrieval tasks without isolating the positional mechanism under test. Benchmark designs that report recovery after adding support routing, copy experts, or auxiliary heads must include `no_position` and method-nonspecific controls before treating the repair as positional-encoding evidence.

Excluded claims:

- PhaseWrap-RoPE improves production transformers.
- PhaseWrap-RoPE replaces RoPE.
- Support-routed recovery is PhaseWrap-specific.

### 2. Optional Note: Evidence Hygiene for Small Quantum-ML Claims

Working title:

`Evidence Hygiene for Hardware-Validated Quantum-ML Microbenchmarks`

Primary evidence:

- Frozen packet manifests and offline verifiers.
- Provider-aware bitstring decoding.
- Known-state calibration validation.
- Raw-count preservation and post-hoc recomputation.
- Confidence intervals, failed promotion gates, and claim-card guardrails.
- Stage 216-218 full IBM Fez replacement interpretation.

Main claim:

The project provides a reusable audit pattern for small quantum-ML hardware claims: keep packet generation, raw counts, provider metadata, calibration checks, decoding rules, metric interpretation, failure gates, and claim boundaries separable and reproducible.

Excluded claims:

- Quantum speedup.
- Entanglement-based advantage.
- Broad cross-backend hardware robustness.
- Transformer-scale validation.

### 3. Appendix or Optional Short Note: Score Theory

Working title:

`Fourier Structure of Product Phase-Wrap Residuals at Coprime Moduli`

Primary evidence:

- Stage 11 score theory.
- The fixed `8/12` score has least common period `24`.
- The score has mirror aliases and only `10` distinct residue values.
- The mod-24 residue table has positive Fourier support `[1, 2, 3, 5]`.

Main claim:

The fixed PhaseWrap-RoPE score is a compact periodic feature with a small exact Fourier representation. This explains why it is easy to audit and why it is structurally limited as a unique long-context address.

Excluded claims:

- The `8/12` period pair is globally optimal.
- The score is a general substitute for high-dimensional transformer positional encodings.
- The score requires quantum hardware to compute.

## Execution Order

1. Prepare the retrieval-benchmark methodology paper first. This is the essential paper and should carry the full Stage 67-96 arc, not just Stage 80/81. Draft v1 is now `docs/publication/phasewrap-methodology-paper-v1.md`.
2. Add Stage 11 score theory as an appendix to the methodology paper unless a short standalone note is clearly worth the extra writing overhead.
3. Prepare the evidence-hygiene note only if the first paper is stable and the hardware-audit contribution can be presented without model-improvement leakage.

## Patent/IP Prominence

The patent posture should remain factual, low-prominence, and separate from the scientific contribution.

- The repo should include only a factual, low-prominence legal mention of the provisional filings.
- Do not use patent status as a credibility signal for the negative-results publication.
- Do not foreground patent notices in README, abstracts, release titles, or paper introductions.
- Keep receipt-specific identifiers out of public materials.
- Keep patent prosecution and conversion strategy outside this research repository.

## Repository Changes Before Public Release

- Update README and documentation landing pages to state that the positive replacement line is closed.
- Keep the bounded hardware result visible but secondary.
- Keep the standalone replacement paper withdrawn.
- Add a negative-results reviewer path with Stage 11, Stage 70, Stage 80, and Stage 81 as first-class commands.
- Keep patent/IP status factual and low-prominence.
- Keep receipt-specific identifiers out of public materials.
- Do not create a new public release until the negative-results framing passes the publication package verifier.

## Release Gate

Proceed with public release only if the package can be summarized without implying any of the following:

- RoPE replacement.
- production transformer superiority.
- quantum advantage.
- broad cross-backend robustness.
- PhaseWrap-specific success for method-nonspecific support-routing repairs.

The release is successful if a reviewer can reproduce the negative findings and understand why the line was closed without reading the frozen stage cascade end to end.
