# Epic

## Epic ID and title
E002 - Bounded positional selection robustness

## Problem statement
The current Q-RoPE package preserves bounded successor-class evidence for fixed-size positional selection, including `key-query-offset-selection` and `dual-anchor-offset-consensus`. The next unresolved stretch question is whether the witness signal survives bounded positional selection when candidate-set size and distractor composition vary without breaking fairness. That is a stronger robustness question than the current fixed-cardinality successor layer and is the right next stretch effort if the line reopens.

## Research questions
- Can the witness survive bounded variable-cardinality positional selection under distractor insertion and candidate-set growth?
- Does successor-class signal remain stable when the choice set changes size rather than only content?
- Can that robustness be tested without allowing fairness blow-up in the symbolic control?
- If this line fails, does the current successor package represent the practical evidence ceiling for bounded model-like positional selection?

## Goals
- Define a bounded successor-class robustness track beyond fixed-cardinality selection.
- Test one materially different missing question with explicit decision leverage.
- Preserve clear stop conditions if fairness or task definition becomes unstable.

## Non-goals
- Reopening hardware.
- Unbounded candidate-set scaling.
- Default successor-class proliferation.
- Transformer benchmark surrogates without bounded fairness.

## Scope
- Memo-level missing-question and candidate design for variable-cardinality positional selection.
- Candidate-level gate and bounded implementation plan only if admissibility stays strong.
- One bounded execution cycle at most if the design clears the full gate ladder.

## Success metrics
- One candidate with clear decision leverage and bounded fairness contract.
- Explicit stop conditions at branch and portfolio level.
- Either a preserved bounded robustness result or a defensible ceiling decision.

## Methods and approach
- Start from the preserved successor package.
- Define one variable-cardinality positional selection task with fixed candidate-count cap and distractor insertion rule.
- Freeze the allowed symbolic basis before any implementation opens.
- Use the standard fixed packet and retained hardening ladder only if the candidate survives memo-level gates.

## Risks and mitigations
- Risk: candidate-set variability becomes a hidden lookup problem.
  Mitigation: freeze bounded candidate-count cap and aggregate symbolic summaries only.
- Risk: the task collapses into the existing fixed-cardinality successor family.
  Mitigation: reject the candidate unless variable-cardinality effects are genuinely decision-relevant.
- Risk: successor-class churn resumes by relabeling nearby branches.
  Mitigation: enforce explicit missing-question leverage and epic-level stop rules.

## Deliverables
- Missing-question memo for variable-cardinality positional selection.
- Candidate memo and gate sketch.
- Bounded implementation plan only if the gates pass.
- Preserved result or ceiling memo.

## Evidence log
- `docs/evidence/E001-evidence-log.md`

## User stories
- S1327 - E002 epic opening memo
- S1328 - Variable-cardinality positional selection missing question
- S1329 - Variable-cardinality successor candidate sketch
