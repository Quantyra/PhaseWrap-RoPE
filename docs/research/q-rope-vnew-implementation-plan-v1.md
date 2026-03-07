# Q-RoPE V_new Implementation Plan v1

## Decision
Implement the approved restart candidate in one minimal local phase only.

Target:
- `V_new_explicit_interference`

Scope:
- local-only
- zero-credit
- synthetic packet only

## Files allowed to change

### Primary
- [qsim.py](\\?\C:\Users\Dan\Desktop\Projects\QuantyraQRope\src\qrope\qsim.py)
- [run.py](\\?\C:\Users\Dan\Desktop\Projects\QuantyraQRope\src\qrope\run.py)
- [test_qsim.py](\\?\C:\Users\Dan\Desktop\Projects\QuantyraQRope\tests\test_qsim.py)
- [test_run_real_mode.py](\\?\C:\Users\Dan\Desktop\Projects\QuantyraQRope\tests\test_run_real_mode.py)

### New allowed support file
- `tests/test_vnew_interference.py`

### Diagnostics / docs
- one run-summary note in `docs/research/`
- run artifacts in `logs/ablation_runs/`
- one diagnostics artifact in `logs/diagnostics/`

## Files not allowed to change
- remote/cloud adapters
  - `src/qrope/qphotonic.py`
  - `src/qrope/qibm.py`
- cloud onboarding / provider docs
- benchmark dataset files outside the existing synthetic generator path
- non-synthetic experiment configs

## Required code additions

### In `qsim.py`
Add:
- a new variant path for `V_new_explicit_interference`
- explicit branch-state preparation helper if needed
- constructive-channel state construction
- destructive-channel state construction
- parity-contrast observable helper

Constraints:
- must reuse the fixed branch structure from the planning memos
- must not silently rewrite `V0`
- must keep deterministic behavior

### In `run.py`
Add:
- routing so `V_new_explicit_interference` can be evaluated on `synthetic_offset_binary`
- diagnostics emission for:
  - score-vs-offset
  - positive-minus-negative offset gap
  - overall score-level shift

Constraints:
- no remote backend support
- no broader dataset support

## Required tests

### `test_qsim.py`
Add tests for:
- deterministic constructive/destructive channel scores
- parity-contrast observable output range
- distinction between raw overlap-style behavior and the new contrast path

### `test_run_real_mode.py`
Add tests for:
- `synthetic_offset_binary` running with `V_new_explicit_interference`
- diagnostics artifact presence
- stable repeated-run metrics for the same seed/config

### `test_vnew_interference.py`
Add focused tests for:
- branch symmetry assumptions
- parity-contrast sign/range sanity
- score-shift rejection helper logic if introduced

## Required diagnostics
Per run or per packet:
- score-vs-offset curve JSON
- positive-minus-negative offset gap
- overall score mean / score-level shift
- per-seed metric summary

## Required first execution packet
After implementation, run only:
- dataset: `synthetic_offset_binary`
- seeds: `42`, `123`, `777`
- variants:
  - `V0`
  - `V_new_explicit_interference`

Do not run:
- `V3`
- remote backends
- non-synthetic datasets

## Stop conditions during implementation
Stop immediately if:
- the new comparator reduces in practice to plain overlap magnitude
- parity contrast cannot be implemented without collapsing into a score-shift proxy
- deterministic test behavior breaks

## Deliverable of this phase
Only this:
- executable local implementation of `V_new_explicit_interference`
- synthetic falsification packet results

Nothing else.

## Bottom line
The implementation phase is now narrow enough to execute without reopening the old sprawl.
If approved further, the next coding step should be exactly this plan and nothing broader.
