# Q-RoPE Sector-Parity Restart Scaffold v1

## Purpose
Preserve the minimum restart scaffold for any future branch that wants to use:
- `synthetic_sector_parity_binary`

## Required elements
Any future restart brief must declare:
- representation family
- comparator or measurement family
- exact sector-resolution rule
- exact anti-collapse diagnostic
- exact three-seed packet:
  - `42`
  - `123`
  - `777`

## Required baselines
- `V0`
- one future candidate only

No multi-branch reopen.

## Required pass condition
A future candidate must show all of:
- better mean accuracy than `V0`
- better mean F1 than `V0`
- positive sector-parity separation across all three seeds
- no pooled-score-only explanation

## Required failure condition
Stop immediately if:
- improvement appears in only one seed
- the task can be explained by pooled score drift
- sector resolution is not preserved before aggregation

## Bottom line
The archive now preserves not just the next task family, but the minimum approval scaffold for any future restart that wants to use it.
