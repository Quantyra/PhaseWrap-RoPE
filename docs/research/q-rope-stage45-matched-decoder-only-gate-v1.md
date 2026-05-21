# PhaseWrap-RoPE Stage 45 Matched Decoder-Only Gate v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 45 is the first post-plateau matched decoder-only gate after Stage 44 bounded the compact sequence diagnostics. It reuses the repository's no-credential one-block decoder-only attention harness and standardizes the fair comparison set as:

- `rope_relative`
- `alibi`
- `sinusoidal`
- `no_position`
- `phasewrap_bias`
- `phasewrap_adapter`

The task set is the Stage 10 synthetic train-short/test-long packet:

- phase-cued retrieval;
- exact-offset passkey;
- tiny text-fact QA.

This is a matched decoder-only gate, not a production-scale transformer validation.

## Reviewer Command

```bash
python scripts/run_stage45_matched_decoder_only_gate.py
```

This writes:

- `logs/automated_stage_gates/stage45_matched_decoder_only_gate/manifest.json`
- `logs/automated_stage_gates/stage45_matched_decoder_only_gate/results.json`
- `logs/automated_stage_gates/stage45_matched_decoder_only_gate/summary.csv`
- `logs/automated_stage_gates/stage45_matched_decoder_only_gate/per_seed_results.csv`
- `logs/automated_stage_gates/stage45_matched_decoder_only_gate/failed_runs.json`

## Result

Stage 45 records `PROMOTION_NOT_SUPPORTED`.

The one-block decoder remains near chance. Mean target probability is approximately uniform at `0.007812-0.007813` across all methods and tasks. The strongest observed top-1 means are only `0.025000` on the phase-cued and exact-offset tasks, and `0.000000` on tiny text-fact QA.

Best methods by task:

| Task | Best by ranking order | Top-1 | MRR | Target probability |
| --- | --- | ---: | ---: | ---: |
| `phase_cued_retrieval` | `sinusoidal` | 0.025000 | 0.066336 | 0.007812 |
| `exact_offset_passkey` | `phasewrap_adapter` | 0.025000 | 0.052398 | 0.007813 |
| `tiny_text_fact_qa` | `phasewrap_adapter` | 0.000000 | 0.033809 | 0.007813 |

The result preserves two positives without over-reading them:

- PhaseWrap adapters are not eliminated; they are ranking-best by MRR on exact-offset passkey and tiny text-fact QA under this weak one-block gate.
- The phase-cued lane does not favor PhaseWrap under the Stage 45 ranking order; `sinusoidal` is slightly ahead.

Those positives are too weak for promotion because all target probabilities remain near uniform and no task reaches useful absolute accuracy.

## Interpretation

Stage 45 moves beyond compact copy-path diagnostics into a matched decoder-only harness, but the harness is still too weak to support any replacement claim. The honest interpretation is negative for promotion and useful for bounding: this one-block decoder gate does not show a meaningful PhaseWrap advantage, RoPE advantage, or production-relevant transformer behavior.

The next useful transformer-side work is either:

- strengthen the decoder-only implementation enough to learn the task at all, then rerun the same fair comparison; or
- record that the current one-block decoder gate is a capacity/optimization failure rather than a positional-method discriminator.

## Claim Boundary

Supported:

- matched one-block decoder-only gate evidence after the Stage 44 compact plateau;
- fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparison under matched data, seeds, epochs, and model shape;
- negative promotion evidence with failed-run retention and per-seed artifacts;
- weak PhaseWrap ranking positives on exact-offset and tiny text-fact QA that do not survive absolute-performance scrutiny.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that Stage 45 is a reliable positional-method discriminator when the one-block decoder remains near chance.
