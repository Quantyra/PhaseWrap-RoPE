# Q-RoPE Portfolio Saturation And Review Protocol

## Purpose
Prevent endless branch churn by adding explicit portfolio-level stopping rules above individual branch execution rules.

## Scope
This protocol applies to all Q-RoPE evidence classes, including:
- symbolic fairness families
- transfer families
- bridge-task families
- realism-bridge families

It governs when new branches may open, when a portfolio is considered saturated, and when review becomes mandatory.

## Core Rule
New branches may not open by default once an evidence class has become decision-sufficient.

A branch may open only if it answers a missing question that the current portfolio does not already answer.

## Automated Stage-Gate Exception
The core rule blocks opportunistic new branches. It does not block a predeclared automated stage ladder after that ladder has been frozen.

Under an automated stage-gate ladder:
- each stage is treated as one planned continuation, not a new discretionary branch;
- the path advances on deterministic `PASS`;
- the path stops on deterministic `FAIL_STOP` or `BLOCKED`;
- human review is deferred until the terminal package;
- no extra candidates may be inserted between stages.

## Required Missing-Question Justification
Before opening any new branch, write a memo-level justification that states:
- the exact missing question,
- which current positive results do not answer it,
- which current failure boundaries do not answer it,
- what program decision would change if the branch succeeds,
- what program decision would change if the branch fails.

If these answers are weak or merely novelty-based, the branch must not open.

## Decision-Leverage Rule
Novelty alone is not enough.

A new branch must have clear decision leverage on at least one of:
- internal continuation judgment,
- escalation judgment,
- mechanism interpretation,
- boundary-map refinement,
- RoPE-relevance interpretation.

If a branch cannot materially change one of those, it must not open.

## Evidence-Class Caps
Default caps apply unless an explicit exception memo is approved by the VP-of-Research proxy.

### Symbolic Fairness Families
- default cap: `5` serious challenger families per cycle

### Transfer Families
- default cap: `6` materially different families per cycle

### Bridge Families
- default cap: `5` materially different bridge families per cycle

### Realism-Bridge Families
- default cap: `1` active or execution-approved realism-bridge family after bridge-cycle closure

Opening beyond these caps requires an explicit exception memo that states:
- why the current class is not yet saturated,
- why theory/review is lower value than another branch,
- what missing decision the additional branch addresses.

## Survivor-Failure Balance Rule
If an evidence class has both:
- multiple positive survivors, and
- multiple explicit failure boundaries,
then synthesis and review become the default next step.

At that point, new execution is blocked unless a missing-question justification is approved.

## Mandatory Review Trigger
A review checkpoint is mandatory when any of the following happens:
- an evidence class reaches its default cap,
- an evidence class has at least `2` explicit failure boundaries,
- an evidence class has at least `2` preserved positive survivors and at least `2` explicit failure boundaries,
- a new evidence layer has been established and at least `3` materially different branches have been tested within it.

Once a mandatory review trigger is hit, default execution closes until review artifacts are refreshed.

For an active automated stage-gate ladder, the mandatory review trigger is satisfied by the terminal final package, not by pausing between stages.

## One-Active-Branch Rule
Per evidence class, only one new branch may be active at a time.

This means:
- at most one active transfer branch,
- at most one active bridge branch,
- at most one active realism-bridge branch,
- at most one active symbolic fairness expansion line.

No parallel branch spray is allowed within the same evidence class.

## Negative-Boundary Respect Rule
If a proposed candidate is structurally close to an archived failure boundary, it must be rejected by default.

It may reopen only if a memo explicitly states:
- why the earlier failure mode should not recur,
- what structural difference makes the new candidate materially distinct,
- why the current boundary map is insufficient without it.

## Mandatory Why-Not-Theory Check
Before any new branch opens, the candidate memo must answer:
- why another experiment is higher value right now than theory, synthesis, review, or package refresh.

If the answer is not strong, execution must remain closed.

## Closed-Cycle Reopen Rule
Once a cycle has been marked review-ready or review-complete, it may not reopen by inertia.

Reopening requires a memo that states:
- the exact unresolved gap,
- the exact new candidate,
- why the current portfolio is insufficient,
- why reopening is better than theory or review work.

If the user or governing program direction replaces intermediate review with automated deterministic gates, a closed cycle may reopen only through a supersession memo and a frozen automated stage-gate path. The path itself then governs advancement until terminal review.

## Escalation-Ladder Rule
Every evidence class must map to a next escalation criterion.

If no escalation criterion is made more likely by another branch, the branch must not open.

In practice, this means branch count cannot become a goal in itself.

## Traceability Requirements
When this protocol blocks or permits a new branch, update all relevant artifacts:
- the candidate or review memo,
- `docs/evidence/E001-evidence-log.md`,
- `logs/checkpoint.json`,
- any board or research-opinion memo if the program posture changes.

## Current Program Interpretation
As of the 2026-05-16 automated-stage update:
- transfer and bridge evidence remain saturated,
- phase-wrap is the preserved local algorithm component,
- the active continuation is not another open-ended branch;
- the active continuation is one deterministic path through transformer-adjacent validation, circuit parity, noisy simulation, bounded hardware, and terminal review packaging;
- final human review happens after that path terminates.
