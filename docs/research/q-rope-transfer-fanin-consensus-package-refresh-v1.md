# Q-RoPE Fan-in Consensus Package Refresh v1

## Decision
- Preserve `fan-in consensus` in the internal package as an archived negative transfer boundary.

## Rationale
- The branch failed bounded nuisance hardening.
- The failure is informative for future transfer screening and should remain visible in the internal portfolio.

## Package Effect
- Positive transfer portfolio is unchanged.
- Archived negative boundaries now include:
  - `braid`
  - `staggered-binding`
  - `fan-in consensus`
