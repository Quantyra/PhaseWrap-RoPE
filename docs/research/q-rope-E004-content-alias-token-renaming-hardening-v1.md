# Q-RoPE E004 Content-Alias Token-Renaming Hardening v1

Date: 2026-03-15
Stories: S1402-S1404

## Fixed Hardening Packet
- dataset: `synthetic_positional_content_alias_disambiguation_response`
- witness: `V_future_relational_witness_positional_content_alias_disambiguation`
- control: `V_control_symbolic_positional_content_alias_disambiguation_regressor`
- backend: `sim_quantum_statevector`
- token permutation: `cdab`
- seeds: `42`, `123`, `777`

## Mean Hardening Results
- witness:
  - `mae = 0.042089`
  - `rank_correlation = 0.353312`
  - `calibration_slope = 0.813013`
- control:
  - `mae = 0.047922`
  - `rank_correlation = -0.002872`
  - `calibration_slope = -0.134676`

## Interpretation
- `token_permutation=cdab` was non-inert.
- The witness remained ahead on both declared mean gate metrics.
- The content-alias line strengthened relative to the first packet under retained nuisance hardening.

## Summary CSV
- `logs/ablation_runs/summary/E004_content_alias_disambiguation_cdab_v1.csv`
