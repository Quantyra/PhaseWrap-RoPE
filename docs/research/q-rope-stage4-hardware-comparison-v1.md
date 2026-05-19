# Q-RoPE Stage 4 Hardware Comparison v1

Date: 2026-05-18

## BLUF

The hardware run goals were completed. Both witness families were executed on all currently discovered hardware targets, and every run returned `PASS / hardware-positive`.

The product-state witness and the entangling CX witness both preserved the same qualitative pattern:

- witness metrics were substantially better than the control metrics
- control rank correlation remained negative on every backend
- IBM runs used 4096 shots
- IonQ `ionq_qpu` completed with 1024 shots, which is the exposed cap from the available provider metadata

## Visual Summary

![Stage 4 hardware comparison](../publication/figures/qrope-stage4-comparison-v1.svg)

The figure shows the same result pattern in a compact form:

- the witness bars stay low on MAE and high on rank correlation
- the control bars stay high on MAE and negative on rank correlation
- the entangling CX family improves rank correlation on the IBM backends relative to the product-state family

## Hardware Targets

| Provider | Backend | Shots used | Status | Outcome |
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

## Comparison

### Product-state vs entangling

The entangling CX witness was competitive with, and in some cases stronger than, the product-state witness on rank correlation. On IBM backends, the entangling witness reached:

- `0.925187` on `ibm_kingston`
- `0.960468` on `ibm_marrakesh`
- `0.981446` on `ibm_fez`

That is the cleanest hardware evidence that the CX variant is not merely decorative. It still needs careful claim wording, but it did execute and it did preserve the desired directionality.

### Backend deltas

| Backend | MAE delta, product | MAE delta, entangling | Rank delta, product | Rank delta, entangling |
| --- | ---: | ---: | ---: | ---: |
| `ibm_kingston` | 0.1718 | 0.1790 | 0.9326 | 1.1095 |
| `ibm_marrakesh` | 0.2183 | 0.2101 | 1.0639 | 1.1373 |
| `ibm_fez` | 0.2047 | 0.1973 | 1.1102 | 1.1508 |
| `ionq_qpu` | 0.2153 | 0.2138 | 1.0458 | 1.0854 |

Here the MAE delta is `control MAE - witness MAE`, so larger is better. The rank delta is `witness rank correlation - control rank correlation`, so larger is better.

### IBM vs IonQ

IBM delivered the most complete and directly comparable set of 4096-shot runs.

IonQ also completed both families successfully, but the run was constrained to 1024 shots by the backend exposure. The qualitative result still matched the IBM pattern:

- witness MAE remained low
- control MAE remained high
- control rank correlation stayed negative

### Family-level summary

| Family | Best witness MAE | Best witness rank corr | Worst control MAE | Worst control rank corr |
| --- | ---: | ---: | ---: | ---: |
| Product-state | 0.011859 | 0.940875 | 0.230163 | -0.184302 |
| Entangling CX | 0.015108 | 0.981446 | 0.229827 | -0.184302 |

### Goal status

The execution goals are complete:

1. run the existing product-state hardware witness on all available non-simulator hardware targets
2. run the entangling CX witness variant on the same set
3. record backend-specific artifacts and job IDs
4. preserve the 4096-shot target where supported

## Evidence Pointers

- [Product-state IBM/IonQ sweep logs](/C:/Users/Dan/Desktop/Projects/QuantyraQRope/logs/automated_stage_gates/stage4_hardware_sweep)
- [Stage 4 sweep runner](/C:/Users/Dan/Desktop/Projects/QuantyraQRope/scripts/run_stage4_hardware_sweep.py)

## Recommendation

The next step is documentation packaging, not more execution:

1. fold these run results into the publication docs
2. decide whether the entangling witness should be described as a confirmed result or a supporting extension
3. keep the 4096-shot wording for IBM and explicitly note the IonQ cap
