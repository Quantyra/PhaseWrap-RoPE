# Q-RoPE Parity Shadow Comparison Policy v1

## Policy
Use `parity` as the default local screening readout.

Require `weighted` as a shadow comparator only under specific trigger conditions.

## Why this policy is needed
Current evidence supports parity as the strongest local screening path available.
But the evidence also shows a real exception:
- `V3` on `amazon` remains materially stronger under `weighted`

Without a shadow policy:
- parity could over-shape important local decisions

With shadowing on every run:
- local iteration would become slower and noisier than necessary

So the correct protocol is selective shadowing.

## Required weighted shadow triggers
Run weighted shadow comparison when any of the following is true:

1. A major branch decision is being made
   - promote or demote a variant
   - reopen a deferred branch
   - decide whether a mechanism-level branch is justified

2. `amazon` materially affects the conclusion
   - especially when `V3` performance on `amazon` is being used as evidence

3. A result would influence remote-budget decisions
   - any conclusion that could reopen paid remote execution

4. A parity-based result reverses a prior local conclusion
   - if parity changes the branch ranking relative to earlier weighted-based evidence

## Weighted shadow not required when
Weighted shadow is optional for:
- exploratory diagnostics
- intermediate local probing
- infrastructure-only sanity checks
- iterations that do not affect a branch or budget decision

## Reporting rule
When weighted shadow is triggered:
- parity remains the primary local screening readout
- weighted must be reported alongside it
- the final decision must explicitly note whether:
  - parity and weighted agree
  - parity and weighted disagree

If they disagree, the disagreement itself becomes evidence and must be recorded.

## Decision implication
This policy keeps the current local process disciplined:
- parity remains useful as the faster default screening path
- weighted remains available to catch readout-specific distortions on important decisions

## Next local path
Future local packets should default to parity.
Use weighted shadow only when one of the trigger conditions is met.

## Bottom line
Parity is the default.
Weighted is mandatory only for decisions that materially affect branch status, `amazon`-dependent conclusions, or potential remote spend.
