# Q-RoPE E004 Content-Alias Deeper Pair-Reindex Hardening v1

Date: 2026-03-15
Stories: S1411-S1414

## Fixed Hardening Packet
- dataset: `synthetic_positional_content_alias_disambiguation_response`
- witness: `V_future_relational_witness_positional_content_alias_disambiguation`
- control: `V_control_symbolic_positional_content_alias_disambiguation_regressor`
- backend: `sim_quantum_statevector`
- pair reindex: `7`
- seeds: `42`, `123`, `777`

## Mean Hardening Results
- witness:
  - `mae = 0.045704`
  - `rank_correlation = 0.195134`
  - `calibration_slope = 0.600702`
- control:
  - `mae = 0.048482`
  - `rank_correlation = 0.053014`
  - `calibration_slope = -0.181309`

## Interpretation
- `pair_reindex=7` was non-inert.
- The witness remained ahead on both declared mean gate metrics.
- The closure packet left the content-alias line preserved rather than reopening wider perturbation churn.

## Summary CSV
- `logs/ablation_runs/summary/E004_content_alias_disambiguation_pair7_v1.csv`
