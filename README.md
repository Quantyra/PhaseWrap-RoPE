# PhaseWrap-RoPE

[![CI](https://github.com/Quantyra/PhaseWrap-RoPE/actions/workflows/ci.yml/badge.svg)](https://github.com/Quantyra/PhaseWrap-RoPE/actions/workflows/ci.yml)
[![Open verification in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Quantyra/PhaseWrap-RoPE/blob/main/docs/notebooks/phasewrap_rope_verify.ipynb)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20306786.svg)](https://doi.org/10.5281/zenodo.20306786)

PhaseWrap-RoPE is Quantyra's public research repository for a phase-wrap positional scoring rule with two-qubit hardware readout.

This repository is intended for open scientific review of the PhaseWrap-RoPE scoring rule, validation scripts, evidence packets, and publication materials. It is not a claim of general quantum advantage, full transformer-scale superiority, entanglement-based advantage, or cross-backend hardware robustness.

Repository naming note: public materials use `PhaseWrap-RoPE`; Python imports, script paths, packet IDs, and evidence IDs retain the existing `qrope` stem.

## Read the Paper

Start here:

- [Repository paper: PhaseWrap-RoPE bounded phase-wrap scoring rule](docs/publication/qrope-paper-v1.md)
- Zenodo concept DOI: [10.5281/zenodo.20306786](https://doi.org/10.5281/zenodo.20306786)
- One-page reviewer summary: [Quickstart and results summary](docs/publication/quickstart-results-summary-v1.md)
- One-cell verification notebook: [Open in Colab](https://colab.research.google.com/github/Quantyra/PhaseWrap-RoPE/blob/main/docs/notebooks/phasewrap_rope_verify.ipynb)

The paper is the canonical narrative for the current release. It frames PhaseWrap-RoPE as a bounded positional scoring rule, not as a validated production transformer positional encoding method. The repository provides the artifacts behind the paper: frozen packets, raw counts, verifier scripts, hardware sweep outputs, classical baselines, and toy downstream ablations.

Minimal local verification:

```bash
python scripts/verify_stage4_hardware_packet.py
python scripts/verify_stage4_hardware_sweep.py
python scripts/estimate_stage4_classical_compute_cost.py
python scripts/preregister_stage4_replication_packets.py
python scripts/prepare_stage4_bitstring_calibration_packets.py
python scripts/run_stage5_attention_baselines.py
python scripts/run_stage6_downstream_attention.py
python scripts/run_stage7_toy_transformer_ablation.py
python scripts/run_stage8_needle_benchmark.py
python scripts/run_stage9_trained_transformer_ablation.py
python scripts/run_stage10_small_decoder_transformer.py
python scripts/run_stage11_phasewrap_theory.py
python scripts/run_stage12_ruler_retrieval.py
python scripts/run_stage13_positional_adapter.py
python scripts/run_stage14_attention_readout.py
python scripts/run_stage15_learned_attention.py
python scripts/run_stage16_learned_attention_stability.py
python scripts/run_stage17_small_decoder_value_model.py
python scripts/run_stage18_value_output_capacity.py
python scripts/run_stage19_value_output_hardening.py
python scripts/run_stage20_hardened_positional_value_model.py
python scripts/run_stage21_hardened_positional_stability.py
python scripts/run_stage22_long_context_retrieval.py
python scripts/run_stage23_long_context_adapter.py
python scripts/run_stage24_long_context_value_model.py
python scripts/run_stage25_long_context_value_stability.py
python scripts/run_stage26_compact_kv_qa.py
python scripts/run_stage27_compact_kv_transformer_bridge.py
python scripts/run_stage28_ruler_attention_bridge.py
python scripts/run_stage29_period_pair_task_audit.py
python scripts/run_stage30_matched_retrieval_bridge.py
python scripts/run_stage31_full_context_retrieval_attention.py
python scripts/run_stage32_full_context_feature_bridge.py
python scripts/run_stage33_temperature_calibration.py
python scripts/run_stage34_small_decoder_value_bridge.py
python scripts/run_stage35_value_bridge_bottleneck_diagnostic.py
python scripts/run_stage36_copy_value_bridge.py
python scripts/run_stage37_copy_value_temperature_calibration.py
python scripts/run_stage38_hardened_decoder_value_bridge.py
python scripts/run_stage39_sequence_decoder_retrieval.py
python scripts/run_stage40_sequence_length_curriculum.py
python scripts/run_stage41_pointer_copy_sequence.py
python scripts/run_stage42_trainable_pointer_generator_sequence.py
python scripts/run_stage43_generator_hardened_pointer_sequence.py
python scripts/run_stage44_compact_diagnostic_plateau_audit.py
python scripts/run_stage45_matched_decoder_only_gate.py
python scripts/run_stage46_decoder_capacity_hardening_audit.py
python scripts/run_stage47_adam_decoder_generalization_audit.py
python scripts/run_stage48_adam_decoder_stability_audit.py
python scripts/run_stage49_copy_decoder_retrieval_repair_audit.py
python scripts/run_stage50_learned_pointer_generator_decoder_audit.py
python scripts/run_stage51_decoder_path_plateau_audit.py
python scripts/run_stage52_two_block_decoder_feasibility_audit.py
python scripts/run_stage53_two_block_retrieval_hardening_audit.py
python scripts/run_stage54_attention_supervised_two_block_audit.py
python scripts/run_stage55_row_metadata_cue_copy_upper_bound_audit.py
python scripts/run_stage56_standard_input_cue_copy_audit.py
python scripts/run_stage57_support_aware_query_cue_audit.py
python scripts/run_stage58_pooled_train_query_support_audit.py
python scripts/run_stage59_seed_local_query_support_audit.py
python scripts/run_stage60_support_fallback_strictness_audit.py
python scripts/run_stage61_support_complete_two_block_audit.py
python scripts/run_stage62_long_training_support_complete_audit.py
python scripts/run_stage63_two_block_copy_output_capacity_audit.py
python scripts/run_stage64_two_block_pointer_generator_capacity_audit.py
python scripts/run_stage65_pointer_generator_length_curriculum_audit.py
python scripts/run_stage66_positional_copy_expert_audit.py
python scripts/run_stage67_content_key_retrieval_audit.py
python scripts/run_stage68_content_key_auxiliary_transfer_audit.py
python scripts/run_stage69_original_multitask_pointer_generator_audit.py
python scripts/run_stage70_strongest_honest_claim_synthesis.py
python scripts/run_stage71_positional_bias_copy_upper_bound_audit.py
python scripts/run_stage72_phase_cued_bias_tie_support_audit.py
python scripts/run_stage73_phase_cued_period_pair_support_audit.py
python scripts/run_stage74_leave_one_seed_query_support_audit.py
python scripts/run_stage75_learned_query_support_head_audit.py
```

## Status

- `Patent/IP posture`: USPTO provisional submission received `2026-05-18`; the Electronic Acknowledgement Receipt lists application `64/068,121` and Patent Center `76347440`; final Filing Receipt pending. See [Patent status note](docs/publication/patent-status-note-v1.md).
- `Archive DOI`: `10.5281/zenodo.20306786` for the latest bounded evidence release.
- `License`: GNU Affero General Public License v3.0 only (`AGPL-3.0-only`).
- `Publication posture`: bounded, reproducible, evidence-disciplined.
- `Current evidence posture`: Stage 4 real-noisy-hardware results for bounded frozen packet/backend/date/calibration contexts, including IBM Fez positives, Amazon Braket/Rigetti product-state positive evidence, and provider-aware Amazon Braket CX positive recomputations from committed raw counts.
- `Stage 4 cost posture`: local recomputation of the committed Stage 4 sweep is covered by a deterministic classical compute estimate: 4,096 static operations over 163,072 recorded hardware shots, with zero incremental local verifier cost and no provider billing reconstruction.
- `Stage 4 preregistration posture`: future replication lanes now have no-hardware preregistered row-set artifacts with fixed seeds, families, shots, row counts, and row-set hashes; they are not submitted hardware evidence.
- `Stage 4 calibration posture`: provider bitstring calibration packet specs and a failing-by-default verifier contract now exist for IBM-style `q1q0` and Amazon Braket-style `q0q1` known-state checks; real calibration counts are still missing.
- `RoPE-facing benchmark posture`: Stage 8 adds a local phase-cued Needle-style retrieval packet, Stage 9 adds a trained decoder-style positional attention ablation, Stage 12 adds a stricter non-phase-cued RULER-style retrieval packet, Stage 13 tests trained positional adapters, Stage 14 turns the non-phase-cued rows into key-value attention readout, Stage 15 adds a one-hidden-layer learned attention scorer, Stage 16 checks initialization stability, Stage 17 adds learned value embeddings plus output projection, Stage 18 probes that value-output bottleneck with teacher-forced attention, Stage 19 hardens the teacher-forced value-output path, Stage 20 reintroduces learned positional attention with the hardened path, Stage 21 reruns that comparison across five initialization seeds, Stage 22 extends explicit retrieval to 4096-token contexts, Stage 23 trains adapters on those long-context rows, Stage 24 adds learned value embeddings/output projection to the long-context rows, Stage 25 reruns that long-context value model across five initialization seeds, Stage 26 adds a compact key-value QA retrieval packet with explicit content keys, Stage 27 trains a compact attention bridge on that packet across five model initialization seeds, Stage 28 trains a compact attention bridge directly over non-phase-cued RULER-style retrieval rows, Stage 29 audits fixed period-pair choices on those retrieval rows, Stage 30 repeats the Stage 28 bridge with matched feature width and parameter count, Stage 31 moves to learned full-prefix retrieval attention, Stage 32 adds a nonlinear full-context feature bridge, Stage 33 adds post-hoc temperature calibration, Stage 34 adds a compact decoder-style value bridge, Stage 35 adds a teacher-forced value-output diagnostic, Stage 36 adds a copy-value bridge, Stage 37 calibrates that copy-value bridge, Stage 38 hardens the learned decoder-style value bridge, Stage 39 moves to all-prefix sequence decoder retrieval, Stage 40 adds a broader length curriculum, Stage 41 adds a pointer/copy sequence head, Stage 42 makes that output path trainable with a pointer-generator mixture, Stage 43 adds auxiliary generator-target hardening, Stage 44 records a compact-diagnostic plateau, Stage 45 runs a matched one-block decoder-only gate, Stage 46 audits longer-training capacity, Stage 47 adds Adam optimizer hardening, Stage 48 checks five-seed stability, Stage 49 tests a fixed copy-decoder retrieval repair, Stage 50 tests a learned pointer-generator decoder, Stage 51 records the decoder path as a bounded plateau, Stage 52 starts a stronger two-block decoder feasibility path, Stage 53 hardens retrieval exposure for that two-block path, Stage 54 adds target-attention supervision, Stage 55 adds an explicit row-metadata cue-copy upper bound, Stage 56 restricts cue-copy to visible input tokens, Stage 57 adds a known-support prior for decoding the query cue, Stage 58 learns that support map from pooled train rows, Stage 59 makes the lookup seed-local, Stage 60 removes fallback cue help for unseen residues, Stage 61 returns to learned two-block decoding with support-complete training, Stage 62 extends that learned decoder to longer training, Stage 63 replaces the vocab softmax with learned copy-output attention, Stage 64 tests a learned pointer-generator mixture, Stage 65 adds length-40 curriculum rows, Stage 66 adds a direct positional-copy expert, Stage 67 redesigns rows around visible content-key retrieval, Stage 68 tests whether that content-key signal transfers back to original retrieval rows, Stage 69 tests original-task multitask training, Stage 70 synthesizes the current strongest honest claim, Stage 71 tests deterministic positional-bias copy on the original rows, Stage 72 tests tie-aware phase-cued max-bias support, Stage 73 sweeps predeclared PhaseWrap period pairs on phase-cued support, Stage 74 tests leave-one-seed visible query-support recovery, and Stage 75 replaces that hard lookup with a learned query-support head. Stage 75 records `LEARNED_QUERY_SUPPORT_HEAD_SOLVES_PHASE_CUED_NOT_PROMOTION`: phase-cued retrieval reaches top-1 `0.900000`, but `no_position` reaches the same result, so this is learned visible-cue evidence rather than positional-method promotion.
- `Score theory posture`: Stage 11 formalizes the fixed 8/12 score as a mod-24 periodic feature with translation invariance, mirror aliases, 10 distinct residue scores, and exact small Fourier support. This clarifies why stronger transformer benchmarks must resolve aliasing before any replacement claim.
- `Hardware posture`: IBM Fez product-state, IBM Fez CX, Amazon Braket/Rigetti product-state, and Amazon Braket CX lanes have completed active Stage 4 hardware artifacts; additional IBM machines are deferred from the active sweep; Amazon Braket/IonQ was checked on 2026-05-19 and was not run because Forte devices were `OFFLINE` and Aria 1 was `RETIRED`; AQT IBEX Q1 is deferred due cost.
- `Evidence tree posture`: `logs/automated_stage_gates/stage4_hardware_packet/` remains the default single-packet verifier path. The same IBM Fez 2026-05-17 product-state pass is also preserved as an immutable named run under `logs/automated_stage_gates/stage4_hardware_packet_ibm_fez_20260517_pass/` for the sweep manifest.

## Claim boundary

The public claim frame for this repository is:

- PhaseWrap-RoPE defines phase-wrap residual features using mod-8 and mod-12 structure.
- The SQR score uses the product of the mod-8 and mod-12 signed margins.
- The evidence lane includes deterministic frozen-packet validation, raw counts, backend metadata, and offline recomputation.
- The Stage 4 result is a bounded real-hardware validation for the frozen packet reported in this repository.
- The Amazon Braket/Rigetti replication artifact is an 8-row, 1000-shot-per-row product-state hardware-positive run with offline verifier pass.
- The current active hardware evidence includes two product-state angle-encoding/readout witness artifacts: IBM Fez and Amazon Braket/Rigetti.
- The entangling CX witness family is implemented as `two_qubit_cx_parity_phase_wrap_v2`; IBM Fez and Amazon Braket executions on Rigetti Cepheus, IQM Garnet, and IQM Emerald verify as hardware-positive when decoded with the manifest-declared provider bitstring order. This does not support a general cross-backend robustness claim.

The public claim frame excludes:

- broad quantum advantage;
- full transformer-scale validation;
- general cross-backend superiority;
- claims that PhaseWrap-RoPE improves production language-model quality;
- claims that one backend/date/calibration result generalizes without additional evidence.

The active research north star is to find the strongest honest claim PhaseWrap-RoPE can support under fair RoPE, ALiBI, sinusoidal, and no-position comparisons while preserving both positive evidence and failure modes. See [Strongest honest claim goal](docs/research/q-rope-strongest-honest-claim-goal-v1.md).

## Key documents

- [Repository paper v1](docs/publication/qrope-paper-v1.md)
- [Manuscript-to-provisional support audit](docs/publication/manuscript-to-provisional-support-audit-v1.md)
- [Patent status note](docs/publication/patent-status-note-v1.md)
- [Quickstart and results summary](docs/publication/quickstart-results-summary-v1.md)
- [External review response](docs/publication/external-review-response-v1.md)
- [Replication plan](docs/publication/replication-plan-v1.md)
- [External release plan](docs/publication/external-release-plan-v1.md)
- [PhaseWrap-RoPE method schematic](docs/publication/figures/qrope-method-schematic-v1.svg)
- [Validation pipeline figure](docs/publication/figures/qrope-validation-pipeline-v1.svg)
- [Stage 4 comparison figure](docs/publication/figures/qrope-stage4-comparison-v1.svg)
- [Open-source release checklist](docs/publication/open-source-release-checklist-v1.md)
- [Patent notice](PATENTS.md)
- [Stage 4 real-hardware validation result](docs/research/q-rope-stage4-real-hardware-validation-result-v1.md)
- [Stage 4 preregistered replication packets](docs/research/q-rope-stage4-preregistered-replication-packets-v1.md)
- [Stage 4 bitstring calibration plan](docs/research/q-rope-stage4-bitstring-calibration-plan-v1.md)
- [Stage 4 classical compute cost estimate](docs/research/q-rope-stage4-classical-compute-cost-v1.md)
- [Stage 4 CX portability diagnostic](docs/research/q-rope-stage4-cx-portability-diagnostic-v1.md)
- [Stage 5 attention baseline result](docs/research/q-rope-stage5-attention-baselines-v1.md)
- [Stage 6 downstream attention result](docs/research/q-rope-stage6-downstream-attention-v1.md)
- [Stage 7 toy transformer ablation](docs/research/q-rope-stage7-toy-transformer-ablation-v1.md)
- [Stage 8 Needle-style benchmark](docs/research/q-rope-stage8-needle-benchmark-v1.md)
- [Stage 9 trained transformer ablation plan and first executable subset](docs/research/q-rope-stage9-trained-transformer-ablation-plan-v1.md)
- [Next transformer benchmark roadmap](docs/research/q-rope-next-transformer-benchmark-roadmap-v1.md)
- [Stage 11 PhaseWrap score theory analysis](docs/research/q-rope-stage11-phasewrap-theory-v1.md)
- [Stage 12 RULER-style retrieval benchmark](docs/research/q-rope-stage12-ruler-retrieval-v1.md)
- [Stage 13 positional-adapter benchmark](docs/research/q-rope-stage13-positional-adapter-v1.md)
- [Stage 14 attention-readout benchmark](docs/research/q-rope-stage14-attention-readout-v1.md)
- [Stage 15 learned attention-readout benchmark](docs/research/q-rope-stage15-learned-attention-v1.md)
- [Stage 16 learned attention stability benchmark](docs/research/q-rope-stage16-learned-attention-stability-v1.md)
- [Stage 17 small decoder value-model benchmark](docs/research/q-rope-stage17-small-decoder-value-model-v1.md)
- [Stage 18 value-output capacity probe](docs/research/q-rope-stage18-value-output-capacity-v1.md)
- [Stage 19 value-output hardening probe](docs/research/q-rope-stage19-value-output-hardening-v1.md)
- [Stage 20 hardened positional value-model benchmark](docs/research/q-rope-stage20-hardened-positional-value-model-v1.md)
- [Stage 21 hardened positional stability benchmark](docs/research/q-rope-stage21-hardened-positional-stability-v1.md)
- [Stage 22 long-context retrieval benchmark](docs/research/q-rope-stage22-long-context-retrieval-v1.md)
- [Stage 23 long-context adapter benchmark](docs/research/q-rope-stage23-long-context-adapter-v1.md)
- [Stage 24 long-context value-model benchmark](docs/research/q-rope-stage24-long-context-value-model-v1.md)
- [Stage 25 long-context value-model stability](docs/research/q-rope-stage25-long-context-value-stability-v1.md)
- [Stage 26 compact key-value QA benchmark](docs/research/q-rope-stage26-compact-kv-qa-v1.md)
- [Stage 27 compact key-value transformer-bridge benchmark](docs/research/q-rope-stage27-compact-kv-transformer-bridge-v1.md)
- [Stage 28 RULER-style attention-bridge benchmark](docs/research/q-rope-stage28-ruler-attention-bridge-v1.md)
- [Stage 29 period-pair task audit](docs/research/q-rope-stage29-period-pair-task-audit-v1.md)
- [Stage 30 matched retrieval-bridge benchmark](docs/research/q-rope-stage30-matched-retrieval-bridge-v1.md)
- [Stage 31 full-context retrieval-attention benchmark](docs/research/q-rope-stage31-full-context-retrieval-attention-v1.md)
- [Stage 32 full-context feature-bridge benchmark](docs/research/q-rope-stage32-full-context-feature-bridge-v1.md)
- [Stage 33 temperature calibration audit](docs/research/q-rope-stage33-temperature-calibration-v1.md)
- [Stage 34 small decoder value-bridge benchmark](docs/research/q-rope-stage34-small-decoder-value-bridge-v1.md)
- [Stage 35 value-bridge bottleneck diagnostic](docs/research/q-rope-stage35-value-bridge-bottleneck-diagnostic-v1.md)
- [Stage 36 copy-value bridge benchmark](docs/research/q-rope-stage36-copy-value-bridge-v1.md)
- [Stage 37 copy-value temperature calibration audit](docs/research/q-rope-stage37-copy-value-temperature-calibration-v1.md)
- [Stage 38 hardened decoder value-bridge benchmark](docs/research/q-rope-stage38-hardened-decoder-value-bridge-v1.md)
- [Stage 39 sequence decoder retrieval benchmark](docs/research/q-rope-stage39-sequence-decoder-retrieval-v1.md)
- [Stage 40 sequence length-curriculum benchmark](docs/research/q-rope-stage40-sequence-length-curriculum-v1.md)
- [Stage 41 pointer/copy sequence benchmark](docs/research/q-rope-stage41-pointer-copy-sequence-v1.md)
- [Stage 42 trainable pointer-generator sequence benchmark](docs/research/q-rope-stage42-trainable-pointer-generator-sequence-v1.md)
- [Stage 43 generator-hardened pointer sequence benchmark](docs/research/q-rope-stage43-generator-hardened-pointer-sequence-v1.md)
- [Stage 44 compact-diagnostic plateau audit](docs/research/q-rope-stage44-compact-diagnostic-plateau-audit-v1.md)
- [Stage 45 matched decoder-only gate](docs/research/q-rope-stage45-matched-decoder-only-gate-v1.md)
- [Stage 46 decoder capacity hardening audit](docs/research/q-rope-stage46-decoder-capacity-hardening-audit-v1.md)
- [Stage 47 Adam decoder generalization audit](docs/research/q-rope-stage47-adam-decoder-generalization-audit-v1.md)
- [Stage 48 Adam decoder stability audit](docs/research/q-rope-stage48-adam-decoder-stability-audit-v1.md)
- [Stage 49 copy-decoder retrieval repair audit](docs/research/q-rope-stage49-copy-decoder-retrieval-repair-audit-v1.md)
- [Stage 50 learned pointer-generator decoder audit](docs/research/q-rope-stage50-learned-pointer-generator-decoder-audit-v1.md)
- [Stage 51 decoder-path plateau audit](docs/research/q-rope-stage51-decoder-path-plateau-audit-v1.md)
- [Stage 52 two-block decoder feasibility audit](docs/research/q-rope-stage52-two-block-decoder-feasibility-audit-v1.md)
- [Stage 53 two-block retrieval hardening audit](docs/research/q-rope-stage53-two-block-retrieval-hardening-audit-v1.md)
- [Stage 54 attention-supervised two-block audit](docs/research/q-rope-stage54-attention-supervised-two-block-audit-v1.md)
- [Stage 55 row-metadata cue-copy upper-bound audit](docs/research/q-rope-stage55-row-metadata-cue-copy-upper-bound-audit-v1.md)
- [Stage 56 standard-input cue-copy audit](docs/research/q-rope-stage56-standard-input-cue-copy-audit-v1.md)
- [Stage 57 support-aware query-cue audit](docs/research/q-rope-stage57-support-aware-query-cue-audit-v1.md)
- [Stage 58 pooled-train query support audit](docs/research/q-rope-stage58-pooled-train-query-support-audit-v1.md)
- [Stage 59 seed-local query support audit](docs/research/q-rope-stage59-seed-local-query-support-audit-v1.md)
- [Stage 60 support fallback strictness audit](docs/research/q-rope-stage60-support-fallback-strictness-audit-v1.md)
- [Stage 61 support-complete two-block audit](docs/research/q-rope-stage61-support-complete-two-block-audit-v1.md)
- [Stage 62 long-training support-complete audit](docs/research/q-rope-stage62-long-training-support-complete-audit-v1.md)
- [Stage 63 two-block copy-output capacity audit](docs/research/q-rope-stage63-two-block-copy-output-capacity-audit-v1.md)
- [Stage 64 two-block pointer-generator capacity audit](docs/research/q-rope-stage64-two-block-pointer-generator-capacity-audit-v1.md)
- [Stage 65 pointer-generator length-curriculum audit](docs/research/q-rope-stage65-pointer-generator-length-curriculum-audit-v1.md)
- [Stage 66 positional-copy expert audit](docs/research/q-rope-stage66-positional-copy-expert-audit-v1.md)
- [Stage 67 content-key retrieval audit](docs/research/q-rope-stage67-content-key-retrieval-audit-v1.md)
- [Stage 68 content-key auxiliary transfer audit](docs/research/q-rope-stage68-content-key-auxiliary-transfer-audit-v1.md)
- [Stage 69 original multitask pointer-generator audit](docs/research/q-rope-stage69-original-multitask-pointer-generator-audit-v1.md)
- [Stage 70 strongest honest claim synthesis](docs/research/q-rope-stage70-strongest-honest-claim-synthesis-v1.md)
- [Stage 71 positional-bias copy upper-bound audit](docs/research/q-rope-stage71-positional-bias-copy-upper-bound-audit-v1.md)
- [Stage 72 phase-cued bias tie-support audit](docs/research/q-rope-stage72-phase-cued-bias-tie-support-audit-v1.md)
- [Stage 73 phase-cued period-pair support audit](docs/research/q-rope-stage73-phase-cued-period-pair-support-audit-v1.md)
- [Stage 74 leave-one-seed query-support audit](docs/research/q-rope-stage74-leave-one-seed-query-support-audit-v1.md)
- [Stage 75 learned query-support head audit](docs/research/q-rope-stage75-learned-query-support-head-audit-v1.md)
- [Strongest honest claim goal](docs/research/q-rope-strongest-honest-claim-goal-v1.md)
- [Amazon Braket hardware runbook](docs/evidence/E002-braket-hardware-runbook.md)
- [Automated terminal human-review packet](docs/evidence/review-packets/qrope-automated-terminal-v1/qrope-terminal-human-review-packet-v1.md)
- [Phase-wrap algorithm note](docs/research/q-rope-phase-wrap-qrope-algorithm-v1.md)

## Quickstart

Recommended local environment: Python `3.11+`.

```bash
python -m pip install -e ".[dev]"
```

Run a simulator-free local method check with no IBM credentials:

```bash
python - <<'PY'
from qrope.automated_stage_gates import phase_margins, normalized_phase_label

margins = phase_margins(delta_a=1, delta_b=4)
print(margins)
print("label", normalized_phase_label(margins["score"]))
PY
```

IBM and Amazon Braket hardware reruns require separate cloud credentials and provider dependencies. The local method check and saved-packet verifier do not require hardware credentials.

Install IBM Runtime dependencies only when preparing a real hardware run:

```bash
python -m pip install -e ".[ibm]"
```

Install Amazon Braket dependencies only when preparing a Braket hardware run:

```bash
python -m pip install -e ".[braket]"
```

The current Amazon Braket adapter also shells out to the external `aws` executable for STS, Braket, and S3 operations. Install and configure AWS CLI v2 separately before attempting a Braket hardware run.

Verify the saved Stage 4 packet arithmetic from the published raw-count evidence:

```bash
python scripts/verify_stage4_hardware_packet.py
```

Expected verifier summary:

```json
{
  "pass": true,
  "provider": "ibm_runtime",
  "backend": "ibm_fez",
  "packet_id": "qrope-hardware-73c61893576297ff",
  "job_ids": ["d84jbq00bvlc73d4krr0"]
}
```

Verify the Stage 4 hardware sweep manifest:

```bash
python scripts/verify_stage4_hardware_sweep.py
```

This verifier recomputes metrics for the active sweep records whose packet/execution/evaluation artifacts are present. The current active sweep covers the committed IBM Fez product-state packet, IBM Fez CX packet, Amazon Braket/Rigetti product-state artifact, and Amazon Braket CX artifacts on Rigetti Cepheus, IQM Garnet, and IQM Emerald. The verifier is provider-aware: IBM records use `q1q0` bitstring decoding and Amazon Braket records use `q0q1` decoding as declared in the manifest. Additional IBM backends and Amazon Braket/IonQ are documented as deferred or excluded targets unless real raw-count artifacts are later added.

The default single-packet verifier output is checked in CI against the README expected summary:

```bash
python scripts/check_readme_verifier_output.py
```

Audit the earlier Braket CX generic-decoder failure from saved raw counts:

```bash
python scripts/diagnose_stage4_cx_portability.py
```

The diagnostic documents why the earlier generic `q1q0` Braket CX classification was corrected in the provider-aware sweep verifier.

Estimate the local classical recomputation work for the committed Stage 4 sweep:

```bash
python scripts/estimate_stage4_classical_compute_cost.py
```

This emits `logs/automated_stage_gates/stage4_classical_compute_cost/`. The estimate is a static local verifier diagnostic, not provider billing reconstruction and not a hardware queue-time predictor.

Preregister future Stage 4 replication row sets without submitting hardware:

```bash
python scripts/preregister_stage4_replication_packets.py
```

This emits `logs/automated_stage_gates/stage4_preregistered_replication_packets/`. These artifacts are future-run controls, not new hardware evidence.

Prepare provider bitstring calibration packet specs:

```bash
python scripts/prepare_stage4_bitstring_calibration_packets.py
python scripts/verify_stage4_bitstring_calibration.py
```

The verifier currently fails with `missing-evidence` until real known-state calibration counts are supplied. This is intentional and prevents treating planned calibration as completed calibration.

Run the deterministic Stage 5 attention-scoring baselines:

```bash
python scripts/run_stage5_attention_baselines.py
```

Stage 5 compares the phase-wrap scoring rule against mod-24 lookup, `m8`/`m12`/`m8*m12`, a shallow regression tree, RoPE-style, sinusoidal, and ALiBI-style attention-scoring baselines. The current synthetic label is exactly recoverable by mod-24 lookup and the direct `m8*m12` feature baseline, so this closes the requested baseline gap but does not support transformer-scale superiority.

Run the deterministic Stage 6 toy downstream attention benchmark:

```bash
python scripts/run_stage6_downstream_attention.py
```

Stage 6 is an oracle phase-feature sanity check: it mixes token/content compatibility with phase-wrap positional signal so mod-24 lookup and direct `m8/m12/m8*m12` baselines are no longer exact. On the fixed packet, `phasewrap_rope_attention` has the lowest MAE, while the claim remains limited to this toy downstream packet.

Run the deterministic Stage 7 four-layer toy transformer ablation:

```bash
python scripts/run_stage7_toy_transformer_ablation.py
```

Stage 7 swaps the PhaseWrap positional term into a four-layer attention-only toy transformer on a synthetic length-extrapolation retrieval task. On the fixed packet, `phasewrap_rope_4layer` has the best argmax retrieval ranking by top-1 and MRR, while `rope_4layer` is better on target-probability calibration. This remains a small synthetic ablation, not production transformer evidence.

Run the deterministic Stage 8 local Needle-style benchmark:

```bash
python scripts/run_stage8_needle_benchmark.py
```

Stage 8 compares PhaseWrap-RoPE against RoPE-like, ALiBI-like, sinusoidal, and no-position scoring rules on a phase-cued synthetic retrieval packet across five seeds and context lengths up to 1024. The result supports keeping the RoPE-replacement research lane open, but it is not a RULER score or production transformer result.

Run the deterministic Stage 9 trained positional-attention ablation:

```bash
python scripts/run_stage9_trained_transformer_ablation.py
```

Stage 9 is an executable subset of the trained-transformer plan. It trains matched decoder-style positional attention mechanisms across five seeds, short training contexts, and longer test contexts. On the phase-cued packet, `phasewrap_adapter` has the best mean MRR and top-1 accuracy. On the exact-offset passkey packet whose answer is not selected by the PhaseWrap score, `rope_relative` is strongest. This remains a compact trained positional-attention ablation, not a full language-model benchmark or proof that PhaseWrap-RoPE replaces RoPE.

Run the Stage 10 small decoder-only transformer ablation:

```bash
python scripts/run_stage10_small_decoder_transformer.py
```

Stage 10 trains a small one-block decoder-only single-head transformer with matched seeds, tasks, model shape, optimizer, and epochs. The task set now includes phase-cued retrieval, exact-offset passkey retrieval, and a tiny curated text-fact QA lane. The result is weak and near chance across the tested lanes; target probabilities are near uniform (`~0.007813`) and the included capacity probe does not show strong training-set fit. The artifact now reports calibration-sensitive metrics, including target-probability MAE, top-1 confidence, and expected calibration error. This is useful as a first full-transformer sanity check, not as evidence that PhaseWrap-RoPE improves transformers.

Run the deterministic Stage 11 score-theory analysis:

```bash
python scripts/run_stage11_phasewrap_theory.py
```

Stage 11 analyzes the fixed 8/12 score directly. It verifies mod-24 periodicity, translation invariance, mirrored aliases, context-length alias growth, period-pair tradeoffs, and exact small Fourier support `[1, 2, 3, 5]` over the mod-24 residue table. This is useful theory evidence for the score, not evidence that PhaseWrap-RoPE replaces RoPE in trained transformers.

Run the deterministic Stage 12 RULER-style retrieval benchmark:

```bash
python scripts/run_stage12_ruler_retrieval.py
```

Stage 12 uses passkey, multi-needle, and aggregation-style retrieval rows whose targets are not selected by the PhaseWrap score. On the fixed packet, RoPE-like and sinusoidal baselines solve the exact-offset retrieval task while `phasewrap_rope_8_12` does not. This is useful negative evidence for the current fixed score and clarifies that a stronger PhaseWrap positional mechanism is needed before making any RoPE-replacement claim.

Run the deterministic Stage 13 positional-adapter benchmark:

```bash
python scripts/run_stage13_positional_adapter.py
```

Stage 13 trains lightweight positional adapters on short Stage 12 contexts and evaluates on held-out length-1024 rows. The fixed `phasewrap_score` remains weak; `phasewrap_residual_adapter` improves ranking; `phasewrap_distance_adapter` matches `rope_relative` on top-1 and MRR but has lower target-probability mass. This is a mechanism clue, not a production transformer result.

Run the deterministic Stage 14 attention-readout benchmark:

```bash
python scripts/run_stage14_attention_readout.py
```

Stage 14 converts the Stage 12 retrieval rows into key-value attention-readout rows. `phasewrap_distance_adapter` again matches `rope_relative` on top-1 and MRR, while `rope_relative` has higher target value probability. This supports testing PhaseWrap-plus-distance inside a stronger small decoder, not a replacement claim.

Run the deterministic Stage 15 learned attention-readout benchmark:

```bash
python scripts/run_stage15_learned_attention.py
```

Stage 15 trains a one-hidden-layer scorer over each positional feature family on the Stage 14 key-value rows. `phasewrap_distance_adapter` leads top-1 and MRR on the held-out local packet, while `rope_relative` keeps higher target value probability. This is promising ranking evidence for a candidate adapter shape, not a production transformer result.

Run the deterministic Stage 16 learned attention stability benchmark:

```bash
python scripts/run_stage16_learned_attention_stability.py
```

Stage 16 reruns Stage 15 across five deterministic learned-scorer initialization seeds. `phasewrap_distance_adapter` remains at top-1 `1.0` and MRR `1.0` across all five runs, while `rope_relative` keeps higher target value probability. This is stability evidence for the local ranking result, not a full transformer claim.

Run the deterministic Stage 17 small decoder value-model benchmark:

```bash
python scripts/run_stage17_small_decoder_value_model.py
```

Stage 17 adds learned value embeddings and an output projection to the Stage 14 key-value rows. All tested methods are near chance, including PhaseWrap-plus-distance and RoPE-like scoring. This is negative evidence for the current compact decoder-style readout and points to optimization/capacity work before stronger replacement claims.

Run the deterministic Stage 18 value-output capacity probe:

```bash
python scripts/run_stage18_value_output_capacity.py
```

Stage 18 compares uniform attention with teacher-forced target attention through the same learned value-output path. Teacher forcing does not substantially fix train or test performance, so the current bottleneck is value-output capacity/optimization, not only positional attention.

Run the deterministic Stage 19 value-output hardening probe:

```bash
python scripts/run_stage19_value_output_hardening.py
```

Stage 19 keeps attention teacher-forced and hardens the value-output path with full-batch Adam and larger value embeddings. It fits train perfectly and reaches held-out top-1 around `0.50` to `0.53`, so the value-output bottleneck is improvable. This is not a PhaseWrap-versus-RoPE result because positional attention is bypassed.

Run the deterministic Stage 20 hardened positional value-model benchmark:

```bash
python scripts/run_stage20_hardened_positional_value_model.py
```

Stage 20 reintroduces learned positional attention with the hardened value-output path. All methods fit train, but held-out value retrieval favors `rope_relative` with top-1 `0.383333` and MRR `0.429275`; `phasewrap_distance_adapter` has top-1 `0.250000` and MRR `0.321470`. This is useful negative/mixed evidence for the current PhaseWrap adapter, not a replacement claim.

Run the deterministic Stage 21 hardened positional stability benchmark:

```bash
python scripts/run_stage21_hardened_positional_stability.py
```

Stage 21 reruns Stage 20 across five learned-parameter initialization seeds. `rope_relative` remains strongest with mean top-1 `0.376666` and mean MRR `0.421212`; `phasewrap_distance_adapter` has mean top-1 `0.286667` and mean MRR `0.339284`. This stabilizes the Stage 20 mixed/negative result.

Run the deterministic Stage 22 long-context retrieval benchmark:

```bash
python scripts/run_stage22_long_context_retrieval.py
```

Stage 22 extends the Stage 12 explicit retrieval rules to contexts up to `4096`. RoPE-like and sinusoidal scoring solve the packet with top-1 `1.0` and MRR `1.0`; fixed `phasewrap_rope_8_12` has top-1 `0.012500` and MRR `0.096153`. This is strong negative evidence for the fixed score on non-phase-cued long-context retrieval.

Run the deterministic Stage 23 long-context adapter benchmark:

```bash
python scripts/run_stage23_long_context_adapter.py
```

Stage 23 trains positional adapters on the Stage 22 long-context rows: train on `512`/`1024`, validate on `2048`, and test on `4096`. `phasewrap_distance_adapter` recovers top-1 `1.0` and MRR `1.0`, matching `rope_relative` on argmax ranking, while `rope_relative` keeps higher target probability mass (`0.910440` versus `0.600201`).

Run the deterministic Stage 24 long-context value-model benchmark:

```bash
python scripts/run_stage24_long_context_value_model.py
```

Stage 24 adds learned value embeddings and output projection to the Stage 22 long-context rows. All methods fit train, but held-out `4096` token value retrieval favors `rope_relative` with top-1 `0.350000` and MRR `0.399642`; the strongest PhaseWrap-derived result is `phasewrap_residual_adapter` with top-1 `0.133333` and MRR `0.221899`.

Run the deterministic Stage 25 long-context value-model stability benchmark:

```bash
python scripts/run_stage25_long_context_value_stability.py
```

Stage 25 reruns Stage 24 across five learned-parameter initialization seeds. `rope_relative` remains strongest with mean top-1 `0.383333` and mean MRR `0.426498`; the strongest PhaseWrap-derived result is `phasewrap_residual_adapter` with mean top-1 `0.073333` and mean MRR `0.120739`.

Run the deterministic Stage 26 compact key-value QA retrieval benchmark:

```bash
python scripts/run_stage26_compact_kv_qa.py
```

Stage 26 adds explicit content keys and distractor facts. On held-out `2048` token rows, `alibi`, `phasewrap_residual_adapter`, and `phasewrap_distance_adapter` tie at top-1 `0.950000` and MRR `0.975000`; `phasewrap_distance_adapter` has the highest mean target probability among those tied methods (`0.767915`). The fixed `phasewrap_score` remains weak.

Run the deterministic Stage 27 compact key-value transformer-bridge benchmark:

```bash
python scripts/run_stage27_compact_kv_transformer_bridge.py
```

Stage 27 trains a one-hidden-layer attention bridge over the Stage 26 candidate features across five model initialization seeds. On held-out `2048` token rows, `phasewrap_distance_adapter` and `alibi` tie at mean top-1 `0.950000` and mean MRR `0.975000`; `phasewrap_distance_adapter` has slightly higher mean target probability (`0.823006` versus `0.821886`). This is a compact bridge toward the roadmap, not a full decoder-only language-model benchmark.

Run the deterministic Stage 28 RULER-style attention-bridge benchmark:

```bash
python scripts/run_stage28_ruler_attention_bridge.py
```

Stage 28 trains a one-hidden-layer attention bridge directly on Stage 12 non-phase-cued passkey, multi-needle, and aggregation-style retrieval rows across five model initialization seeds. `phasewrap_distance_adapter` and `rope_relative` both reach mean top-1 `1.000000` and mean MRR `1.000000`; `rope_relative` keeps higher mean target probability (`0.704867` versus `0.518441`) and lower top-1 expected calibration error (`0.297454` versus `0.486407`). This is compact retrieval-bridge evidence, not a full decoder-only language-model benchmark.

Run the deterministic Stage 29 period-pair task audit:

```bash
python scripts/run_stage29_period_pair_task_audit.py
```

Stage 29 audits the Stage 11 period-pair grid on Stage 12 local and Stage 22 long-context non-phase-cued retrieval rows. No tested fixed period pair solves the retrieval packets: the best local top-1 is `8/24` at `0.045833`, and the best long-context top-1 is `9/15` at `0.016667`; default `8/12` has local top-1 `0.020833` and long top-1 `0.012500`.

Run the deterministic Stage 30 matched retrieval-bridge benchmark:

```bash
python scripts/run_stage30_matched_retrieval_bridge.py
```

Stage 30 reruns the Stage 28 non-phase-cued RULER-style retrieval bridge with equal feature width (`12`), hidden width (`10`), learned parameter count (`141`), optimizer, epochs, and five initialization seeds for every positional variant. `phasewrap_distance_adapter` and `rope_relative` both reach mean top-1 `1.000000` and mean MRR `1.000000`; `rope_relative` keeps higher mean target probability (`0.744078` versus `0.564161`) and lower expected calibration error (`0.260653` versus `0.446620`). This is matched retrieval-bridge evidence, not a full decoder-only language-model benchmark.

Run the deterministic Stage 31 full-context retrieval-attention benchmark:

```bash
python scripts/run_stage31_full_context_retrieval_attention.py
```

Stage 31 trains the same four learned attention parameters for every positional variant while every prefix position competes, not only preselected key candidates. On the Stage 12 non-phase-cued held-out rows, `rope_relative` reaches mean top-1 `1.000000`, mean MRR `1.000000`, and mean target probability `0.821104`. The current PhaseWrap variants are weak in this harder full-context setting: `phasewrap_bias` has mean top-1 `0.016667`, and `phasewrap_distance_adapter` has mean top-1 `0.000000`. This is negative standard-retrieval evidence for the current variants.

Run the deterministic Stage 32 full-context feature-bridge benchmark:

```bash
python scripts/run_stage32_full_context_feature_bridge.py
```

Stage 32 reruns the full-prefix setting with a one-hidden-layer feature bridge and equal feature width (`12`), hidden width (`10`), parameter count (`141`), optimizer, epochs, and five model seeds. `phasewrap_distance_adapter`, `phasewrap_multiscale_adapter`, and `rope_relative` all reach mean top-1 `1.000000` and mean MRR `1.000000`; `rope_relative` keeps higher mean target probability (`0.713026` versus `0.480310` for multiscale and `0.429075` for distance) and lower expected calibration error. This is constructive mechanism evidence, not a RoPE replacement claim.

Run the deterministic Stage 33 temperature-calibration audit:

```bash
python scripts/run_stage33_temperature_calibration.py
```

Stage 33 applies validation-selected post-hoc temperature scaling to the Stage 32 full-context feature bridge. `phasewrap_distance_adapter`, `phasewrap_multiscale_adapter`, and `rope_relative` all retain mean top-1 `1.000000` and mean MRR `1.000000`; temperature scaling improves target probability and ECE for all solved methods. `rope_relative` remains strongest on calibrated target probability (`0.993605`) and ECE (`0.006395`), followed by `phasewrap_multiscale_adapter` (`0.960102`, ECE `0.041080`) and `phasewrap_distance_adapter` (`0.917118`, ECE `0.084114`). This narrows but does not close the RoPE-facing probability/calibration gap.

Run the deterministic Stage 34 small-decoder value-bridge benchmark:

```bash
python scripts/run_stage34_small_decoder_value_bridge.py
```

Stage 34 moves the Stage 32/33 retrieval signal into a compact decoder-style value bridge with learned attention, learned value embeddings, and an output projection. `rope_relative` is strongest on the held-out value-token packet with top-1 `0.360000`, MRR `0.403972`, and mean target value probability `0.345612`. The strongest PhaseWrap-derived result is `phasewrap_distance_adapter` with top-1 `0.283333`, MRR `0.333489`, and mean target value probability `0.244297`; `phasewrap_multiscale_adapter` trails further. This is mixed-to-negative evidence for the current PhaseWrap adapters under a learned value-output bottleneck.

Run the deterministic Stage 35 value-bridge bottleneck diagnostic:

```bash
python scripts/run_stage35_value_bridge_bottleneck_diagnostic.py
```

Stage 35 teacher-forces target attention on the Stage 34 rows and trains only learned value embeddings plus output projection. The diagnostic reaches mean top-1 around `0.50-0.53` and mean target value probability around `0.49` across method labels. The recorded verdict is `value_output_partly_viable_attention_selection_still_primary`: the value-output path is partly viable but not solved, and learned attention/mechanism selection remains a major bottleneck.

Run the deterministic Stage 36 copy-value bridge benchmark:

```bash
python scripts/run_stage36_copy_value_bridge.py
```

Stage 36 hardens the value-output path by copying learned attention mass directly onto candidate value tokens. `rope_relative`, `phasewrap_multiscale_adapter`, and `phasewrap_distance_adapter` all reach top-1 `1.000000` and MRR `1.000000`; `rope_relative` keeps higher target value probability (`0.659427`) than `phasewrap_multiscale_adapter` (`0.510753`) and `phasewrap_distance_adapter` (`0.447922`). This suggests the Stage 34 weakness was substantially value-output coupling, while the probability-mass gap remains.

Run the deterministic Stage 37 copy-value temperature-calibration audit:

```bash
python scripts/run_stage37_copy_value_temperature_calibration.py
```

Stage 37 applies validation-selected post-hoc temperature scaling to the Stage 36 copy-value bridge. `rope_relative`, `phasewrap_multiscale_adapter`, and `phasewrap_distance_adapter` retain mean top-1 `1.000000` and mean MRR `1.000000`; calibration sharply improves target value probability for the PhaseWrap-derived adapters (`0.920368` for multiscale and `0.907215` for distance). `rope_relative` remains strongest on calibrated target probability (`0.998545`) and ECE (`0.001455`), so the probability-mass gap narrows but does not close.

Run the deterministic Stage 38 hardened decoder value-bridge benchmark:

```bash
python scripts/run_stage38_hardened_decoder_value_bridge.py
```

Stage 38 returns to learned value embeddings plus output projection with larger hidden/value capacity and longer Adam training. All methods fit train nearly perfectly, but held-out length generalization still favors `rope_relative` with top-1 `0.370000`, MRR `0.419859`, and target value probability `0.350489`. The strongest PhaseWrap-derived held-out result is `phasewrap_multiscale_adapter` with top-1 `0.306667`, MRR `0.358125`, and target value probability `0.213638`. This keeps the learned decoder-style value-output path as an open RoPE-favorable bottleneck.

Run the deterministic Stage 39 sequence decoder retrieval benchmark:

```bash
python scripts/run_stage39_sequence_decoder_retrieval.py
```

Stage 39 makes every prefix token compete in a compact sequence-style decoder diagnostic. Several positional methods fit short train rows, but all methods are near chance on held-out full-prefix length extrapolation. `phasewrap_multiscale_adapter` reaches train top-1 `0.973334` but only test top-1 `0.003333`; `rope_relative` reaches train top-1 `0.935000` but only test top-1 `0.010000`. This is a broader sequence-level generalization failure, not a RoPE win.

Run the deterministic Stage 40 sequence length-curriculum benchmark:

```bash
python scripts/run_stage40_sequence_length_curriculum.py
```

Stage 40 trains the all-prefix sequence decoder on lengths `128`, `256`, and `512`, validates on `1024`, and tests on `2048`. The broader curriculum does not repair held-out length generalization. `phasewrap_distance_adapter` is strongest on the weak `2048` test rows with top-1 `0.030000`, MRR `0.060933`, and target value probability `0.020555`; `phasewrap_multiscale_adapter` follows with top-1 `0.023333`. Absolute performance remains too weak for a promotion claim.

Run the deterministic Stage 41 pointer/copy sequence benchmark:

```bash
python scripts/run_stage41_pointer_copy_sequence.py
```

Stage 41 keeps the Stage 40 all-prefix length curriculum but replaces learned value-token output with a pointer/copy head that sums attention mass over observed prefix token IDs. This repairs held-out `2048` ranking for `rope_relative` and `phasewrap_multiscale_adapter`, both with top-1 `1.000000` and MRR `1.000000`; `phasewrap_distance_adapter` is near-perfect with top-1 `0.966667` and MRR `0.983333`. `rope_relative` remains strongest on target value probability (`0.999834`) and ECE (`0.000166`), so this is a constructive copy-head diagnostic rather than a RoPE-replacement claim.

Run the deterministic Stage 42 trainable pointer-generator sequence benchmark:

```bash
python scripts/run_stage42_trainable_pointer_generator_sequence.py
```

Stage 42 keeps the Stage 40/41 all-prefix curriculum but makes the copy-aware value path trainable by mixing copied prefix-token mass with a learned vocab distribution. `rope_relative` reaches test top-1 `1.000000`, MRR `1.000000`, and target value probability `0.937847`; `phasewrap_distance_adapter` reaches top-1 `0.966667`, MRR `0.983333`, and target probability `0.904314`; `phasewrap_multiscale_adapter` reaches top-1 `0.946667`, MRR `0.973333`, and target probability `0.880976`. The learned generator branch stays near uniform target mass, so this is a copy-aware trainable-output diagnostic rather than a solved free value-generation result.

Run the deterministic Stage 43 generator-hardened pointer sequence benchmark:

```bash
python scripts/run_stage43_generator_hardened_pointer_sequence.py
```

Stage 43 keeps the Stage 42 setup but adds an auxiliary generator-target loss. Generator target probability improves from near uniform to roughly `0.31` for the strongest methods, and mixed-output target probability rises to `0.975293` for `rope_relative`, `0.935594` for `phasewrap_multiscale_adapter`, and `0.924739` for `phasewrap_distance_adapter`. RoPE-like scoring remains strongest overall, and generator-only top-1 remains below `0.50`, so this is output-path hardening evidence rather than RoPE-replacement evidence.

## Reviewer path in 10 minutes

- Read the claim boundary in this README.
- Open [Quickstart and results summary](docs/publication/quickstart-results-summary-v1.md).
- Open [Repository paper v1](docs/publication/qrope-paper-v1.md).
- Inspect [Patent status note](docs/publication/patent-status-note-v1.md).
- Inspect the Stage 4 packet files under `logs/automated_stage_gates/stage4_hardware_packet/`.
- Run `python scripts/verify_stage4_hardware_packet.py`.
- Inspect `logs/automated_stage_gates/stage4_hardware_sweep/manifest.json`.
- Run `python scripts/verify_stage4_hardware_sweep.py`.
- Run `python scripts/estimate_stage4_classical_compute_cost.py`.
- Inspect `logs/automated_stage_gates/stage4_preregistered_replication_packets/manifest.json`.
- Run `python scripts/run_stage8_needle_benchmark.py` for the local RoPE-facing retrieval sanity check.
- Run `python scripts/run_stage9_trained_transformer_ablation.py` for the trained positional-attention ablation.
- Run `python scripts/run_stage10_small_decoder_transformer.py` for the small decoder-only transformer ablation.
- Run `python scripts/run_stage11_phasewrap_theory.py` for the score invariance and aliasing analysis.
- Run `python scripts/run_stage12_ruler_retrieval.py` for the stricter non-phase-cued retrieval benchmark.
- Run `python scripts/run_stage13_positional_adapter.py` for the trained positional-adapter follow-up.
- Run `python scripts/run_stage14_attention_readout.py` for the key-value attention-readout follow-up.
- Run `python scripts/run_stage15_learned_attention.py` for the learned attention-readout follow-up.
- Run `python scripts/run_stage16_learned_attention_stability.py` for the learned attention initialization-stability follow-up.
- Run `python scripts/run_stage17_small_decoder_value_model.py` for the learned value-embedding/output readout check.
- Run `python scripts/run_stage18_value_output_capacity.py` for the value-output capacity probe.
- Run `python scripts/run_stage19_value_output_hardening.py` for the hardened teacher-forced value-output probe.
- Run `python scripts/run_stage20_hardened_positional_value_model.py` for the hardened learned positional value-model comparison.
- Run `python scripts/run_stage21_hardened_positional_stability.py` for the five-initialization stability check.
- Run `python scripts/run_stage22_long_context_retrieval.py` for the long-context explicit retrieval stress test.
- Run `python scripts/run_stage23_long_context_adapter.py` for the trained long-context adapter benchmark.
- Run `python scripts/run_stage24_long_context_value_model.py` for the learned long-context value-model benchmark.
- Run `python scripts/run_stage25_long_context_value_stability.py` for the five-initialization long-context value-model stability check.
- Run `python scripts/run_stage26_compact_kv_qa.py` for the compact key-value QA retrieval benchmark.
- Run `python scripts/run_stage27_compact_kv_transformer_bridge.py` for the compact key-value transformer-bridge benchmark.
- Run `python scripts/run_stage28_ruler_attention_bridge.py` for the non-phase-cued RULER-style attention-bridge benchmark.
- Run `python scripts/run_stage29_period_pair_task_audit.py` for the period-pair task audit.
- Run `python scripts/run_stage30_matched_retrieval_bridge.py` for the matched feature-budget retrieval bridge.
- Run `python scripts/run_stage31_full_context_retrieval_attention.py` for the learned full-context retrieval-attention benchmark.
- Run `python scripts/run_stage32_full_context_feature_bridge.py` for the nonlinear full-context feature-bridge benchmark.
- Run `python scripts/run_stage33_temperature_calibration.py` for the post-hoc calibration audit.
- Run `python scripts/run_stage34_small_decoder_value_bridge.py` for the compact decoder-style value bridge.
- Run `python scripts/run_stage35_value_bridge_bottleneck_diagnostic.py` for the teacher-forced value-output diagnostic.
- Run `python scripts/run_stage36_copy_value_bridge.py` for the copy-value bridge.
- Run `python scripts/run_stage37_copy_value_temperature_calibration.py` for the copy-value calibration audit.
- Run `python scripts/run_stage38_hardened_decoder_value_bridge.py` for the hardened decoder value bridge.
- Run `python scripts/run_stage39_sequence_decoder_retrieval.py` for the all-prefix sequence decoder retrieval diagnostic.
- Run `python scripts/run_stage40_sequence_length_curriculum.py` for the sequence length-curriculum diagnostic.
- Run `python scripts/run_stage41_pointer_copy_sequence.py` for the pointer/copy sequence diagnostic.
- Run `python scripts/run_stage42_trainable_pointer_generator_sequence.py` for the trainable pointer-generator sequence diagnostic.
- Run `python scripts/run_stage43_generator_hardened_pointer_sequence.py` for the generator-hardened pointer sequence diagnostic.

## CI and test coverage

GitHub Actions runs the full unit suite on Python `3.11` and `3.12` without hardware-provider credentials:

```bash
pytest --cov=qrope --cov-report=term-missing --cov-report=xml
python scripts/check_readme_verifier_output.py
```

Coverage XML is uploaded as a workflow artifact. Optional provider SDK tests use mocks or skip paths when optional packages such as Perceval are not installed.

## Publication use

If you cite or discuss this work, use the bounded posture:

> PhaseWrap-RoPE is a phase-wrap positional scoring rule with two-qubit hardware readout and repository-backed deterministic evidence packets, including bounded Stage 4 real-hardware validation records.

Do not restate the result as a proof of broad quantum transformer superiority.

## Research Roadmap

The current release is ready for bounded repository/preprint publication. The next research work should be evidence-producing rather than claim-broadening:

| Priority | Work item | Purpose |
| --- | --- | --- |
| 1 | Attention-scoring benchmark against classical and positional baselines | Complete for the current synthetic task; simple exposed-feature baselines recover the label exactly. |
| 2 | DOI/preprint release hygiene | Make the current evidence package citable before further experiments change the repository state. |
| 3 | Toy downstream attention benchmark | Complete for a fixed synthetic packet; Stage 6 is best read as an oracle phase-feature sanity check. |
| 4 | Four-layer toy transformer ablation | Complete for a fixed synthetic length-extrapolation packet; PhaseWrap-RoPE has the best argmax ranking, while calibration remains mixed. |
| 5 | Local Needle-style retrieval benchmark | Complete for a phase-cued synthetic packet with five seeds, bootstrap intervals, and a period-pair ablation; use it to justify harder RoPE-facing benchmarks, not production claims. |
| 6 | Stage 9 trained transformer ablation | Executable subset complete for phase-cued and exact-offset passkey trained positional-attention tasks. Remaining work: full small decoder-only transformer training, non-synthetic retrieval or QA tasks, and richer calibration metrics. |
| 7 | Stage 10 full transformer ablation | Complete for a very small autograd-backed one-block decoder-only transformer with phase-cued, passkey, and tiny text-fact QA lanes, now with calibration-sensitive metrics. The result is near chance, so the next step is a stronger small-transformer implementation and harder non-synthetic retrieval or QA tasks. |
| 8 | Hardware witness hardening | Partly complete: intervals, local cost estimates, preregistered future replication packets, and provider bitstring calibration packet specs/verifier contract are present. Remaining work is real provider bit-order calibration execution and independent reruns across dates. |
| 9 | Theory of the score | Complete for the fixed 8/12 score: Stage 11 verifies mod-24 periodicity, translation invariance, mirror aliases, alias growth, period-pair tradeoffs, and exact small Fourier support. Remaining work is to connect those facts to task distributions and stronger trained mechanisms. |
| 10 | Stage 12 non-phase-cued retrieval benchmark | Complete for passkey, multi-needle, and aggregation-style local retrieval. RoPE-like and sinusoidal baselines solve the packet while the fixed 8/12 PhaseWrap score does not, making the remaining mechanism gap explicit. |
| 11 | Stage 13 positional-adapter benchmark | Complete for a train-short/test-long adapter on Stage 12 rows. PhaseWrap-plus-distance closes argmax ranking on this local packet, while RoPE remains better calibrated by target probability mass. |
| 12 | Stage 14 attention-readout benchmark | Complete for key-value readout rows derived from Stage 12. PhaseWrap-plus-distance again closes argmax value retrieval, while RoPE remains better calibrated by target value probability. |
| 13 | Stage 15 learned attention-readout benchmark | Complete for a one-hidden-layer scorer over Stage 14 rows. PhaseWrap-plus-distance leads argmax value retrieval, while RoPE remains stronger on target value probability. |
| 14 | Stage 16 learned attention stability benchmark | Complete for five initialization seeds. PhaseWrap-plus-distance preserves top-1/MRR leadership across the tested seeds, while RoPE remains stronger on target value probability. |
| 15 | Stage 17 small decoder value-model benchmark | Complete for learned value embeddings plus output projection. All methods are near chance, so the next transformer step is optimization/capacity hardening. |
| 16 | Stage 18 value-output capacity probe | Complete for uniform and teacher-forced attention. Teacher forcing does not substantially fix the learned value-output path, so capacity/optimization hardening is next. |
| 17 | Stage 19 value-output hardening probe | Complete for teacher-forced attention with Adam and larger embeddings. Train fit is solved and held-out retrieval improves, so the next step is reintroducing learned positional attention. |
| 18 | Stage 20 hardened positional value-model benchmark | Complete for learned positional attention using the hardened value-output path. `rope_relative` is strongest on the held-out packet; PhaseWrap-plus-distance remains behind. |
| 19 | Stage 21 hardened positional stability benchmark | Complete for five initialization seeds. `rope_relative` remains strongest by mean held-out top-1/MRR; PhaseWrap-plus-distance remains behind on MRR. |
| 20 | Stage 22 long-context retrieval benchmark | Complete for explicit passkey, multi-needle, and aggregation rules through 4096-token contexts. RoPE-like and sinusoidal rules solve it; fixed PhaseWrap 8/12 is weak. |
| 21 | Stage 23 long-context adapter benchmark | Complete for train-short/test-long adapters on Stage 22 rows. PhaseWrap-plus-distance matches RoPE-like top-1/MRR at 4096, while RoPE-like scoring keeps higher target probability mass. |
| 22 | Stage 24 long-context value-model benchmark | Complete for learned value embeddings/output projection on Stage 22 rows. RoPE-like scoring is strongest on held-out value retrieval; PhaseWrap-derived adapters remain behind. |
| 23 | Stage 25 long-context value-model stability | Complete for five initialization seeds. RoPE-like scoring remains strongest by mean top-1/MRR; PhaseWrap-derived adapters remain behind. |
| 24 | Stage 26 compact key-value QA benchmark | Complete for explicit content-key retrieval rows. PhaseWrap-derived adapters match ALiBI-style top-1/MRR; fixed PhaseWrap scoring remains weak. |
| 25 | Stage 27 compact key-value transformer-bridge benchmark | Complete for five model initialization seeds on Stage 26 rows. PhaseWrap-plus-distance ties ALiBI-style top-1/MRR and slightly leads target probability on this compact bridge; this is not full transformer evidence. |
| 26 | Stage 28 RULER-style attention-bridge benchmark | Complete for five model initialization seeds on Stage 12 rows. PhaseWrap-plus-distance matches RoPE-like top-1/MRR on this compact non-phase-cued retrieval bridge, while RoPE-like scoring keeps stronger probability/calibration metrics. |
| 27 | Stage 29 period-pair task audit | Complete for the Stage 11 period-pair grid on local and long-context retrieval rows. Period-pair swaps alone do not solve the fixed-score retrieval gap. |
| 28 | Stage 30 matched retrieval-bridge benchmark | Complete for five model initialization seeds on Stage 12 rows with equal feature width and parameter count across methods. PhaseWrap-plus-distance matches RoPE-like top-1/MRR, while RoPE-like scoring keeps stronger probability/calibration metrics. |
| 29 | Stage 31 full-context retrieval-attention benchmark | Complete for five model initialization seeds on Stage 12 rows with every prefix position competing. RoPE-like scoring solves the held-out packet; current PhaseWrap variants are weak. |
| 30 | Stage 32 full-context feature-bridge benchmark | Complete for five model initialization seeds on Stage 12 rows with every prefix position competing. PhaseWrap distance and multiscale adapters recover top-1/MRR, while RoPE-like scoring remains stronger on probability/calibration. |
| 31 | Stage 33 temperature calibration audit | Complete for the Stage 32 bridge. Temperature scaling improves probability/ECE for all solved methods, but RoPE-like scoring remains strongest on calibrated probability/ECE. |
| 32 | Stage 34 small decoder value bridge | Complete for five model initialization seeds on Stage 14 key-value rows. RoPE-like scoring is strongest once learned value-token output is required; current PhaseWrap-derived adapters trail. |
| 33 | Stage 35 value-bridge bottleneck diagnostic | Complete for five model initialization seeds with teacher-forced target attention. Value output is partly viable but not solved; learned attention/mechanism selection remains a major bottleneck. |
| 34 | Stage 36 copy-value bridge | Complete for five model initialization seeds on Stage 14 key-value rows. PhaseWrap-derived adapters recover perfect top-1/MRR when value output copies candidate values, while RoPE-like scoring keeps higher target probability mass. |
| 35 | Stage 37 copy-value temperature calibration | Complete for five model initialization seeds on the Stage 36 bridge. PhaseWrap-derived adapters retain perfect top-1/MRR and sharply improve calibrated target probability, while RoPE-like scoring remains strongest on probability/ECE. |
| 36 | Stage 38 hardened decoder value bridge | Complete for five model initialization seeds on Stage 14 key-value rows. All methods fit train, but held-out length generalization still favors RoPE-like scoring over the PhaseWrap-derived adapters. |
| 37 | Stage 39 sequence decoder retrieval | Complete for five model initialization seeds on all-prefix sequence rows. Several methods fit train, but all methods collapse on held-out length extrapolation. |
| 38 | Stage 40 sequence length curriculum | Complete for five model initialization seeds with train lengths 128/256/512. The curriculum does not repair held-out length extrapolation; PhaseWrap-derived adapters lead weak 2048-token test rows. |
| 39 | Stage 41 pointer/copy sequence | Complete for five model initialization seeds with the Stage 40 curriculum and copy-style sequence output. RoPE-like and PhaseWrap multiscale both reach perfect 2048-token top-1/MRR, while RoPE-like scoring remains better calibrated. |
| 40 | Stage 42 trainable pointer-generator sequence | Complete for five model initialization seeds with copied prefix-token mass mixed by a learned gate with learned vocab output. Strong ranking mostly survives, but RoPE-like scoring remains best and the generator branch is weak. |
| 41 | Stage 43 generator-hardened pointer sequence | Complete for five model initialization seeds with auxiliary generator-target loss. Generator target probability improves, but RoPE-like scoring remains strongest and generator-only top-1 remains weak. |
| 42 | Stage 44 compact-diagnostic plateau audit | Complete over Stages 39-43. Decision: `BOUND_COMPACT_DIAGNOSTIC_PLATEAU`; compact diagnostics should not broaden the claim boundary. |
| 43 | Stage 45 matched decoder-only gate | Complete for a matched one-block decoder-only harness. Decision: `PROMOTION_NOT_SUPPORTED`; the model remains near chance and is not a reliable promotion discriminator. |
| 44 | Stage 46 decoder capacity hardening audit | Complete for longer training on the one-block harness. Decision: `CAPACITY_NOT_ESTABLISHED`; train fit remains insufficient for promotion. |
| 45 | Stage 47 Adam decoder generalization audit | Complete for Adam hardening on the one-block harness. Decision: `TRAIN_FIT_WITH_PARTIAL_GENERALIZATION`; tiny text-fact QA has a PhaseWrap-positive result, but retrieval does not generalize. |
| 46 | Stage 48 Adam decoder stability audit | Complete for five seeds. Decision: `TINY_QA_POSITIVE_NOT_PHASEWRAP_STABLE_RETRIEVAL_FAILED`; the Stage 47 PhaseWrap lead is not stable. |
| 47 | Stage 49 copy-decoder retrieval repair audit | Complete for five seeds. Decision: `COPY_DECODER_PARTIALLY_REPAIRS_RETRIEVAL`; copy output repairs exact-offset passkey for `rope_relative`, but PhaseWrap does not lead and phase-cued retrieval remains weak. |
| 48 | Stage 50 learned pointer-generator decoder audit | Complete for five seeds. Decision: `LEARNED_POINTER_GENERATOR_RETRIEVAL_REPAIR_FAILED`; learned attention/gating does not preserve the Stage 49 fixed-copy retrieval repair. |
| 49 | Stage 51 decoder-path plateau audit | Complete over Stages 45-50. Decision: `BOUND_DECODER_PATH_PLATEAU`; decoder-path repairs are bounded diagnostics, not promotion evidence. |
| 50 | Stage 52 two-block decoder feasibility audit | Complete for one seed. Decision: `TWO_BLOCK_TRAIN_FIT_WITHOUT_RETRIEVAL_GENERALIZATION`; capacity improves but retrieval remains failed. |
| 51 | Stage 53 two-block retrieval hardening audit | Complete for one seed. Decision: `TWO_BLOCK_RETRIEVAL_HARDENING_FAILED`; extra exposure/training does not repair retrieval. |
| 52 | Stage 54 attention-supervised two-block audit | Complete for one seed. Decision: `ATTENTION_SUPERVISION_RETRIEVAL_REPAIR_FAILED`; target-attention supervision does not repair held-out retrieval attention or top-1. |
| 53 | Stage 55 row-metadata cue-copy upper-bound audit | Complete for five seeds. Decision: `ROW_METADATA_CUE_COPY_UPPER_BOUND_SOLVES_RETRIEVAL_NOT_PROMOTION`; explicit cue-copy metadata solves retrieval for all methods, including `no_position`. |
| 54 | Stage 56 standard-input cue-copy audit | Complete for five seeds. Decision: `STANDARD_INPUT_CUE_COPY_PARTIAL_RETRIEVAL`; visible-token cue decoding repairs exact-offset only partially and phase-cued retrieval remains weak. |
| 55 | Stage 57 support-aware query-cue audit | Complete for five seeds. Decision: `SUPPORT_AWARE_QUERY_CUE_SOLVES_PHASE_CUED_NOT_PROMOTION`; support-aware query decoding solves phase-cued retrieval for `no_position` too. |
| 56 | Stage 58 pooled-train query support audit | Complete for five seeds. Decision: `POOLED_TRAIN_QUERY_SUPPORT_SOLVES_PHASE_CUED_NOT_PROMOTION`; pooled train lookup recovers the support map but solves for `no_position` too. |
| 57 | Stage 59 seed-local query support audit | Complete for five seeds. Decision: `SEED_LOCAL_QUERY_SUPPORT_PARTIAL_COVERAGE_SOLVES_NOT_PROMOTION`; seed-local support coverage is incomplete, fallback cue decoding crosses threshold, and `no_position` solves too. |
| 58 | Stage 60 support fallback strictness audit | Complete for five seeds. Decision: `FALLBACK_DEPENDENT_PHASE_CUED_RETRIEVAL_NOT_PROMOTION`; strict known-support decoding does not solve phase-cued retrieval. |
| 59 | Stage 61 support-complete two-block audit | Complete for five seeds. Decision: `SUPPORT_COMPLETE_TWO_BLOCK_CAPACITY_NOT_ESTABLISHED`; complete support coverage does not make the learned decoder fit. |
| 60 | Stage 62 long-training support-complete audit | Complete for five seeds. Decision: `LONG_TRAINING_SUPPORT_COMPLETE_CAPACITY_NOT_ESTABLISHED`; longer training improves fit but still misses capacity and retrieval generalization. |
| 61 | Stage 63 two-block copy-output capacity audit | Complete for five seeds. Decision: `TWO_BLOCK_COPY_OUTPUT_CAPACITY_WITHOUT_RETRIEVAL_GENERALIZATION`; copy output establishes train capacity but not held-out retrieval generalization. |
| 62 | Stage 64 two-block pointer-generator capacity audit | Complete for five seeds. Decision: `TWO_BLOCK_POINTER_GENERATOR_CAPACITY_WITHOUT_RETRIEVAL_GENERALIZATION`; learned copy/vocab mixture preserves capacity but not held-out retrieval generalization. |
| 63 | Stage 65 pointer-generator length-curriculum audit | Complete for five seeds. Decision: `POINTER_GENERATOR_LENGTH_CURRICULUM_WITHOUT_RETRIEVAL_GENERALIZATION`; adding length-40 rows does not repair retrieval. |
| 64 | Stage 66 positional-copy expert audit | Complete for five seeds. Decision: `POSITIONAL_COPY_EXPERT_WITHOUT_RETRIEVAL_GENERALIZATION`; direct method-bias copy expert preserves capacity but does not repair retrieval. |
| 65 | Stage 67 content-key retrieval audit | Complete for five seeds. Decision: `CONTENT_KEY_RETRIEVAL_SOLVABLE_FOR_ALL_METHODS_NOT_PROMOTION`; content-key retrieval solves for all methods, including `no_position`. |
| 66 | Stage 68 content-key auxiliary transfer audit | Complete for five seeds. Decision: `CONTENT_KEY_AUXILIARY_TRANSFER_WITHOUT_RETRIEVAL_GENERALIZATION`; content-key auxiliary training preserves capacity but does not transfer to original retrieval generalization. |
| 67 | Stage 69 original multitask pointer-generator audit | Complete for five seeds. Decision: `ORIGINAL_MULTITASK_POINTER_GENERATOR_WITHOUT_RETRIEVAL_GENERALIZATION`; training all original tasks together preserves capacity but does not repair retrieval. |
| 68 | Stage 70 strongest honest claim synthesis | Complete. Decision: `BOUND_STRONGEST_HONEST_CLAIM_WITH_RETRIEVAL_FAILURES`; current fair evidence supports a bounded compact/auditable mechanism claim, not RoPE replacement. |
| 69 | Stage 71 positional-bias copy upper-bound audit | Complete. Decision: `POSITIONAL_BIAS_COPY_PARTIAL_ORIGINAL_RETRIEVAL_UPPER_BOUND`; deterministic positional copy solves exact-offset for `rope_relative`, but not phase-cued retrieval. |
| 70 | Stage 72 phase-cued bias tie-support audit | Complete. Decision: `PHASE_CUED_TARGET_NOT_IN_PHASEWRAP_MAX_BIAS_SUPPORT`; PhaseWrap max-bias support misses the held-out phase-cued target. |
| 71 | Stage 73 phase-cued period-pair support audit | Complete. Decision: `PHASE_CUED_PERIOD_PAIR_SWEEP_DOES_NOT_REPAIR_SUPPORT`; the predeclared period-pair grid does not repair max-support. |
| 72 | Stage 74 leave-one-seed query-support audit | Complete. Decision: `LEAVE_ONE_SEED_QUERY_SUPPORT_SOLVES_PHASE_CUED_NOT_PROMOTION`; cross-seed visible query-support recovery solves phase-cued retrieval for `no_position` too. |
| 73 | Stage 75 learned query-support head audit | Complete. Decision: `LEARNED_QUERY_SUPPORT_HEAD_SOLVES_PHASE_CUED_NOT_PROMOTION`; learned visible-cue recovery solves phase-cued retrieval for `no_position` too. |
| 74 | Stronger decoder-only transformer | Redesign beyond Stage 75 enough to integrate visible-cue recovery into a matched decoder-only mechanism before evaluating positional-method promotion. |
| 75 | Larger or error-aware witnesses | Explore larger qubit witnesses or mitigation analysis after downstream and replication evidence justify the added complexity. |

The mod-8/mod-12 choice is a fixed first-release design: two wrapped residual bases with one-step thresholds at `pi/4` and `pi/6`, producing a cross-band product signal. Stage 8 now includes a release-local period-pair ablation in which `(8, 12)` is best on the synthetic phase-cued Needle-style packet. That supports the current design choice for this packet, but it is not a proof of global optimality.

The CX variant was chosen as the smallest entangling extension of the product-state witness: it preserves the two `RY` margin encodings, adds one `CX(q0 -> q1)`, and reads a target-qubit parity/product signal without changing the packet discipline. The full Stage 4 packet generation pipeline is already present in `src/qrope/automated_stage_gates.py` and exposed through the Stage 4 runner/verifier scripts; future work is to separate that path into a cleaner researcher-facing API without changing the recorded packets.

For roadmap clarity, the repository separates three tracks:

- the mathematical score, which is a classical modular phase feature;
- the transformer hypothesis, which remains unproven until trained-model ablations exist;
- the hardware witness, which audits small-circuit readout of the score and is not evidence of model advantage.

The next promotion gate is documented in [Next transformer benchmark roadmap](docs/research/q-rope-next-transformer-benchmark-roadmap-v1.md). Stage 75 shows that a learned visible query-support head solves the phase-cued lane for `no_position` too. The next useful work is integrating that recovery into a matched decoder-only mechanism before evaluating positional-method differences.

## Licensing and patent notice

Software in this repository is released under `AGPL-3.0-only`. Patent and IP-status boundaries are documented in [PATENTS.md](PATENTS.md) and [Patent status note](docs/publication/patent-status-note-v1.md).
