# Q-RoPE V_new Synthetic Decision Memo v1

## Decision
- `STOP`

`V_new_explicit_interference` should not continue as an active implementation branch.

## Why
The bounded restart phase was approved under a strict falsification rule:
- local-only
- synthetic-only
- `V0` vs `V_new_explicit_interference`
- no mixed-metric or score-shift-only success claims

The executed packet failed that rule.

## Evidence
- Packet summary: `docs/research/q-rope-first-vnew-synthetic-packet-v1.md`
- Mean results:
  - `V0`: accuracy `0.536459`, F1 `0.461147`, offset gap `0.018340`
  - `V_new_explicit_interference`: accuracy `0.510417`, F1 `0.475110`, offset gap `-0.001737`

## Interpretation
- `V_new_explicit_interference` is executable.
- It does not show the intended relative-offset mechanism advantage.
- The slight mean `F1` gain is not enough because:
  - mean `accuracy` is worse
  - signed offset separation is worse
  - the offset gap flips negative overall

## What not to do next
- Do not reopen implementation tweaks on `V_new_explicit_interference`
- Do not broaden the synthetic family
- Do not reopen remote execution
- Do not spend cloud budget on this branch

## What may still be preserved
- Preserve the mechanism as a documented failed restart hypothesis.
- A future reopening is allowed only if there is a new comparator hypothesis that is materially different from:
  - similarity magnitude
  - parity-contrast constructive/destructive comparison

## Program effect
- The bounded restart is complete.
- The repo should return to paused/internal-archive posture after this memo.

