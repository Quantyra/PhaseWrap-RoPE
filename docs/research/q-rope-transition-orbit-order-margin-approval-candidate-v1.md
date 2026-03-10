# Q-RoPE Transition Orbit Order Margin Approval Candidate v1

Date: 2026-03-11
Stories: S394

## Status
- approval-candidate
- implementation not approved in this step

## Why This Line Is Preserved
- the stopped listwise branch still preserved stronger order signal under deeper hardening
- the smallest credible continuation is to test order-margin response directly
- this avoids retrying the failed top-1 listwise branch while preserving the only remaining rationale from that line

## Remaining Blockers
- exact generator must prove the target cannot collapse to a top-1-only shortcut
- bounded symbolic margin controls must be specified at the same abstraction level as the target
- no code should reopen until those generator diagnostics are part of the approval gate
