# Q-RoPE Transition Orbit Listwise Ranking Decision Memo v1

Date: 2026-03-11
Stories: S381

## Decision
- keep the branch active
- do not broaden the task or control family yet

## Why
- the witness tied the strongest controls on the first primary metric, top-1 accuracy
- the witness led the control stack on the second primary metric, order-F1
- that is enough to preserve the branch, but not enough to claim a decisive advantage

## Bound Next Step
- next bounded step: token-renaming hardening on the same listwise task
- keep the witness fixed
- keep the strongest current symbolic baselines fixed
- keep the scope local-only and zero-credit
