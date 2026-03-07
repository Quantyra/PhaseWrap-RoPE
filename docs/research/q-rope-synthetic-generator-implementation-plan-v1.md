# Q-RoPE Synthetic Generator Implementation Plan v1

## Decision
Implement the salvage restart with the smallest possible code boundary:
- one deterministic synthetic generator module
- one synthetic dataset mode in the runner
- one restart-packet execution path
- one diagnostics artifact bundle

Do not generalize beyond the signed relative-offset binary family in the first implementation.

## Implementation boundary

### New module
Add:
- `src/qrope/synthetic.py`

Responsibilities:
- generate deterministic signed relative-offset samples
- split into train / validation / test
- emit leakage-check summaries

Non-responsibilities:
- no generic benchmark framework
- no remote execution hooks
- no new model variants

### Runner changes
Update:
- [run.py](C:/Users/Dan/Desktop/Projects/QuantyraQRope/src/qrope/run.py)

Minimal runner additions:
- allow dataset mode `synthetic_offset_binary`
- load generated structured samples instead of text-only fallback rows
- preserve current `V0` / `V3` backend path
- write one extra diagnostics JSON artifact for the synthetic packet

### Simulator changes
No new simulator family is justified yet.

Allowed simulator change:
- a minimal helper only if needed to score structured pair text consistently through the existing local backend

Not allowed:
- reopening pairwise-overlap redesign
- reopening new mixing-preset branches
- reopening `V4`/`V5`

## Structured sample format
The generator should emit rows with:
- `text`
- `label`
- `left_token`
- `right_token`
- `left_pos`
- `right_pos`
- `offset`
- `offset_abs`

The runner can still score `text` through the current local path.
The extra fields exist for diagnostics and leakage checks.

## Deterministic text rendering
Render each sample into a canonical token string:
- example form:
  - `lt:A rt:C lp:2 rp:5 off:+3`

Reason:
- preserve current text-based local scoring path
- avoid unnecessary simulator refactors in the first restart packet

## Generator packet
Per seed:
- train: balanced signed-offset rows
- validation: balanced signed-offset rows
- test: balanced signed-offset rows

The generator should expose one function returning:
- split rows
- balance diagnostics
- generation metadata

## Diagnostics artifact
Write one JSON artifact per run containing:
- class counts
- offset counts
- token-pair counts
- absolute-position marginals
- seed
- split sizes

This should live beside `metrics.json` in the run directory.

## First restart packet
Variants:
- `V0`
- `V3`

Seeds:
- `42`
- `123`
- `777`

Backend:
- `sim_quantum_statevector`

Readout:
- `parity` default

Shadow policy:
- `weighted` only if the result becomes branch-changing

## Minimal implementation order
1. add deterministic generator module
2. thread `synthetic_offset_binary` through dataset loading
3. emit generator diagnostics artifact
4. add focused tests for:
   - deterministic generation
   - label rule
   - balance checks
   - runner integration

## Success condition for implementation
The implementation is complete when:
- one seed can be run end to end on `V0` and `V3`
- diagnostics show the generator obeys the balancing and leakage rules
- the restart packet can be expanded to seeds `42/123/777` without new code paths

## Explicit restraint
Do not:
- add bucket prediction yet
- add retrieval yet
- add remote support
- add new readouts or variants
- re-open the stopped local redesign branches

## Next step
Implement the deterministic synthetic generator and first runner integration only.
