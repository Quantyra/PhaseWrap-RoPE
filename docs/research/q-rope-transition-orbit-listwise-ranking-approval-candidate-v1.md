# Q-RoPE Transition Orbit Listwise Ranking Approval-Candidate v1

Date: 2026-03-11
Story: S376

## Status
Approval-candidate only.

## Why This Line Merits Advancement
- The pairwise-order branch failed cleanly on classification metrics.
- The next smallest materially different angle is listwise ranking, not another binary classifier or regression retry.
- This line still targets the preserved ordinal signal without reusing the stopped task frame.

## Why It Is Not Approved Yet
- the listwise generator is not yet formalized
- the bounded symbolic ranking controls are not yet bound to concrete feature contracts
- the exact listwise metric implementation is not yet fixed in code

## Next Legitimate Move
Write the implementation-approval gate for the listwise ranking line only after the bounded symbolic ranking controls and the within-state list diagnostics are fixed in the restart contract.
