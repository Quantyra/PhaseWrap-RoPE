# QRoPE Stage 116 Provider Runner Plan

Stage 116 prepares provider/window runner plans from the Stage 114 job shards, Stage 111 provider readiness records, Stage 118 payload records, and Stage 129 cutover records.

It emits one runner record per provider/window shard with:

- job shard path;
- provider result output path for Stage 115;
- calibration and packet job counts;
- inherited Stage 111 blockers;
- provider-specific runner command shape with explicit Stage 111, Stage 118, and Stage 129 evidence inputs.

Current expected decision before provider readiness clears:

`PROVIDER_RUNNER_PLAN_PREPARED_EXECUTION_BLOCKED`

This stage does not submit hardware jobs, invoke provider SDKs, record credentials, produce result records, assemble evidence, or support a noisy-hardware robustness claim.
