# Q-RoPE Pairwise Relative-Overlap Implementation Plan v1

## Decision
Implement one local pairwise screening path without replacing the current proxy path yet.

Keep:
- current single-state proxy path as the local baseline

Add:
- one pairwise-overlap path for diagnostics

## Minimal implementation boundary
Primary file:
- `src/qrope/qsim.py`

Required additions:
1. factor state preparation into a reusable helper, e.g.:
   - `build_quantum_state(...)`
2. add one pairwise comparison helper, e.g.:
   - `pairwise_quantum_score(text_a, text_b, variant, seed, ...)`
3. use a normalized overlap-like score derived from the two final statevectors

Keep fixed for the first pass:
- existing feature loading
- existing positional phase schedule
- existing baseline tail choice (`mix_v0`)
- no new variant definitions

Secondary file:
- `src/qrope/run.py`

Required additions:
- no broad runner refactor yet
- only add a minimal local diagnostic path or helper callable if needed for the first packet

## Locked diagnostic packet
Goal:
- compare the old proxy score and the new pairwise score on the smallest useful diagnostic packet

Packet:
- backend: local statevector only
- variants:
  - `V0`
  - `V3`
- scoring modes:
  - current proxy
  - pairwise overlap
- datasets:
  - `yelp`
  - `imdb`
  - `amazon`
- seeds:
  - `42`
  - `123`
  - `777`

This stays diagnostic on purpose.

## Minimal evaluation structure
Use a simple class-prototype style comparison:
1. build class prototypes from train split using the current local path
2. score test items against class prototypes using pairwise overlap
3. compare `V0` vs `V3` behavior against the current single-state proxy baseline

This is still a proxy task, but it is much closer to an actual comparison primitive than the current scalar-only path.

## Promotion gate
Carry the redesign forward only if at least one is true:
1. `V3` separates from `V0` more clearly than under the current proxy path
2. seed behavior is less erratic than the current proxy path
3. score behavior is more interpretable relative to the original relative-phase thesis

If none hold:
- stop the redesign
- do not widen benchmark scope

## Tests
Focused tests only:
- `tests/test_qsim.py`
- `tests/test_run_real_mode.py` if runner plumbing changes

Need:
- deterministic pairwise score
- normalized score range
- identical-input behavior sanity check

## Explicitly out of scope
- remote execution
- new benchmark family
- more than one pairwise scoring family
- replacing the main runner end-to-end in the same step

## Bottom line
The next code step should add one pairwise-overlap diagnostic path beside the current proxy path.
That is the smallest faithful implementation of the new scoring branch.
