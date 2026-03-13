# Q-RoPE Transfer Fan-In Consensus Token-Renaming Hardening v1

Status: completed

Packet:
- task: `synthetic_symbolic_insufficiency_fanin_consensus_response`
- perturbation: `token_permutation=cdab`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- retained models:
  - `V_future_relational_witness_symbolic_insufficiency_fanin_consensus`
  - `V_control_symbolic_symbolic_insufficiency_fanin_consensus_regressor`

Hardening packet means:
- witness:
  - `mae = 0.081235`
  - `rank_correlation = 0.115789`
  - `calibration_slope = 0.270569`
- control:
  - `mae = 0.072069`
  - `rank_correlation = 0.175342`
  - `calibration_slope = 0.458694`

Interpretation:
- The perturbation was non-inert.
- Under `token_permutation=cdab`, the bounded symbolic control overtook the witness on both declared packet metrics in the mean.
- That stops the `fanin-consensus` execution branch under the active hardening rule.
