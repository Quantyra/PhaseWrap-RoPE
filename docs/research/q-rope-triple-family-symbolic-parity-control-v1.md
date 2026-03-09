# Research note

## Scope
- Control: `V_control_symbolic_three_family_parity`
- Task: `synthetic_dual_content_parity_coupling_binary`
- Packet: candidate vs control, seeds `42/123/777`

## Result
- `V_future_relational_witness_triple`: mean accuracy `1.000000`, mean F1 `1.000000`
- `V_control_symbolic_three_family_parity`: mean accuracy `1.000000`, mean F1 `1.000000`

## Interpretation
- The stronger symbolic parity control matched the candidate exactly.
- The candidate's first-packet win is real relative to weaker controls.
- But uniqueness on this task is exhausted.

## Mechanism read
- Candidate coefficients were dominated by `triple_even_parity`.
- The symbolic control uses exactly that same explicit parity variable.
- This is the same pattern that exhausted earlier agreement-based tasks.

## Artifact
- `logs/ablation_runs/summary/triple_family_parity_control_v1.csv`
