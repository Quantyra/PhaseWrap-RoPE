# Transition Orbit Post Deeper Pair-Reindex Decision v1

## Decision
- stop the current transition-orbit execution branch

## Why
- protocol primary metric is mean MAE
- under `pair_reindex = 7`, the strongest symbolic baseline beat the witness on mean MAE (`0.094035` vs `0.103347`)
- stronger rank correlation was not enough to preserve the branch once the primary metric lead was lost

## Consequence
- no more execution on `synthetic_chart_transition_orbit_response`
- preserve only one next memo-level angle
