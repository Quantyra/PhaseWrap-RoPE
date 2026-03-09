# Q-RoPE Dual-Sector Agreement First Packet v1

## Scope
- Story: `S178`
- Task: `synthetic_dual_sector_agreement_binary`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Variants:
  - `V_future_relational_witness_dual`
  - `V_control_symbolic_dual_sector`

## Per-seed results
| Variant | Seed | Accuracy | F1 | Forbidden inputs absent | Bounded feature audit |
| --- | --- | ---: | ---: | --- | --- |
| `V_control_symbolic_dual_sector` | `42` | `0.500000` | `0.666667` | `true` | `n/a` |
| `V_control_symbolic_dual_sector` | `123` | `0.500000` | `0.666667` | `true` | `n/a` |
| `V_control_symbolic_dual_sector` | `777` | `0.500000` | `0.666667` | `true` | `n/a` |
| `V_future_relational_witness_dual` | `42` | `1.000000` | `1.000000` | `true` | `true` |
| `V_future_relational_witness_dual` | `123` | `1.000000` | `1.000000` | `true` | `true` |
| `V_future_relational_witness_dual` | `777` | `1.000000` | `1.000000` | `true` | `true` |

## Packet means
| Variant | Mean accuracy | Mean F1 |
| --- | ---: | ---: |
| `V_control_symbolic_dual_sector` | `0.500000` | `0.666667` |
| `V_future_relational_witness_dual` | `1.000000` | `1.000000` |

## Primary read
The dual-sector agreement task differentiated the witness branch cleanly.

The bounded symbolic control failed to solve the task linearly.
The dual witness candidate beat it on all three seeds.

## Why this matters
This is the first witness-task result in the repo where:
- the candidate stayed bounded
- the symbolic control stayed bounded
- and the task still differentiated the candidate cleanly

That directly addresses the weakness of `synthetic_sector_parity_binary`.

## What remains true
The packet is positive, but still first-packet evidence.

What is already strong:
- perfect multi-seed candidate result
- symbolic control stayed at chance-level accuracy
- forbidden-input audit remained clean
- bounded-feature audit remained clean

What is not yet justified:
- benchmark expansion
- remote execution
- multiple new variants

## Bottom line
This is the strongest differentiating witness result in the repository so far.
The next correct move is one bounded hardening step, not broadening.
