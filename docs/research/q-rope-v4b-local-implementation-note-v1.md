# Q-RoPE V4b Local Implementation Note v1

## Scope completed
- Added `V4b` config
- Implemented shared raw/effective phase helpers
- Kept `V0-V4` behavior backward-compatible
- Routed local, photonic, and IBM translation paths through the shared effective phase logic
- Preserved the `V3`/`V4` hardware-cost class for `V4b`

## Implementation details
- `V4b` raw base phase: `0.18`
- global phase clip: `0.22`
- feature/phase ratio factor: `0.35`
- `variant_phases(...)` remains as a raw-schedule compatibility wrapper
- `effective_variant_phases(...)` now holds the `V4b` mechanism

## Validation
- Focused tests passed: `25 passed`
- Local smoke run succeeded:
  - `sim_quantum_statevector`
  - dataset `yelp`
  - seed `42`

## Next step
- Execute the zero-credit local comparison packet for `V3` vs `V4` vs `V4b`
- Decide whether `V4b` is cleaner than damped-only `V4`
