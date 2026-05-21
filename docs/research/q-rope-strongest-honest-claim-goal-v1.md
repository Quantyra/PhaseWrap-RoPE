# PhaseWrap-RoPE Strongest Honest Claim Goal v1

Date: `2026-05-21`

Status: `active`

## Goal

Find the strongest honest claim PhaseWrap-RoPE can support under fair RoPE, ALiBI, sinusoidal, and no-position comparisons, preserving both positive evidence and failure modes.

The program should optimize for the maximum defensible claim boundary, not for proving that PhaseWrap-RoPE replaces RoPE. A negative or mixed result is successful if it cleanly separates useful PhaseWrap behavior from unsupported replacement, hardware-advantage, or production-transformer claims.

## Evidence Standard

Promotion evidence must include:

- matched positional-method comparisons against RoPE or RoPE-like, ALiBI, sinusoidal, and no-position baselines;
- non-PhaseWrap-labeled retrieval, QA, or language-model-style tasks;
- at least five seeds for learned components;
- loss or perplexity, top-1, MRR, target probability, calibration, confidence intervals, and weak-run reporting;
- failed, diverged, and underperforming runs retained in the artifact tree.

Evidence is not enough for a RoPE-replacement claim if it is only a compact bridge, a deterministic copy diagnostic, a post-hoc calibration audit, a PhaseWrap-labeled task, a small-circuit hardware witness, or a result selected only by top-1/MRR while probability and calibration remain worse.

## Current Claim Boundary

Supported now:

- PhaseWrap-RoPE is an auditable modular phase-wrap scoring rule with reproducible classical analyses.
- The repository contains bounded small-circuit hardware readout witnesses for the recorded packets, providers, dates, and calibration contexts.
- PhaseWrap-derived adapters can be competitive on ranking in several compact retrieval and copy-aware diagnostics.
- Stage 43 shows that generator-target hardening improves the Stage 42 learned vocab branch and preserves PhaseWrap-derived ranking competitiveness.
- Stage 44 records Stages 39-43 as a compact-diagnostic plateau: useful bounded mechanism evidence, not promotion evidence.
- Stage 45 runs a matched one-block decoder-only gate and records `PROMOTION_NOT_SUPPORTED`; the harness remains near chance and is not a reliable promotion discriminator.
- Stage 46 applies longer training to that one-block harness and records `CAPACITY_NOT_ESTABLISHED`; weak PhaseWrap tiny text-fact QA positives remain below the capacity threshold.
- Stage 47 applies Adam optimizer hardening and records `TRAIN_FIT_WITH_PARTIAL_GENERALIZATION`; PhaseWrap leads tiny text-fact QA, but retrieval lanes still fail held-out generalization.
- Stage 48 reruns the Adam decoder audit across five seeds and records `TINY_QA_POSITIVE_NOT_PHASEWRAP_STABLE_RETRIEVAL_FAILED`; tiny text-fact QA stays positive, but the PhaseWrap lead is not stable and retrieval still fails.
- Stage 49 applies a copy-decoder retrieval repair to the same row family and records `COPY_DECODER_PARTIALLY_REPAIRS_RETRIEVAL`; exact-offset passkey is repaired for `rope_relative`, tiny text-fact QA becomes easy for all methods, and phase-cued retrieval remains weak.
- Stage 50 trains a learned pointer-generator decoder on the same row family and records `LEARNED_POINTER_GENERATOR_RETRIEVAL_REPAIR_FAILED`; tiny text-fact QA remains positive, but learned attention/gating does not preserve the Stage 49 fixed-copy exact-offset repair.
- Stage 51 audits Stages 45-50 and records `BOUND_DECODER_PATH_PLATEAU`; optimizer and output-path repairs are useful bottleneck diagnostics, but learned decoder retrieval generalization is not established and PhaseWrap does not lead a repaired retrieval lane.
- Stage 52 moves beyond the Stage 51 plateau with a two-block residual decoder feasibility audit and records `TWO_BLOCK_TRAIN_FIT_WITHOUT_RETRIEVAL_GENERALIZATION`; train fit and tiny text-fact QA improve on the one-seed feasibility packet, but retrieval generalization remains zero.
- Stage 53 hardens Stage 52 with more retrieval exposure and training budget and records `TWO_BLOCK_RETRIEVAL_HARDENING_FAILED`; held-out retrieval top-1 remains zero and the hardening direction weakens the tiny text-fact QA positive.
- Stage 54 adds target-attention supervision to the Stage 52/53 two-block path and records `ATTENTION_SUPERVISION_RETRIEVAL_REPAIR_FAILED`; training attention can be raised, but held-out retrieval target attention and top-1 remain unrepaired.
- Stage 55 adds explicit row-metadata cue-copy features and records `ROW_METADATA_CUE_COPY_UPPER_BOUND_SOLVES_RETRIEVAL_NOT_PROMOTION`; the row family is solvable when the target-distance/congruence cue is handed to every method, including `no_position`, so this is not positional-method promotion evidence.
- Stage 56 restricts cue-copy to visible input tokens and records `STANDARD_INPUT_CUE_COPY_PARTIAL_RETRIEVAL`; exact-offset passkey is partially repaired for `rope_relative`, but phase-cued retrieval remains weak.
- Stage 57 adds a known support prior to visible query-token cue decoding and records `SUPPORT_AWARE_QUERY_CUE_SOLVES_PHASE_CUED_NOT_PROMOTION`; phase-cued retrieval is solvable from the query cue plus support prior, but `no_position` solves too.
- Stage 58 learns the query-token support map from pooled train rows and records `POOLED_TRAIN_QUERY_SUPPORT_SOLVES_PHASE_CUED_NOT_PROMOTION`; the support prior is train-recoverable, but the repair still solves for `no_position` too.
- Stage 59 makes the support lookup seed-local and records `SEED_LOCAL_QUERY_SUPPORT_PARTIAL_COVERAGE_SOLVES_NOT_PROMOTION`; held-out phase-cued support coverage is incomplete per seed, fallback cue decoding crosses threshold, and `no_position` solves too.
- Stage 60 removes fallback cue help for unseen seed-local residues and records `FALLBACK_DEPENDENT_PHASE_CUED_RETRIEVAL_NOT_PROMOTION`; phase-cued retrieval crosses threshold only with fallback decoding, while strict known-support decoding falls below threshold.
- Stage 61 returns to a learned two-block vocab-softmax decoder with complete phase-cued support coverage and records `SUPPORT_COMPLETE_TWO_BLOCK_CAPACITY_NOT_ESTABLISHED`; support coverage alone does not make the learned decoder fit or generalize retrieval.
- Stage 62 increases the support-complete learned two-block decoder to longer training and records `LONG_TRAINING_SUPPORT_COMPLETE_CAPACITY_NOT_ESTABLISHED`; train fit improves, including a PhaseWrap-adapter phase-cued train lead, but capacity and held-out retrieval remain below threshold.

Not supported now:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that the Stage 4 hardware witnesses establish model advantage;
- a claim that Stage 43 solves free learned value generation or validates PhaseWrap-RoPE as a RoPE replacement.
- a claim that additional compact copy-path diagnostics should broaden the claim boundary after the Stage 44 plateau audit.
- a claim that Stage 45 validates PhaseWrap-RoPE as a replacement or production transformer mechanism.
- a claim that Stage 46 validates the one-block decoder harness as a positional-method discriminator.
- a claim that Stage 47's tiny text-fact QA positive is enough for a RoPE-replacement claim.
- a claim that the Stage 47 one-seed PhaseWrap tiny text-fact QA lead is stable across seeds.
- a claim that Stage 49's copy-output repair is equivalent to free learned value generation or promotes PhaseWrap-RoPE over RoPE.
- a claim that Stage 50 validates PhaseWrap-RoPE as a RoPE replacement or solves learned retrieval generation.
- a claim that the Stage 45-50 decoder path should broaden the claim boundary after the Stage 51 plateau audit.
- a claim that Stage 52 satisfies the five-seed promotion standard or establishes retrieval generalization.
- a claim that Stage 53 repairs retrieval or validates the two-block hardening path for promotion.
- a claim that Stage 54 attention supervision repairs retrieval, proves a value-output-only bottleneck, or validates the two-block auxiliary-loss path for promotion.
- a claim that Stage 55 is positional-method promotion evidence or that explicit row metadata is a standard decoder-only input feature.
- a claim that Stage 56 solves the phase-cued retrieval blocker or validates a learned decoder-only transformer.
- a claim that Stage 57 is positional-method promotion evidence or that the known support prior is a learned decoder-only transformer capability.
- a claim that Stage 58 is positional-method promotion evidence or that a pooled lookup map is a matched decoder-only transformer.
- a claim that Stage 59 is positional-method promotion evidence, that seed-local lookup/fallback is a matched decoder-only transformer, or that per-seed support coverage is complete on held-out phase-cued rows.
- a claim that Stage 60 is positional-method promotion evidence, that fallback decoding is learned decoder behavior, or that strict seed-local support solves held-out phase-cued retrieval.
- a claim that Stage 61 is positional-method promotion evidence or that complete support coverage alone establishes learned decoder capacity.
- a claim that Stage 62 is positional-method promotion evidence or that longer training alone establishes learned decoder capacity.

## Decision Outcomes

The active research goal can resolve in any of three valid outcomes:

- `PROMOTE`: PhaseWrap-derived mechanisms become credible auxiliary or replacement candidates under matched transformer-style benchmarks.
- `BOUND`: PhaseWrap remains useful as a bounded modular feature, adapter, or hardware-witness system, with clear limits.
- `FALSIFY_PROMOTION`: PhaseWrap fails the transformer promotion path, while the repo preserves a defensible negative result and avoids overclaiming.

Until a matched transformer-style benchmark satisfies the evidence standard, the default outcome remains `BOUND`.

## Next Gate

The next gate should redesign the stronger matched decoder-only implementation beyond Stage 62 so learned capacity is established before positional-method promotion is evaluated, under the same fair RoPE, ALiBI, sinusoidal, no-position, and PhaseWrap comparison.

Preferred next direction:

- keep RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons matched;
- move from the partially generalizing one-block decoder-only gate, bounded copy-output repair, failed learned pointer-generator repair, Stage 51 plateau, Stage 52 feasibility result, Stage 53 failed hardening result, Stage 54 failed attention-supervision result, Stage 55 metadata upper bound, Stage 56 standard-input partial repair, Stage 57 support-aware cue upper bound, Stage 58 pooled lookup, Stage 59 seed-local lookup/fallback diagnostic, Stage 60 fallback strictness result, Stage 61 support-complete capacity failure, and Stage 62 long-training capacity failure into a redesigned retrieval-targeted decoder-only harness;
- report ranking and calibration even if the PhaseWrap result weakens.

Because Stage 44 records the compact plateau and Stage 51 records the decoder-path plateau, another diagnostic should be justified only if it directly improves retrieval generalization in a materially stronger matched decoder-only transformer implementation. Stage 52 starts that stronger path, Stage 53 hardens it, Stage 54 adds target-attention supervision, Stage 55 proves metadata-cue solvability, Stage 56 tests visible-token cues, Stage 57 adds the known support prior, Stage 58 learns the pooled support map, Stage 59 makes that map seed-local, Stage 60 shows phase-cued success is fallback-dependent, Stage 61 shows support completeness still does not establish learned decoder capacity, and Stage 62 shows longer training is still below capacity; none establishes fair positional-method promotion.
