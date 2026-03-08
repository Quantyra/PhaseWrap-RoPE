# Q-RoPE First Pair-State Synthetic Packet v1

## Scope
- Story: `S130`
- Packet: `V0` vs `V_pairstate_relational`
- Dataset: `synthetic_offset_binary`
- Seeds: `42`, `123`, `777`
- Backend: `sim_quantum_statevector`

## Per-seed results
| Variant | Seed | Accuracy | F1 | Positive-minus-negative offset gap | Signed contrast mean | Magnitude balance mean |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `V0` | `42` | `0.562500` | `0.481481` | `0.017148` | `n/a` | `n/a` |
| `V0` | `123` | `0.554688` | `0.521008` | `0.012244` | `n/a` | `n/a` |
| `V0` | `777` | `0.492188` | `0.380952` | `0.025629` | `n/a` | `n/a` |
| `V_pairstate_relational` | `42` | `1.000000` | `1.000000` | `0.482001` | `0.067242` | `0.033282` |
| `V_pairstate_relational` | `123` | `1.000000` | `1.000000` | `0.351762` | `0.116561` | `0.057693` |
| `V_pairstate_relational` | `777` | `1.000000` | `1.000000` | `0.482764` | `0.061058` | `0.030222` |

## Packet means
| Variant | Mean accuracy | Mean F1 | Mean offset gap | Mean signed contrast | Mean magnitude balance |
| --- | ---: | ---: | ---: | ---: | ---: |
| `V0` | `0.536459` | `0.461147` | `0.018340` | `n/a` | `n/a` |
| `V_pairstate_relational` | `1.000000` | `1.000000` | `0.438842` | `0.081620` | `0.040399` |

## Raw result
- On the fixed packet, `V_pairstate_relational` dominates `V0`.

## Validity warning
This result is not yet decision-grade for one reason:
- the current pair-state construction uses explicit signed offset sectors on a dataset whose label is itself the sign of the relative offset

That means the mechanism may be validly relational in the narrow synthetic sense, but it may also be too directly aligned to the label rule to count as a sufficient restart win by itself.

## Correct interpretation
- The packet is a strong positive signal.
- It is not yet a clean approval-to-expand signal.
- The next required step is a validity audit:
  - determine whether the pair-state branch is expressing the intended mechanism
  - or whether it is exploiting a too-direct encoding of the synthetic label rule

## Bottom line
- `Positive packet`
- `Do not broaden yet`
- `Run validity controls next`

