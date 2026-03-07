# Q-RoPE Synthetic Task Family Specification v1

## Decision
Use one primary synthetic family for the salvage restart:
- `signed relative-offset classification`

Keep one secondary family on the roadmap only:
- `relative-offset bucket prediction`

Do not implement retrieval yet.

## Why this family comes first
The first restart packet must answer one question cleanly:
- does `V3` express relative-offset structure more strongly than `V0` under controlled conditions?

Binary signed-offset classification is the smallest task that:
- depends directly on `(j - i)`
- supports deterministic balancing
- is easy to diagnose for leakage
- does not require a large candidate-set protocol

## Dataset definition
Each sample is a tuple:
- `left_token`
- `right_token`
- `left_pos`
- `right_pos`
- `offset = right_pos - left_pos`
- `label`

Sequence length domain:
- `L = 12`

Position domain:
- `left_pos, right_pos in {0, ..., 11}`
- require `left_pos != right_pos`

Token vocabulary:
- `V = {A, B, C, D}`

Token-pair domain:
- ordered token pairs `(u, v)` with `u, v in V`

## Label rule
Use a signed relative-offset binary target:
- positive if `offset in {+1, +2, +3, +4}`
- negative if `offset in {-1, -2, -3, -4}`

Exclude:
- `offset = 0`
- offsets with `|offset| > 4`

This creates a task where:
- absolute positions should not determine the label
- token identity should not determine the label
- only relative displacement sign matters

## Balancing constraints
For every split:
- equal positive and negative counts
- matched absolute-position marginals across classes
- matched token-pair marginals across classes
- matched absolute-offset magnitudes across classes

Concrete balancing rule:
- for each magnitude `d in {1,2,3,4}`
- for each ordered token pair `(u, v)`
- include the same count for:
  - `(offset = +d, tokens = (u, v))`
  - `(offset = -d, tokens = (u, v))`

## Split protocol
Use deterministic seeded generation with three independent dataset seeds:
- `42`
- `123`
- `777`

Per seed:
- train
- validation
- test

Required split property:
- no duplicate full sample tuples across splits

Preferred split size target for the first packet:
- train: `256`
- validation: `128`
- test: `128`

If exact counts are inconvenient under the balancing rules, preserve balance first and size second.

## Leakage checks
The generator must emit diagnostics proving the task is not being solved by shortcuts.

Required checks:
1. `token-pair balance`
   - class counts by ordered token pair must match exactly or within one sample if size rounding is unavoidable
2. `absolute-position balance`
   - class counts by `(left_pos, right_pos)` marginals must be symmetric enough that sign cannot be inferred from one absolute index alone
3. `magnitude balance`
   - counts for `|offset| = d` must match across classes
4. `permutation invariance probe`
   - relabel token vocabulary and verify labels remain unchanged
5. `absolute-position baseline sanity`
   - a trivial absolute-position heuristic should be documented as non-sufficient by construction

## First restart evaluation packet
Backend:
- `sim_quantum_statevector`

Variants:
- `V0`
- `V3`

Scoring paths:
- current local proxy path
- one synthetic diagnostic path if the implementation stays minimal

Datasets:
- one generated dataset per seed under this specification

Readout policy:
- default local readout remains `parity`
- `weighted` is used only if the result becomes branch-changing under current shadow policy

## Primary metrics
- test accuracy
- test F1
- mean score by offset
- score monotonicity by signed offset bucket

## Required restart diagnostics
For each seed and variant:
- score vs signed offset curve
- within-class variance by offset
- token-pair sensitivity summary
- class-separation summary

The key mechanism question is:
- does `V3` produce a cleaner signed-offset response than `V0`?

## Promotion gate to implementation
This synthetic family is ready for implementation because:
- the label rule is simple
- balancing is explicit
- leakage checks are concrete
- the task aligns directly to the theorem target

## Deferred family
`relative-offset bucket prediction` remains deferred until the binary family is implemented and inspected.

Reason:
- if the binary signed-offset task fails, there is no value in opening a broader bucket task immediately

## Next step
Implement the deterministic generator and restart packet runner for this single synthetic family only.
