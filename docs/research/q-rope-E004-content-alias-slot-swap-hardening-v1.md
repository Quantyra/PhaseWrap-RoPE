# Q-RoPE E004 Content-Alias Slot-Swap Hardening v1

Date: 2026-03-15
Stories: S1408-S1410

## Fixed Hardening Packet
- dataset: `synthetic_positional_content_alias_disambiguation_response`
- witness: `V_future_relational_witness_positional_content_alias_disambiguation`
- control: `V_control_symbolic_positional_content_alias_disambiguation_regressor`
- backend: `sim_quantum_statevector`
- slot swap: `1`
- seeds: `42`, `123`, `777`

## Mean Hardening Results
- witness:
  - `mae = 0.049824`
  - `rank_correlation = 0.269658`
  - `calibration_slope = 0.844474`
- control:
  - `mae = 0.051691`
  - `rank_correlation = 0.181735`
  - `calibration_slope = 0.628466`

## Interpretation
- `slot_swap=1` was non-inert.
- The witness remained ahead on both declared mean gate metrics.
- The second structural packet preserved the line under alias-pressure slot perturbation.

## Summary CSV
- `logs/ablation_runs/summary/E004_content_alias_disambiguation_slot1_v1.csv`
