# Q-RoPE Local Observable Screening Implementation Plan v1

## Decision
The next implementation step should add configurable local readout selection for screening purposes only.

This is:
- a local screening-path infrastructure change

This is not:
- a new algorithm branch
- a new Q-RoPE novelty claim

## Minimal code changes
### 1. Extend local simulator readout selection
Primary file:
- `src/qrope/qsim.py`

Add a small readout helper layer so the final state can be scored by:
- `weighted`
- `q2`
- `parity`

Target shape:
- keep `simple_quantum_score(...)` as backward-compatible default using `weighted`
- add a readout selector parameter or thin wrapper so local screening can request:
  - `q2`
  - `parity`

### 2. Thread readout selection through the local runner
Primary file:
- `src/qrope/run.py`

Need:
- optional local config field or explicit screening override for readout choice
- no change to remote backends
- no change to variant definitions

### 3. Add focused test coverage
Primary file:
- `tests/test_qsim.py`

Need:
- deterministic coverage for `q2`
- deterministic coverage for `parity`
- confirmation that default `weighted` behavior stays intact

## Evaluation packet
Backend:
- `sim_quantum_statevector`

Variants:
- `V3`
- `V4`

Datasets:
- `yelp`
- `imdb`
- `amazon`

Seeds:
- `42`
- `123`
- `777`
- `2024`
- `9001`

Readouts:
- `weighted` baseline
- `q2`
- `parity`

## Decision criteria
An alternative readout is worth carrying forward for the local screening path only if it improves:
1. score spread or range
2. class separation or overlap behavior
3. stability across seeds

If it improves spread only, that is not enough.

## Output framing
Any result from this step must be framed as:
- local screening-path evidence

Not as:
- a new algorithm result
- a new publishability claim
- a new remote execution question

## Recommended next story
Implement the local readout selector and run the screening packet.

## Bottom line
The minimal next change is a configurable local readout layer for `weighted`, `q2`, and `parity`.
That lets us test whether the local screening path itself is worth upgrading before any future mechanism-level variant is proposed.
