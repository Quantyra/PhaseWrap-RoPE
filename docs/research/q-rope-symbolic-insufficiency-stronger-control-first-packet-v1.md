# Q-RoPE Symbolic Insufficiency Stronger-Control First Packet v1

Date: 2026-03-10
Stories: S697

## Packet
- task: `synthetic_symbolic_insufficiency_transition_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- variants:
  - `V_future_relational_witness_symbolic_insufficiency`
  - `V_control_symbolic_symbolic_insufficiency_regressor_v2`

## Per-Seed Results
- seed `42`
  - witness: `mae=0.091881`, `rank_correlation=0.987491`, `calibration_slope=0.958442`
  - stronger control: `mae=0.274743`, `rank_correlation=0.075333`, `calibration_slope=0.357402`
- seed `123`
  - witness: `mae=0.140404`, `rank_correlation=0.950000`, `calibration_slope=1.036111`
  - stronger control: `mae=0.251844`, `rank_correlation=0.369935`, `calibration_slope=0.263520`
- seed `777`
  - witness: `mae=0.126887`, `rank_correlation=0.964706`, `calibration_slope=0.974537`
  - stronger control: `mae=0.238146`, `rank_correlation=0.646021`, `calibration_slope=0.456826`

## Mean Result
- witness:
  - `mae=0.119724`
  - `rank_correlation=0.967399`
  - `calibration_slope=0.989697`
- stronger control:
  - `mae=0.254911`
  - `rank_correlation=0.363763`
  - `calibration_slope=0.359249`

## Summary Artifact
- `logs/ablation_runs/summary/symbolic_insufficiency_stronger_v1.csv`
