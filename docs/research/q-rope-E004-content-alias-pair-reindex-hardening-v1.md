# Q-RoPE E004 Content-Alias Pair-Reindex Hardening v1

Date: 2026-03-15
Stories: S1405-S1407

## Fixed Hardening Packet
- dataset: `synthetic_positional_content_alias_disambiguation_response`
- witness: `V_future_relational_witness_positional_content_alias_disambiguation`
- control: `V_control_symbolic_positional_content_alias_disambiguation_regressor`
- backend: `sim_quantum_statevector`
- pair reindex: `1`
- seeds: `42`, `123`, `777`

## Mean Hardening Results
- witness:
  - `mae = 0.044752`
  - `rank_correlation = 0.417230`
  - `calibration_slope = 1.115544`
- control:
  - `mae = 0.053455`
  - `rank_correlation = 0.013500`
  - `calibration_slope = 0.019226`

## Interpretation
- `pair_reindex=1` was non-inert.
- The witness remained ahead on both declared mean gate metrics.
- The first structural packet strengthened the line under active alias pressure.

## Summary CSV
- `logs/ablation_runs/summary/E004_content_alias_disambiguation_pair1_v1.csv`
