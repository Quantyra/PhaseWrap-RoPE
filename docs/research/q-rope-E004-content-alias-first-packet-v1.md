# Q-RoPE E004 Content-Alias First Packet v1

Date: 2026-03-15
Stories: S1398-S1401

## Fixed Packet
- dataset: `synthetic_positional_content_alias_disambiguation_response`
- witness: `V_future_relational_witness_positional_content_alias_disambiguation`
- control: `V_control_symbolic_positional_content_alias_disambiguation_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.044364`
  - `rank_correlation = 0.303365`
  - `calibration_slope = 0.812025`
- control:
  - `mae = 0.046853`
  - `rank_correlation = -0.018676`
  - `calibration_slope = -0.003839`

## Interpretation
- The witness led on both declared mean gate metrics.
- The alias-pressure task stayed bounded and auditable.
- Under the declared two-metric gate, the branch remains active.

## Summary CSV
- `logs/ablation_runs/summary/E004_content_alias_disambiguation_v1.csv`
