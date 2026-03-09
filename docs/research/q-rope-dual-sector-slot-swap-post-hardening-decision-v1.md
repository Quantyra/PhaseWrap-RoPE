# Q-RoPE Dual-Sector Slot-Swap Post-Hardening Decision v1

## Decision
- `BRANCH REMAINS ACTIVE`
- `DO NOT BROADEN`
- `NEXT BOUNDED STEP = TOKEN-RENAMING HARDENING`

## Why the branch remains active
The slot-swap packet matched the original packet exactly:
- candidate remained perfect on all three seeds
- control remained at the same bounded baseline
- diagnostics stayed clean

So the current result is now stronger than a single task win.
It has survived a real symmetry hardening step.

## Why the branch still should not broaden
The active task is still synthetic and narrow.

The next unresolved validity question is not scale.
It is symbol dependence:
- does the branch still win if token identities are globally renamed while sector structure stays fixed?

That matters because the task label depends on relational sector agreement, not on lexical symbol names.

## Next bounded evidence step
### `token-renaming hardening`
Apply one deterministic global token permutation that:
- renames all token symbols consistently
- preserves positions and offsets
- leaves labels unchanged

Then rerun the same six-run packet.

## Why this is the right next move
It is smaller than expansion and more informative than another training perturbation.

If the branch survives token renaming:
- the current result gets materially closer to a true relational-structure claim

If it does not:
- the branch may still be leaning on lexical identity in a way the current task does not justify

## What remains disallowed
- benchmark expansion
- remote execution
- multiple new hardening steps in parallel

## Bottom line
The branch survived slot-swap hardening.
The next correct step is token-renaming hardening, not scale.
