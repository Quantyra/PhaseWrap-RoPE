# Q-RoPE Pairwise Relative-Overlap Screening Implementation v1

## Scope
This step implemented a local pairwise-overlap diagnostic path beside the current proxy score.

Compared:
- scoring modes:
  - `proxy`
  - `pairwise_overlap`
- variants:
  - `V0`
  - `V3`
- datasets:
  - `yelp`
  - `imdb`
  - `amazon`
- seeds:
  - `42`
  - `123`
  - `777`

Credit status:
- `0` additional Quandela credits consumed

## Implementation
Updated:
- `src/qrope/qsim.py`
- `tests/test_qsim.py`

Added:
- reusable state-preparation helper
- normalized state-overlap helper
- `pairwise_quantum_score(...)`

No remote backend behavior changed.

## Validation
- focused tests: `39 passed`

## Diagnostic summary
Source:
- `logs/ablation_runs/summary/pairwise_diag_v1.csv`

### Proxy path
The existing proxy still differentiates `V0` and `V3` on part of the packet.

Examples:
- `yelp`
  - `V0`: acc `0.583`, F1 `0.522`
  - `V3`: acc `0.667`, F1 `0.606`
- `imdb`
  - `V0`: acc `0.292`, F1 `0.265`
  - `V3`: acc `0.458`, F1 `0.433`

### Pairwise-overlap path
The pairwise path produced no variant separation at all on this first packet.

For every dataset:
- `V0` and `V3` matched exactly in aggregate metrics

Examples:
- `yelp`
  - `V0`: acc `0.500`, F1 `0.444`
  - `V3`: acc `0.500`, F1 `0.444`
- `imdb`
  - `V0`: acc `0.583`, F1 `0.500`
  - `V3`: acc `0.583`, F1 `0.500`
- `amazon`
  - `V0`: acc `0.500`, F1 `0.464`
  - `V3`: acc `0.500`, F1 `0.464`

## Promotion-gate result
Decision: `NO-GO`

Gate status:
1. clearer `V3` vs `V0` separation than the current proxy path:
   - `fail`
2. lower seed-instability than the current proxy path:
   - `fail`
3. more interpretable relative-phase behavior:
   - `fail`

## Interpretation
This was the right technical branch to test.
It also failed quickly and informatively.

The issue is not that pairwise comparison is a bad idea in principle.
The issue is that this first local pairwise-overlap approximation did not express useful variant sensitivity on the current packet.

That means:
- we should not widen this redesign branch immediately
- we should not spend remote budget on it
- the core-scoring redesign branch should now be reassessed just as the earlier local redesign branch was

## Bottom line
The first pairwise-relative-overlap implementation did not improve the program.
It did not even separate `V3` from `V0` on the diagnostic packet.
That is a clean stop signal for this first pass.
