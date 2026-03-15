# Q-RoPE Technical Briefing And BLUF Protocol

## Purpose
Standardize how technical information is explained in this repo so executive readers get the decision quickly without losing access to the supporting technical detail.

## Core Rule
Use `Bottom Line Up Front` by default for:
- VP-of-Research judgments,
- board-style recommendations,
- internal review memos,
- handoff notes,
- explanations of technical findings when the audience may include executives or mixed technical/non-technical readers.

BLUF means:
- state the conclusion first,
- state the decision or recommendation next,
- state the reason in the fewest lines needed,
- move supporting detail after that.

## Default Briefing Order
When writing a briefing-style response or memo, use this order unless a stronger repo protocol overrides it.

### 1. BLUF
Answer these immediately:
- what happened,
- what it means,
- what should be done next.

Target:
- 1 short paragraph or 3 to 5 bullets.

### 2. Decision
State one explicit judgment:
- continue,
- stop,
- preserve,
- reopen,
- escalate,
- do not escalate.

Avoid vague outcomes such as:
- interesting,
- promising,
- mixed,
- needs more work.

If the evidence is mixed, still force a decision and explain the boundary.

### 3. Why
State the 2 to 4 facts that drove the judgment.

These should be:
- auditable,
- tied to declared metrics, gates, or protocol boundaries,
- free of unnecessary implementation detail.

### 4. Risks Or Limits
State what the result does not justify.

Typical examples:
- does not justify hardware reopening,
- does not justify publication,
- does not support broad superiority claims,
- remains simulator-local.

### 5. Next Step
State the single best next step.

If execution is closed, say so directly.
Do not offer multiple equal options unless the protocol actually allows multiple valid choices.

## Audience Layers
Default to three layers when explaining technical information.

### Layer 1. Executive Layer
Use plain language.
Focus on:
- decision,
- impact,
- risk,
- next step.

### Layer 2. Technical Layer
Explain:
- mechanism,
- metric behavior,
- gate outcome,
- why the decision follows.

### Layer 3. Artifact Layer
Point to:
- memo,
- package,
- code path,
- summary CSV,
- checkpoint state.

Do not collapse all three layers together.
Lead with Layer 1, then move downward only as needed.

## Technical Explanation Rule
When the user asks a technical question, answer in this order:

### 1. Short answer
One to three sentences.

### 2. What matters
Explain the mechanism or distinction that actually drives the result.

### 3. Why it matters for the program
Tie the explanation back to:
- the current gate,
- the current portfolio,
- the current decision layer.

### 4. References
Point to the smallest set of relevant files or memos.

## Executive Memo Format
For board recommendations, review memos, or VP-of-Research judgments, use:
- `BLUF`
- `Decision`
- `Why`
- `Limits`
- `Next Step`

Keep the memo body compact.
Push detailed packet-by-packet evidence into linked artifacts.

## Anti-Patterns
Do not:
- bury the decision under background,
- present long chronological narration before the conclusion,
- list many possibilities when one recommendation is clearly best,
- explain every implementation detail before stating impact,
- confuse evidence count with decision leverage,
- treat “more research is needed” as a substitute for a judgment.

## Required Discipline For This Repo
When the repo is in a review-ready or saturation posture:
- explanations must emphasize decision relevance over branch history,
- new information must be framed in terms of whether it changes the decision layer,
- default next steps must be review or preservation unless a protocol explicitly reopens execution.

## Source Basis
This protocol is aligned with the briefing patterns emphasized in:
- University of Calgary guidance on briefing notes and front-loaded recommendations,
- University of Washington guidance on BLUF business writing,
- George Mason University guidance on executive summaries and recommendation-led structure.
