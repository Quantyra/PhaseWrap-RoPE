# Orthogonalized continuous implementation plan

## Approved branch
- task: `synthetic_dual_orthogonalized_continuous_response`
- candidate: `V_future_relational_witness_orthogonalized`
- controls:
  - `V_control_symbolic_coarse_lookup_regressor`
  - `V_control_symbolic_analog_only_regressor`
  - `V_control_symbolic_full_declared_residual_regressor`

## Target construction to implement
1. Compute bounded analog factors per dual sample:
- `sector_magnitude_delta in [-1, +1]`
- `ordered_content_delta in [-1, +1]`
- optional analog coupling: `sector_magnitude_delta * ordered_content_delta`

2. Form a raw analog target:
- `raw = 0.45*sector_magnitude_delta + 0.35*ordered_content_delta + 0.20*(sector_magnitude_delta*ordered_content_delta)`

3. Orthogonalize by coarse tuple:
- group by `(sign_agreement, content_agreement, orientation_agreement)`
- subtract the within-group mean `raw`
- round to fixed precision

## Control schemas
- coarse lookup regressor:
  - sees only `sign_agreement`, `content_agreement`, `orientation_agreement`
- analog-only regressor:
  - sees only `sector_magnitude_delta`, `ordered_content_delta`
- full declared residual regressor:
  - sees coarse agreement bits plus the two analog factors
  - does not receive explicit multiplicative analog coupling term

## Candidate schema
- witness features may include sector-first relational responses plus bounded analog witness summaries
- no token identity, no absolute positions, no direct tuple lookup, no pooled-score shortcut

## Writable scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- focused tests only

## Fixed first packet
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- local-only
- zero-credit
- no extra tasks or variants

## Required diagnostics
- target summary by split
- coarse-tuple means after orthogonalization
- proof that coarse-tuple mean is near zero
- proof that within-state variation remains positive
- coefficient/intercept audit for all controls and candidate
- `anti_collapse_pass`
- packet summary on primary metric: `MAE`
