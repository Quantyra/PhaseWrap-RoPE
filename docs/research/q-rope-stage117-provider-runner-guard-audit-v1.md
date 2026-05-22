# QRoPE Stage 117 Provider Runner Guard Audit

Stage 117 adds guarded provider runner entrypoints for the Stage 116 command handoff and audits that those commands are currently blocked before live execution.

The committed runner scripts:

- `scripts/provider_runners/run_ibm_runtime_stage112_jobs.py`
- `scripts/provider_runners/run_amazon_braket_stage112_jobs.py`

Both entrypoints load Stage 111 readiness, Stage 118 payloads, and Stage 129 cutover authorization, inspect the requested Stage 114 job shard, and refuse to run while the provider is not ready or cutover is not authorized. Even if Stage 111 later reports ready, live submission still requires an explicit `--allow-live-submit` flag and provider-specific submitter.

Current expected decision:

`PROVIDER_RUNNER_GUARDS_PREPARED_EXECUTION_BLOCKED`

This stage does not submit hardware jobs, record credentials, produce provider results, assemble evidence, or support a noisy-hardware robustness claim.
