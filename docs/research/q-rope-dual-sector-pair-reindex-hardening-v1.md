# Q-RoPE Dual-Sector Pair-Reindex Hardening v1

## Scope
- Story: `S190`
- Task: `synthetic_dual_sector_agreement_binary`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Variants:
  - `V_future_relational_witness_dual`
  - `V_control_symbolic_dual_sector`

## Control
- Applied `pair_reindex = 1`
- Reindexed `sample_b` within each sector-pair bucket before pairing

## Validation
- Focused local suite passed: `85 passed`

## Reindexed packet
| Variant | Seed | Accuracy | F1 |
| --- | --- | ---: | ---: |
| `V_control_symbolic_dual_sector` | `42` | `0.500000` | `0.666667` |
| `V_control_symbolic_dual_sector` | `123` | `0.500000` | `0.666667` |
| `V_control_symbolic_dual_sector` | `777` | `0.500000` | `0.666667` |
| `V_future_relational_witness_dual` | `42` | `1.000000` | `1.000000` |
| `V_future_relational_witness_dual` | `123` | `1.000000` | `1.000000` |
| `V_future_relational_witness_dual` | `777` | `1.000000` | `1.000000` |

## Direct comparison to prior packets
- Candidate mean accuracy: unchanged at `1.000000`
- Candidate mean F1: unchanged at `1.000000`
- Control mean accuracy: unchanged at `0.500000`
- Control mean F1: unchanged at `0.666667`

Unlike split rotation, this control is meaningful:
- it changes concrete pairings inside each sector-pair bucket
- while preserving labels and balance

## Diagnostics
- Generator diagnostics record `pair_reindex = 1`
- Candidate diagnostics stayed clean:
  - `forbidden_inputs_absent = true`
  - `bounded_feature_audit_pass = true`
- Control diagnostics stayed clean:
  - `forbidden_inputs_absent = true`

## Interpretation
The current dual-sector witness result survives the first meaningful concrete-pairing perturbation.

That makes the branch materially stronger than it was after the earlier invariance checks alone.

## Bottom line
Pair-reindex hardening passed cleanly.
The next correct pressure test is not another simple generator perturbation.
It is a stronger symbolic relational control.
