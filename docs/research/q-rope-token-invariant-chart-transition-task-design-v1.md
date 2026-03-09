# Token-permutation-safe chart-transition task design

## Goal
Preserve one next memo-only direction that removes token-convention sensitivity from the chart-transition line.

## Preserved next angle
- `synthetic_chart_transition_token_invariant_response`

## Design requirement
- task target must depend on chart-transition geometry only
- token identities must be nuisance variables by construction
- fixed token permutations should leave the target and the witness-control ordering invariant if the mechanism is real

## Why this is the right next memo angle
The chart-transition line produced the strongest bounded fairness results in the current manifold program, but the token-renaming hardening showed that the current task still mixes chart-transition structure with token convention. The next legitimate continuation is therefore a task redesign that removes token convention as a latent shortcut rather than another execution pass on the same task.
