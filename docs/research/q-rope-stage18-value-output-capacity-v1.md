# PhaseWrap-RoPE Stage 18 Value-Output Capacity Probe v1

Date: `2026-05-20`

## Purpose

Stage 18 diagnoses the Stage 17 small decoder value-model failure. It removes positional attention as the main bottleneck by comparing uniform attention with teacher-forced target attention, while keeping the learned value embeddings and output projection.

This is a local capacity probe. It is not a production transformer benchmark and not proof that PhaseWrap-RoPE replaces RoPE.

## Artifact Paths

- Manifest: `logs/automated_stage_gates/stage18_value_output_capacity/manifest.json`
- Results: `logs/automated_stage_gates/stage18_value_output_capacity/results.json`
- Summary CSV: `logs/automated_stage_gates/stage18_value_output_capacity/summary.csv`
- Runner: `scripts/run_stage18_value_output_capacity.py`
- Implementation: `src/qrope/stage18_value_output_capacity.py`
- Tests: `tests/test_stage18_value_output_capacity.py`

## Reproduce

```bash
python scripts/run_stage18_value_output_capacity.py
```

The command is local-only. It does not submit hardware jobs and does not require provider credentials.

## Result

| Mode | Split | Rows | Top-1 | MRR | Mean target value probability | Mean first relevant value rank |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `uniform_attention` | train | 120 | 0.033333 | 0.115652 | 0.007808 | 30.100000 |
| `uniform_attention` | validation | 60 | 0.000000 | 0.022567 | 0.005111 | 109.033333 |
| `uniform_attention` | test | 60 | 0.016667 | 0.034671 | 0.005182 | 112.550000 |
| `teacher_forced_attention` | train | 120 | 0.066667 | 0.140586 | 0.008271 | 24.550000 |
| `teacher_forced_attention` | validation | 60 | 0.000000 | 0.028111 | 0.005147 | 102.333333 |
| `teacher_forced_attention` | test | 60 | 0.016667 | 0.041872 | 0.005308 | 109.066667 |

Teacher-forced attention does not make the learned value-output path fit the training packet strongly. This indicates that the Stage 17 failure is not only a positional-attention issue; the compact value embedding/output projection is also underpowered or poorly optimized for the current packet.

## Claim Boundary

Supported:

- deterministic capacity probe for the Stage 17 learned value-output bottleneck;
- evidence that teacher-forced target attention does not substantially fix train or test performance in the current setup;
- evidence that the next decoder experiment should harden the value-output path before interpreting positional mechanisms.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- proof that PhaseWrap-RoPE replaces RoPE.

## Next Step

The next downstream experiment should improve capacity and optimization before re-testing positional mechanisms: larger value embeddings, more train rows, better optimizer dynamics, and validation-based checkpointing.
