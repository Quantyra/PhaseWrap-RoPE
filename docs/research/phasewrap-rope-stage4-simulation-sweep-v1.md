# PhaseWrap-RoPE Stage 4 Simulation Sweep v1

Date: 2026-05-19

## BLUF

The active no-spend Stage 4 evidence lane is complete on free local simulators. It verifies the packet, circuit-family, raw-count, and offline-verifier mechanics for both witness families without submitting hardware jobs.

Run:

```bash
python scripts/run_stage4_simulation_sweep.py
python scripts/verify_stage4_simulation_sweep.py
```

Canonical artifacts:

- `logs/automated_stage_gates/stage4_simulation_sweep/manifest.json`
- `logs/automated_stage_gates/stage4_simulation_sweep/offline_verification.json`

## Claim Boundary

This is simulation evidence only. It does not establish hardware validation, broad quantum advantage, production transformer superiority, full transformer-scale validation, deployed-model performance improvement, or general cross-backend robustness.

No hardware execution is approved at this time. Any future hardware execution or rerun with estimated cost over `$100` requires explicit approval before submission.

## Verified Simulation Matrix

| Backend | Family | Shots | Rows | Witness MAE | Witness rank corr | Control MAE | Control rank corr | Outcome |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `local_ideal_simulator` | `two_qubit_zz_expectation_phase_wrap_v1` | 4096 | 16 | 0.000051 | 1.000000 | 0.229743 | -0.171995 | simulation-positive |
| `local_ideal_simulator` | `two_qubit_cx_parity_phase_wrap_v2` | 4096 | 16 | 0.000051 | 1.000000 | 0.229743 | -0.171995 | simulation-positive |
| `local_readout_bias_simulator` | `two_qubit_zz_expectation_phase_wrap_v1` | 4096 | 16 | 0.017787 | 1.000000 | 0.228767 | -0.187215 | simulation-positive |
| `local_readout_bias_simulator` | `two_qubit_cx_parity_phase_wrap_v2` | 4096 | 16 | 0.000051 | 1.000000 | 0.231697 | -0.187215 | simulation-positive |

## Interpretation

The simulation sweep is sufficient to finish the current research package around the method, packet format, two circuit families, raw-count recomputation, and verifier path. It is not a substitute for real hardware evidence.

The prior hardware sweep manifest remains intentionally strict and currently fails because the real raw-count artifacts are not present in the repository. That is the correct public state until real hardware artifacts are supplied and verified.
