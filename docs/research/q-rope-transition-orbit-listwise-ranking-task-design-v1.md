# Q-RoPE Transition Orbit Listwise Ranking Task Design v1

Date: 2026-03-11
Story: S373

## Preserved Direction
The next angle is not another pairwise binary classifier on the same latent order signal.

The preserved angle is:
- a listwise transition-orbit ranking task where the model must recover the within-state ordering over a small set of candidates, not just answer one binary comparison at a time.

## Reason
The pairwise-order witness branch failed on both primary classification metrics.
A listwise task is still materially different because it removes the specific classifier decision boundary that may be favoring bounded symbolic baselines.

## Constraint
Any future listwise task must still predeclare bounded symbolic ranking baselines and must not reopen implementation until those are fixed in a restart scaffold.
