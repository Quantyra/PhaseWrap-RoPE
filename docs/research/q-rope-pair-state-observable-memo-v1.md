# Q-RoPE Pair-State Observable Memo v1

## Status
- `memo-only`
- `archive-safe`
- `not approved for implementation`

## Candidate observable family
Use a `sector-contrast relational observable`.

Core idea:
- define offset sectors inside the pair-state representation
- measure contrast between sector responses rather than a single global score

## Why this is the leading observable
The stopped branches repeatedly collapsed into:
- uniform score shifts
- weak parity/readout compression
- downstream attempts to infer relation from the wrong primitive

The pair-state family changes the primitive object.
The observable should change in the same way.

So the future measurement target should not be:
- one scalar parity over the whole state
- one overlap magnitude
- one weighted excitation summary

It should be:
- contrast across explicitly defined relative-offset sectors

## One concrete memo-level form
Assume the pair-state representation contains:
- a positive-offset sector
- a negative-offset sector
- optional magnitude-conditioned sub-sectors

Then define an observable family like:
- `O_rel = Response_pos - Response_neg`

Possible refinements:
- `O_rel_mag = (Response_pos_small - Response_neg_small) + (Response_pos_large - Response_neg_large)`

The key point is structural:
- measure relational contrast directly at the sector level
- do not reduce the entire state to one global scalar first

## Why this differs from prior failed readouts
This is not:
- parity over the old branch-local state
- parity contrast over constructive/destructive channels of the same branch-local encoding
- weighted excitation
- top-heavy state mass

Those all acted after a representation that left relation implicit.

This observable assumes relation is explicit and reads that relation directly.

## What a future restart would need to specify
Before any restart brief, this observable family would still need:
1. exact sector definition
2. exact measurement operator or measurement rule
3. exact aggregation rule across sectors
4. exact synthetic success criterion tied to sector contrast

## Why this angle is worth preserving
If pair-state relative-offset encoding is the representation candidate, then sector-contrast relational measurement is the natural measurement candidate.

Together they form a coherent new angle:
- represent relation explicitly
- measure relation explicitly

That is materially cleaner than asking one downstream scalar to recover everything.

## Bottom line
The leading observable direction for the pair-state family is:
- `sector-contrast relational measurement`

That is the most defensible next memo-level refinement because it stays aligned to the representation shift rather than drifting back to the old readout logic.

