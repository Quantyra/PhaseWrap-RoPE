# Local atlas manifold first packet

## Packet
- task: `synthetic_dual_local_atlas_manifold_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- compared candidate plus six fixed controls

## Mean results
- `V_future_relational_witness_local_atlas`
  - MAE: `0.192108`
  - rank correlation: `0.875911`
  - calibration slope: `0.849456`
- `V_control_symbolic_coarse_lookup_regressor`
  - MAE: `0.233384`
  - rank correlation: `0.000000`
  - calibration slope: `-1.340060`
- `V_control_symbolic_analog_only_regressor`
  - MAE: `0.236167`
  - rank correlation: `-0.022038`
  - calibration slope: `-1.938809`
- `V_control_symbolic_nonlinear_manifold_regressor`
  - MAE: `0.183625`
  - rank correlation: `0.857131`
  - calibration slope: `0.741240`
- `V_control_symbolic_phase_insensitive_regressor`
  - MAE: `0.181260`
  - rank correlation: `0.864980`
  - calibration slope: `0.685709`
- `V_control_symbolic_global_phase_regressor`
  - MAE: `0.223408`
  - rank correlation: `0.507578`
  - calibration slope: `1.154891`
- `V_control_symbolic_single_chart_regressor`
  - MAE: `0.183422`
  - rank correlation: `0.849189`
  - calibration slope: `0.717246`

## Interpretation
- the candidate beat the coarse lookup, analog-only, and bounded global-phase controls
- the candidate did not beat the nonlinear manifold, phase-insensitive, or single-chart controls on the primary metric
- the current task is therefore not strong enough to support a witness-specific claim
