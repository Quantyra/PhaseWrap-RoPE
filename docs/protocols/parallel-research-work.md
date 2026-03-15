# Q-RoPE Parallel Research Work Protocol

## Purpose
Allow useful parallel work without reintroducing branch churn, fairness drift, or ambiguous decision paths.

## Scope
This protocol applies to all Q-RoPE research work, including:
- memo-level planning,
- gate drafting,
- implementation work,
- bounded packet execution,
- review and package refresh work.

It supplements:
- `docs/protocols/research-planning.md`
- `docs/protocols/portfolio-saturation-and-review.md`
- `docs/protocols/vp-of-research-proxy.md`

## Core Rule
Parallelism is allowed only when it does not weaken decision clarity.

The default standard is:
- parallelize support work,
- keep decision-critical execution serial.

## Allowed Parallel Work
The following may run in parallel by default if they do not conflict on the same files or decision thread.

### Memo-Only Candidate Work
- missing-question memos
- candidate design memos
- gate sketches
- theory notes
- portfolio comparison notes

Conditions:
- at most `2` memo-only candidate threads per evidence class at one time
- each thread must answer a materially different missing question
- no thread may bypass the active saturation rules

### Review And Package Work
- review memo refreshes
- executive summary refreshes
- handoff index refreshes
- evidence-log and package synthesis work

Conditions:
- package work must not silently change the meaning of an active branch decision
- if package work changes posture, checkpoint and evidence must be updated immediately

### Intra-Branch Compute
Inside one already-approved bounded branch, the following may run in parallel:
- witness and control runs across fixed seeds
- summary generation
- metrics aggregation
- post-result documentation drafting after results are known

Conditions:
- the branch contract must already be frozen
- all retained runs must use the same fixed packet and stop rule
- parallelism may not add challengers, packets, or perturbations not already approved

## Disallowed Parallel Work By Default
### Multiple Active Execution Branches In The Same Evidence Class
Do not run multiple implementation or execution branches in parallel within the same evidence class.

This means:
- one active transfer execution branch max
- one active bridge execution branch max
- one active realism-bridge execution branch max
- one active successor-class execution branch max

Reason:
- this preserves decision leverage and prevents branch spray.

### Parallel Hardening Packets On The Same Branch
Do not run multiple retained hardening packets at the same time on one branch.

Examples that are blocked:
- `token_permutation=cdab` and `pair_reindex=1` together
- `pair_reindex=1`, `slot_swap=1`, and `pair_reindex=7` together

Reason:
- each packet determines whether the branch should continue.

### Parallel Reopens After Review Closure
Do not reopen multiple post-review candidates in parallel by default.

Reason:
- once a cycle is review-closed, any reopen must remain rare, explicit, and easy to audit.

## Exception Rule
The VP-of-Research proxy may approve a parallel exception only if all are true:
- the work answers clearly different missing questions
- the work has disjoint write scope or clean sequencing
- the work cannot blur which result changes the program decision
- the work does not violate the one-active-execution-branch rule within an evidence class

The exception memo must state:
- what is parallelized,
- why serial execution is lower value,
- why decision clarity is still preserved,
- what stop rule applies if one thread resolves the question early.

## Priority Rule
If a conflict exists between speed and decision clarity, choose decision clarity.

In practice:
- serial execution beats parallel branch churn
- one clean decision beats two muddled partial answers

## Traceability Requirements
When parallel work is approved or rejected, update:
- the relevant memo or exception note,
- `docs/evidence/E001-evidence-log.md`,
- `logs/checkpoint.json` if posture or next actions change.

## Current Default Interpretation
Under the current program state:
- package refresh and review work may run in parallel,
- memo-only candidate design may run in limited parallel form,
- active execution branches remain serial by default,
- retained hardening packets remain strictly sequential.
