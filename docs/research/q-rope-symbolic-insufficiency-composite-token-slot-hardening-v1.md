# Q-RoPE Symbolic Insufficiency Composite Token-Slot Hardening v1

Date: 2026-03-10
Stories: S678

## Packet
- dataset: `synthetic_symbolic_insufficiency_transition_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- perturbations:
  - `token_permutation=cdab`
  - `slot_swap=1`
- candidate: `V_future_relational_witness_symbolic_insufficiency`
- control: `V_control_symbolic_symbolic_insufficiency_regressor`

## Means
- witness:
  - mean MAE `0.146614`
  - mean rank correlation `0.878177`
  - mean calibration slope `0.928210`
- control:
  - mean MAE `0.251269`
  - mean rank correlation `0.257014`
  - mean calibration slope `2.231281`

## Readout
- the composite perturbation was non-inert; both witness and control moved relative to the single-axis hardening packets
- the witness still beat the frozen-basis symbolic control on both declared packet metrics across all three seeds
- generator diagnostics still passed on all six runs under the composite perturbation

## Artifact
- summary: `logs/ablation_runs/summary/symbolic_insufficiency_cdab_slot1_v1.csv`
