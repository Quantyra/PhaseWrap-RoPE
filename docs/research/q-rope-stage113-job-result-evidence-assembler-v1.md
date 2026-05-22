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

When every Stage 112 job has counts, Stage 113 can be rerun with `--write-evidence` to fill the declared calibration and matched-packet evidence files. By default it only validates readiness and writes no evidence files.

Current expected decision before provider execution:

`JOB_RESULT_EVIDENCE_ASSEMBLY_BLOCKED_RESULTS_MISSING`

This stage does not submit hardware jobs, validate calibration, compute robustness metrics, or support a noisy-hardware advantage claim.
