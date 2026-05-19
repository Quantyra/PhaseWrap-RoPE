# Q-RoPE Realism-Bridge Gate Protocol v1

## Purpose
Govern the only currently admissible class of future execution beyond the saturated transfer and bridge portfolio: one realism-bridge candidate.

## Admissibility Requirements
A realism-bridge candidate must:
- be materially closer to actual positional encoding behavior than the current bridge set,
- answer the explicit missing question in `q-rope-next-question-ladder-v1.md`,
- be materially different from `anchor-order`, `anchor-distance`, `anchor-span-membership`, `anchor-offset-signature`, and `anchor-betweenness`,
- still support a bounded symbolic control and explicit fairness contract,
- remain local-only and non-hardware.

## Candidate Preservation Versus Execution Opening
Preserving a realism-bridge candidate is not the same as opening execution.

Allowed at candidate-preservation level:
- name the missing positional question,
- explain why it is materially closer to real positional encoding behavior,
- define the candidate family at memo level,
- state what escalation decision success or failure could affect.

Not allowed without a separate implementation gate:
- dataset generation,
- challenger implementation,
- benchmark execution,
- nuisance or hardening packet selection,
- hardware work,
- publication or superiority claims.

## Required Memo Before Any New Candidate Opens
The memo must state:
- why this is realism-bridge rather than another bridge variant,
- what exact escalation decision it can change,
- why theory/review is lower value than this candidate,
- why the current portfolio is insufficient without it.

## Required Implementation Gate Before Execution
Before any realism-bridge execution opens, a separate gate must freeze:
- the exact task label construction,
- the fixed local basis or rotary frame,
- allowed and prohibited symbolic-control features,
- leakage checks against raw order, distance, signed offset, span, betweenness, and simple lookup shortcuts,
- nuisance transformations,
- retained stop rule,
- claim boundary for witness win, control win, mixed result, and inert perturbation.

For any phase- or rotation-shaped candidate, the gate must additionally state why the label does not collapse to a trivial raw-offset, modulo-bucket, single-band phase, or lookup baseline. If a phase-aware symbolic baseline is allowed to see the full label-generating sufficient statistic, then a witness win may be interpreted only against that declared baseline and a control win must stop the branch.

## Default Policy
- zero realism-bridge candidates are open by default.
- at most one realism-bridge candidate may be active at a time.
- failure to define a clean realism-bridge candidate is itself evidence that the current line may have reached its useful evidence ceiling.

## Automated Stage-Gate Override
If a realism-bridge result has already been preserved and an automated stage-gate path is frozen, the next stage may open without intermediate human approval.

This override does not permit arbitrary new realism-bridge candidates. It permits only the next stage named in the frozen automated path.

Required conditions:
- the prior stage has a `PASS` artifact,
- the next stage has deterministic pass/fail/block gates,
- the symbolic-control and leakage boundaries are frozen before execution,
- all execution artifacts are reproducible from repo-local commands or captured provider job records,
- any failed or blocked gate produces a terminal packet rather than a new branch.

Current application:
- `phase-wrap consistency` has passed the local algorithm stage;
- the next automated stage is one bounded transformer-adjacent validation task;
- no human approval is required before that stage if its deterministic specification gate passes.
