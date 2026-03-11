# Q-RoPE Symbolic Insufficiency Slot-Swap Hardening v1

Date: 2026-03-10
Stories: S674

## Packet
- dataset: `synthetic_symbolic_insufficiency_transition_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- perturbation: `slot_swap=1`
- candidate: `V_future_relational_witness_symbolic_insufficiency`
- control: `V_control_symbolic_symbolic_insufficiency_regressor`

## Means
- witness:
  - mean MAE `0.162977`
  - mean rank correlation `0.873250`
  - mean calibration slope `0.925510`
- control:
  - mean MAE `0.248957`
  - mean rank correlation `0.407700`
  - mean calibration slope `0.823956`

## Readout
- the perturbation was non-inert; both witness and control moved relative to the earlier packets
- the witness still beat the frozen-basis symbolic control on both declared packet metrics across all three seeds
- generator diagnostics still passed on all six runs under `slot_swap=1`

## Artifact
- summary: `logs/ablation_runs/summary/symbolic_insufficiency_slot1_v1.csv`
