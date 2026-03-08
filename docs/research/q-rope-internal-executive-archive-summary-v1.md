# Q-RoPE Internal Executive Archive Summary v1

## Status
- Program state: `paused`
- Repository posture: `internal archive`
- Publication status: `gated off`

## Executive assessment
Q-RoPE produced meaningful internal research value, but not a deployable or publishable positive result.

The work succeeded in:
- building a disciplined research protocol stack
- creating reproducible local and remote execution infrastructure
- testing the core idea across baseline, variant, salvage, and bounded-restart phases
- identifying concrete failure modes instead of masking them

The work did not succeed in:
- showing stable performance superiority
- showing stable cross-provider agreement
- validating a restart mechanism that improved relative-offset discrimination over baseline

## What Quantyra should retain
Retain as reusable assets:
- the protocol and evidence framework
- the git-traceable story history
- the local simulator/test harness
- the IBM and Quandela integration paths
- the synthetic theorem-validation workflow
- the restart brief template and approval gate

## What Quantyra should not reopen casually
Do not casually reopen:
- `V4`
- `V4b`
- local screening-tail tuning
- the bounded `V_new_explicit_interference` branch
- remote-expansion-on-faith

Those paths were tested enough to justify stopping them.

## Best internal reading of the science
The repo does not show that quantum relative-phase positional encoding is impossible.

It does show that, in the tested mechanism families:
- phase was present
- but the comparison/observable path did not reliably convert it into stronger relative-offset discrimination

That is the central technical lesson.

## Restart bar
Only reopen if all of the following are true:
1. a materially new comparator hypothesis exists
2. it is written in a restart brief before implementation
3. it has an explicit synthetic falsification packet
4. it clears that packet before any broader work resumes

## Bottom line
This repository is a good internal research archive.
It is not an active program.
Its value is now in preserved evidence, reusable infrastructure, and a higher bar for any future restart.

