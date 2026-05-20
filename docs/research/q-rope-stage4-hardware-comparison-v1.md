# PhaseWrap-RoPE Stage 4 Hardware Comparison v1

Date: 2026-05-19

## BLUF

The active machine-verifiable hardware sweep records six completed artifacts: the original IBM Fez product-state hardware packet, an IBM Fez entangling-CX hardware-positive packet, an Amazon Braket/Rigetti product-state hardware-positive replication artifact, and three Amazon Braket CX artifacts on Rigetti Cepheus, IQM Garnet, and IQM Emerald. The sweep verifier is now provider-aware: IBM records use `q1q0` bitstring decoding and Amazon Braket records use `q0q1` decoding as declared in the manifest. Under that canonical verifier all six active records recompute as hardware-positive from committed raw counts. Additional IBM targets are deferred from the active sweep. Amazon Braket/IonQ is excluded from the active sweep because the checked IonQ devices were unavailable.

The completed active records preserve the same qualitative pattern:

- witness metrics were substantially better than the control metrics for the positive IBM Fez and Braket product-state records
- the IBM Fez control rank correlation remained negative
- the Braket/Rigetti control rank correlation remained below the witness rank correlation
- IBM Fez used 4096 shots
- IBM Fez CX used 4096 shots and preserved witness/control ordering
- Amazon Braket CX executions completed on Rigetti Cepheus, IQM Garnet, and IQM Emerald at 1000 shots per row and now verify as hardware-positive under manifest-declared `q0q1` decoding
- the CX portability diagnostic remains as audit evidence explaining why the earlier generic `q1q0` Braket CX decode was negative
- Amazon Braket/IonQ was checked on 2026-05-19 and was not run because `Forte-1` and `Forte-Enterprise-1` were `OFFLINE`, while `Aria-1` was `RETIRED`
- Amazon Braket/Rigetti completed the product-state lane with 1000 shots per row on `Cepheus-1-108Q`

## Visual Summary

![Stage 4 hardware comparison](../publication/figures/qrope-stage4-comparison-v1.svg)

The figure is historical comparison context. The canonical active sweep evidence is the manifest and verifier output under `logs/automated_stage_gates/stage4_hardware_sweep/`.

- the active IBM Fez and Braket records recompute from raw counts
- deferred IBM rows are not active public evidence until real artifacts are added

## Hardware Targets

| Provider | Backend | Shots used | Status | Outcome |
| --- | --- | ---: | --- | --- |
| IBM Runtime | `ibm_fez` | 4096 | PASS | hardware-positive |
| Amazon Braket | `Rigetti Cepheus-1-108Q` | 1000 | PASS | hardware-positive |
| Amazon Braket | `Rigetti Cepheus-1-108Q` CX | 1000 | PASS | hardware-positive |
| Amazon Braket | `IQM Garnet` CX | 1000 | PASS | hardware-positive |
| Amazon Braket | `IQM Emerald` CX | 1000 | PASS | hardware-positive |

## Product-State Witness

Circuit family: `two_qubit_zz_expectation_phase_wrap_v1`

| Backend | Witness MAE | Witness rank corr | Control MAE | Control rank corr |
| --- | ---: | ---: | ---: | ---: |
| `ibm_fez` | 0.018382 | 0.876558 | 0.217262 | -0.176940 |
| `rigetti_cepheus_1_108q` | 0.069901 | 0.786644 | 0.149995 | 0.121232 |

## Entangling CX Witness

Circuit family: `two_qubit_cx_parity_phase_wrap_v2`

The CX witness is now an active machine-verifiable hardware sweep family. The IBM Fez CX run used 16 rows and 4096 shots, completed as job `d86e50lg7okc73el0fog`, and verified as hardware-positive. Amazon Braket CX runs on Rigetti Cepheus, IQM Garnet, and IQM Emerald completed at 8 rows and 1000 shots per row. The canonical provider-aware verifier decodes Amazon Braket result keys as `q0q1`; under that manifest-declared convention all three Braket CX records verify as hardware-positive:

| Backend | Witness MAE | Witness rank corr | Control MAE | Control rank corr |
| --- | ---: | ---: | ---: | ---: |
| `ibm_fez` | 0.021458 | 0.972455 | 0.212516 | -0.169318 |
| `rigetti_cepheus_1_108q` | 0.061643 | 0.557668 | 0.194370 | -0.060616 |
| `iqm_garnet` | 0.021719 | 0.981981 | 0.204370 | -0.060616 |
| `iqm_emerald` | 0.021479 | 0.884995 | 0.210995 | -0.096986 |

A no-hardware ideal-count rehearsal remains present at `logs/automated_stage_gates/stage4_cx_rehearsal/ideal_counts_rehearsal/`. An earlier Amazon Braket/Rigetti CX attempt on 2026-05-19 timed out while queued and was cancelled; the later Rigetti, IQM Garnet, and IQM Emerald CX executions completed and are recorded as provider-aware positive hardware evidence.

The diagnostic at `docs/research/q-rope-stage4-cx-portability-diagnostic-v1.md` replays those same raw counts under alternate result-key conventions. It records that the earlier generic `q1q0` decode classified Braket CX as negative, while the now-canonical `q0q1` Amazon Braket interpretation preserves witness/control ordering with the original `E[Z1 after CX]` witness source:

| Backend | Corrected-convention witness MAE | Corrected-convention witness rank corr |
| --- | ---: | ---: |
| `rigetti_cepheus_1_108q` | 0.061643 | 0.557668 |
| `iqm_garnet` | 0.021719 | 0.981981 |
| `iqm_emerald` | 0.021479 | 0.884995 |

## Comparison

### Product-state vs entangling

The entangling CX witness supports bounded positive results on the recorded IBM Fez, Rigetti Cepheus, IQM Garnet, and IQM Emerald packet/backend/date/calibration contexts under the provider-aware verifier. This is not a basis for a general cross-backend CX robustness claim.

### Backend deltas

| Backend | MAE delta, product | Rank delta, product |
| --- | ---: | ---: |
| `ibm_fez` | 0.1989 | 1.0535 |
| `rigetti_cepheus_1_108q` | 0.0801 | 0.6654 |

Here the MAE delta is `control MAE - witness MAE`, so larger is better. The rank delta is `witness rank correlation - control rank correlation`, so larger is better.

### Excluded IonQ target

The active sweep does not require additional IBM machines. IBM Kingston and IBM Marrakesh are deferred from the active verifier path because the distinct value-add over the committed IBM Fez plus Braket/Rigetti artifacts is not enough to justify requiring extra hardware evidence for the current bounded claim.

The current intended IonQ route is Amazon Braket, not direct IonQ API execution. A read-only Braket device check on 2026-05-19 found `arn:aws:braket:us-east-1::device/qpu/ionq/Forte-1` and `arn:aws:braket:us-east-1::device/qpu/ionq/Forte-Enterprise-1` in `OFFLINE` status and `arn:aws:braket:us-east-1::device/qpu/ionq/Aria-1` in `RETIRED` status. No Braket/IonQ Stage 4 task was submitted, and no IonQ hardware artifact is present in the repository.

### Amazon Braket / Rigetti

The Braket/Rigetti product-state run completed after adding a Braket-specific preparation and execution adapter. It used 8 frozen rows with 1000 shots per row on `Cepheus-1-108Q`. The witness beat control on both declared metrics:

- witness MAE: `0.069901` vs control MAE: `0.149995`
- witness rank correlation: `0.786644` vs control rank correlation: `0.121232`
- offline verifier: `pass=true`

This run should be treated as a bounded cross-provider replication artifact, not as a broad robustness proof.

### Machine-verification status

The canonical sweep manifest is:

`logs/automated_stage_gates/stage4_hardware_sweep/manifest.json`

The offline sweep verifier is:

`scripts/verify_stage4_hardware_sweep.py`

The verifier output is:

`logs/automated_stage_gates/stage4_hardware_sweep/offline_verification.json`

The current verifier includes deterministic row-bootstrap percentile intervals over committed per-row records and deterministic shot-resampling percentile intervals from committed raw counts for witness/control MAE, rank correlation, and witness-control deltas. These intervals are verifier diagnostics over recorded artifacts, not independent hardware reruns.

The classical recomputation cost estimate is:

`logs/automated_stage_gates/stage4_classical_compute_cost/results.json`

It estimates the local verifier-side recomputation of the six active Stage 4 records at `4096` static arithmetic-scale operations over `163072` recorded hardware shots, with zero incremental local verifier cost. This is not provider billing reconstruction and is not a hardware queue-time predictor.

Current repository state distinguishes active sweep records from deferred or excluded targets:

- The IBM Fez 4096-shot artifact is present and recomputable from raw counts.
- The Amazon Braket/Rigetti 1000-shot artifact is present and recomputable from raw counts.
- Additional IBM Kingston/Marrakesh hardware rows are deferred, not active verifier records.
- The CX no-hardware rehearsal passes and is explicitly marked as non-hardware readiness evidence.
- The IBM Fez CX hardware artifact is present and recomputable from raw counts.
- The Braket CX Rigetti, IQM Garnet, and IQM Emerald artifacts are present, recomputable from raw counts, and hardware-positive under manifest-declared provider-aware decoding.
- The CX portability diagnostic is present and explains the earlier generic-decoder negative classification.
- The sweep verifier passes for the active records.
- IonQ is not an active sweep record. The manifest records it only under excluded targets because the checked Amazon Braket IonQ devices were unavailable on 2026-05-19, so IonQ hardware tests could not be run from the checked AWS account.

Deferred IBM rows should not be treated as machine-verifiable public evidence until the real run records, job IDs, raw counts, backend metadata, and verifier outputs are added. For IonQ specifically, a future artifact should be labeled as a new dated Amazon Braket/IonQ run if a Braket IonQ device becomes available, and then added as a new manifest record.

### Provider bitstring calibration status

Amazon Braket CX records are positive only under the manifest-declared `q0q1` result-key convention. The current support for that convention is the provider-aware manifest plus the CX portability diagnostic over committed raw counts. A stronger future replication packet should add known-state provider calibration runs for `|00>`, `|01>`, `|10>`, and `|11>` before promoting any broader provider-level decoding claim.

### Shot-resampling intervals

The sweep verifier writes per-record `uncertainty_intervals.shot_resampling` blocks in `logs/automated_stage_gates/stage4_hardware_sweep/offline_verification.json`. The witness-MAE point estimates and 95% shot-resampling intervals are:

| Backend/context | Family | Witness MAE point | 95% shot-resampling interval |
| --- | --- | ---: | --- |
| IBM Fez | product-state | 0.018382 | 0.017004-0.024981 |
| Rigetti Cepheus-1-108Q | product-state | 0.069901 | 0.062423-0.088949 |
| IBM Fez | CX | 0.021458 | 0.019492-0.027762 |
| Rigetti Cepheus-1-108Q | CX | 0.061643 | 0.051555-0.076311 |
| IQM Garnet | CX | 0.021719 | 0.016609-0.037590 |
| IQM Emerald | CX | 0.021479 | 0.016966-0.037472 |

These intervals do not replace the need for independent reruns across dates and calibration windows.

### Family-level summary

| Family | Best witness MAE | Best witness rank corr | Worst control MAE | Worst control rank corr |
| --- | ---: | ---: | ---: | ---: |
| Product-state | 0.018382 | 0.876558 | 0.217262 | -0.176940 |

### Goal status

The active evidence packaging goals are complete:

1. verify the existing IBM Fez product-state hardware packet from committed raw counts
2. add an Amazon Braket/Rigetti product-state replication artifact with completed task ARNs and S3 result URIs
3. record IonQ unavailability without promoting a missing IonQ run
4. add a no-hardware CX ideal-count rehearsal
5. add a completed IBM Fez CX hardware artifact with raw counts and verifier recomputation
6. add completed Braket CX artifacts with raw counts and provider-aware verifier recomputation
7. keep additional IBM hardware execution lanes deferred unless real artifacts are later added

## Evidence Pointers

- Product-state IBM packet logs: `logs/automated_stage_gates/stage4_hardware_packet`
- IBM Fez CX artifact: `logs/automated_stage_gates/stage4_hardware_sweep/ibm_runtime__ibm_fez/two_qubit_cx_parity_phase_wrap_v2_20260519T222219Z`
- Amazon Braket/Rigetti 1000-shot artifact: `logs/automated_stage_gates/stage4_hardware_sweep/amazon_braket__arn_aws_braket_us-west-1__device_qpu_rigetti_Cepheus-1-108Q/two_qubit_zz_expectation_phase_wrap_v1_20260519T100942Z`
- Amazon Braket/Rigetti CX artifact: `logs/automated_stage_gates/stage4_hardware_sweep/amazon_braket__arn_aws_braket_us-west-1__device_qpu_rigetti_Cepheus-1-108Q/two_qubit_cx_parity_phase_wrap_v2_20260519T230047Z`
- Amazon Braket/IQM Garnet CX artifact: `logs/automated_stage_gates/stage4_hardware_sweep/amazon_braket__arn_aws_braket_eu-north-1__device_qpu_iqm_Garnet/two_qubit_cx_parity_phase_wrap_v2_20260519T230446Z`
- Amazon Braket/IQM Emerald CX artifact: `logs/automated_stage_gates/stage4_hardware_sweep/amazon_braket__arn_aws_braket_eu-north-1__device_qpu_iqm_Emerald/two_qubit_cx_parity_phase_wrap_v2_20260519T230818Z`
- CX portability diagnostic: `docs/research/q-rope-stage4-cx-portability-diagnostic-v1.md`
- CX no-hardware rehearsal: `logs/automated_stage_gates/stage4_cx_rehearsal/ideal_counts_rehearsal`
- Stage 4 sweep manifest: `logs/automated_stage_gates/stage4_hardware_sweep/manifest.json`
- Stage 4 sweep verifier output: `logs/automated_stage_gates/stage4_hardware_sweep/offline_verification.json`
- Stage 4 sweep verifier: `scripts/verify_stage4_hardware_sweep.py`
- Stage 4 sweep runner: `scripts/run_stage4_hardware_sweep.py`

## Recommendation

The next step is review packaging, not more execution:

1. fold these run results into the publication docs
2. describe the entangling witness as bounded active IBM Fez and Amazon Braket positive hardware evidence under provider-aware decoding
3. keep the 4096-shot wording for IBM and explicitly note that Amazon Braket/IonQ was unavailable during the 2026-05-19 check
