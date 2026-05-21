# PhaseWrap-RoPE Quickstart and Results Summary v1

Date: `2026-05-21`

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

Run the Stage 30 no-credential matched retrieval-bridge benchmark:

```bash
python scripts/run_stage30_matched_retrieval_bridge.py
```

This writes `logs/automated_stage_gates/stage30_matched_retrieval_bridge/manifest.json`, `results.json`, `summary.csv`, `per_run_results.csv`, `task_summary.csv`, and `weak_runs.json`. The current result reruns the Stage 28 bridge with equal feature width, hidden width, and learned parameter count across positional variants. `phasewrap_distance_adapter` and `rope_relative` both reach mean top-1 `1.000000` and mean MRR `1.000000`; `rope_relative` keeps higher mean target probability (`0.744078` versus `0.564161`) and lower expected calibration error (`0.260653` versus `0.446620`).

Run the Stage 31 no-credential full-context retrieval-attention benchmark:

```bash
python scripts/run_stage31_full_context_retrieval_attention.py
```

This writes `logs/automated_stage_gates/stage31_full_context_retrieval_attention/manifest.json`, `results.json`, `summary.csv`, `per_run_results.csv`, `task_summary.csv`, and `weak_runs.json`. The current result moves from candidate-only ranking to learned full-prefix attention. `rope_relative` solves the held-out packet with mean top-1 `1.000000`, mean MRR `1.000000`, and mean target probability `0.821104`; `phasewrap_bias` has mean top-1 `0.016667`, and `phasewrap_distance_adapter` has mean top-1 `0.000000`.

Run the Stage 32 no-credential full-context feature-bridge benchmark:

```bash
python scripts/run_stage32_full_context_feature_bridge.py
```

This writes `logs/automated_stage_gates/stage32_full_context_feature_bridge/manifest.json`, `results.json`, `summary.csv`, `per_run_results.csv`, `task_summary.csv`, and `weak_runs.json`. The current result uses a nonlinear full-prefix feature bridge. `phasewrap_distance_adapter`, `phasewrap_multiscale_adapter`, and `rope_relative` all reach mean top-1 `1.000000` and mean MRR `1.000000`; `rope_relative` keeps higher target probability and better calibration.

Run the Stage 33 no-credential temperature-calibration audit:

```bash
python scripts/run_stage33_temperature_calibration.py
```

This writes `logs/automated_stage_gates/stage33_temperature_calibration/manifest.json`, `results.json`, `summary.csv`, `per_run_results.csv`, and `weak_runs.json`. The current result applies validation-selected post-hoc temperature scaling to the Stage 32 bridge. `phasewrap_distance_adapter`, `phasewrap_multiscale_adapter`, and `rope_relative` retain mean top-1 `1.000000` and mean MRR `1.000000`; `rope_relative` remains strongest on calibrated target probability (`0.993605`) and ECE (`0.006395`), followed by `phasewrap_multiscale_adapter` (`0.960102`, ECE `0.041080`) and `phasewrap_distance_adapter` (`0.917118`, ECE `0.084114`).

Run the Stage 34 no-credential small-decoder value-bridge benchmark:

```bash
python scripts/run_stage34_small_decoder_value_bridge.py
```

This writes `logs/automated_stage_gates/stage34_small_decoder_value_bridge/manifest.json`, `results.json`, `summary.csv`, `per_run_results.csv`, `task_summary.csv`, and `weak_runs.json`. The current result trains learned attention plus learned value embeddings/output projection on Stage 14 key-value rows. `rope_relative` is strongest with top-1 `0.360000`, MRR `0.403972`, and mean target value probability `0.345612`; the strongest PhaseWrap-derived row is `phasewrap_distance_adapter` with top-1 `0.283333`, MRR `0.333489`, and mean target value probability `0.244297`.

Run the Stage 35 no-credential value-bridge bottleneck diagnostic:

```bash
python scripts/run_stage35_value_bridge_bottleneck_diagnostic.py
```

This writes `logs/automated_stage_gates/stage35_value_bridge_bottleneck_diagnostic/manifest.json`, `results.json`, `summary.csv`, `per_run_results.csv`, `task_summary.csv`, and `weak_runs.json`. The current result teacher-forces target attention on the Stage 34 rows and trains only learned value embeddings plus output projection. It reaches mean top-1 around `0.50-0.53` and mean target value probability around `0.49`; the recorded verdict is `value_output_partly_viable_attention_selection_still_primary`.

Run the Stage 36 no-credential copy-value bridge:

```bash
python scripts/run_stage36_copy_value_bridge.py
```

This writes `logs/automated_stage_gates/stage36_copy_value_bridge/manifest.json`, `results.json`, `summary.csv`, `per_run_results.csv`, `task_summary.csv`, and `weak_runs.json`. The current result copies learned attention mass directly onto candidate value tokens. `rope_relative`, `phasewrap_multiscale_adapter`, and `phasewrap_distance_adapter` all reach top-1 `1.000000` and MRR `1.000000`; `rope_relative` keeps higher target value probability (`0.659427`) than `phasewrap_multiscale_adapter` (`0.510753`) and `phasewrap_distance_adapter` (`0.447922`).

Run the Stage 37 no-credential copy-value temperature-calibration audit:

```bash
python scripts/run_stage37_copy_value_temperature_calibration.py
```

This writes `logs/automated_stage_gates/stage37_copy_value_temperature_calibration/manifest.json`, `results.json`, `summary.csv`, `per_run_results.csv`, `task_summary.csv`, and `weak_runs.json`. The current result applies validation-selected temperature scaling to the Stage 36 copy-value bridge. `rope_relative`, `phasewrap_multiscale_adapter`, and `phasewrap_distance_adapter` all retain top-1 `1.000000` and MRR `1.000000`; PhaseWrap-derived target value probability improves to `0.920368` for multiscale and `0.907215` for distance, while `rope_relative` remains strongest at `0.998545`.

Run the Stage 38 no-credential hardened decoder value bridge:

```bash
python scripts/run_stage38_hardened_decoder_value_bridge.py
```

This writes `logs/automated_stage_gates/stage38_hardened_decoder_value_bridge/manifest.json`, `results.json`, `summary.csv`, `train_summary.csv`, `validation_summary.csv`, `per_run_results.csv`, `task_summary.csv`, and `weak_runs.json`. The current result hardens the learned value-output path with hidden width `16`, value embedding width `64`, and `360` Adam epochs. All methods fit train, but held-out length generalization still favors `rope_relative` with top-1 `0.370000`, MRR `0.419859`, and target value probability `0.350489`; the strongest PhaseWrap-derived row is `phasewrap_multiscale_adapter` with top-1 `0.306667`, MRR `0.358125`, and target value probability `0.213638`.

Run the Stage 39 no-credential sequence decoder retrieval diagnostic:

```bash
python scripts/run_stage39_sequence_decoder_retrieval.py
```

This writes `logs/automated_stage_gates/stage39_sequence_decoder_retrieval/manifest.json`, `results.json`, `summary.csv`, `train_summary.csv`, `validation_summary.csv`, `per_run_results.csv`, `task_summary.csv`, and `weak_runs.json`. The current result makes all prefix tokens compete in a compact sequence-style decoder. Several methods fit train, but all methods are near chance on held-out length extrapolation: `phasewrap_multiscale_adapter` has train top-1 `0.973334` and test top-1 `0.003333`; `rope_relative` has train top-1 `0.935000` and test top-1 `0.010000`.

Run the Stage 40 no-credential sequence length-curriculum diagnostic:

```bash
python scripts/run_stage40_sequence_length_curriculum.py
```

This writes `logs/automated_stage_gates/stage40_sequence_length_curriculum/manifest.json`, `results.json`, `summary.csv`, `train_summary.csv`, `validation_summary.csv`, `per_run_results.csv`, `task_summary.csv`, and `weak_runs.json`. The current result trains the all-prefix compact sequence decoder on lengths `128`, `256`, and `512`, validates on `1024`, and tests on `2048`. The curriculum does not repair length extrapolation: `phasewrap_distance_adapter` is strongest on the weak `2048` test rows with top-1 `0.030000`, MRR `0.060933`, and target value probability `0.020555`.

Run the Stage 41 no-credential pointer/copy sequence diagnostic:

```bash
python scripts/run_stage41_pointer_copy_sequence.py
```

This writes `logs/automated_stage_gates/stage41_pointer_copy_sequence/manifest.json`, `results.json`, `summary.csv`, `train_summary.csv`, `validation_summary.csv`, `per_run_results.csv`, `task_summary.csv`, and `weak_runs.json`. The current result keeps the Stage 40 length curriculum and all-prefix token competition but replaces learned value-token output with copy-style output over observed prefix token IDs. `rope_relative` and `phasewrap_multiscale_adapter` both reach test top-1 `1.000000` and MRR `1.000000` at length `2048`; `phasewrap_distance_adapter` reaches top-1 `0.966667` and MRR `0.983333`. `rope_relative` remains strongest on target value probability (`0.999834`) and ECE (`0.000166`).

Run the Stage 42 no-credential trainable pointer-generator sequence diagnostic:

```bash
python scripts/run_stage42_trainable_pointer_generator_sequence.py
```

This writes `logs/automated_stage_gates/stage42_trainable_pointer_generator_sequence/manifest.json`, `results.json`, `summary.csv`, `train_summary.csv`, `validation_summary.csv`, `per_run_results.csv`, `task_summary.csv`, and `weak_runs.json`. The current result keeps the Stage 40/41 curriculum and all-prefix token competition, but mixes copied prefix-token mass with a learned vocab distribution through a trainable gate. At length `2048`, `rope_relative` reaches top-1 `1.000000` and MRR `1.000000`; `phasewrap_distance_adapter` reaches top-1 `0.966667` and MRR `0.983333`; `phasewrap_multiscale_adapter` reaches top-1 `0.946667` and MRR `0.973333`. The learned generator branch remains near uniform target mass, so the repair is still mainly copy-route driven.

Run the Stage 43 no-credential generator-hardened pointer sequence diagnostic:

```bash
python scripts/run_stage43_generator_hardened_pointer_sequence.py
```

This writes `logs/automated_stage_gates/stage43_generator_hardened_pointer_sequence/manifest.json`, `results.json`, `summary.csv`, `train_summary.csv`, `validation_summary.csv`, `per_run_results.csv`, `task_summary.csv`, and `weak_runs.json`. The current result keeps the Stage 42 setup but adds an auxiliary generator-target loss. Generator target probability improves to roughly `0.31` for the strongest positional methods, and mixed-output target probability rises, but `rope_relative` remains strongest overall with top-1 `1.000000`, MRR `1.000000`, target value probability `0.975293`, and ECE `0.024725`. `phasewrap_multiscale_adapter` reaches top-1 `0.970000`, MRR `0.985000`, and target value probability `0.935594`; `phasewrap_distance_adapter` reaches top-1 `0.966667`, MRR `0.983333`, and target probability `0.924739`. Generator-only top-1 remains below `0.50`, so this is output-path hardening evidence, not a solved free value-generation result.

Run the Stage 44 no-credential compact-diagnostic plateau audit:

```bash
python scripts/run_stage44_compact_diagnostic_plateau_audit.py
```

This writes `logs/automated_stage_gates/stage44_compact_diagnostic_plateau_audit/manifest.json`, `results.json`, and `summary.csv`. The audit reads the sealed Stage 39-43 summaries and records `BOUND_COMPACT_DIAGNOSTIC_PLATEAU`: Stage 40 is a real compact positive for PhaseWrap-derived adapters, but Stages 41-43 remain RoPE-favorable overall and the compact lane should not broaden the claim boundary.

Run the Stage 45 no-credential matched decoder-only gate:

```bash
python scripts/run_stage45_matched_decoder_only_gate.py
```

This writes `logs/automated_stage_gates/stage45_matched_decoder_only_gate/manifest.json`, `results.json`, `summary.csv`, `per_seed_results.csv`, and `failed_runs.json`. The gate records `PROMOTION_NOT_SUPPORTED`: the matched one-block decoder-only harness remains near chance, with target probability near uniform for all methods and tasks. PhaseWrap adapters are ranking-best by MRR on exact-offset passkey and tiny text-fact QA, but absolute accuracy and probability are too weak for promotion.

Run the Stage 46 no-credential decoder capacity hardening audit:

```bash
python scripts/run_stage46_decoder_capacity_hardening_audit.py
```

This writes `logs/automated_stage_gates/stage46_decoder_capacity_hardening_audit/manifest.json`, `results.json`, `summary.csv`, `per_run_results.csv`, and `failed_runs.json`. The audit records `CAPACITY_NOT_ESTABLISHED`: longer training improves the tiny text-fact QA lane, where PhaseWrap variants reach train/test top-1 `0.500000`, but the best train top-1 remains below the `0.750000` capacity threshold and retrieval lanes do not generalize.

Run the Stage 47 no-credential Adam decoder generalization audit:

```bash
python scripts/run_stage47_adam_decoder_generalization_audit.py
```

This writes `logs/automated_stage_gates/stage47_adam_decoder_generalization_audit/manifest.json`, `results.json`, `summary.csv`, `per_run_results.csv`, and `failed_runs.json`. The audit records `TRAIN_FIT_WITH_PARTIAL_GENERALIZATION`: Adam solves train fit and PhaseWrap variants lead tiny text-fact QA, but phase-cued retrieval and exact-offset passkey still fail held-out generalization.

Run the Stage 48 no-credential Adam decoder stability audit:

```bash
python scripts/run_stage48_adam_decoder_stability_audit.py
```

This writes `logs/automated_stage_gates/stage48_adam_decoder_stability_audit/manifest.json`, `results.json`, `summary.csv`, `per_run_results.csv`, and `failed_runs.json`. The audit records `TINY_QA_POSITIVE_NOT_PHASEWRAP_STABLE_RETRIEVAL_FAILED`: tiny text-fact QA remains positive across five seeds, but `rope_relative` and `no_position` lead, while both retrieval lanes still fail held-out top-1 for every method.

Run the Stage 49 no-credential copy-decoder retrieval repair audit:

```bash
python scripts/run_stage49_copy_decoder_retrieval_repair_audit.py
```

This writes `logs/automated_stage_gates/stage49_copy_decoder_retrieval_repair_audit/manifest.json`, `results.json`, `summary.csv`, `per_run_results.csv`, and `failed_runs.json`. The audit records `COPY_DECODER_PARTIALLY_REPAIRS_RETRIEVAL`: exact-offset passkey is repaired for `rope_relative`, tiny text-fact QA is easy for all methods, and phase-cued retrieval remains weak.

Run the Stage 50 no-credential learned pointer-generator decoder audit:

```bash
python scripts/run_stage50_learned_pointer_generator_decoder_audit.py
```

This writes `logs/automated_stage_gates/stage50_learned_pointer_generator_decoder_audit/manifest.json`, `results.json`, `summary.csv`, `per_run_results.csv`, and `failed_runs.json`. The audit records `LEARNED_POINTER_GENERATOR_RETRIEVAL_REPAIR_FAILED`: tiny text-fact QA remains positive, but the Stage 49 fixed-copy exact-offset repair does not survive learned attention and copy/vocab gating.

Run the Stage 51 no-credential decoder-path plateau audit:

```bash
python scripts/run_stage51_decoder_path_plateau_audit.py
```

This writes `logs/automated_stage_gates/stage51_decoder_path_plateau_audit/manifest.json`, `results.json`, and `summary.csv`. The audit records `BOUND_DECODER_PATH_PLATEAU`: Stages 45-50 are useful bottleneck diagnostics, but learned decoder retrieval generalization is not established and PhaseWrap does not lead a repaired retrieval lane.

Run the Stage 52 no-credential two-block decoder feasibility audit:

```bash
python scripts/run_stage52_two_block_decoder_feasibility_audit.py
```

This writes `logs/automated_stage_gates/stage52_two_block_decoder_feasibility_audit/manifest.json`, `results.json`, `summary.csv`, `per_run_results.csv`, and `failed_runs.json`. The audit records `TWO_BLOCK_TRAIN_FIT_WITHOUT_RETRIEVAL_GENERALIZATION`: train fit and tiny text-fact QA improve on a one-seed feasibility packet, but retrieval held-out top-1 remains zero.

Run the Stage 53 no-credential two-block retrieval hardening audit:

```bash
python scripts/run_stage53_two_block_retrieval_hardening_audit.py
```

This writes `logs/automated_stage_gates/stage53_two_block_retrieval_hardening_audit/manifest.json`, `results.json`, `summary.csv`, `per_run_results.csv`, and `failed_runs.json`. The audit records `TWO_BLOCK_RETRIEVAL_HARDENING_FAILED`: extra retrieval exposure and training budget still leave held-out retrieval top-1 at zero.

Run the Stage 54 no-credential attention-supervised two-block audit:

```bash
python scripts/run_stage54_attention_supervised_two_block_audit.py
```

This writes `logs/automated_stage_gates/stage54_attention_supervised_two_block_audit/manifest.json`, `results.json`, `summary.csv`, `per_run_results.csv`, and `failed_runs.json`. The audit records `ATTENTION_SUPERVISION_RETRIEVAL_REPAIR_FAILED`: target-attention supervision does not repair held-out retrieval target attention or top-1.

Run the Stage 55 no-credential row-metadata cue-copy upper-bound audit:

```bash
python scripts/run_stage55_row_metadata_cue_copy_upper_bound_audit.py
```

This writes `logs/automated_stage_gates/stage55_row_metadata_cue_copy_upper_bound_audit/manifest.json`, `results.json`, `summary.csv`, `per_run_results.csv`, and `failed_runs.json`. The audit records `ROW_METADATA_CUE_COPY_UPPER_BOUND_SOLVES_RETRIEVAL_NOT_PROMOTION`: explicit row metadata solves retrieval for every method, including `no_position`, so the row family is solvable but the result is not positional-method promotion evidence.

Run the Stage 56 no-credential standard-input cue-copy audit:

```bash
python scripts/run_stage56_standard_input_cue_copy_audit.py
```

This writes `logs/automated_stage_gates/stage56_standard_input_cue_copy_audit/manifest.json`, `results.json`, `summary.csv`, `per_run_results.csv`, and `failed_runs.json`. The audit records `STANDARD_INPUT_CUE_COPY_PARTIAL_RETRIEVAL`: visible-token cue decoding partially repairs exact-offset passkey for `rope_relative`, but phase-cued retrieval remains weak.

Run the Stage 57 no-credential support-aware query-cue audit:

```bash
python scripts/run_stage57_support_aware_query_cue_audit.py
```

This writes `logs/automated_stage_gates/stage57_support_aware_query_cue_audit/manifest.json`, `results.json`, `summary.csv`, `per_run_results.csv`, and `failed_runs.json`. The audit records `SUPPORT_AWARE_QUERY_CUE_SOLVES_PHASE_CUED_NOT_PROMOTION`: phase-cued retrieval is recoverable from the visible query token plus the known support prior, but `no_position` solves too.

Run the Stage 58 no-credential pooled-train query support audit:

```bash
python scripts/run_stage58_pooled_train_query_support_audit.py
```

This writes `logs/automated_stage_gates/stage58_pooled_train_query_support_audit/manifest.json`, `results.json`, `summary.csv`, `per_run_results.csv`, and `failed_runs.json`. The audit records `POOLED_TRAIN_QUERY_SUPPORT_SOLVES_PHASE_CUED_NOT_PROMOTION`: the support map is recovered from pooled train rows, but the repair still solves for `no_position`.

Run the Stage 59 no-credential seed-local query support audit:

```bash
python scripts/run_stage59_seed_local_query_support_audit.py
```

This writes `logs/automated_stage_gates/stage59_seed_local_query_support_audit/manifest.json`, `results.json`, `summary.csv`, `per_run_results.csv`, and `failed_runs.json`. The audit records `SEED_LOCAL_QUERY_SUPPORT_PARTIAL_COVERAGE_SOLVES_NOT_PROMOTION`: seed-local support coverage is incomplete on held-out phase-cued rows, fallback cue decoding crosses threshold, and the repair still solves for `no_position`.

Run the Stage 60 no-credential support fallback strictness audit:

```bash
python scripts/run_stage60_support_fallback_strictness_audit.py
```

This writes `logs/automated_stage_gates/stage60_support_fallback_strictness_audit/manifest.json`, `results.json`, `summary.csv`, `per_run_results.csv`, and `failed_runs.json`. The audit records `FALLBACK_DEPENDENT_PHASE_CUED_RETRIEVAL_NOT_PROMOTION`: phase-cued retrieval crosses threshold only with fallback decoding, not strict known-support decoding.

Run the Stage 61 no-credential support-complete two-block decoder audit:

```bash
python scripts/run_stage61_support_complete_two_block_audit.py
```

This writes `logs/automated_stage_gates/stage61_support_complete_two_block_audit/manifest.json`, `results.json`, `summary.csv`, `per_run_results.csv`, and `failed_runs.json`. The audit records `SUPPORT_COMPLETE_TWO_BLOCK_CAPACITY_NOT_ESTABLISHED`: every seed has complete phase-cued support coverage, but the learned vocab-softmax decoder still does not fit well enough for promotion.

Run the Stage 62 no-credential long-training support-complete decoder audit:

```bash
python scripts/run_stage62_long_training_support_complete_audit.py
```

This writes `logs/automated_stage_gates/stage62_long_training_support_complete_audit/manifest.json`, `results.json`, `summary.csv`, `per_run_results.csv`, and `failed_runs.json`. The audit records `LONG_TRAINING_SUPPORT_COMPLETE_CAPACITY_NOT_ESTABLISHED`: longer training improves support-complete train fit, with `phasewrap_adapter` reaching phase-cued train top-1 `0.533333`, but capacity remains below threshold and held-out retrieval remains unrepaired.

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
- A deterministic Stage 30 matched retrieval-bridge benchmark showing that the Stage 28 PhaseWrap-plus-distance top-1/MRR tie persists when feature width and learned parameter count are equalized, while RoPE-like scoring still has stronger probability and calibration metrics.
- A deterministic Stage 31 full-context retrieval-attention benchmark showing that the current PhaseWrap variants do not solve the harder full-prefix non-phase-cued retrieval packet, while RoPE-like scoring does.
- A deterministic Stage 32 full-context feature-bridge benchmark showing that richer PhaseWrap-derived adapters can recover full-prefix argmax retrieval, while RoPE-like scoring remains stronger on probability and calibration.
- A deterministic Stage 33 temperature-calibration audit showing that simple post-hoc calibration improves Stage 32 probability/ECE for all solved methods, while RoPE-like scoring remains strongest on calibrated probability/ECE.
- A deterministic Stage 34 compact decoder-style value bridge showing that RoPE-like scoring remains strongest once learned value-token output is required.
- A deterministic Stage 35 teacher-forced diagnostic showing that value output is partly viable but not solved, and learned attention/mechanism selection remains a major bottleneck.
- A deterministic Stage 36 copy-value bridge showing that PhaseWrap-derived adapters recover held-out top-1/MRR when value-output coupling is hardened, while RoPE-like scoring keeps higher probability mass.
- A deterministic Stage 37 copy-value temperature-calibration audit showing that scalar sharpening sharply improves PhaseWrap-derived target probability under hardened value output, while RoPE-like scoring remains strongest on calibrated probability/ECE.
- A deterministic Stage 38 hardened decoder value-bridge benchmark showing that all methods fit train with larger value-output capacity, but held-out length generalization still favors RoPE-like scoring.
- A deterministic Stage 39 sequence decoder retrieval diagnostic showing that all-prefix token competition causes severe held-out length failure for every tested positional method in the current compact decoder.
- A deterministic Stage 40 length-curriculum diagnostic showing that adding train length `512` does not repair held-out `1024`/`2048` generalization, although PhaseWrap-derived adapters lead the weak `2048` test rows.
- A deterministic Stage 41 pointer/copy sequence diagnostic showing that copy-style value output repairs held-out `2048` ranking for RoPE-like scoring and PhaseWrap multiscale, while RoPE-like scoring remains best calibrated.
- A deterministic Stage 42 trainable pointer-generator sequence diagnostic showing that learned copy/vocab mixing preserves much of the Stage 41 repair, while RoPE-like scoring remains best and the learned generator branch remains weak.
- A deterministic Stage 43 generator-hardened pointer sequence diagnostic showing that auxiliary generator supervision improves learned generator target probability, while RoPE-like scoring remains strongest overall and generator-only top-1 remains weak.
- A deterministic Stage 44 plateau audit showing that Stages 39-43 are bounded compact diagnostics, not RoPE-replacement evidence.
- A deterministic Stage 45 matched one-block decoder-only gate showing `PROMOTION_NOT_SUPPORTED`; the harness remains near chance, so it is negative promotion evidence rather than a useful positional-method discriminator.
- A deterministic Stage 46 capacity audit showing longer training does not make the one-block decoder reliable enough for positional-method promotion, while preserving weak PhaseWrap tiny text-fact QA positives.
- A deterministic Stage 47 Adam decoder audit showing train fit and a narrow PhaseWrap-positive tiny text-fact QA result, while preserving the retrieval-generalization failure.
- A deterministic Stage 48 five-seed Adam decoder stability audit showing tiny text-fact QA remains positive but the one-seed PhaseWrap lead is not stable.
- A deterministic Stage 49 copy-decoder retrieval repair audit showing that copy output repairs exact-offset passkey for `rope_relative`, while PhaseWrap does not lead and phase-cued retrieval remains weak.
- A deterministic Stage 50 learned pointer-generator decoder audit showing that the Stage 49 fixed-copy repair does not survive learned attention/gating and retrieval remains below threshold.
- A deterministic Stage 51 decoder-path plateau audit showing that Stages 45-50 are bounded diagnostics, not RoPE-replacement evidence.
- A deterministic Stage 52 two-block decoder feasibility audit showing that stronger decoder capacity can fit train rows and tiny text-fact QA, while retrieval generalization still fails.
- A deterministic Stage 53 two-block retrieval hardening audit showing that more retrieval exposure/training does not repair held-out retrieval in that path.
- A deterministic Stage 54 attention-supervised two-block audit showing that target-attention supervision does not repair held-out retrieval attention or top-1 in that path.
- A deterministic Stage 55 row-metadata cue-copy upper-bound audit showing that the rows are solvable when explicit cue metadata is handed to every method, including `no_position`.
- A deterministic Stage 56 standard-input cue-copy audit showing that visible-token cue decoding only partially repairs retrieval and does not solve phase-cued retrieval.
- A deterministic Stage 57 support-aware query-cue audit showing that the phase-cued signal is visible with a known support prior, while also solving for `no_position`.
- A deterministic Stage 58 pooled-train query support audit showing that the support map can be recovered from train rows, while still solving phase-cued retrieval for `no_position`.
- A deterministic Stage 59 seed-local query support audit showing that per-seed support coverage is incomplete on held-out phase-cued rows, while fallback cue decoding still crosses threshold for `no_position`.
- A deterministic Stage 60 support fallback strictness audit showing that the phase-cued result falls below threshold when unseen residues do not receive fallback cue help.
- A learned Stage 61 support-complete two-block audit showing that complete support coverage alone does not establish learned decoder capacity.
- A learned Stage 62 long-training support-complete audit showing that longer training improves train fit but still does not establish learned decoder capacity or held-out retrieval generalization.
- An active claim-boundary research goal: find the strongest honest claim PhaseWrap-RoPE can support under fair RoPE, ALiBI, sinusoidal, and no-position comparisons while preserving both positive evidence and failure modes.

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
- a claim that Stage 30 establishes production transformer superiority, full decoder-only language-model validation, or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 31 establishes production transformer superiority, full decoder-only language-model validation, or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 32 establishes production transformer superiority, full decoder-only language-model validation, or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 33 establishes production transformer superiority, full decoder-only language-model validation, or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 34 establishes production transformer superiority, full decoder-only language-model validation, or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 35 establishes production transformer superiority, full decoder-only language-model validation, or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 36 establishes production transformer superiority, full decoder-only language-model validation, or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 37 establishes production transformer superiority, full decoder-only language-model validation, or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 38 establishes production transformer superiority, full decoder-only language-model validation, or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 39 establishes production transformer superiority, full decoder-only language-model validation, or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 40 establishes production transformer superiority, full decoder-only language-model validation, or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 41 establishes production transformer superiority, full decoder-only language-model validation, or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 42 establishes production transformer superiority, full decoder-only language-model validation, or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 43 establishes production transformer superiority, full decoder-only language-model validation, solved free value generation, or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 44 establishes production transformer superiority, full decoder-only language-model validation, or that compact diagnostics can substitute for the matched decoder-only transformer gate.
- a claim that Stage 45 establishes production transformer superiority, full decoder-only language-model validation, or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 46 establishes production transformer superiority, full decoder-only language-model validation, or that the one-block decoder is a reliable positional-method discriminator.
- a claim that Stage 47 establishes production transformer superiority, full decoder-only language-model validation, or that tiny text-fact QA alone validates PhaseWrap-RoPE as a replacement.
- a claim that the Stage 47 one-seed PhaseWrap tiny text-fact QA lead is stable across seeds.
- a claim that Stage 49 establishes production transformer superiority, full decoder-only language-model validation, free learned value generation, or that PhaseWrap-RoPE replaces RoPE.
- a claim that Stage 50 establishes production transformer superiority, full decoder-only language-model validation, learned retrieval generation, or that PhaseWrap-RoPE replaces RoPE.
- a claim that the Stage 45-50 decoder path should broaden the claim boundary after the Stage 51 plateau audit.
- a claim that Stage 52 establishes production transformer superiority, satisfies the five-seed promotion standard, or establishes retrieval generalization.
- a claim that Stage 53 repairs retrieval or validates the two-block hardening path for promotion.
- a claim that Stage 54 attention supervision repairs retrieval, proves a value-output-only bottleneck, or validates the two-block auxiliary-loss path for promotion.
- a claim that Stage 55 is positional-method promotion evidence or that explicit row metadata is a standard decoder-only input feature.
- a claim that Stage 56 solves phase-cued retrieval or validates a learned decoder-only transformer.
- a claim that Stage 57 is positional-method promotion evidence or that the known support prior is learned by a matched decoder-only transformer.
- a claim that Stage 58 is positional-method promotion evidence or that a pooled lookup map is a matched decoder-only transformer.
- a claim that Stage 59 is positional-method promotion evidence, that seed-local lookup/fallback is a matched decoder-only transformer, or that held-out phase-cued support coverage is complete.
- a claim that Stage 60 is positional-method promotion evidence, that fallback decoding is learned decoder behavior, or that strict seed-local support solves held-out phase-cued retrieval.
- a claim that Stage 61 is positional-method promotion evidence or that complete support coverage alone establishes learned decoder capacity.
- a claim that Stage 62 is positional-method promotion evidence or that longer training alone establishes learned decoder capacity.

## Open Questions

- **Why mod-8 and mod-12?** They provide two distinct wrapped residual bases with one-step thresholds at `pi/4` and `pi/6`, producing a cross-band interaction through the product of signed margins. Stage 8 adds a release-local period-pair ablation where `(8, 12)` is best on the phase-cued Needle-style packet, and Stage 11 shows the fixed 8/12 score is exactly a mod-24 periodic feature with frequency support `[1, 2, 3, 5]`; this is still not a proof of global optimality.
- **Does PhaseWrap-RoPE help a classical ML task?** Stage 5 through Stage 62 are now present as bounded synthetic downstream checks. Stage 9 gives a compact trained positional-attention result with a useful split: PhaseWrap wins the phase-cued lane, while RoPE-relative wins the exact-offset passkey lane. Stage 10 adds a very small decoder-only transformer run, but it is near chance. Stage 12 adds a stricter non-phase-cued retrieval packet where RoPE-like and sinusoidal baselines solve the task and the fixed PhaseWrap score does not. Stages 13-43 preserve a mixed pattern: PhaseWrap-derived adapters can recover ranking in selected compact settings, while RoPE-like scoring often keeps stronger probability/calibration and the learned value-generation path remains weak. Stage 44 records the compact sequence and pointer-generator diagnostics as a bounded plateau. Stage 45 then runs a matched one-block decoder-only gate and records `PROMOTION_NOT_SUPPORTED`; Stage 46 confirms longer training still leaves the harness below capacity threshold; Stage 47 shows Adam solves train fit and gives a one-seed PhaseWrap-positive tiny text-fact QA result; Stage 48 shows that lead is not stable across five seeds and retrieval generalization still fails. Stage 49 shows copy-output repair can solve exact-offset passkey for RoPE-relative scoring, Stage 50 shows that repair does not survive learned pointer-generator attention/gating, Stage 51 records the decoder path as bounded, Stage 52 starts a stronger two-block decoder path, Stage 53 shows simple hardening of that path still fails retrieval, Stage 54 shows target-attention supervision still does not repair held-out retrieval attention or top-1, Stage 55 shows the row family is solvable only when explicit cue metadata is handed to all methods, Stage 56 shows visible-token cue decoding still does not solve phase-cued retrieval, Stage 57 shows a known support prior recovers phase-cued retrieval for `no_position` too, Stage 58 shows that support map is train-recoverable but still not positional-method evidence, Stage 59 shows seed-local held-out support coverage is incomplete while fallback cue decoding still crosses threshold for `no_position`, Stage 60 shows that strict known-support decoding does not preserve the phase-cued threshold crossing, Stage 61 shows complete support coverage still does not make the learned two-block decoder fit, and Stage 62 shows longer training improves fit but still misses capacity and held-out retrieval.
- **What would make the RoPE-replacement case stronger?** The next expansion should redesign the stronger matched small decoder-only transformer beyond Stage 62 with RoPE, ALiBI, sinusoidal, no-position, and PhaseWrap positional mechanisms; evaluate train-short/test-long context extrapolation; include non-synthetic retrieval or QA tasks; run at least five seeds; and publish failed runs plus confidence intervals. Stage 12 and Stage 13 make clear that the fixed score alone is not enough; Stage 55 makes clear that solving the rows with explicit metadata is not positional-method evidence; Stage 62 makes clear that longer training alone is not enough. The detailed gate is tracked in `docs/research/q-rope-next-transformer-benchmark-roadmap-v1.md`.
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
| Stage 30 | Matched retrieval bridge | Complete for five model initialization seeds on Stage 12 rows with equal feature width and parameter count. PhaseWrap-plus-distance matches RoPE-like top-1/MRR, while RoPE-like scoring keeps stronger probability/calibration metrics. |
| Stage 31 | Full-context retrieval attention | Complete for five model initialization seeds on Stage 12 rows. RoPE-like scoring solves the held-out full-prefix packet; current PhaseWrap variants are weak. |
| Stage 32 | Full-context feature bridge | Complete for five model initialization seeds on Stage 12 rows. PhaseWrap distance/multiscale adapters recover full-prefix top-1/MRR, while RoPE-like scoring keeps stronger probability/calibration metrics. |
| Stage 33 | Temperature calibration audit | Complete for the Stage 32 bridge. Temperature scaling improves probability/ECE, but RoPE-like scoring remains strongest on calibrated probability/ECE. |
| Stage 34 | Small decoder value bridge | Complete for five model initialization seeds on Stage 14 key-value rows. RoPE-like scoring is strongest; current PhaseWrap-derived adapters trail under the learned value-output bottleneck. |
| Stage 35 | Value-bridge bottleneck diagnostic | Complete for five model initialization seeds with teacher-forced target attention. Value output is partly viable but not solved; learned attention/mechanism selection remains a major bottleneck. |
| Stage 36 | Copy-value bridge | Complete for five model initialization seeds on Stage 14 key-value rows. PhaseWrap-derived adapters recover perfect top-1/MRR when value output copies candidate values, while RoPE-like scoring keeps higher target probability mass. |
| Stage 37 | Copy-value temperature calibration | Complete for five model initialization seeds on the Stage 36 bridge. PhaseWrap-derived adapters retain perfect top-1/MRR and sharply improve calibrated target probability, while RoPE-like scoring remains strongest on probability/ECE. |
| Stage 38 | Hardened decoder value bridge | Complete for five model initialization seeds on Stage 14 rows. All methods fit train with larger value-output capacity, but held-out length generalization still favors RoPE-like scoring. |
| Stage 39 | Sequence decoder retrieval | Complete for five model initialization seeds with all prefix tokens competing. Several methods fit train, but all tested methods collapse on held-out length extrapolation. |
| Stage 40 | Sequence length curriculum | Complete for five model initialization seeds with train lengths 128/256/512. The curriculum does not repair held-out 1024/2048 generalization; PhaseWrap-derived adapters lead the weak 2048 test rows. |
| Stage 41 | Pointer/copy sequence diagnostic | Complete for five model initialization seeds with the Stage 40 curriculum and copy-style sequence output. RoPE-like and PhaseWrap multiscale both reach perfect 2048-token top-1/MRR, while RoPE-like scoring remains best calibrated. |
| Stage 42 | Trainable pointer-generator sequence | Complete for five model initialization seeds with copied prefix-token mass mixed by a learned gate and learned vocab output. Strong ranking mostly survives, but RoPE-like scoring remains best and the generator branch is weak. |
| Stage 43 | Generator-hardened pointer sequence | Complete for five model initialization seeds with auxiliary generator-target loss. Generator target probability improves, but RoPE-like scoring remains strongest and generator-only top-1 remains weak. |
| Stage 44 | Compact-diagnostic plateau audit | Complete over Stages 39-43. Decision: `BOUND_COMPACT_DIAGNOSTIC_PLATEAU`; compact diagnostics should not broaden the claim boundary. |
| Stage 45 | Matched decoder-only gate | Complete for a matched one-block decoder-only harness. Decision: `PROMOTION_NOT_SUPPORTED`; the model remains near chance. |
| Stage 46 | Decoder capacity hardening audit | Complete for longer training on the one-block harness. Decision: `CAPACITY_NOT_ESTABLISHED`; train fit remains below threshold. |
| Stage 47 | Adam decoder generalization audit | Complete for Adam hardening on the one-block harness. Decision: `TRAIN_FIT_WITH_PARTIAL_GENERALIZATION`; tiny text-fact QA is PhaseWrap-positive, but retrieval does not generalize. |
| Stage 48 | Adam decoder stability audit | Complete across five seeds. Decision: `TINY_QA_POSITIVE_NOT_PHASEWRAP_STABLE_RETRIEVAL_FAILED`; tiny text-fact QA is positive but not PhaseWrap-led. |
| Stage 49 | Copy-decoder retrieval repair audit | Complete across five seeds. Decision: `COPY_DECODER_PARTIALLY_REPAIRS_RETRIEVAL`; exact-offset passkey is repaired for `rope_relative`, but PhaseWrap does not lead and phase-cued retrieval remains weak. |
| Stage 50 | Learned pointer-generator decoder audit | Complete across five seeds. Decision: `LEARNED_POINTER_GENERATOR_RETRIEVAL_REPAIR_FAILED`; learned attention/gating does not preserve the fixed-copy retrieval repair. |
| Stage 51 | Decoder-path plateau audit | Complete over Stages 45-50. Decision: `BOUND_DECODER_PATH_PLATEAU`; one-block and pointer-generator repairs are bounded diagnostics. |
| Stage 52 | Two-block decoder feasibility audit | Complete for one seed. Decision: `TWO_BLOCK_TRAIN_FIT_WITHOUT_RETRIEVAL_GENERALIZATION`; stronger capacity fits train/tiny QA but retrieval remains failed. |
| Stage 53 | Two-block retrieval hardening audit | Complete for one seed. Decision: `TWO_BLOCK_RETRIEVAL_HARDENING_FAILED`; extra exposure/training does not repair retrieval. |
| Stage 54 | Attention-supervised two-block audit | Complete for one seed. Decision: `ATTENTION_SUPERVISION_RETRIEVAL_REPAIR_FAILED`; target-attention supervision does not repair held-out retrieval attention or top-1. |
| Stage 55 | Row-metadata cue-copy upper-bound audit | Complete across five seeds. Decision: `ROW_METADATA_CUE_COPY_UPPER_BOUND_SOLVES_RETRIEVAL_NOT_PROMOTION`; explicit cue metadata solves rows for all methods, including `no_position`. |
| Stage 56 | Standard-input cue-copy audit | Complete across five seeds. Decision: `STANDARD_INPUT_CUE_COPY_PARTIAL_RETRIEVAL`; visible-token cue decoding partially repairs exact-offset but not phase-cued retrieval. |
| Stage 57 | Support-aware query-cue audit | Complete across five seeds. Decision: `SUPPORT_AWARE_QUERY_CUE_SOLVES_PHASE_CUED_NOT_PROMOTION`; known support prior recovers phase-cued retrieval for `no_position` too. |
| Stage 58 | Pooled-train query support audit | Complete across five seeds. Decision: `POOLED_TRAIN_QUERY_SUPPORT_SOLVES_PHASE_CUED_NOT_PROMOTION`; pooled train lookup recovers the support map but solves for `no_position` too. |
| Stage 59 | Seed-local query support audit | Complete across five seeds. Decision: `SEED_LOCAL_QUERY_SUPPORT_PARTIAL_COVERAGE_SOLVES_NOT_PROMOTION`; seed-local support coverage is incomplete and fallback cue decoding solves for `no_position` too. |
| Stage 60 | Support fallback strictness audit | Complete across five seeds. Decision: `FALLBACK_DEPENDENT_PHASE_CUED_RETRIEVAL_NOT_PROMOTION`; strict known-support decoding does not solve phase-cued retrieval. |
| Stage 61 | Support-complete two-block audit | Complete across five seeds. Decision: `SUPPORT_COMPLETE_TWO_BLOCK_CAPACITY_NOT_ESTABLISHED`; complete support coverage does not make the learned decoder fit. |
| Stage 62 | Long-training support-complete audit | Complete across five seeds. Decision: `LONG_TRAINING_SUPPORT_COMPLETE_CAPACITY_NOT_ESTABLISHED`; longer training improves fit but still misses capacity and held-out retrieval. |
| Next downstream gate | Stronger decoder-only transformer | Redesign beyond Stage 62 enough to establish learned capacity before testing positional-method promotion. |
| Hardware replication track | Hardware witness hardening | Partly complete for intervals, local cost estimates, preregistered future replication row sets, and provider bitstring calibration specs/verifier contract. Remaining work is real provider calibration execution and independent reruns. |
| Later hardware track | Larger/error-aware witnesses | Add larger witness families or mitigation analysis only after downstream and replication evidence justify it. |
