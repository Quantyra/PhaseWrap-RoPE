# PhaseWrap Research Program Decision v1

Status: `PROGRAM_DECISION_NEGATIVE_RESULTS_FIRST`

Date: `2026-05-25`

## Decision

The best course of action is to stop treating PhaseWrap as an active positive RoPE-replacement or quantum-advantage research program and publish the current body of work as a negative-results and methodology package.

The essential deliverable is one focused methodology paper:

`On the Difficulty of Isolating Positional Contributions in Retrieval Benchmarks`

That paper should carry the Stage 67-96 arc and use the fixed PhaseWrap score as the worked example. Stage 11 score theory should be an appendix unless it cleanly separates into a short note. Evidence-hygiene material should be an optional follow-on only after the methodology paper is stable.

## Why This Is the Best Course

The accumulated feedback and repo evidence agree on the same direction:

- The fixed `8/12` score is compact, classical, periodic, and heavily aliased.
- The original synthetic task was recoverable by trivial classical baselines, so it cannot support a strong model claim.
- Later retrieval stages repeatedly show that assistance pipelines can solve the task for `no_position` as well as for PhaseWrap-derived methods.
- Stage 219 supports ranking parity in selected bridge settings with probability/calibration degradation, not substitution adequacy.
- Stage 216-218 hardware evidence is real but bounded to two-qubit readout/noise-sensitivity auditing, not transformer relevance.
- The repo's strongest durable contribution is methodological: preserving failed gates, comparator controls, calibration checks, raw counts, claim cards, and evidence boundaries.

Publishing those facts directly is stronger than continuing to search for a positive PhaseWrap result.

## Feedback Assessment

| Feedback theme | Decision | Implementation posture |
| --- | --- | --- |
| Add stronger classical baselines | Accepted | Keep mod-24 lookup, direct product features, RoPE-like, sinusoidal, ALiBI-like, and `no_position` controls central in the paper. |
| Acknowledge the score is classical | Accepted | State that `SQR = m8 * m12` is CPU-computable and does not require quantum hardware. |
| Clarify hardware contribution | Accepted | Hardware is a bounded readout/audit lane. It is not speedup, entanglement advantage, or transformer improvement. |
| Quantify calibration degradation | Accepted | Report probability, ECE, Brier-style or equivalent calibration metrics beside top-1/MRR wherever a ranking result is discussed. |
| Treat Stage 219 as substitution | Rejected | Stage 219 is a ranking-parity bridge with measured probability/calibration degradation. It is not a substitution pass. |
| Publish Stage 80/81 methodology warning | Accepted and broadened | Use the full Stage 67-96 arc, not only Stage 80/81, because multiple independent repairs show the same method-nonspecific confound. |
| Write three separate papers now | Rejected for effort/payoff | Write one essential methodology paper first. Score theory and evidence hygiene remain appendix or optional follow-on material. |
| Continue PhaseWrap-positive experiments | Rejected by default | No more stage proliferation for positive replacement claims unless a predeclared gate introduces a materially different missing question. |
| Expand hardware runs now | Deferred | Preserve hardware evidence as audit infrastructure. New hardware spending requires a preregistered matched-encoding protocol and an explicit reason it helps the negative-results publication. |
| Build a future quantum-attention experiment | Separate program | Swap-test attention, photonic kernels, or Hamiltonian/variational positional injection may be worthwhile, but they should not be framed as PhaseWrap continuation evidence. |
| Patent/IP prominence | Low-prominence mention only | Patent status is not part of the scientific claim and should not appear as a credibility signal. Receipt-specific identifiers and confirmation numbers stay out of public materials. |

## What Continues

- Prepare the essential retrieval-benchmark methodology paper around Stages 67-96.
- Use Stage 11 score theory to explain why the fixed score is auditable but structurally limited.
- Preserve Stage 216-218 and Stage 4 hardware artifacts as examples of evidence hygiene and bounded readout auditing.
- Keep `qrope.scoring`, verifier scripts, frozen packets, manifests, raw counts, calibration checks, claim cards, and failed-run records reproducible.
- Keep Stage 219 language limited to ranking parity with calibration degradation.
- Keep patent/IP posture as a factual, low-prominence legal mention only.

## What Stops

- Stop claiming or implying RoPE replacement.
- Stop treating hardware-positive readout records as transformer evidence.
- Stop adding small synthetic stages to chase a PhaseWrap-positive promotion.
- Stop publishing assistance-pipeline repairs as positional-method success unless `no_position` and method-nonspecific controls fail under the same repair.
- Stop foregrounding patent status in research materials.

## Reopen Gates

PhaseWrap-positive claims can be reopened only if a future artifact satisfies one of these predeclared gates:

- `Transformer gate`: a matched trained benchmark on a non-phase-cued task shows a PhaseWrap-derived method beating or matching strong baselines across rank, probability, and calibration metrics with confidence intervals and retained failed runs.
- `Hardware gate`: a preregistered matched-encoding hardware protocol shows a stable hardware-specific contribution beyond exact classical `m8*m12`, mod-24 lookup, product-state readout, and noisy-simulator controls.
- `New-method gate`: a successor method changes the core representation enough that it is no longer evidence for the fixed `8/12` PhaseWrap score and should be tracked as a separate research program.

Until one of those gates is met, the active public posture remains negative-results first.

The execution-freeze guardrail is [PhaseWrap execution freeze](phasewrap-execution-freeze-v1.md).

Execution audit: [PhaseWrap decision execution audit](phasewrap-decision-execution-audit-v1.md).

## Publication Plan

1. Freeze the public repository in negative-results framing.
2. Draft the methodology paper around the claim:

   `Assistance pipelines can repair retrieval tasks without isolating the positional mechanism under test.`

3. Include Stage 11 score theory as a compact appendix explaining the fixed score's period, aliasing, and Fourier support.
4. Include Stage 216-218 only as a bounded hardware-audit example, not as model-improvement evidence.
5. Run the publication verifier before release and keep receipt-specific identifiers and confirmation numbers out of public materials.
6. Release under a conservative tag such as `v0.3.0-negative-results` only after the paper/repo wording can be summarized without RoPE replacement, production transformer superiority, quantum advantage, broad cross-backend robustness, or PhaseWrap-specific support-routing success.

## Bottom Line

PhaseWrap should be published because the negative result is useful and unusually well-audited. It should not continue as a positive replacement research line in this repo. The next valuable work is writing the negative-results methodology paper cleanly, not running another batch of PhaseWrap-positive diagnostics.
