# QRoPE Stage 120 - Live Runner Orchestration Audit

## Objective
Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, under fixed circuit width.

## Result
Stage 120 upgrades the guarded provider runner from a dead-end live-submit placeholder into an orchestration boundary that can load Stage 118 payloads, require Stage 129 cutover authorization, validate Stage 114-shaped submitter output, and write provider result JSONL only when an explicit submitter is injected.

Current decision:

`LIVE_RUNNER_ORCHESTRATION_READY_ADAPTER_REQUIRED`

## What this supports
- Runner commands accept Stage 118 payload input.
- Runner commands require Stage 129 cutover authorization before invoking provider submitters.
- The runner guard validates result count, known job IDs, duplicates, required Stage 114 fields, and non-empty counts before writing provider results.
- CLI execution still refuses live submission unless a provider SDK adapter is supplied.

## What this does not support
- No hardware job submission occurred.
- No provider credentials or secret values were read or recorded.
- No real provider result records were produced.
- Stage 113 evidence assembly remains blocked.
- No noisy-hardware robustness or PhaseWrap advantage claim is supported.

## Artifacts
- `logs/automated_stage_gates/stage120_live_runner_orchestration_audit/manifest.json`
- `logs/automated_stage_gates/stage120_live_runner_orchestration_audit/results.json`
- `logs/automated_stage_gates/stage120_live_runner_orchestration_audit/summary.csv`

## Next gate
Clear Stage 106/111 readiness and Stage 129 cutover authorization, then run guarded live submissions with `--allow-live-submit` and `--stage129-results`.
