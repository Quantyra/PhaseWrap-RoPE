# Q-RoPE Dual-Sector Post-Rotation Decision v1

## Decision
- `BRANCH REMAINS ACTIVE`
- `DO NOT COUNT SPLIT ROTATION AS NEW ROBUSTNESS EVIDENCE`
- `NEXT BOUNDED STEP = PAIR-REINDEX HARDENING`

## Why the branch remains active
Nothing degraded under the `split_rotation = 1` packet.

But that alone is not enough to call it stronger, because the control was effectively inert.

## Why split rotation does not count
The current generator structure makes `split_rotation = 1` a no-op for the dual-sector branch.

So the correct interpretation is:
- no negative signal
- no new positive robustness signal

## Next bounded evidence step
### `pair-reindex hardening`
Use one deterministic control that changes:
- which concrete `sample_a` and `sample_b` instances are paired within each sector bucket

while preserving:
- labels
- class balance
- sector-pair balance
- packet scope

## Why this is the right next move
It is the smallest remaining generator-level control that actually changes concrete examples.

That makes it a real robustness test, unlike the inert split-rotation path.

## What remains disallowed
- benchmark expansion
- remote execution
- multiple new hardening steps in parallel

## Bottom line
The branch is still alive.
The split-rotation result should be treated as a control-design finding, not as added robustness evidence.
