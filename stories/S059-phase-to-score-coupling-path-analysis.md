# Story template

## Story ID and title
S059 - Phase-to-score coupling path analysis

## User value
As a research lead, I want the local phase-to-score coupling path analyzed, so we can determine where dynamic range is being lost before defining any future mechanism-level variant.

## Acceptance criteria
- A zero-credit analysis plan is defined for the local screening circuit
- The coupling-path checkpoints to inspect are specified
- A decision framework is recorded for when a new mechanism-level variant becomes justified

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-v3-v4-token-to-score-sensitivity-v1.md`
- `docs/research/q-rope-v3-v4-score-geometry-diagnostics-v1.md`

## Out of scope
- Paid remote execution
- Immediate new variant implementation

## Dependencies
- S058

## Risks
- Coupling-path analysis may show that the current screening observable is fundamentally too compressive, forcing a later redesign of the local scoring path.

## Unit tests (development stories only)
- No new unit tests required unless code changes are introduced.

## Cycle time
- Start: 2026-03-06 14:22 (Pacific/Honolulu)

## Completion
- Completed: 2026-03-06 14:28 (Pacific/Honolulu)
- Decision: the main dynamic-range bottleneck is downstream of phase injection, specifically across the `RX` mixing plus weighted-excitation readout path; further calibration work and remote `V4` spend remain unjustified.
