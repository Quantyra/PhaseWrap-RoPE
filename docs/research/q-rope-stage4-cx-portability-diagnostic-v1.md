# PhaseWrap-RoPE Stage 4 CX Portability Diagnostic v1

Date: 2026-05-19

## BLUF

This diagnostic explains the earlier Braket CX generic-decoder negatives. Replaying the committed raw counts under alternate two-bit conventions showed that all three Braket CX records recover as positive under the same simple interpretation:

- bitstring order: `q0q1`
- witness source: original `E[Z1 after CX]`

This pointed to a provider result-decoding convention mismatch between IBM-style `q1q0` counts and Amazon Braket OpenQASM result keys, not to a native-gate or backend-noise failure. The canonical sweep verifier now records this explicitly: IBM records use `q1q0`; Amazon Braket records use `q0q1`.

## Inputs

Diagnostic command:

```bash
python scripts/diagnose_stage4_cx_portability.py
```

Machine-readable output:

`logs/automated_stage_gates/stage4_cx_portability_diagnostic/offline_diagnostic.json`

Source artifacts:

- `logs/automated_stage_gates/stage4_hardware_sweep/ibm_runtime__ibm_fez/two_qubit_cx_parity_phase_wrap_v2_20260519T222219Z/`
- `logs/automated_stage_gates/stage4_hardware_sweep/amazon_braket__arn_aws_braket_us-west-1__device_qpu_rigetti_Cepheus-1-108Q/two_qubit_cx_parity_phase_wrap_v2_20260519T230047Z/`
- `logs/automated_stage_gates/stage4_hardware_sweep/amazon_braket__arn_aws_braket_eu-north-1__device_qpu_iqm_Garnet/two_qubit_cx_parity_phase_wrap_v2_20260519T230446Z/`
- `logs/automated_stage_gates/stage4_hardware_sweep/amazon_braket__arn_aws_braket_eu-north-1__device_qpu_iqm_Emerald/two_qubit_cx_parity_phase_wrap_v2_20260519T230818Z/`

## Result

| Backend | Historical generic-decoder outcome | Recovered by convention | Best witness MAE | Best witness rank corr |
| --- | --- | --- | ---: | ---: |
| IBM Fez | `hardware-positive` | yes | 0.021458 | 0.972455 |
| Rigetti Cepheus-1-108Q | `hardware-negative` | yes | 0.061643 | 0.557668 |
| IQM Garnet | `hardware-negative` | yes | 0.021719 | 0.981981 |
| IQM Emerald | `hardware-negative` | yes | 0.021479 | 0.884995 |

Common recovered Braket convention:

```json
{
  "bit_order": "q0q1_reversed",
  "witness_source": "z1_current_target"
}
```

Under that convention, the Braket records preserve witness/control ordering. The original negative Braket outcomes came from applying the earlier generic decoder, which treated two-bit strings as `q1q0`.

## Interpretation

The evidence supports this narrower diagnosis:

1. IBM Fez CX is positive under the existing `q1q0` decoder.
2. Braket CX raw counts were negative under the earlier generic decoder.
3. The same Braket raw counts become positive under a uniform `q0q1` result-key interpretation.
4. Therefore, the apparent Braket CX failure was likely a classical result-decoding convention issue.

This is not a license to claim general cross-backend CX robustness. The historical generic-decoder classification remains auditable, while the canonical sweep verifier now records provider bit-order metadata and recomputes corrected evaluations from the same raw counts.

## Next Steps

1. Completed: add an explicit provider bitstring-order field to the sweep manifest.
2. Completed: update the offline verifier to decode Amazon Braket OpenQASM result keys as `q0q1` while preserving IBM's current interpretation.
3. Completed: recompute corrected Braket CX evaluation files from the already committed raw counts.
4. Completed: keep the old negative interpretation visible as a diagnostic finding, not as the final scientific classification.
5. Planned: add known-state provider calibration packets for `|00>`, `|01>`, `|10>`, and `|11>` before promoting broader provider-wide bit-order claims.
6. Partly completed after this diagnostic: the Stage 4 sweep verifier now emits deterministic row-bootstrap and shot-resampling intervals from committed artifacts, Stage 4 has a deterministic local recomputation cost estimate, future replication packet row sets are preregistered, and provider bitstring calibration packet specs plus a failing-by-default verifier contract are present. Remaining hardware-hardening work is real calibration execution and independent reruns across dates and queue conditions.
7. Future work: only after provider-aware decoding is verified should native CZ or XX-family variants be considered.

## Claim Boundary

This diagnostic does not claim broad quantum advantage, production transformer superiority, full transformer-scale validation, or general cross-backend robustness. It only identifies a likely bitstring-order explanation for the apparent Braket CX portability failure in the recorded Stage 4 artifacts.
