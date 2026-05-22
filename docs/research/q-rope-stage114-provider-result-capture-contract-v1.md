# QRoPE Stage 114 Provider Result Capture Contract

Stage 114 prepares the result-capture contract for provider runners that execute Stage 112 jobs.

It emits:

- `provider_job_result_schema.json`, the required JSONL record contract consumed by Stage 113;
- per-provider/window job shards under `job_shards/`;
- fillable per-provider/window result stubs under `result_stubs/`;
- declared result output paths under `provider_results/`.

Every provider result record must include:

- `job_id`;
- `job_or_task_id`;
- `backend_metadata`;
- `submitted_at_utc`;
- `completed_at_utc`;
- `counts`.

Current expected decision before hardware execution:

`PROVIDER_RESULT_CAPTURE_CONTRACT_PREPARED_RESULTS_REQUIRED`

This stage does not submit hardware jobs, record credentials, produce counts, validate calibration, compute metrics, or support a noisy-hardware robustness claim.
