# Q-RoPE Interference-Tail Screening Implementation Plan v1

## Decision
Implement exactly one additional local screening tail on the `V3` path:

- baseline tail: current `mix_v0`
- candidate tail: `mix_it1`

This keeps the branch narrow and testable.

## Minimal code boundary
Primary file:
- `src/qrope/qsim.py`

Required changes:
1. extend supported local tail presets to include `mix_it1`
2. implement one local Hadamard-style basis-change layer helper
3. route `mix_it1` through:
   - current forward CNOT chain
   - global `RX(pi/4)` layer
   - basis-change layer on all qubits
   - reverse CNOT chain
4. leave:
   - feature loading unchanged
   - `RZ` schedule unchanged
   - variant definitions unchanged

Secondary file:
- `src/qrope/run.py`

Required changes:
- no new conceptual path
- only allow the new preset to flow through the existing `local_mixing_preset` plumbing

## Locked evaluation packet
Primary packet:
- backend: `sim_quantum_statevector`
- variant: `V3`
- readout: `parity`
- tails:
  - `mix_v0`
  - `mix_it1`
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

Weighted shadow:
- required only if parity results are strong enough to threaten a branch change

## Promotion gate
Carry `mix_it1` forward only if it satisfies at least two:
1. improves mean F1 on at least two datasets vs `mix_v0 + parity`
2. lowers seed variance on at least two datasets
3. improves worst-seed F1 on at least two datasets

And:
- weighted shadow must not reverse the conclusion on both `yelp` and `amazon`

If the gate fails:
- stop this branch
- keep `mix_v0`
- do not reopen remote spend

## Test boundary
Focused tests only:
- `tests/test_qsim.py`
- `tests/test_run_real_mode.py`

Need:
- support for `mix_it1`
- deterministic scoring
- runner metadata still reflects readout and preset correctly

## Explicitly out of scope
- more than one new tail
- new readout types
- remote backend changes
- new variant naming

## Bottom line
The implementation should add one candidate interference-sensitive tail and nothing else.
That is the smallest code change that can answer the broader redesign question cleanly.
