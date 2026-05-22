# PhaseWrap-RoPE Stage 108 Provider Configuration Handoff v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 108 converts the Stage 106 blocker report into non-secret provider configuration templates.

Stage 107 gives the execution sequence, but every hardware-dependent step remains blocked until Stage 106 clears. Stage 108 prepares local-only environment templates and a checklist for the exact fields Stage 106 needs.

## Reviewer Command

```bash
python scripts/run_stage108_provider_configuration_handoff.py
```

This writes:

- `logs/automated_stage_gates/stage108_provider_configuration_handoff/manifest.json`
- `logs/automated_stage_gates/stage108_provider_configuration_handoff/results.json`
- `logs/automated_stage_gates/stage108_provider_configuration_handoff/summary.csv`
- `logs/automated_stage_gates/stage108_provider_configuration_handoff/env_templates/*.template`

## Result

Current decision:

`PROVIDER_CONFIGURATION_HANDOFF_PREPARED_STAGE106_STILL_BLOCKED`

Stage 108 writes templates for:

- `amazon_braket_stage106_env.template`
- `ibm_runtime_stage106_env.template`

The templates contain variable names and placeholders only. They do not contain credential values.

## Current Blockers

Amazon Braket:

- provider credentials/profile missing;
- backend/device selection missing;
- output S3 bucket missing;
- region missing.

IBM Runtime:

- IBM instance CRN missing.

Common budget and queue caps were already present in the Stage 106 preflight.

## Claim Boundary

Supported:

- a non-secret provider configuration handoff for clearing Stage 106;
- provider-specific environment templates tied to observed Stage 106 blockers;
- a reminder that credentials and secret values must remain local and uncommitted.

Excluded:

- real provider credentials;
- backend availability discovery;
- hardware submission;
- completed calibration or matched packet execution;
- a noisy-hardware robustness result.

## Next Gate

Fill provider configuration locally, rerun Stage 106 with `--load-dotenv`, and proceed to Stage 107 only after Stage 106 reports ready.
