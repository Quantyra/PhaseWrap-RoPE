# Q-RoPE Pair-State Sector-Alignment Control v1

## Decision
- `ONE CONTROL ONLY`
- `SECTOR PERMUTATION`

## Goal
Test whether the current `V_pairstate_relational` synthetic win survives only because the signed sector definition is too directly aligned with the synthetic label rule.

## Minimal control
Keep the full pair-state skeleton unchanged:
- ordered token-pair content encoding
- four-sector partition
- sector-first response collection
- signed-contrast aggregation

Change only one thing:
- permute the sector-to-sign alignment used by the relational readout

## Recommended control packet
- Variant under test: `V_pairstate_relational`
- Dataset: `synthetic_offset_binary`
- Seeds: `42`, `123`, `777`
- Backend: `sim_quantum_statevector`
- Control mode: `sector_permuted`

## Exact control logic
Use the same four sectors:
- `P_small`
- `P_large`
- `N_small`
- `N_large`

But do not aggregate them with the original positive-vs-negative grouping.

Instead, use one fixed crossed assignment:
- positive bucket: `P_small + N_large`
- negative bucket: `N_small + P_large`

This is the preferred first control because:
- it preserves the same sector inventory
- it preserves the same content encoding
- it preserves sector-first measurement
- it breaks the direct correspondence between sector sign and task label

## Expected outcomes
### If the current win is mostly tautological
- accuracy and F1 should collapse sharply
- signed contrast should lose alignment with label sign
- offset-gap advantage should shrink toward baseline

### If the current win is still informative
- some separation may remain
- but it should be materially weaker than the original aligned packet

The control does not need to preserve performance.
It only needs to tell us whether the original result depended on direct alignment.

## Pass-fail interpretation
### Validity-preserving outcome
- original aligned packet remains strong
- permuted control collapses clearly
- interpretation: the current packet is highly alignment-sensitive and should still be treated as validity-limited

### Stronger restart-supporting outcome
- original aligned packet is strong
- permuted control still shows meaningful relational separation
- interpretation: the pair-state mechanism may be learning something beyond direct sign alignment

### Weakening outcome
- both aligned and permuted packets look similarly strong
- interpretation: current diagnostics are not isolating the intended mechanism cleanly

## Scope limits
Do not add:
- new datasets
- new pair-state variants
- remote execution
- broader ablations

## Next step
Implement only this one `sector_permuted` control mode and compare it directly against the existing aligned packet.
