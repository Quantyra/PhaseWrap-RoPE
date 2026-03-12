# Q-RoPE Transfer Fork-Join Pair-Reindex Hardening v1

Date: 2026-03-12
Stories: S922

## Packet
- task:
  - `synthetic_symbolic_insufficiency_fork_join_response`
- perturbation:
  - `pair_reindex = 1`
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`, `123`, `777`
- compared:
  - `V_future_relational_witness_symbolic_insufficiency_fork_join`
  - `V_control_symbolic_symbolic_insufficiency_fork_join_regressor`

## Mean Results
- witness:
  - `mae = 0.119703`
  - `rank_correlation = 0.055304`
  - `calibration_slope = -0.023360`
- control:
  - `mae = 0.126384`
  - `rank_correlation = -0.284804`
  - `calibration_slope = -0.679777`

## Per-Seed Result
- seed `42`
  - witness: `mae 0.072805`, `rank_correlation 0.314706`
  - control: `mae 0.072994`, `rank_correlation -0.111765`
- seed `123`
  - witness: `mae 0.179530`, `rank_correlation -0.119381`
  - control: `mae 0.157892`, `rank_correlation -0.666177`
- seed `777`
  - witness: `mae 0.106775`, `rank_correlation -0.029412`
  - control: `mae 0.148267`, `rank_correlation -0.076471`

## Interpretation
- the perturbation was non-inert
- the witness remained ahead on both declared packet metrics in the mean
- the rank-correlation lead narrowed sharply, so the next step should continue structural hardening rather than claim stable transfer strength

## Artifact
- summary:
  - `logs/ablation_runs/summary/transfer_fork_join_pair1_v1.csv`
