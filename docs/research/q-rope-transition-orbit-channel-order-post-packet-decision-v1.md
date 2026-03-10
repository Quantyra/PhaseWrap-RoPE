# Q-RoPE Transition Orbit Channel-Order Post-Packet Decision v1

Date: 2026-03-10
Stories: S462

## Decision
- keep the transition-orbit channel-order execution branch active

## Why
- the witness did not lose the primary metric stack
- it tied the strongest retained control on mean accuracy
- it led the full fixed control stack on mean F1
- the packet passed all declared generator hard-stop diagnostics

## Consequence
- do not widen the task or control family yet
- move to one bounded robustness step
- next step: `pair_reindex=1` hardening against the strongest retained symbolic baselines
