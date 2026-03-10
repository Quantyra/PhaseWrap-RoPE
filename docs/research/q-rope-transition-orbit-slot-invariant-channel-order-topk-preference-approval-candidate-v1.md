# Q-RoPE Transition Orbit Slot-Invariant Channel-Order Top-K Preference Approval Candidate v1

Date: 2026-03-10
Status: approval-candidate
Story: S529

## Decision
- elevate the line to approval-candidate posture
- keep it memo-only in this step

## Why This Line Exists
- the stopped slot-invariant top-k rank-only branch preserved stronger order structure than bounded controls but failed the declared top-level accuracy gate
- this line makes top-k pairwise preference primary instead of full top-k rank structure
- this is materially different from the stopped branch, not a relabel of the same objective

## Why It Is Not Yet Implementation-Approved
- the task still needs a dedicated implementation-approval gate
- the hard-stop diagnostics must be bound directly into that gate before code reopens
