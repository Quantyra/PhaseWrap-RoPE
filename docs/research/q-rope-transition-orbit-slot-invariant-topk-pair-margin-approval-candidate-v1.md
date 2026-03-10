# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Margin Approval Candidate v1

Date: 2026-03-10
Status: approval-candidate
Story: S538

## Decision
- elevate the line to approval-candidate posture
- keep it memo-only in this step

## Why This Line Exists
- the stopped slot-invariant top-k preference branch failed on both declared primary metrics against bounded controls
- this line makes top-k pair-margin magnitude primary instead of binary preference classification
- this is materially different from the stopped branch, not a relabel of the same objective

## Why It Is Not Yet Implementation-Approved
- the task still needs a dedicated implementation-approval gate
- the hard-stop diagnostics must be bound directly into that gate before code reopens
