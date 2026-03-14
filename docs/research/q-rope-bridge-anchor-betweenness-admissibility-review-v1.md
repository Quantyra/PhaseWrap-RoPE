# Q-RoPE Bridge Anchor-Betweenness Admissibility Review v1

## Admissibility Check
- Closer to positional-encoding behavior than the current transfer families: `pass`
- Can be stated without reopening hardware: `pass`
- Supports a bounded symbolic challenger with an explicit frozen basis: `pass`
- Preserves auditable diagnostics and stop rules: `pass`
- Does not collapse back into ordinary transfer-family churn: `pass`

## Structural Difference Versus Earlier Bridge Tasks
- `anchor-order` asks whether candidates are ordered correctly around an anchor.
- `anchor-distance` asks whether relative nearer/farther distance to an anchor is preserved.
- `anchor-span-membership` asks whether a probe is inside or outside an anchor-defined interval.
- `anchor-offset-signature` asks whether the selected probe preserves the correct signed offset class relative to the anchor.
- `anchor-betweenness` asks whether the probe and final resolution preserve the correct ordered betweenness relation relative to a left-bound, anchor, and right-bound frame.
- That difference matters because betweenness is a composite positional relation that should be harder to compress into the already-tested order, distance, or bucket summaries.

## Decision
- Pass to memo-level approval-candidate posture only.
- Keep execution closed until a dedicated implementation gate is written.
