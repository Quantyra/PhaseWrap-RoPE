# QRoPE Stage 113 Job Result Evidence Assembler

Stage 113 converts completed Stage 112 provider job results into the exact evidence files validated by Stage 109.

Input files:

- Stage 112 job manifest JSONL;
- provider job result JSONL with one record per Stage 112 job.

Each provider result record must include:

- `job_id`;
- non-empty `counts`;
- job/task identifier;
- backend metadata;
- submitted and completed timestamps.

When every Stage 112 job has counts, Stage 113 can be rerun with `--write-evidence` to fill the declared calibration and matched-packet evidence files only after Stage 115 reports that it collected and wrote the matching Stage 113 provider-result input. Each written evidence file carries `stage113_live_submit_provenance` copied from the Stage 115/152 readiness counters so Stage 109 can reject hand-filled or replayed evidence that lacks all-command authorization and live-submit readiness. By default it only validates readiness and writes no evidence files.

Current expected decision before provider execution:

`JOB_RESULT_EVIDENCE_ASSEMBLY_BLOCKED_RESULTS_MISSING`

This stage does not submit hardware jobs, validate calibration, compute robustness metrics, or support a noisy-hardware advantage claim.
