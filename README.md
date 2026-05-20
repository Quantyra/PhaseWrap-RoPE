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
- `RoPE-facing benchmark posture`: Stage 8 adds a local phase-cued Needle-style retrieval packet, Stage 9 adds a trained decoder-style positional attention ablation, Stage 12 adds a stricter non-phase-cued RULER-style retrieval packet, Stage 13 tests trained positional adapters, Stage 14 turns the non-phase-cued rows into key-value attention readout, Stage 15 adds a one-hidden-layer learned attention scorer, Stage 16 checks initialization stability, Stage 17 adds learned value embeddings plus output projection, Stage 18 probes that value-output bottleneck with teacher-forced attention, Stage 19 hardens the teacher-forced value-output path, Stage 20 reintroduces learned positional attention with the hardened path, Stage 21 reruns that comparison across five initialization seeds, Stage 22 extends explicit retrieval to 4096-token contexts, Stage 23 trains adapters on those long-context rows, Stage 24 adds learned value embeddings/output projection to the long-context rows, Stage 25 reruns that long-context value model across five initialization seeds, Stage 26 adds a compact key-value QA retrieval packet with explicit content keys, Stage 27 trains a compact attention bridge on that packet across five model initialization seeds, Stage 28 trains a compact attention bridge directly on non-phase-cued RULER-style retrieval rows, and Stage 29 audits fixed period-pair choices on those retrieval rows. Stage 29 shows changing the fixed period pair alone does not close the retrieval gap; Stage 28 shows `phasewrap_distance_adapter` can match `rope_relative` top-1/MRR on a compact retrieval bridge while `rope_relative` keeps stronger probability/calibration metrics.
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
| 28 | Larger or error-aware witnesses | Explore larger qubit witnesses or mitigation analysis after downstream and replication evidence justify the added complexity. |

The mod-8/mod-12 choice is a fixed first-release design: two wrapped residual bases with one-step thresholds at `pi/4` and `pi/6`, producing a cross-band product signal. Stage 8 now includes a release-local period-pair ablation in which `(8, 12)` is best on the synthetic phase-cued Needle-style packet. That supports the current design choice for this packet, but it is not a proof of global optimality.

The CX variant was chosen as the smallest entangling extension of the product-state witness: it preserves the two `RY` margin encodings, adds one `CX(q0 -> q1)`, and reads a target-qubit parity/product signal without changing the packet discipline. The full Stage 4 packet generation pipeline is already present in `src/qrope/automated_stage_gates.py` and exposed through the Stage 4 runner/verifier scripts; future work is to separate that path into a cleaner researcher-facing API without changing the recorded packets.

For roadmap clarity, the repository separates three tracks:

- the mathematical score, which is a classical modular phase feature;
- the transformer hypothesis, which remains unproven until trained-model ablations exist;
- the hardware witness, which audits small-circuit readout of the score and is not evidence of model advantage.

The next promotion gate is documented in [Next transformer benchmark roadmap](docs/research/q-rope-next-transformer-benchmark-roadmap-v1.md). In short, the repository needs a matched small decoder-only transformer benchmark where only the positional mechanism changes, RoPE/ALiBI/sinusoidal/no-position/PhaseWrap variants share training controls, at least five seeds are reported with confidence intervals, and at least one task is not labeled by the PhaseWrap score.

## Licensing and patent notice

Software in this repository is released under `AGPL-3.0-only`. Patent and IP-status boundaries are documented in [PATENTS.md](PATENTS.md) and [Patent status note](docs/publication/patent-status-note-v1.md).
