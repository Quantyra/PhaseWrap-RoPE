# Research note

## Scope
- Story: `S209`
- Task: `synthetic_dual_content_parity_coupling_binary`
- Candidate: `V_future_relational_witness_triple`
- Controls:
  - `V_control_symbolic_sector_only`
  - `V_control_symbolic_content_only`
  - `V_control_symbolic_orientation_only`
  - `V_control_symbolic_sign_content_cross`
  - `V_control_symbolic_two_family_bounded`

## Implementation summary
- Added the approved triple-family synthetic task generator.
- Added the triple-family witness backend and the fixed five-control stack.
- Added focused tests for generator, parser, candidate, and controls.
- Executed the fixed first packet on seeds `42/123/777`.

## Validation
- Focused suite: `106 passed`

## Packet summary
- `V_future_relational_witness_triple`: mean accuracy `1.000000`, mean F1 `1.000000`
- all five approved bounded controls: mean accuracy `0.500000`, mean F1 `0.666667`

## Packet artifact
- `logs/ablation_runs/summary/triple_family_v1.csv`
