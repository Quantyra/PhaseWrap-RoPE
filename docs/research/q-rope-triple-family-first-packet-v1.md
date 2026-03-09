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
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`

## Fixed packet result
- `V_future_relational_witness_triple`: mean accuracy `1.000000`, mean F1 `1.000000`
- all five bounded controls: mean accuracy `0.500000`, mean F1 `0.666667`

Summary CSV:
- `logs/ablation_runs/summary/triple_family_v1.csv`

## Mechanism read
- The candidate cleared the full approved bounded control stack.
- Its coefficients were dominated by `triple_even_parity` on all three seeds.
- Representative values:
  - seed `42`: `triple_even_parity = 3.310585`
  - seed `123`: `triple_even_parity = 3.342405`
  - seed `777`: `triple_even_parity = 3.313241`

## Decision
- `GO` for one harder fairness control.
- Do not expand the task or benchmarks.
- Next bounded step: a symbolic three-family parity control on the same task.
