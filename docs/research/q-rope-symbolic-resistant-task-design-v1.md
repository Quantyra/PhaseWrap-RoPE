# Q-RoPE Symbolic-Resistant Task Design v1

## Scope
- Story: `S172`
- Branch: relational witness
- Status: memo-only

## Proposed next task family
- `synthetic_dual_sector_agreement_binary`

## Core idea
Each sample contains **two** relational pair observations instead of one.

For each observation, compute a sector as before:
- `P_small`
- `P_large`
- `N_small`
- `N_large`

Call them:
- `sector_a`
- `sector_b`

The label is not the identity of either sector alone.
It is an agreement-style relational predicate over the pair:
- `1` if the two sectors belong to the same sign family
- `0` otherwise

Equivalent view:
- positive if both are from `{P_small, P_large}` or both are from `{N_small, N_large}`
- negative otherwise

## Why this is symbolic-resistant
A direct one-hot baseline over a **single** sector clearly cannot solve it.

More importantly, even a bounded symbolic control over:
- one-hot `sector_a`
- one-hot `sector_b`

with a logistic-regression-equivalent head still should not solve it linearly without explicit interaction terms.

Why:
- the label is an agreement/XOR-style relation across two categorical variables
- additive linear weights over separate one-hot blocks cannot represent that interaction exactly
- solving it would require either:
  - cross features
  - a hidden layer
  - or a representation that already mixes the two relational observations

Those are exactly the things the bounded symbolic control should not be allowed to use.

## Why this is still alignment-safe
The task still forbids the old shortcuts:
- no token identity dependence in the label rule
- no direct numeric offset sign label
- no direct numeric offset magnitude label
- no handcrafted scalar giving the answer directly

The label depends only on:
- relational agreement across two sector assignments

## Why this is the right next candidate
It is the minimal escalation beyond `synthetic_sector_parity_binary`.

It preserves:
- discrete relational structure
- auditability
- bounded synthetic control

But it removes the old shortcut where:
- explicit sector identity for one relation was already enough

## Required bounded control on this task
If this task is approved later, the first symbolic control should be:
- separate one-hot for `sector_a`
- separate one-hot for `sector_b`
- same logistic-regression-equivalent head
- no cross terms

That control is intentionally strong but still bounded.

## Pass criterion for task suitability
The task is suitable only if the memo-level task definition preserves all of these:
- alignment-safe labeling
- no single-sector linear shortcut
- no forbidden direct scalar shortcut
- clean synthetic balancing across sector-pair combinations

## What remains out of scope
- implementation
- running the new task
- designing multiple alternative task families in parallel

## Bottom line
The strongest next task candidate is a dual-relation agreement task.
It is harder than the current task for the exact right reason:
- the answer depends on interaction between relational sectors, not on a single explicit sector identity.
