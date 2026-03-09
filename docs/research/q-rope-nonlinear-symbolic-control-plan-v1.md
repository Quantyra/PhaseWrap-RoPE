# Nonlinear symbolic control plan

## Motivation
The witness branch now beats all approved additive controls. The next correctness question is whether the win survives a fair bounded nonlinear symbolic baseline over the same declared analog factors.

## Next bounded control
- future control: `V_control_symbolic_nonlinear_manifold_regressor`

## Allowed information
- `sector_magnitude_delta`
- `ordered_content_delta`
- `orientation_delta`

## Allowed nonlinear terms
- one fixed nonlinear feature family derived directly from the declared task memo
- no lookup features
- no coarse tuple one-hot features
- no free-form basis expansion

## Goal
Test whether the witness win is specifically over additive controls only, or whether it still holds against one direct symbolic nonlinear control matched to the declared manifold structure.
