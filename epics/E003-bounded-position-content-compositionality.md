# Epic

## Epic ID and title
E003 - Bounded position-content compositionality

## Problem statement
The current Q-RoPE package preserves bounded evidence for positional selection, including fixed-cardinality successor tasks and one variable-cardinality robustness survivor. The next unresolved stretch question is whether the witness signal survives when correctness depends on composing a positional rule with a bounded content or key filter rather than position alone. That is closer to how RoPE-like structure matters in model use, where position interacts with query-key relevance instead of operating in a purely positional vacuum.

## Research questions
- Can the witness survive bounded positional selection when the correct candidate must satisfy both a positional offset rule and a bounded content-key relevance rule?
- Does the current signal survive content aliasing without collapsing into token-identity lookup behavior?
- Can that compositionality be tested without fairness blow-up in the symbolic control?
- If this line fails, does the current package represent the practical ceiling for bounded position-only evidence?

## Goals
- Define one bounded stretch effort beyond position-only selection.
- Test whether Q-RoPE evidence can survive position-content composition under explicit fairness limits.
- Preserve clear stop conditions if the task collapses into lookup shortcuts or uncontrolled symbolic growth.

## Non-goals
- Reopening hardware.
- Unbounded content vocabularies or open-ended candidate sets.
- Transformer benchmark surrogates without bounded fairness.
- Default epic proliferation without decision leverage.

## Scope
- Memo-level missing-question and candidate design for bounded position-content compositional selection.
- Candidate-level gate and bounded implementation plan only if admissibility stays strong.
- One bounded execution cycle at most if the design clears the full gate ladder.

## Success metrics
- One candidate with clear decision leverage and bounded fairness contract.
- Explicit stop conditions at branch and portfolio level.
- Either a preserved bounded compositionality result or a defensible ceiling memo.

## Methods and approach
- Start from the preserved `E002` package.
- Define one bounded candidate-selection task where the correct item must satisfy both offset structure and content relevance.
- Freeze the allowed symbolic basis before any implementation opens.
- Use the standard fixed packet and retained hardening ladder only if the candidate survives memo-level gates.

## Risks and mitigations
- Risk: content gating becomes a disguised token-identity lookup problem.
  Mitigation: cap content classes tightly and forbid raw token-id or slot-id symbolic shortcuts.
- Risk: the task collapses into the current position-only successor family.
  Mitigation: reject the candidate unless both position and content are decision-relevant.
- Risk: compositionality claims become over-read as realistic transformer validation.
  Mitigation: keep the task bounded, local, and explicitly internal-only.

## Deliverables
- Missing-question memo for bounded position-content compositional selection.
- Candidate memo and gate sketch.
- Bounded implementation plan only if the gates pass.
- Preserved result or ceiling memo.

## Evidence log
- `docs/evidence/E001-evidence-log.md`

## User stories
- S1359 - E003 epic opening memo
- S1360 - Position-content compositionality missing question
- S1361 - Position-content compositional candidate sketch
