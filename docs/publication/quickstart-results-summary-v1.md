# PhaseWrap-RoPE Quickstart and Results Summary v1

Date: `2026-05-20`

Archive DOI: `10.5281/zenodo.20306786`

## Purpose

This page is the one-page reviewer entry point for the current bounded PhaseWrap-RoPE release. It summarizes what is present, what passes, what is excluded, and what research comes next.

Repository naming note: public materials use `PhaseWrap-RoPE`; internal imports and artifact IDs retain the existing `qrope` stem.

## Current Result

The active Stage 4 hardware sweep is machine-verifiable from committed packet, execution, raw-count, evaluation, and manifest artifacts. It reports six completed hardware records:

| Backend | Provider | Family | Shots | Rows | Witness MAE | Witness rank corr | Control MAE | Control rank corr | Outcome |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| IBM Fez | `ibm_runtime` | `two_qubit_zz_expectation_phase_wrap_v1` | 4096 | 16 | 0.018382 | 0.876558 | 0.217262 | -0.176940 | `hardware-positive` |
| Rigetti Cepheus-1-108Q | `amazon_braket` | `two_qubit_zz_expectation_phase_wrap_v1` | 1000 | 8 | 0.069901 | 0.786644 | 0.149995 | 0.121232 | `hardware-positive` |
| IBM Fez | `ibm_runtime` | `two_qubit_cx_parity_phase_wrap_v2` | 4096 | 16 | 0.021458 | 0.972455 | 0.212516 | -0.169318 | `hardware-positive` |
| Rigetti Cepheus-1-108Q | `amazon_braket` | `two_qubit_cx_parity_phase_wrap_v2` | 1000 | 8 | 0.061643 | 0.557668 | 0.194370 | -0.060616 | `hardware-positive` |
| IQM Garnet | `amazon_braket` | `two_qubit_cx_parity_phase_wrap_v2` | 1000 | 8 | 0.021719 | 0.981981 | 0.204370 | -0.060616 | `hardware-positive` |
| IQM Emerald | `amazon_braket` | `two_qubit_cx_parity_phase_wrap_v2` | 1000 | 8 | 0.021479 | 0.884995 | 0.210995 | -0.096986 | `hardware-positive` |

For every active completed record, the witness has lower MAE than the control and higher rank correlation than the control under the manifest-declared verifier. Amazon Braket records use `q0q1` bitstring decoding; IBM records use `q1q0`.

The default single-packet path `logs/automated_stage_gates/stage4_hardware_packet/` remains the reviewer entry point for the original IBM Fez product-state packet. The same run is also preserved as `logs/automated_stage_gates/stage4_hardware_packet_ibm_fez_20260517_pass/` so the sweep manifest can refer to an immutable named run directory.

## Reproduce

Install local development dependencies:

```bash
python -m pip install -e ".[dev]"
```

Verify the original single-packet hardware result:

```bash
python scripts/verify_stage4_hardware_packet.py
```

Verify the multi-platform hardware sweep:

```bash
python scripts/verify_stage4_hardware_sweep.py
```

Estimate local classical recomputation cost for the committed Stage 4 sweep:

```bash
python scripts/estimate_stage4_classical_compute_cost.py
```

Preregister future Stage 4 replication packet sets:

```bash
python scripts/preregister_stage4_replication_packets.py
```

Prepare and check provider bitstring calibration packet specs:

```bash
python scripts/prepare_stage4_bitstring_calibration_packets.py
python scripts/verify_stage4_bitstring_calibration.py
```

The default calibration verifier reports `missing-evidence` until real known-state calibration counts are supplied.

Audit the Braket CX bitstring-order correction:

```bash
python scripts/diagnose_stage4_cx_portability.py
```

These commands recompute from saved artifacts. They do not submit hardware jobs and do not require IBM, AWS, IonQ, Quandela, or AQT credentials.

Run the Stage 5 no-credential attention-scoring baselines:

```bash
python scripts/run_stage5_attention_baselines.py
```

This writes `logs/automated_stage_gates/stage5_attention_baselines/manifest.json`, `results.json`, and `summary.csv`.

Run the Stage 6 no-credential downstream attention benchmark:

```bash
python scripts/run_stage6_downstream_attention.py
```

This writes `logs/automated_stage_gates/stage6_downstream_attention/manifest.json`, `results.json`, and `summary.csv`.

Run the Stage 7 no-credential four-layer toy transformer ablation:

```bash
python scripts/run_stage7_toy_transformer_ablation.py
```

This writes `logs/automated_stage_gates/stage7_toy_transformer_ablation/manifest.json`, `results.json`, and `summary.csv`.

Run the Stage 8 no-credential local Needle-style benchmark:

```bash
python scripts/run_stage8_needle_benchmark.py
```

This writes `logs/automated_stage_gates/stage8_needle_benchmark/manifest.json`, `results.json`, `summary.csv`, and `period_pair_ablation.csv`.

Run the Stage 9 no-credential trained positional-attention ablation:

```bash
python scripts/run_stage9_trained_transformer_ablation.py
```

This writes `logs/automated_stage_gates/stage9_trained_transformer_ablation/manifest.json`, `results.json`, `summary.csv`, `per_seed_results.csv`, and `failed_runs.json`.

Run the Stage 10 small decoder-only transformer ablation:

```bash
python scripts/run_stage10_small_decoder_transformer.py
```

This writes `logs/automated_stage_gates/stage10_small_decoder_transformer/manifest.json`, `results.json`, `summary.csv`, `per_seed_results.csv`, and `failed_runs.json`. The current result is near chance across phase-cued retrieval, exact-offset passkey retrieval, and a tiny curated text-fact QA lane, with target probabilities near uniform (`~0.007813`). The artifact now includes target-probability MAE, top-1 confidence, and expected calibration error.

Run the Stage 11 score-theory analysis:

```bash
python scripts/run_stage11_phasewrap_theory.py
```

This writes `logs/automated_stage_gates/stage11_phasewrap_theory/manifest.json`, `results.json`, `alias_summary.csv`, `period_pair_summary.csv`, and `residue_score_table.csv`. The current result verifies that the fixed 8/12 score is a mod-24 periodic feature with translation invariance, mirror aliases, 10 distinct residue scores, alias growth with context length, and exact small Fourier support `[1, 2, 3, 5]`.

Run the Stage 12 no-credential RULER-style retrieval benchmark:

```bash
python scripts/run_stage12_ruler_retrieval.py
```

This writes `logs/automated_stage_gates/stage12_ruler_retrieval/manifest.json`, `results.json`, `summary.csv`, `task_summary.csv`, and `per_example_results.csv`. The current result is non-phase-cued: RoPE-like and sinusoidal baselines solve the fixed passkey/multi-needle/aggregation-style packet, while the fixed 8/12 PhaseWrap score does not.

Run the Stage 13 no-credential positional-adapter benchmark:

```bash
python scripts/run_stage13_positional_adapter.py
```

This writes `logs/automated_stage_gates/stage13_positional_adapter/manifest.json`, `results.json`, `summary.csv`, and `task_summary.csv`. The current result shows that `phasewrap_distance_adapter` matches `rope_relative` on held-out top-1 and MRR, while `rope_relative` has higher target-probability mass.

Run the Stage 14 no-credential attention-readout benchmark:

```bash
python scripts/run_stage14_attention_readout.py
```

This writes `logs/automated_stage_gates/stage14_attention_readout/manifest.json`, `results.json`, `summary.csv`, and `task_summary.csv`. The current result turns the Stage 12 rows into key-value readout rows and preserves the Stage 13 pattern: PhaseWrap-plus-distance matches RoPE-like top-1/MRR, while RoPE-like scoring has higher target value probability.

Run the Stage 15 no-credential learned attention-readout benchmark:

```bash
python scripts/run_stage15_learned_attention.py
```

This writes `logs/automated_stage_gates/stage15_learned_attention/manifest.json`, `results.json`, `summary.csv`, and `task_summary.csv`. The current result trains a one-hidden-layer scorer over each positional feature family. PhaseWrap-plus-distance leads held-out top-1/MRR, while RoPE-like scoring remains better on target value probability.

Run the Stage 16 no-credential learned attention stability benchmark:

```bash
python scripts/run_stage16_learned_attention_stability.py
```

This writes `logs/automated_stage_gates/stage16_learned_attention_stability/manifest.json`, `results.json`, `summary.csv`, and `per_run_results.csv`. The current result reruns Stage 15 across five learned-scorer initialization seeds. PhaseWrap-plus-distance keeps top-1 `1.0` and MRR `1.0` in all five runs, while RoPE-like scoring remains stronger on target value probability.

Run the Stage 17 no-credential small decoder value-model benchmark:

```bash
python scripts/run_stage17_small_decoder_value_model.py
```

This writes `logs/automated_stage_gates/stage17_small_decoder_value_model/manifest.json`, `results.json`, `summary.csv`, and `task_summary.csv`. The current result adds learned value embeddings and an output projection; all methods are near chance, so this is negative evidence for the compact decoder-style readout.

Run the Stage 18 no-credential value-output capacity probe:

```bash
python scripts/run_stage18_value_output_capacity.py
```

This writes `logs/automated_stage_gates/stage18_value_output_capacity/manifest.json`, `results.json`, and `summary.csv`. The current result compares uniform attention with teacher-forced target attention through the same learned value-output path. Teacher forcing does not substantially improve train or test performance, so the Stage 17 failure is not only a positional-attention issue.

Run the Stage 19 no-credential value-output hardening probe:

```bash
python scripts/run_stage19_value_output_hardening.py
```

This writes `logs/automated_stage_gates/stage19_value_output_hardening/manifest.json`, `results.json`, and `summary.csv`. The current result keeps attention teacher-forced and uses full-batch Adam with larger value embeddings. It fits the training rows perfectly and reaches held-out top-1 around `0.50` to `0.53`, so the value-output path is improvable. Because attention is teacher-forced, this is not a positional-method comparison.

Run the Stage 20 no-credential hardened positional value-model benchmark:

```bash
python scripts/run_stage20_hardened_positional_value_model.py
```

This writes `logs/automated_stage_gates/stage20_hardened_positional_value_model/manifest.json`, `results.json`, `summary.csv`, and `task_summary.csv`. The current result reintroduces learned positional attention with the hardened value-output path. All methods fit train, but held-out value retrieval favors RoPE-like scoring; PhaseWrap-plus-distance remains behind on this non-phase-cued packet.

Run the Stage 21 no-credential hardened positional stability benchmark:

```bash
python scripts/run_stage21_hardened_positional_stability.py
```

This writes `logs/automated_stage_gates/stage21_hardened_positional_stability/manifest.json`, `results.json`, `summary.csv`, and `per_run_results.csv`. The current result reruns Stage 20 across five learned-parameter initialization seeds. RoPE-like scoring remains strongest by mean held-out top-1/MRR; PhaseWrap-plus-distance remains behind on MRR.

Run the Stage 22 no-credential long-context retrieval benchmark:

```bash
python scripts/run_stage22_long_context_retrieval.py
```

This writes `logs/automated_stage_gates/stage22_long_context_retrieval/manifest.json`, `results.json`, `summary.csv`, `task_summary.csv`, `length_summary.csv`, and `per_example_results.csv`. The current result extends the Stage 12 explicit retrieval rules through `4096`-token contexts. RoPE-like and sinusoidal scoring solve the packet; fixed PhaseWrap 8/12 scoring is weak.

Run the Stage 23 no-credential long-context adapter benchmark:

```bash
python scripts/run_stage23_long_context_adapter.py
```

This writes `logs/automated_stage_gates/stage23_long_context_adapter/manifest.json`, `results.json`, `summary.csv`, and `task_summary.csv`. The current result trains adapters on Stage 22 rows, with train lengths `512`/`1024`, validation length `2048`, and test length `4096`. PhaseWrap-plus-distance matches RoPE-like top-1/MRR on the held-out rows, while RoPE-like scoring keeps higher target probability mass.

Run the Stage 24 no-credential long-context value-model benchmark:

```bash
python scripts/run_stage24_long_context_value_model.py
```

This writes `logs/automated_stage_gates/stage24_long_context_value_model/manifest.json`, `results.json`, `summary.csv`, and `task_summary.csv`. The current result adds learned value embeddings and output projection to the long-context rows. All methods fit train, but held-out `4096` token value retrieval favors RoPE-like scoring over the tested PhaseWrap-derived adapters.

Run the Stage 25 no-credential long-context value-model stability benchmark:

```bash
python scripts/run_stage25_long_context_value_stability.py
```

This writes `logs/automated_stage_gates/stage25_long_context_value_stability/manifest.json`, `results.json`, `summary.csv`, `per_run_results.csv`, and `weak_run_records.json`. The current result reruns Stage 24 across five initialization seeds. RoPE-like scoring remains strongest by mean top-1/MRR; PhaseWrap-derived adapters remain behind.

Run the Stage 26 no-credential compact key-value QA retrieval benchmark:

```bash
python scripts/run_stage26_compact_kv_qa.py
```

This writes `logs/automated_stage_gates/stage26_compact_kv_qa/manifest.json`, `results.json`, `summary.csv`, and `weak_runs.json`. The current result adds explicit content keys and distractor facts. PhaseWrap-derived adapters match ALiBI-style top-1/MRR on the held-out rows, while fixed PhaseWrap scoring remains weak.

Run the Stage 27 no-credential compact key-value transformer-bridge benchmark:

```bash
python scripts/run_stage27_compact_kv_transformer_bridge.py
```

This writes `logs/automated_stage_gates/stage27_compact_kv_transformer_bridge/manifest.json`, `results.json`, `summary.csv`, `per_run_results.csv`, and `weak_runs.json`. The current result trains a one-hidden-layer attention bridge over the Stage 26 candidate features across five model initialization seeds. `phasewrap_distance_adapter` and `alibi` tie at mean top-1 `0.950000` and mean MRR `0.975000`; `phasewrap_distance_adapter` has slightly higher mean target probability (`0.823006` versus `0.821886`). This remains a compact bridge, not a full decoder-only language-model result.

Run the Stage 28 no-credential RULER-style attention-bridge benchmark:

```bash
python scripts/run_stage28_ruler_attention_bridge.py
```

This writes `logs/automated_stage_gates/stage28_ruler_attention_bridge/manifest.json`, `results.json`, `summary.csv`, `per_run_results.csv`, `task_summary.csv`, and `weak_runs.json`. The current result trains a one-hidden-layer attention bridge directly on Stage 12 non-phase-cued passkey, multi-needle, and aggregation-style retrieval rows across five model initialization seeds. `phasewrap_distance_adapter` and `rope_relative` both reach mean top-1 `1.000000` and mean MRR `1.000000`; `rope_relative` keeps higher mean target probability (`0.704867` versus `0.518441`) and lower top-1 expected calibration error (`0.297454` versus `0.486407`). This remains compact retrieval-bridge evidence, not full decoder-only language-model validation.

Run the Stage 29 no-credential period-pair task audit:

```bash
python scripts/run_stage29_period_pair_task_audit.py
```

This writes `logs/automated_stage_gates/stage29_period_pair_task_audit/manifest.json`, `results.json`, `local_summary.csv`, `long_summary.csv`, `task_summary.csv`, and `length_summary.csv`. The current result audits the Stage 11 period-pair grid on Stage 12 local and Stage 22 long-context non-phase-cued retrieval rows. No tested fixed period pair solves the retrieval packets: the best local top-1 is `8/24` at `0.045833`, and the best long-context top-1 is `9/15` at `0.016667`.

## What This Supports

- A bounded phase-wrap scoring method using mod-8 and mod-12 wrapped residual margins.
- A deterministic evidence lane with frozen packets, raw counts, backend metadata, and offline recomputation.
- Small-circuit hardware validation that the witness/control ordering holds for the recorded packet/backend/date/calibration contexts listed above.
- A provider-aware Amazon Braket correction that is auditable from the saved raw counts.
- A deterministic Stage 4 classical recomputation cost estimate: `4096` static operations over `163072` recorded hardware shots, with zero incremental local verifier cost and no provider billing reconstruction.
- Preregistered future Stage 4 replication row sets for IBM-style and Amazon Braket-style product-state and CX reruns. These are no-hardware controls, not new hardware evidence.
- Provider bitstring calibration packet specs plus a verifier contract that fails as `missing-evidence` until real known-state counts are supplied.
- A deterministic Stage 5 attention-scoring baseline suite showing that the current synthetic label is exactly recoverable by mod-24 lookup and direct `m8*m12` exposed features.
- A deterministic Stage 6 oracle phase-feature sanity check where the target is not exactly recoverable by mod-24 lookup or direct phase features alone, and `phasewrap_rope_attention` has the lowest MAE on the fixed packet.
- A deterministic Stage 7 four-layer toy transformer ablation where `phasewrap_rope_4layer` has the best argmax retrieval ranking on a fixed synthetic length-extrapolation retrieval packet, while calibration remains mixed.
- A deterministic Stage 8 local Needle-style retrieval benchmark where `phasewrap_rope_8_12` has the best top-1 and MRR on a phase-cued synthetic packet across five seeds and context lengths up to 1024.
- A deterministic Stage 9 trained positional-attention ablation where `phasewrap_adapter` has mean test top-1 `0.668750` and mean test MRR `0.745096` on the phase-cued train-short/test-long packet, while `rope_relative` is strongest on the exact-offset passkey packet whose answer is not selected by the PhaseWrap score.
- A Stage 10 small decoder-only transformer ablation showing that this very small autograd-backed model does not yet produce a meaningful PhaseWrap advantage on the tested phase-cued, passkey, or tiny text-fact QA lanes; target probabilities remain near uniform, calibration-sensitive metrics are now reported, and the capacity probe also indicates weak training-set fit.
- A Stage 11 score-theory analysis showing that the fixed 8/12 score is compact and exactly auditable as a classical periodic feature, with explicit long-context aliasing limits.
- A deterministic Stage 12 RULER-style retrieval benchmark showing that exact-offset passkey, multi-needle, and aggregation-style retrieval currently favor RoPE-like and sinusoidal baselines over the fixed 8/12 PhaseWrap score.
- A deterministic Stage 13 positional-adapter benchmark showing that PhaseWrap-derived distance features can close argmax ranking on the local non-phase-cued packet, while RoPE-like scoring remains better on target-probability mass.
- A deterministic Stage 14 attention-readout benchmark showing the same PhaseWrap-plus-distance argmax result after the target is converted into value-token retrieval, while RoPE-like scoring remains better on target value probability.
- A deterministic Stage 15 learned attention-readout benchmark where PhaseWrap-plus-distance leads argmax value retrieval on the local held-out packet, while RoPE-like scoring remains better on target value probability.
- A deterministic Stage 16 learned attention stability benchmark where the PhaseWrap-plus-distance argmax result persists across five initialization seeds, while RoPE-like scoring remains better on target value probability.
- A deterministic Stage 17 small decoder value-model benchmark showing that the current learned value-embedding/output projection readout is near chance for every tested positional method.
- A deterministic Stage 18 value-output capacity probe showing that teacher-forced target attention does not substantially fix the current learned value-output path.
- A deterministic Stage 19 value-output hardening probe showing that full-batch Adam and larger value embeddings can fit train and improve held-out value-token retrieval under teacher-forced attention.
- A deterministic Stage 20 hardened positional value-model benchmark showing that the value-output bottleneck is no longer the blocker, and that RoPE-like scoring is stronger than the tested PhaseWrap adapters on the current held-out non-phase-cued packet.
- A deterministic Stage 21 five-initialization stability check showing the Stage 20 RoPE-like held-out advantage is stable on this packet.
- A deterministic Stage 22 long-context retrieval benchmark showing that RoPE-like and sinusoidal fixed scoring solve the explicit non-phase-cued packet through 4096-token contexts, while fixed PhaseWrap 8/12 scoring remains weak.
- A deterministic Stage 23 trained long-context adapter benchmark showing that PhaseWrap-plus-distance can recover argmax ranking through 4096-token held-out rows, while RoPE-like scoring remains stronger on target probability mass.
- A deterministic Stage 24 long-context value-model benchmark showing that adding learned value embeddings and output projection favors RoPE-like scoring on held-out value retrieval; the strongest PhaseWrap-derived method remains behind.
- A deterministic Stage 25 long-context value-model stability benchmark showing that the Stage 24 RoPE-like held-out advantage persists across five initialization seeds.
- A deterministic Stage 26 compact key-value QA retrieval benchmark showing that PhaseWrap-derived adapters can match ALiBI-style top-1/MRR on one explicit content-key packet, while fixed PhaseWrap scoring remains weak.
- A deterministic Stage 27 compact key-value transformer-bridge benchmark showing that PhaseWrap-plus-distance can tie ALiBI-style top-1/MRR and slightly lead target probability on one compact attention bridge across five model initialization seeds.
- A deterministic Stage 28 RULER-style attention-bridge benchmark showing that PhaseWrap-plus-distance can match RoPE-like top-1/MRR on one compact non-phase-cued retrieval bridge, while RoPE-like scoring keeps stronger probability and calibration metrics.
- A deterministic Stage 29 period-pair task audit showing that period-pair swaps alone do not solve the fixed-score retrieval gap on local or long-context non-phase-cued retrieval rows.

## What This Does Not Support

- broad quantum advantage;
- production transformer superiority;
- full transformer-scale validation;
- general cross-backend robustness;
- a claim that product-state readout is entanglement evidence;
- a claim that the result generalizes to unrun packets, dates, providers, or calibration windows.
- a claim that Stage 5 establishes production transformer or full transformer-scale superiority.
- a claim that Stage 6 establishes production transformer or full transformer-scale superiority.
- a claim that Stage 7 establishes production transformer or full transformer-scale superiority.
- a claim that Stage 8 is a standard RULER benchmark, production transformer result, or proof that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 9 is a full language-model benchmark, production transformer result, or proof that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 10 establishes production transformer superiority, a RoPE replacement result, or a full language-model benchmark.
- a claim that Stage 11 proves the 8/12 period pair is globally optimal or resolves long-context aliasing by itself.
- a claim that Stage 12 establishes production transformer superiority or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 13 establishes production transformer superiority or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 14 establishes production transformer superiority or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 15 establishes production transformer superiority or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 16 establishes production transformer superiority or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 17 establishes production transformer superiority or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 18 establishes production transformer superiority or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 19 establishes production transformer superiority, compares positional mechanisms, or proves that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 20 establishes production transformer superiority or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 21 establishes production transformer superiority or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 22 establishes production transformer superiority or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 23 establishes production transformer superiority or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 24 establishes production transformer superiority or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 25 establishes production transformer superiority or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 26 establishes production transformer superiority or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 27 establishes production transformer superiority, full decoder-only language-model validation, or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 28 establishes production transformer superiority, full decoder-only language-model validation, or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 29 proves a globally optimal period pair or that period-pair swaps alone make PhaseWrap-RoPE a RoPE replacement.

## Open Questions

- **Why mod-8 and mod-12?** They provide two distinct wrapped residual bases with one-step thresholds at `pi/4` and `pi/6`, producing a cross-band interaction through the product of signed margins. Stage 8 adds a release-local period-pair ablation where `(8, 12)` is best on the phase-cued Needle-style packet, and Stage 11 shows the fixed 8/12 score is exactly a mod-24 periodic feature with frequency support `[1, 2, 3, 5]`; this is still not a proof of global optimality.
- **Does PhaseWrap-RoPE help a classical ML task?** Stage 5 through Stage 29 are now present as bounded synthetic downstream checks. Stage 9 gives a compact trained positional-attention result with a useful split: PhaseWrap wins the phase-cued lane, while RoPE-relative wins the exact-offset passkey lane. Stage 10 adds a very small decoder-only transformer run, but it is near chance. Stage 12 adds a stricter non-phase-cued retrieval packet where RoPE-like and sinusoidal baselines solve the task and the fixed PhaseWrap score does not. Stages 13 and 14 show that a PhaseWrap-plus-distance adapter can close argmax ranking on local value-retrieval packets, but not target-probability mass. Stage 15 shows the learned PhaseWrap-plus-distance scorer can lead argmax value retrieval while RoPE remains stronger on probability mass. Stage 16 shows the ranking result is stable across the tested initialization seeds. Stage 17 shows the current learned value-output bottleneck is near chance for all methods. Stage 18 shows teacher-forced attention does not substantially fix that bottleneck with the compact optimizer. Stage 19 shows Adam and larger value embeddings can solve train fit and improve held-out value-token retrieval under teacher-forced attention. Stage 20 then reintroduces learned positional attention and favors RoPE-like scoring over the tested PhaseWrap adapters on held-out rows. Stage 21 confirms that ordering across five learned-parameter initialization seeds. Stage 22 extends explicit retrieval through 4096-token contexts and is strongly negative for the fixed PhaseWrap 8/12 score. Stage 23 trains adapters on those rows and shows PhaseWrap-plus-distance can recover held-out argmax ranking, but not RoPE-like target probability mass. Stage 24 adds learned value embeddings and output projection to the long-context rows; RoPE-like scoring is strongest and the PhaseWrap-derived adapters trail. Stage 25 confirms the Stage 24 RoPE-like held-out advantage across five initialization seeds. Stage 26 adds a compact content-key QA retrieval packet where PhaseWrap-derived adapters match ALiBI-style top-1/MRR. Stage 27 trains a compact attention bridge on the Stage 26 rows and preserves the PhaseWrap-plus-distance/ALiBI top-1 and MRR tie across five model initialization seeds. Stage 28 trains a compact attention bridge on Stage 12 non-phase-cued retrieval rows and shows PhaseWrap-plus-distance matching RoPE-like top-1/MRR, with lower target probability. Stage 29 shows period-pair swaps alone do not solve the fixed-score retrieval gap.
- **What would make the RoPE-replacement case stronger?** The next expansion should train a stronger matched small decoder-only transformer with RoPE, ALiBI, sinusoidal, no-position, and PhaseWrap positional mechanisms; evaluate train-short/test-long context extrapolation; include non-synthetic retrieval or QA tasks; run at least five seeds; and publish failed runs plus confidence intervals. Stage 12 and Stage 13 make clear that the fixed score alone is not enough; the useful direction is an explicit positional mechanism or adapter. The detailed gate is tracked in `docs/research/q-rope-next-transformer-benchmark-roadmap-v1.md`.
- **Why the CX variant?** It is the smallest entangling extension of the product-state witness: keep the two `RY` margin encodings, add one `CX(q0 -> q1)`, and read a target-qubit parity/product signal while preserving the same packet discipline.
- **Will the packet generation pipeline be reusable?** The current pipeline is open in `src/qrope/automated_stage_gates.py` and the Stage 4 runner/verifier scripts. A cleaner researcher-facing API is a packaging task, not new scientific evidence.
- **Should more hardware be run?** Yes, but as independent replication: new dates, new frozen packets, and cost-justified provider targets. IonQ was unavailable through Amazon Braket during the checked window; Quandela/AQT require separate execution and budget decisions.
- **How should the hardware be interpreted?** As an auditable witness for a classical phase score, not as quantum-enhanced attention. The sweep verifier now includes deterministic row-bootstrap and shot-resampling intervals from committed artifacts, Stage 4 has a deterministic local recomputation cost estimate, future replication packet sets are preregistered, and provider bitstring calibration specs are prepared; the next hardware hardening step is real provider calibration execution and independent reruns.

## Next Research Stages

| Stage | Goal | Promotion condition |
| --- | --- | --- |
| Stage 4 | Hardware evidence packaging | Complete for the active sweep. |
| Stage 5 | Attention-scoring baselines | Complete for the current synthetic task; the label is exactly recoverable by mod-24 lookup and direct `m8*m12` features. |
| Stage 6 | Toy downstream attention comparison | Complete for one fixed synthetic packet; best read as an oracle phase-feature sanity check. |
| Stage 7 | Four-layer toy transformer ablation | Complete for one fixed synthetic length-extrapolation packet; PhaseWrap-RoPE has the best argmax ranking, while calibration remains mixed. |
| Stage 8 | Local Needle-style retrieval benchmark | Complete for one phase-cued synthetic packet with five seeds, bootstrap intervals, and period-pair ablation. |
| Stage 9 | Trained transformer ablation | Executable subset complete for phase-cued and exact-offset passkey trained positional-attention packets; remaining work is full small decoder-only transformer training and non-synthetic retrieval or QA tasks. |
| Stage 10 | Full small decoder-only transformer ablation | Complete for a very small one-block decoder-only transformer with phase-cued, passkey, and tiny text-fact QA lanes plus calibration-sensitive metrics; result is near chance, so stronger small-transformer and harder non-synthetic tasks remain next. |
| Stage 11 | Theory of the score | Complete for the fixed 8/12 score: invariances, aliasing, period-pair tradeoffs, context-length behavior, and exact periodic-feature support are artifact-backed. Remaining work is task-distribution theory. |
| Stage 12 | RULER-style retrieval benchmark | Complete for a deterministic non-phase-cued passkey, multi-needle, and aggregation-style local packet. Result is negative for the fixed 8/12 PhaseWrap score against RoPE-like and sinusoidal baselines. |
| Stage 13 | Positional-adapter benchmark | Complete for a local train-short/test-long adapter on Stage 12 rows. PhaseWrap-plus-distance matches RoPE on top-1/MRR, while RoPE remains better on target-probability mass. |
| Stage 14 | Attention-readout benchmark | Complete for key-value readout rows derived from Stage 12. PhaseWrap-plus-distance matches RoPE on top-1/MRR, while RoPE remains better on target value probability. |
| Stage 15 | Learned attention-readout benchmark | Complete for a one-hidden-layer scorer over Stage 14 rows. PhaseWrap-plus-distance leads top-1/MRR, while RoPE remains better on target value probability. |
| Stage 16 | Learned attention stability benchmark | Complete for five initialization seeds. PhaseWrap-plus-distance preserves top-1/MRR leadership, while RoPE remains better on target value probability. |
| Stage 17 | Small decoder value-model benchmark | Complete for learned value embeddings plus output projection. Result is near chance for all methods, so optimizer/capacity hardening is next. |
| Stage 18 | Value-output capacity probe | Complete for uniform and teacher-forced attention through the learned value-output path. Teacher forcing does not substantially fix the bottleneck, so capacity/optimization hardening is next. |
| Stage 19 | Value-output hardening probe | Complete for teacher-forced attention with Adam and larger embeddings. Train fit is solved and held-out retrieval improves, so the next step is reintroducing learned positional attention. |
| Stage 20 | Hardened positional value-model benchmark | Complete for learned positional attention using the hardened value-output path. RoPE-like scoring is strongest on the held-out packet; PhaseWrap-plus-distance remains behind. |
| Stage 21 | Hardened positional stability benchmark | Complete for five initialization seeds. RoPE-like scoring remains strongest by mean top-1/MRR; PhaseWrap-plus-distance remains behind on MRR. |
| Stage 22 | Long-context retrieval benchmark | Complete through 4096-token contexts. RoPE-like and sinusoidal rules solve the explicit retrieval packet; fixed PhaseWrap 8/12 remains weak. |
| Stage 23 | Long-context adapter benchmark | Complete for trained adapters on Stage 22 rows. PhaseWrap-plus-distance matches RoPE-like top-1/MRR at 4096, while RoPE-like scoring keeps higher target probability mass. |
| Stage 24 | Long-context value-model benchmark | Complete for learned value embeddings/output projection on Stage 22 rows. RoPE-like scoring is strongest on held-out value retrieval; PhaseWrap-derived adapters remain behind. |
| Stage 25 | Long-context value-model stability | Complete for five initialization seeds. RoPE-like scoring remains strongest by mean top-1/MRR; PhaseWrap-derived adapters remain behind. |
| Stage 26 | Compact key-value QA retrieval | Complete for one explicit content-key packet. PhaseWrap-derived adapters match ALiBI-style top-1/MRR; fixed PhaseWrap scoring remains weak. |
| Stage 27 | Compact key-value transformer bridge | Complete for five model initialization seeds on the Stage 26 packet. PhaseWrap-plus-distance ties ALiBI-style top-1/MRR and slightly leads target probability on this compact bridge. |
| Stage 28 | RULER-style attention bridge | Complete for five model initialization seeds on Stage 12 retrieval rows. PhaseWrap-plus-distance matches RoPE-like top-1/MRR, while RoPE-like scoring keeps higher target probability. |
| Stage 29 | Period-pair task audit | Complete for Stage 11 period-pair grid on local and long-context retrieval rows. Period-pair swaps alone do not solve the fixed-score retrieval gap. |
| Stage 30 | Hardware witness hardening | Partly complete for intervals, local cost estimates, preregistered future replication row sets, and provider bitstring calibration specs/verifier contract. Remaining work is real provider calibration execution and independent reruns. |
| Stage 31 | Larger/error-aware witnesses | Add larger witness families or mitigation analysis only after downstream and replication evidence justify it. |
