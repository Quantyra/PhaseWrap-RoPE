# Token-invariant latent-state diagnostics memo

## Goal
Make token invariance a measurable gate rather than a prose requirement.

## Required latent-state diagnostic procedure
- generate one latent chart-transition state bundle before text rendering
- render at least two token-permuted views of the same latent states:
  - `identity`
  - `cdab`
- compute target values from latent chart-transition geometry only
- verify that each latent state's target value is identical across rendered token views

## Required diagnostics
- `latent_target_invariance_pass`
  - true only if target values match exactly across token-permuted views for every latent state
- `latent_render_pair_count`
  - number of latent states checked across the paired renders
- `latent_target_max_abs_delta`
  - maximum absolute target difference across token views for the same latent state
- `token_view_balance_pass`
  - true only if token-permuted renders preserve the same split sizes and latent-state counts

## Rejection rule
- reject implementation approval immediately if:
  - `latent_target_invariance_pass` is false, or
  - `latent_target_max_abs_delta` is nonzero, or
  - `token_view_balance_pass` is false

## Why this matters
This prevents the next chart-transition task from smuggling token identity back into the target through rendering or dataset assembly details.
