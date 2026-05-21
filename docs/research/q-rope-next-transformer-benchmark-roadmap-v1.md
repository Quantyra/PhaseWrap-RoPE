# PhaseWrap-RoPE Next Transformer Benchmark Roadmap v1

Date: `2026-05-20`

Status: `planned`

## Purpose

This roadmap defines the evidence needed before PhaseWrap-RoPE can be presented as a credible RoPE-replacement candidate rather than an auditable phase-wrap scoring rule with bounded hardware witnesses and toy downstream checks.

North-star goal: find the strongest honest claim PhaseWrap-RoPE can support under fair RoPE, ALiBI, sinusoidal, and no-position comparisons, preserving both positive evidence and failure modes. The detailed active goal is recorded in `docs/research/q-rope-strongest-honest-claim-goal-v1.md`.

The current repository already separates three tracks:

- the mathematical score: a classical modular phase feature;
- the transformer hypothesis: unproven until matched trained-model ablations show value;
- the hardware witness: a small-circuit readout audit of the score, not evidence of model advantage.

This document makes the next promotion gate explicit.

## Minimum Next Milestone

The next high-impact experiment should be a real transformer ablation where the positional mechanism is the intended experimental variable.

Required comparison set:

| Variant | Requirement |
| --- | --- |
| `no_position` | Same architecture with no explicit positional mechanism. |
| `sinusoidal` | Fixed sinusoidal positional baseline. |
| `alibi` | ALiBI-style attention bias baseline. |
| `rope` | RoPE or RoPE-like rotary query/key baseline. |
| `phasewrap_bias` | PhaseWrap-derived positional attention bias. |
| `phasewrap_adapter` | Learned adapter around PhaseWrap positional features. |
| `phasewrap_rotation` | Optional query/key rotation analogue if implemented without giving oracle labels. |

Controls:

- matched parameter counts, with any extra PhaseWrap parameters explicitly reported;
- matched optimizer, scheduler, batch size, gradient clipping, training tokens, and hyperparameter budget;
- at least five initialization/data seeds;
- train-short/test-long context extrapolation;
- all failed, diverged, or underperforming runs retained in the artifact tree;
- confidence intervals over seeds for all headline metrics.

Metrics:

- loss or perplexity;
- retrieval top-1 accuracy;
- mean reciprocal rank;
- target probability or another calibration-sensitive score;
- expected calibration error or comparable calibration statistic;
- confidence intervals for each metric and method.

## Task Requirements

The benchmark must include at least one task where the answer is not constructed from the PhaseWrap score.

Preferred task lanes:

| Lane | Examples | Reason |
| --- | --- | --- |
| Standard retrieval | Needle-in-Haystack, passkey retrieval, multi-needle retrieval | Tests positional recall without using PhaseWrap as the label generator. |
| RULER-style retrieval | multi-hop retrieval, aggregation, variable tracking | Tests compositional long-context behavior. |
| Compact QA or language modeling | controlled text-fact QA, small natural-language corpus | Checks whether the mechanism survives a non-synthetic text setting. |
| Synthetic diagnostics | phase-cued retrieval, alias/adversarial rows | Preserves interpretability, but cannot be the sole success criterion. |

Stage 26 provides a useful compact content-key QA packet. Stage 27 adds a compact attention bridge over that packet with five deterministic model initialization seeds. Stage 28 adds a compact attention bridge directly over non-phase-cued RULER-style retrieval rows. Stage 30 reruns that bridge with matched feature width and learned parameter count across positional variants. Stage 31 moves from candidate-only ranking to learned full-prefix retrieval attention and is negative for the simple PhaseWrap variants. Stage 32 adds a nonlinear full-context feature bridge and recovers PhaseWrap argmax retrieval while RoPE-like scoring remains better on probability and calibration. Stage 33 applies validation-selected post-hoc temperature scaling to that bridge; the PhaseWrap-derived adapters keep perfect argmax retrieval and improve probability/ECE, but RoPE-like scoring remains strongest on calibrated probability/ECE. Stage 34 moves the richer retrieval signal into a compact decoder-style value bridge with learned value embeddings and output projection; RoPE-like scoring remains strongest. Stage 35 then teacher-forces target attention and shows the value-output path is partly viable but not solved. Stage 36 hardens value output with copy-style candidate-value readout and shows PhaseWrap-derived adapters recover top-1/MRR, while RoPE-like scoring keeps higher probability mass. Stage 37 applies validation-selected temperature calibration to that copy-value bridge; PhaseWrap-derived target probability improves sharply, but RoPE-like scoring remains strongest on calibrated probability/ECE. Stage 38 hardens the learned decoder-style value bridge and shows all methods fit train, but held-out length generalization still favors RoPE-like scoring. Stage 39 moves to all-prefix sequence decoder retrieval and shows the current compact sequence decoder collapses on held-out length for all tested positional methods. Stage 40 adds a broader length curriculum and still does not repair held-out `1024`/`2048` generalization. Stage 41 adds a pointer/copy sequence head and repairs held-out `2048` ranking for RoPE-like scoring and PhaseWrap multiscale, while RoPE-like scoring remains strongest on probability/calibration. Stage 42 makes that output path trainable with a pointer-generator mixture; strong ranking mostly survives, but RoPE-like scoring remains best and the learned generator branch remains weak. Stage 43 adds auxiliary generator-target loss; generator target probability improves substantially, but RoPE-like scoring remains strongest overall and generator-only top-1 remains below `0.50`. Stage 49 returns to the Stage 45-48 row family with a copy-decoder repair and shows exact-offset retrieval is repairable for RoPE-relative scoring, but PhaseWrap does not lead and phase-cued retrieval remains weak. Stage 50 makes that path learned with a pointer-generator decoder and shows the fixed-copy repair does not survive learned attention/gating. Stage 51 audits Stages 45-50 as a bounded decoder-path plateau. Stage 52 moves beyond that plateau with a two-block residual decoder feasibility audit; train fit and tiny text-fact QA improve, but retrieval generalization remains zero. Stage 53 hardens retrieval exposure/training for that two-block path and still fails retrieval. Stage 54 adds target-attention supervision and still fails to repair held-out retrieval attention or top-1. Stage 55 exposes row-metadata cue-copy features and solves the rows for every method, including `no_position`, so it proves row-family solvability without supporting positional-method promotion. Stage 56 restricts cue-copy to visible input tokens and recovers only exact-offset passkey partially; phase-cued retrieval remains weak. Stage 57 adds the known support prior and solves phase-cued retrieval for `no_position` too. Stage 58 learns that support map from pooled train rows, but remains a lookup/copy diagnostic and still solves for `no_position`. Stage 59 makes the support lookup seed-local; held-out support coverage is incomplete, fallback cue decoding crosses the loose threshold, and `no_position` solves too. Stage 60 removes fallback cue help for unseen residues and shows phase-cued retrieval falls below threshold under strict known-support decoding. Stage 61 gives the learned two-block decoder complete support coverage and still fails capacity. Stage 62 lengthens training and improves train fit but still misses capacity and retrieval generalization. Stage 63 replaces the vocab softmax with copy output and establishes train capacity, but held-out retrieval still remains far below threshold. Stage 64 uses a learned copy/vocab mixture and preserves train capacity, but held-out retrieval still remains below threshold. Stage 65 adds length-40 curriculum rows to that pointer-generator path; it preserves train capacity and improves tiny text-fact QA, but both retrieval lanes reach only `0.033333` best held-out top-1. Stage 66 adds a direct method-bias positional-copy expert; it preserves train capacity, but phase-cued retrieval reaches only `0.033333` and exact-offset passkey only `0.050000` best held-out top-1. Stage 67 redesigns rows around standard visible content-key retrieval and solves held-out retrieval for every method, including `no_position`. The next step is a stronger learned decoder redesign or original-row mechanism that improves phase-cued/exact-offset retrieval generalization, not another claim-broadening diagnostic, simple length curriculum, output-path expert, or content-key row redesign.

## PhaseWrap Mechanism Requirements

The PhaseWrap variant should be implemented as a positional mechanism comparable to RoPE or ALiBI, not as a scalar oracle feature.

Acceptable implementations include:

- positional attention bias derived from PhaseWrap residual features;
- learned adapter around PhaseWrap residual features;
- query/key rotation analogue tied to the phase-wrap feature map;
- hybrid mechanism that combines PhaseWrap features with explicit distance, if the extra features are also reported for baselines or treated as a separate adapter family.

Unacceptable promotion evidence:

- a target label directly algebraically generated from the same PhaseWrap feature exposed to the model;
- selecting the winning method from top-1 or MRR alone while hiding loss, probability mass, or calibration;
- reporting a phase-cued synthetic task as a standard retrieval or language-model benchmark.

## Hardware Track

The hardware track should remain framed as an auditable witness for a classical phase score.

Next hardware hardening items:

- execute the predeclared provider bit-order calibration circuits for each hardware provider before interpreting provider-specific bitstrings;
- report bootstrap intervals over rows and shot-resampling intervals from raw counts;
- run independent reruns across different dates, queue conditions, and calibration windows;
- keep product-state, CX, and future entangling witness families separate in the manifest and report;
- include classical compute-equivalent timing or operation-count estimates when discussing hardware cost.

These items improve artifact reliability. They do not, by themselves, establish quantum-enhanced attention or model advantage.

## Theory Track

Stage 11 shows that the fixed 8/12 score is a mod-24 periodic feature with translation invariance, mirror aliases, context-length alias growth, period-pair tradeoffs, and exact small Fourier support. Stage 29 connects that theory to retrieval rows by auditing the Stage 11 period-pair grid on Stage 12 and Stage 22 non-phase-cued packets; the audit shows that period-pair swaps alone do not solve the fixed-score retrieval gap.

Open theory questions:

- which task distributions benefit from the 8/12 aliases and which are harmed by them;
- whether the score can be treated as a low-rank positional kernel;
- when a classical periodic feature map approximates the same behavior;
- whether other period pairs improve alias behavior under non-phase-cued retrieval;
- how PhaseWrap features should be combined with distance or content features without becoming an oracle label.

## Promotion Gate

PhaseWrap-RoPE can be described as a credible RoPE-replacement candidate only after a matched trained-transformer benchmark shows competitive performance against RoPE, ALiBI, sinusoidal, and no-position baselines on at least one non-PhaseWrap-labeled task, across multiple seeds, with confidence intervals and failed-run artifacts.

Stage 30 closes a compact-bridge confound by equalizing feature width and parameter count, but it does not satisfy this promotion gate because it is still a retrieval bridge rather than a stronger decoder-only transformer or standard language-model/retrieval harness.

Stage 31 adds a harder standard-retrieval stress test in which every prefix position competes. It also does not satisfy this promotion gate because the current PhaseWrap variants are weak against RoPE-like scoring in that setting.

Stage 32 shows a richer nonlinear PhaseWrap feature bridge can recover full-prefix argmax retrieval, but it still does not satisfy this promotion gate because it is not a decoder-only transformer and RoPE-like scoring remains stronger on probability/calibration metrics.

Stage 33 shows the Stage 32 probability/calibration gap is partly a post-hoc sharpness issue, but it also does not satisfy this promotion gate because RoPE-like scoring still has the strongest calibrated probability/ECE and the experiment is still a compact bridge rather than a decoder-only transformer.

Stage 34 is closer to the decoder-style target because it includes learned value embeddings and output projection, but it also does not satisfy this promotion gate because the current PhaseWrap-derived adapters trail RoPE-like scoring on top-1, MRR, and target value probability.

Stage 35 is diagnostic rather than a promotion benchmark. It removes learned attention selection and still reaches only partial value-output success, so the current package needs both better attention selection and stronger value-output coupling before scale-up.

Stage 36 improves the interpretation by hardening value-output coupling. It still does not satisfy this promotion gate because it is a compact bridge, not a decoder-only language-model benchmark, and RoPE-like scoring keeps stronger target probability mass.

Stage 37 narrows the hardened-output probability gap with scalar calibration, but it still does not satisfy this promotion gate because it is post-hoc calibration on a compact copy-value bridge rather than a matched decoder-only transformer. RoPE-like scoring also remains strongest on calibrated probability and ECE.

Stage 38 tests whether larger learned value-output capacity resolves the decoder-style gap. It still does not satisfy this promotion gate because it remains a compact bridge and because the hardened learned value-output path fits train but generalizes best with RoPE-like scoring on held-out length.

Stage 39 is closer to a sequence-level diagnostic because all prefix tokens compete, but it still does not satisfy this promotion gate. The current compact decoder does not achieve held-out length generalization for any tested positional method, so the artifact is a negative training/generalization result rather than evidence for a replacement mechanism.

Stage 40 tests a direct curriculum repair by adding length `512` to training and testing at `2048`. It still does not satisfy this promotion gate because held-out absolute performance remains weak. The PhaseWrap-derived adapters lead the weak `2048` test rows, but the compact sequence decoder remains an unreliable promotion harness.

Stage 41 tests a mechanism repair by adding pointer/copy value output to the Stage 40 all-prefix sequence setup. It still does not satisfy this promotion gate because the value path is a deterministic copy-head diagnostic rather than a matched decoder-only transformer, and RoPE-like scoring remains strongest on target probability and calibration even though PhaseWrap multiscale matches top-1/MRR.

Stage 42 tests a trainable version of that repair by mixing copied prefix-token mass with a learned vocab distribution. It still does not satisfy this promotion gate because it is a compact pointer-generator diagnostic, not a matched decoder-only transformer, and because the learned generator branch contributes little target mass while RoPE-like scoring remains strongest on probability/calibration.

Stage 43 tests generator-target hardening for the Stage 42 pointer-generator. It still does not satisfy this promotion gate because it remains a compact diagnostic and RoPE-like scoring remains strongest overall, even though generator target probability improves substantially for the successful methods.

Stage 44 audits Stages 39-43 as a compact-diagnostic plateau. It still does not satisfy this promotion gate because it trains no decoder-only transformer and instead records that the compact lane should remain bounded evidence rather than claim-expansion evidence.

Stage 45 runs the same fair-comparison frame in a matched one-block decoder-only gate. It still does not satisfy this promotion gate because the harness remains near chance across all tested methods and tasks, with target probability near uniform. The decision is `PROMOTION_NOT_SUPPORTED`, and the result is best read as a capacity/optimization failure before positional-method discrimination.

Stage 46 audits that capacity/optimization failure with longer training. It still does not satisfy this promotion gate because the best train top-1 reaches only `0.500000`, below the `0.750000` capacity threshold. PhaseWrap variants lead weak tiny text-fact QA rows, but the harness is still not a reliable positional-method discriminator.

Stage 47 replaces plain gradient descent with Adam on the same one-block decoder harness. It still does not satisfy this promotion gate because the retrieval lanes fail held-out generalization, even though train fit is solved and PhaseWrap variants lead the tiny text-fact QA lane.

Stage 48 reruns the Adam decoder audit across five seeds. It still does not satisfy this promotion gate because the tiny text-fact QA positive is not PhaseWrap-stable and both retrieval lanes still have zero held-out top-1 for every method.

Stage 49 applies a copy-decoder retrieval repair to the same row family. It still does not satisfy this promotion gate because the repaired exact-offset passkey lane is led by `rope_relative`, phase-cued retrieval remains weak, and copy-output repair is not the same as free learned value generation.

Stage 50 trains a learned pointer-generator decoder on the same row family. It still does not satisfy this promotion gate because retrieval remains below threshold, the Stage 49 fixed-copy repair does not survive learned attention/gating, and PhaseWrap-derived methods do not lead.

Stage 51 audits the Stage 45-50 decoder path. It still does not satisfy this promotion gate because it records the one-block, fixed-copy, and learned pointer-generator path as a bounded plateau rather than a promotion-ready transformer result.

Stage 52 starts a stronger two-block decoder path. It still does not satisfy this promotion gate because it is a one-seed feasibility audit and both retrieval lanes have zero held-out top-1 even though train fit and tiny text-fact QA improve.

Stage 53 hardens the Stage 52 two-block path. It still does not satisfy this promotion gate because held-out retrieval top-1 remains zero and the hardening direction weakens the tiny text-fact QA positive.

Stage 54 adds target-attention supervision to the Stage 52/53 two-block path. It still does not satisfy this promotion gate because target-attention supervision does not repair held-out retrieval target attention or top-1, and it is an auxiliary teacher signal rather than standard free decoder generation.

Stage 55 exposes row-metadata cue-copy features to every method. It still does not satisfy this promotion gate because the same upper bound solves retrieval for `no_position`; the result proves row-family solvability, not a positional-mechanism advantage.

Stage 56 restricts cue-copy to visible input tokens. It still does not satisfy this promotion gate because it only partially repairs exact-offset passkey and leaves phase-cued retrieval weak.

Stage 57 adds a known support prior to visible-token cue decoding. It still does not satisfy this promotion gate because phase-cued retrieval is solved for `no_position` too, and the support prior is supplied rather than learned by a matched decoder-only transformer.

Stage 58 learns the support map from pooled train rows. It still does not satisfy this promotion gate because it is a deterministic lookup/copy diagnostic, not a matched decoder-only transformer, and phase-cued retrieval still solves for `no_position`.

Stage 59 makes the support lookup seed-local. It still does not satisfy this promotion gate because held-out phase-cued support coverage is incomplete, the threshold-crossing result depends on deterministic fallback/copy behavior, and phase-cued retrieval still solves for `no_position`.

Stage 60 removes fallback cue help for unseen seed-local residues. It still does not satisfy this promotion gate because it shows the opposite of a robust repair: phase-cued retrieval crosses threshold only under fallback decoding and falls below threshold under strict known-support decoding.

Stage 61 returns to the learned two-block decoder with complete phase-cued support coverage. It still does not satisfy this promotion gate because the learned vocab-softmax decoder does not establish capacity and retrieval remains near zero.

Stage 62 lengthens training for that support-complete learned decoder. It still does not satisfy this promotion gate because train fit remains below the capacity threshold and held-out retrieval remains unrepaired.

Stage 63 replaces the learned vocab softmax with copied prefix-token mass from learned second-block attention. It establishes train capacity, but it still does not satisfy this promotion gate because held-out retrieval remains far below threshold and copy output is a diagnostic output-path repair, not free learned value generation.

Stage 64 replaces fixed copy output with a learned copy/vocab mixture. It establishes train capacity, but it still does not satisfy this promotion gate because held-out retrieval remains far below threshold and learned pointer-generation is still not full decoder-only language-model validation.

Stage 65 adds length-40 curriculum rows to the learned pointer-generator path. It preserves train capacity and improves tiny text-fact QA, but it still does not satisfy this promotion gate because held-out retrieval remains far below threshold, PhaseWrap-derived methods do not lead retrieval, and validation-length curriculum training is not the original train-short/test-long gate.

Stage 66 adds a direct positional-copy expert to the learned pointer-generator path. It preserves train capacity, but it still does not satisfy this promotion gate because held-out retrieval remains far below threshold and the expert is an output-path diagnostic rather than full decoder-only language-model validation.

Stage 67 redesigns the rows around visible content-key retrieval. It still does not satisfy this promotion gate because every tested method solves the rows, including `no_position`; the result proves harness/data-design solvability rather than a positional-mechanism advantage.

Until then, the supported claim remains narrower: PhaseWrap-RoPE is a compact, auditable phase-wrap positional scoring rule with reproducible classical analyses, bounded hardware readout witnesses, and mixed but useful toy downstream evidence.

The next gate should redesign the stronger matched decoder-only transformer beyond Stage 67 enough to improve original phase-cued/exact-offset held-out retrieval generalization before testing positional-method promotion. Hardware witness hardening remains a separate replication track and should not displace the fair-comparison promotion path.

## Researcher Use Context

The repository software is released under `AGPL-3.0-only`. Patent and IP-status notices are documented in `PATENTS.md` and `docs/publication/patent-status-note-v1.md`. Researchers should treat those notices as licensing and IP context, not as scientific evidence.
