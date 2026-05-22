# QRoPE Stage 112 Provider Execution Manifest

Stage 112 builds a provider-neutral, no-submission execution manifest from the Stage 107 window plans and Stage 102/104 circuit templates.

The manifest flattens each independent window into concrete circuit jobs:

- known-state calibration jobs from `raw_counts_by_state`;
- matched packet row jobs from `raw_counts_by_row`;
- stable job IDs;
- OpenQASM 3 source;
- shot counts;
- target evidence files that Stage 109 expects to validate.

It also carries forward Stage 111 provider readiness. If Stage 111 is blocked, Stage 112 still writes the manifest but marks submission blocked.

Current expected decision before provider readiness clears:

`PROVIDER_EXECUTION_MANIFEST_PREPARED_SUBMISSION_BLOCKED`

This stage does not submit jobs, collect counts, validate calibration, compute metrics, or support a noisy-hardware robustness claim.
