# Q-RoPE Pair-State Implementation Plan v1

## Scope
- Story: `S128`
- Approved variant: `V_pairstate_relational`
- Boundary:
  - local-only
  - `synthetic_offset_binary` only
  - seeds `42/123/777` only for the first packet
  - no remote code path changes
  - no broader benchmark changes

## Exact files to change
1. `src/qrope/qsim.py`
- add `V_pairstate_relational` support
- implement pair-state content/sector/coupling state construction
- implement sector-resolved signed-response measurement
- keep anti-collapse behavior explicit in helper structure

2. `src/qrope/run.py`
- thread the new variant through the local synthetic path only
- emit pair-state run diagnostics:
  - sector responses
  - signed contrast
  - magnitude-balance
  - offset-gap summary
- do not touch remote backend paths

3. `tests/test_qsim.py`
- add focused construction and sector-response tests

4. `tests/test_run_real_mode.py`
- add focused runner-path coverage for `V_pairstate_relational`

5. optional, only if needed:
- `tests/test_vnew_interference.py`
  - do not repurpose unless there is shared helper value

## Exact files not allowed to change
- `src/qrope/qphotonic.py`
- `src/qrope/qibm.py`
- cloud onboarding scripts
- benchmark config families outside the bounded pair-state path

## Variant/config approach
- do not create multiple pair-state variants
- use one variant id:
  - `V_pairstate_relational`
- if a config file is needed, it should be one bounded config only

## Required diagnostics per run
- per-sector responses:
  - `P_small`
  - `P_large`
  - `N_small`
  - `N_large`
- signed contrast
- magnitude-balance
- positive-minus-negative offset gap
- explicit marker proving sector resolution happened before aggregation

## Required tests
- deterministic pair-state construction for same input/seed
- ordered token-pair content distinction:
  - `(A, B)` differs from `(B, A)`
- sector assignment sanity for positive vs negative offsets
- no-pooled-scalar shortcut in the pair-state local path
- runner emits the expected pair-state diagnostics structure

## First execution packet after implementation
- `V0` vs `V_pairstate_relational`
- dataset: `synthetic_offset_binary`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- no remote execution

## Stop conditions
- stop immediately if implementation collapses back into pooled scalar scoring before sector resolution
- stop immediately if diagnostics cannot expose per-sector responses
- stop immediately if code changes drift into remote or benchmark-expansion paths

## Bottom line
The implementation boundary is intentionally narrow.
If `V_pairstate_relational` cannot show mechanism signal inside this boundary, the branch should stop without expansion.

