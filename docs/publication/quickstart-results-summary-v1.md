# PhaseWrap-RoPE Quickstart and Results Summary v1

Date: `2026-05-20`

## Purpose

This page is the one-page reviewer entry point for the current bounded PhaseWrap-RoPE release. It summarizes what is present, what passes, what is excluded, and what research comes next.

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

## What This Supports

- A bounded phase-wrap scoring method using mod-8 and mod-12 wrapped residual margins.
- A deterministic evidence lane with frozen packets, raw counts, backend metadata, and offline recomputation.
- Small-circuit hardware validation that the witness/control ordering holds for the recorded packet/backend/date/calibration contexts listed above.
- A provider-aware Amazon Braket correction that is auditable from the saved raw counts.

## What This Does Not Support

- broad quantum advantage;
- production transformer superiority;
- full transformer-scale validation;
- general cross-backend robustness;
- a claim that product-state readout is entanglement evidence;
- a claim that the result generalizes to unrun packets, dates, providers, or calibration windows.

## Open Questions

- **Why mod-8 and mod-12?** They provide two distinct wrapped residual bases with one-step thresholds at `pi/4` and `pi/6`, producing a cross-band interaction through the product of signed margins. Other period pairs remain an ablation target.
- **Does PhaseWrap-RoPE help a classical ML task?** Not yet shown in this release. The next scientific step is a toy transformer or attention-scoring benchmark against standard RoPE on length extrapolation or attention stability.
- **Should more hardware be run?** Yes, but as independent replication: new dates, new frozen packets, and cost-justified provider targets. IonQ was unavailable through Amazon Braket during the checked window; Quandela/AQT require separate execution and budget decisions.
- **Should the release go to arXiv or DOI archive?** Yes. The current repository is suitable for a bounded methods/evidence preprint and a Zenodo-style archived release after final release hygiene.

## Next Research Stages

| Stage | Goal | Promotion condition |
| --- | --- | --- |
| Stage 4 | Hardware evidence packaging | Complete for the active sweep. |
| Stage 5 | Toy downstream ML comparison | Compare PhaseWrap-RoPE/PhaseWrap scoring against RoPE on a concrete small task with fixed metrics. |
| Stage 6 | Independent hardware replication | Add new packet/date/backend records with raw counts and verifier output. |
| Stage 7 | Larger/error-aware witnesses | Add larger witness families or mitigation analysis only after Stage 5/6 evidence justifies it. |
