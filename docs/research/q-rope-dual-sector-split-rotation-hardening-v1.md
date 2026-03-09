# Q-RoPE Dual-Sector Split-Rotation Hardening v1

## Scope
- Story: `S187`
- Task: `synthetic_dual_sector_agreement_binary`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Variants:
  - `V_future_relational_witness_dual`
  - `V_control_symbolic_dual_sector`

## Control
- Applied `split_rotation = 1`

## Observed packet
| Variant | Seed | Accuracy | F1 |
| --- | --- | ---: | ---: |
| `V_control_symbolic_dual_sector` | `42` | `0.500000` | `0.666667` |
| `V_control_symbolic_dual_sector` | `123` | `0.500000` | `0.666667` |
| `V_control_symbolic_dual_sector` | `777` | `0.500000` | `0.666667` |
| `V_future_relational_witness_dual` | `42` | `1.000000` | `1.000000` |
| `V_future_relational_witness_dual` | `123` | `1.000000` | `1.000000` |
| `V_future_relational_witness_dual` | `777` | `1.000000` | `1.000000` |

## Validity finding
This control did not create a meaningful new packet.

Reason:
- the current dual-sector generator constructs exactly one required set of paired examples per bucket for each split
- with that bucket cardinality, `split_rotation = 1` does not alter the selected rows

The metrics matched earlier packets exactly, but that should not be counted as new robustness evidence.

## Diagnostics
- Generator diagnostics do correctly record `split_rotation = 1`
- Task balance stayed intact
- But the control is effectively inert under the current generator construction

## Interpretation
`split_rotation` is a no-op for the current dual-sector branch.

That is still a useful finding:
- it prevents the repo from treating an inert control as real robustness evidence
- it identifies the next meaningful generator-level question as pair reindexing, not more split rotation

## Bottom line
The branch did not weaken, but this control did not actually harden it either.
The next correct move is a meaningful pair-reindex control, not another split-rotation rerun.
