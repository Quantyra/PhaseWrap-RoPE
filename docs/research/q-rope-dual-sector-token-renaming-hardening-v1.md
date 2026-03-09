# Q-RoPE Dual-Sector Token-Renaming Hardening v1

## Scope
- Story: `S184`
- Task: `synthetic_dual_sector_agreement_binary`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Variants:
  - `V_future_relational_witness_dual`
  - `V_control_symbolic_dual_sector`

## Control
- Applied `token_permutation = cdab`
- Renamed tokens globally:
  - `A -> C`
  - `B -> D`
  - `C -> A`
  - `D -> B`
- Kept positions, offsets, and labels unchanged

## Validation
- Focused local suite passed: `83 passed`

## Renamed packet
| Variant | Seed | Accuracy | F1 |
| --- | --- | ---: | ---: |
| `V_control_symbolic_dual_sector` | `42` | `0.500000` | `0.666667` |
| `V_control_symbolic_dual_sector` | `123` | `0.500000` | `0.666667` |
| `V_control_symbolic_dual_sector` | `777` | `0.500000` | `0.666667` |
| `V_future_relational_witness_dual` | `42` | `1.000000` | `1.000000` |
| `V_future_relational_witness_dual` | `123` | `1.000000` | `1.000000` |
| `V_future_relational_witness_dual` | `777` | `1.000000` | `1.000000` |

## Direct comparison to earlier packets
- Candidate mean accuracy: unchanged at `1.000000`
- Candidate mean F1: unchanged at `1.000000`
- Control mean accuracy: unchanged at `0.500000`
- Control mean F1: unchanged at `0.666667`

This matches:
- the original packet
- the slot-swap packet

## Diagnostics
- Generator diagnostics now record `token_permutation = cdab`
- Candidate diagnostics stayed clean:
  - `forbidden_inputs_absent = true`
  - `bounded_feature_audit_pass = true`
- Control diagnostics stayed clean:
  - `forbidden_inputs_absent = true`

## Interpretation
The current dual-sector witness result is invariant to one deterministic global token renaming.

That materially weakens a lexical-identity explanation:
- the active branch is not depending on the specific token alphabet labels used in the rendered text
- the current win survives both slot symmetry and token renaming

## Bottom line
Token-renaming hardening passed cleanly.
The branch remains active and earned one further bounded robustness check, not broad expansion.
