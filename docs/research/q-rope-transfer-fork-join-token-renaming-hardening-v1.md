# Q-RoPE Transfer Fork-Join Token-Renaming Hardening v1

Date: 2026-03-12
Stories: S919

## Packet
- task:
  - `synthetic_symbolic_insufficiency_fork_join_response`
- perturbation:
  - `token_permutation = cdab`
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`, `123`, `777`
- compared:
  - `V_future_relational_witness_symbolic_insufficiency_fork_join`
  - `V_control_symbolic_symbolic_insufficiency_fork_join_regressor`

## Mean Results
- witness:
  - `mae = 0.079036`
  - `rank_correlation = 0.323721`
  - `calibration_slope = 0.793774`
- control:
  - `mae = 0.089465`
  - `rank_correlation = 0.111353`
  - `calibration_slope = 0.528132`

## Per-Seed Result
- seed `42`
  - witness: `mae 0.046418`, `rank_correlation 0.664706`
  - control: `mae 0.087556`, `rank_correlation -0.191176`
- seed `123`
  - witness: `mae 0.105324`, `rank_correlation 0.250368`
  - control: `mae 0.101661`, `rank_correlation 0.103093`
- seed `777`
  - witness: `mae 0.085367`, `rank_correlation 0.056089`
  - control: `mae 0.079179`, `rank_correlation 0.422143`

## Interpretation
- the perturbation was non-inert
- the witness remained ahead on both declared packet metrics in the mean
- the margin narrowed versus the base fork-join packet, so the next step should be structural hardening rather than widening the family

## Artifact
- summary:
  - `logs/ablation_runs/summary/transfer_fork_join_cdab_v1.csv`
