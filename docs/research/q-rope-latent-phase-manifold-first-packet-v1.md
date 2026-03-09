# Latent phase manifold first packet

## Packet
- task: `synthetic_dual_latent_phase_manifold_residual_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- compared candidate plus five fixed controls

## Mean results
- `V_future_relational_witness_latent_phase`
  - MAE: `0.297610`
  - rank correlation: `0.878484`
  - calibration slope: `0.741769`
- `V_control_symbolic_coarse_lookup_regressor`
  - MAE: `0.281352`
  - rank correlation: `0.082107`
  - calibration slope: `-0.119706`
- `V_control_symbolic_analog_only_regressor`
  - MAE: `0.242432`
  - rank correlation: `0.457033`
  - calibration slope: `0.519017`
- `V_control_symbolic_nonlinear_manifold_regressor`
  - MAE: `0.209603`
  - rank correlation: `0.895327`
  - calibration slope: `0.835990`
- `V_control_symbolic_phase_insensitive_regressor`
  - MAE: `0.286697`
  - rank correlation: `0.907907`
  - calibration slope: `0.662117`
- `V_control_symbolic_global_phase_regressor`
  - MAE: `0.248360`
  - rank correlation: `0.525370`
  - calibration slope: `0.744383`

## Interpretation
- the candidate beat the coarse lookup baseline on rank and beat the phase-insensitive baseline on mean MAE
- the candidate did not beat the analog-only, nonlinear manifold, or global-phase controls on the primary metric
- the current task is therefore not strong enough to support a witness-specific claim
