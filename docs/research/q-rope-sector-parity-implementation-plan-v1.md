# Q-RoPE Sector-Parity Implementation Plan v1

## Scope
- story: `S146`
- candidate: `V_future_sector_contrast_pairstate`
- baseline: `V0`
- task: `synthetic_sector_parity_binary`
- backend: `sim_quantum_statevector`

## Writable files
Only these files may change in the implementation phase:
- `src/qrope/synthetic.py`
- `src/qrope/qsim.py`
- `src/qrope/run.py`
- focused tests in `tests/`

No remote adapters, reports, or benchmark configs may change.

## Required implementation units
### Dataset unit
Add one new synthetic dataset mode:
- `synthetic_sector_parity_binary`

Requirements:
- reuse the existing four-sector language
- assign labels by crossed sector parity:
  - `1`: `P_small`, `N_large`
  - `0`: `N_small`, `P_large`
- keep deterministic multi-seed generation
- emit generator diagnostics proving balanced sector coverage

### Candidate unit
Add one new candidate variant:
- `V_future_sector_contrast_pairstate`

Requirements:
- remain pair-state and sector-first
- expose per-sector responses before any final statistic
- compute task-relevant contrast for the sector-parity task

### Baseline unit
Reuse:
- `V0`

No new baselines are allowed.

## Required diagnostics
Each run must emit:
- `score_by_sector`
- `task_contrast_mean`
- `sector_responses`
- `sector_resolution_pre_aggregation`
- `anti_collapse_pass`
- multi-seed packet summary fields sufficient to compare with `V0`

## Required tests
Add focused tests for:
- deterministic `synthetic_sector_parity_binary` generation
- correct crossed-label assignment
- candidate result exposing sector responses before aggregation
- run diagnostics carrying `task_contrast_mean`

## Packet boundary
The first and only implementation packet after code lands must be:
- seeds `42`, `123`, `777`
- `V0` vs `V_future_sector_contrast_pairstate`
- `sim_quantum_statevector`

No additional packet is approved in the same story.

## Stop conditions
Stop immediately if implementation pressure creates any of:
- pooled-score shortcut instead of sector-first measurement
- second candidate branch
- benchmark expansion
- remote execution hooks

## Next step
Implement the bounded sector-parity path and execute only the fixed first packet.
