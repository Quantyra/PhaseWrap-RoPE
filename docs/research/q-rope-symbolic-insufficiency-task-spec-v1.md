# Q-RoPE Symbolic Insufficiency Task Specification v1

Date: 2026-03-11
Stories: S656

## Task
- `synthetic_symbolic_insufficiency_transition_response`

## Objective
- predict a relational response that depends on structured interaction across two transition channels and one latent path variable
- the response must vary within every coarse observable state used by the allowed symbolic controls

## Allowed Symbolic Control Family
- additive and low-order polynomial functions over:
  - coarse transition state indicators
  - single-channel analog summaries
  - pairwise cross-direction summaries
- no latent path-state identifiers
- no explicit lookup over full relational microstate

## Forbidden Feature Family
- latent path-state ids
- exact microstate keys
- pooled lookup tables over hidden transition tuples
- arbitrary basis expansion beyond the declared low-order control family

## Structural Requirement
- the target must be centered so every coarse symbolic state has near-zero standalone predictive value
- within each coarse symbolic state, the target must still vary as a function of latent path interaction

## Audit Requirements
- declare the exact allowed symbolic basis before implementation
- declare the exact forbidden feature family before implementation
- declare diagnostics proving coarse-state nullness and within-state variation

## Status
- memo-only
- no implementation approved
