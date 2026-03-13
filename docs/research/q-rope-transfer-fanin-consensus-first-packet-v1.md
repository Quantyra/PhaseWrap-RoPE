# Q-RoPE Transfer Fan-In Consensus First Packet v1

## Packet
- Task: `synthetic_symbolic_insufficiency_fanin_consensus_response`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Models:
  - `V_future_relational_witness_symbolic_insufficiency_fanin_consensus`
  - `V_control_symbolic_symbolic_insufficiency_fanin_consensus_regressor`

## Mean Results
- Witness:
  - `mae = 0.106825`
  - `rank_correlation = -0.463037`
  - `calibration_slope = -0.415472`
- Control:
  - `mae = 0.150056`
  - `rank_correlation = -0.269809`
  - `calibration_slope = -0.019376`

## Interpretation
- The declared packet metrics for this line are:
  - `mae`
  - `rank_correlation`
- On both declared packet metrics, the witness led the bounded symbolic control in the mean.
- The packet is still weakly conditioned:
  - both variants have negative mean `rank_correlation`
  - so the line should advance only to one bounded nuisance hardening step, not broader expansion

## Artifact
- Summary CSV: `logs/ablation_runs/summary/transfer_fanin_consensus_v1.csv`
