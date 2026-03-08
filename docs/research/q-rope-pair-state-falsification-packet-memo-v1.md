# Q-RoPE Pair-State Falsification Packet Memo v1

## Status
- `memo-only`
- `archive-safe`
- `not approved for implementation`

## Fixed packet
If Quantyra ever reopens the pair-state family, the first packet should be:

- dataset family: `synthetic_offset_binary`
- seeds: `42`, `123`, `777`
- baseline: `V0`
- candidate: `V_pairstate_relational`
- execution scope: local-only
- remote scope: not allowed

## Why reuse the synthetic family
The point of the next restart is not benchmark breadth.
It is mechanism discrimination.

The existing synthetic family is already the cleanest available place to ask:
- does the new representation plus new observable improve signed relative-offset separation?

## Required diagnostics
The packet must report at least:
- mean accuracy
- mean F1
- positive-minus-negative offset gap
- sector-level positive/negative response contrast
- evidence that any gain is not explained by a uniform score shift

## Pass condition
The pair-state candidate passes only if all are true:
1. it beats `V0` on positive-minus-negative offset gap
2. the direction holds across all three seeds
3. metric gains are not mixed in a way that hides a failed mechanism signal
4. sector-contrast diagnostics show real relational separation

## Fail condition
The pair-state candidate fails immediately if any are true:
1. offset-gap improvement is absent or mixed
2. the signal is only a global score shift
3. sector responses do not distinguish positive vs negative offsets
4. success depends on one seed or one headline metric only

## Why this matters
This packet preserves the restart discipline that the repo earned the hard way:
- no implementation without a fixed gate
- no broad experiments before a mechanism win
- no rescue by narrative if the synthetic relation test fails

## Bottom line
The pair-state family is only worth reopening under one condition:
- it accepts the same hard discipline as the prior bounded restart,
- but with a representation and observable that are materially different.

