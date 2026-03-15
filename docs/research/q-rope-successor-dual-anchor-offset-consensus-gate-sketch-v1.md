# Q-RoPE Successor Dual-Anchor Offset Consensus Gate Sketch v1

Date: 2026-03-14
Stories: S1295-S1297

## BLUF
- This candidate should stop immediately unless it stays bounded and genuinely dual-anchor.
- It must not degrade into a renamed single-query task.
- It must not require uncontrolled cross-candidate lookup growth.

## Required Candidate Conditions
- at least two anchors are genuinely active in defining correctness
- the correct candidate must satisfy both anchor-relative rules, not just one
- at least three candidates are genuinely active in the selection problem
- the symbolic control must remain bounded to declared anchor summaries, per-candidate summaries, and bounded aggregate consensus summaries
- no latent ids, lookup tables, learned attention modules, or unbounded higher-order candidate interactions

## Candidate-Level Stop Rule
Stop this candidate immediately if any of the following are true:
- correctness collapses to one anchor only
- the control family requires uncontrolled cross-anchor x candidate lookup structure
- the task requires larger candidate sets or longer sequences just to remain nontrivial
- success or failure would not change a real program decision
