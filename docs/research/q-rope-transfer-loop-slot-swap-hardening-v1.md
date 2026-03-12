# Q-RoPE Transfer Loop-Closure Slot-Swap Hardening v1

Date: 2026-03-11
Stories: S895

## Packet
- task:
  - `synthetic_symbolic_insufficiency_loop_closure_response`
- perturbation:
  - `slot_swap = 1`
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`, `123`, `777`
- compared:
  - `V_future_relational_witness_symbolic_insufficiency_loop`
  - `V_control_symbolic_symbolic_insufficiency_loop_regressor`

## Mean Results
- witness:
  - `mae = 0.057070`
  - `rank_correlation = 0.279495`
  - `calibration_slope = 0.318141`
- control:
  - `mae = 0.079051`
  - `rank_correlation = 0.089562`
  - `calibration_slope = 0.056989`

## Interpretation
- the perturbation was non-inert
- the witness stayed ahead on both declared packet metrics in the mean
- one seed (`42`) favored the control on rank correlation, but the control did not clear the two-metric gate overall
- this supports keeping the branch active while moving to one deeper structural perturbation

## Artifact
- summary:
  - `logs/ablation_runs/summary/transfer_loop_slot1_v1.csv`
