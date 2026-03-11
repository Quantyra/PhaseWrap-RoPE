# Q-RoPE Symbolic Insufficiency Composite Slot-Deep-Pair Hardening v1

Date: 2026-03-10
Stories: S682

## Packet
- dataset: `synthetic_symbolic_insufficiency_transition_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- perturbations:
  - `slot_swap=1`
  - `pair_reindex=7`
- candidate: `V_future_relational_witness_symbolic_insufficiency`
- control: `V_control_symbolic_symbolic_insufficiency_regressor`

## Means
- witness:
  - mean MAE `0.140609`
  - mean rank correlation `0.865368`
  - mean calibration slope `0.860233`
- control:
  - mean MAE `0.360147`
  - mean rank correlation `0.033087`
  - mean calibration slope `-0.118595`

## Readout
- the remaining composite structural perturbation was non-inert
- the witness still beat the frozen-basis symbolic control on both declared packet metrics across all three seeds
- this completes the current bounded hardening matrix for the symbolic-insufficiency branch

## Artifact
- summary: `logs/ablation_runs/summary/symbolic_insufficiency_slot1_pair7_v1.csv`
