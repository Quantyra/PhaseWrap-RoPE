# Q-RoPE Symbolic Insufficiency Composite Token-Deep-Pair Hardening v1

Date: 2026-03-10
Stories: S680

## Packet
- dataset: `synthetic_symbolic_insufficiency_transition_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- perturbations:
  - `token_permutation=cdab`
  - `pair_reindex=7`
- candidate: `V_future_relational_witness_symbolic_insufficiency`
- control: `V_control_symbolic_symbolic_insufficiency_regressor`

## Means
- witness:
  - mean MAE `0.124338`
  - mean rank correlation `0.909266`
  - mean calibration slope `0.944314`
- control:
  - mean MAE `0.285511`
  - mean rank correlation `0.338063`
  - mean calibration slope `0.690321`

## Readout
- the composite perturbation was non-inert and the witness remained clearly ahead of the frozen-basis symbolic control on both declared packet metrics
- this packet is stronger than the earlier token-plus-slot packet on both witness MAE and witness rank correlation
- generator diagnostics still passed on all six runs under the composite perturbation

## Artifact
- summary: `logs/ablation_runs/summary/symbolic_insufficiency_cdab_pair7_v1.csv`
