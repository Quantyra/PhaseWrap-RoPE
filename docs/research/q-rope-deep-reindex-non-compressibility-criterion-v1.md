# Q-RoPE Deep-Reindex Non-Compressibility Criterion v1

Date: 2026-03-12
Stories: S989

## BLUF
A future transfer family should be treated as viable only if its useful latent-conditioned relational state is expected to remain non-compressible under deeper reindexing. If deeper reindexing can plausibly reduce the task to a compact symbolic recovery path over declared summaries, the family should fail before implementation.

## Purpose
Refine the current survivor-vs-braid screen into an explicit theoretical criterion that can be applied during memo review.

## Core Criterion
A candidate satisfies `deep_reindex_non_compressibility` only if all of the following are true.

### 1. Reindex stability does not collapse the latent state
Under the candidate's expected perturbation family, deeper reindexing should not reduce the effective latent state to a small equivalence class recoverable from declared summaries.

### 2. The target depends on retained intermediate state
The supervised target should require information that persists through relay, accumulation, closure, recombination, or comparable multi-step state retention.

### 3. Compact symbolic recovery remains implausible
There must be a concrete memo-level reason why bounded additive, quadratic, atlas, or transfer-summary families still cannot reconstruct the useful state after reindexing.

## Failure Modes
A candidate fails this criterion if any of the following look plausible at memo level.

### A. Tuple collapse
The target can be rewritten as a compact tuple summary over declared local states.

### B. Reindex compression
Deeper `pair_reindex` can permute the latent structure into a smaller symbolic summary without losing task-relevant information.

### C. Shallow order substitution
The target can be approximated by shallow ordering, ranking, or margin summaries rather than retained latent state.

### D. Atlas recoverability
A small frozen charting or atlas over declared analog summaries appears sufficient to recover the useful structure.

## Internal Reading Of Existing Portfolio
### Pass cluster
- `path`
- `loop-closure`
- `fork-join`
- `relay-binding`

### Fail boundary
- `braid`

Working interpretation:
- the survivor cluster still needed retained latent-conditioned state after bounded hardening
- `braid` did not; deeper reindexing appears to have exposed a compact symbolic recovery path

## Operational Consequence
No future transfer family should reach implementation-approval gate drafting unless the memo explicitly argues why it passes this criterion.
