# Q-RoPE Symbolic Insufficiency Implementation Approval Candidate v2

Date: 2026-03-10
Stories: S689

## Decision
- implementation-approval candidate
- still memo-only

## Preconditions For Any Future Implementation Gate
- the task spec, proof sketch, restart scaffold, and approval gate must use the same exact stronger symbolic basis
- the implementation gate must include:
  - `allowed_symbolic_basis_frozen_pass`
  - `forbidden_feature_family_absent_pass`
- no new symbolic features may be introduced during implementation planning or execution
- the current bounded witness result remains the baseline comparison point

## Frozen Allowed Symbolic Basis
- coarse transition indicators
- first-order single-channel analog summaries
- first-order pairwise cross-direction summaries
- one bounded quadratic layer over declared analog summaries only
- one bounded cubic layer over declared analog summaries only
- one bounded gated interaction family where a coarse transition indicator may modulate a declared analog summary

## Frozen Forbidden Feature Family
- latent path-state ids
- exact microstate keys
- hidden tuple lookups
- explicit per-latent bucket parameters
- uncontrolled mixed symbolic-analog basis growth
- arbitrary higher-than-cubic analog expansion

## Review Rule
- if the stronger symbolic family is approved for implementation later, it must be challenged against the preserved symbolic-insufficiency witness result under one fixed bounded packet only
- if the stronger symbolic family catches up, the current branch loses uniqueness under a fairer symbolic bar
- if it does not, the current branch earns a stronger internal claim than it has now

## Status
- memo-only implementation-approval candidate
- no implementation approved
