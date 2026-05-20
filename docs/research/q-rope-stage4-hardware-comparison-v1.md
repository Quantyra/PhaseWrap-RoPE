# PhaseWrap-RoPE Stage 4 Hardware Comparison v1

Date: 2026-05-18

## BLUF

The repository now treats the Stage 4 multi-platform sweep as a manifest-driven evidence lane. The narrative comparison below records the reported hardware sweep outcome, but first-class public evidence requires the tracked raw-count artifacts listed in:

```text
logs/automated_stage_gates/stage4_hardware_sweep/manifest.json
```

Run the offline verifier with:

```bash
python scripts/verify_stage4_hardware_sweep.py
```

If real sweep artifacts are absent, the verifier fails and lists the missing records. That failure is intentional; missing raw counts, job IDs, timestamps, or backend metadata must be supplied from real run records, not reconstructed from this report.

The active no-spend research lane is the free local simulation sweep:

```bash
python scripts/run_stage4_simulation_sweep.py
python scripts/verify_stage4_simulation_sweep.py
```

That simulation lane passes offline verification and should be used to finish the current research packaging before any hardware spend is reconsidered.

## Claim Boundary

The comparison may support only recorded packet/backend/date/calibration-specific outcomes after offline verification from raw counts. It does not establish broad quantum advantage, production transformer superiority, full transformer-scale validation, deployed-model performance improvement, or general cross-backend robustness.

Any future hardware execution or rerun with estimated cost over `$100` requires explicit approval before submission.

No hardware execution is approved at this time.

## Reported Hardware Targets

| Provider | Backend | Shots used | Reported status | Reported outcome |
| --- | --- | ---: | --- | --- |
| IBM Runtime | `ibm_kingston` | 4096 | PASS | hardware-positive |
| IBM Runtime | `ibm_marrakesh` | 4096 | PASS | hardware-positive |
| IBM Runtime | `ibm_fez` | 4096 | PASS | hardware-positive |
| IonQ | `ionq_qpu` | 1024 | PASS | hardware-positive |

## Product-State Witness

Circuit family: `two_qubit_zz_expectation_phase_wrap_v1`

| Backend | Witness MAE | Witness rank corr | Control MAE | Control rank corr |
| --- | ---: | ---: | ---: | ---: |
| `ibm_kingston` | 0.043376 | 0.781236 | 0.215599 | -0.151337 |
| `ibm_marrakesh` | 0.011859 | 0.879555 | 0.230110 | -0.184302 |
| `ibm_fez` | 0.015664 | 0.940875 | 0.220397 | -0.169318 |
| `ionq_qpu` | 0.014829 | 0.861459 | 0.230163 | -0.184302 |

## Entangling CX Witness

Circuit family: `two_qubit_cx_parity_phase_wrap_v2`

| Backend | Witness MAE | Witness rank corr | Control MAE | Control rank corr |
| --- | ---: | ---: | ---: | ---: |
| `ibm_kingston` | 0.026686 | 0.925187 | 0.205612 | -0.184302 |
| `ibm_marrakesh` | 0.015108 | 0.960468 | 0.225158 | -0.176810 |
| `ibm_fez` | 0.016162 | 0.981446 | 0.213417 | -0.169318 |
| `ionq_qpu` | 0.016037 | 0.908612 | 0.229827 | -0.176810 |

## Interpretation

The reported runs preserve the intended witness/control ordering: witness MAE is lower and witness rank correlation is higher than the additive control in each reported lane. The entangling CX family is therefore a reported supporting extension, not proof of quantum advantage or broad robustness.

Backend calibration, queue conditions, transpilation details, shot caps, and packet composition can affect future results. The proper review path is the manifest plus verifier, not this markdown table alone.

## Evidence Pointers

- Sweep manifest: `logs/automated_stage_gates/stage4_hardware_sweep/manifest.json`
- Sweep verifier: `scripts/verify_stage4_hardware_sweep.py`
- Sweep verifier output: `logs/automated_stage_gates/stage4_hardware_sweep/offline_verification.json`
- Stage 4 sweep runner: `scripts/run_stage4_hardware_sweep.py`

## Next Step

Finish the research package against the free simulation sweep first. Hardware remains deferred until the simulation-only output is reviewed and an explicit hardware budget decision is made.
