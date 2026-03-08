# Q-RoPE Relational Witness Schema-Compression v1

## Scope
- Story: `S167`
- Task: `synthetic_sector_parity_binary`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Candidate: `V_future_relational_witness`
- Modes:
  - `full`
  - `means_only`
  - `contrasts_only`

## Mean results
| Mode | Mean accuracy | Mean F1 | Mean task contrast | Anti-collapse | Forbidden inputs absent |
| --- | ---: | ---: | ---: | --- | --- |
| `full` | `1.000000` | `1.000000` | `-0.005529` | `true` | `true` |
| `means_only` | `0.916667` | `0.888889` | `-0.005529` | `true` | `true` |
| `contrasts_only` | `1.000000` | `1.000000` | `-0.005529` | `true` | `true` |

## Primary read
The witness win survives intact on a cleaner relational core.

Specifically:
- `contrasts_only` matched `full`
- `means_only` degraded materially

## Why this matters
This is the strongest mechanism clarification in the witness branch so far.

The prior ablation packet already said:
- the result is not a `delta_task` shortcut
- the full schema is redundant

This compression packet now says more:
- the branch does not need the raw sector means to preserve the win
- the direct relational contrasts are sufficient

## What this supports
A stronger interpretation is now justified:
- the current positive result is carried by a compact relational contrast core
- not by the full overcomplete witness schema

That is materially better than a generic positive result because it sharpens:
- what the branch is actually using
- what a future cleaner implementation should preserve

## What did not break
Across all nine runs:
- `anti_collapse_pass = true`
- `forbidden_inputs_absent = true`

So the compression result did not come from relaxing the discipline rules.

## Correct interpretation
- `positive packet`
- `mechanism signal strengthened`
- `contrasts_only is the preferred witness schema`

## What is still not justified
- remote execution
- benchmark expansion
- multiple new witness candidates

## Bottom line
The relational witness branch is now stronger than it was after the ablation packet.
The best-supported schema is:
- `contrasts_only`

The next branch decision should be based on that compressed schema, not on the original full witness feature set.
