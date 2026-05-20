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

Run the Stage 10 full-transformer preflight:

```bash
python scripts/run_stage10_small_decoder_transformer.py
```

This writes `logs/automated_stage_gates/stage10_small_decoder_transformer/manifest.json`, `preflight.json`, and `summary.csv`. In the current release environment, Stage 10 is blocked because there is insufficient free disk space to install the optional `transformer` dependency group.

## What This Supports

- A bounded phase-wrap scoring method using mod-8 and mod-12 wrapped residual margins.
- A deterministic evidence lane with frozen packets, raw counts, backend metadata, and offline recomputation.
- Small-circuit hardware validation that the witness/control ordering holds for the recorded packet/backend/date/calibration contexts listed above.
- A provider-aware Amazon Braket correction that is auditable from the saved raw counts.
- A deterministic Stage 5 attention-scoring baseline suite showing that the current synthetic label is exactly recoverable by mod-24 lookup and direct `m8*m12` exposed features.
- A deterministic Stage 6 oracle phase-feature sanity check where the target is not exactly recoverable by mod-24 lookup or direct phase features alone, and `phasewrap_rope_attention` has the lowest MAE on the fixed packet.
- A deterministic Stage 7 four-layer toy transformer ablation where `phasewrap_rope_4layer` has the best argmax retrieval ranking on a fixed synthetic length-extrapolation retrieval packet, while calibration remains mixed.
- A deterministic Stage 8 local Needle-style retrieval benchmark where `phasewrap_rope_8_12` has the best top-1 and MRR on a phase-cued synthetic packet across five seeds and context lengths up to 1024.
- A deterministic Stage 9 trained positional-attention ablation where `phasewrap_adapter` has mean test top-1 `0.668750` and mean test MRR `0.745096` on the phase-cued train-short/test-long packet, while `rope_relative` is strongest on the exact-offset passkey packet whose answer is not selected by the PhaseWrap score.
- A Stage 10 full-transformer preflight artifact that records the current blocker for a real small decoder-only transformer run: insufficient disk space for the optional `torch` dependency install.

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
- a claim that Stage 10 has produced model metrics before the optional transformer dependency is installed and the run artifacts exist.

## Open Questions

- **Why mod-8 and mod-12?** They provide two distinct wrapped residual bases with one-step thresholds at `pi/4` and `pi/6`, producing a cross-band interaction through the product of signed margins. Stage 8 adds a release-local period-pair ablation where `(8, 12)` is best on the phase-cued Needle-style packet; this is not a proof of global optimality.
- **Does PhaseWrap-RoPE help a classical ML task?** Stage 5 through Stage 9 are now present as bounded synthetic downstream checks. Stage 9 gives a compact trained positional-attention result with a useful split: PhaseWrap wins the phase-cued lane, while RoPE-relative wins the exact-offset passkey lane. The next milestone is a full small decoder-only transformer ablation where only the positional mechanism changes.
- **What would make the RoPE-replacement case stronger?** The next Stage 9 expansion should train full matched small decoder-only transformers with RoPE, ALiBI, sinusoidal, no-position, and PhaseWrap positional mechanisms; evaluate train-short/test-long context extrapolation; include non-synthetic retrieval or QA tasks; run at least five seeds; and publish failed runs plus confidence intervals.
- **Why the CX variant?** It is the smallest entangling extension of the product-state witness: keep the two `RY` margin encodings, add one `CX(q0 -> q1)`, and read a target-qubit parity/product signal while preserving the same packet discipline.
- **Will the packet generation pipeline be reusable?** The current pipeline is open in `src/qrope/automated_stage_gates.py` and the Stage 4 runner/verifier scripts. A cleaner researcher-facing API is a packaging task, not new scientific evidence.
- **Should more hardware be run?** Yes, but as independent replication: new dates, new frozen packets, and cost-justified provider targets. IonQ was unavailable through Amazon Braket during the checked window; Quandela/AQT require separate execution and budget decisions.
- **How should the hardware be interpreted?** As an auditable witness for a classical phase score, not as quantum-enhanced attention. The next hardware hardening step is provider bit-order calibration circuits, shot-noise intervals, independent reruns, preregistered packet sets, and classical compute timing/cost estimates.

## Next Research Stages

| Stage | Goal | Promotion condition |
| --- | --- | --- |
| Stage 4 | Hardware evidence packaging | Complete for the active sweep. |
| Stage 5 | Attention-scoring baselines | Complete for the current synthetic task; the label is exactly recoverable by mod-24 lookup and direct `m8*m12` features. |
| Stage 6 | Toy downstream attention comparison | Complete for one fixed synthetic packet; best read as an oracle phase-feature sanity check. |
| Stage 7 | Four-layer toy transformer ablation | Complete for one fixed synthetic length-extrapolation packet; PhaseWrap-RoPE has the best argmax ranking, while calibration remains mixed. |
| Stage 8 | Local Needle-style retrieval benchmark | Complete for one phase-cued synthetic packet with five seeds, bootstrap intervals, and period-pair ablation. |
| Stage 9 | Trained transformer ablation | Executable subset complete for phase-cued and exact-offset passkey trained positional-attention packets; remaining work is full small decoder-only transformer training and non-synthetic retrieval or QA tasks. |
| Stage 10 | Full small decoder-only transformer gate | Preflight artifact complete; currently blocked by insufficient disk space for optional `transformer` dependency installation. |
| Stage 11 | Hardware witness hardening | Add provider bit-order calibration circuits, shot-noise intervals, independent reruns, preregistered packets, and classical compute timing/cost estimates. |
| Stage 12 | Theory of the score | Formalize invariances, aliasing, period-pair tradeoffs, context-length behavior, kernel interpretations, and task distributions where the score helps or hurts. |
| Stage 13 | Larger/error-aware witnesses | Add larger witness families or mitigation analysis only after downstream and replication evidence justify it. |
