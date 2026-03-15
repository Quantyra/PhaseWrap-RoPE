# Q-RoPE E002 Variable-Cardinality Gate v1

Date: 2026-03-14
Stories: S1330-S1331

## BLUF
- The variable-cardinality candidate passes the memo bar only if candidate-set variability is genuinely active and the symbolic control remains bounded under a small frozen cap.
- This gate does not approve implementation yet.
- It passes only to bounded implementation planning if the fairness contract stays clean and non-cardinality-specific.

## Task
- `synthetic_positional_variable_cardinality_offset_selection_response`

## Candidate Intent
- one query anchor
- bounded candidate-count range within a small fixed cap, for example `3` to `5`
- one correct positional choice under a relative-offset rule
- distractor insertion that changes set composition while preserving ambiguity
- correctness must remain stable under candidate-count change, not just token replacement

## Bounded Symbolic Control
- additive and bounded-quadratic regressor over declared query summaries, per-candidate summaries, and bounded aggregate set summaries only

## Frozen Declared Summary Scope
Allowed declared summaries may include only:
- query identity summary
- candidate relative-offset summaries to the query
- candidate token-identity summaries
- bounded candidate-count summary
- bounded aggregate confusability summaries across the active set
- bounded aggregate distractor-insertion summaries across the active set

Not allowed:
- per-cardinality lookup tables
- slot-identity lookup features
- latent ids
- unrestricted higher-order candidate interactions
- transformer surrogates
- cardinality-specific basis expansion

## Required Candidate-Level Admissibility Conditions
The candidate passes only if all are true:
- candidate-count variability is genuinely active in defining task difficulty
- the active candidate-count cap is explicit and small
- exactly one candidate remains correct across bounded set-composition changes
- the task does not collapse into a fixed-cardinality padded variant
- the symbolic control can be written as one frozen bounded family across all allowed candidate counts
- success or failure would still change whether successor-class robustness goes beyond fixed-cardinality selection

## Candidate-Level Stop Rule
Stop the candidate immediately if any are true:
- variability reduces to cosmetic padding only
- correctness depends on slot identity rather than relative-offset selection
- the symbolic control requires cardinality-specific lookup or separate per-count families
- the candidate-count cap must grow to stay nontrivial
- the task no longer provides decision leverage beyond the preserved successor package

## Gate Decision Rule
- Pass to bounded implementation planning only if the candidate specification remains clean under this gate.
- Otherwise stop `E002` and treat the current successor package as the practical ceiling for bounded model-like positional selection.
