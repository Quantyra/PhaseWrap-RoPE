# Q-RoPE Interference-Tail Screening Implementation v1

## Scope
This step implemented one broader local redesign candidate:
- `mix_it1`

Compared against:
- `mix_v0`

Screened path:
- backend: `sim_quantum_statevector`
- variant: `V3`
- readout: `parity`
- datasets:
  - `yelp`
  - `imdb`
  - `amazon`
- seeds:
  - `42`
  - `123`
  - `777`
  - `2024`
  - `9001`

Credit status:
- `0` additional Quandela credits consumed

## Implementation
Updated:
- `src/qrope/qsim.py`
- `tests/test_qsim.py`
- `tests/test_run_real_mode.py`

Added:
- a single Hadamard-style basis-change layer helper
- one new local tail preset: `mix_it1`

No remote backend behavior changed.

## Validation
- focused tests: `35 passed`

## Parity packet summary
Source:
- `logs/ablation_runs/summary/itail_parity_v1.csv`

### `yelp`
- `mix_v0`: acc `0.600`, std `0.122`; F1 `0.567`, std `0.131`; worst F1 `0.400`
- `mix_it1`: acc `0.400`, std `0.184`; F1 `0.387`, std `0.317`; worst F1 `0.000`

Read:
- strong regression
- no stability gain

### `imdb`
- `mix_v0`: acc `0.475`, std `0.146`; F1 `0.463`, std `0.065`; worst F1 `0.400`
- `mix_it1`: acc `0.525`, std `0.184`; F1 `0.527`, std `0.180`; worst F1 `0.250`

Read:
- mean performance improved
- seed variance worsened
- worst-seed behavior worsened

### `amazon`
- `mix_v0`: acc `0.475`, std `0.146`; F1 `0.383`, std `0.205`; worst F1 `0.000`
- `mix_it1`: acc `0.500`, std `0.079`; F1 `0.248`, std `0.220`; worst F1 `0.000`

Read:
- mean accuracy improved slightly
- mean F1 regressed materially

## Promotion-gate result
Decision: `NO-GO`

Gate status:
1. improves mean F1 on at least two datasets:
   - `fail`
2. lowers seed variance on at least two datasets:
   - `fail`
3. improves worst-seed F1 on at least two datasets:
   - `fail`

Because the parity packet did not produce a branch-changing positive result:
- weighted shadow was not triggered

## Interpretation
The broader redesign candidate answered the branch question cleanly:
- a shallow interference-sensitive tail can alter the signal
- but this specific redesign is not a reliable improvement over the current baseline

This is not a near miss.
The result is negative enough that the local redesign branch should be reassessed before opening another tail candidate.

## Bottom line
`mix_it1` is not worth carrying forward.
The next protocol step should be a local-screening-branch reassessment, not another immediate redesign candidate and not remote spend.
