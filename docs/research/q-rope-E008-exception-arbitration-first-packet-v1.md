# Q-RoPE E008 Exception Arbitration First Packet v1

Date: 2026-03-16
Stories: S1518-S1521

## Fixed Packet
- dataset: `synthetic_positional_exception_conditioned_reference_selection_response`
- witness: `V_future_relational_witness_positional_exception_conditioned_reference_selection`
- control: `V_control_symbolic_positional_exception_conditioned_reference_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.019617`
  - `rank_correlation = 0.464040`
  - `calibration_slope = 1.002274`
- control:
  - `mae = 0.023773`
  - `rank_correlation = 0.096551`
  - `calibration_slope = 0.335899`

## Interpretation
- The witness beat the bounded symbolic control on both declared mean packet metrics.
- The exception-conditioned task stayed within the frozen fairness contract.
- The line has earned exactly one next move: retained nuisance hardening with `token_permutation=cdab`.

## Summary CSV
- `logs/ablation_runs/summary/E008_exception_arbitration_v1.csv`
