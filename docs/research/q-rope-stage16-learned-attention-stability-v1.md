# PhaseWrap-RoPE Stage 16 Learned Attention Stability Benchmark v1

Date: `2026-05-20`

## Purpose

Stage 16 tests whether the Stage 15 learned attention-readout result is stable across initialization seeds. It reruns the same non-phase-cued key-value readout task across five deterministic learned-scorer initializations.

This is a local stability check. It is not a full decoder-only transformer benchmark and not proof that PhaseWrap-RoPE replaces RoPE.

## Artifact Paths

- Manifest: `logs/automated_stage_gates/stage16_learned_attention_stability/manifest.json`
- Results: `logs/automated_stage_gates/stage16_learned_attention_stability/results.json`
- Summary CSV: `logs/automated_stage_gates/stage16_learned_attention_stability/summary.csv`
- Per-run CSV: `logs/automated_stage_gates/stage16_learned_attention_stability/per_run_results.csv`
- Runner: `scripts/run_stage16_learned_attention_stability.py`
- Implementation: `src/qrope/stage16_learned_attention_stability.py`
- Tests: `tests/test_stage16_learned_attention_stability.py`

## Reproduce

```bash
python scripts/run_stage16_learned_attention_stability.py
```

The command is local-only. It does not submit hardware jobs and does not require provider credentials.

## Result

| Method | Init seeds | Top-1 mean | Top-1 min-max | MRR mean | Target value probability mean | Target value probability min-max |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| `phasewrap_distance_adapter` | 5 | 1.000000 | 1.000000-1.000000 | 1.000000 | 0.522507 | 0.515931-0.529001 |
| `rope_relative` | 5 | 0.983333 | 0.933333-1.000000 | 0.991667 | 0.706780 | 0.680342-0.731759 |
| `sinusoidal` | 5 | 0.733333 | 0.733333-0.733333 | 0.859722 | 0.473392 | 0.471383-0.476096 |
| `phasewrap_residual_adapter` | 5 | 0.500000 | 0.500000-0.500000 | 0.718056 | 0.332621 | 0.326535-0.339595 |
| `alibi` | 5 | 0.100000 | 0.100000-0.100000 | 0.214748 | 0.042713 | 0.042676-0.042768 |
| `no_position` | 5 | 0.083333 | 0.083333-0.083333 | 0.195125 | 0.042635 | 0.042635-0.042635 |
| `phasewrap_score` | 5 | 0.050000 | 0.050000-0.050000 | 0.147274 | 0.051229 | 0.050660-0.052044 |

The Stage 15 ranking result is stable across the tested initialization seeds: `phasewrap_distance_adapter` has top-1 `1.0` and MRR `1.0` in every run. RoPE-like scoring still has higher target value probability in every run, so the result remains a ranking advantage on this local packet rather than a general replacement claim.

## Claim Boundary

Supported:

- deterministic initialization-stability check for the Stage 15 learned attention-readout benchmark;
- evidence that PhaseWrap-plus-distance ranking behavior is stable across the five tested initialization seeds;
- evidence that RoPE-like scoring remains stronger on target value probability.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- proof that PhaseWrap-RoPE replaces RoPE.

## Next Step

The next downstream experiment should move from learned attention-readout to a stronger small decoder-only transformer with learned token embeddings, matched compute, multiple seeds, failed-run artifacts, and non-phase-cued retrieval or compact QA tasks.
