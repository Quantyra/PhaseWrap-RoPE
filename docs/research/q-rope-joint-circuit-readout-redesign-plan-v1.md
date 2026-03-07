# Q-RoPE Joint Circuit-Readout Redesign Plan v1

## Decision
Use a single narrow redesign family:

`interference-tail parity screening`

Meaning:
- keep the current `V3` primary path
- keep the existing feature loading and `RZ` phase schedule
- replace the current fixed post-`RZ` tail with a slightly richer interference-sensitive tail
- keep `parity` as the default readout
- keep `weighted` as the policy-driven shadow comparator

## Why this family
The evidence points to a downstream bottleneck:
- phase information does not reach the score strongly enough after `RZ`
- weighted readout is compressive
- simple fixed mixing tweaks were not robust enough

So the next branch should change both:
1. the final phase-to-amplitude conversion tail
2. the final observable path

But it should not reopen:
- variant design
- remote execution
- broad hyperparameter search

## Narrow implementation target
Target branch:
- add one alternative local circuit tail after the forward entangling layer
- pair it with parity-first evaluation

Recommended tail shape:
1. current feature `RY`
2. current positional `RZ`
3. forward CNOT chain
4. global `RX(pi/4)` layer
5. local Hadamard-style basis-change layer on all qubits
6. reverse CNOT chain
7. parity readout

Rationale:
- still shallow
- easy to express in the current simulator
- explicitly targets interference sensitivity before readout
- does not require a new algorithm family

## What this is not
This is not:
- `V5`
- a new Q-RoPE claim
- a remote-readiness change

It is:
- local screening-path redesign

## Evaluation gate
Promotion gate before any broader implementation:

The redesign is worth carrying forward only if it does at least two of the following:
1. improves mean F1 on at least two datasets vs current `mix_v0 + parity`
2. lowers seed variance on at least two datasets
3. improves worst-seed F1 on at least two datasets

And:
- weighted shadow must not reverse the conclusion on both `yelp` and `amazon`

If that gate fails:
- stop this redesign family
- do not reopen remote spend

## Immediate next step
Implement the alternative tail as a local-only configurable screening mode and run a parity-default packet against the current baseline tail.

## Bottom line
The next branch should be a single interference-sensitive tail redesign with parity-first evaluation.
That is the narrowest broader redesign that matches the evidence and stays zero-credit.
