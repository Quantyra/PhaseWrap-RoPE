# Q-RoPE Pair-State Validity Audit v1

## Decision
- `CONDITIONAL`
- `DO NOT EXPAND YET`

## Main validity risk
The current pair-state branch explicitly encodes signed offset sectors on a synthetic dataset whose label is the sign of the relative offset.

That creates a serious validity risk:
- the branch may be expressing the intended relational mechanism
- but it may also be too directly aligned to the label rule to count as a sufficiently informative restart success

## What is still meaningful
The result is not invalid in the narrow sense.

Why:
- the branch is doing exactly what it was designed to do
- the effect is multi-seed
- diagnostics show sector-first processing rather than pooled scalar collapse

So the packet is a real positive signal.

## Why it is still not trustworthy enough to expand
The packet alone does not distinguish between:
1. a genuinely useful relational mechanism
2. a design that is too tightly keyed to the synthetic label definition

That distinction matters because if the branch only wins when the sector definition mirrors the label rule too directly, it is not yet a strong restart success.

## Correct current interpretation
- `trustworthy as a mechanism-positive signal`
- `not trustworthy yet as a broad restart-validation signal`

## Smallest control needed next
Run one `sector-alignment control` and nothing broader.

Control concept:
- keep the same pair-state skeleton
- break the direct label alignment in the sector mapping
- test whether the branch still retains useful separation or collapses immediately

Examples of acceptable control styles:
- permute sector-to-sign assignments
- mask sign information while preserving coarse magnitude sectors

The point is not to find a better variant.
The point is to test whether the current win depends on a too-direct encoding of the label rule.

## Decision consequence
Do not broaden:
- benchmarks
- cloud execution
- additional pair-state variants

Only allow the minimal validity control next.

## Bottom line
The current pair-state packet is:
- `positive`
- `conditional`
- `not yet enough to justify expansion`

The next correct move is one narrow validity control, not celebration and not broadening.

