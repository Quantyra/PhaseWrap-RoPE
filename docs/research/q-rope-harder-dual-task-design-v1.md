# Q-RoPE Harder Dual-Task Design v1

## Decision
- preserve one harder dual-task direction only:
  - `synthetic_dual_sector_content_agreement_binary`

## Why the current task is exhausted
`synthetic_dual_sector_agreement_binary` can be solved by a bounded symbolic baseline with:
- explicit sector-pair interaction terms
- logistic-regression-equivalent head

That means the next task must require more than:
- sector identity alone
- sector-pair identity alone

## Harder task design principle
The next task should require agreement across two distinct relational families:
1. sector-sign agreement
2. content-family agreement

The label should depend on their interaction, not on either family alone.

## Proposed task shape
Each sample still contains:
- observation `A`
- observation `B`

Each observation still has:
- token pair
- signed offset

But the task derives two separate relational summaries:
- `sign_agreement`
  - whether `sector_a` and `sector_b` belong to the same sign family
- `content_agreement`
  - whether the two observations belong to the same token-content family

Then define the label from the interaction:
- `label = 1` iff `sign_agreement == content_agreement`

This is an equality/XNOR-style coupling rule.

## Why this is harder
A bounded symbolic sector-pair interaction control can represent:
- `sign_agreement`

but not:
- `content_agreement`

unless content-family variables are also exposed.

A content-only control can represent:
- `content_agreement`

but not:
- the coupled rule over both families

So the next task can only be fair if later controls are forced to declare explicitly:
- whether they use sector features
- whether they use content-family features
- whether they use cross-family interaction terms

## Why this is the right next angle
It keeps the branch focused on what the current witness path actually carries:
- relational sector structure
- content-sensitive structure

It also raises the bar cleanly:
- the next task must test whether those two families interact in a useful way

## What this is not
- not a new benchmark family
- not a remote path
- not an implementation approval
- not multiple task proposals

## Bottom line
The strongest next memo-only angle is a dual task whose label depends on agreement between:
- sector-sign relation
- content-family relation

That is the smallest clear step beyond the exhausted sector-pair uniqueness task.
