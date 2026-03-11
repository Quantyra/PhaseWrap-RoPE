# Q-RoPE Symbolic Insufficiency Deeper Pair-Reindex Hardening v1

Date: 2026-03-10
Stories: S676

## Packet
- dataset: `synthetic_symbolic_insufficiency_transition_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- perturbation: `pair_reindex=7`
- candidate: `V_future_relational_witness_symbolic_insufficiency`
- control: `V_control_symbolic_symbolic_insufficiency_regressor`

## Means
- witness:
  - mean MAE `0.131687`
  - mean rank correlation `0.952691`
  - mean calibration slope `0.988831`
- control:
  - mean MAE `0.262611`
  - mean rank correlation `0.277690`
  - mean calibration slope `0.648798`

## Readout
- the perturbation was non-inert and the witness remained clearly ahead of the frozen-basis symbolic control on both declared packet metrics
- compared with the `pair_reindex=1` packet, the deeper perturbation improved the witness mean MAE and mean rank correlation
- generator diagnostics still passed on all six runs under `pair_reindex=7`

## Artifact
- summary: `logs/ablation_runs/summary/symbolic_insufficiency_pair7_v1.csv`
