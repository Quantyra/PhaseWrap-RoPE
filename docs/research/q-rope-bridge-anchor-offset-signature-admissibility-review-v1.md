# Q-RoPE Bridge Anchor-Offset-Signature Admissibility Review v1

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
- That difference matters because signed offset signatures are closer to the kind of directional positional relation that motivates RoPE-style phase structure.

## Decision
- Pass to memo-level approval-candidate posture only.
- Keep execution closed until a dedicated implementation gate is written.
