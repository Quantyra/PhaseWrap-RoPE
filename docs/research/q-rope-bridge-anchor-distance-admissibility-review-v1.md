# Q-RoPE Bridge Anchor-Distance Admissibility Review v1

## Admissibility Check
- Closer to positional-encoding behavior than the current transfer families: `pass`
- Can be stated without reopening hardware: `pass`
- Supports a bounded symbolic challenger with an explicit frozen basis: `pass`
- Preserves auditable diagnostics and stop rules: `pass`
- Does not collapse back into ordinary transfer-family churn: `pass`

## Structural Difference Versus `anchor-order`
- `anchor-order` asks whether two candidates are ordered correctly around an anchor.
- `anchor-distance` asks whether the final resolution preserves the correct nearer/farther relation to the anchor.
- That change matters because RoPE-style positional structure is not only directional; it also depends on relative positional separation.

## Decision
- Pass to memo-level approval-candidate posture only.
- Keep execution closed until a dedicated implementation gate is written.
