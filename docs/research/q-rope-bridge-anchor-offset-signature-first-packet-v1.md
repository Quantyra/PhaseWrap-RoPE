# Q-RoPE Bridge Anchor-Offset-Signature First Packet v1

## Fixed Packet
- dataset: `synthetic_positional_anchor_offset_signature_response`
- witness: `V_future_relational_witness_positional_anchor_offset_signature`
- control: `V_control_symbolic_positional_anchor_offset_signature_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.084740`
  - `rank_correlation = 0.166087`
  - `calibration_slope = 0.239691`
- control:
  - `mae = 0.082069`
  - `rank_correlation = 0.086957`
  - `calibration_slope = 0.123508`

## Per-Seed Results
- witness:
  - `42`: `mae 0.114805`, `rank_correlation 0.203478`, `calibration_slope 0.147230`
  - `123`: `mae 0.078590`, `rank_correlation 0.141739`, `calibration_slope 0.399475`
  - `777`: `mae 0.060825`, `rank_correlation 0.153043`, `calibration_slope 0.172369`
- control:
  - `42`: `mae 0.112200`, `rank_correlation 0.106087`, `calibration_slope 0.042721`
  - `123`: `mae 0.080624`, `rank_correlation -0.037391`, `calibration_slope 0.155090`
  - `777`: `mae 0.053382`, `rank_correlation 0.192174`, `calibration_slope 0.172712`
