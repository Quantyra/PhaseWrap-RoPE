# PhaseWrap-RoPE Stage 44 Compact-Diagnostic Plateau Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 44 audits the sealed Stage 39-43 compact sequence and pointer-generator diagnostics as a claim-boundary plateau. It does not train another compact model. Instead, it reads the committed `summary.csv` artifacts for Stages 39, 40, 41, 42, and 43, compares the same primary metrics, and records whether the compact diagnostic lane can support broader claims.

The audited metrics are:

- top-1 accuracy;
- MRR;
- mean target value probability;
- expected calibration error.

## Reviewer Command

```bash
python scripts/run_stage44_compact_diagnostic_plateau_audit.py
```

This writes:

- `logs/automated_stage_gates/stage44_compact_diagnostic_plateau_audit/manifest.json`
- `logs/automated_stage_gates/stage44_compact_diagnostic_plateau_audit/results.json`
- `logs/automated_stage_gates/stage44_compact_diagnostic_plateau_audit/summary.csv`

## Result

Stage 44 records `BOUND_COMPACT_DIAGNOSTIC_PLATEAU`.

| Stage | Best top-1 | Best MRR | Best target probability | Best ECE | PhaseWrap primary wins |
| --- | --- | --- | --- | --- | --- |
| Stage 39 | `no_position` | `rope_relative` | `sinusoidal` | `alibi` | none |
| Stage 40 | `phasewrap_distance_adapter` | `phasewrap_distance_adapter` | `phasewrap_distance_adapter` | `no_position` | top-1, MRR, target probability |
| Stage 41 | `rope_relative` | `rope_relative` | `rope_relative` | `rope_relative` | none |
| Stage 42 | `rope_relative` | `rope_relative` | `rope_relative` | `no_position` | none |
| Stage 43 | `rope_relative` | `rope_relative` | `rope_relative` | `no_position` | none |

The plateau decision is based on three facts:

- Stages 39-43 are all compact diagnostics rather than matched decoder-only transformer benchmarks.
- No Stage 39-43 result gives PhaseWrap-derived methods a sweep across all primary metrics.
- The final hardened compact diagnostic, Stage 43, remains RoPE-favorable on ranking and target probability while calibration is not led by PhaseWrap.

## Interpretation

The compact diagnostic lane has become useful for bounding the claim, not for expanding it. Stage 40 is genuine positive evidence that PhaseWrap-derived adapters can lead weak held-out rows inside a compact sequence curriculum. Stages 41-43 are also positive in a narrower sense: PhaseWrap-derived adapters remain ranking-competitive once copy-aware output paths repair the sequence task.

Those positives do not erase the failure modes. The compact lane repeatedly depends on diagnostic output paths, Stage 43 remains RoPE-favorable overall, and the learned generator branch is still weak as a free value generator. Stage 44 therefore makes the current honest outcome explicit: `BOUND`, not `PROMOTE`.

The next evidence-producing move should be a stronger matched decoder-only transformer benchmark using the same fair RoPE, ALiBI, sinusoidal, no-position, and PhaseWrap comparison frame.

## Claim Boundary

Supported:

- reproducible plateau audit over the Stage 39-43 compact diagnostics;
- bounded evidence that PhaseWrap-derived methods can be competitive on compact ranking diagnostics;
- explicit preservation of negative evidence where RoPE-like scoring remains stronger;
- a decision that additional compact copy-path diagnostics should not broaden the claim boundary.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that the compact diagnostic lane should substitute for a matched decoder-only transformer gate.
