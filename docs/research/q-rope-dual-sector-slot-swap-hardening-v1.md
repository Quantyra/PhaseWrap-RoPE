# Q-RoPE Dual-Sector Slot-Swap Hardening v1

## Scope
- Story: `S181`
- Task: `synthetic_dual_sector_agreement_binary`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Variants:
  - `V_future_relational_witness_dual`
  - `V_control_symbolic_dual_sector`

## Control
- Applied `slot_swap = 1`
- Swapped all observation `A` fields with observation `B` fields before model execution
- Kept labels unchanged

## Validation
- Focused local suite passed: `81 passed`

## Swapped packet
| Variant | Seed | Accuracy | F1 |
| --- | --- | ---: | ---: |
| `V_control_symbolic_dual_sector` | `42` | `0.500000` | `0.666667` |
| `V_control_symbolic_dual_sector` | `123` | `0.500000` | `0.666667` |
| `V_control_symbolic_dual_sector` | `777` | `0.500000` | `0.666667` |
| `V_future_relational_witness_dual` | `42` | `1.000000` | `1.000000` |
| `V_future_relational_witness_dual` | `123` | `1.000000` | `1.000000` |
| `V_future_relational_witness_dual` | `777` | `1.000000` | `1.000000` |

## Direct comparison to the original packet
- Candidate mean accuracy: unchanged at `1.000000`
- Candidate mean F1: unchanged at `1.000000`
- Control mean accuracy: unchanged at `0.500000`
- Control mean F1: unchanged at `0.666667`

## Diagnostics
- Generator diagnostics now record `slot_swap = 1`
- Candidate diagnostics stayed clean:
  - `forbidden_inputs_absent = true`
  - `bounded_feature_audit_pass = true`
- Control diagnostics stayed clean:
  - `forbidden_inputs_absent = true`

## Interpretation
The current dual-sector witness result is symmetric under deterministic exchange of observation slots.

That materially strengthens the agreement interpretation:
- the active branch is not depending on whether a relation appears in slot `A` or slot `B`
- the current win survives the cleanest remaining symmetry check from the first packet

## Bottom line
Slot-swap hardening passed cleanly.
The branch remains active and earned one further bounded validity check, not broad expansion.
