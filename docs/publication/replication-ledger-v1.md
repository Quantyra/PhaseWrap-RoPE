# PhaseWrap replication ledger v1

Status: `FULL_IBM_REPLACEMENT_AND_PROVIDER_AWARE_BRAKET_CX_RECORDED`

Date: `2026-05-23`

## Purpose

This ledger records what has actually been executed and what remains blocked. It is intentionally separate from the replication plan so reviewers can distinguish completed evidence from intended replication work.

Machine-readable ledger: `logs/automated_stage_gates/replication_lanes/replication-ledger.json`

## Current execution state

| Lane | Circuit family | Target | Status | Public evidence claim |
| --- | --- | --- | --- | --- |
| Stage 4 product original | `two_qubit_zz_expectation_phase_wrap_v1` | IBM `ibm_fez`, `2026-05-17` | `published_completed` | Bounded hardware-positive result for one packet/backend/date/calibration context. |
| Product Braket replication | `two_qubit_zz_expectation_phase_wrap_v1` | Amazon Braket Rigetti `Cepheus-1-108Q`, `2026-05-19` | `published_completed` | Bounded hardware-positive Braket/Rigetti replication for one packet/backend/date/calibration context. |
| Product rerun A | `two_qubit_zz_expectation_phase_wrap_v1` | Second IBM backend, date 1 | `blocked_pending_credentials_and_backend_selection` | No replication claim. |
| Product rerun B | `two_qubit_zz_expectation_phase_wrap_v1` | Third IBM backend or same backend on date 2 | `blocked_pending_credentials_and_backend_selection` | No replication claim. |
| CX IBM Fez original | `two_qubit_cx_parity_phase_wrap_v2` | IBM `ibm_fez`, `2026-05-19` | `published_completed` | Bounded CX hardware-positive result for one packet/backend/date/calibration context. |
| CX Braket Rigetti replication | `two_qubit_cx_parity_phase_wrap_v2` | Amazon Braket Rigetti `Cepheus-1-108Q`, `2026-05-19` | `published_completed` | Bounded provider-aware hardware-positive Braket CX result; does not support a general cross-backend CX claim. |
| CX Braket IQM Garnet replication | `two_qubit_cx_parity_phase_wrap_v2` | Amazon Braket IQM `Garnet`, `2026-05-19` | `published_completed` | Bounded provider-aware hardware-positive Braket CX result; does not support a general cross-backend CX claim. |
| CX Braket IQM Emerald replication | `two_qubit_cx_parity_phase_wrap_v2` | Amazon Braket IQM `Emerald`, `2026-05-19` | `published_completed` | Bounded provider-aware hardware-positive Braket CX result; does not support a general cross-backend CX claim. |
| CX Braket queued attempt | `two_qubit_cx_parity_phase_wrap_v2` | Amazon Braket Rigetti `Cepheus-1-108Q`, `2026-05-19` | `hardware_attempt_timeout_cancelled` | No raw counts; superseded by the later completed Rigetti CX record. |
| Full IBM Fez replacement comparison | `replacement_packet_execution_counts` plus known-state calibration | IBM `ibm_fez`, `2026-05-23` UTC collection artifacts | `published_completed` | Bounded full 4096-shot positive replacement comparison across product-state and CX templates, two seeds, and matched positional/null controls. |

## Braket replication result for this update

The implementation environment had AWS credentials, a reachable Amazon Braket Rigetti QPU, and a Braket-compatible output bucket. The Braket replication lane completed with 8 tasks at 1000 shots per task and verified as `PASS / hardware-positive`.

Artifact directory:

`logs/automated_stage_gates/stage4_hardware_sweep/amazon_braket__arn_aws_braket_us-west-1__device_qpu_rigetti_Cepheus-1-108Q/two_qubit_zz_expectation_phase_wrap_v1_20260519T100942Z`

Metrics:

- witness MAE: `0.069901`
- witness rank correlation: `0.786644`
- control MAE: `0.149995`
- control rank correlation: `0.121232`
- offline verifier: `pass=true`

## CX no-hardware rehearsal

The CX witness lane now has a local ideal-count rehearsal artifact:

`logs/automated_stage_gates/stage4_cx_rehearsal/ideal_counts_rehearsal/`

Metrics:

- witness MAE: `0.000051`
- witness rank correlation: `1.000000`
- control MAE: `0.229743`
- control rank correlation: `-0.171995`
- gate pass: `true`

This artifact submits no hardware job and makes no entangling-witness hardware evidence claim. It records that the frozen-packet, CX ideal-count, and evaluator mechanics are ready for a future credentialled hardware execution.

## CX hardware attempt

An Amazon Braket/Rigetti CX hardware run was attempted on `2026-05-19` after the ideal-count rehearsal passed.

Attempt artifacts:

- preflight blocked by bucket naming rule: `logs/automated_stage_gates/stage4_hardware_sweep/amazon_braket__arn_aws_braket_us-west-1__device_qpu_rigetti_Cepheus-1-108Q/two_qubit_cx_parity_phase_wrap_v2_20260519T213312Z/`
- submitted task timed out while queued: `logs/automated_stage_gates/stage4_hardware_sweep/amazon_braket__arn_aws_braket_us-west-1__device_qpu_rigetti_Cepheus-1-108Q/two_qubit_cx_parity_phase_wrap_v2_20260519T220400Z/`

Submitted task:

`arn:aws:braket:us-west-1:[account-redacted]:quantum-task/ac7e2b2e-2794-43e8-ba18-c65225efceea`

The task remained `QUEUED` until the local runner hit its `1800` second timeout. A cancellation request was then sent, and AWS reported `CANCELLED` at `2026-05-19T22:07:22.245000Z`. No raw counts were produced, no CX metrics were computed from hardware counts, and this remains non-evidence for the entangling witness.

## CX Braket provider-aware replications

Later on `2026-05-19`, online Amazon Braket gate-model devices were run for the CX witness at 8 rows and 1000 shots per row. These runs produced raw counts and machine-verifiable provider-aware positive outcomes. The earlier generic `q1q0` decode classified them as negative; the active sweep verifier now records Amazon Braket result keys as `q0q1`.

| Target | Artifact | Witness MAE | Witness rank corr | Control MAE | Control rank corr | Outcome |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Rigetti `Cepheus-1-108Q` | `logs/automated_stage_gates/stage4_hardware_sweep/amazon_braket__arn_aws_braket_us-west-1__device_qpu_rigetti_Cepheus-1-108Q/two_qubit_cx_parity_phase_wrap_v2_20260519T230047Z/` | 0.061643 | 0.557668 | 0.194370 | -0.060616 | `hardware-positive` |
| IQM `Garnet` | `logs/automated_stage_gates/stage4_hardware_sweep/amazon_braket__arn_aws_braket_eu-north-1__device_qpu_iqm_Garnet/two_qubit_cx_parity_phase_wrap_v2_20260519T230446Z/` | 0.021719 | 0.981981 | 0.204370 | -0.060616 | `hardware-positive` |
| IQM `Emerald` | `logs/automated_stage_gates/stage4_hardware_sweep/amazon_braket__arn_aws_braket_eu-north-1__device_qpu_iqm_Emerald/two_qubit_cx_parity_phase_wrap_v2_20260519T230818Z/` | 0.021479 | 0.884995 | 0.210995 | -0.096986 | `hardware-positive` |

These records show that Braket execution succeeded and that provider-aware decoding preserves witness/control ordering for the recorded packet/backend/date/calibration contexts. They should not be reframed as support for general cross-backend robustness.

## Full IBM Fez replacement comparison

Stages 216-218 complete the full 4096-shot IBM Fez replacement lane. The final merged artifact combines the original 13 completed templates with 8 allocated-instance replacement templates and records `21/21` templates. Stage 217 validates unique `q1q0` bitstring order from known-state calibration counts. Stage 218 records public decision `IBM_FEZ_FROZEN_PACKET_READOUT_NOISE_DELTA_FAVORS_PHASEWRAP` and preserves the historical manifest decision as an evidence alias.

Artifacts:

- `logs/automated_stage_gates/stage216_full_replacement_merged_result_counts_250usd/`
- `logs/automated_stage_gates/stage217_full_replacement_calibration_validation_250usd/`
- `logs/automated_stage_gates/stage218_full_replacement_hardware_metric_interpreter_250usd/`

Summary:

| Source lane | Circuit template | PhaseWrap delta | Best positional delta | Matched null delta | Outcome |
| --- | --- | ---: | ---: | ---: | --- |
| `ibm_cx_seed314_rows16_shots4096` | CX parity | 0.056686 | 0.073770 | 0.079248 | `stable_full_replacement_hardware_target` |
| `ibm_cx_seed577_rows16_shots4096` | CX parity | 0.058017 | 0.082664 | 0.072316 | `stable_full_replacement_hardware_target` |
| `ibm_product_seed314_rows16_shots4096` | Product state | 0.027709 | 0.038480 | 0.039844 | `stable_full_replacement_hardware_target` |
| `ibm_product_seed577_rows16_shots4096` | Product state | 0.037817 | 0.039628 | 0.042044 | `stable_full_replacement_hardware_target` |

This lane supports a bounded two-qubit hardware comparison claim only. It does not establish production transformer improvement, RoPE replacement, quantum advantage, or broad cross-backend robustness.

A replication lane becomes publishable only after it contains:

- completed raw counts;
- backend metadata;
- calibration metadata;
- job identifier retained in the evidence record;
- verifier output recomputed from the published packet files.

## Publication rule

Do not describe PhaseWrap as cross-backend robust, cross-date replicated, or entanglement-validated until the relevant lane changes from blocked/planned to completed with raw counts and verifier output. Negative or inconclusive replications should be published in this ledger rather than hidden.
