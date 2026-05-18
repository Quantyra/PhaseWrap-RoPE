# Q-RoPE Phase-Wrap Algorithm v1

Date: 2026-05-15
Epic: E011
Story: S1658
Status: viable local realism-bridge algorithm component

## Algorithm

Given two query-key relative offsets `delta_a` and `delta_b`, and a fixed rotary basis with periods `8` and `12`:

1. Compute wrapped phase for each offset and period:
   - `theta_p(delta) = wrap_to_pi(2*pi*delta/p)`
2. Compute per-band residuals between the two offset pairs:
   - `r_p = abs(wrap_to_pi(theta_p(delta_a) - theta_p(delta_b)))`
3. Convert residuals into band margins:
   - `m_8 = cos(r_8) - cos(pi/4)`
   - `m_12 = cos(r_12) - cos(pi/6)`
4. Use the cross-band phase interaction as the Q-RoPE signal:
   - `qrope_phase_wrap_score = m_8 * m_12`
5. Interpret the score:
   - positive score: cross-band phase consistency
   - negative score: cross-band phase inconsistency

## Why This Is Q-RoPE-Relevant

The algorithm uses RoPE-shaped relative phase behavior rather than raw anchor order, anchor distance, span membership, or single-band modulo summaries. Its discriminating term is a cross-band interaction over wrapped rotary residuals.

## Research Criteria Met Locally

The component meets the current local realism-bridge criteria:

- bounded local task with frozen rotary basis,
- balanced four-quadrant label construction,
- additive single-band symbolic control excluded from cross-band interactions,
- all required diagnostics passed,
- witness beat control on three first-packet seeds,
- witness survived retained token-renaming, pair-slot-swap, and orientation-inversion checks.

## Evidence Summary

First packet mean metrics:

- witness `mae`: `0.107456`
- control `mae`: `0.485067`
- witness `rank_correlation`: `0.882035`
- control `rank_correlation`: `0.135743`

Retained hardening also preserved witness leadership on both metrics for every retained check.

## Limits

This is not yet:

- a transformer-adjacent validation,
- a hardware-backed result,
- a publication-ready claim,
- a broad superiority claim,
- proof of full RoPE behavior in a complete quantum attention model.

## Next Research Question

Does this phase-wrap Q-RoPE component retain value when embedded into a transformer-adjacent validation design rather than a local synthetic realism-bridge task?

That question requires a separate escalation-review memo before any new implementation opens.

