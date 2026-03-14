# Q-RoPE Research Planning Protocol

## Purpose
Provide a reusable protocol for planning future Q-RoPE research so new work begins from the right question, the right gate sequence, and the right stop conditions.

## Core Principle
Research planning must start from a missing question, not from a candidate branch.

A valid plan answers:
- what is still unknown,
- why it matters,
- what evidence could change the decision,
- what would count as failure,
- when the line should stop.

## Required Planning Sequence
Every new research cycle must follow this order.

### 1. State The Current Ceiling
Write a short summary of:
- what the current package already establishes,
- what evidence classes are saturated,
- what decisions are already stable,
- what escalation remains unsupported.

### 2. Define The Next Missing Question
State one question only.

It must be specific enough that success and failure would both be informative.

Bad question:
- can we make Q-RoPE better?

Good question:
- does one realism-bridge task exist that materially increases confidence that the witness signal is relevant to positional encoding behavior?

### 3. Define Decision Leverage
Specify what decision this question could change.

Allowed examples:
- continue vs stop,
- preserve vs escalate,
- synthetic-only vs realism-bridge,
- mechanism-only vs transformer-adjacent validation.

If no decision would change, the plan must stop.

### 4. Choose The Evidence Class
Select the smallest evidence class that can answer the question.

Choices may include:
- theory,
- synthesis/review,
- bounded transfer,
- bounded bridge,
- realism-bridge,
- escalation memo.

Default rule:
- prefer theory or synthesis over execution unless execution is clearly higher leverage.

### 5. Write The Gate Ladder
Every plan must include an explicit gate ladder:
- design gate,
- admissibility gate,
- implementation gate,
- bounded execution gate,
- stop or preserve gate,
- escalation review gate if relevant.

### 6. Write The Stop Conditions
Every plan must state both:
- branch-level stop conditions,
- portfolio-level stop conditions.

This includes:
- metric stop rules,
- saturation triggers,
- review triggers,
- reasons the entire evidence class should close.

### 7. Write The Reopen Criteria
If the plan fails, specify what would be required to justify reopening later.

## Mandatory Planning Checks
Before any new execution plan is accepted, answer all of the following.

### Missing-Question Check
- Is there exactly one missing question?
- Is it not already answered by the current portfolio?

### Why-This-Now Check
- Why is this the highest-value next move?
- Why not theory, review, or packaging instead?

### Boundary Check
- Which existing positive results are relevant?
- Which archived failures are relevant?
- Why is this not just a neighbor of an archived failure?

### Escalation Check
- If this succeeds, what becomes more justified?
- If this fails, what becomes less justified?

### Stop Check
- What exact condition ends the line?

## Planning Outputs
A complete planning packet should normally include:
- next-question memo,
- decision-leverage memo,
- evidence-class choice memo,
- gate ladder memo,
- checkpoint update,
- evidence-log entry.

These can be combined when concise, but the content must exist.

## Default Anti-Churn Rule
If planning cannot produce a strong missing-question statement and a strong decision-leverage statement, no new branch may open.

## Current Program Application
As of the current Q-RoPE state:
- ordinary symbolic, transfer, and bridge expansion are saturated,
- the only admissible future execution class is realism-bridge, and only if a candidate can be justified under the realism-bridge gate,
- otherwise the correct next move is review, theory, or stop.
