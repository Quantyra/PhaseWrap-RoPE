# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Order Agreement Approval Candidate v1

Date: 2026-03-10
Status: approval-candidate
Story: S547

## Decision
- elevate the line to approval-candidate posture
- keep it memo-only in this step

## Why This Line Exists
- the stopped slot-invariant top-k pair-margin branch failed on mixed `mae` and `rank_correlation` leadership against bounded controls
- this line makes top-k pair-order agreement primary instead of pair-margin regression
- this is materially different from the stopped branch, not a relabel of the same objective

## Why It Is Not Yet Implementation-Approved
- the task still needs a dedicated implementation-approval gate
- the hard-stop diagnostics must be bound directly into that gate before code reopens
