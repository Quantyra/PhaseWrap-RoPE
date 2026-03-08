# Q-RoPE Relational Witness Split-Rotation Hardening v1

## Scope
- Story: `S161`
- Task: `synthetic_sector_parity_binary`
- Control: `split_rotation = 1`
- Seeds: `42`, `123`, `777`
- Variants:
  - `V0`
  - `V_future_relational_witness`

## Rotated packet means
| Variant | Mean accuracy | Mean F1 | Mean task contrast |
| --- | ---: | ---: | ---: |
| `V0` | `0.484375` | `0.507835` | `n/a` |
| `V_future_relational_witness` | `1.000000` | `1.000000` | `-0.005529` |

## Comparison to original packet
| Variant | Original mean accuracy | Rotated mean accuracy | Original mean F1 | Rotated mean F1 |
| --- | ---: | ---: | ---: | ---: |
| `V0` | `0.520833` | `0.484375` | `0.475733` | `0.507835` |
| `V_future_relational_witness` | `1.000000` | `1.000000` | `1.000000` | `1.000000` |

## Interpretation
The witness branch did not degrade under the alternate deterministic split policy.

That matters because the main remaining concern after the first positive packet was:
- dependence on one particular split realization

This hardening step weakens that concern materially.

## What is now stronger
- packet robustness to split assignment
- continued anti-collapse compliance
- continued forbidden-input compliance

## What is still not justified
- remote execution
- benchmark expansion
- multiple new variants

## Bottom line
- `hardening pass`
- `branch remains active`
- `next move can expand evidence quality, but should still stay disciplined`
