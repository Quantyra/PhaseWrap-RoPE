# Q-RoPE Dual-Sector Token-Renaming Post-Hardening Decision v1

## Decision
- `BRANCH REMAINS ACTIVE`
- `DO NOT BROADEN`
- `NEXT BOUNDED STEP = SPLIT-ROTATION HARDENING`

## Why the branch remains active
The token-renaming packet matched both earlier packets:
- candidate remained perfect on all three seeds
- control remained flat at the same bounded baseline
- diagnostics stayed clean

So the branch has now survived:
- the original differentiating packet
- slot-swap symmetry
- token renaming

## Why it still should not broaden
The remaining unresolved risk is not invariance to simple transforms.
It is brittleness to sample selection inside the fixed balanced task family.

The next bounded question is:
- does the branch still win if the selected within-bucket examples are deterministically rotated?

That is more informative now than another symbolic or lexical transform.

## Next bounded evidence step
### `split-rotation hardening`
Apply one deterministic split rotation:
- `split_rotation = 1`

Keep everything else fixed:
- same task
- same seeds
- same candidate
- same control

## Why this is the right next move
It tests robustness to concrete example choice without broadening the task family.

If the branch survives split rotation:
- the current line becomes materially stronger as an internal mechanism result

If it does not:
- the branch may still be relying on one favorable balanced slice

## What remains disallowed
- benchmark expansion
- remote execution
- multiple new hardening steps in parallel

## Bottom line
The branch has passed the key invariance checks.
The next correct step is robustness to deterministic sample rotation, not scale.
