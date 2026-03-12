# Q-RoPE Transfer Fork-Join Slot-Swap Hardening v1

Date: 2026-03-12
Stories: S925

## Packet
- task:
  - `synthetic_symbolic_insufficiency_fork_join_response`
- perturbation:
  - `slot_swap = 1`
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`, `123`, `777`
- compared:
  - `V_future_relational_witness_symbolic_insufficiency_fork_join`
  - `V_control_symbolic_symbolic_insufficiency_fork_join_regressor`

## Mean Results
- witness:
  - `mae = 0.055123`
  - `rank_correlation = 0.529562`
  - `calibration_slope = 1.116614`
- control:
  - `mae = 0.077148`
  - `rank_correlation = 0.144751`
  - `calibration_slope = 0.287271`

## Per-Seed Result
- seed `42`
  - witness: `mae 0.037559`, `rank_correlation 0.567430`
  - control: `mae 0.061833`, `rank_correlation 0.356670`
- seed `123`
  - witness: `mae 0.065814`, `rank_correlation 0.533020`
  - control: `mae 0.100668`, `rank_correlation 0.227582`
- seed `777`
  - witness: `mae 0.061997`, `rank_correlation 0.488235`
  - control: `mae 0.068944`, `rank_correlation -0.150000`

## Interpretation
- the perturbation was non-inert
- the witness remained ahead on both declared packet metrics in the mean
- this step materially strengthened the branch relative to the earlier `pair_reindex=1` packet, so the next step should be a deeper structural perturbation rather than branch widening

## Artifact
- summary:
  - `logs/ablation_runs/summary/transfer_fork_join_slot1_v1.csv`
