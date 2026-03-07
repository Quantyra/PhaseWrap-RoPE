# Q-RoPE Post-RZ Mixing Implementation Plan v1

## Decision
Implement configurable local post-`RZ` mixing presets in the simulator path only.

This is:
- local mechanism screening infrastructure

This is not:
- a new variant branch
- a new remote backend path
- a publishability claim

## Minimal code changes
### 1. Add configurable mixing presets in the local simulator
Primary file:
- `src/qrope/qsim.py`

Need:
- preserve current baseline mixing as `mix_v0`
- add a stronger fixed-mixing preset `mix_v1`
- add a two-stage preset `mix_v2`

Recommended implementation shape:
- add a `mixing_preset` parameter to `simple_quantum_score(...)`
- route the final-state construction through a small helper that applies:
  - `mix_v0`: current single `RX(pi/4)` layer
  - `mix_v1`: stronger single-layer fixed `RX`
  - `mix_v2`: `RX`, reverse/forward entangling continuation, second `RX`

Keep the candidate set fixed at three presets.

### 2. Thread the mixing preset through the local runner
Primary file:
- `src/qrope/run.py`

Need:
- optional local backend config field such as `backend.local_mixing_preset`
- apply only to `sim_quantum_statevector`
- leave remote backends unchanged

### 3. Add focused tests
Primary files:
- `tests/test_qsim.py`
- optionally `tests/test_run_real_mode.py`

Need:
- deterministic support for all three presets
- default behavior remains the current baseline

## Evaluation packet
Primary packet:
- backend: `sim_quantum_statevector`
- variant: `V3`
- readout: `parity`
- mixing presets:
  - `mix_v0`
  - `mix_v1`
  - `mix_v2`
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
- only if a preset appears strong enough to affect a branch or future remote decision

## Decision criteria
A preset is worth carrying forward only if it improves:
1. F1 or class separation on at least two datasets
2. stability across seeds
3. worst-seed behavior

If it only increases variance or only helps one dataset, it is not enough.

## Output framing
Any result must be framed as:
- local mechanism-screening evidence on `V3`

Not as:
- a new Q-RoPE algorithm
- a remote-readiness result

## Recommended next story
Implement the configurable mixing presets and execute the zero-credit screen.

## Bottom line
The minimal next change is configurable local mixing presets on `V3` under parity readout.
That is the cleanest way to test the real unresolved mechanism question.
