# Q-RoPE Mechanism Family Selection v1

## Decision
Select one planning priority:
- `explicit relative-phase interference comparator`

Defer all other mechanism families.

## Why this family is first
It best targets the exact failure mode observed in the paused line:
- phase was present
- but measurement/comparison did not convert it into stronger relative-offset separation

It is also the most faithful next candidate relative to the theorem target:
- make `P(i)^dagger P(j)` matter inside the measured comparison
- not just inside state preparation

## Deferred families
Deferred, not rejected:
- observable-family redesign
- architecture-level query-key redesign

Reason for deferral:
- both have merit
- neither is as tightly aligned to the observed failure mode
- both are easier to let sprawl before falsification is explicit

## What this means for the planning phase
Advance only the following sequence:
- `S099` state-preparation design
- `S100` comparator/interference design
- `S101` observable/readout design
- `S102` synthetic falsification packet
- `S103` implementation-readiness review

Do not open parallel mechanism planning branches.

## Bottom line
The new mechanism phase is now focused.
If Quantyra wants a future restart, it should start by planning the explicit relative-phase interference comparator and nothing else first.
