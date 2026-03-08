# Q-RoPE Relational Witness Symbolic-Control v1

## Scope
- Story: `S170`
- Task: `synthetic_sector_parity_binary`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Comparison:
  - `V_future_relational_witness` under `contrasts_only`
  - `V_control_symbolic_relational`

## Mean results
| Variant | Mean accuracy | Mean F1 | Feature schema |
| --- | ---: | ---: | --- |
| `V_future_relational_witness` (`contrasts_only`) | `1.000000` | `1.000000` | quantum-derived relational contrasts |
| `V_control_symbolic_relational` | `1.000000` | `1.000000` | direct sector one-hot |

## Primary read
The compressed witness branch does **not** beat the direct symbolic relational control on this task.

The symbolic control matched it exactly.

## What this means
This is not a failure of the witness branch as an internal mechanism result.

It does mean something narrower and important:
- `synthetic_sector_parity_binary` is linearly solved once explicit sector identity is available
- so this task no longer supports a claim that the current quantum-derived witness representation is uniquely necessary

## What remains true
The witness branch still established useful things:
- the branch can extract a compact relational contrast core
- that core is stronger than the earlier Q-RoPE lines in this repo
- the branch survived multiple bounded validity checks

## What is no longer supported on this task
- quantum-specific necessity
- superiority over a fair direct symbolic relational baseline

## Correct interpretation
- `positive internal mechanism result`
- `negative uniqueness result on current task`

Both statements need to stay together.

## Bottom line
The witness branch is real, but `synthetic_sector_parity_binary` is now exhausted as a differentiating task.
If the branch continues, it needs a harder alignment-safe task where direct symbolic sector identity alone is not enough.
