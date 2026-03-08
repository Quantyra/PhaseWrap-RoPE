# Q-RoPE Archive Handoff Index v1

## Repository posture
- Current state: `paused`
- Usage mode: `internal archive`
- Active experimentation: `not allowed`

## Read first
1. `docs/research/q-rope-internal-executive-archive-summary-v1.md`
2. `docs/research/q-rope-archive-posture-v1.md`
3. `docs/research/q-rope-final-salvage-pause-memo-v1.md`

## Key decision documents
- Final bounded restart stop:
  - `docs/research/q-rope-vnew-synthetic-decision-memo-v1.md`
- Bounded restart packet:
  - `docs/research/q-rope-first-vnew-synthetic-packet-v1.md`
- Approved restart brief template:
  - `docs/research/q-rope-future-restart-brief-template-v1.md`

## Key reusable infrastructure references
- Local simulator path:
  - `src/qrope/qsim.py`
- Main runner:
  - `src/qrope/run.py`
- Synthetic generator:
  - `src/qrope/synthetic.py`
- Focused restart tests:
  - `tests/test_qsim.py`
  - `tests/test_run_real_mode.py`
  - `tests/test_vnew_interference.py`

## Key artifact directories
- Synthetic bounded restart runs:
  - `logs/ablation_runs/v0-synthetic-s42/`
  - `logs/ablation_runs/v0-synthetic-s123/`
  - `logs/ablation_runs/v0-synthetic-s777/`
  - `logs/ablation_runs/vnew-synthetic-s42/`
  - `logs/ablation_runs/vnew-synthetic-s123/`
  - `logs/ablation_runs/vnew-synthetic-s777/`
- Diagnostics:
  - `logs/diagnostics/`

## Restart gate
Do not reopen implementation unless all are true:
1. a materially new comparator hypothesis exists
2. it is written in a restart brief before coding
3. it has an explicit synthetic falsification packet
4. that packet is approved before execution

## Do not reopen casually
- `V4`
- `V4b`
- `V_new_explicit_interference`
- local screening-tail tuning
- remote-expansion-on-faith

## Bottom line
This index is the starting point for any future reuse of the repository.
If the work is not memo-level or restart-brief-level, it should not begin.

