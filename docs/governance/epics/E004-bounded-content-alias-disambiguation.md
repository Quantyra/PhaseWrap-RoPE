# Epic

## Epic ID and title
E004 - Bounded content-alias disambiguation

## Problem statement
The current Q-RoPE package now preserves bounded evidence for position-only selection, variable-cardinality robustness, and one bounded position-content compositionality survivor. The next unresolved stretch question is whether the witness signal survives when bounded content classes are no longer uniquely identifying and multiple candidates share the same content class. That is a more realistic stressor because practical selection problems often require positional disambiguation under content aliasing rather than clean one-to-one content gating.

## Research questions
- Can the witness survive bounded candidate selection when multiple candidates share the same bounded content class and only the correct position-content composition identifies the target?
- Does the current signal survive content alias pressure without collapsing into slot heuristics or lookup shortcuts?
- Can alias disambiguation be tested with one frozen bounded symbolic family rather than class-specific symbolic branching?
- If this line fails, does the current package represent the practical ceiling for bounded position-content evidence under alias stress?

## Goals
- Define one bounded stretch effort beyond clean position-content gating.
- Test whether Q-RoPE evidence can survive bounded content alias disambiguation under explicit fairness limits.
- Preserve clear stop conditions if the task collapses into token lookup, slot lookup, or symbolic family blow-up.

## Non-goals
- Reopening hardware.
- Unbounded vocabularies or open-ended candidate sets.
- Transformer benchmark surrogates without bounded fairness.
- Default epic proliferation without decision leverage.

## Scope
- Memo-level missing-question and candidate design for bounded content-alias disambiguation.
- Candidate-level gate and bounded implementation plan only if admissibility stays strong.
- One bounded execution cycle at most if the design clears the full gate ladder.

## Success metrics
- One candidate with clear decision leverage and bounded fairness contract.
- Explicit stop conditions at branch and portfolio level.
- Either a preserved bounded alias-disambiguation result or a defensible ceiling memo.

## Methods and approach
- Start from the preserved `E003` package.
- Define one bounded candidate-selection task where at least two candidates share the target content class.
- Require the correct answer to depend on positional disambiguation under alias pressure, not just content match.
- Freeze the allowed symbolic basis before any implementation opens.
- Use the standard fixed packet and retained hardening ladder only if the candidate survives memo-level gates.

## Risks and mitigations
- Risk: aliasing quietly reintroduces slot-identity shortcuts.
  Mitigation: forbid slot-id features and require alias-target rotation across active slots.
- Risk: the task is just a renamed E003 position-content gate.
  Mitigation: require explicit same-class distractors and reject candidates without real alias pressure.
- Risk: symbolic fairness blows up by candidate-count or alias pattern.
  Mitigation: require one frozen symbolic family across all allowed alias patterns.

## Deliverables
- Missing-question memo for bounded content-alias disambiguation.
- Candidate memo and gate sketch.
- Bounded implementation plan only if the gates pass.
- Preserved result or ceiling memo.

## Evidence log
- `docs/evidence/E001-evidence-log.md`

## User stories
- S1391 - E004 epic opening memo
- S1392 - Content-alias disambiguation missing question
- S1393 - Content-alias successor candidate sketch
