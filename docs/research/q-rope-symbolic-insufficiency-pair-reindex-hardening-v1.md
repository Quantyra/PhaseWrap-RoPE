# Q-RoPE Symbolic Insufficiency Pair-Reindex Hardening v1

Date: 2026-03-10
Stories: S672

## Packet
- dataset: `synthetic_symbolic_insufficiency_transition_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- perturbation: `pair_reindex=1`
- candidate: `V_future_relational_witness_symbolic_insufficiency`
- control: `V_control_symbolic_symbolic_insufficiency_regressor`

## Means
- witness:
  - mean MAE `0.184697`
  - mean rank correlation `0.917647`
  - mean calibration slope `0.915945`
- control:
  - mean MAE `0.308018`
  - mean rank correlation `-0.128199`
  - mean calibration slope `-0.259156`

## Readout
- the perturbation was non-inert; both witness and control moved relative to the base packet
- the witness still beat the frozen-basis symbolic control on both declared packet metrics across all three seeds
- generator diagnostics still passed on all six runs under `pair_reindex=1`

## Artifact
- summary: `logs/ablation_runs/summary/symbolic_insufficiency_pair1_v1.csv`
